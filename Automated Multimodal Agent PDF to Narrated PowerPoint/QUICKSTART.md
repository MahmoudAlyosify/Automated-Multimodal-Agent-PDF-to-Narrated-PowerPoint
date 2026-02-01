# Quick Start Guide - PDF to Narrated PowerPoint

## 30-Second Setup

### 1. **Clone or Open Project**
```bash
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"
```

### 2. **Create Virtual Environment** (one-time)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source venv/bin/activate
```

### 3. **Install Dependencies** (one-time)
```bash
pip install -r requirements.txt
```

### 4. **Set Mistral API Key** (one-time)
Create a `.env` file in the project root:
```
MISTRAL_API_KEY=your_mistral_api_key_here
```

Get your API key: https://console.mistral.ai/

## Running the Full Pipeline

### Option A: Quick Command (Recommended)
```bash
python orchestrator.py input.pdf output.pptx
```

### Option B: Step-by-Step

**Step 1: Extract Document Content**
```bash
cd document_understanding_agent
python example_usage.py
# Output: extracted_content.json
```

**Step 2: Generate Slides (Mistral AI)**
```bash
cd ../brain
python main.py extracted_content.json slides.json
# Output: slides.json
```

**Step 3: Create PowerPoint**
```bash
cd ../"JSON To PPT"
python main.py slides.json output.pptx
# Output: output.pptx
```

## Usage Examples

### Basic Usage
```bash
python orchestrator.py lecture.pdf presentation.pptx
```

### With Page Range
```bash
python orchestrator.py lecture.pdf presentation.pptx --start-page 1 --end-page 20
```

### Specify Domain & Language
```bash
python orchestrator.py document.pdf output.pptx --domain academic --language en
```

### Keep Temporary Files
```bash
python orchestrator.py input.pdf output.pptx --keep-temp
```

## Verify Installation

Run this to test all components:
```bash
# Test Document Understanding
python -c "from dua import DocumentUnderstandingAgent; print('✓ DUA OK')"

# Test Brain Agent
python -c "from mistralai import Mistral; print('✓ Mistral AI OK')"

# Test PPT Agent
python -c "from pptx import Presentation; print('✓ Python-pptx OK')"
```

## Troubleshooting

### "MISTRAL_API_KEY not set"
- Create `.env` file with `MISTRAL_API_KEY=your_key`
- Or set environment variable: `set MISTRAL_API_KEY=your_key`

### "PDF not found"
- Use absolute or relative path to PDF
- Ensure file exists: `ls input.pdf`

### "Streamlit not found"
```bash
pip install streamlit
```

### "ImportError: dua"
```bash
cd document_understanding_agent
pip install -e .
```

## Document Understanding Agent GUI

For interactive PDF processing:
```bash
cd document_understanding_agent
streamlit run streamlit_app.py
```
Opens browser at: http://localhost:8501

## Performance Tips

- **Large PDFs**: Use `--start-page` and `--end-page` to process in chunks
- **Faster Processing**: Reduce image extraction in Document Understanding Agent
- **Better Results**: Specify correct `--domain` for your content type

## Architecture Overview

```
PDF
  ↓ [Document Understanding Agent]
extracted_content.json (structured document tree)
  ↓ [Brain Agent - Mistral AI 7B]
slides.json (presentation specification)
  ↓ [JSON to PPT Agent]
output.pptx (PowerPoint file)
```

## What Each Agent Does

| Agent | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Document Understanding** | PDF file | JSON with document structure | Extract text, layout, semantic labels |
| **Brain (Mistral AI)** | Structured JSON | Slide specifications | Design presentation, organize content |
| **JSON to PPT** | Slide JSON | PowerPoint file | Render actual PowerPoint presentation |

## Environment Variables

```bash
# Required
MISTRAL_API_KEY=sk-...

# Optional
DUA_LOG_LEVEL=INFO          # Document Understanding logging
PPT_DPI=300                 # Output resolution
TEMP_DIR=./.temp_pipeline   # Temporary file location
```

## Next Steps

1. ✅ Installation done
2. 📄 Try: `python orchestrator.py example.pdf test_output.pptx`
3. 🎨 Customize brain agent prompt in `brain/main.py`
4. 🔧 Configure styling in slide JSON schema

## Support

- 📚 Full Documentation: See [ARCHITECTURE.md](ARCHITECTURE.md)
- 🐛 Issues: Check individual agent READMEs
- 💡 Examples: See `examples/` folder

---

**Ready to convert your PDF?** 
```bash
python orchestrator.py yourfile.pdf output.pptx
```
