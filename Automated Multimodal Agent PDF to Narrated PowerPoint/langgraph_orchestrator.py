#!/usr/bin/env python3
"""
LangGraph-based Orchestrator for PDF-to-Narrated-PowerPoint System

This uses LangGraph to create a state graph orchestrating three agents:
1. Document Understanding Agent - Extracts content from PDF
2. Brain Agent (Mistral AI 7B) - Designs presentation
3. JSON to PPT Agent - Renders PowerPoint

Features:
- State-based workflow management
- Built-in error handling and retries
- Visual graph debugging
- Type-safe state management
- Easy conditional routing

Usage:
    from langgraph_orchestrator import create_orchestration_graph
    
    graph = create_orchestration_graph()
    result = graph.invoke({
        "pdf_path": "document.pdf",
        "output_pptx": "output.pptx"
    })
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict
from enum import Enum

from langgraph.graph import StateGraph, END

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# STATE DEFINITIONS
# ============================================================

class OrchestrationState(TypedDict):
    """State shared across all agents in the workflow."""
    
    # Input parameters
    pdf_path: str
    output_pptx: str
    start_page: Optional[int]
    end_page: Optional[int]
    domain: str
    language: str
    venv_path: Optional[str]
    
    # Step 1: Document Understanding
    document_extracted: bool
    extracted_content: Optional[Dict[str, Any]]
    document_error: Optional[str]
    
    # Step 2: Brain Agent
    slides_designed: bool
    slides_json: Optional[Dict[str, Any]]
    brain_error: Optional[str]
    
    # Step 3: PPT Rendering
    ppt_created: bool
    ppt_error: Optional[str]
    final_output: Optional[str]
    
    # Workflow metadata
    status: str
    errors: list[str]
    
    
class StepStatus(str, Enum):
    """Enumeration for workflow steps."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ============================================================
# AGENT NODE FUNCTIONS
# ============================================================

def document_understanding_node(state: OrchestrationState) -> OrchestrationState:
    """
    Node 1: Document Understanding Agent
    
    Extracts content from PDF using layout analysis and semantic labeling.
    """
    logger.info("=" * 70)
    logger.info("STEP 1: DOCUMENT UNDERSTANDING AGENT")
    logger.info("=" * 70)
    
    try:
        pdf_path = state["pdf_path"]
        
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path}")
        logger.info(f"Domain: {state['domain']}, Language: {state['language']}")
        
        if state["start_page"] or state["end_page"]:
            logger.info(f"Page range: {state['start_page'] or 1} to {state['end_page'] or 'end'}")
        
        # Import and run Document Understanding Agent
        dua_dir = Path(__file__).parent / "document_understanding_agent" / "src" / "dua"
        sys.path.insert(0, str(dua_dir.parent.parent))
        
        from dua.agent import DocumentUnderstandingAgent
        from dua.config import DUAConfig
        
        config = DUAConfig(
            pdf_path=pdf_path,
            start_page=state["start_page"],
            end_page=state["end_page"],
            language=state["language"],
            domain=state["domain"],
            enable_layout_analysis=True,
            enable_semantic_labeling=True,
        )
        
        agent = DocumentUnderstandingAgent(config)
        extracted_content = agent.process()
        
        logger.info("✓ Document extraction completed successfully")
        logger.info(f"  - Sections extracted: {len(extracted_content.get('document_tree', {}).get('sections', []))}")
        
        return {
            **state,
            "document_extracted": True,
            "extracted_content": extracted_content,
            "document_error": None,
            "status": "document_extracted"
        }
        
    except Exception as e:
        error_msg = f"Document understanding failed: {str(e)}"
        logger.error(f"✗ {error_msg}")
        logger.exception(e)
        
        return {
            **state,
            "document_extracted": False,
            "extracted_content": None,
            "document_error": error_msg,
            "status": "document_extraction_failed",
            "errors": state.get("errors", []) + [error_msg]
        }


def brain_agent_node(state: OrchestrationState) -> OrchestrationState:
    """
    Node 2: Brain Agent (Mistral AI 7B)
    
    Designs presentation structure and slide layouts based on extracted content.
    """
    logger.info("=" * 70)
    logger.info("STEP 2: BRAIN AGENT (Mistral AI 7B)")
    logger.info("=" * 70)
    
    # Check if previous step succeeded
    if not state.get("document_extracted"):
        error_msg = "Document extraction failed, skipping brain agent"
        logger.warning(f"⊘ {error_msg}")
        return {
            **state,
            "slides_designed": False,
            "slides_json": None,
            "brain_error": error_msg,
            "status": "skipped"
        }
    
    try:
        extracted_content = state["extracted_content"]
        
        logger.info("Designing presentation with Mistral AI...")
        
        # Import Brain Agent
        brain_dir = Path(__file__).parent / "brain"
        sys.path.insert(0, str(brain_dir))
        
        from main import generate_slides_json
        
        slides_json = generate_slides_json(extracted_content)
        
        logger.info("✓ Presentation design completed successfully")
        logger.info(f"  - Slides generated: {len(slides_json.get('ppt', {}).get('slides', []))}")
        
        return {
            **state,
            "slides_designed": True,
            "slides_json": slides_json,
            "brain_error": None,
            "status": "slides_designed"
        }
        
    except Exception as e:
        error_msg = f"Brain agent failed: {str(e)}"
        logger.error(f"✗ {error_msg}")
        logger.exception(e)
        
        return {
            **state,
            "slides_designed": False,
            "slides_json": None,
            "brain_error": error_msg,
            "status": "brain_design_failed",
            "errors": state.get("errors", []) + [error_msg]
        }


def ppt_rendering_node(state: OrchestrationState) -> OrchestrationState:
    """
    Node 3: JSON to PPT Agent
    
    Renders the designed presentation to PowerPoint (.pptx) format.
    """
    logger.info("=" * 70)
    logger.info("STEP 3: JSON TO PPT AGENT")
    logger.info("=" * 70)
    
    # Check if previous step succeeded
    if not state.get("slides_designed"):
        error_msg = "Slide design failed, skipping PPT rendering"
        logger.warning(f"⊘ {error_msg}")
        return {
            **state,
            "ppt_created": False,
            "ppt_error": error_msg,
            "final_output": None,
            "status": "skipped"
        }
    
    try:
        slides_json = state["slides_json"]
        output_pptx = state["output_pptx"]
        
        logger.info(f"Rendering PowerPoint: {output_pptx}")
        
        # Import JSON to PPT Agent
        ppt_dir = Path(__file__).parent / "JSON To PPT"
        sys.path.insert(0, str(ppt_dir))
        
        from main import json_to_pptx
        
        pptx_path = json_to_pptx(slides_json, output_pptx)
        
        logger.info("✓ PowerPoint rendering completed successfully")
        logger.info(f"  - Output file: {pptx_path}")
        
        return {
            **state,
            "ppt_created": True,
            "ppt_error": None,
            "final_output": str(pptx_path),
            "status": "completed"
        }
        
    except Exception as e:
        error_msg = f"PPT rendering failed: {str(e)}"
        logger.error(f"✗ {error_msg}")
        logger.exception(e)
        
        return {
            **state,
            "ppt_created": False,
            "ppt_error": error_msg,
            "final_output": None,
            "status": "ppt_rendering_failed",
            "errors": state.get("errors", []) + [error_msg]
        }


# ============================================================
# CONDITIONAL EDGE FUNCTIONS
# ============================================================

def should_run_brain_agent(state: OrchestrationState) -> str:
    """
    Conditional edge: Route to brain agent if document extraction succeeded.
    """
    if state.get("document_extracted"):
        return "brain_agent"
    else:
        return "end"


def should_run_ppt_agent(state: OrchestrationState) -> str:
    """
    Conditional edge: Route to PPT agent if brain agent succeeded.
    """
    if state.get("slides_designed"):
        return "ppt_agent"
    else:
        return "end"


# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

def create_orchestration_graph():
    """
    Creates and returns the LangGraph state graph for orchestration.
    
    Returns:
        Compiled graph with nodes and edges configured.
    """
    
    # Initialize the state graph
    workflow = StateGraph(OrchestrationState)
    
    # Add nodes
    workflow.add_node("document_agent", document_understanding_node)
    workflow.add_node("brain_agent", brain_agent_node)
    workflow.add_node("ppt_agent", ppt_rendering_node)
    
    # Define edges
    workflow.set_entry_point("document_agent")
    
    # Conditional edge from document agent to brain agent
    workflow.add_conditional_edges(
        "document_agent",
        should_run_brain_agent,
        {
            "brain_agent": "brain_agent",
            "end": END
        }
    )
    
    # Conditional edge from brain agent to PPT agent
    workflow.add_conditional_edges(
        "brain_agent",
        should_run_ppt_agent,
        {
            "ppt_agent": "ppt_agent",
            "end": END
        }
    )
    
    # Edge from PPT agent to end
    workflow.add_edge("ppt_agent", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    return graph


# ============================================================
# EXECUTION FUNCTION
# ============================================================

def run_orchestration(
    pdf_path: str,
    output_pptx: str,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    domain: str = "general",
    language: str = "en",
    venv_path: Optional[str] = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Execute the orchestration graph for PDF to narrated PowerPoint conversion.
    
    Args:
        pdf_path: Path to input PDF file
        output_pptx: Path to output PowerPoint file
        start_page: Optional start page (1-indexed)
        end_page: Optional end page (1-indexed)
        domain: Document domain (academic, business, technical, general)
        language: Language code (en, es, fr, etc.)
        venv_path: Optional path to virtual environment
        debug: If True, print graph structure
        
    Returns:
        Final state dictionary with results and status
    """
    
    logger.info("🚀 Starting PDF-to-Narrated-PowerPoint Orchestration")
    logger.info(f"Input: {pdf_path} → Output: {output_pptx}")
    
    # Create the graph
    graph = create_orchestration_graph()
    
    if debug:
        logger.info("\n📊 GRAPH STRUCTURE:\n")
        try:
            # Try to print graph structure if mermaid is available
            print(graph.get_graph().draw_ascii())
        except:
            logger.info("Graph visualization not available")
    
    # Initialize state
    initial_state: OrchestrationState = {
        "pdf_path": str(pdf_path),
        "output_pptx": str(output_pptx),
        "start_page": start_page,
        "end_page": end_page,
        "domain": domain,
        "language": language,
        "venv_path": venv_path,
        "document_extracted": False,
        "extracted_content": None,
        "document_error": None,
        "slides_designed": False,
        "slides_json": None,
        "brain_error": None,
        "ppt_created": False,
        "ppt_error": None,
        "final_output": None,
        "status": "initialized",
        "errors": []
    }
    
    # Run the graph
    try:
        final_state = graph.invoke(initial_state)
        
        logger.info("\n" + "=" * 70)
        logger.info("ORCHESTRATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Final Status: {final_state.get('status', 'UNKNOWN')}")
        logger.info(f"Document Extraction: {'✓ SUCCESS' if final_state.get('document_extracted') else '✗ FAILED'}")
        logger.info(f"Slide Design: {'✓ SUCCESS' if final_state.get('slides_designed') else '✗ FAILED'}")
        logger.info(f"PPT Rendering: {'✓ SUCCESS' if final_state.get('ppt_created') else '✗ FAILED'}")
        
        if final_state.get("final_output"):
            logger.info(f"\n✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            logger.info(f"📄 Output file: {final_state['final_output']}")
        
        if final_state.get("errors"):
            logger.warning(f"\n⚠️  Errors encountered:")
            for error in final_state["errors"]:
                logger.warning(f"  - {error}")
        
        return final_state
        
    except Exception as e:
        logger.error(f"\n❌ ORCHESTRATION FAILED: {str(e)}")
        logger.exception(e)
        
        return {
            **initial_state,
            "status": "orchestration_failed",
            "errors": [str(e)]
        }


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="LangGraph-based PDF-to-Narrated-PowerPoint Orchestrator"
    )
    parser.add_argument("pdf_path", help="Path to input PDF file")
    parser.add_argument("output_pptx", help="Path to output PowerPoint file")
    parser.add_argument("--start-page", type=int, help="Start page (1-indexed)")
    parser.add_argument("--end-page", type=int, help="End page (1-indexed)")
    parser.add_argument("--domain", default="general", 
                       choices=["academic", "business", "technical", "general"],
                       help="Document domain")
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--venv", help="Path to virtual environment")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    result = run_orchestration(
        pdf_path=args.pdf_path,
        output_pptx=args.output_pptx,
        start_page=args.start_page,
        end_page=args.end_page,
        domain=args.domain,
        language=args.language,
        venv_path=args.venv,
        debug=args.debug
    )
    
    # Exit with appropriate code
    sys.exit(0 if result.get("status") == "completed" else 1)
