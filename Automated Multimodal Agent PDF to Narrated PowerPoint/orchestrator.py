#!/usr/bin/env python3
"""
Orchestrator for the PDF-to-Narrated-PowerPoint Agent System

This script coordinates the three AI agents:
1. Document Understanding Agent - Extracts content from PDF
2. Brain Agent (Mistral AI 7B) - Designs presentation
3. JSON to PPT Agent - Renders PowerPoint

Usage:
    python orchestrator.py <input_pdf> <output_pptx> [--start-page N] [--end-page N]
    
Example:
    python orchestrator.py document.pdf output.pptx --start-page 1 --end-page 10
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFToPresentation:
    """Orchestrates the three-agent pipeline for PDF to PowerPoint conversion."""
    
    def __init__(self, venv_path: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            venv_path: Path to virtual environment. If None, uses system Python.
        """
        self.venv_path = venv_path or ""
        self.root_dir = Path(__file__).parent.absolute()
        self.dua_dir = self.root_dir / "document_understanding_agent"
        self.brain_dir = self.root_dir / "brain"
        self.ppt_dir = self.root_dir / "JSON To PPT"
        
        logger.info(f"Root directory: {self.root_dir}")
        
    def get_python_cmd(self) -> str:
        """Get the Python command to use."""
        if self.venv_path:
            venv_python = str(Path(self.venv_path) / "Scripts" / "python.exe")
            if Path(venv_python).exists():
                return venv_python
        return sys.executable
    
    def step_1_extract_document(
        self,
        pdf_path: str,
        output_json: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        domain: str = "general",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Step 1: Extract document structure using Document Understanding Agent.
        
        Args:
            pdf_path: Path to input PDF
            output_json: Path to output JSON file
            start_page: Start page (1-indexed)
            end_page: End page (1-indexed)
            domain: Domain type (academic, business, technical, general)
            language: Language code (en, es, fr, etc.)
            
        Returns:
            Extracted document content as dictionary
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Document Understanding Agent")
        logger.info("=" * 60)
        
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Input PDF: {pdf_path}")
        logger.info(f"Domain: {domain}, Language: {language}")
        
        if start_page or end_page:
            logger.info(f"Page range: {start_page or 1} to {end_page or 'end'}")
        
        # Create example usage script dynamically
        example_script = f"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dua import DocumentUnderstandingAgent
from dua.types import DUAInput

# Initialize agent
agent = DocumentUnderstandingAgent(
    use_ml=False,
    extract_images=True,
    log_level="INFO",
)

# Process PDF
dua_input = DUAInput(
    pdf_path=r"{pdf_path}",
    start_page={start_page or 1},
    end_page={end_page or "None"},
    domain="{domain}",
    language="{language}"
)

output = agent.process(dua_input)

# Save output
with open(r"{output_json}", "w", encoding="utf-8") as f:
    json.dump(output.to_dict(), f, indent=2)

print(f"✓ Extracted content saved to {{r'{output_json}'}}")
print(f"  Confidence: {{output.metadata['confidence']:.2%}}")
print(f"  Pages: {{output.metadata['num_pages']}}")
"""
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=self.dua_dir,
            delete=False
        ) as f:
            f.write(example_script)
            temp_script = f.name
        
        try:
            python_cmd = self.get_python_cmd()
            logger.info(f"Running: {python_cmd} {temp_script}")
            
            result = subprocess.run(
                [python_cmd, temp_script],
                cwd=str(self.dua_dir),
                capture_output=True,
                text=True
            )
            
            logger.info(result.stdout)
            if result.stderr:
                logger.warning(result.stderr)
            
            if result.returncode != 0:
                raise RuntimeError(f"Document Understanding Agent failed: {result.stderr}")
            
            # Load and return extracted content
            with open(output_json, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            logger.info(f"✓ Step 1 completed successfully")
            return content
            
        finally:
            Path(temp_script).unlink()
    
    def step_2_generate_slides(
        self,
        extracted_json: str,
        output_json: str
    ) -> Dict[str, Any]:
        """
        Step 2: Generate slide specifications using Brain Agent (Mistral AI).
        
        Args:
            extracted_json: Path to extracted content JSON
            output_json: Path to output slides JSON
            
        Returns:
            Slide specifications as dictionary
        """
        logger.info("=" * 60)
        logger.info("STEP 2: Brain Agent (Mistral AI 7B)")
        logger.info("=" * 60)
        
        if not Path(extracted_json).exists():
            raise FileNotFoundError(f"Extracted content not found: {extracted_json}")
        
        logger.info(f"Input: {extracted_json}")
        logger.info(f"Output: {output_json}")
        
        # Check for API key
        if not os.getenv("MISTRAL_API_KEY"):
            logger.warning("⚠ MISTRAL_API_KEY not set in environment")
            logger.info("  Please set it in .env file or environment variable")
            raise RuntimeError("MISTRAL_API_KEY not configured")
        
        python_cmd = self.get_python_cmd()
        logger.info(f"Running: {python_cmd} main.py {extracted_json} {output_json}")
        
        result = subprocess.run(
            [python_cmd, "main.py", extracted_json, output_json],
            cwd=str(self.brain_dir),
            capture_output=True,
            text=True
        )
        
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
        
        if result.returncode != 0:
            raise RuntimeError(f"Brain Agent failed: {result.stderr}")
        
        # Load and return slides
        with open(output_json, 'r', encoding='utf-8') as f:
            slides = json.load(f)
        
        num_slides = len(slides.get('ppt', {}).get('slides', []))
        logger.info(f"✓ Step 2 completed: Generated {num_slides} slides")
        return slides
    
    def step_3_render_powerpoint(
        self,
        slides_json: str,
        output_pptx: str
    ) -> None:
        """
        Step 3: Render PowerPoint from slide specifications.
        
        Args:
            slides_json: Path to slides JSON
            output_pptx: Path to output PowerPoint file
        """
        logger.info("=" * 60)
        logger.info("STEP 3: JSON to PPT Agent")
        logger.info("=" * 60)
        
        if not Path(slides_json).exists():
            raise FileNotFoundError(f"Slides JSON not found: {slides_json}")
        
        logger.info(f"Input: {slides_json}")
        logger.info(f"Output: {output_pptx}")
        
        python_cmd = self.get_python_cmd()
        logger.info(f"Running: {python_cmd} main.py {slides_json} {output_pptx}")
        
        result = subprocess.run(
            [python_cmd, "main.py", slides_json, output_pptx],
            cwd=str(self.ppt_dir),
            capture_output=True,
            text=True
        )
        
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
        
        if result.returncode != 0:
            raise RuntimeError(f"JSON to PPT Agent failed: {result.stderr}")
        
        logger.info(f"✓ Step 3 completed: PowerPoint saved to {output_pptx}")
    
    def process(
        self,
        pdf_path: str,
        output_pptx: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        domain: str = "general",
        language: str = "en",
        keep_temp: bool = False
    ) -> None:
        """
        Run the complete pipeline.
        
        Args:
            pdf_path: Path to input PDF
            output_pptx: Path to output PowerPoint
            start_page: Optional start page
            end_page: Optional end page
            domain: Content domain
            language: Content language
            keep_temp: Keep temporary JSON files
        """
        try:
            # Create temp directory for intermediate files
            temp_dir = Path(output_pptx).parent / ".temp_pipeline"
            temp_dir.mkdir(exist_ok=True)
            
            extracted_json = temp_dir / "extracted_content.json"
            slides_json = temp_dir / "slides.json"
            
            logger.info("\n" + "=" * 60)
            logger.info("PDF-to-PowerPoint Pipeline Started")
            logger.info("=" * 60 + "\n")
            
            # Step 1: Extract
            self.step_1_extract_document(
                pdf_path=pdf_path,
                output_json=str(extracted_json),
                start_page=start_page,
                end_page=end_page,
                domain=domain,
                language=language
            )
            
            # Step 2: Generate slides
            self.step_2_generate_slides(
                extracted_json=str(extracted_json),
                output_json=str(slides_json)
            )
            
            # Step 3: Render PowerPoint
            self.step_3_render_powerpoint(
                slides_json=str(slides_json),
                output_pptx=output_pptx
            )
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ Pipeline Completed Successfully!")
            logger.info("=" * 60)
            logger.info(f"Output file: {output_pptx}")
            logger.info(f"File size: {Path(output_pptx).stat().st_size / (1024*1024):.2f} MB")
            
            # Cleanup temp files if not keeping them
            if not keep_temp and temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                logger.info("Temporary files cleaned up")
            else:
                logger.info(f"Temporary files saved in: {temp_dir}")
                
        except Exception as e:
            logger.error(f"\n✗ Pipeline failed: {str(e)}")
            raise


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="PDF to Narrated PowerPoint Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py document.pdf output.pptx
  python orchestrator.py document.pdf output.pptx --start-page 1 --end-page 10
  python orchestrator.py document.pdf output.pptx --domain academic --language en
        """
    )
    
    parser.add_argument(
        "input_pdf",
        type=str,
        help="Path to input PDF file"
    )
    
    parser.add_argument(
        "output_pptx",
        type=str,
        help="Path to output PowerPoint file"
    )
    
    parser.add_argument(
        "--start-page",
        type=int,
        default=None,
        help="Start page (1-indexed)"
    )
    
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="End page (1-indexed)"
    )
    
    parser.add_argument(
        "--domain",
        type=str,
        default="general",
        choices=["academic", "business", "technical", "general"],
        help="Content domain"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Content language code"
    )
    
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary JSON files"
    )
    
    parser.add_argument(
        "--venv",
        type=str,
        default=None,
        help="Path to virtual environment"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = PDFToPresentation(venv_path=args.venv)
    
    # Run pipeline
    orchestrator.process(
        pdf_path=args.input_pdf,
        output_pptx=args.output_pptx,
        start_page=args.start_page,
        end_page=args.end_page,
        domain=args.domain,
        language=args.language,
        keep_temp=args.keep_temp
    )


if __name__ == "__main__":
    main()
