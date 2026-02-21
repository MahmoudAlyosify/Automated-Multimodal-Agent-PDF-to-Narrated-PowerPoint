from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_pptx_agent(state: PipelineState) -> PipelineState:
    """Stage 8: Build the final PowerPoint file."""
    stage = "pptx"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting PPTX build")
    state.emit_progress(stage, "running", "Building PowerPoint file")

    try:
        if not state.slides_content_path:
            raise ValueError("Missing slides_content_path from generator stage")
        if not Path(state.slides_content_path).exists():
            raise FileNotFoundError(f"Slides content file not found: {state.slides_content_path}")

        agent_dir = get_agent_directory(stage)
        output_pptx_path = agent_dir / "lecture.pptx"

        pptx_cls = import_agent_class(stage, "pptx_builder_agent", "PPTXBuilderAgent")

        audio_folder = None
        if state.audio_output_dir and Path(state.audio_output_dir).exists():
            audio_folder = state.audio_output_dir

        pptx_builder = pptx_cls(audio_folder=audio_folder)

        if not pptx_builder.load_presentation_json(state.slides_content_path):
            raise RuntimeError("PPTXBuilderAgent.load_presentation_json returned False")
        if not pptx_builder.build_presentation():
            raise RuntimeError("PPTXBuilderAgent.build_presentation returned False")
        if not pptx_builder.save_presentation(str(output_pptx_path)):
            raise RuntimeError("PPTXBuilderAgent.save_presentation returned False")

        state.pptx_path = str(output_pptx_path)
        state.pptx_success = True
        state.add_log("INFO", stage, f"PPTX created at {state.pptx_path}")
        state.emit_progress(stage, "completed", "PPTX created")
    except Exception as exc:
        state.pptx_success = False
        state.error_message = f"PPTX stage failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("PPTX stage failed")

    return state
