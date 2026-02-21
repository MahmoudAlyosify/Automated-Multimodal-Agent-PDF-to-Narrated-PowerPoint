"""
LangGraph orchestration workflow for the 8-stage multimodal pipeline.
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from langgraph.graph import END, START, StateGraph

try:
    from .agents import (
        run_chunker_agent,
        run_generator_agent,
        run_parser_agent,
        run_planner_agent,
        run_pptx_agent,
        run_script_agent,
        run_tts_agent,
        run_vector_agent,
    )
    from .state import PipelineState
except ImportError:  # pragma: no cover
    from agents import (
        run_chunker_agent,
        run_generator_agent,
        run_parser_agent,
        run_planner_agent,
        run_pptx_agent,
        run_script_agent,
        run_tts_agent,
        run_vector_agent,
    )
    from state import PipelineState


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def _coerce_pipeline_state(initial_state: PipelineState, raw_state: Any) -> PipelineState:
    """Normalize LangGraph output into a PipelineState instance."""
    if isinstance(raw_state, PipelineState):
        if raw_state.progress_callback is None:
            raw_state.progress_callback = initial_state.progress_callback
        return raw_state

    if isinstance(raw_state, Mapping):
        for key, value in raw_state.items():
            if not hasattr(initial_state, key):
                continue

            if key == "progress_callback":
                if callable(value):
                    initial_state.progress_callback = value
                continue

            if key in {"start_time", "end_time"} and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    pass

            setattr(initial_state, key, value)
        return initial_state

    raise TypeError(
        f"Unexpected graph output type: {type(raw_state)!r}. "
        "Expected PipelineState or mapping."
    )


def _mark_failed(state: PipelineState, stage: str, message: str) -> PipelineState:
    state.status = "failed"
    if not state.error_message:
        state.error_message = message
    state.add_log("ERROR", stage, message)
    state.emit_progress(stage, "failed", message)
    return state


def handle_parser_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "parser", "Pipeline stopped: parser stage failed")


def handle_chunker_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "chunker", "Pipeline stopped: chunker stage failed")


def handle_vector_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "vector", "Pipeline stopped: vector stage failed")


def handle_planner_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "planner", "Pipeline stopped: planner stage failed")


def handle_generator_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "generator", "Pipeline stopped: generator stage failed")


def handle_pptx_error(state: PipelineState) -> PipelineState:
    return _mark_failed(state, "pptx", "Pipeline stopped: PPTX stage failed")


def check_parser(state: PipelineState) -> str:
    return "chunker" if state.parser_success else "parser_error"


def check_chunker(state: PipelineState) -> str:
    return "vector" if state.chunker_success else "chunker_error"


def check_vector(state: PipelineState) -> str:
    return "planner" if state.vector_success else "vector_error"


def check_planner(state: PipelineState) -> str:
    return "generator" if state.planner_success else "planner_error"


def check_generator(state: PipelineState) -> str:
    return "script" if state.generator_success else "generator_error"


def check_pptx(state: PipelineState) -> str:
    return "finalize" if state.pptx_success else "pptx_error"


def _copy_if_exists(src: str, dst: Path) -> Optional[str]:
    if not src:
        return None
    src_path = Path(src)
    if not src_path.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst)
    return str(dst)


def _create_narrated_zip(state: PipelineState, output_dir: Path) -> Optional[str]:
    if not state.pptx_path or not Path(state.pptx_path).exists():
        return None

    zip_name = (
        f"{state.pdf_filename}_Narrated_with_audio.zip"
        if state.pdf_filename
        else "Narrated_with_audio.zip"
    )
    zip_path = output_dir / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(state.pptx_path, arcname=Path(state.pptx_path).name)
        for audio_file in state.audio_files:
            audio_path = Path(audio_file)
            if audio_path.exists():
                archive.write(audio_path, arcname=f"audio/{audio_path.name}")

    return str(zip_path)


def finalize_pipeline(state: PipelineState) -> PipelineState:
    """Finalize outputs, persist metadata, and set terminal status."""
    state.current_stage = "finalize"
    state.emit_progress("finalize", "running", "Finalizing outputs")
    state.add_log("INFO", "finalize", "Finalizing pipeline outputs")

    try:
        output_dir = Path(state.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if state.pptx_path:
            final_name = (
                f"{state.pdf_filename}_Narrated.pptx"
                if state.pdf_filename
                else "Narrated-PowerPoint.pptx"
            )
            copied_pptx = _copy_if_exists(state.pptx_path, output_dir / final_name)
            if copied_pptx:
                state.pptx_path = copied_pptx
                state.add_log("INFO", "finalize", f"Copied PPTX: {final_name}")

        copied_audio_files = []
        if state.audio_output_dir and Path(state.audio_output_dir).exists():
            audio_dir = output_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            for src in sorted(Path(state.audio_output_dir).glob("*.wav")):
                dst = audio_dir / src.name
                shutil.copy2(src, dst)
                copied_audio_files.append(str(dst))
            state.add_log("INFO", "finalize", f"Copied {len(copied_audio_files)} audio files")
        state.audio_files = copied_audio_files

        metadata_dir = output_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_sources = {
            state.parsed_content_path: "parsed_content.json",
            state.semantic_chunks_path: "semantic_chunks.json",
            state.slide_plan_path: "slide_plan.json",
            state.slides_content_path: "slides_content.json",
            state.scripts_path: "scripts.json",
        }
        copied_metadata = 0
        for src, dst_name in metadata_sources.items():
            copied = _copy_if_exists(src, metadata_dir / dst_name)
            if copied:
                copied_metadata += 1
        state.add_log("INFO", "finalize", f"Copied {copied_metadata} metadata files")

        narrated_zip = _create_narrated_zip(state, output_dir)
        if narrated_zip:
            state.narrated_zip_path = narrated_zip
            state.add_log("INFO", "finalize", f"Created narrated bundle: {Path(narrated_zip).name}")

        state.end_time = datetime.now()
        if state.status != "failed" and state.pptx_success:
            state.status = "completed"
            state.add_log("INFO", "finalize", "Pipeline completed successfully")
            state.emit_progress("finalize", "completed", "Pipeline completed")
        else:
            state.status = "failed"
            state.add_log("ERROR", "finalize", "Pipeline ended with failures")
            state.emit_progress("finalize", "failed", state.error_message or "Pipeline failed")

        metadata_file = state.save_metadata()
        state.add_log("INFO", "finalize", f"Saved pipeline metadata: {Path(metadata_file).name}")
    except Exception as exc:
        state.status = "failed"
        state.error_message = f"Finalize stage failed: {exc}"
        state.end_time = datetime.now()
        state.add_log("ERROR", "finalize", state.error_message)
        state.emit_progress("finalize", "failed", state.error_message)
        logger.exception("Finalize stage failed")

    return state


def create_workflow_graph() -> Any:
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(PipelineState)

    graph.add_node("parser", run_parser_agent)
    graph.add_node("chunker", run_chunker_agent)
    graph.add_node("vector", run_vector_agent)
    graph.add_node("planner", run_planner_agent)
    graph.add_node("generator", run_generator_agent)
    graph.add_node("script", run_script_agent)
    graph.add_node("tts", run_tts_agent)
    graph.add_node("pptx", run_pptx_agent)
    graph.add_node("parser_error", handle_parser_error)
    graph.add_node("chunker_error", handle_chunker_error)
    graph.add_node("vector_error", handle_vector_error)
    graph.add_node("planner_error", handle_planner_error)
    graph.add_node("generator_error", handle_generator_error)
    graph.add_node("pptx_error", handle_pptx_error)
    graph.add_node("finalize", finalize_pipeline)

    graph.add_edge(START, "parser")

    graph.add_conditional_edges(
        "parser",
        check_parser,
        {"chunker": "chunker", "parser_error": "parser_error"},
    )
    graph.add_conditional_edges(
        "chunker",
        check_chunker,
        {"vector": "vector", "chunker_error": "chunker_error"},
    )
    graph.add_conditional_edges(
        "vector",
        check_vector,
        {"planner": "planner", "vector_error": "vector_error"},
    )
    graph.add_conditional_edges(
        "planner",
        check_planner,
        {"generator": "generator", "planner_error": "planner_error"},
    )
    graph.add_conditional_edges(
        "generator",
        check_generator,
        {"script": "script", "generator_error": "generator_error"},
    )

    graph.add_edge("script", "tts")
    graph.add_edge("tts", "pptx")

    graph.add_conditional_edges(
        "pptx",
        check_pptx,
        {"finalize": "finalize", "pptx_error": "pptx_error"},
    )

    graph.add_edge("parser_error", "finalize")
    graph.add_edge("chunker_error", "finalize")
    graph.add_edge("vector_error", "finalize")
    graph.add_edge("planner_error", "finalize")
    graph.add_edge("generator_error", "finalize")
    graph.add_edge("pptx_error", "finalize")

    graph.add_edge("finalize", END)
    return graph.compile()


class WorkflowOrchestrator:
    """High-level API to execute the full graph workflow."""

    def __init__(self, output_base_dir: str = "output") -> None:
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.graph = create_workflow_graph()

    def execute(
        self,
        pdf_path: str,
        pdf_filename: Optional[str] = None,
        run_id: Optional[str] = None,
        callbacks: Optional[Dict[str, Any]] = None,
    ) -> PipelineState:
        """Execute the pipeline once and return the final state."""
        source_pdf = Path(pdf_path)
        if not source_pdf.exists():
            raise ValueError(f"PDF not found: {pdf_path}")
        if source_pdf.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {pdf_path}")

        if not pdf_filename:
            pdf_filename = source_pdf.stem
        if not run_id:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        run_output_dir = self.output_base_dir / run_id
        run_output_dir.mkdir(parents=True, exist_ok=True)

        state = PipelineState(
            pdf_path=str(source_pdf.resolve()),
            pdf_filename=pdf_filename,
            output_dir=str(run_output_dir),
            run_id=run_id,
            start_time=datetime.now(),
            status="running",
            progress_callback=(callbacks or {}).get("on_stage"),
        )
        state.add_log("INFO", "orchestrator", f"Pipeline started (run_id={run_id})")
        state.emit_progress("pipeline", "running", "Pipeline execution started")

        try:
            raw_final_state = self.graph.invoke(state)
            final_state = _coerce_pipeline_state(state, raw_final_state)
            final_state.emit_progress("pipeline", final_state.status, "Pipeline execution finished")

            on_complete = (callbacks or {}).get("on_complete")
            on_error = (callbacks or {}).get("on_error")
            if final_state.status == "completed":
                if callable(on_complete):
                    on_complete(final_state)
            else:
                if callable(on_error):
                    on_error(final_state, final_state.error_message or "Pipeline failed")
            return final_state
        except Exception as exc:
            state.status = "failed"
            state.end_time = datetime.now()
            state.error_message = f"Orchestrator crashed: {exc}"
            state.add_log("ERROR", "orchestrator", state.error_message)
            state.emit_progress("pipeline", "failed", state.error_message)
            try:
                state.save_metadata()
            except Exception:
                logger.exception("Failed to save crash metadata")

            on_error = (callbacks or {}).get("on_error")
            if callable(on_error):
                on_error(state, state.error_message)
            raise

    def get_logs(self, state: PipelineState) -> list:
        return state.logs

    def get_summary(self, state: PipelineState) -> Dict[str, Any]:
        duration_seconds = None
        if state.end_time and state.start_time:
            duration_seconds = (state.end_time - state.start_time).total_seconds()

        return {
            "run_id": state.run_id,
            "status": state.status,
            "pdf_path": state.pdf_path,
            "pptx_path": state.pptx_path,
            "narrated_zip_path": state.narrated_zip_path,
            "audio_files": len(state.audio_files),
            "slides": len(state.slide_plan),
            "duration_seconds": duration_seconds,
            "stage_results": {
                "parser": state.parser_success,
                "chunker": state.chunker_success,
                "vector": state.vector_success,
                "planner": state.planner_success,
                "generator": state.generator_success,
                "script": state.script_success,
                "tts": state.tts_success,
                "pptx": state.pptx_success,
            },
            "error": state.error_message,
        }
