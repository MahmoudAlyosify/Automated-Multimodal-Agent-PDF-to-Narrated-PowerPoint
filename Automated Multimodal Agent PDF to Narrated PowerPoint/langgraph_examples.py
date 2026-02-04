#!/usr/bin/env python3
"""
Example usage and testing script for LangGraph orchestrator.

This script demonstrates:
1. Basic orchestration
2. Error handling
3. Streaming execution
4. State inspection
5. Integration patterns

Run with:
    python langgraph_examples.py
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from langgraph_orchestrator import (
    run_orchestration,
    create_orchestration_graph,
    OrchestrationState
)


# ============================================================
# EXAMPLE 1: Basic Usage
# ============================================================

def example_basic_usage():
    """Example 1: Basic PDF to PowerPoint conversion."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    # Assuming you have a test PDF available
    pdf_path = "test_document.pdf"
    output_path = "example_output.pptx"
    
    # Check if test PDF exists (for demonstration)
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        print("   Create a test PDF or provide your own PDF file")
        return
    
    print(f"\nInput:  {pdf_path}")
    print(f"Output: {output_path}")
    
    # Simple execution
    result = run_orchestration(
        pdf_path=pdf_path,
        output_pptx=output_path
    )
    
    # Check results
    print(f"\nStatus:  {result['status']}")
    print(f"Success: {result['ppt_created']}")
    
    if result['final_output']:
        print(f"✓ Output file: {result['final_output']}")
    
    if result['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in result['errors']:
            print(f"  - {error}")
    
    return result


# ============================================================
# EXAMPLE 2: Advanced Options
# ============================================================

def example_advanced_options():
    """Example 2: Using advanced options."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Advanced Options")
    print("=" * 70)
    
    pdf_path = "test_document.pdf"
    output_path = "example_advanced.pptx"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        return
    
    print("\nRunning with advanced options:")
    print("  - Domain: academic")
    print("  - Language: en")
    print("  - Page range: 1-5")
    print("  - Debug: enabled")
    
    result = run_orchestration(
        pdf_path=pdf_path,
        output_pptx=output_path,
        domain="academic",
        language="en",
        start_page=1,
        end_page=5,
        debug=True
    )
    
    print(f"\nFinal status: {result['status']}")
    
    return result


# ============================================================
# EXAMPLE 3: Stream Execution
# ============================================================

def example_stream_execution():
    """Example 3: Stream results for real-time updates."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Stream Execution (Real-time Updates)")
    print("=" * 70)
    
    pdf_path = "test_document.pdf"
    output_path = "example_stream.pptx"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        return
    
    print("\nStreaming execution progress:")
    print("-" * 70)
    
    graph = create_orchestration_graph()
    
    initial_state: OrchestrationState = {
        "pdf_path": str(pdf_path),
        "output_pptx": str(output_path),
        "start_page": None,
        "end_page": None,
        "domain": "general",
        "language": "en",
        "venv_path": None,
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
    
    # Stream execution and print each step
    for step, state in graph.stream(initial_state):
        timestamp = time.strftime("%H:%M:%S")
        status = state.get("status", "unknown")
        print(f"[{timestamp}] Step: {step:20s} → Status: {status}")
    
    print("-" * 70)
    print(f"\nFinal status: {state['status']}")
    
    return state


# ============================================================
# EXAMPLE 4: Error Handling
# ============================================================

def example_error_handling():
    """Example 4: Handling errors gracefully."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Error Handling")
    print("=" * 70)
    
    # Try with a non-existent file
    pdf_path = "nonexistent.pdf"
    output_path = "example_error.pptx"
    
    print(f"\nAttempting conversion with non-existent file:")
    print(f"  Input: {pdf_path}")
    
    result = run_orchestration(
        pdf_path=pdf_path,
        output_pptx=output_path
    )
    
    print(f"\nResult status: {result['status']}")
    
    # Check for errors
    if result['errors']:
        print(f"\n✓ Errors were properly caught and reported:")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")
    
    # Check state
    print(f"\nWorkflow state:")
    print(f"  - document_extracted: {result['document_extracted']}")
    print(f"  - slides_designed: {result['slides_designed']}")
    print(f"  - ppt_created: {result['ppt_created']}")
    print(f"  - final_output: {result['final_output']}")
    
    print(f"\n✓ Error handling worked correctly!")
    print(f"  (Graceful degradation - subsequent steps skipped)")
    
    return result


# ============================================================
# EXAMPLE 5: State Inspection
# ============================================================

def example_state_inspection():
    """Example 5: Inspect intermediate state."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: State Inspection")
    print("=" * 70)
    
    pdf_path = "test_document.pdf"
    output_path = "example_inspection.pptx"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        return
    
    print(f"\nRunning orchestration and inspecting state...")
    
    result = run_orchestration(
        pdf_path=pdf_path,
        output_pptx=output_path,
        debug=False
    )
    
    # Inspect extracted content
    print("\n1. EXTRACTED DOCUMENT CONTENT:")
    if result['extracted_content']:
        content = result['extracted_content']
        print(f"   - Keys: {list(content.keys())}")
        if 'document_tree' in content:
            tree = content['document_tree']
            sections = tree.get('sections', [])
            print(f"   - Sections extracted: {len(sections)}")
            if sections:
                print(f"   - First section: {sections[0].get('title', 'N/A')}")
        if 'metadata' in content:
            meta = content['metadata']
            print(f"   - Pages: {meta.get('num_pages', 'N/A')}")
            print(f"   - Has images: {meta.get('has_images', 'N/A')}")
    
    # Inspect slides JSON
    print("\n2. DESIGNED SLIDES:")
    if result['slides_json']:
        slides = result['slides_json'].get('ppt', {}).get('slides', [])
        print(f"   - Total slides: {len(slides)}")
        if slides:
            first = slides[0]
            print(f"   - First slide title: {first.get('title', 'N/A')}")
            print(f"   - First slide elements: {len(first.get('elements', []))}")
    
    # Workflow summary
    print("\n3. WORKFLOW SUMMARY:")
    print(f"   - Document extraction: {'✓ PASS' if result['document_extracted'] else '✗ FAIL'}")
    print(f"   - Slide design: {'✓ PASS' if result['slides_designed'] else '✗ FAIL'}")
    print(f"   - PPT rendering: {'✓ PASS' if result['ppt_created'] else '✗ FAIL'}")
    print(f"   - Final output: {result['final_output'] or 'N/A'}")
    
    return result


# ============================================================
# EXAMPLE 6: Performance Monitoring
# ============================================================

def example_performance_monitoring():
    """Example 6: Monitor execution performance."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Performance Monitoring")
    print("=" * 70)
    
    pdf_path = "test_document.pdf"
    output_path = "example_perf.pptx"
    
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        return
    
    print(f"\nMonitoring execution performance...")
    
    # Time the execution
    start_time = time.time()
    start_memory = None  # Could use psutil for actual memory tracking
    
    result = run_orchestration(
        pdf_path=pdf_path,
        output_pptx=output_path
    )
    
    elapsed_time = time.time() - start_time
    
    # Report performance
    print(f"\nExecution Metrics:")
    print(f"  - Total time: {elapsed_time:.2f} seconds")
    print(f"  - Status: {result['status']}")
    
    if result['status'] == 'completed':
        output_size = Path(result['final_output']).stat().st_size
        output_mb = output_size / (1024 * 1024)
        print(f"  - Output file size: {output_mb:.2f} MB")
        print(f"  - Throughput: {output_mb / elapsed_time:.2f} MB/sec")
    
    return result


# ============================================================
# EXAMPLE 7: Integration Pattern
# ============================================================

def example_integration_pattern():
    """Example 7: Integration with your application."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Integration Pattern")
    print("=" * 70)
    
    print("""
This example shows how to integrate the orchestrator into your app:

# In your Streamlit app:
from langgraph_orchestrator import run_orchestration
import streamlit as st

uploaded = st.file_uploader("Upload PDF", type="pdf")
if uploaded:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded.getvalue())
    
    with st.spinner("Converting..."):
        result = run_orchestration(
            pdf_path="temp.pdf",
            output_pptx="output.pptx"
        )
    
    if result['status'] == 'completed':
        st.success("✓ Conversion complete!")
        with open(result['final_output'], 'rb') as f:
            st.download_button("Download", f, "output.pptx")
    else:
        st.error(f"Error: {result['errors'][0]}")

# In your FastAPI:
from fastapi import FastAPI, File, UploadFile
from langgraph_orchestrator import run_orchestration

app = FastAPI()

@app.post("/convert")
async def convert(pdf: UploadFile = File(...)):
    with open("temp.pdf", "wb") as f:
        f.write(await pdf.read())
    
    result = run_orchestration("temp.pdf", "output.pptx")
    return {"status": result["status"], "output": result["final_output"]}

# From command line:
python langgraph_orchestrator.py input.pdf output.pptx --domain academic
    """)
    
    print("\n✓ See LANGGRAPH_GUIDE.md for more integration examples")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("LANGGRAPH ORCHESTRATOR - EXAMPLES & TESTING")
    print("=" * 70)
    
    print("""
Available examples:
  1. Basic usage
  2. Advanced options
  3. Stream execution
  4. Error handling
  5. State inspection
  6. Performance monitoring
  7. Integration patterns
  
To run specific examples, call them from Python:
  from langgraph_examples import example_basic_usage
  result = example_basic_usage()
  
Or uncomment examples below:
    """)
    
    # Uncomment examples to run them:
    
    # example_basic_usage()
    example_error_handling()  # This one works without a test PDF
    # example_stream_execution()
    # example_state_inspection()
    # example_performance_monitoring()
    example_integration_pattern()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
