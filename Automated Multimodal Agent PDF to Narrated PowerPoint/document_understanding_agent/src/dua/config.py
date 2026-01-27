"""
Configuration module for Document Understanding Agent.

This module provides configuration classes and utilities for DUA.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PDFLoaderConfig:
    """Configuration for PDF Loader module."""
    extract_images: bool = True
    extract_tables: bool = True
    max_pages: int = None  # None = no limit


@dataclass
class LayoutAnalyzerConfig:
    """Configuration for Layout Analyzer module."""
    use_spatial_clustering: bool = True
    font_threshold_ratio: float = 1.5
    position_threshold_ratio: float = 0.15


@dataclass
class BlockClassifierConfig:
    """Configuration for Block Classifier module."""
    use_ml: bool = False
    ml_threshold: float = 0.6  # Confidence threshold for ML fallback
    rule_confidence: float = 0.7  # Default confidence for rule-based


@dataclass
class SemanticLabelerConfig:
    """Configuration for Semantic Labeler module."""
    domain: str = "general"  # academic, business, technical, legal
    language: str = "en"  # en, ar, etc.
    context_window: int = 2  # How many blocks to look ahead/behind


@dataclass
class DUAConfig:
    """Overall DUA configuration."""
    pdf_loader: PDFLoaderConfig = None
    layout_analyzer: LayoutAnalyzerConfig = None
    block_classifier: BlockClassifierConfig = None
    semantic_labeler: SemanticLabelerConfig = None
    
    log_level: str = "INFO"
    enable_profiling: bool = False
    
    def __post_init__(self):
        """Initialize default configs if not provided."""
        if self.pdf_loader is None:
            self.pdf_loader = PDFLoaderConfig()
        if self.layout_analyzer is None:
            self.layout_analyzer = LayoutAnalyzerConfig()
        if self.block_classifier is None:
            self.block_classifier = BlockClassifierConfig()
        if self.semantic_labeler is None:
            self.semantic_labeler = SemanticLabelerConfig()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DUAConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "pdf_loader": self.pdf_loader.__dict__,
            "layout_analyzer": self.layout_analyzer.__dict__,
            "block_classifier": self.block_classifier.__dict__,
            "semantic_labeler": self.semantic_labeler.__dict__,
            "log_level": self.log_level,
            "enable_profiling": self.enable_profiling,
        }


# Preset configurations
class Presets:
    """Preset configurations for common use cases."""
    
    @staticmethod
    def academic() -> DUAConfig:
        """Configuration for academic documents."""
        config = DUAConfig()
        config.semantic_labeler.domain = "academic"
        config.pdf_loader.extract_images = True
        return config
    
    @staticmethod
    def business() -> DUAConfig:
        """Configuration for business documents."""
        config = DUAConfig()
        config.semantic_labeler.domain = "business"
        config.pdf_loader.extract_tables = True
        return config
    
    @staticmethod
    def technical() -> DUAConfig:
        """Configuration for technical documents."""
        config = DUAConfig()
        config.semantic_labeler.domain = "technical"
        config.pdf_loader.extract_images = True
        return config
    
    @staticmethod
    def legal() -> DUAConfig:
        """Configuration for legal documents."""
        config = DUAConfig()
        config.semantic_labeler.domain = "legal"
        config.block_classifier.use_ml = False  # Be conservative
        return config
    
    @staticmethod
    def fast() -> DUAConfig:
        """Fast processing configuration."""
        config = DUAConfig()
        config.pdf_loader.extract_images = False
        config.block_classifier.use_ml = False
        config.log_level = "WARNING"
        return config
    
    @staticmethod
    def accurate() -> DUAConfig:
        """Accurate processing configuration."""
        config = DUAConfig()
        config.pdf_loader.extract_images = True
        config.block_classifier.use_ml = True
        config.log_level = "DEBUG"
        return config


# Export
__all__ = [
    "DUAConfig",
    "PDFLoaderConfig",
    "LayoutAnalyzerConfig",
    "BlockClassifierConfig",
    "SemanticLabelerConfig",
    "Presets",
]
