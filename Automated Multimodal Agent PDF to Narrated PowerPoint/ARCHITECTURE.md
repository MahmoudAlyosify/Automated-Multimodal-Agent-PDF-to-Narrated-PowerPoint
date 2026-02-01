# System Architecture: Automated Multimodal PDF-to-Narrated-PowerPoint Agent

## Overview

This is a **three-agent distributed AI system** that transforms PDFs into narrated PowerPoint presentations using multiple AI models working in concert.

```
PDF Input
   │
   ├─► Document Understanding Agent (Layout Analysis + Block Classification)
   │   Output: JSON with extracted text, layout, semantic labels
   │
   ├─► Brain Agent (Mistral AI 7B - Reasoning & Orchestration)
   │   Output: PowerPoint slide specifications (JSON format)
   │
   └─► JSON to PPT Agent (PowerPoint Rendering)
       Output: .pptx file
```

## Agent Details

### 1. Document Understanding Agent
**Location:** `document_understanding_agent/`

**Purpose:** Extract and understand PDF structure

**Key Capabilities:**
- PDF loading and page extraction (PyMuPDF)
- Layout analysis (spatial understanding)
- Block classification (text type, importance)
- Semantic labeling (contextual meaning)
- Structure building (document hierarchy)
- Confidence scoring (reliability metrics)

**Input:**
```json
{
  "pdf_path": "document.pdf",
  "start_page": 1,
  "end_page": 10,
  "language": "en",
  "domain": "academic"
}
```

**Output:**
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
            "semantic_label": "SECTION_TITLE",
            "text": "...",
            "confidence": 0.95
          }
        ]
      }
    ]
  },
  "metadata": {
    "num_pages": 10,
    "has_images": true,
    "confidence": 0.92
  }
}
```

**Technology Stack:**
- PyMuPDF 1.23.8 - Fast PDF processing
- PDFPlumber 0.10.3 - Data extraction
- NumPy 1.24.3 - Array operations
- Optional: LayoutLMv3 (advanced layout understanding)

---

### 2. Brain Agent (Mistral AI 7B)
**Location:** `brain/`

**Purpose:** Reasoning engine that creates presentation architecture

**Key Capabilities:**
- Analyzes extracted document content
- Creates appropriate slide structure
- Designs visual layouts
- Defines color schemes and typography
- Handles content organization across slides
- Generates speaker notes

**Input:**
JSON output from Document Understanding Agent

**Output:**
```json
{
  "ppt": {
    "size": { "width": 1280, "height": 720, "unit": "px" },
    "defaultUnit": "px",
    "theme": {
      "colors": {
        "primary": "#0066CC",
        "secondary": "#FF6B35",
        "accent": "#00D9FF",
        "dark": "#1A1A2E",
        "light": "#FFFFFF"
      }
    },
    "slides": [
      {
        "id": "slide-1",
        "title": "Title Slide",
        "background": { "color": "#0066CC" },
        "elements": [
          {
            "type": "text",
            "text": "Content here",
            "box": { "x": 100, "y": 200, "w": 1080, "h": 120 },
            "style": {
              "fontSize": 72,
              "align": "center",
              "bold": true,
              "color": "#FFFFFF"
            }
          },
          {
            "type": "image",
            "path": "image.png",
            "box": { "x": 100, "y": 350, "w": 1080, "h": 300 }
          }
        ]
      }
    ]
  }
}
```

**Technology Stack:**
- Mistral AI API (mistral-small model)
- Python-dotenv for configuration
- JSON schema validation

**Environment Variables:**
```
MISTRAL_API_KEY=your_api_key_here
```

---

### 3. JSON to PPT Agent
**Location:** `JSON To PPT/`

**Purpose:** Render PowerPoint files from JSON specifications

**Key Capabilities:**
- Parse slide JSON specifications
- Create PowerPoint structure
- Apply styling and formatting
- Insert images and media
- Handle complex layouts
- Support animations and transitions

**Input:**
Slide JSON from Brain Agent

**Output:**
`.pptx` file (Microsoft PowerPoint format)

**Technology Stack:**
- python-pptx - PowerPoint generation
- Pillow - Image processing
- JSON schema validation

---

## Data Flow

```
┌─────────────────┐
│   PDF File      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Document Understanding Agent           │
│  - Load PDF                             │
│  - Analyze Layout                       │
│  - Classify Blocks                      │
│  - Build Document Tree                  │
│  - Estimate Confidence                  │
└────────┬────────────────────────────────┘
         │
         │ JSON Output
         ▼
┌─────────────────────────────────────────┐
│  Brain Agent (Mistral AI 7B)            │
│  - Analyze Content                      │
│  - Design Slides                        │
│  - Create Layout Specs                  │
│  - Define Visual Theme                  │
│  - Generate Speaker Notes               │
└────────┬────────────────────────────────┘
         │
         │ Slide JSON
         ▼
┌─────────────────────────────────────────┐
│  JSON to PPT Agent                      │
│  - Parse Slide Specs                    │
│  - Create PowerPoint                    │
│  - Apply Styling                        │
│  - Insert Elements                      │
│  - Export PPTX                          │
└────────┬────────────────────────────────┘
         │
         ▼
    ┌─────────────┐
    │ output.pptx │
    └─────────────┘
```

## Configuration & Setup

### Environment Files

**Main workspace root:** `.env`
```
MISTRAL_API_KEY=your_mistral_api_key
```

**Document Understanding Agent:** `document_understanding_agent/.env` (optional)
```
# LayoutLMv3 settings if using ML
USE_LAYOUTLMV3=false
```

### Dependencies

Install using the unified requirements:
```bash
pip install -r requirements.txt
```

Or per agent:
```bash
# Document Understanding
pip install -r document_understanding_agent/requirements.txt

# Brain
pip install -r brain/requirements.txt

# JSON to PPT
pip install -r "JSON To PPT/requirements.txt"
```

## Usage Workflows

### Quick Start (End-to-End)
```bash
python orchestrator.py path/to/input.pdf output.pptx
```

### Step-by-Step

1. **Extract Document Understanding:**
   ```bash
   cd document_understanding_agent
   python streamlit_app.py  # GUI mode
   # OR
   python example_usage.py  # CLI mode
   ```
   Output: `extracted_content.json`

2. **Run Brain Agent:**
   ```bash
   cd brain
   python main.py extracted_content.json slides.json
   ```
   Output: `slides.json`

3. **Generate PowerPoint:**
   ```bash
   cd "JSON To PPT"
   python main.py slides.json output.pptx
   ```
   Output: `output.pptx`

## Agent Communication Protocol

### Message Format
Each agent accepts input as JSON and produces JSON output.

### Error Handling
- Document Understanding: Returns warnings/errors in metadata
- Brain: Validates input schema, returns null on invalid input
- JSON to PPT: Validates slide specs, skips invalid elements

### Logging
All agents log to stdout with configurable verbosity:
- `DEBUG`: Detailed processing steps
- `INFO`: High-level progress
- `WARNING`: Non-critical issues
- `ERROR`: Critical failures

## Performance Characteristics

| Agent | Typical Time | Input Size | Output Size |
|-------|-------------|-----------|------------|
| Document Understanding | 2-10s | 1-50MB PDF | 100KB-5MB JSON |
| Brain (API call) | 5-30s | 100KB-5MB | 200KB-10MB |
| JSON to PPT | 1-5s | 200KB-10MB | 2-100MB PPTX |

**Total time for 10-page PDF:** ~10-45 seconds

## Future Enhancements

- [ ] Audio narration generation (Text-to-Speech)
- [ ] Image extraction and optimization
- [ ] Animation and transition orchestration
- [ ] Template selection based on content type
- [ ] Quality scoring and feedback loop
- [ ] Batch processing multiple PDFs
- [ ] Web API for remote execution

## Troubleshooting

### Document Understanding Agent
- **Issue:** "Streamlit not found" → Install: `pip install streamlit`
- **Issue:** "PDF not loaded" → Verify file exists and is readable
- **Issue:** Low confidence scores → Try LayoutLMv3 model

### Brain Agent
- **Issue:** "MISTRAL_API_KEY not set" → Set in `.env` file
- **Issue:** Invalid output JSON → Check API rate limits
- **Issue:** Poor slide quality → Adjust prompt in main.py

### JSON to PPT Agent
- **Issue:** "Invalid slide specs" → Verify Brain Agent output
- **Issue:** Layout issues → Check coordinate values
- **Issue:** Missing images → Verify paths in JSON

