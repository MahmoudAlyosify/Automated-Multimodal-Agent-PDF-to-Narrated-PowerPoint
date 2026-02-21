"""LangGraph orchestrator package for PDF -> narrated PowerPoint generation."""

from __future__ import annotations

__version__ = "2.1"
__author__ = "Automated Multimodal Agent Team"

from .state import PipelineState


def __getattr__(name: str):
    if name in {"WorkflowOrchestrator", "create_workflow_graph"}:
        from .graph import WorkflowOrchestrator, create_workflow_graph

        exports = {
            "WorkflowOrchestrator": WorkflowOrchestrator,
            "create_workflow_graph": create_workflow_graph,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["PipelineState", "WorkflowOrchestrator", "create_workflow_graph"]
