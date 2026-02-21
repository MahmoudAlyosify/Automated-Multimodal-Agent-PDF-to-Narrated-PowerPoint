"""
Backward-compatible wrapper exports.

The new modular implementation lives under `orchestrator/agents/`.
"""

try:
    from .agents import (
        run_parser_agent,
        run_chunker_agent,
        run_vector_agent,
        run_planner_agent,
        run_generator_agent,
        run_script_agent,
        run_tts_agent,
        run_pptx_agent,
    )
except ImportError:  # pragma: no cover
    from agents import (
        run_parser_agent,
        run_chunker_agent,
        run_vector_agent,
        run_planner_agent,
        run_generator_agent,
        run_script_agent,
        run_tts_agent,
        run_pptx_agent,
    )

__all__ = [
    "run_parser_agent",
    "run_chunker_agent",
    "run_vector_agent",
    "run_planner_agent",
    "run_generator_agent",
    "run_script_agent",
    "run_tts_agent",
    "run_pptx_agent",
]
