"""
Unit tests for Document Understanding Agent modules.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dua.types import (
    BoundingBox,
    FontInfo,
    RawBlock,
    BlockType,
    LayoutRole,
    SemanticLabel,
)
from dua.modules import BlockClassifier


def test_block_classifier_question():
    """Test question detection."""
    classifier = BlockClassifier()
    
    from dua.modules.layout_analyzer import LayoutAnalyzer
    
    # Create test blocks
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=20)
    font = FontInfo(size=12, weight=400, is_bold=False, is_italic=False)
    
    raw_block = RawBlock(
        text="What is machine learning?",
        bbox=bbox,
        font_info=font,
        page_number=0,
        block_id="test_1",
    )
    
    analyzer = LayoutAnalyzer()
    analyzed = analyzer.analyze([raw_block])[0]
    classified = classifier.classify([analyzed])
    
    assert classified[0].semantic_label == SemanticLabel.QUESTION


def test_block_classifier_definition():
    """Test definition detection."""
    classifier = BlockClassifier()
    
    from dua.modules.layout_analyzer import LayoutAnalyzer
    
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=20)
    font = FontInfo(size=12, weight=400, is_bold=False, is_italic=False)
    
    raw_block = RawBlock(
        text="Machine Learning is defined as the ability of computers to learn from data.",
        bbox=bbox,
        font_info=font,
        page_number=0,
        block_id="test_2",
    )
    
    analyzer = LayoutAnalyzer()
    analyzed = analyzer.analyze([raw_block])[0]
    classified = classifier.classify([analyzed])
    
    assert classified[0].semantic_label == SemanticLabel.DEFINITION


def test_bounding_box():
    """Test bounding box properties."""
    bbox = BoundingBox(x0=10, y0=20, x1=110, y1=70)
    
    assert bbox.width == 100
    assert bbox.height == 50
    assert bbox.area == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
