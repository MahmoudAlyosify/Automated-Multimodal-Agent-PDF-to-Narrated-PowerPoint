"""
Example usage of the Document Understanding Agent.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dua import DocumentUnderstandingAgent
from dua.types import DUAInput


def main():
    """Example: Process a PDF document with user-selected page range (max 10 pages)."""
    
    # Initialize agent
    agent = DocumentUnderstandingAgent(
        use_ml=False,
        extract_images=True,
        log_level="INFO",
    )
    
    # Check agent status
    print("Agent Status:")
    print(json.dumps(agent.get_status(), indent=2))
    print()
    
    # Find the PDF file
    pdf_files = list(Path(".").glob("*Beginner*Patterns*.pdf"))
    if not pdf_files:
        print("✗ PDF file not found. Looking for '*Beginner*Patterns*.pdf' in current directory.")
        return
    
    pdf_path = str(pdf_files[0])
    print(f"Found PDF: {pdf_path}")
    
    # Get PDF info
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        doc.close()
    except Exception as e:
        print(f"✗ Error reading PDF info: {e}")
        return
    
    print(f"Total pages in PDF: {total_pages}\n")
    
    # ========================================
    # USER INPUT FOR PAGE RANGE
    # ========================================
    print("=" * 60)
    print("SELECT PAGE RANGE (Maximum 10 pages)")
    print("=" * 60)
    
    while True:
        try:
            start_input = input(f"Enter starting page (0-{total_pages-1}) [default: 0]: ").strip()
            start_page = int(start_input) if start_input else 0
            
            if start_page < 0 or start_page >= total_pages:
                print(f"✗ Invalid start page. Must be between 0 and {total_pages-1}")
                continue
            
            end_input = input(f"Enter ending page (0-{total_pages-1}) [default: 9]: ").strip()
            end_page = int(end_input) if end_input else min(9, total_pages - 1)
            
            if end_page < 0 or end_page >= total_pages:
                print(f"✗ Invalid end page. Must be between 0 and {total_pages-1}")
                continue
            
            if end_page < start_page:
                print(f"✗ End page must be greater than or equal to start page")
                continue
            
            # Check max 10 pages
            num_pages = end_page - start_page + 1
            if num_pages > 10:
                print(f"\n⚠️  WARNING: You selected {num_pages} pages, but maximum is 10 pages!")
                print(f"   Please select a range with at most 10 pages.\n")
                continue
            
            # Valid range
            print(f"\n✓ Processing pages {start_page} to {end_page} ({num_pages} pages)")
            break
            
        except ValueError:
            print("✗ Please enter valid numbers")
            continue
        except KeyboardInterrupt:
            print("\n✗ Cancelled by user")
            return
    
    print()
    
    # Create input with selected page range
    example_input = DUAInput(
        pdf_path=pdf_path,
        language="en",
        domain="academic",
        start_page=start_page,
        end_page=end_page
    )
    
    # Process
    try:
        output = agent.process(example_input)
        
        # Display results
        print(f"✓ Document processed successfully!")
        print(f"  Pages: {output.metadata.num_pages}")
        print(f"  Sections: {len(output.document_tree.sections)}")
        print(f"  Confidence: {output.metadata.confidence:.1%}")
        print(f"  Processing time: {output.metadata.processing_time:.2f}s")
        print()
        
        # Show document structure
        print("Document Structure:")
        for i, section in enumerate(output.document_tree.sections[:5]):  # First 5 sections
            indent = "  " * (section.level - 1)
            print(f"{indent}[Level {section.level}] {section.title}")
            print(f"{indent}  └─ {len(section.blocks)} blocks")
        
        if len(output.document_tree.sections) > 5:
            print(f"  ... and {len(output.document_tree.sections) - 5} more sections")
        print()
        
        # Save to JSON
        output_dict = output.to_dict()
        with open("output.json", "w") as f:
            json.dump(output_dict, f, indent=2)
        print("✓ Output saved to output.json")
        
    except FileNotFoundError:
        print("✗ PDF file not found. Please provide a valid PDF path.")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
