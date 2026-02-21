"""
Shared helpers for loading and running existing agent modules safely.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_SYSTEMS_DIR = PROJECT_ROOT / "Agentic Systems"

AGENT_DIRECTORY_MAP: Dict[str, str] = {
    "parser": "1- PDF Parser and Layout Analyzer Agent",
    "chunker": "2- Semantic Chunker Agent",
    "vector": "3- Vector DB + Embeddings Layer",
    "planner": "4- Slide Planner Agent",
    "generator": "5- Slide Generator Agent",
    "pptx": "6- PPTX Builder Agent",
    "script": "7- Script Agent for each slide in PPTX",
    "tts": "8- TTS  Generative Audio Agent",
}


def get_agent_directory(stage: str) -> Path:
    """Return the absolute directory for a given stage key."""
    if stage not in AGENT_DIRECTORY_MAP:
        raise KeyError(f"Unknown stage: {stage}")
    agent_dir = AGENT_SYSTEMS_DIR / AGENT_DIRECTORY_MAP[stage]
    if not agent_dir.exists():
        raise FileNotFoundError(f"Agent directory not found: {agent_dir}")
    return agent_dir


def import_agent_class(stage: str, module_name: str, class_name: str) -> Any:
    """
    Import a class from an existing stage module while isolating cwd/sys.path changes.
    """
    agent_dir = get_agent_directory(stage)
    original_cwd = Path.cwd()
    original_path = list(sys.path)

    try:
        os.chdir(agent_dir)
        sys.path.insert(0, str(agent_dir))

        # Prevent collisions when different folders reuse the same module name.
        if module_name in sys.modules:
            del sys.modules[module_name]

        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    finally:
        os.chdir(original_cwd)
        sys.path = original_path
