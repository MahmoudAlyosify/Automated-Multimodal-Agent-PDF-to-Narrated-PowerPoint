"""
Type definitions and data structures for the Document Understanding Agent.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class BlockType(str, Enum):
    """Types of content blocks in a document."""
    PARAGRAPH = "PARAGRAPH"
    HEADING = "HEADING"
    TITLE = "TITLE"
    IMAGE = "IMAGE"
    TABLE = "TABLE"
    LIST = "LIST"
    CODE = "CODE"
    QUOTE = "QUOTE"
    FOOTER = "FOOTER"
    HEADER = "HEADER"
    UNKNOWN = "UNKNOWN"


class LayoutRole(str, Enum):
    """Spatial/visual role of content in layout."""
    MAIN_HEADING = "MAIN_HEADING"
    SUBHEADING = "SUBHEADING"
    BODY_TEXT = "BODY_TEXT"
    SIDEBAR = "SIDEBAR"
    CAPTION = "CAPTION"
    FOOTER = "FOOTER"
    HEADER = "HEADER"
    UNKNOWN = "UNKNOWN"


class SemanticLabel(str, Enum):
    """Semantic meaning of content."""
    EXPLANATION = "EXPLANATION"
    DEFINITION = "DEFINITION"
    EXAMPLE = "EXAMPLE"
    IMPORTANT = "IMPORTANT"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    SUMMARY = "SUMMARY"
    INTRODUCTION = "INTRODUCTION"
    CONCLUSION = "CONCLUSION"
    METADATA = "METADATA"
    UNKNOWN = "UNKNOWN"


@dataclass
class BoundingBox:
    """2D bounding box coordinates."""
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class FontInfo:
    """Font properties of text."""
    size: float
    weight: int  # 100-900
    is_bold: bool
    is_italic: bool
    family: str = "Unknown"


@dataclass
class RawBlock:
    """Raw block extracted from PDF."""
    text: str
    bbox: BoundingBox
    font_info: FontInfo
    page_number: int
    block_id: str


@dataclass
class AnalyzedBlock:
    """Block after layout analysis."""
    block_id: str
    text: str
    bbox: BoundingBox
    font_info: FontInfo
    page_number: int
    layout_role: LayoutRole
    block_type: BlockType
    confidence: float


@dataclass
class ClassifiedBlock:
    """Block after classification."""
    block_id: str
    text: str
    bbox: BoundingBox
    font_info: FontInfo
    page_number: int
    layout_role: LayoutRole
    block_type: BlockType
    semantic_label: SemanticLabel
    importance: float  # 0.0-1.0
    confidence: float


@dataclass
class DocumentBlock:
    """Final semantic block in document tree."""
    type: BlockType
    semantic_label: SemanticLabel
    importance: float
    text: Optional[str] = None
    path: Optional[str] = None  # For images
    caption: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentSection:
    """Section in document hierarchy."""
    title: str
    level: int  # 1=top level, 2=subsection, etc.
    blocks: List[DocumentBlock]
    subsections: List['DocumentSection'] = field(default_factory=list)


@dataclass
class DocumentMetadata:
    """Metadata about the processed document."""
    num_pages: int
    has_tables: bool
    has_images: bool
    has_lists: bool
    languages: List[str]
    confidence: float
    processing_time: float  # seconds


@dataclass
class DocumentTree:
    """Complete structured document tree."""
    sections: List[DocumentSection]
    metadata: DocumentMetadata


@dataclass
class DUAInput:
    """Input contract for Document Understanding Agent."""
    pdf_path: str
    language: str = "en"
    domain: str = "general"  # academic, business, technical, legal, etc.
    extract_images: bool = True
    analyze_tables: bool = True
    start_page: int = 0  # First page to process (0-indexed)
    end_page: Optional[int] = None  # Last page to process (None = all pages)


@dataclass
class DUAOutput:
    """Output contract for Document Understanding Agent."""
    document_tree: DocumentTree
    metadata: DocumentMetadata
    raw_text: str  # Full extracted text for reference
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "document_tree": {
                "sections": self._serialize_sections(self.document_tree.sections)
            },
            "metadata": {
                "num_pages": self.metadata.num_pages,
                "has_tables": self.metadata.has_tables,
                "has_images": self.metadata.has_images,
                "has_lists": self.metadata.has_lists,
                "languages": self.metadata.languages,
                "confidence": self.metadata.confidence,
                "processing_time": self.metadata.processing_time,
            },
            "warnings": self.warnings,
        }

    @staticmethod
    def _serialize_sections(sections: List[DocumentSection]) -> List[Dict[str, Any]]:
        """Recursively serialize sections to dictionaries."""
        result = []
        for section in sections:
            serialized = {
                "title": section.title,
                "level": section.level,
                "blocks": [
                    {
                        "type": block.type.value,
                        "semantic_label": block.semantic_label.value,
                        "importance": block.importance,
                        "text": block.text,
                        "path": block.path,
                        "caption": block.caption,
                    }
                    for block in section.blocks
                ],
            }
            if section.subsections:
                serialized["subsections"] = DUAOutput._serialize_sections(
                    section.subsections
                )
            result.append(serialized)
        return result
