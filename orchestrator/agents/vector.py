from __future__ import annotations

import logging
from pathlib import Path

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def run_vector_agent(state: PipelineState) -> PipelineState:
    """Stage 3: Build embeddings and vector index from semantic chunks."""
    stage = "vector"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting vector store build")
    state.emit_progress(stage, "running", "Building embeddings and FAISS index")

    try:
        if not state.semantic_chunks_path:
            raise ValueError("Missing semantic_chunks_path from chunker stage")
        if not Path(state.semantic_chunks_path).exists():
            raise FileNotFoundError(f"Semantic chunks file not found: {state.semantic_chunks_path}")

        agent_dir = get_agent_directory(stage)
        index_path = agent_dir / "chunks.index"
        metadata_path = agent_dir / "chunks_metadata.json"
        embeddings_path = agent_dir / "chunks_embeddings.npy"

        vector_cls = import_agent_class(stage, "vector_store_agent", "VectorStoreAgent")
        vector_agent = vector_cls(state.semantic_chunks_path)
        success = vector_agent.process(
            semantic_chunks_path=state.semantic_chunks_path,
            index_output_path=str(index_path),
            metadata_output_path=str(metadata_path),
            embeddings_output_path=str(embeddings_path),
        )
        if not success:
            raise RuntimeError("VectorStoreAgent.process returned False")

        state.vector_index_path = str(index_path)
        state.vector_metadata_path = str(metadata_path)
        state.vector_embeddings_path = str(embeddings_path)
        state.vector_store = {
            "index_path": state.vector_index_path,
            "metadata_path": state.vector_metadata_path,
            "embeddings_path": state.vector_embeddings_path,
            "vector_count": len(getattr(vector_agent, "metadata", [])),
            "embedding_model": getattr(vector_agent, "embedding_model_name", ""),
        }

        state.vector_success = True
        state.add_log("INFO", stage, "Vector store created")
        state.emit_progress(stage, "completed", "Vector store created")
    except Exception as exc:
        state.vector_success = False
        state.error_message = f"Vector stage failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("Vector stage failed")

    return state
