"""
Layout Analyzer Module
Analyzes spatial layout, font hierarchy, and whitespace to determine layout roles.
"""

import logging
from typing import List, Tuple
from collections import defaultdict

from ..types import RawBlock, AnalyzedBlock, LayoutRole, BlockType

logger = logging.getLogger(__name__)


class LayoutAnalyzer:
    """
    Analyzes document layout through:
    - Font hierarchy (size, weight)
    - Spatial clustering
    - Whitespace detection
    - Position in document
    """

    def __init__(self):
        self.logger = logger
        self.font_size_distribution = {}
        self.page_heights = {}

    def analyze(self, raw_blocks: List[RawBlock]) -> List[AnalyzedBlock]:
        """
        Analyze layout of raw blocks.
        
        Args:
            raw_blocks: List of RawBlock objects from PDF loader.
            
        Returns:
            List of AnalyzedBlock objects with layout roles assigned.
        """
        # Calculate statistics
        self._calculate_statistics(raw_blocks)

        analyzed_blocks = []

        for block in raw_blocks:
            layout_role = self._determine_layout_role(block, raw_blocks)
            block_type = self._infer_block_type(block, layout_role)
            confidence = self._calculate_layout_confidence(block)

            analyzed = AnalyzedBlock(
                block_id=block.block_id,
                text=block.text,
                bbox=block.bbox,
                font_info=block.font_info,
                page_number=block.page_number,
                layout_role=layout_role,
                block_type=block_type,
                confidence=confidence,
            )

            analyzed_blocks.append(analyzed)

        self.logger.info(f"Analyzed {len(analyzed_blocks)} blocks for layout")
        return analyzed_blocks

    def _calculate_statistics(self, raw_blocks: List[RawBlock]) -> None:
        """Calculate font size and position statistics."""
        font_sizes_by_page = defaultdict(list)

        for block in raw_blocks:
            font_sizes_by_page[block.page_number].append(block.font_info.size)
            if block.page_number not in self.page_heights:
                self.page_heights[block.page_number] = 792  # Standard page height

        # Calculate average font sizes
        for page_num, sizes in font_sizes_by_page.items():
            if sizes:
                self.font_size_distribution[page_num] = {
                    "min": min(sizes),
                    "max": max(sizes),
                    "avg": sum(sizes) / len(sizes),
                }

    def _determine_layout_role(self, block: RawBlock, all_blocks: List[RawBlock]) -> LayoutRole:
        """
        Determine the spatial/layout role of a block.
        
        Rules:
        1. Top of page, large font → MAIN_HEADING
        2. Smaller font than heading → SUBHEADING
        3. Very small font at bottom → FOOTER
        4. Very small font at top → HEADER
        5. Normal flow → BODY_TEXT
        """
        # Get page statistics
        page_stats = self.font_size_distribution.get(
            block.page_number, {"min": 8, "max": 16, "avg": 12}
        )

        font_size = block.font_info.size
        bbox = block.bbox
        page_height = self.page_heights.get(block.page_number, 792)

        # Position in page (normalized 0-1)
        rel_y = bbox.y0 / page_height if page_height > 0 else 0

        # Thresholds
        top_threshold = 0.15
        bottom_threshold = 0.9
        large_font_threshold = page_stats["avg"] * 1.5
        medium_font_threshold = page_stats["avg"] * 1.1

        # Footer detection
        if rel_y > bottom_threshold and font_size < page_stats["avg"] * 0.9:
            return LayoutRole.FOOTER

        # Header detection
        if rel_y < 0.05 and font_size < page_stats["avg"] * 0.9:
            return LayoutRole.HEADER

        # Main heading detection
        if rel_y < top_threshold and font_size > large_font_threshold:
            return LayoutRole.MAIN_HEADING

        # Subheading detection
        if font_size > medium_font_threshold and block.font_info.is_bold:
            return LayoutRole.SUBHEADING

        # Caption detection (small text near images)
        if font_size < page_stats["avg"] * 0.8:
            return LayoutRole.CAPTION

        # Default to body text
        return LayoutRole.BODY_TEXT

    def _infer_block_type(self, block: RawBlock, layout_role: LayoutRole) -> BlockType:
        """Infer block type from layout role and content patterns."""
        # Check for special content patterns
        text = block.text.lower()

        # Image detection
        if "[image:" in text or text.endswith(".png") or text.endswith(".jpg"):
            return BlockType.IMAGE

        # List detection
        if any(text.startswith(marker) for marker in ["•", "-", "*", "◦"]):
            return BlockType.LIST

        # Code detection
        if "```" in block.text or ("def " in text and ":" in text):
            return BlockType.CODE

        # Quote detection
        if text.startswith('"') or text.startswith("'"):
            return BlockType.QUOTE

        # Based on layout role
        if layout_role == LayoutRole.MAIN_HEADING:
            return BlockType.TITLE
        elif layout_role == LayoutRole.SUBHEADING:
            return BlockType.HEADING
        elif layout_role == LayoutRole.FOOTER:
            return BlockType.FOOTER
        elif layout_role == LayoutRole.HEADER:
            return BlockType.HEADER

        return BlockType.PARAGRAPH

    def _calculate_layout_confidence(self, block: RawBlock) -> float:
        """Calculate confidence in layout analysis."""
        # Confidence based on:
        # - Clear font hierarchy
        # - Explicit positioning
        # - Content patterns

        confidence = 0.8  # Base confidence

        # Increase if bold
        if block.font_info.is_bold:
            confidence += 0.1

        # Increase if large font
        if block.font_info.size > 14:
            confidence += 0.05

        return min(confidence, 1.0)
