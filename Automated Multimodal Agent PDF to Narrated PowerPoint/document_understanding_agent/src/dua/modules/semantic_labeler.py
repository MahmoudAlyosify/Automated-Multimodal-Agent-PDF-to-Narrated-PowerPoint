"""
Semantic Labeler Module
Refines semantic labels based on context and relationships.
"""

import logging
from typing import List, Dict

from ..types import ClassifiedBlock, SemanticLabel

logger = logging.getLogger(__name__)


class SemanticLabeler:
    """
    Refines semantic labels based on:
    - Contextual relationships between blocks
    - Sequence patterns (Q→A, Term→Definition)
    - Document structure
    - Domain-specific patterns
    """

    def __init__(self, domain: str = "general", language: str = "en"):
        """
        Initialize Semantic Labeler.
        
        Args:
            domain: Document domain (academic, business, technical, legal).
            language: Document language.
        """
        self.domain = domain
        self.language = language
        self.logger = logger

    def label(self, classified_blocks: List[ClassifiedBlock]) -> List[ClassifiedBlock]:
        """
        Refine semantic labels based on context.
        
        Args:
            classified_blocks: Blocks from classifier.
            
        Returns:
            Blocks with refined labels.
        """
        # Refine labels based on relationships
        for i, block in enumerate(classified_blocks):
            refined_label = self._refine_label(block, classified_blocks, i)
            block.semantic_label = refined_label

        self.logger.info(f"Refined labels for {len(classified_blocks)} blocks")
        return classified_blocks

    def _refine_label(
        self, block: ClassifiedBlock, all_blocks: List[ClassifiedBlock], index: int
    ) -> SemanticLabel:
        """
        Refine label based on context.
        
        Rules:
        - If previous block is definition, this is probably explanation
        - If previous is question, this is answer
        - If text is very long, more likely explanation
        """
        current_label = block.semantic_label

        # Get previous block context
        prev_block = all_blocks[index - 1] if index > 0 else None
        next_block = all_blocks[index + 1] if index < len(all_blocks) - 1 else None

        # Contextual refinement
        if (
            prev_block
            and prev_block.semantic_label == SemanticLabel.QUESTION
            and current_label == SemanticLabel.EXPLANATION
        ):
            return SemanticLabel.ANSWER

        if (
            prev_block
            and prev_block.semantic_label == SemanticLabel.DEFINITION
            and len(block.text) > 200
        ):
            return SemanticLabel.EXPLANATION

        # Domain-specific refinement
        if self.domain == "academic":
            return self._refine_academic(block, current_label, prev_block, next_block)

        return current_label

    def _refine_academic(
        self,
        block: ClassifiedBlock,
        label: SemanticLabel,
        prev_block: ClassifiedBlock = None,
        next_block: ClassifiedBlock = None,
    ) -> SemanticLabel:
        """Academic domain-specific refinement."""
        text_lower = block.text.lower()

        # Common academic patterns
        if any(word in text_lower for word in ["proof", "theorem", "hypothesis"]):
            return SemanticLabel.DEFINITION

        if any(word in text_lower for word in ["exercise", "practice", "problem"]):
            if "?" in block.text:
                return SemanticLabel.QUESTION
            else:
                return SemanticLabel.EXAMPLE

        return label
