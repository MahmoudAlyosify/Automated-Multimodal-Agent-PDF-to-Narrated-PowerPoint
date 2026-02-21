from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_chunker_agent(state: PipelineState) -> PipelineState:
    """Stage 2: Convert parsed content into semantic chunks."""
    stage = "chunker"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting semantic chunking")
    state.emit_progress(stage, "running", "Creating semantic chunks")

    try:
        if not state.parsed_content_path:
            raise ValueError("Missing parsed_content_path from parser stage")
        if not Path(state.parsed_content_path).exists():
            raise FileNotFoundError(f"Parsed content file not found: {state.parsed_content_path}")

        agent_dir = get_agent_directory(stage)
        chunks_output = agent_dir / "semantic_chunks.json"

        chunker_cls = import_agent_class(stage, "semantic_chunker_agent", "SemanticChunkerAgent")
        chunker = chunker_cls(state.parsed_content_path)
        success = chunker.process(
            parsed_blocks_path=state.parsed_content_path,
            output_path=str(chunks_output),
        )
        if not success:
            raise RuntimeError("SemanticChunkerAgent.process returned False")

        state.semantic_chunks = list(chunker.chunks)
        state.semantic_chunks_path = str(chunks_output)

        state.chunker_success = True
        state.add_log("INFO", stage, f"Created {len(state.semantic_chunks)} semantic chunks")
        state.emit_progress(stage, "completed", f"Created {len(state.semantic_chunks)} chunks")
    except Exception as exc:
        state.chunker_success = False
        state.error_message = f"Chunker failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("Chunker stage failed")

    return state
