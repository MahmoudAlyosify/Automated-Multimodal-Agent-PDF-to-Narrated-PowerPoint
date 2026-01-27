"""
Confidence Estimator Module
Calculates overall confidence scores for document understanding.
"""

import logging
from typing import List

from ..types import ClassifiedBlock, DocumentMetadata

logger = logging.getLogger(__name__)


class ConfidenceEstimator:
    """
    Estimates confidence in the document understanding process.
    
    Factors:
    - Individual block confidence scores
    - Consistency of classifications
    - Coverage (what % of document was understood)
    - Presence of expected elements
    """

    def __init__(self):
        self.logger = logger

    def estimate(
        self,
        classified_blocks: List[ClassifiedBlock],
        num_pages: int,
        has_tables: bool,
        has_images: bool,
        has_lists: bool,
    ) -> DocumentMetadata:
        """
        Estimate overall confidence.
        
        Args:
            classified_blocks: All classified blocks from document.
            num_pages: Total pages in PDF.
            has_tables: Whether document contains tables.
            has_images: Whether document contains images.
            has_lists: Whether document contains lists.
            
        Returns:
            DocumentMetadata with confidence scores.
        """
        # Calculate average block confidence
        avg_block_confidence = (
            sum(block.confidence for block in classified_blocks)
            / len(classified_blocks)
            if classified_blocks
            else 0.0
        )

        # Calculate label consistency
        label_diversity = self._calculate_label_diversity(classified_blocks)

        # Calculate coverage (blocks vs expected for pages)
        coverage = self._calculate_coverage(len(classified_blocks), num_pages)

        # Factor in document complexity
        complexity_penalty = self._calculate_complexity_penalty(
            has_tables, has_images, has_lists
        )

        # Overall confidence
        overall_confidence = (
            avg_block_confidence * 0.4  # Individual block confidence
            + label_diversity * 0.3  # Consistent labeling
            + coverage * 0.2  # Good coverage
            + (1.0 - complexity_penalty) * 0.1  # Simplicity bonus
        )

        overall_confidence = max(0.0, min(overall_confidence, 1.0))

        metadata = DocumentMetadata(
            num_pages=num_pages,
            has_tables=has_tables,
            has_images=has_images,
            has_lists=has_lists,
            languages=["en"],  # TODO: Detect language
            confidence=overall_confidence,
            processing_time=0.0,  # Will be set by agent
        )

        self.logger.info(f"Confidence estimate: {overall_confidence:.2%}")
        return metadata

    def _calculate_label_diversity(self, classified_blocks: List[ClassifiedBlock]) -> float:
        """
        Calculate how consistent/diverse the labels are.
        
        High consistency (most blocks same label) → high score.
        High diversity (all different) → lower score.
        """
        if not classified_blocks:
            return 0.0

        label_counts = {}
        for block in classified_blocks:
            label = block.semantic_label.value
            label_counts[label] = label_counts.get(label, 0) + 1

        # Calculate entropy-based diversity
        total = len(classified_blocks)
        diversity = 0.0

        for count in label_counts.values():
            if count > 0:
                prob = count / total
                diversity -= prob * (prob ** 0.5)  # Weighted by prob

        # Normalize: expect mostly EXPLANATION (0.7) + some others (0.3)
        expected_diversity = -0.7 * (0.7 ** 0.5) - 0.15 * (0.15 ** 0.5) - 0.15 * (0.15 ** 0.5)
        consistency = 1.0 - (diversity / expected_diversity if expected_diversity < 0 else 0.5)

        return max(0.0, min(consistency, 1.0))

    def _calculate_coverage(self, num_blocks: int, num_pages: int) -> float:
        """
        Calculate coverage (blocks extracted per page).
        
        Expected: ~5-10 blocks per page.
        """
        if num_pages == 0:
            return 0.0

        blocks_per_page = num_blocks / num_pages
        expected_range = (5, 10)

        if blocks_per_page < expected_range[0]:
            # Too few blocks extracted
            coverage = blocks_per_page / expected_range[0]
        elif blocks_per_page > expected_range[1]:
            # Too many blocks (maybe fragmented)
            coverage = expected_range[1] / blocks_per_page
        else:
            # Good range
            coverage = 1.0

        return max(0.0, min(coverage, 1.0))

    def _calculate_complexity_penalty(
        self, has_tables: bool, has_images: bool, has_lists: bool
    ) -> float:
        """
        Calculate penalty for complex documents.
        
        Tables and images reduce confidence slightly.
        """
        penalty = 0.0

        if has_tables:
            penalty += 0.1  # Tables harder to parse

        if has_images:
            penalty += 0.05  # Images reduce semantic understanding

        if has_lists:
            penalty += 0.05  # Lists should be easy but nested lists harder

        return penalty
