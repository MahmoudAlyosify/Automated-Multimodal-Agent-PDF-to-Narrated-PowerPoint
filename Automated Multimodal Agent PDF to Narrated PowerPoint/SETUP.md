# Complete Setup Guide - PDF to Narrated PowerPoint

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Running the System](#running-the-system)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.8+ (tested with 3.10, 3.11, 3.13)
- **OS**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 2GB for installation + dependencies

### Required Accounts/Keys
- **Mistral AI API Key**: Get from https://console.mistral.ai/
  - Free tier available: 10,000 tokens/month
  - Used for slide design and content optimization

## Installation

### Step 1: Clone/Download Project

```bash
# If from GitHub
git clone <repository-url>
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"

# Or just open the project folder
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"
```

### Step 2: Create Virtual Environment

**Windows:**
```batch
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when activated.

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: Install Dependencies

**All at once (recommended):**
```bash
pip install -r requirements.txt
```

**Or individually by agent:**
```bash
# Document Understanding Agent
pip install -r document_understanding_agent/requirements.txt

# Brain Agent
pip install -r brain/requirements.txt

# JSON to PPT Agent
pip install -r "JSON To PPT/requirements.txt"
```

### Step 5: Install LayoutLMv3 (Optional)

For advanced document layout understanding:

```bash
# This is optional but improves accuracy for complex PDFs
pip install torch transformers torchvision
python document_understanding_agent/init_layoutlmv3.py
```

## Configuration

### Step 1: Create .env File

In the project root directory, create a file named `.env`:

**Windows (Command Prompt):**
```batch
type nul > .env
# Then open in notepad and add:
```

**Unix/macOS:**
```bash
touch .env
# Then open in your editor
```

**Content:**
```env
# Mistral AI Configuration
MISTRAL_API_KEY=your_actual_api_key_here

# Optional: Document Understanding Agent
DUA_USE_ML=false
DUA_EXTRACT_IMAGES=true
DUA_LOG_LEVEL=INFO

# Optional: Output Settings
OUTPUT_DPI=300
TEMP_DIR=./.temp_pipeline
```

### Step 2: Get Mistral API Key

1. Go to https://console.mistral.ai/
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key
5. Copy key to `.env` file

### Step 3: Verify .env File

```bash
# Test that API key is loaded (Windows)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('MISTRAL_API_KEY:', 'set' if os.getenv('MISTRAL_API_KEY') else 'NOT SET')"
```

## Verification

### Quick Verification (< 1 minute)

Run all component tests:
```bash
python verify_setup.py
```

Or manually test each component:

```bash
# Test 1: Document Understanding Agent
cd document_understanding_agent
python -c "from src.dua import DocumentUnderstandingAgent; print('✓ DUA imports successfully')"

# Test 2: Brain Agent
cd ../brain
python -c "from mistralai import Mistral; print('✓ Mistral AI imports successfully')"

# Test 3: JSON to PPT
cd ../"JSON To PPT"
python -c "from pptx import Presentation; print('✓ Python-pptx imports successfully')"

# Back to root
cd ..
```

### Comprehensive Verification

Run the full verification script:
```bash
python -c "
from pathlib import Path
import sys
import json

# Check Python version
print(f'Python: {sys.version.split()[0]}')

# Check virtual environment
print(f'VEnv: {hasattr(sys, 'real_prefix') or sys.prefix != sys.base_prefix}')

# Check imports
try:
    import pymupdf
    print('✓ PyMuPDF')
except ImportError:
    print('✗ PyMuPDF')

try:
    import pdfplumber
    print('✓ PDFPlumber')
except ImportError:
    print('✗ PDFPlumber')

try:
    from mistralai import Mistral
    print('✓ Mistral AI')
except ImportError:
    print('✗ Mistral AI')

try:
    from pptx import Presentation
    print('✓ Python-pptx')
except ImportError:
    print('✗ Python-pptx')

try:
    import streamlit
    print('✓ Streamlit')
except ImportError:
    print('✗ Streamlit')
"
```

## Running the System

### Method 1: Automated Orchestrator (Recommended)

**Basic:**
```bash
python orchestrator.py input.pdf output.pptx
```

**With Options:**
```bash
python orchestrator.py input.pdf output.pptx \
    --start-page 1 \
    --end-page 10 \
    --domain academic \
    --language en \
    --keep-temp
```

**Options:**
- `--start-page N`: Process from page N (1-indexed)
- `--end-page N`: Process up to page N
- `--domain`: academic|business|technical|general
- `--language`: Language code (en, es, fr, etc.)
- `--keep-temp`: Keep temporary JSON files for debugging

### Method 2: Interactive Document Understanding GUI

```bash
cd document_understanding_agent
streamlit run streamlit_app.py
```

Then:
1. Upload PDF in browser (http://localhost:8501)
2. Select page range
3. Click "Extract"
4. Download `extracted_content.json`

### Method 3: Manual Step-by-Step

**Step 1 - Extract Document:**
```bash
cd document_understanding_agent
python example_usage.py
# Creates: extracted_content.json
cd ..
```

**Step 2 - Generate Slides:**
```bash
cd brain
python main.py extracted_content.json slides.json
# Creates: slides.json
cd ..
```

**Step 3 - Create PowerPoint:**
```bash
cd "JSON To PPT"
python main.py slides.json output.pptx
# Creates: output.pptx
```

## Output Structure

After successful processing, you'll have:

```
project_root/
├── output.pptx                 # Final PowerPoint
├── .temp_pipeline/
│   ├── extracted_content.json  # Step 1 output
│   └── slides.json             # Step 2 output
```

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Small PDF (1-5 pages) | 5-15s | Quick turnaround |
| Medium PDF (10-20 pages) | 15-45s | Normal processing |
| Large PDF (50+ pages) | 1-3 min | Use `--end-page` to limit |
| Mistral API call | 5-30s | Depends on API load |
| PPT generation | 1-5s | Usually fast |

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'dua'`

**Solution:**
```bash
cd document_understanding_agent
pip install -e .
cd ..
```

### MISTRAL_API_KEY Not Found

**Problem:** `ValueError: MISTRAL_API_KEY environment variable not set`

**Solutions:**
1. Create `.env` file in project root with `MISTRAL_API_KEY=your_key`
2. Or set environment variable:
   ```bash
   # Windows
   set MISTRAL_API_KEY=your_key
   
   # Unix/macOS
   export MISTRAL_API_KEY=your_key
   ```

### PDF Not Processing

**Problem:** `FileNotFoundError: PDF not found`

**Solutions:**
1. Use full path: `python orchestrator.py "C:\Users\...\file.pdf" output.pptx`
2. Check file exists: `ls input.pdf` or `dir input.pdf`
3. Check permissions: File should be readable

### Out of Memory

**Problem:** `MemoryError` on large PDFs

**Solutions:**
1. Process page ranges: `--start-page 1 --end-page 20`
2. Disable image extraction: Set `DUA_EXTRACT_IMAGES=false`
3. Increase available RAM

### Streamlit Not Found

**Problem:** `streamlit: command not found`

**Solution:**
```bash
pip install streamlit
# Or for GUI only:
cd document_understanding_agent
pip install -r requirements.txt
```

### Slow Performance

**Problem:** Each step takes very long

**Solutions:**
1. Check internet connection (Mistral API calls)
2. Check Mistral API rate limits
3. Reduce page count with `--end-page`
4. Disable image processing

## Common Workflows

### Workflow 1: Quick Presentation (1-2 min)
```bash
# Process first 5 pages only
python orchestrator.py document.pdf output.pptx --end-page 5
```

### Workflow 2: Full Document (10-30 min)
```bash
# Process entire document
python orchestrator.py document.pdf output.pptx --domain general
```

### Workflow 3: Academic/Technical (5-20 min)
```bash
# Optimize for academic content
python orchestrator.py research_paper.pdf presentation.pptx --domain academic
```

### Workflow 4: Interactive Design (Custom)
```bash
# Use GUI for preview, then generate
cd document_understanding_agent
streamlit run streamlit_app.py
# Review extracted content, then run:
cd ..
python brain/main.py extracted_content.json slides.json
python "JSON To PPT/main.py" slides.json output.pptx
```

## Updating Dependencies

To update all packages to latest versions:
```bash
pip install --upgrade -r requirements.txt
```

Or specific packages:
```bash
pip install --upgrade mistralai python-pptx streamlit
```

## Deactivating Virtual Environment

When done working:
```bash
# Windows
.venv\Scripts\deactivate

# macOS/Linux
deactivate
```

## Next Steps

1. ✅ Complete setup with SETUP.md
2. 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. ⚡ Check [QUICKSTART.md](QUICKSTART.md) for quick examples
4. 🔧 Customize brain agent in `brain/main.py`
5. 🎨 Modify slide templates in `JSON To PPT/ppt.schema.json`

## Support & Help

- **Agent Issues**: Check individual README files
- **Architecture**: See `ARCHITECTURE.md`
- **Quick Help**: See `QUICKSTART.md`
- **API Reference**: See `document_understanding_agent/API_REFERENCE.md`

---

**Installation complete!** Ready to process your first PDF.

```bash
python orchestrator.py your_file.pdf output.pptx
```
