"""
PDF Parser & Layout Analyzer Agent

Transforms raw PDF documents into structured, layout-aware representations.
Uses Microsoft LayoutLMv3 (if available) to preserve spatial layout, hierarchy, and semantic roles.

INPUT:
  - PDF file path (single document)

OUTPUT:
  - List of structured layout blocks in JSON format:
    {
      "block_id": 1,
      "block_type": "Section Header",
      "text": "Project Goals",
      "bbox": [x1, y1, x2, y2],  # normalized to 0-1000 scale
      "page": 1
    }

USAGE:
  agent = PDFParserAgent()
  blocks = agent.parse_pdf("document.pdf")
  json_output = agent.to_json(blocks)
"""

import logging
import json
import unicodedata
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

import pymupdf  # PyMuPDF (fitz)
import numpy as np

# Optional: LayoutLMv3 support
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification
    HAS_LAYOUTLMV3 = True
except ImportError:
    HAS_LAYOUTLMV3 = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BlockType(str, Enum):
    """Types of content blocks in a document."""
    TITLE = "Title"
    SECTION_HEADER = "Section Header"
    PARAGRAPH = "Paragraph"
    LIST_ITEM = "List Item"
    IMAGE = "Image"
    TABLE = "Table"
    CODE = "Code"
    QUOTE = "Quote"
    FOOTER = "Footer"
    HEADER = "Header"
    UNKNOWN = "Unknown"


@dataclass
class BoundingBox:
    """Bounding box coordinates (normalized to 0-1000 scale)."""
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

    def to_list(self) -> List[float]:
        """Return bbox as list [x0, y0, x1, y1]."""
        return [self.x0, self.y0, self.x1, self.y1]


@dataclass
class FontInfo:
    """Font properties of text."""
    size: float
    weight: int  # 100-900
    is_bold: bool
    is_italic: bool
    family: str = "Unknown"


@dataclass
class StructuredBlock:
    """Structured layout block extracted from PDF."""
    block_id: int
    block_type: BlockType
    text: str
    bbox: BoundingBox
    page: int
    confidence: float = 0.8
    font_info: Optional[FontInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching required schema."""
        return {
            "block_id": self.block_id,
            "block_type": self.block_type.value,
            "text": self.text,
            "bbox": self.bbox.to_list(),
            "page": self.page,
        }


class PDFParserAgent:
    """
    PDF Parser & Layout Analyzer Agent

    Extracts structured blocks from PDFs with:
    - Text content and bounding boxes
    - Block type classification (Title, Section Header, Paragraph, etc.)
    - Font hierarchy analysis
    - Optional LayoutLMv3 enhancement
    """

    def __init__(self, use_layoutlmv3: bool = True, log_level: str = "INFO"):
        """
        Initialize PDF Parser Agent.

        Args:
            use_layoutlmv3: Whether to use LayoutLMv3 if available.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        """
        self.logger = logger
        logging.getLogger().setLevel(getattr(logging, log_level))
        
        self.use_layoutlmv3 = use_layoutlmv3 and HAS_LAYOUTLMV3
        self.layoutlmv3_model = None
        self.layoutlmv3_tokenizer = None
        
        if self.use_layoutlmv3 and HAS_LAYOUTLMV3:
            self._init_layoutlmv3()
        elif use_layoutlmv3 and not HAS_LAYOUTLMV3:
            self.logger.warning("LayoutLMv3 requested but not installed. Install with: pip install transformers")
            self.use_layoutlmv3 = False

        self.logger.info("[OK] PDFParserAgent initialized")

    def _init_layoutlmv3(self) -> None:
        """Initialize LayoutLMv3 model."""
        try:
            self.logger.info("Loading LayoutLMv3 model...")
            model_name = "microsoft/layoutlmv3-base"
            self.layoutlmv3_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                apply_ocr=True,
                trust_remote_code=True
            )
            self.layoutlmv3_model = AutoModelForTokenClassification.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.layoutlmv3_model.eval()
            self.logger.info("[OK] LayoutLMv3 model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load LayoutLMv3: {str(e)}")
            self.use_layoutlmv3 = False

    def parse_pdf(
        self,
        pdf_path: str,
        start_page: int = 0,
        end_page: Optional[int] = None,
    ) -> List[StructuredBlock]:
        """
        Parse PDF and extract structured blocks.

        Args:
            pdf_path: Path to the PDF file.
            start_page: First page to process (0-indexed, default: 0).
            end_page: Last page to process (inclusive, default: None = all pages).

        Returns:
            List of StructuredBlock objects.

        Raises:
            FileNotFoundError: If PDF file doesn't exist.
            RuntimeError: If PDF parsing fails.
        """
        try:
            pdf_path = str(Path(pdf_path))
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            self.logger.info(f"Parsing PDF: {pdf_path}")
            
            # Open PDF
            doc = pymupdf.open(pdf_path)
            total_pages = len(doc)

            # Determine page range
            start = max(0, start_page)
            end = min(total_pages, end_page + 1 if end_page is not None else total_pages)
            
            if start_page > 0 or end_page is not None:
                self.logger.info(f"Processing pages {start}-{end-1} of {total_pages}")
            else:
                self.logger.info(f"Processing all {total_pages} pages")

            # Calculate font statistics
            font_stats = self._calculate_font_statistics(doc, start, end)

            # Extract blocks
            blocks = []
            block_counter = 0

            for page_num in range(start, end):
                page = doc[page_num]
                page_blocks = self._extract_page_blocks(
                    page,
                    page_num,
                    block_counter,
                    font_stats.get(page_num, {})
                )
                blocks.extend(page_blocks)
                block_counter += len(page_blocks)

            doc.close()

            self.logger.info(f"[OK] Extracted {len(blocks)} blocks from {end - start} page(s)")
            return blocks

        except FileNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            raise RuntimeError(f"Failed to parse PDF: {str(e)}")

    def _calculate_font_statistics(
        self, doc: pymupdf.Document, start_page: int, end_page: int
    ) -> Dict[int, Dict[str, float]]:
        """Calculate font size statistics for each page."""
        stats = {}

        for page_num in range(start_page, end_page):
            page = doc[page_num]
            page_text_dict = page.get_text("dict")
            font_sizes = []

            for block in page_text_dict.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            font_sizes.append(span.get("size", 12.0))

            if font_sizes:
                stats[page_num] = {
                    "min": min(font_sizes),
                    "max": max(font_sizes),
                    "avg": np.mean(font_sizes),
                    "median": float(np.median(font_sizes)),
                }
            else:
                stats[page_num] = {"min": 8, "max": 16, "avg": 12, "median": 12}

        return stats

    def _extract_page_blocks(
        self,
        page: pymupdf.Page,
        page_num: int,
        block_counter: int,
        font_stats: Dict[str, float],
    ) -> List[StructuredBlock]:
        """Extract and classify blocks from a single page."""
        blocks = []
        page_text_dict = page.get_text("dict")
        page_rect = page.rect

        for block_idx, block_dict in enumerate(page_text_dict.get("blocks", [])):
            # Skip non-text blocks initially
            if block_dict.get("type") != 0:
                continue

            # Extract text and bbox
            text = self._extract_text_from_block(block_dict)
            if not text.strip():
                continue

            bbox = self._extract_bbox_from_block(block_dict, page_rect)
            font_info = self._extract_font_info_from_block(block_dict)

            # Classify block type
            block_type = self._classify_block_type(
                text, bbox, font_info, page_rect, font_stats
            )

            # Create structured block
            structured_block = StructuredBlock(
                block_id=block_counter,
                block_type=block_type,
                text=text,
                bbox=bbox,
                page=page_num,
                confidence=0.85,
                font_info=font_info,
            )

            blocks.append(structured_block)
            block_counter += 1

        return blocks

    @staticmethod
    def _extract_text_from_block(block_dict: Dict[str, Any]) -> str:
        """Extract text from a block dictionary with comprehensive character encoding fixes."""
        text_parts = []

        for line in block_dict.get("lines", []):
            for span in line.get("spans", []):
                text_parts.append(span.get("text", ""))

        raw_text = "".join(text_parts)
        
        # Normalize Unicode (NFD decomposition helps with some encoding issues)
        normalized = unicodedata.normalize('NFKD', raw_text)
        
        # Replace specific problematic characters
        cleaned = normalized
        
        # Handle various types of quotes and apostrophes
        quote_replacements = {
            '\u00ac': "'",      # ¬ 
            '\u2018': "'",      # ' (left single quote)
            '\u2019': "'",      # ' (right single quote)
            '\u201c': '"',      # " (left double quote)
            '\u201d': '"',      # " (right double quote)
            '\u00ab': '"',      # « (angle quote)
            '\u00bb': '"',      # » (angle quote)
            '\u2013': '-',      # – (en dash)
            '\u2014': '-',      # — (em dash)
            '\u00c6': "'",      # Æ (AE ligature)
            '\u00e6': "'",      # æ (ae ligature)
            'Æ': "'",
            'æ': "'",
        }
        
        for old_char, new_char in quote_replacements.items():
            cleaned = cleaned.replace(old_char, new_char)
        
        # Try to handle any remaining non-ASCII apostrophes by replacing with ASCII single quote
        # This catches characters that might have slipped through
        cleaned = re.sub(r"[`´΄''‛]", "'", cleaned)
        
        return cleaned

    @staticmethod
    def _extract_bbox_from_block(
        block_dict: Dict[str, Any], page_rect: Tuple
    ) -> BoundingBox:
        """Extract and normalize bounding box from a block."""
        bbox_raw = block_dict.get("bbox", (0, 0, 100, 100))
        x0, y0, x1, y1 = bbox_raw
        
        # Normalize to 0-1000 scale
        page_width = page_rect.width if hasattr(page_rect, 'width') else page_rect[2]
        page_height = page_rect.height if hasattr(page_rect, 'height') else page_rect[3]
        
        normalized_bbox = BoundingBox(
            x0=int((x0 / page_width) * 1000) if page_width > 0 else 0,
            y0=int((y0 / page_height) * 1000) if page_height > 0 else 0,
            x1=int((x1 / page_width) * 1000) if page_width > 0 else 1000,
            y1=int((y1 / page_height) * 1000) if page_height > 0 else 1000,
        )
        
        return normalized_bbox

    @staticmethod
    def _extract_font_info_from_block(block_dict: Dict[str, Any]) -> FontInfo:
        """Extract font information from a block."""
        font_size = 12.0
        font_weight = 400
        is_bold = False
        is_italic = False
        font_family = "Unknown"

        # Get font info from first span
        for line in block_dict.get("lines", []):
            for span in line.get("spans", []):
                font_size = span.get("size", 12.0)
                font_family = span.get("font", "Unknown")

                # Determine bold/italic from font name
                font_name_lower = font_family.lower()
                is_bold = "bold" in font_name_lower
                is_italic = "italic" in font_name_lower or "oblique" in font_name_lower
                font_weight = 700 if is_bold else 400

                break
            break

        return FontInfo(
            size=font_size,
            weight=font_weight,
            is_bold=is_bold,
            is_italic=is_italic,
            family=font_family,
        )

    def _classify_block_type(
        self,
        text: str,
        bbox: BoundingBox,
        font_info: FontInfo,
        page_rect: Tuple,
        font_stats: Dict[str, float],
    ) -> BlockType:
        """
        Classify block type based on:
        - Position in page
        - Font properties
        - Text length and content patterns
        """
        text_lower = text.lower().strip()

        # Get page dimensions
        page_width = page_rect.width if hasattr(page_rect, 'width') else page_rect[2]
        page_height = page_rect.height if hasattr(page_rect, 'height') else page_rect[3]
        
        # Normalized position (0-1)
        rel_y = bbox.y0 / 1000 if bbox.y0 <= 1000 else 0
        rel_x = bbox.x0 / 1000 if bbox.x0 <= 1000 else 0

        # Image detection
        if any(text_lower.find(ext) != -1 for ext in [".png", ".jpg", ".jpeg", ".gif", "[image"]):
            return BlockType.IMAGE

        # List detection
        if any(text_lower.startswith(marker) for marker in ["•", "-", "*", "◦", "◾", "◻"]):
            return BlockType.LIST_ITEM

        # Code detection
        if "```" in text or ("def " in text_lower and ":" in text_lower):
            return BlockType.CODE

        # Quote detection
        if text_lower.startswith('"') or text_lower.startswith("'") or text_lower.startswith("`"):
            return BlockType.QUOTE

        # Get font stats
        avg_font_size = font_stats.get("avg", 12.0)
        max_font_size = font_stats.get("max", 16.0)

        # TITLE: Large font at top, centered
        if rel_y < 0.15 and font_info.size > max_font_size * 0.9:
            # Check if roughly centered
            block_center_x = (bbox.x0 + bbox.x1) / 2
            if abs(block_center_x - 500) < 300:  # Within 30% of center
                return BlockType.TITLE

        # SECTION HEADER: Bold, larger font, at reasonable position
        if font_info.is_bold and font_info.size > avg_font_size * 1.3:
            return BlockType.SECTION_HEADER

        # HEADER: Small font at top of page
        if rel_y < 0.05 and font_info.size < avg_font_size * 0.9:
            return BlockType.HEADER

        # FOOTER: Small font at bottom of page
        if rel_y > 0.9 and font_info.size < avg_font_size * 0.9:
            return BlockType.FOOTER

        # Default: Paragraph
        return BlockType.PARAGRAPH

    def to_json(
        self, blocks: List[StructuredBlock], pretty: bool = True
    ) -> str:
        """
        Convert blocks to JSON format.

        Args:
            blocks: List of StructuredBlock objects.
            pretty: Whether to pretty-print JSON.

        Returns:
            JSON string.
        """
        block_dicts = [block.to_dict() for block in blocks]
        return json.dumps(
            block_dicts,
            indent=2 if pretty else None,
            ensure_ascii=False
        )

    def save_json(self, blocks: List[StructuredBlock], output_path: str) -> None:
        """
        Save blocks to JSON file.

        Args:
            blocks: List of StructuredBlock objects.
            output_path: Path to output JSON file.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(blocks, pretty=True))
        self.logger.info(f"[OK] Saved {len(blocks)} blocks to {output_path}")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and configuration."""
        return {
            "agent": "PDF Parser & Layout Analyzer Agent",
            "version": "1.0.0",
            "status": "ready",
            "layoutlmv3_available": self.use_layoutlmv3,
            "features": [
                "PDF text extraction",
                "Bounding box detection",
                "Block classification",
                "Font hierarchy analysis",
                "LayoutLMv3 integration (optional)",
            ],
        }


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example usage of PDFParserAgent."""
    
    # Initialize agent
    agent = PDFParserAgent(use_layoutlmv3=True)  # Enable LayoutLMv3 if available
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Example: Parse a PDF - Using Test_PDF_genai-principles.pdf
    pdf_filename = "Test_PDF_genai-principles.pdf"
    pdf_path = os.path.join(script_dir, pdf_filename)
    
    if Path(pdf_path).exists():
        # Parse PDF
        blocks = agent.parse_pdf(pdf_path)
        
        # Print status
        print("\n" + "=" * 80)
        print("PDF PARSER & LAYOUT ANALYZER AGENT - STATUS")
        print("=" * 80)
        print(json.dumps(agent.get_status(), indent=2))
        print("=" * 80)
        
        # Print extracted blocks summary
        print(f"\n[OK] Successfully extracted {len(blocks)} structured blocks from {pdf_filename}\n")
        
        # Save JSON output to file in the same directory
        output_json_path = os.path.join(script_dir, "parsed_blocks.json")
        agent.save_json(blocks, output_json_path)
        print(f"[OK] JSON output saved to: {output_json_path}\n")
        
        # Show statistics
        print("=" * 80)
        print("BLOCK STATISTICS")
        print("=" * 80)
        block_types = defaultdict(int)
        for block in blocks:
            block_types[block.block_type.value] += 1
        
        for block_type, count in sorted(block_types.items()):
            print(f"  {block_type}: {count} blocks")
        
        # Print unique pages
        pages = set(block.page for block in blocks)
        print(f"\n  Total Pages: {len(pages)}")
        print(f"  Page Numbers: {sorted(pages)}\n")
        
    else:
        print(f"[ERROR] PDF file not found: {pdf_path}")
        print(f"\nTo use this agent:")
        print(f"  1. Place 'Test_PDF_genai-principles.pdf' in the same directory as this script:")
        print(f"     {script_dir}")
        print(f"  2. Run this script from any directory")


if __name__ == "__main__":
    main()
