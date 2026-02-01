# System Integration Guide - Running the Complete Pipeline

This guide explains how to run the entire PDF-to-Narrated-PowerPoint system with all three AI agents working together.

## Overview

The system consists of three autonomous AI agents that work in sequence:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your PDF Input File                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │ Agent 1: Document Understanding         │
        │ - Parses PDF structure                  │
        │ - Extracts text and layout              │
        │ - Creates semantic labels               │
        │ - Output: JSON (document structure)     │
        └────────┬─────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────┐
        │ Agent 2: Brain (Mistral AI 7B)         │
        │ - Analyzes content structure            │
        │ - Designs presentation layout           │
        │ - Creates slide specifications          │
        │ - Output: JSON (slide designs)          │
        └────────┬─────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────┐
        │ Agent 3: JSON to PowerPoint             │
        │ - Renders PowerPoint file               │
        │ - Applies styles and layouts            │
        │ - Embeds content and media              │
        │ - Output: PPTX file                     │
        └────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│               Your PowerPoint Presentation Output                │
└──────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8+ (test with 3.10+)
- **RAM**: 4GB minimum
- **Storage**: 2GB free

### Required API Key
- **Mistral AI**: Free account at https://console.mistral.ai/
  - Free tier: 10,000 tokens/month
  - Sufficient for ~100 slides of content

## Installation Steps

### Step 1: Prepare Environment
```bash
# Navigate to project
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"

# Create virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Verify activation (you should see (.venv) in prompt)
```

### Step 2: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# This installs:
# - PyMuPDF (PDF reading)
# - Python-pptx (PowerPoint creation)
# - Mistral AI (AI reasoning)
# - Streamlit (optional GUI)
# - And many more support libraries
```

### Step 3: Configure API Key
```bash
# Create .env file with your Mistral API key
# Option A: Create manually
echo MISTRAL_API_KEY=sk-your_actual_key_here > .env

# Option B: Edit .env in your editor
# Add this line:
# MISTRAL_API_KEY=sk-your_actual_key_here

# Get your free key: https://console.mistral.ai/
```

### Step 4: Verify Installation
```bash
# Run verification script
python verify_setup.py

# This checks:
# ✓ Python version
# ✓ All packages installed
# ✓ API key configured
# ✓ All components working
```

## Running the Pipeline

### Option 1: Automated Pipeline (Recommended)

**Simplest method - one command does everything:**

```bash
python orchestrator.py input.pdf output.pptx
```

**With options:**
```bash
# Process specific pages only
python orchestrator.py document.pdf presentation.pptx --start-page 1 --end-page 20

# Specify domain and language
python orchestrator.py document.pdf presentation.pptx --domain academic --language en

# Keep intermediate JSON files
python orchestrator.py document.pdf presentation.pptx --keep-temp
```

**What it does automatically:**
1. ✓ Extracts document structure from PDF
2. ✓ Designs slides using Mistral AI
3. ✓ Generates PowerPoint file
4. ✓ Cleans up temporary files
5. ✓ Provides progress updates

**Typical output:**
```
============================================================
PDF-to-PowerPoint Pipeline Started
============================================================

============================================================
STEP 1: Document Understanding Agent
============================================================
Input PDF: document.pdf
Domain: general, Language: en
Running: python extract_script.py
✓ Extracted content saved to .temp_pipeline/extracted_content.json
  Confidence: 92.50%
  Pages: 10
✓ Step 1 completed successfully

============================================================
STEP 2: Brain Agent (Mistral AI 7B)
============================================================
Input: .temp_pipeline/extracted_content.json
Output: .temp_pipeline/slides.json
Running: python main.py extracted_content.json slides.json
✓ Step 2 completed: Generated 8 slides

============================================================
STEP 3: JSON to PPT Agent
============================================================
Input: .temp_pipeline/slides.json
Output: presentation.pptx
Running: python main.py slides.json presentation.pptx
✓ Step 3 completed: PowerPoint saved to presentation.pptx

============================================================
✓ Pipeline Completed Successfully!
============================================================
Output file: presentation.pptx
File size: 4.25 MB
Temporary files cleaned up
```

### Option 2: Interactive GUI Workflow

**For previewing and customizing extraction:**

```bash
# Start the GUI
cd document_understanding_agent
streamlit run streamlit_app.py

# Opens browser: http://localhost:8501
```

**In the browser:**
1. Upload your PDF
2. Select page range (max 10 pages for preview)
3. Click "Extract"
4. Review extracted content
5. Download `extracted_content.json`

**Then process with Brain and PPT:**
```bash
# From root directory
cd ../brain
python main.py ../extracted_content.json slides.json

cd ../"JSON To PPT"
python main.py ../slides.json ../final_output.pptx
```

### Option 3: Manual Step-by-Step

**Full control over each stage:**

**Step 1: Extract Document Content**
```bash
cd document_understanding_agent

# Run extraction
python example_usage.py

# Interactive prompts:
# - Enter PDF path
# - Select page range
# - Wait for extraction

# Output: extracted_content.json
```

**Step 2: Generate Slide Design**
```bash
cd ../brain

# Create slides from extracted content
python main.py ../document_understanding_agent/extracted_content.json slides.json

# Output: slides.json
# This calls Mistral AI to design the presentation
```

**Step 3: Render PowerPoint**
```bash
cd ../"JSON To PPT"

# Generate the actual PowerPoint file
python main.py ../brain/slides.json ../final_output.pptx

# Output: final_output.pptx
# Ready to open in PowerPoint!
```

## Understanding the Pipeline

### Agent 1: Document Understanding Agent

**What it does:**
- Reads PDF file
- Extracts text, layout, and structure
- Identifies headings, paragraphs, lists, images
- Estimates importance and confidence scores
- Creates document tree representation

**Input:** `document.pdf`
**Output:** `extracted_content.json` with structure like:
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
            "text": "This is the introduction paragraph...",
            "importance": 0.85
          }
        ]
      }
    ]
  },
  "metadata": {
    "num_pages": 10,
    "confidence": 0.92,
    "has_images": true
  }
}
```

### Agent 2: Brain Agent (Mistral AI 7B)

**What it does:**
- Receives extracted document structure
- Analyzes content and creates presentation strategy
- Designs slide layouts and visual hierarchy
- Specifies colors, fonts, positioning
- Generates speaker notes (future feature)

**Input:** `extracted_content.json`
**Output:** `slides.json` with structure like:
```json
{
  "ppt": {
    "size": {"width": 1280, "height": 720, "unit": "px"},
    "theme": {
      "colors": {
        "primary": "#0066CC",
        "secondary": "#FF6B35",
        "accent": "#00D9FF"
      }
    },
    "slides": [
      {
        "id": "slide-1",
        "title": "Title Slide",
        "background": {"color": "#0066CC"},
        "elements": [
          {
            "type": "text",
            "text": "Document Title",
            "box": {"x": 100, "y": 200, "w": 1080, "h": 120},
            "style": {
              "fontSize": 72,
              "bold": true,
              "color": "#FFFFFF"
            }
          }
        ]
      }
    ]
  }
}
```

### Agent 3: JSON to PPT Agent

**What it does:**
- Parses slide specification JSON
- Creates PowerPoint structure
- Positions elements according to specs
- Applies styling and formatting
- Saves as .pptx file

**Input:** `slides.json`
**Output:** `presentation.pptx` (ready to present!)

## Configuration Options

### Environment Variables (.env file)

```env
# Required
MISTRAL_API_KEY=sk-your_key_here

# Optional Document Understanding
DUA_USE_ML=false              # Use ML models (slower, better accuracy)
DUA_EXTRACT_IMAGES=true       # Extract image references
DUA_LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR

# Optional Output
OUTPUT_DPI=300                # Resolution
TEMP_DIR=./.temp_pipeline     # Temporary file location
```

### Command Line Arguments

```bash
python orchestrator.py <input.pdf> <output.pptx> [options]

Options:
  --start-page N        Start page (1-indexed)
  --end-page N          End page (1-indexed)
  --domain DOMAIN       academic|business|technical|general
  --language LANG       en, es, fr, de, it, pt, nl, pl, ru, zh, ja, ko
  --keep-temp           Keep temporary JSON files
  --venv PATH           Path to virtual environment
```

## Troubleshooting

### Problem: "MISTRAL_API_KEY not set"
```bash
# Solution 1: Create .env file
echo MISTRAL_API_KEY=sk-your_key > .env

# Solution 2: Set environment variable
# Windows:
set MISTRAL_API_KEY=sk-your_key

# macOS/Linux:
export MISTRAL_API_KEY=sk-your_key
```

### Problem: "Module 'dua' not found"
```bash
# Solution: Install Document Understanding Agent
cd document_understanding_agent
pip install -e .
cd ..
```

### Problem: "PDF not found"
```bash
# Use full path or ensure file exists
python orchestrator.py "C:\Users\...\document.pdf" output.pptx
# Or check current directory
ls *.pdf  # or dir *.pdf on Windows
```

### Problem: "Out of memory"
```bash
# Process only specific pages
python orchestrator.py large.pdf output.pptx --end-page 20

# Then process rest
python orchestrator.py large.pdf output.pptx --start-page 21
```

### Problem: "Slow performance"
```bash
# Disable image extraction
# Edit orchestrator call or use GUI

# Check internet connection (API calls)
ping console.mistral.ai

# Check API rate limits at https://console.mistral.ai/
```

## Performance Optimization

### For Large PDFs
```bash
# Process in chunks
python orchestrator.py large.pdf part1.pptx --end-page 25
python orchestrator.py large.pdf part2.pptx --start-page 26 --end-page 50
python orchestrator.py large.pdf part3.pptx --start-page 51
```

### For Faster Processing
```bash
# Use CLI instead of GUI
python orchestrator.py input.pdf output.pptx

# Skip image extraction
# Edit streamlit_app.py or use example_usage.py

# Use smaller page ranges
python orchestrator.py input.pdf output.pptx --end-page 10
```

### For Better Quality
```bash
# Use domain-specific settings
python orchestrator.py academic.pdf output.pptx --domain academic

# Set appropriate language
python orchestrator.py spanish.pdf output.pptx --language es

# Keep temp files for review
python orchestrator.py input.pdf output.pptx --keep-temp
```

## Output Files

After running the pipeline:

```
project_root/
├── output.pptx                    ← Your PowerPoint (ready to use!)
│
└── .temp_pipeline/               ← Intermediate files (if --keep-temp)
    ├── extracted_content.json     ← Agent 1 output
    └── slides.json                ← Agent 2 output
```

## Batch Processing

Convert multiple PDFs:

```bash
# Windows batch script
for /r "input_folder" %%f in (*.pdf) do (
  python orchestrator.py "%%f" "output\%%~nf.pptx"
)

# macOS/Linux bash script
for file in input_folder/*.pdf; do
  python orchestrator.py "$file" "output/${file%.pdf}.pptx"
done
```

## API Usage (Programmatic)

```python
from orchestrator import PDFToPresentation

# Create orchestrator
orchestrator = PDFToPresentation()

# Process PDF
orchestrator.process(
    pdf_path="input.pdf",
    output_pptx="output.pptx",
    start_page=1,
    end_page=10,
    domain="academic",
    language="en",
    keep_temp=False
)

print("✓ PowerPoint generated successfully!")
```

## Testing

### Run Tests
```bash
# Verify all components
python verify_setup.py

# Run integration tests
python test_integration.py
```

### Test with Sample PDF
```bash
# Create minimal test PDF first
python -c "
from reportlab.pdfgen import canvas
c = canvas.Canvas('test.pdf')
c.drawString(50, 750, 'Test PDF')
c.showPage()
c.save()
"

# Then run pipeline
python orchestrator.py test.pdf test_output.pptx
```

## Next Steps

1. **✓ Installation**: Follow setup steps above
2. **✓ Configuration**: Set MISTRAL_API_KEY
3. **✓ Verification**: Run `python verify_setup.py`
4. **✓ First Test**: `python orchestrator.py sample.pdf output.pptx`
5. **✓ Customize**: Edit brain/main.py for your style preferences
6. **✓ Scale**: Process your full documents

## Additional Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [QUICKSTART.md](QUICKSTART.md) - Quick examples
- [SETUP.md](SETUP.md) - Detailed setup
- [EXAMPLES.md](EXAMPLES.md) - Usage scenarios
- [README_MAIN.md](README_MAIN.md) - Project overview

## Support

For issues, check:
1. [SETUP.md](SETUP.md) - Troubleshooting section
2. [EXAMPLES.md](EXAMPLES.md) - Common scenarios
3. Individual agent READMEs:
   - document_understanding_agent/README.md
   - brain/README.md
   - JSON To PPT/docs/API_SPEC.md

---

**Ready to convert your PDF to PowerPoint?**

```bash
python orchestrator.py your_file.pdf output.pptx
```

It should complete in 10-60 seconds depending on PDF size!
