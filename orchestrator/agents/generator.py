from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_generator_agent(state: PipelineState) -> PipelineState:
    """Stage 5: Generate slide content JSON from slide plan."""
    stage = "generator"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting slide content generation")
    state.emit_progress(stage, "running", "Generating slides content")

    try:
        if not state.slide_plan_path:
            raise ValueError("Missing slide_plan_path from planner stage")
        if not Path(state.slide_plan_path).exists():
            raise FileNotFoundError(f"Slide plan file not found: {state.slide_plan_path}")

        agent_dir = get_agent_directory(stage)
        presentation_path = agent_dir / "presentation.json"

        generator_cls = import_agent_class(stage, "slide_generator_agent", "SlideGeneratorAgent")
        generator = generator_cls()

        if not generator.load_plan(state.slide_plan_path):
            raise RuntimeError("SlideGeneratorAgent.load_plan returned False")

        slides_content = generator.generate_presentation()
        if not slides_content:
            raise RuntimeError("SlideGeneratorAgent.generate_presentation returned empty result")

        if not generator.save_presentation(str(presentation_path)):
            raise RuntimeError("Failed to save presentation.json")

        state.slides_content = slides_content
        state.slides_content_path = str(presentation_path)
        state.generator_success = True

        slide_count = len(slides_content.get("ppt", {}).get("slides", []))
        state.add_log("INFO", stage, f"Generated slide content for {slide_count} slides")
        state.emit_progress(stage, "completed", f"Generated {slide_count} slides")
    except Exception as exc:
        state.generator_success = False
        state.error_message = f"Generator failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("Generator stage failed")

    return state
