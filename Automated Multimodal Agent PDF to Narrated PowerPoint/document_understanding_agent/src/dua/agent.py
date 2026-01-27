"""
Document Understanding Agent (DUA)
Main orchestrator for document understanding pipeline.

Pipeline Flow:
1. PDF Loader → Raw blocks
2. Layout Analyzer → Layout roles
3. Block Classifier → Block types + semantic labels
4. Semantic Labeler → Refined labels
5. Structure Builder → Document tree
6. Confidence Estimator → Confidence scores
"""

import logging
import time
from typing import Dict, Any

from .modules import (
    PDFLoader,
    LayoutAnalyzer,
    BlockClassifier,
    SemanticLabeler,
    StructureBuilder,
    ConfidenceEstimator,
)
from .types import (
    DUAInput,
    DUAOutput,
    BlockType,
    DocumentTree,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DocumentUnderstandingAgent:
    """
    Document Understanding Agent (DUA)
    
    Transforms raw PDFs into structured semantic documents through a modular pipeline.
    
    **Agent Contract:**
    
    Input:
    ```json
    {
      "pdf_path": "lecture.pdf",
      "language": "en",
      "domain": "academic"
    }
    ```
    
    Output:
    ```json
    {
      "document_tree": {
        "sections": [
          {
            "title": "...",
            "level": 2,
            "blocks": [
              {
                "type": "PARAGRAPH",
                "semantic_label": "EXPLANATION",
                "importance": 0.91,
                "text": "..."
              }
            ]
          }
        ]
      },
      "metadata": {
        "num_pages": 12,
        "has_tables": true,
        "confidence": 0.94
      }
    }
    ```
    """

    def __init__(
        self,
        use_ml: bool = False,
        extract_images: bool = True,
        log_level: str = "INFO",
    ):
        """
        Initialize Document Understanding Agent.
        
        Args:
            use_ml: Whether to use ML models in block classifier.
            extract_images: Whether to extract image references.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        """
        self.logger = logger
        logging.getLogger().setLevel(getattr(logging, log_level))

        # Initialize modules
        self.pdf_loader = PDFLoader(extract_images=extract_images)
        self.layout_analyzer = LayoutAnalyzer()
        self.block_classifier = BlockClassifier(use_ml=use_ml)
        self.semantic_labeler = SemanticLabeler()
        self.structure_builder = StructureBuilder()
        self.confidence_estimator = ConfidenceEstimator()

        self.logger.info("✓ Document Understanding Agent initialized")

    def process(self, dua_input: DUAInput) -> DUAOutput:
        """
        Process a PDF according to the DUA contract.
        
        Args:
            dua_input: DUAInput with pdf_path, language, domain, and optional page range.
            
        Returns:
            DUAOutput with document_tree and metadata.
            
        Raises:
            FileNotFoundError: If PDF doesn't exist.
            RuntimeError: If processing fails.
        """
        start_time = time.time()
        warnings = []

        try:
            self.logger.info(f"Processing: {dua_input.pdf_path}")
            if dua_input.start_page > 0 or dua_input.end_page is not None:
                self.logger.info(f"  Page range: {dua_input.start_page} to {dua_input.end_page or 'end'}")

            # Step 1: Load PDF
            self.logger.info("→ Step 1: PDF Loading")
            raw_blocks = self.pdf_loader.load(
                dua_input.pdf_path,
                start_page=dua_input.start_page,
                end_page=dua_input.end_page
            )
            pdf_metadata = self.pdf_loader.get_pdf_metadata(dua_input.pdf_path)

            if not raw_blocks:
                warnings.append("No blocks extracted from PDF")

            # Step 2: Analyze Layout
            self.logger.info("→ Step 2: Layout Analysis")
            analyzed_blocks = self.layout_analyzer.analyze(raw_blocks)

            # Step 3: Classify Blocks
            self.logger.info("→ Step 3: Block Classification")
            self.semantic_labeler.domain = dua_input.domain
            self.semantic_labeler.language = dua_input.language
            classified_blocks = self.block_classifier.classify(analyzed_blocks)

            # Step 4: Refine Semantic Labels
            self.logger.info("→ Step 4: Semantic Labeling")
            refined_blocks = self.semantic_labeler.label(classified_blocks)

            # Step 5: Build Document Structure
            self.logger.info("→ Step 5: Structure Building")
            sections = self.structure_builder.build(refined_blocks)

            # Step 6: Estimate Confidence
            self.logger.info("→ Step 6: Confidence Estimation")
            has_tables = any(b.block_type == BlockType.TABLE for b in refined_blocks)
            has_images = any(b.block_type == BlockType.IMAGE for b in refined_blocks)
            has_lists = any(b.block_type == BlockType.LIST for b in refined_blocks)

            metadata = self.confidence_estimator.estimate(
                refined_blocks,
                pdf_metadata["num_pages"],
                has_tables,
                has_images,
                has_lists,
            )

            # Calculate total processing time
            processing_time = time.time() - start_time
            metadata.processing_time = processing_time

            # Build document tree
            document_tree = DocumentTree(
                sections=sections,
                metadata=metadata,
            )

            # Extract full text for reference
            full_text = "\n\n".join(block.text for block in refined_blocks)

            # Create output
            output = DUAOutput(
                document_tree=document_tree,
                metadata=metadata,
                raw_text=full_text,
                warnings=warnings,
            )

            self.logger.info(
                f"✓ Processing complete ({processing_time:.2f}s, "
                f"confidence: {metadata.confidence:.1%})"
            )

            return output

        except FileNotFoundError as e:
            self.logger.error(f"✗ File not found: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"✗ Processing failed: {str(e)}")
            raise RuntimeError(f"Failed to process PDF: {str(e)}")

    def process_dict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process PDF from dictionary input (for API compatibility).
        
        Args:
            input_dict: Dictionary with pdf_path, language, domain.
            
        Returns:
            Dictionary output following DUA contract.
        """
        dua_input = DUAInput(**input_dict)
        dua_output = self.process(dua_input)
        return dua_output.to_dict()

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and configuration."""
        return {
            "agent": "Document Understanding Agent (DUA)",
            "version": "1.0.0",
            "status": "ready",
            "modules": [
                "PDF Loader",
                "Layout Analyzer",
                "Block Classifier",
                "Semantic Labeler",
                "Structure Builder",
                "Confidence Estimator",
            ],
        }
