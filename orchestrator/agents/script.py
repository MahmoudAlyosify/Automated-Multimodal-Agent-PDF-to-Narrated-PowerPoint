from __future__ import annotations

import json
import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_script_agent(state: PipelineState) -> PipelineState:
    """
    Stage 6 (non-critical): Generate narration scripts from slide plan.

    Failures are logged but do not stop the pipeline.
    """
    stage = "script"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting narration script generation")
    state.emit_progress(stage, "running", "Generating scripts")

    try:
        if not state.slide_plan_path:
            raise ValueError("Missing slide_plan_path from planner stage")
        if not Path(state.slide_plan_path).exists():
            raise FileNotFoundError(f"Slide plan file not found: {state.slide_plan_path}")

        agent_dir = get_agent_directory(stage)
        scripts_path = agent_dir / "scripts.json"

        script_cls = import_agent_class(stage, "script_agent", "NarrationScriptAgent")
        script_agent = script_cls()

        if not script_agent.load_slide_plan(state.slide_plan_path):
            raise RuntimeError("NarrationScriptAgent.load_slide_plan returned False")

        generated_ok = script_agent.generate_scripts()
        if not generated_ok:
            state.add_log("WARNING", stage, "Script generation fallback was used")

        if not script_agent.save_scripts(str(scripts_path)):
            raise RuntimeError("Failed to save scripts.json")

        scripts_payload = {}
        if scripts_path.exists():
            with scripts_path.open("r", encoding="utf-8") as file:
                scripts_payload = json.load(file)

        state.scripts = scripts_payload
        state.scripts_path = str(scripts_path)
        state.script_success = True

        script_count = len(scripts_payload.get("scripts", []))
        state.add_log("INFO", stage, f"Generated scripts for {script_count} slides")
        state.emit_progress(stage, "completed", f"Generated {script_count} scripts")
    except Exception as exc:
        state.script_success = False
        state.add_log("WARNING", stage, f"Script stage skipped: {exc}")
        state.emit_progress(stage, "failed", f"Script stage skipped: {exc}")
        logger.warning("Script stage failed (non-critical): %s", exc)

    return state
