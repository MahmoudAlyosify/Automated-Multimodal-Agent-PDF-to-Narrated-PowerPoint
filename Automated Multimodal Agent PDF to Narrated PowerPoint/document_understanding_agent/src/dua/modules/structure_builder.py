"""
Structure Builder Module
Constructs hierarchical document tree from classified blocks.
"""

import logging
from typing import List, Dict

from ..types import (
    ClassifiedBlock,
    DocumentBlock,
    DocumentSection,
    BlockType,
    SemanticLabel,
)

logger = logging.getLogger(__name__)


class StructureBuilder:
    """
    Builds hierarchical document tree from flat classified blocks.
    
    Process:
    1. Identify sections (by headings)
    2. Group blocks into sections
    3. Create hierarchy (nested subsections)
    4. Generate section titles
    """

    def __init__(self):
        self.logger = logger

    def build(self, classified_blocks: List[ClassifiedBlock]) -> List[DocumentSection]:
        """
        Build document structure from blocks.
        
        Args:
            classified_blocks: Classified blocks in document order.
            
        Returns:
            List of top-level DocumentSection objects.
        """
        sections = []
        current_section = None
        section_stack = []  # For hierarchy

        for block in classified_blocks:
            # Determine if this block is a section heading
            heading_level = self._get_heading_level(block)

            if heading_level > 0:
                # This is a heading - create new section
                new_section = DocumentSection(
                    title=block.text,
                    level=heading_level,
                    blocks=[],
                )

                if not section_stack:
                    # Top level section
                    sections.append(new_section)
                    current_section = new_section
                    section_stack = [new_section]
                else:
                    # Nested section
                    current_level = section_stack[-1].level

                    if heading_level > current_level:
                        # Subsection of current
                        section_stack[-1].subsections.append(new_section)
                        section_stack.append(new_section)
                        current_section = new_section
                    else:
                        # Pop stack to correct level
                        while section_stack and section_stack[-1].level >= heading_level:
                            section_stack.pop()

                        if section_stack:
                            section_stack[-1].subsections.append(new_section)
                        else:
                            sections.append(new_section)

                        section_stack.append(new_section)
                        current_section = new_section
            else:
                # Regular content block
                doc_block = DocumentBlock(
                    type=block.block_type,
                    semantic_label=block.semantic_label,
                    importance=block.importance,
                    text=block.text if block.block_type != BlockType.IMAGE else None,
                    path=block.text if block.block_type == BlockType.IMAGE else None,
                    caption=self._extract_caption(block),
                )

                if current_section is not None:
                    current_section.blocks.append(doc_block)
                else:
                    # No section yet - create default section
                    if not sections or not sections[-1].blocks:
                        default_section = DocumentSection(
                            title="Document Content",
                            level=1,
                            blocks=[],
                        )
                        sections.append(default_section)
                        current_section = default_section

                    current_section.blocks.append(doc_block)

        self.logger.info(f"Built document structure with {len(sections)} top-level sections")
        return sections

    def _get_heading_level(self, block: ClassifiedBlock) -> int:
        """
        Determine heading level (0 = not a heading).
        
        Mapping:
        - TITLE → level 1
        - HEADING → level 2
        - Other → level 0
        """
        if block.block_type == BlockType.TITLE:
            return 1
        elif block.block_type == BlockType.HEADING:
            return 2
        elif block.semantic_label == SemanticLabel.INTRODUCTION:
            return 1
        else:
            return 0

    def _extract_caption(self, block: ClassifiedBlock) -> str:
        """Extract caption from block if present."""
        # For images, look for nearby text
        if block.block_type == BlockType.IMAGE:
            # Extract from text field if present
            if "[" in block.text and "]" in block.text:
                start = block.text.find("[")
                end = block.text.find("]")
                if start < end:
                    return block.text[start + 1 : end]

        return ""

    def flatten_sections(self, sections: List[DocumentSection]) -> List[DocumentSection]:
        """
        Flatten nested sections (optional).
        
        For some use cases, you might want to flatten the hierarchy.
        """
        flattened = []

        def recurse(secs: List[DocumentSection], depth: int = 0) -> None:
            for sec in secs:
                # Adjust level based on depth
                sec.level = depth + 1
                flattened.append(sec)
                if sec.subsections:
                    recurse(sec.subsections, depth + 1)

        recurse(sections)
        return flattened
