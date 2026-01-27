"""
PDF Loader Module
Extracts raw text, bounding boxes, and font information from PDFs.

Uses PyMuPDF for fast, reliable PDF processing.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import pymupdf  # PyMuPDF (fitz)
from pathlib import Path

from ..types import RawBlock, BoundingBox, FontInfo

logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Extracts raw blocks from PDF files.
    
    Each block contains:
    - Text content
    - Bounding box coordinates
    - Font information (size, weight, family)
    - Page number
    """

    def __init__(self, extract_images: bool = True):
        """
        Initialize PDF Loader.
        
        Args:
            extract_images: Whether to extract image references.
        """
        self.extract_images = extract_images
        self.logger = logger

    def load(self, pdf_path: str, start_page: int = 0, end_page: Optional[int] = None) -> List[RawBlock]:
        """
        Load and parse a PDF file into raw blocks.
        
        Args:
            pdf_path: Path to the PDF file.
            start_page: First page to process (0-indexed, default: 0).
            end_page: Last page to process (inclusive, default: None = all pages).
            
        Returns:
            List of RawBlock objects.
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist.
            RuntimeError: If PDF parsing fails.
        """
        try:
            # Try to open directly (handles encoding issues on Windows)
            doc = pymupdf.open(pdf_path)
        except FileNotFoundError:
            # Fallback: check if file exists
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            doc = pymupdf.open(str(pdf_file))

        try:
            blocks = []
            block_counter = 0
            
            # Determine page range
            total_pages = len(doc)
            start = max(0, start_page)
            end = min(total_pages, end_page + 1 if end_page is not None else total_pages)
            
            self.logger.info(f"Processing pages {start}-{end-1} of {total_pages}")

            for page_num in range(start, end):
                page = doc[page_num]
                page_blocks = page.get_text("dict")["blocks"]

                for block_dict in page_blocks:
                    # Skip empty blocks
                    if not block_dict.get("lines"):
                        continue

                    # Extract text content
                    block_text = self._extract_text_from_block(block_dict)
                    if not block_text.strip():
                        continue

                    # Extract font info and bbox
                    font_info = self._extract_font_info(block_dict)
                    bbox = self._extract_bbox(block_dict)

                    # Create RawBlock
                    raw_block = RawBlock(
                        text=block_text,
                        bbox=bbox,
                        font_info=font_info,
                        page_number=page_num,
                        block_id=f"raw_{page_num}_{block_counter}",
                    )

                    blocks.append(raw_block)
                    block_counter += 1

            # Extract images if requested
            if self.extract_images:
                self._extract_images(doc, blocks)

            doc.close()
            self.logger.info(f"Successfully loaded {len(blocks)} blocks from {pdf_path}")
            return blocks

        except Exception as e:
            self.logger.error(f"Error loading PDF {pdf_path}: {str(e)}")
            raise RuntimeError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def _extract_text_from_block(block_dict: Dict[str, Any]) -> str:
        """Extract text from a block dictionary."""
        text_parts = []

        for line in block_dict.get("lines", []):
            for span in line.get("spans", []):
                text_parts.append(span.get("text", ""))

        return "".join(text_parts)

    @staticmethod
    def _extract_font_info(block_dict: Dict[str, Any]) -> FontInfo:
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

                # Determine bold from font name (common convention)
                font_name_lower = font_family.lower()
                is_bold = "bold" in font_name_lower
                is_italic = "italic" in font_name_lower or "oblique" in font_name_lower

                # Set weight based on bold
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

    @staticmethod
    def _extract_bbox(block_dict: Dict[str, Any]) -> BoundingBox:
        """Extract bounding box from a block."""
        bbox = block_dict.get("bbox", (0, 0, 100, 100))
        return BoundingBox(x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3])

    def _extract_images(self, doc: Any, blocks: List[RawBlock]) -> None:
        """Extract images from PDF and add as blocks."""
        image_counter = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images()

            for img_index, img_ref in enumerate(images):
                try:
                    xref = img_ref[0]
                    image_path = f"image_p{page_num}_i{img_index}.png"

                    # Store image reference as block
                    image_block = RawBlock(
                        text=f"[IMAGE: {image_path}]",
                        bbox=BoundingBox(0, 0, 100, 100),  # Placeholder
                        font_info=FontInfo(size=0, weight=400, is_bold=False, is_italic=False),
                        page_number=page_num,
                        block_id=f"image_{page_num}_{image_counter}",
                    )
                    blocks.append(image_block)
                    image_counter += 1

                except Exception as e:
                    self.logger.warning(f"Failed to extract image: {str(e)}")

    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            Dictionary with PDF metadata.
        """
        try:
            doc = pymupdf.open(pdf_path)
            metadata = {
                "num_pages": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
            }
            doc.close()
            return metadata
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return {"num_pages": 0}
