# Example Workflows & Testing

This document provides complete example workflows for the PDF-to-Narrated-PowerPoint system.

## Example 1: Simple Document (Academic Paper)

### Input
- Academic research paper (10 pages)
- English language
- Technical domain

### Execution
```bash
python orchestrator.py "examples/research_paper.pdf" "examples/output/research_paper.pptx" \
    --domain academic \
    --language en \
    --end-page 10
```

### Expected Outputs
- **Time**: ~15-30 seconds
- **Slides**: 8-12 slides
- **File Size**: 2-5 MB

### Generated Structure
```
Title Slide
├── Abstract Summary
├── Introduction
├── Literature Review
├── Methodology
├── Results & Findings
├── Discussion
└── Conclusion & References
```

---

## Example 2: Business Document (Detailed)

### Input
- Business proposal (25 pages)
- English language
- Business domain

### Execution
```bash
python orchestrator.py "examples/business_proposal.pdf" "examples/output/proposal.pptx" \
    --domain business \
    --language en
```

### Configuration (Advanced)
For more control, process step-by-step:

**Step 1: Extract Content**
```bash
cd document_understanding_agent
python example_usage.py
# Select page range interactively
# Output: extracted_content.json
```

**Step 2: Review & Modify (Optional)**
Edit `extracted_content.json` to adjust content emphasis

**Step 3: Generate Slides**
```bash
cd ../brain
python main.py ../extracted_content.json slides.json
```

**Step 4: Create Presentation**
```bash
cd ../"JSON To PPT"
python main.py ../slides.json ../output.pptx
```

---

## Example 3: Interactive GUI Workflow

### Best For
- Preview extraction before processing
- Manual content curation
- Complex documents requiring review

### Steps

**1. Start GUI:**
```bash
cd document_understanding_agent
streamlit run streamlit_app.py
```

**2. In Browser (http://localhost:8501):**
- Upload PDF file
- Select page range (max 10 pages)
- Click "Extract Content"
- Review extracted text and layout
- Download `extracted_content.json`

**3. Run Brain Agent:**
```bash
cd ../brain
python main.py extracted_content.json slides.json
```

**4. Generate PowerPoint:**
```bash
cd ../"JSON To PPT"
python main.py slides.json output.pptx
```

---

## Example 4: Batch Processing Multiple PDFs

### Use Case
Convert multiple PDFs to presentations

### Script: `batch_process.py`
```python
#!/usr/bin/env python3
"""Batch process multiple PDFs to PowerPoints."""

import os
from pathlib import Path
from orchestrator import PDFToPresentation

def batch_process(input_dir, output_dir):
    """Process all PDFs in input directory."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    orchestrator = PDFToPresentation()
    
    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs to process")
    
    for i, pdf in enumerate(pdf_files, 1):
        output_pptx = output_path / pdf.stem / ".pptx"
        print(f"\n[{i}/{len(pdf_files)}] Processing {pdf.name}")
        
        try:
            orchestrator.process(
                pdf_path=str(pdf),
                output_pptx=str(output_pptx)
            )
            print(f"✓ Successfully created {output_pptx}")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    batch_process("./input_pdfs", "./output_presentations")
```

### Execution
```bash
python batch_process.py
```

---

## Example 5: Custom Domain & Language

### Scenario
Converting Spanish business documents

### Execution
```bash
python orchestrator.py \
    "documento_negocio.pdf" \
    "presentacion.pptx" \
    --domain business \
    --language es
```

### Supported Languages
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `nl` - Dutch
- `pl` - Polish
- `ru` - Russian
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean

### Supported Domains
- `academic` - Research papers, textbooks
- `business` - Reports, proposals, presentations
- `technical` - Documentation, specifications
- `general` - Default for mixed content

---

## Example 6: Large Document Processing

### Challenge
50+ page PDF with memory constraints

### Solution: Page Chunking
```bash
# Process first 20 pages
python orchestrator.py large_doc.pdf output_part1.pptx --end-page 20

# Process next 20 pages
python orchestrator.py large_doc.pdf output_part2.pptx \
    --start-page 21 \
    --end-page 40

# Process remaining
python orchestrator.py large_doc.pdf output_part3.pptx \
    --start-page 41
```

### Combining Presentations
After creating parts, manually combine them in PowerPoint:
1. Open output_part1.pptx
2. Insert slides from output_part2.pptx (via Insert → Pictures → From File)
3. Repeat for output_part3.pptx

---

## Example 7: Debugging & Troubleshooting

### Keep Temporary Files
```bash
python orchestrator.py input.pdf output.pptx --keep-temp
```

### Inspect Intermediate Files
```
.temp_pipeline/
├── extracted_content.json    # Document Understanding output
└── slides.json               # Brain Agent output
```

### Debug Document Extraction
```bash
cd document_understanding_agent
python -c "
from pathlib import Path
from src.dua import DocumentUnderstandingAgent
from src.dua.types import DUAInput

agent = DocumentUnderstandingAgent()
input_data = DUAInput(pdf_path='your.pdf', end_page=1)
output = agent.process(input_data)

print(f'Extracted {len(output.document_tree.sections)} sections')
print(f'Confidence: {output.metadata[\"confidence\"]:.2%}')

# Print first section
if output.document_tree.sections:
    section = output.document_tree.sections[0]
    print(f'Title: {section.title}')
    print(f'Blocks: {len(section.blocks)}')
"
```

---

## Test Data

### Minimal Test PDF
For testing the pipeline without a real PDF:

**Create test PDF:**
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "Test Document")
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "This is a test PDF for the pipeline")
    c.drawString(50, 680, "Created for demonstration purposes")
    
    c.showPage()
    c.save()

create_test_pdf("test_document.pdf")
```

### Test Pipeline
```bash
python orchestrator.py test_document.pdf test_output.pptx --keep-temp
```

---

## Expected Outputs Reference

### After Step 1 (Document Understanding)
File: `extracted_content.json`
```json
{
  "document_tree": {
    "sections": [
      {
        "title": "Introduction",
        "level": 1,
        "blocks": [
          {
            "type": "HEADING",
            "text": "Introduction",
            "confidence": 0.95
          },
          {
            "type": "PARAGRAPH",
            "text": "This document...",
            "semantic_label": "INTRODUCTION"
          }
        ]
      }
    ]
  },
  "metadata": {
    "num_pages": 5,
    "confidence": 0.92
  }
}
```

### After Step 2 (Brain Agent)
File: `slides.json`
```json
{
  "ppt": {
    "size": {"width": 1280, "height": 720},
    "theme": {
      "colors": {
        "primary": "#0066CC",
        "secondary": "#FF6B35"
      }
    },
    "slides": [
      {
        "id": "slide-1",
        "title": "Title Slide",
        "elements": [
          {
            "type": "text",
            "text": "Document Title",
            "style": {"fontSize": 72, "bold": true}
          }
        ]
      }
    ]
  }
}
```

### After Step 3 (JSON to PPT)
File: `output.pptx`
- Standard PowerPoint format
- Openable in Microsoft PowerPoint, Google Slides, etc.
- Contains all specified elements, styles, and layouts

---

## Performance Benchmarks

| Scenario | Input | Time | Output |
|----------|-------|------|--------|
| Small PDF | 5 pages | 10s | 2MB |
| Medium PDF | 20 pages | 30s | 5MB |
| Large PDF | 50 pages | 90s | 12MB |
| Complex Layout | 10 pages + images | 45s | 8MB |
| Multi-language | 15 pages | 35s | 6MB |

---

## Validation Checklist

After running the pipeline:

- [ ] Output PowerPoint opens without errors
- [ ] All slides render correctly
- [ ] Text formatting is applied properly
- [ ] Images display correctly (if applicable)
- [ ] Color scheme matches specifications
- [ ] Slide count matches expected amount
- [ ] No missing content from source PDF

---

## Customization Examples

### Example: Change Color Scheme

Edit `brain/main.py` to customize theme:
```python
custom_colors = {
    "primary": "#FF0000",      # Red
    "secondary": "#00FF00",    # Green
    "accent": "#0000FF",       # Blue
    "dark": "#000000",
    "light": "#FFFFFF"
}
```

### Example: Adjust Slide Count

Modify the Brain Agent prompt to prefer more/fewer slides:
```python
# In brain/main.py - adjust this line:
prompt = f"""
...
Requirements:
- Create {content_length // 500} slides minimum
- One slide per section maximum
...
"""
```

### Example: Custom Image Extraction

In `document_understanding_agent/src/dua/agent.py`:
```python
# Enable/disable image extraction
agent = DocumentUnderstandingAgent(
    extract_images=True,    # Change to False to skip images
    use_ml=True             # Enable ML models
)
```

---

## Next Steps

1. **Run a test:** `python orchestrator.py test.pdf output.pptx`
2. **Review output:** Open output.pptx in PowerPoint
3. **Customize:** Edit brain/main.py for your preferences
4. **Scale up:** Process full-length documents
5. **Batch process:** Handle multiple PDFs

---

For more information, see [ARCHITECTURE.md](ARCHITECTURE.md) and [SETUP.md](SETUP.md).
