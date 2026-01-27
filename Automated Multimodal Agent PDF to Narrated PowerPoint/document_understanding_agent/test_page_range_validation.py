"""
Automated test for page range selection with validation (max 10 pages).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dua import DocumentUnderstandingAgent
from dua.types import DUAInput
import json


def test_page_range(start_page, end_page, description):
    """Test a specific page range."""
    print(f"\n{'=' * 70}")
    print(f"TEST: {description}")
    print(f"{'=' * 70}")
    print(f"Input: start_page={start_page}, end_page={end_page}")
    
    # Find PDF
    pdf_files = list(Path(".").glob("*Beginner*Patterns*.pdf"))
    if not pdf_files:
        print("✗ PDF not found")
        return False
    
    pdf_path = str(pdf_files[0])
    
    # Validate page range (max 10 pages)
    num_pages = end_page - start_page + 1
    
    if num_pages > 10:
        print(f"\n⚠️  VALIDATION FAILED:")
        print(f"   You selected {num_pages} pages, but maximum is 10 pages!")
        print(f"   Range: [{start_page}, {end_page}] = {num_pages} pages")
        return False
    
    if start_page < 0 or end_page < 0:
        print(f"\n⚠️  VALIDATION FAILED:")
        print(f"   Page numbers must be >= 0")
        return False
    
    if end_page < start_page:
        print(f"\n⚠️  VALIDATION FAILED:")
        print(f"   End page must be >= start page")
        return False
    
    # Validation passed - process
    print(f"\n✓ VALIDATION PASSED")
    print(f"  Processing {num_pages} pages ({start_page}-{end_page})")
    
    agent = DocumentUnderstandingAgent(log_level="WARNING")
    
    try:
        example_input = DUAInput(
            pdf_path=pdf_path,
            language="en",
            domain="academic",
            start_page=start_page,
            end_page=end_page
        )
        
        output = agent.process(example_input)
        
        print(f"\n✓ PROCESSING SUCCESSFUL:")
        print(f"  Pages: {output.metadata.num_pages}")
        print(f"  Sections: {len(output.document_tree.sections)}")
        print(f"  Confidence: {output.metadata.confidence:.1%}")
        print(f"  Processing time: {output.metadata.processing_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"\n✗ PROCESSING FAILED: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PAGE RANGE VALIDATION TESTS (Max 10 pages)")
    print("=" * 70)
    
    tests = [
        (0, 9, "✓ VALID: First 10 pages (0-9)"),
        (0, 4, "✓ VALID: First 5 pages (0-4)"),
        (5, 14, "✓ VALID: Pages 5-14 (10 pages)"),
        (0, 19, "✗ INVALID: 20 pages exceeds limit (0-19)"),
        (10, 25, "✗ INVALID: 16 pages exceeds limit (10-25)"),
        (-1, 5, "✗ INVALID: Negative start page (-1-5)"),
        (5, 4, "✗ INVALID: End < Start (5-4)"),
    ]
    
    results = []
    
    for start, end, description in tests:
        result = test_page_range(start, end, description)
        results.append((description, result))
    
    # Summary
    print(f"\n\n{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for description, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {description}")
    
    print(f"\n{passed}/{total} tests passed")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
