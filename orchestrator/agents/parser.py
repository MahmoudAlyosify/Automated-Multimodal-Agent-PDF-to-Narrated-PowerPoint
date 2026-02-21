from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from .common import get_agent_directory, import_agent_class

try:
    from ..state import PipelineState
except ImportError:  # pragma: no cover
    from state import PipelineState


logger = logging.getLogger(__name__)


def _normalize_blocks(blocks: List[Any]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for block in blocks:
        if isinstance(block, dict):
            normalized.append(block)
            continue
        to_dict = getattr(block, "to_dict", None)
        if callable(to_dict):
            normalized.append(to_dict())
            continue
        normalized.append({"text": str(block)})
    return normalized


def run_parser_agent(state: PipelineState) -> PipelineState:
    """Stage 1: Parse the input PDF into layout-aware content blocks."""
    stage = "parser"
    state.current_stage = stage
    state.add_log("INFO", stage, "Starting PDF parsing")
    state.emit_progress(stage, "running", "Parsing PDF")

    try:
        if not state.pdf_path:
            raise ValueError("Missing pdf_path in state")

        pdf_path = Path(state.pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        agent_dir = get_agent_directory(stage)
        parser_output = agent_dir / "parsed_blocks.json"

        parser_cls = import_agent_class(stage, "parser_agent", "PDFParserAgent")
        parser = parser_cls(use_layoutlmv3=True)

        blocks = parser.parse_pdf(str(pdf_path))
        if not blocks:
            raise ValueError("Parser returned no blocks")

        parser.save_json(blocks, str(parser_output))
        state.parsed_content = _normalize_blocks(blocks)
        state.parsed_content_path = str(parser_output)

        state.parser_success = True
        state.add_log("INFO", stage, f"Parsed {len(state.parsed_content)} blocks")
        state.emit_progress(stage, "completed", f"Parsed {len(state.parsed_content)} blocks")
    except Exception as exc:
        state.parser_success = False
        state.error_message = f"Parser failed: {exc}"
        state.add_log("ERROR", stage, state.error_message)
        state.emit_progress(stage, "failed", state.error_message)
        logger.exception("Parser stage failed")

    return state
