"""
Streamlit UI for PDF -> narrated PowerPoint generation.
"""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

try:
    from .graph import WorkflowOrchestrator
    from .state import PipelineState
except ImportError:  # pragma: no cover
    from graph import WorkflowOrchestrator
    from state import PipelineState


CORE_STAGES = [
    "parser",
    "chunker",
    "vector",
    "planner",
    "generator",
    "script",
    "tts",
    "pptx",
]

STAGE_LABELS = {
    "pipeline": "Pipeline",
    "parser": "PDF Parser",
    "chunker": "Semantic Chunker",
    "vector": "Vector Store",
    "planner": "Slide Planner",
    "generator": "Slide Generator",
    "script": "Script Generator",
    "tts": "TTS Audio",
    "pptx": "PPTX Builder",
    "finalize": "Finalize",
}


def init_session() -> None:
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = WorkflowOrchestrator(output_base_dir="output")
    if "result_state" not in st.session_state:
        st.session_state.result_state = None
    if "stage_events" not in st.session_state:
        st.session_state.stage_events = []
    if "run_error" not in st.session_state:
        st.session_state.run_error = ""


def save_uploaded_pdf(uploaded_file: Any) -> str:
    uploads_dir = Path("temp_uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    path = uploads_dir / filename
    path.write_bytes(uploaded_file.getbuffer())
    return str(path.resolve())


def event_to_progress(event: Dict[str, Any]) -> int:
    stage = event.get("stage", "")
    status = event.get("status", "")

    if stage == "finalize":
        if status == "completed":
            return 100
        if status == "failed":
            return 100
        return 95

    if stage not in CORE_STAGES:
        return 0

    stage_index = CORE_STAGES.index(stage) + 1
    if status == "completed":
        return int(stage_index / len(CORE_STAGES) * 90)
    if status == "running":
        return int(((stage_index - 1) + 0.5) / len(CORE_STAGES) * 90)
    if status == "failed":
        return int(((stage_index - 1) + 0.5) / len(CORE_STAGES) * 90)
    return 0


def build_narrated_zip(state: PipelineState) -> bytes:
    if state.narrated_zip_path and Path(state.narrated_zip_path).exists():
        return Path(state.narrated_zip_path).read_bytes()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        if state.pptx_path and Path(state.pptx_path).exists():
            archive.write(state.pptx_path, arcname=Path(state.pptx_path).name)
        for audio_file in state.audio_files:
            audio_path = Path(audio_file)
            if audio_path.exists():
                archive.write(audio_path, arcname=f"audio/{audio_path.name}")
    return zip_buffer.getvalue()


def render_stage_status(state: PipelineState) -> None:
    stage_flags = [
        ("PDF Parser", state.parser_success),
        ("Semantic Chunker", state.chunker_success),
        ("Vector Store", state.vector_success),
        ("Slide Planner", state.planner_success),
        ("Slide Generator", state.generator_success),
        ("Script Generator", state.script_success),
        ("TTS Audio", state.tts_success),
        ("PPTX Builder", state.pptx_success),
    ]

    cols = st.columns(4)
    for idx, (name, ok) in enumerate(stage_flags):
        col = cols[idx % 4]
        with col:
            if ok:
                st.success(f"{name}: OK")
            else:
                st.warning(f"{name}: Not complete")


def run_pipeline(uploaded_file: Any) -> None:
    st.session_state.stage_events = []
    st.session_state.result_state = None
    st.session_state.run_error = ""

    pdf_path = save_uploaded_pdf(uploaded_file)
    # Diagnostic: show where upload was saved and verify existence
    try:
        st.info(f"Saved upload to: {pdf_path}")
        if not Path(pdf_path).exists():
            st.error(f"Uploaded file not found at expected path: {pdf_path}")
            return
    except Exception:
        # In case Streamlit is not ready to render info, continue silently
        pass
    pdf_filename = Path(uploaded_file.name).stem

    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    events_placeholder = st.empty()

    def on_stage(event: Dict[str, Any]) -> None:
        st.session_state.stage_events.append(event)
        progress_bar.progress(event_to_progress(event))

        stage = STAGE_LABELS.get(event.get("stage", ""), event.get("stage", "unknown"))
        message = event.get("message", "")
        status_placeholder.info(f"{stage}: {message}")

        latest_lines = [
            f"{item['timestamp']} | {STAGE_LABELS.get(item['stage'], item['stage'])} | {item['status']} | {item['message']}"
            for item in st.session_state.stage_events[-8:]
        ]
        events_placeholder.code("\n".join(latest_lines), language="text")

    def on_complete(state: PipelineState) -> None:
        st.session_state.result_state = state

    def on_error(state: PipelineState, error: str) -> None:
        st.session_state.result_state = state
        st.session_state.run_error = error

    try:
        state = st.session_state.orchestrator.execute(
            pdf_path=pdf_path,
            pdf_filename=pdf_filename,
            callbacks={
                "on_stage": on_stage,
                "on_complete": on_complete,
                "on_error": on_error,
            },
        )
        # Diagnostic: show basic run info and persist metadata
        try:
            st.info(f"Pipeline run_id: {state.run_id}")
            st.info(f"Output directory: {state.output_dir}")
            # Ensure metadata is saved for inspection
            metadata_path = state.save_metadata()
            st.info(f"Saved pipeline metadata: {metadata_path}")
            # List output dir contents briefly
            out_dir = Path(state.output_dir)
            if out_dir.exists():
                items = [p.name for p in out_dir.iterdir()]
                st.write("Output directory contents:", items)
        except Exception:
            pass
        st.session_state.result_state = state
        progress_bar.progress(100)
    except Exception as exc:
        st.session_state.run_error = str(exc)


def render_results(state: PipelineState) -> None:
    st.subheader("Results")

    if state.status == "completed":
        st.success("Pipeline completed successfully.")
    else:
        st.error(f"Pipeline failed: {state.error_message or st.session_state.run_error or 'Unknown error'}")

    duration_seconds = None
    if state.end_time and state.start_time:
        duration_seconds = (state.end_time - state.start_time).total_seconds()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Status", state.status)
    col2.metric("Slides", len(state.slide_plan))
    col3.metric("Audio Files", len(state.audio_files))
    col4.metric("Duration (s)", f"{duration_seconds:.1f}" if duration_seconds is not None else "-")

    render_stage_status(state)

    if state.pptx_path and Path(state.pptx_path).exists():
        pptx_bytes = Path(state.pptx_path).read_bytes()
        st.download_button(
            label="Download PPTX",
            data=pptx_bytes,
            file_name=Path(state.pptx_path).name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )

    if state.pptx_path and Path(state.pptx_path).exists():
        zip_bytes = build_narrated_zip(state)
        zip_name = (
            f"{state.pdf_filename}_Narrated_with_audio.zip"
            if state.pdf_filename
            else "Narrated_with_audio.zip"
        )
        st.download_button(
            label="Download Narrated Bundle (ZIP)",
            data=zip_bytes,
            file_name=zip_name,
            mime="application/zip",
            use_container_width=True,
        )

    with st.expander("Execution Logs", expanded=False):
        if state.logs:
            st.dataframe(state.logs, use_container_width=True)
        else:
            st.write("No logs captured.")


def main() -> None:
    st.set_page_config(
        page_title="PDF to Narrated PowerPoint",
        layout="wide",
    )
    init_session()

    st.title("PDF to Narrated PowerPoint")
    st.write("Upload a PDF, run the full 8-agent LangGraph pipeline, and download outputs.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    run_clicked = st.button("Run Pipeline", type="primary", disabled=uploaded_file is None)

    if uploaded_file is not None:
        st.caption(f"Selected file: {uploaded_file.name} ({uploaded_file.size} bytes)")

    if run_clicked and uploaded_file is not None:
        run_pipeline(uploaded_file)

    if st.session_state.run_error and st.session_state.result_state is None:
        st.error(st.session_state.run_error)

    result_state = st.session_state.result_state
    if isinstance(result_state, PipelineState):
        render_results(result_state)


if __name__ == "__main__":
    main()
