# 🎙️ Automated Multimodal Agent: PDF to Narrated PowerPoint

A multimodal AI system that autonomously converts static PDF documents into professional PowerPoint presentations with synchronized, AI-generated audio narration.

Powered by an 8-stage agentic pipeline orchestrated with LangGraph and presented through a sleek Streamlit web interface, this tool delivers complete end-to-end automation.

The Automated Multimodal Agent is an advanced artificial intelligence system designed to autonomously convert static PDF documents into dynamic, narrated PowerPoint presentations. Utilizing a sophisticated multi-agent orchestration framework, the system breaks down the complex task of presentation creation into specialized micro-tasks. By seamlessly integrating document parsing, natural language processing (NLP), vector-based semantic retrieval, and Text-to-Speech (TTS) synthesis, the project significantly reduces the time and manual effort required to create professional, accessible, and engaging multimedia presentations.

------
## Article at Medium

You can explore it here: 
🔗 https://medium.com/@mahmoudalyosify/from-static-pdf-to-talking-slides-automated-multimodal-agent-9b62c9a992c3

---

## 🌐 Project Website

You can explore the full project details here:

🔗 https://mahmoudalyosifysite.github.io/Projects/Automated%20MultimodalAgent%20PDF%20to%20Narrated%20PowerPoint.html

---

## 📽️ Demo Video

<p align="center">
  <a href="https://www.youtube.com/watch?v=srhrPcwGKZo" target="_blank">
    <img src="https://img.youtube.com/vi/srhrPcwGKZo/0.jpg" alt="Automated Multimodal Agent Demo" width="700"/>
  </a>
</p>

<p align="center">
  ▶️ Click the image above to watch the full demo on YouTube
</p>

---

## ✨ Key Features

- 📄 **Intelligent PDF Parsing**  
  Extracts text, layout, and structural information seamlessly.

- 🧩 **Semantic Chunking**  
  Organizes content into meaningful blocks for logical slide flow.

- 🔍 **Vector-Based Retrieval**  
  Utilizes FAISS embeddings for intelligent content mapping.

- 🎨 **Automated Slide Planning**  
  Designs optimal slide layouts and content distribution.

- ✍️ **Content Generation**  
  Synthesizes dense text into concise, professional presentation points.

- 🔊 **AI Voice Narration**  
  Generates natural-sounding TTS audio scripts and synchronized `.wav` files.

- 🌐 **Professional Web UI**  
  Real-time progress tracking, error handling, and file management via Streamlit.
---

## 🏗️ System Architecture (v2.0 – LangGraph Edition)

The system deviates from monolithic scripts by utilizing an **Agentic Workflow**.  
Eight specialized agents handle specific micro-tasks, all coordinated by a master LangGraph orchestrator.

```

┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                     │
│  (Upload PDF → Monitor Progress → Download PPTX+Audio)  │
└────────────────────┬────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────┐
│              LangGraph StateGraph Orchestrator          │
├─────────────────────────────────────────────────────────┤
│  [1] PDF Parser   → Extract blocks                      │
│  [2] Chunker      → Create semantic chunks              │
│  [3] Vector DB    → Generate embeddings (FAISS)         │
│  [4] Planner      → Design slide layout                 │
│  [5] Generator    → Synthesize presentation text        │
│  [6] Script Agent → Write narration script              │
│  [7] TTS Agent    → Generate audio (.wav)               │
│  [8] PPTX Builder → Assemble final PowerPoint           │
└─────────────────────────────────────────────────────────┘

````

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

- Python 3.10+
- 8GB+ RAM (16GB recommended)
- 5GB Disk Space (for dependencies and local models)

---

### 2️⃣ Installation

Clone the repository and set up your virtual environment:

```bash
git clone https://github.com/yourusername/Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint.git
cd Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint

# Create and activate virtual environment
python -m venv venv

# On macOS / Linux
source venv/bin/activate  

# On Windows
venv\Scripts\activate

# Install dependencies
cd orchestrator
pip install -r requirements.txt
````

---

### 3️⃣ Run the Web Interface

Launch the Streamlit application:

```bash
streamlit run app.py
```

Then open your browser:

```
http://localhost:8501
```

Upload your PDF, click **Generate**, and download your narrated PowerPoint when complete!

---

### 💻 Legacy CLI Usage (v1.0)

If you prefer the CLI version:

```bash
python "Agentic Systems/Master Orchestrator Agent/master_agent.py"
```

---

## 🛠️ Tech Stack

**Frameworks**

* LangGraph
* Streamlit
* Pydantic

**NLP & ML**

* HuggingFace Transformers
* PyTorch
* Sentence-Transformers
* scikit-learn

**Document Processing**

* PyMuPDF (fitz)
* python-pptx

**Vector Search**

* FAISS
* NumPy

**Audio Synthesis**

* pyttsx3
* SoundFile

---

## 📁 Output Structure

All generated files are neatly organized in the `output/` directory, timestamped for your convenience:

```
output/
└── 20260223_120000/
    ├── YourDocument_Narrated.pptx
    ├── audio/
    │   ├── slide_1.wav
    │   └── slide_2.wav
    └── metadata/
        ├── chunks.json
        ├── embeddings.json
        └── logs.txt
```

---

## 📊 Performance Benchmarks

| PDF Size    | Est. Processing Time | PPTX Size | Total Audio |
| ----------- | -------------------- | --------- | ----------- |
| 5–10 pages  | 3–4 min              | 2–3 MB    | ~60 sec     |
| 10–20 pages | 6–8 min              | 5–8 MB    | ~120 sec    |
| 20–50 pages | 10–15 min            | 10–15 MB  | ~240 sec    |

> ⚡ Utilizing an NVIDIA GPU with CUDA improves embedding generation speeds by approximately 30%.

---

## 🗺️ Roadmap (v2.1+)

* [ ] Async execution for parallel pipeline stages
* [ ] Integration with advanced cloud TTS providers (ElevenLabs, Azure)
* [ ] Multi-language support and translation capabilities
* [ ] Custom corporate `.potx` template support
* [ ] Vision-Language Models (VLMs) for chart/image extraction

---

## 👥 Development Team

* **Mahmoud Alyosify**
* **Mirna Embaby**

---

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 📚 Documentation

For extensive documentation, please refer to:

* `README_COMPLETE.md`
* `SYSTEM_COMPLETE.md`
* `orchestrator/` markdown files

---

## ⭐ Support the Project

If you find this project useful:

* ⭐ Star the repository
* 🐛 Open issues for bugs
* 🚀 Submit pull requests

---

**Automate. Narrate. Elevate.**

