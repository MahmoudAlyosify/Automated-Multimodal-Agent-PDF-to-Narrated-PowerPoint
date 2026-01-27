"""
Block Classifier Module
Classifies blocks into semantic types using rule-based (80%) + ML fallback (20%) approach.
"""

import logging
import re
from typing import List

from ..types import AnalyzedBlock, ClassifiedBlock, BlockType, SemanticLabel

logger = logging.getLogger(__name__)


class BlockClassifier:
    """
    Classifies blocks using:
    - 80% Rule-based logic (fast, deterministic)
    - 20% ML fallback for ambiguous cases
    
    Rules cover:
    - Text patterns (keywords, structure)
    - Font properties (size, weight)
    - Layout context
    """

    def __init__(self, use_ml: bool = False):
        """
        Initialize Block Classifier.
        
        Args:
            use_ml: Whether to use ML models for ambiguous cases (experimental).
        """
        self.use_ml = use_ml
        self.logger = logger
        self._init_rule_patterns()

    def _init_rule_patterns(self) -> None:
        """Initialize regex patterns for rule-based classification."""
        self.question_patterns = [
            r"^\s*Q[:\.]",  # Q: or Q.
            r"^\s*\?",  # Starts with ?
            r"what|when|where|why|how|which|who",
        ]

        self.answer_patterns = [
            r"^\s*A[:\.]",  # A: or A.
            r"^\s*answer",
            r"accordingly|therefore|thus|hence",
        ]

        self.definition_patterns = [
            r"is\s+defined?\s+as",
            r"definition|define",
            r"mean[s]?",
            r"refers?\s+to",
        ]

        self.example_patterns = [
            r"example|for\s+instance|e\.g\.",
            r"illustrated\s+by",
            r"such\s+as",
        ]

        self.summary_patterns = [
            r"in\s+summary|summarizing",
            r"to\s+summarize",
            r"in\s+conclusion",
        ]

        self.important_patterns = [
            r"important|critical|note|attention",
            r"must|required|essential",
            r"!+",  # Multiple exclamation marks
        ]

    def classify(self, analyzed_blocks: List[AnalyzedBlock]) -> List[ClassifiedBlock]:
        """
        Classify analyzed blocks.
        
        Args:
            analyzed_blocks: List of AnalyzedBlock objects from layout analyzer.
            
        Returns:
            List of ClassifiedBlock objects with semantic labels.
        """
        classified = []

        for block in analyzed_blocks:
            # Rule-based classification (80%)
            label, confidence = self._classify_by_rules(block)

            # ML fallback for low confidence (20%)
            if confidence < 0.6 and self.use_ml:
                label = self._classify_by_ml(block)
                confidence = 0.5  # ML confidence

            # Calculate importance
            importance = self._calculate_importance(block, label)

            classified_block = ClassifiedBlock(
                block_id=block.block_id,
                text=block.text,
                bbox=block.bbox,
                font_info=block.font_info,
                page_number=block.page_number,
                layout_role=block.layout_role,
                block_type=block.block_type,
                semantic_label=label,
                importance=importance,
                confidence=confidence,
            )

            classified.append(classified_block)

        self.logger.info(f"Classified {len(classified)} blocks")
        return classified

    def _classify_by_rules(
        self, block: AnalyzedBlock
    ) -> tuple[SemanticLabel, float]:
        """
        Rule-based classification (80% of cases).
        
        Returns:
            Tuple of (SemanticLabel, confidence).
        """
        text_lower = block.text.lower()

        # Metadata: Headers/Footers
        if block.block_type in [BlockType.HEADER, BlockType.FOOTER]:
            return SemanticLabel.METADATA, 0.95

        # Title/Heading → INTRODUCTION
        if block.block_type == BlockType.TITLE:
            return SemanticLabel.INTRODUCTION, 0.9

        # Question detection
        if self._matches_patterns(text_lower, self.question_patterns):
            return SemanticLabel.QUESTION, 0.85

        # Answer detection
        if self._matches_patterns(text_lower, self.answer_patterns):
            return SemanticLabel.ANSWER, 0.85

        # Definition detection
        if self._matches_patterns(text_lower, self.definition_patterns):
            return SemanticLabel.DEFINITION, 0.88

        # Example detection
        if self._matches_patterns(text_lower, self.example_patterns):
            return SemanticLabel.EXAMPLE, 0.82

        # Summary/Conclusion
        if self._matches_patterns(text_lower, self.summary_patterns):
            return SemanticLabel.CONCLUSION, 0.85

        # Important/Note
        if self._matches_patterns(text_lower, self.important_patterns):
            return SemanticLabel.IMPORTANT, 0.8

        # Default: General explanation
        return SemanticLabel.EXPLANATION, 0.7

    def _classify_by_ml(self, block: AnalyzedBlock) -> SemanticLabel:
        """
        ML-based classification for ambiguous cases (20% fallback).
        
        This is a placeholder for future ML implementation.
        For now, returns EXPLANATION as default.
        """
        # TODO: Integrate with trained classifier
        # Could use:
        # - Transformer models (BERT, RoBERTa)
        # - FastText
        # - Sklearn classifiers
        return SemanticLabel.EXPLANATION

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any patterns."""
        for pattern in patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            except re.error:
                self.logger.warning(f"Invalid regex pattern: {pattern}")
        return False

    def _calculate_importance(
        self, block: AnalyzedBlock, label: SemanticLabel
    ) -> float:
        """
        Calculate importance score (0.0-1.0).
        
        Based on:
        - Block type (headings more important)
        - Semantic label (definitions, important notes)
        - Font properties (bold, large)
        - Length (some context)
        """
        importance = 0.5  # Base

        # Increase for headings
        if block.block_type in [BlockType.TITLE, BlockType.HEADING]:
            importance += 0.3

        # Increase for semantic labels
        label_importance_map = {
            SemanticLabel.IMPORTANT: 0.25,
            SemanticLabel.DEFINITION: 0.20,
            SemanticLabel.CONCLUSION: 0.15,
            SemanticLabel.INTRODUCTION: 0.20,
            SemanticLabel.QUESTION: 0.15,
            SemanticLabel.ANSWER: 0.15,
            SemanticLabel.EXAMPLE: 0.05,
        }
        importance += label_importance_map.get(label, 0)

        # Increase for bold/large font
        if block.font_info.is_bold:
            importance += 0.05
        if block.font_info.size > 14:
            importance += 0.05

        return min(importance, 1.0)
