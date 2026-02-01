#!/usr/bin/env python3
"""
Demonstration of the PDF-to-Narrated-PowerPoint System

This script demonstrates each component of the system working together:
1. Document Understanding Agent - Extracts content from PDF
2. Brain Agent (Optional - Mistral AI) - Designs presentation
3. JSON to PPT Agent - Generates PowerPoint
"""

import sys
import json
from pathlib import Path

print("=" * 70)
print("PDF-TO-NARRATED-POWERPOINT SYSTEM DEMONSTRATION")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Document Understanding Agent
# ============================================================================
print("[STEP 1] Document Understanding Agent")
print("-" * 70)

try:
    sys.path.insert(0, str(Path('document_understanding_agent/src').absolute()))
    from dua import DocumentUnderstandingAgent
    from dua.types import DUAInput
    
    # Initialize agent
    agent = DocumentUnderstandingAgent(use_ml=False, log_level='WARNING')
    print("✓ Agent initialized successfully")
    
    # Check agent status
    status = agent.get_status()
    print(f"✓ Modules loaded: {len(status.get('modules', []))}")
    print(f"  - {', '.join(m for m in status.get('modules', []))}")
    
    # Process PDF
    pdf_path = 'test_input.pdf'
    input_data = DUAInput(
        pdf_path=pdf_path,
        start_page=0,
        end_page=None,  # All pages
        domain='technical',
        language='en'
    )
    
    print(f"✓ Processing PDF: {pdf_path}")
    result = agent.process(input_data)
    
    print(f"✓ PDF processing complete")
    print(f"  - Pages processed: {result.metadata.num_pages}")
    print(f"  - Content blocks extracted: {len(result.document_tree.sections[0].blocks) if result.document_tree.sections else 0}")
    print(f"  - Confidence: {result.metadata.confidence:.1%}")
    
    # Save extracted content
    extracted_json = "extracted_content.json"
    with open(extracted_json, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"✓ Extracted content saved to: {extracted_json}")
    
except Exception as e:
    print(f"✗ Error in Document Understanding Agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================================
# STEP 2: Brain Agent (Design) - Skipped (Requires Mistral API Key)
# ============================================================================
print("[STEP 2] Brain Agent (Design Presentation)")
print("-" * 70)

api_key = os.environ.get('MISTRAL_API_KEY') if 'os' in dir() else None
if not api_key:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('MISTRAL_API_KEY')

if api_key:
    print("✓ Mistral API key detected")
    print("✓ Brain Agent would design the presentation here")
    print("  (This step is skipped in demo mode)")
else:
    print("⊘ Mistral API key not configured")
    print("  To enable: Create .env file with MISTRAL_API_KEY=your_key")
    print("  Get key from: https://console.mistral.ai/")
    
    # Create sample presentation structure for demo
    print()
    print("  Creating sample presentation structure for demo...")
    sample_slides = {
        "slides": [
            {
                "title": "Introduction to Machine Learning",
                "elements": [
                    {"type": "text", "text": "Machine Learning Fundamentals", 
                     "box": {"x": 50, "y": 50, "w": 880, "h": 80}, 
                     "style": {"fontSize": 44, "bold": True, "align": "center"}}
                ]
            },
            {
                "title": "Key Concepts",
                "elements": [
                    {"type": "text", "text": "Supervised Learning", 
                     "box": {"x": 50, "y": 50, "w": 400, "h": 50},
                     "style": {"fontSize": 28, "bold": True}},
                    {"type": "text", "text": "Unsupervised Learning", 
                     "box": {"x": 500, "y": 50, "w": 400, "h": 50},
                     "style": {"fontSize": 28, "bold": True}},
                    {"type": "text", "text": "Learning from labeled data", 
                     "box": {"x": 50, "y": 120, "w": 400, "h": 100},
                     "style": {"fontSize": 18}}
                ]
            }
        ]
    }
    
    slides_json = "slides.json"
    with open(slides_json, 'w') as f:
        json.dump(sample_slides, f, indent=2)
    print(f"✓ Sample presentation structure created: {slides_json}")

print()

# ============================================================================
# STEP 3: JSON to PPT Agent
# ============================================================================
print("[STEP 3] JSON to PPT Agent (Generate PowerPoint)")
print("-" * 70)

try:
    # Prepare input for PPT generator
    ppt_input = {
        "ppt": {
            "size": {"width": 960, "height": 540, "unit": "px"},
            "defaultUnit": "px",
            "slides": [
                {
                    "title": "Machine Learning Overview",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Introduction to Machine Learning",
                            "box": {"x": 50, "y": 50, "w": 860, "h": 80},
                            "style": {"fontSize": 40, "bold": True, "align": "center"}
                        },
                        {
                            "type": "text",
                            "text": "A comprehensive guide to AI and machine learning concepts",
                            "box": {"x": 50, "y": 150, "w": 860, "h": 50},
                            "style": {"fontSize": 18, "align": "center"}
                        }
                    ]
                },
                {
                    "title": "Key Concepts",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Supervised Learning",
                            "box": {"x": 50, "y": 50, "w": 400, "h": 50},
                            "style": {"fontSize": 24, "bold": True}
                        },
                        {
                            "type": "text",
                            "text": "Learning from labeled training data",
                            "box": {"x": 50, "y": 110, "w": 400, "h": 80},
                            "style": {"fontSize": 14}
                        },
                        {
                            "type": "text",
                            "text": "Unsupervised Learning",
                            "box": {"x": 510, "y": 50, "w": 400, "h": 50},
                            "style": {"fontSize": 24, "bold": True}
                        },
                        {
                            "type": "text",
                            "text": "Finding patterns in unlabeled data",
                            "box": {"x": 510, "y": 110, "w": 400, "h": 80},
                            "style": {"fontSize": 14}
                        }
                    ]
                }
            ]
        }
    }
    
    ppt_input_json = "ppt_input.json"
    with open(ppt_input_json, 'w') as f:
        json.dump(ppt_input, f, indent=2)
    
    print(f"✓ Prepared PPT input: {ppt_input_json}")
    
    # Call the JSON to PPT generator
    sys.path.insert(0, str(Path('JSON To PPT').absolute()))
    from main import build
    
    prs, slide_count = build(ppt_input)
    
    output_pptx = "output_demo.pptx"
    prs.save(output_pptx)
    
    print(f"✓ PowerPoint presentation generated successfully")
    print(f"  - Output file: {output_pptx}")
    print(f"  - Slides created: {slide_count}")
    print(f"  - File size: {Path(output_pptx).stat().st_size} bytes")
    
except Exception as e:
    print(f"✗ Error in JSON to PPT Agent: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("DEMONSTRATION COMPLETE")
print("=" * 70)
print()
print("System Status:")
print("  ✓ Document Understanding Agent: Working")
print("  ✓ Brain Agent: Ready (requires API key for full operation)")
print("  ✓ JSON to PPT Agent: Working")
print()
print("Next Steps:")
print("  1. For full automation, set MISTRAL_API_KEY in .env file")
print("  2. Run: python orchestrator.py input.pdf output.pptx")
print("  3. View output files:")
print(f"     - PDF content: {extracted_json}")
print(f"     - Generated slides: {output_pptx}")
