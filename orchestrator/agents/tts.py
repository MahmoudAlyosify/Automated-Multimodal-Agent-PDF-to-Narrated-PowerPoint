from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_tts_agent(state: PipelineState) -> PipelineState:
    """
    Stage 7 (non-critical): Generate WAV files from scripts.

    Failures are logged but do not stop the pipeline.
    """
    stage = "tts"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting TTS audio generation")
    state.emit_progress(stage, "running", "Generating audio narration")

    try:
        if not state.scripts_path:
            raise ValueError("Missing scripts_path from script stage")
        if not Path(state.scripts_path).exists():
            raise FileNotFoundError(f"Scripts file not found: {state.scripts_path}")

        agent_dir = get_agent_directory(stage)
        audio_output_dir = agent_dir / "audio_output"

        tts_cls = import_agent_class(stage, "tts_agent", "TTSAgent")
        tts_agent = tts_cls(
            scripts_path=state.scripts_path,
            output_dir=str(audio_output_dir),
        )

        tts_agent.process_scripts()

        audio_files = sorted(str(path) for path in audio_output_dir.glob("*.wav"))
        state.audio_output_dir = str(audio_output_dir)
        state.audio_files = audio_files
        state.tts_success = bool(audio_files)

        if state.tts_success:
            state.add_log("INFO", stage, f"Generated {len(audio_files)} audio files")
            state.emit_progress(stage, "completed", f"Generated {len(audio_files)} audio files")
        else:
            state.add_log("WARNING", stage, "No audio files were generated")
            state.emit_progress(stage, "failed", "No audio files were generated")
    except Exception as exc:
        state.tts_success = False
        state.add_log("WARNING", stage, f"TTS stage skipped: {exc}")
        state.emit_progress(stage, "failed", f"TTS stage skipped: {exc}")
        logger.warning("TTS stage failed (non-critical): %s", exc)

    return state
