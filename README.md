# Automated Multimodal Agent: PDF to Narrated PowerPoint

## 📽️ Demo Video

<video controls width="900" preload="metadata">
  <source src="https://raw.githubusercontent.com/MahmoudAlyosify/Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint/main/Demo/Demo%20of%20the%20Project%20PDF%20to%20Narrated%20Power%20point.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

## 📋 Project Overview

The **PDF to Narrated PowerPoint Generator** is a production-ready multimodal AI system that automatically converts PDF documents into professional PowerPoint presentations with synchronized audio narration. 

The system uses an **8-stage agentic pipeline** orchestrated with **LangGraph**, powered by a **professional Streamlit web interface**, to deliver end-to-end automation:

```
PDF Input → [8-Stage Pipeline] → Narrated PowerPoint + Audio Files
```

### 🎯 What It Does

1. **📄 Parses PDFs** - Intelligently extracts text, layout, and structure
2. **🧩 Chunks Content** - Semantically organizes content into meaningful blocks
3. **🔍 Creates Embeddings** - Generates vector embeddings for semantic understanding
4. **🎨 Plans Slides** - Automatically designs optimal slide layouts
5. **✍️ Generates Content** - Creates presentation structure and formatted content
6. **📝 Writes Scripts** - Generates narration scripts for each slide
7. **🔊 Creates Audio** - Synthesizes natural-sounding audio narration (TTS)
8. **🎁 Builds Output** - Assembles final PowerPoint with embedded/linked audio

### Key Features
- **Intelligent PDF Parsing**: Extracts text, layout, and structural information from PDFs
- **Smart Content Chunking**: Semantically organizes content for logical slide flow
- **Vector-based Retrieval**: Uses embeddings for intelligent content mapping
- **Automated Slide Planning**: Generates optimized slide layouts and content distribution
- **Professional Presentation Generation**: Creates PPTX files with formatted content
- **AI Narration**: Generates natural-sounding audio narration for each slide using TTS
- **End-to-End Orchestration**: Seamless integration of all components through a master agent
### ✨ Key Features

## Team
✅ **Professional Web Interface** - Streamlit GUI with real-time progress tracking  
✅ **Smart Naming** - Output PPT automatically named after input PDF  
✅ **Graph-Based Orchestration** - LangGraph StateGraph for reliable workflow  
✅ **Error Handling** - Graceful degradation with non-critical stage skipping  
✅ **Comprehensive Logging** - Structured logging with execution metadata  
✅ **Audio Support** - Generate and download audio files separately or with PPTX  
✅ **Production Ready** - Full error handling, state persistence, and monitoring  

- **Mahmoud Alyosify**
- **Mirna Mohsen**
---

## 👥 Team & Contributors

## System Architecture
**Developers:**
- 👨‍💼 **Mahmoud Alyosify**
- 👩‍💼 **Mirna Embaby**

The system is built on a multi-agent orchestration framework with the following agents:
**Version:** 2.0 (LangGraph Edition)  
**Last Updated:** February 2026

1. **PDF Parser & Layout Analyzer Agent**: Extracts and analyzes PDF content structure
2. **Semantic Chunker Agent**: Breaks down content into meaningful semantic blocks
3. **Vector DB & Embeddings Layer**: Creates and manages vector embeddings for content
4. **Slide Planner Agent**: Plans slide layouts and content organization
5. **Slide Generator Agent**: Creates presentation structure and content
6. **PPTX Builder Agent**: Builds the actual PowerPoint file
7. **Script Agent**: Generates narration scripts for each slide
8. **TTS Generative Audio Agent**: Creates audio files from scripts
9. **Master Orchestrator Agent**: Coordinates all agents and manages the workflow
---

## Quick Start
## 🛠️ Models and Tools Used

### Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)
### **Core Framework & Orchestration**

### Installation
| Tool | Version | Purpose |
|------|---------|---------|
| **LangGraph** | 0.0.7+ | Graph-based workflow orchestration |
| **Streamlit** | 1.28+ | Web interface and user interaction |
| **Python** | 3.10+ | Runtime and development |

### **NLP & Machine Learning**

| Tool | Version | Purpose |
|------|---------|---------|
| **Transformers** | 4.30+ | NLP models for text processing |
| **PyTorch** | 2.0+ | Deep learning framework |
| **sentence-transformers** | 2.2+ | Semantic embeddings generation |
| **scikit-learn** | 1.3+ | ML utilities and preprocessing |

### **Document Processing**

| Tool | Version | Purpose |
|------|---------|---------|
| **PyMuPDF (fitz)** | 1.23+ | PDF parsing and extraction |
| **python-pptx** | 0.6.21 | PowerPoint file generation |
| **LayoutLMv3** | Optional | Advanced layout analysis |

### **Vector Search & Embeddings**

| Tool | Version | Purpose |
|------|---------|---------|
| **FAISS** | 1.7.4+ | Vector similarity search and indexing |
| **NumPy** | 1.24+ | Numerical computing for embeddings |

### **Audio & Speech Synthesis**

| Tool | Version | Purpose |
|------|---------|---------|
| **pyttsx3** | 2.90+ | Offline text-to-speech (TTS) |
| **SoundFile** | 0.12+ | Audio file I/O |

### **Utilities & Support**

| Tool | Version | Purpose |
|------|---------|---------|
| **Pydantic** | 2.0+ | Data validation and settings |
| **python-dotenv** | 1.0+ | Environment configuration |
| **requests** | 2.31+ | HTTP client for API calls |

---

## 🚀 Steps to Run the Demo

### **Step 1: Prerequisites**

Ensure you have:
- **Python 3.10+** installed
- **8GB RAM** minimum (16GB recommended)
- **5GB disk space** for dependencies
- **Internet connection** (for first-run model downloads)

**Check Python version:**

```bash
python --version
# Should output: Python 3.10.x or higher
```

### **Step 2: Clone/Navigate to Project**

```bash
# Clone or navigate to the project directory
cd "Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint"
```

### **Step 3: Create Virtual Environment (Recommended)**

# Install dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### **Step 4: Install Dependencies**

```bash
cd orchestrator
pip install -r requirements.txt
```

### Usage
**Installation takes ~5-10 minutes** depending on internet speed.

```python
# Run the master orchestrator
python "Agentic Systems/Master Orchestrator Agent/master_agent.py"
```

Provide your PDF file path when prompted, and the system will automatically:
1. Parse the PDF
2. Extract and chunk content
3. Plan the presentation structure
4. Generate slides
5. Create narration scripts
6. Generate audio files
7. Output the final narrated PowerPoint presentation

## Output Structure

All generated files are organized in the `output/` directory:
- `slides/`: Generated PPTX file(s)
- `audio/`: Audio files for narration
- `metadata/`: Intermediate processing files and metadata

## Documentation

For detailed implementation guides and technical documentation, refer to:
- [Complete System Documentation](README_COMPLETE.md)
- [System Architecture Details](SYSTEM_COMPLETE.md)
- [Audio Integration Guide](AUDIO_INTEGRATION_GUIDE.md)
- [Quick Start Audio Setup](QUICK_START_AUDIO.md)

## Project Directory

```
Agentic Systems/
├── 1- PDF Parser and Layout Analyzer Agent/
├── 2- Semantic Chunker Agent/
├── 3- Vector DB + Embeddings Layer/
├── 4- Slide Planner Agent/
├── 5- Slide Generator Agent/
├── 6- PPTX Builder Agent/
├── 7- Script Agent for each slide in PPTX/
├── 8- TTS Generative Audio Agent/
└── Master Orchestrator Agent/
### **Step 5: Launch Streamlit Web Interface**

```bash
streamlit run app.py
```

**Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### **Step 6: Use the Web Interface**

1. **Open browser** → `http://localhost:8501`

2. **Upload PDF:**
   - Click "Choose a PDF file" or drag-and-drop
   - File preview shows name, size, type

3. **Generate Presentation:**
   - Click "✨ Generate Narrated PPT" button
   - Watch real-time progress (8-10 minutes typical)

4. **Download Results:**
   - Click "📊 ⬇️ Download PowerPoint Presentation"
   - File named: `{YourPDF}_Narrated.pptx`
   - Download ZIP option for PPT + audio files

5. **Review:** 
   - View execution summary with timing
   - Check logs panel for detailed processing info
   - See stage-by-stage results

---

## 📊 Processing Timeline

| PDF Size | Est. Time | Output PPTX | Audio |
|----------|-----------|------------|-------|
| 5-10 pages | 3-4 min | 2-3 MB | ~60s |
| 10-20 pages | 6-8 min | 5-8 MB | ~120s |
| 20-50 pages | 10-15 min | 10-15 MB | ~240s |

---

## 📁 Output Structure

After processing, outputs are organized in `orchestrator/output/{timestamp}/`:

```
output/
├── slides/
├── audio/
└── metadata/
└── 20240221_120000/
    ├── Research_Paper_Narrated.pptx    ← Main output
    ├── audio/
    │   ├── slide_1.wav
    │   ├── slide_2.wav
    │   ├── slide_3.wav
    │   └── ... (one per slide)
    └── metadata/
        ├── parsed_blocks.json
        ├── semantic_chunks.json
        ├── slide_plan.json
        ├── presentation.json
        ├── scripts.json
        └── pipeline_state_*.json
```

---

## 🏗️ System Architecture

### **8-Stage Processing Pipeline**

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                      │
│  (Upload PDF → Monitor Progress → Download PPTX+Audio)  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              LangGraph StateGraph Orchestrator          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  START                                                  │
│    ↓                                                    │
│  [1] PDF Parser → Extract blocks (parsed_blocks.json)   │
│    ↓                                                    │
│  [2] Chunker → Semantic chunks (semantic_chunks.json)   │
│    ↓                                                    │
│  [3] Vector DB → Embeddings (chunks.index)              │
│    ↓                                                    │
│  [4] Planner → Slide layout (slide_plan.json)           │
│    ↓                                                    │
│  [5] Generator → Presentation (presentation.json)       │
│    ↓                                                    │
│  [6] Script Agent → Narration (scripts.json)            │
│    ↓                                                    │
│  [7] TTS Agent → Audio (*.wav files)                    │
│    ↓                                                    │
│  [8] PPTX Builder → PowerPoint (lecture.pptx)           │
│    ↓                                                    │
│  Finalize → Output assembly                             │
│    ↓                                                    │
│  END                                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Final Output Delivery                      │
├─────────────────────────────────────────────────────────┤
│  ✓ {PDF}_Narrated.pptx (PowerPoint)                     │
│  ✓ audio/ folder (WAV files)                            │
│  ✓ metadata/ folder (processing logs)                   │
└─────────────────────────────────────────────────────────┘
```

### **Data Flow in Pipeline**

Each agent receives and updates a centralized **PipelineState** object:

```python
PDF File
  ↓
Parser Agent → state.parsed_blocks = [...]
  ↓
Chunker Agent → state.semantic_chunks = [...]
  ↓
Vector Agent → state.vector_store = faiss_index
  ↓
Planner Agent → state.slide_plan = [...]
  ↓
Generator Agent → state.presentation_json = {...}
  ↓
Script Agent → state.scripts = {...}
  ↓
TTS Agent → state.audio_files = [...]
  ↓
PPTX Builder → state.pptx_path = "..."
  ↓
Finalize → Copy to output/ directory
  ↓
Ready for Download
```

---

## 💻 System Requirements

### **Minimum Specifications**

- **Processor:** Multi-core CPU (2+ cores)
- **RAM:** 8 GB
- **Disk Space:** 5 GB for dependencies + 1 GB per PDF
- **Python:** 3.10+
- **OS:** Windows, macOS, or Linux

### **Recommended Specifications**

- **Processor:** 4+ cores, Intel i7/Ryzen 7 or better
- **RAM:** 16 GB
- **Disk Space:** 10 GB+ available
- **GPU:** NVIDIA GPU with CUDA (for 30% faster embeddings)

---

## 📖 Project Directory Structure

```
Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint/
│
├── orchestrator/                           ← NEW: LangGraph + Streamlit
│   ├── app.py                              (Streamlit web interface)
│   ├── graph.py                            (LangGraph orchestration)
│   ├── state.py                            (State management)
│   ├── wrapper_agents.py                   (Agent wrappers)
│   ├── requirements.txt                    (Dependencies)
│   ├── setup.py                            (Setup script)
│   ├── README.md                           (Orchestrator guide)
│   ├── GETTING_STARTED.md                  (Quick start)
│   ├── INTEGRATION_GUIDE.md                (Tech guide)
│   └── .streamlit/config.toml              (Streamlit config)
│
├── Agentic Systems/                        ← Original agents (unchanged)
│   ├── 1- PDF Parser and Layout Analyzer Agent/
│   ├── 2- Semantic Chunker Agent/
│   ├── 3- Vector DB + Embeddings Layer/
│   ├── 4- Slide Planner Agent/
│   ├── 5- Slide Generator Agent/
│   ├── 6- PPTX Builder Agent/
│   ├── 7- Script Agent for each slide in PPTX/
│   ├── 8- TTS Generative Audio Agent/
│   └── Master Orchestrator Agent/          (Original - still available)
│
├── output/                                 ← Processing results
│   └── {timestamp}/
│       ├── {PDF}_Narrated.pptx
│       ├── audio/
│       │   └── slide_*.wav
│       └── metadata/
│
├── README.md                               (This file)
├── LICENSE                                 (Project license)
└── requirements.txt                        (Original dependencies)
```

---

## 🔧 Configuration

### **Streamlit Configuration** (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"

[server]
port = 8501
maxUploadSize = 200          # Max file size (MB)
timeout = 300                # Timeout (seconds)
```

### **Environment Variables** (Optional)

```bash
export PIPELINE_OUTPUT_DIR="./output"
export LOG_LEVEL="INFO"
export MAX_WORKERS="4"
```

---

## 📚 Documentation Files

| Location | File | Purpose |
|----------|------|---------|
| `orchestrator/` | `README.md` | Quick overview |
| `orchestrator/` | `GETTING_STARTED.md` | Step-by-step setup |
| `orchestrator/` | `INTEGRATION_GUIDE.md` | Technical deep-dive |
| `orchestrator/` | `IMPLEMENTATION_SUMMARY.md` | Architecture docs |
| `orchestrator/` | `INDEX.md` | Documentation index |
| Root | `README_COMPLETE.md` | Full system details |
| Root | `SYSTEM_COMPLETE.md` | System architecture |

---

## 🎯 Usage Examples

### **Web Interface (Recommended)**

```bash
# 1. Start the app
cd orchestrator
streamlit run app.py

# 2. Open browser to http://localhost:8501
# 3. Upload PDF and click "Generate"
# 4. Download results when complete
```

### **Python API**

```python
from orchestrator.graph import WorkflowOrchestrator

# Create orchestrator
orch = WorkflowOrchestrator(output_base_dir="output")

# Process PDF
state = orch.execute(
    pdf_path="my_document.pdf",
    pdf_filename="my_document"
)

# Check results
print(f"Status: {state.status}")
print(f"PPTX: {state.pptx_path}")
print(f"Audio Files: {len(state.audio_files)}")
print(f"Duration: {(state.end_time - state.start_time).total_seconds()}s")
```

### **Command Line (Legacy)**

```bash
# Run original master agent (sequential execution)
cd "Agentic Systems/Master Orchestrator Agent"
python master_agent.py
```

---

## ✅ Performance Benchmarks

### **Execution Timeline (20-page PDF)**

| Stage | Time | Output |
|-------|------|--------|
| Parser | ~45s | 135 blocks |
| Chunker | ~12s | 24 chunks |
| Vector | ~60s | 24 embeddings |
| Planner | ~30s | Slide plan |
| Generator | ~45s | presentation.json |
| Script | ~25s | 24 scripts |
| TTS | ~180s | 24 audio files |
| PPTX Builder | ~15s | lecture.pptx |
| **Total** | **~412s** | **~6.8 min** |

### **Resource Usage**

- **Memory:** 2-4 GB average, peak 5-6 GB
- **Disk:** 500 MB for outputs (typical)
- **CPU:** 2-4 cores utilized
- **GPU:** Optional (30% faster with CUDA)

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError: No module named 'langgraph'"**

```bash
pip install -r requirements.txt --upgrade
```

### **Streamlit won't start**

```bash
# Check if port 8501 is available, or use different port
streamlit run app.py --server.port 8502
```

## License
### **PDF parsing fails**

1. Verify PDF is not corrupted
2. Try smaller PDF (5-10 pages)
3. Ensure sufficient disk space (1+ GB free)

### **Out of memory errors**

1. Close other applications
2. Process smaller PDFs
3. Increase system RAM or use GPU mode

### **Audio generation skipped**

This is normal if TTS fails (non-critical stage). You still get:
- ✅ PowerPoint presentation
- 📁 Audio files in output folder
- 📋 Error details in logs

---

## 🔐 Security & Privacy

✅ **Local Processing** - No data sent to cloud services  
✅ **Input Validation** - PDF type and size checking  
✅ **File Isolation** - Each run in separate directory  
✅ **Automatic Cleanup** - Temporary files removed  
✅ **No External APIs** - Uses local models only  

---

## 📊 Comparison: v1.0 vs v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Interface** | CLI only | Web UI (Streamlit) |
| **Orchestration** | Sequential script | LangGraph graph |
| **Error Handling** | Fail-fast | Graceful degradation |
| **Logging** | Basic prints | Structured logs |
| **Progress** | No visibility | Real-time updates |
| **File Naming** | Generic | Uses PDF filename |
| **State Management** | Class attributes | Centralized StateGraph |
| **Documentation** | Minimal | Comprehensive |

---

## 🚀 Future Enhancements (v2.1+)

Planned improvements:

- [ ] Async execution for parallel stages
- [ ] Advanced TTS (Google Cloud, Azure, ElevenLabs)
- [ ] Distributed processing (Ray, Celery)
- [ ] GPU acceleration for embeddings
- [ ] Web-based progress streaming
- [ ] Custom agent pipeline builder UI
- [ ] PDF metadata preservation
- [ ] Multi-language support

---

## 📝 License

See [LICENSE](LICENSE) file for details.

## Support
---

## 🤝 Contributing

Contributions are welcome! For major changes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---


**Last Updated**: March 2026
## 🎬 Quick Start Summary

```bash
# 1. Install
cd orchestrator && pip install -r requirements.txt

# 2. Start
streamlit run app.py

# 3. Upload PDF via web interface

# 4. Download {PDF}_Narrated.pptx when complete

# Done! 🎉
```

---

**Version:** 2.0 (LangGraph Edition)  
**Updated:** March 2026  
**Status:** ✅ Production Ready

**Created by:** 👨‍💼 Mahmoud Alyosify & 👩‍💼 Mirna Embaby
