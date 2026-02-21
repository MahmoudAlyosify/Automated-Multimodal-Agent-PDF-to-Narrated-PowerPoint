from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_planner_agent(state: PipelineState) -> PipelineState:
    """Stage 4: Build a slide plan from semantic chunks."""
    stage = "planner"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting slide planning")
    state.emit_progress(stage, "running", "Planning slide structure")

    try:
        if not state.semantic_chunks_path:
            raise ValueError("Missing semantic_chunks_path from chunker stage")
        if not Path(state.semantic_chunks_path).exists():
            raise FileNotFoundError(f"Semantic chunks file not found: {state.semantic_chunks_path}")

        agent_dir = get_agent_directory(stage)
        plan_path = agent_dir / "slide_plan.json"

        planner_cls = import_agent_class(stage, "slide_planner_agent", "SlidePlannerAgent")
        chunk_loader_cls = import_agent_class(stage, "slide_planner_agent", "ChunkLoader")

        chunks = chunk_loader_cls.load(state.semantic_chunks_path)
        if not chunks:
            raise RuntimeError("ChunkLoader returned no chunks")

        planner = planner_cls()
        planner.load_chunks(chunks)

        try:
            slides = planner.plan(13)
            state.add_log("INFO", stage, "Planned slides via API")
        except Exception:
            state.add_log("WARNING", stage, "API planning failed, using fallback planner")
            slides = planner._fallback_plan(13)

        if not slides:
            raise RuntimeError("Slide planner returned no slides")

        planner.slides = slides
        if not planner.save_plan(str(plan_path)):
            raise RuntimeError("Failed to save slide_plan.json")

        state.slide_plan = slides
        state.slide_plan_path = str(plan_path)
        state.planner_success = True

        state.add_log("INFO", stage, f"Created plan for {len(slides)} slides")
        state.emit_progress(stage, "completed", f"Planned {len(slides)} slides")
    except Exception as exc:
        state.planner_success = False
        state.error_message = f"Planner failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("Planner stage failed")

    return state
