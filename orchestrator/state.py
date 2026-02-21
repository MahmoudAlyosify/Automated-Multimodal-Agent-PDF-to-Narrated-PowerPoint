"""
Shared LangGraph state for the PDF -> narrated PowerPoint pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PipelineState:
    """
    Canonical shared state flowing across all LangGraph nodes.

    Required fields requested by the user are kept as first-class keys:
    - pdf_path
    - parsed_content
    - semantic_chunks
    - vector_store
    - slide_plan
    - slides_content
    - scripts
    - audio_files
    - pptx_path
    """

    # Canonical shared state fields
    pdf_path: str = ""
    parsed_content: List[Dict[str, Any]] = field(default_factory=list)
    semantic_chunks: List[Dict[str, Any]] = field(default_factory=list)
    vector_store: Dict[str, Any] = field(default_factory=dict)
    slide_plan: List[Dict[str, Any]] = field(default_factory=list)
    slides_content: Dict[str, Any] = field(default_factory=dict)
    scripts: Dict[str, Any] = field(default_factory=dict)
    audio_files: List[str] = field(default_factory=list)
    pptx_path: str = ""

    # Runtime metadata
    pdf_filename: str = ""
    output_dir: str = ""
    run_id: str = ""
    current_stage: str = ""
    status: str = "initialized"  # initialized, running, completed, failed
    error_message: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Artifact paths
    parsed_content_path: str = ""
    semantic_chunks_path: str = ""
    vector_index_path: str = ""
    vector_metadata_path: str = ""
    vector_embeddings_path: str = ""
    slide_plan_path: str = ""
    slides_content_path: str = ""
    scripts_path: str = ""
    audio_output_dir: str = ""
    narrated_zip_path: str = ""

    # Stage results
    parser_success: bool = False
    chunker_success: bool = False
    vector_success: bool = False
    planner_success: bool = False
    generator_success: bool = False
    script_success: bool = False
    tts_success: bool = False
    pptx_success: bool = False

    # Logs and UI callback
    logs: List[Dict[str, str]] = field(default_factory=list)
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = field(
        default=None,
        repr=False,
        compare=False,
    )

    def add_log(self, level: str, stage: str, message: str) -> None:
        """Append a structured log record to state."""
        self.logs.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "level": level.upper(),
                "stage": stage,
                "message": message,
            }
        )

    def emit_progress(self, stage: str, status: str, message: str) -> None:
        """Emit stage progress to the optional UI callback."""
        callback = self.progress_callback
        if not callback:
            return
        callback(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "stage": stage,
                "status": status,
                "message": message,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to a JSON-friendly dictionary."""
        vector_store = self.vector_store
        if not isinstance(vector_store, dict):
            vector_store = {"repr": str(vector_store)}

        return {
            "run_id": self.run_id,
            "pdf_path": self.pdf_path,
            "pdf_filename": self.pdf_filename,
            "output_dir": self.output_dir,
            "status": self.status,
            "current_stage": self.current_stage,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "parsed_content_count": len(self.parsed_content),
            "semantic_chunks_count": len(self.semantic_chunks),
            "slide_plan_count": len(self.slide_plan),
            "audio_files_count": len(self.audio_files),
            "pptx_path": self.pptx_path,
            "parsed_content_path": self.parsed_content_path,
            "semantic_chunks_path": self.semantic_chunks_path,
            "vector_index_path": self.vector_index_path,
            "vector_metadata_path": self.vector_metadata_path,
            "vector_embeddings_path": self.vector_embeddings_path,
            "slide_plan_path": self.slide_plan_path,
            "slides_content_path": self.slides_content_path,
            "scripts_path": self.scripts_path,
            "audio_output_dir": self.audio_output_dir,
            "narrated_zip_path": self.narrated_zip_path,
            "vector_store": vector_store,
            "stage_results": {
                "parser": self.parser_success,
                "chunker": self.chunker_success,
                "vector": self.vector_success,
                "planner": self.planner_success,
                "generator": self.generator_success,
                "script": self.script_success,
                "tts": self.tts_success,
                "pptx": self.pptx_success,
            },
            "logs": self.logs,
        }

    def save_metadata(self) -> str:
        """Persist pipeline state metadata under output/metadata."""
        metadata_dir = Path(self.output_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = metadata_dir / f"pipeline_state_{self.run_id}.json"
        with metadata_file.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2, ensure_ascii=False)
        return str(metadata_file)

    # Backward-compatible aliases
    @property
    def parsed_blocks(self) -> List[Dict[str, Any]]:
        return self.parsed_content

    @parsed_blocks.setter
    def parsed_blocks(self, value: List[Dict[str, Any]]) -> None:
        self.parsed_content = value

    @property
    def parsed_blocks_path(self) -> str:
        return self.parsed_content_path

    @parsed_blocks_path.setter
    def parsed_blocks_path(self, value: str) -> None:
        self.parsed_content_path = value

    @property
    def presentation_json(self) -> Dict[str, Any]:
        return self.slides_content

    @presentation_json.setter
    def presentation_json(self, value: Dict[str, Any]) -> None:
        self.slides_content = value

    @property
    def presentation_json_path(self) -> str:
        return self.slides_content_path

    @presentation_json_path.setter
    def presentation_json_path(self, value: str) -> None:
        self.slides_content_path = value

    @property
    def vector_store_path(self) -> str:
        return self.vector_index_path

    @vector_store_path.setter
    def vector_store_path(self, value: str) -> None:
        self.vector_index_path = value

    @property
    def metadata_path(self) -> str:
        return self.vector_metadata_path

    @metadata_path.setter
    def metadata_path(self, value: str) -> None:
        self.vector_metadata_path = value

    @property
    def embeddings_path(self) -> str:
        return self.vector_embeddings_path

    @embeddings_path.setter
    def embeddings_path(self, value: str) -> None:
        self.vector_embeddings_path = value

    @property
    def num_slides(self) -> int:
        return len(self.slide_plan)
