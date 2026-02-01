# Automated Multimodal Agent: PDF-to-Narrated-PowerPoint

Convert any PDF into a professional PowerPoint presentation automatically using AI agents.

```
PDF → Extract Content → Design Slides → Generate PowerPoint
```

## Features

✨ **Fully Automated Pipeline**
- 🤖 Document Understanding Agent - Extracts structure from PDFs
- 🧠 Brain Agent (Mistral AI 7B) - Designs presentations intelligently
- 📊 JSON to PPT Agent - Renders professional PowerPoints
- ⚡ Orchestrator - Coordinates all agents seamlessly

🎨 **Smart Design**
- Automatic slide layout optimization
- Professional color schemes
- Semantic content organization
- Multi-language support

🔧 **Enterprise Ready**
- Fully modular architecture
- REST API compatible
- Batch processing support
- Extensive logging and debugging

## Quick Start

### Installation (30 seconds)
```bash
# 1. Navigate to project
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
echo MISTRAL_API_KEY=your_key_here > .env
```

### Convert PDF to PowerPoint
```bash
python orchestrator.py input.pdf output.pptx
```

That's it! ✓

## System Architecture

### Three Intelligent Agents

```
┌─────────────────────────────────────────┐
│  Document Understanding Agent (DUA)     │
│  - PDF loading & parsing                │
│  - Layout analysis                      │
│  - Block classification                 │
│  - Semantic labeling                    │
│  - Confidence scoring                   │
│  Output: Structured document JSON       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Brain Agent (Mistral AI 7B)            │
│  - Content analysis                     │
│  - Slide design                         │
│  - Layout optimization                  │
│  - Visual hierarchy                     │
│  - Speaker notes                        │
│  Output: Slide specifications JSON      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  JSON to PPT Agent                      │
│  - PowerPoint generation                │
│  - Styling & formatting                 │
│  - Element positioning                  │
│  - Media handling                       │
│  Output: .pptx file                     │
└─────────────────────────────────────────┘
```

## Project Structure

```
Automated Multimodal Agent PDF to Narrated PowerPoint/
├── document_understanding_agent/       # PDF extraction agent
│   ├── src/dua/                       # Core DUA modules
│   ├── streamlit_app.py               # Interactive GUI
│   └── requirements.txt               # DUA dependencies
│
├── brain/                              # Mistral AI agent
│   ├── main.py                        # Brain orchestrator
│   ├── requirements.txt               # Brain dependencies
│   └── .env.example                   # Configuration template
│
├── JSON To PPT/                        # PowerPoint generation
│   ├── main.py                        # PPT renderer
│   ├── ppt.schema.json               # Slide schema
│   └── pyproject.toml                # Dependencies
│
├── orchestrator.py                     # Main pipeline coordinator
├── verify_setup.py                     # System verification
├── test_integration.py                 # Integration tests
│
├── ARCHITECTURE.md                     # System design documentation
├── SETUP.md                            # Complete setup guide
├── QUICKSTART.md                       # Quick start guide
├── EXAMPLES.md                         # Usage examples
│
├── requirements.txt                    # All dependencies
└── .env                                # Configuration (create)
```

## Usage Examples

### Basic Usage
```bash
python orchestrator.py document.pdf output.pptx
```

### With Options
```bash
# Process specific pages
python orchestrator.py document.pdf output.pptx --start-page 1 --end-page 20

# Specify domain and language
python orchestrator.py document.pdf output.pptx --domain academic --language en

# Keep intermediate files for debugging
python orchestrator.py document.pdf output.pptx --keep-temp
```

### Interactive GUI (Preview First)
```bash
cd document_understanding_agent
streamlit run streamlit_app.py
# Opens browser → upload PDF → preview extraction → download JSON
# Then run Brain and PPT agents on exported JSON
```

### Step-by-Step Processing
```bash
# 1. Extract document structure
cd document_understanding_agent
python example_usage.py
# Output: extracted_content.json

# 2. Design slides with Mistral AI
cd ../brain
python main.py ../extracted_content.json slides.json
# Output: slides.json

# 3. Generate PowerPoint
cd ../"JSON To PPT"
python main.py ../slides.json ../output.pptx
# Output: output.pptx
```

## Supported Domains

- **academic** - Research papers, textbooks, lectures
- **business** - Reports, proposals, presentations
- **technical** - Documentation, specifications, manuals
- **general** - Mixed content (default)

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Russian, Chinese, Japanese, Korean, and more.

## Requirements

- **Python**: 3.8+
- **Memory**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for installation
- **API Key**: Mistral AI (free tier: 10K tokens/month)

## Installation

See [SETUP.md](SETUP.md) for complete installation instructions.

### Quick Setup
```bash
# 1. Activate virtual environment
.venv\Scripts\activate  # Windows

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Set Mistral API key
# Create .env file with: MISTRAL_API_KEY=your_key

# 4. Verify installation
python verify_setup.py
```

## Configuration

Create a `.env` file in the project root:
```env
# Required
MISTRAL_API_KEY=sk-your_key_here

# Optional
DUA_LOG_LEVEL=INFO
DUA_EXTRACT_IMAGES=true
OUTPUT_DPI=300
```

Get your free Mistral API key: https://console.mistral.ai/

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and agent contracts
- **[SETUP.md](SETUP.md)** - Complete installation & configuration guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast reference and examples
- **[EXAMPLES.md](EXAMPLES.md)** - Detailed usage scenarios
- **[document_understanding_agent/README.md](document_understanding_agent/README.md)** - DUA documentation
- **[brain/README.md](brain/README.md)** - Brain agent documentation
- **[JSON To PPT/docs/API_SPEC.md](JSON%20To%20PPT/docs/API_SPEC.md)** - PPT agent API reference

## Verification

### Quick Test
```bash
python verify_setup.py
```

### Full Integration Test
```bash
python test_integration.py
```

Both scripts verify:
- ✓ Python version compatibility
- ✓ All dependencies installed
- ✓ API configuration
- ✓ Component initialization
- ✓ File structure integrity

## Performance

| Scenario | Input | Time | Output |
|----------|-------|------|--------|
| Small PDF | 5 pages | ~10s | 2MB |
| Medium PDF | 20 pages | ~30s | 5MB |
| Large PDF | 50 pages | ~90s | 12MB |
| Complex Layout | 10 pages | ~45s | 8MB |

Times include API calls to Mistral AI.

## Troubleshooting

### Issue: "MISTRAL_API_KEY not found"
**Solution**: Create `.env` file with your API key
```env
MISTRAL_API_KEY=sk-your_key_here
```

### Issue: "PDF not found"
**Solution**: Use full path to PDF file
```bash
python orchestrator.py "C:\Users\...\document.pdf" output.pptx
```

### Issue: "Module not found" (dua, etc.)
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Out of memory on large PDFs
**Solution**: Process in page ranges
```bash
python orchestrator.py large.pdf output_1-20.pptx --end-page 20
python orchestrator.py large.pdf output_21-40.pptx --start-page 21 --end-page 40
```

See [SETUP.md](SETUP.md) for more troubleshooting.

## Use Cases

### 1. Academic Presentations
Convert research papers, textbooks, and lecture notes into presentation slides automatically.

```bash
python orchestrator.py paper.pdf presentation.pptx --domain academic
```

### 2. Business Reports
Transform business reports and proposals into executive presentations.

```bash
python orchestrator.py report.pdf presentation.pptx --domain business
```

### 3. Training Materials
Convert training documents and manuals into interactive learning presentations.

```bash
python orchestrator.py manual.pdf presentation.pptx
```

### 4. Batch Processing
Convert multiple PDFs in bulk:

```bash
for file in *.pdf; do
  python orchestrator.py "$file" "${file%.pdf}.pptx"
done
```

## Features Highlights

### Smart Content Extraction
- Preserves document hierarchy
- Identifies semantic elements (headings, body, images)
- Handles complex layouts
- Extracts images and media

### Intelligent Slide Design
- Automatically determines slide count
- Optimizes content distribution
- Applies professional styling
- Generates visual hierarchy

### Flexible Output
- Standard PowerPoint format (.pptx)
- Compatible with Office, Google Slides, LibreOffice
- High-quality rendering
- Professional color schemes

## API Reference

### Orchestrator
```python
from orchestrator import PDFToPresentation

orchestrator = PDFToPresentation()
orchestrator.process(
    pdf_path="input.pdf",
    output_pptx="output.pptx",
    start_page=1,
    end_page=20,
    domain="academic",
    language="en"
)
```

### Document Understanding Agent
```python
from dua import DocumentUnderstandingAgent
from dua.types import DUAInput

agent = DocumentUnderstandingAgent()
output = agent.process(DUAInput(
    pdf_path="document.pdf",
    language="en",
    domain="academic"
))
```

### Brain Agent
```python
from mistralai import Mistral

client = Mistral(api_key="sk-...")
response = client.chat.complete(
    model="mistral-small",
    messages=[{"role": "user", "content": "..."}]
)
```

### PPT Agent
```python
from pptx import Presentation

prs = Presentation()
# Create slides programmatically
prs.save("output.pptx")
```

## Contributing

Contributions are welcome! Areas for enhancement:
- [ ] Audio narration generation
- [ ] Animation and transitions
- [ ] Template marketplace
- [ ] Quality scoring
- [ ] Feedback loop optimization

See [CONTRIBUTING.md](JSON%20To%20PPT/docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Audio narration (Text-to-Speech)
- [ ] Image optimization and enhancement
- [ ] Template library
- [ ] Web interface
- [ ] Cloud deployment
- [ ] Batch API endpoint
- [ ] Quality scoring system

## Support

- 📚 Documentation: [ARCHITECTURE.md](ARCHITECTURE.md), [SETUP.md](SETUP.md)
- 🚀 Quick start: [QUICKSTART.md](QUICKSTART.md)
- 💡 Examples: [EXAMPLES.md](EXAMPLES.md)
- 🐛 Issues: Check individual agent READMEs
- 💬 Discussions: GitHub Discussions

## Authors

Built with Mistral AI, Python-pptx, and PyMuPDF.

## Acknowledgments

- Mistral AI for the 7B model and API
- PyMuPDF for PDF processing
- Python-pptx for PowerPoint generation
- All open-source contributors

---

**Ready to transform your PDFs into presentations?**

```bash
python orchestrator.py your_file.pdf output.pptx
```

For detailed setup instructions, see [SETUP.md](SETUP.md).

For quick examples, see [QUICKSTART.md](QUICKSTART.md).
