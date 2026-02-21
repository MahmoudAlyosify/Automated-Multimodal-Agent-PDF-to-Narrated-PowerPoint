# Getting Started - PDF to Narrated PowerPoint with LangGraph

## 🎯 Quick Start (5 minutes)

### Step 1: Install Packages

```bash
cd orchestrator
pip install -r requirements.txt
```

### Step 2: Launch Web Interface

```bash
streamlit run app.py
```

### Step 3: Use the GUI

1. Open browser → http://localhost:8501
2. Click "Choose a PDF file" → select your PDF
3. Click "✨ Generate Narrated PPT" button
4. Watch progress in real-time
5. Download PPTX when complete

**That's it!** Your presentation will be ready in 6-8 minutes.

---

## 📋 What You Get

✅ `Narrated-PowerPoint.pptx` - Fully formatted presentation  
✅ `audio/*.wav` - Individual slide narrations  
✅ `metadata/*.json` - Processing logs and metadata

---

## 🏗️ System Architecture Overview

```
Your PDF
    ↓
LangGraph Orchestrator
    ├─ Parser Agent (extract content)
    ├─ Chunker Agent (organize content)
    ├─ Vector Agent (create embeddings)
    ├─ Planner Agent (plan slides)
    ├─ Generator Agent (create content)
    ├─ Script Agent (write narration)
    ├─ TTS Agent (generate audio)
    └─ PPTX Builder (create PowerPoint)
    ↓
Final Output (PPTX + Audio)
```

---

## 💻 System Requirements

- **Python:** 3.10 or higher
- **RAM:** 8GB minimum (16GB recommended)
- **Disk Space:** 5GB for dependencies + 1GB per PDF (approximate)
- **GPU:** Optional (NVIDIA GPU with CUDA for faster embeddings)

### Check Python Version

```bash
python --version
# Should show Python 3.10.x or higher
```

---

## 🚀 Installation Details

### 1. Navigate to Orchestrator

```bash
cd path/to/Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint/orchestrator
```

### 2. Verify Structure

Ensure parent directory has all agents:
```
../Agentic Systems/
├── 1- PDF Parser and Layout Analyzer Agent/
├── 2- Semantic Chunker Agent/
├── 3- Vector DB + Embeddings Layer/
├── 4- Slide Planner Agent/
├── 5- Slide Generator Agent/
├── 6- PPTX Builder Agent/
├── 7- Script Agent for each slide in PPTX/
└── 8- TTS Generative Audio Agent/
```

### 3. Create Virtual Environment (Optional but Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Installation should take 5-10 minutes depending on internet speed.

### 5. Verify Installation

```bash
python -c "import langgraph; import streamlit; print('✅ Ready!')"
```

---

## 🎨 Using the Web Interface

### Upload PDF

1. Click the file uploader area
2. Select a PDF file from your computer
3. See file preview with name, size, type

### Generate Presentation

1. Click "✨ Generate Narrated PPT" button
2. System starts processing (takes 6-8 minutes)
3. Progress bar shows overall completion
4. Stage indicators show which step is running

### Monitor Progress

Real-time updates show:
- ✓ PDF Parser (135 blocks extracted)
- ✓ Semantic Chunker (24 chunks)
- ✓ Vector Embeddings (24 embeddings)
- ... (all 8 stages)

### Download Results

When complete:
1. Click "📊 Download PPTX" → saves `narrated_presentation.pptx`
2. Click "📦 Download ZIP" → saves `narrated_presentation.zip` (includes audio)
3. View "📊 Execution Summary" → timing and statistics

---

## 🔍 Viewing Detailed Logs

1. Expand "📋 Execution Logs" section
2. See timestamped log entries
3. Check "🎯 Pipeline Stages" for stage-by-stage results

### Log Format

```
[12:34:56] INFO     Parser       Starting PDF parsing...
[12:35:01] SUCCESS  Parser       Extracted 135 blocks
[12:35:01] INFO     Chunker      Starting semantic chunking...
[12:35:13] SUCCESS  Chunker      Created 24 chunks
```

---

## 📁 Output Files

After processing, you'll find:

```
output/
└── {timestamp}/
    ├── Narrated-PowerPoint.pptx        ← Your final presentation
    ├── audio/
    │   ├── slide_1.wav
    │   ├── slide_2.wav
    │   └── ... (one for each slide)
    └── metadata/
        ├── parsed_blocks.json
        ├── semantic_chunks.json
        ├── slide_plan.json
        ├── presentation.json
        ├── scripts.json
        └── pipeline_state_{id}.json
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langgraph'"

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Streamlit app won't start

**Solution:** Check port 8501 is available
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: "PDF not found" error

**Solution:** Use full path to PDF file
```python
state = orchestrator.execute("/full/path/to/document.pdf")
```

### Issue: Pipeline fails at vector stage

**Solution:** Too large PDF. Try smaller PDFs or:
1. Add more RAM
2. Use GPU acceleration
3. Process PDF in sections

### Issue: Audio generation skipped

**Solution:** This is normal if TTS fails. You get:
- ✅ PPTX without embedded audio
- 📥 Audio files still available in `audio/` folder

---

## 🔐 Privacy & Security

✅ **Everything stays local**
- No cloud uploads
- No external API calls
- PDF never leaves your machine
- All processing on your computer

✅ **Safe file handling**
- Automatic temporary file cleanup  
- Output organized by run ID
- No cross-contamination between runs

---

## 📊 Performance Tips

### Faster Processing

1. **Use a smaller PDF** (start with <20 pages)
2. **GPU Acceleration** (if NVIDIA GPU available):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. **Increase RAM** - More RAM = faster embedding processing

### Expected Times (by PDF size)

| Pages | Time | PPTX Size |
|-------|------|-----------|
| 5-10 | 3-4 min | 2-3 MB |
| 10-20 | 6-8 min | 5-8 MB |
| 20-50 | 10-15 min | 10-15 MB |
| 50+ | 15-30 min | 20+ MB |

---

## 🎓 Advanced Usage

### Python API

Instead of web UI, use Python directly:

```python
from orchestrator.graph import WorkflowOrchestrator

# Create orchestrator
orch = WorkflowOrchestrator(output_base_dir="output")

# Execute pipeline
state = orch.execute(
    pdf_path="/path/to/document.pdf",
    run_id="my_document_2024"
)

# Check results
if state.status == "completed":
    print(f"Success! PPTX: {state.pptx_path}")
    print(f"Audio files: {len(state.audio_files)}")
    print(f"Duration: {(state.end_time - state.start_time).total_seconds()}s")
else:
    print(f"Failed: {state.error_message}")
```

### Direct Graph Usage

```python
from orchestrator.graph import create_workflow_graph
from orchestrator.state import PipelineState

# Create graph
graph = create_workflow_graph()

# Initialize state
state = PipelineState(
    pdf_path="document.pdf",
    output_dir="output"
)

# Run
final_state = graph.invoke(state)
```

### Callbacks for Monitoring

```python
def on_stage_complete(state):
    print(f"Stage: {state.current_stage}")

orchestrator.execute(
    pdf_path="doc.pdf",
    callbacks={"on_complete": on_stage_complete}
)
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | User-friendly overview |
| `INTEGRATION_GUIDE.md` | Technical deep-dive |
| `IMPLEMENTATION_SUMMARY.md` | Architecture and design decisions |
| `setup.py` | Automated setup script |
| `requirements.txt` | Python dependencies |

---

## 🔧 Customization

### Adjust Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"  # Change primary color
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"

[server]
port = 8501              # Change port
maxUploadSize = 200      # Max file size in MB
timeout = 300            # Timeout in seconds
```

### Modify Agent Parameters

In `wrapper_agents.py`, customize agent behavior:

```python
def run_parser_agent(state: PipelineState) -> PipelineState:
    parser = PDFParserAgent(
        use_layoutlmv3=True,  # Enable layout analysis
        # Add other parameters here
    )
    # ...
```

---

## 🆘 Getting Help

### Check Logs

1. **In Streamlit UI:**
   - Expand "📋 Execution Logs" section
   - Look for ERROR or WARN entries

2. **In Files:**
   - `output/{run_id}/metadata/pipeline_state_{run_id}.json`
   - Contains full execution log

### Common Issues & Solutions

**Q: Takes too long?**  
A: Normal for large PDFs. First run slower due to model downloads.

**Q: No audio files?**  
A: TTS is non-critical. PPTX still works. Check permissions in `audio/` folder.

**Q: PDF parsing fails?**  
A: Try different PDF or check if it's corrupted.

**Q: Out of memory?**  
A: Close other apps or process smaller PDFs.

### Reporting Issues

When reporting issues, include:
1. PDF file details (size, pages)
2. Error message from logs
3. Stage where it failed
4. System specs (RAM, GPU, Python version)

---

## 🎯 Next Steps

1. ✅ **Install** - `pip install -r requirements.txt`
2. ✅ **Start** - `streamlit run app.py`
3. ✅ **Upload** - Select your first PDF
4. ✅ **Wait** - Let pipeline process
5. ✅ **Download** - Get your narrated PowerPoint!

---

## 📞 Support Resources

- **Documentation** - See `README.md` and `INTEGRATION_GUIDE.md`
- **Examples** - Check `setup.py` for working code examples
- **Issues** - Review execution logs for detailed error info
- **Performance** - See "Performance Tips" section above

---

## 🎬 You're Ready!

Your PDF-to-narrated-PowerPoint system is now ready to use.

**Quick checklist before starting:**

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All agent directories present in `../Agentic Systems/`
- [ ] 5+ GB free disk space
- [ ] Browser ready to access http://localhost:8501

**Now launch the app:**

```bash
streamlit run app.py
```

Enjoy creating narrated presentations! 🎉

---

**Version:** 2.0  
**Last Updated:** 2024  
**Status:** Ready for Production ✅
