"""
Document Understanding Agent (DUA)
A modular, intelligent agent for converting raw PDFs into structured semantic documents.

Pipeline: PDF → Loader → Analyzer → Classifier → Labeler → Builder → Estimator → JSON

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Development Team"

from .agent import DocumentUnderstandingAgent
from .config import DUAConfig, Presets
from . import types

__all__ = [
    "DocumentUnderstandingAgent",
    "DUAConfig",
    "Presets",
    "types",
]
