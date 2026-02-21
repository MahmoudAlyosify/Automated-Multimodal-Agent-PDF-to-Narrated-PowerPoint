# LangGraph Orchestrator - README

## 🎬 Overview

The **LangGraph Orchestrator** is a production-ready refactoring of the Automated Multimodal Agent system's Master Orchestrator. It replaces sequential execution with a **directed graph-based orchestration architecture** using LangGraph, paired with a **Streamlit web interface** for user-friendly access.

### Key Features

✅ **Graph-Based Orchestration** - LangGraph StateGraph for structured workflow  
✅ **Professional Web UI** - Streamlit with real-time progress and logging  
✅ **Error Handling & Recovery** - Granular error nodes and conditional routing  
✅ **State Management** - Centralized PipelineState flowing through all stages  
✅ **Non-Breaking Integration** - Wraps existing agents without modifications  
✅ **Production Ready** - Logging, monitoring, and execution summaries  
✅ **Extensible Architecture** - Easy to add new agent nodes to the pipeline  

---

## 📋 Quick Start

### 1. Installation

```bash
# Navigate to orchestrator directory
cd orchestrator

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Streamlit Web UI (Recommended)

```bash
streamlit run app.py
```

Then open your browser to: **http://localhost:8501**

### 3. Web UI Workflow

1. **Upload PDF** - Click "Choose a PDF file"
2. **Generate** - Click "✨ Generate Narrated PPT" button
3. **Monitor** - Watch real-time progress and stage completion
4. **Download** - Get PPTX and audio ZIP files

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Web UI                          │
│  (PDF Upload → Progress → Download PPTX + Audio)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ START → Parser → Chunker → Vector → Planner → Generator │   │
│  │         ↓        ↓         ↓      ↓        ↓              │   │
│  │      [Error]  [Error]   [Error] [Error] [Error]          │   │
│  │         ↓        ↓         ↓      ↓        ↓              │   │
│  │         └────────────────────────────────┘               │   │
│  │                    Script → TTS → PPTX                   │   │
│  │                             ↓                             │   │
│  │                         [Error]                           │   │
│  │                             ↓                             │   │
│  │                          Finalize → END                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Existing Agents (Wrapped)                     │
│  [Parser] [Chunker] [Vector] [Planner] [Generator]              │
│  [Scripts] [TTS] [PPTX Builder]                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
PDF Input
   ↓
1. Parser Agent
   └─→ parsed_blocks.json
       ↓
2. Chunker Agent
   └─→ semantic_chunks.json
       ↓
3. Vector Agent
   └─→ chunks.index + embeddings.npy
       ↓
4. Planner Agent
   └─→ slide_plan.json
       ↓
5. Generator Agent
   └─→ presentation.json
       ↓
6. Script Agent
   └─→ scripts.json
       ↓
7. TTS Agent
   └─→ audio_*.wav files
       ↓
8. PPTX Builder
   └─→ lecture.pptx
       ↓
Finalization
   └─→ output/
       ├── Narrated-PowerPoint.pptx
       ├── audio/
       │   ├── slide_1.wav
       │   ├── slide_2.wav
       │   └── ...
       └── metadata/
           ├── parsed_blocks.json
           ├── semantic_chunks.json
           └── ...
```

### State Management

All pipeline data flows through a centralized `PipelineState` object:

```python
state = PipelineState(
    pdf_path="document.pdf",
    output_dir="output",
    parsed_blocks=[...],
    semantic_chunks=[...],
    vector_store=faiss_index,
    slide_plan=[...],
    presentation_json={...},
    scripts={...},
    audio_files=[...],
    pptx_path="lecture.pptx",
    status="completed",
    logs=[...],
)
```

---

## 🎨 Streamlit Web Interface

### UI Components

#### 1. Upload Section
- Drag-and-drop PDF upload
- File details (name, size, type)
- "✨ Generate" button

#### 2. Execution Section
- Progress bar (0-100%)
- Real-time status updates
- Stage-by-stage indicators

#### 3. Results Section
- Execution summary metrics
- Download PPTX button
- Download ZIP (PPT + Audio) button
- Process another PDF option

#### 4. Logs Panel
- Expandable execution logs
- Color-coded by level (INFO ℹ️, SUCCESS ✅, ERROR ❌, WARN ⚠️)
- Stage results breakdown
- Timing information

### Example Workflow

```
1. User uploads PDF (2.5 MB)
2. System shows:
   - ✓ PDF Parser (135 blocks extracted)
   - ✓ Semantic Chunker (24 chunks created)
   - ✓ Vector Embeddings (24 embeddings)
   - ✓ Slide Planner (13 slides planned)
   - ✓ Slide Generator (presentation.json created)
   - ✓ Script Generator (13 scripts created)
   - ✓ TTS Audio (13 audio files, 4.2 MB)
   - ✓ PPTX Builder (final PPTX created)

3. Execution Summary:
   - Duration: 487 seconds (8.1 minutes)
   - Output: Narrated-PowerPoint.pptx (8.4 MB)
   - Audio Files: 13

4. Download buttons appear
```

---

## 🔧 Command-Line Usage

### Python API

```python
from orchestrator.graph import WorkflowOrchestrator
from orchestrator.state import PipelineState

# Create orchestrator
orch = WorkflowOrchestrator(output_base_dir="output")

# Execute pipeline
state = orch.execute(
    pdf_path="path/to/document.pdf",
    run_id="my_run_2024"
)

# Check status
print(f"Status: {state.status}")
print(f"PPTX: {state.pptx_path}")
print(f"Audio Dir: {state.audio_output_dir}")

# Get summary
summary = orch.get_summary(state)
print(json.dumps(summary, indent=2))

# View logs
for log in orch.get_logs(state):
    print(f"[{log['level']}] {log['stage']}: {log['message']}")
```

### Programmatic Execution

```python
from orchestrator.graph import create_workflow_graph
from orchestrator.state import PipelineState

# Create graph
graph = create_workflow_graph()

# Initialize state
state = PipelineState(pdf_path="document.pdf", output_dir="output")

# Run
final_state = graph.invoke(state)

# Check results
if final_state.status == "completed":
    print(f"Success! PPTX: {final_state.pptx_path}")
else:
    print(f"Failed: {final_state.error_message}")
```

---

## 📦 Project Structure

```
orchestrator/
├── app.py                      # Streamlit web application
├── graph.py                    # LangGraph workflow engine
├── state.py                    # PipelineState definition
├── wrapper_agents.py           # Agent interface wrappers
├── __init__.py                # Package initialization
├── requirements.txt           # Python dependencies
├── INTEGRATION_GUIDE.md       # Detailed integration docs
├── README.md                  # This file
└── .streamlit/
    └── config.toml            # Streamlit configuration

Parent structure:
../
├── Agentic Systems/
│   ├── 1- PDF Parser.../
│   ├── 2- Semantic Chunker.../
│   ├── 3- Vector DB.../
│   ├── 4- Slide Planner.../
│   ├── 5- Slide Generator.../
│   ├── 6- PPTX Builder.../
│   ├── 7- Script Agent.../
│   └── 8- TTS Agent.../
└── output/
    └── {run_id}/
        ├── Narrated-PowerPoint.pptx
        ├── audio/
        └── metadata/
```

---

## 🚀 Performance

### Execution Timeline

| Stage | Time | Output |
|-------|------|--------|
| 1. Parser | ~45s | 135 blocks |
| 2. Chunker | ~12s | 24 chunks |
| 3. Vector | ~60s | 24 embeddings |
| 4. Planner | ~30s | 13 slides |
| 5. Generator | ~45s | presentation.json |
| 6. Script | ~25s | 13 scripts |
| 7. TTS | ~180s | 13 audio files |
| 8. PPTX | ~15s | lecture.pptx |
| **Total** | **~412s** | **~6.8 min** |

### Optimization Tips

1. **Batch Processing** - Process images/embeddings in parallel
2. **Caching** - Skip re-processing completed stages
3. **Async Execution** - Run non-dependent stages concurrently
4. **GPU Acceleration** - Use CUDA for embeddings (if available)

---

## 🔗 Integration with Existing Agents

### Non-Breaking Changes

The orchestrator **does not modify** any existing agents. Instead, it:

1. **Imports** agent classes from their original locations
2. **Wraps** agent calls in functions compatible with LangGraph
3. **Manages state** between agents automatically
4. **Preserves** all agent outputs and behaviors

### Agent Mapping

| Stage | Agent Directory | Wrapper Function |
|-------|-----------------|------------------|
| 1 | 1- PDF Parser... | `run_parser_agent()` |
| 2 | 2- Semantic Chunker... | `run_chunker_agent()` |
| 3 | 3- Vector DB... | `run_vector_agent()` |
| 4 | 4- Slide Planner... | `run_planner_agent()` |
| 5 | 5- Slide Generator... | `run_generator_agent()` |
| 6 | 7- Script Agent... | `run_script_agent()` |
| 7 | 8- TTS Agent... | `run_tts_agent()` |
| 8 | 6- PPTX Builder... | `run_pptx_agent()` |

---

## ⚙️ Configuration

### Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"

[server]
port = 8501
maxUploadSize = 200  # MB
timeout = 300        # seconds
```

### Environment Variables (Optional)

```bash
export PIPELINE_OUTPUT_DIR="./output"
export LOG_LEVEL="INFO"
export MAX_WORKERS="4"
```

---

## 🐛 Troubleshooting

### Issue: "Agent not found"

**Solution:** Check agent directory paths match actual directories:

```bash
ls -la "Agentic Systems/"
# Should show agent directories with exact names
```

### Issue: Import errors for existing agents

**Solution:** Ensure all dependencies in `requirements.txt` are installed:

```bash
pip install -r requirements.txt
```

### Issue: Streamlit app won't start

**Solution:** Check port 8501 is available:

```bash
streamlit run app.py --server.port 8502  # Use different port
```

### Issue: Pipeline fails at TTS stage

**Solution:** TTS failures don't stop the pipeline (non-critical):

```python
# Check TTS output
state.tts_success  # False = skipped
state.audio_output_dir  # Check for audio files
```

### Issue: Large PDF causes memory issues

**Solution:** Process in smaller batches:

```python
# In wrapper_agents.py, modify vector agent
vector_agent.process(batch_size=16)  # Reduce from default
```

---

## 📊 Monitoring & Debugging

### View Logs

**In Streamlit UI:**
- Click "📋 Execution Logs" expandable section
- Shows all pipeline events with timestamps

**From logs file:**
```bash
cat output/{run_id}/metadata/pipeline_state_{run_id}.json | jq '.logs'
```

### Runtime Monitoring

```python
# Check state during execution
state = orchestrator.execute("doc.pdf")

# Get detailed summary
print(orchestrator.get_summary(state))

# Output:
# {
#   "status": "completed",
#   "stages_passed": 8,
#   "duration_seconds": 487.2,
#   "pptx": "output/20240101_120000/Narrated-PowerPoint.pptx"
# }
```

---

## 🔐 Security & Safety

### Input Validation

- ✅ PDF file type validation
- ✅ File size limits (configurable in Streamlit config)
- ✅ Path traversal prevention
- ✅ Safe temporary file handling

### Error Handling

- ✅ Graceful degradation (non-critical stages skip)
- ✅ Detailed error logging
- ✅ State preservation for debugging

### Resource Management

- ✅ Automatic temporary file cleanup
- ✅ Output directory organization
- ✅ Memory-efficient streaming

---

## 📈 Scalability

### Current Limitations

- Single-machine execution
- Sequential stage processing (data-dependent)
- In-memory state management

### Future Enhancements (v2.1+)

- [ ] Distributed execution (Ray, Celery)
- [ ] Async stage processing
- [ ] Database-backed state management
- [ ] Web-based async progress streaming
- [ ] Load balancing for high-volume use

---

## 📚 API Reference

### WorkflowOrchestrator

```python
class WorkflowOrchestrator:
    def __init__(self, output_base_dir: str = "output")
    def execute(
        self,
        pdf_path: str,
        run_id: str = None,
        callbacks: Dict = None
    ) -> PipelineState
    def get_logs(self, state: PipelineState) -> List[Dict]
    def get_summary(self, state: PipelineState) -> Dict[str, Any]
```

### PipelineState

```python
@dataclass
class PipelineState:
    pdf_path: str
    output_dir: str
    status: str
    
    # Stage-specific success flags
    parser_success: bool
    chunker_success: bool
    vector_success: bool
    planner_success: bool
    generator_success: bool
    script_success: bool
    tts_success: bool
    pptx_success: bool
    
    # Methods
    def add_log(self, level: str, stage: str, message: str)
    def to_dict() -> Dict[str, Any]
    def save_metadata()
```

---

## 🤝 Contributing

To extend the orchestrator:

1. **Add agent** in `wrapper_agents.py`
2. **Update state** in `state.py`
3. **Update graph** in `graph.py` (add node + routing)
4. **Test** with `streamlit run app.py`

See `INTEGRATION_GUIDE.md` for detailed examples.

---

## 📝 License

See parent project [LICENSE](../LICENSE) file.

---

## 👥 Authors & Attribution

- **Original System:** Mahmoud Alyosify, Mirna Mohsen
- **LangGraph Refactoring:** Automated Multimodal Agent Team
- **Version:** 2.0 (LangGraph-based)

---

## 🆘 Support

For issues or questions:

1. Check logs in Streamlit UI
2. Review execution summary metrics
3. See `INTEGRATION_GUIDE.md` for troubleshooting
4. Check individual agent outputs in `Agentic Systems/`

---

## 🎯 Next Steps

1. **Install:** Run `pip install -r requirements.txt`
2. **Start UI:** Run `streamlit run app.py`
3. **Upload PDF:** Use Streamlit file uploader
4. **Monitor:** Watch real-time progress
5. **Download:** Get PPTX and audio files

**Happy narrated presentations! 🎬**
