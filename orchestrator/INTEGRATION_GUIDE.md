# LangGraph Orchestrator - Integration Guide

## Overview

The LangGraph Orchestrator is a production-ready refactoring of the Master Orchestrator Agent that replaces sequential execution with a graph-based orchestration architecture. This guide covers setup, integration, and usage.

## Architecture

### Key Components

```
orchestrator/
├── graph.py                  # LangGraph workflow & orchestration engine
├── app.py                    # Streamlit web interface
├── state.py                  # Shared PipelineState definition
├── wrapper_agents.py         # Agent interface wrappers
├── requirements.txt          # Python dependencies
├── __init__.py              # Package init
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

### Data Flow

```
PDF File
   ↓
[1] Parser Agent → parsed_blocks
   ↓
[2] Chunker Agent → semantic_chunks
   ↓
[3] Vector Agent → vector_store + embeddings
   ↓
[4] Planner Agent → slide_plan
   ↓
[5] Generator Agent → presentation.json
   ↓
[6] Script Agent → scripts.json
   ↓
[7] TTS Agent → audio_files
   ↓
[8] PPTX Builder → lecture.pptx
   ↓
Finalization → output/
```

### State Management

All pipeline data flows through a `PipelineState` object that contains:

```python
State {
  # Input
  pdf_path: str
  output_dir: str
  
  # Intermediate outputs from each stage
  parsed_blocks: List[Dict]
  semantic_chunks: List[Dict]
  vector_store: Any
  slide_plan: List[Dict]
  presentation_json: Dict
  scripts: Dict
  audio_files: List[str]
  pptx_path: str
  
  # Tracking
  status: str  # "initialized", "running", "completed", "failed"
  logs: List[Dict]
  error_message: str
  
  # Stage success flags
  parser_success: bool
  chunker_success: bool
  ...
}
```

## Installation

### 1. Install Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
```

### 2. Verify Existing Agents

Ensure all agent directories are properly set up in `Agentic Systems/`:

```
Agentic Systems/
├── 1- PDF Parser and Layout Analyzer Agent/
├── 2- Semantic Chunker Agent/
├── 3- Vector DB + Embeddings Layer/
├── 4- Slide Planner Agent/
├── 5- Slide Generator Agent/
├── 6- PPTX Builder Agent/
├── 7- Script Agent for each slide in PPTX/
└── 8- TTS Generative Audio Agent/
```

## Usage

### Option 1: Streamlit Web UI (Recommended)

```bash
cd orchestrator
streamlit run app.py
```

Then open browser to `http://localhost:8501`

**UI Features:**
- PDF upload widget
- Real-time progress bar with stage markers
- Execution logs and debugging
- Download PPTX and ZIP (PPT + audio)
- Execution summary with timing

### Option 2: Direct Python API

```python
from orchestrator.graph import WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator(output_base_dir="output")

# Execute pipeline
state = orchestrator.execute(
    pdf_path="path/to/document.pdf",
    run_id="my_run_20240101_120000"  # Optional, auto-generated if None
)

# Check results
print(f"Status: {state.status}")
print(f"PPTX: {state.pptx_path}")
print(f"Audio Dir: {state.audio_output_dir}")

# Get logs
orchestrator.get_logs(state)

# Get summary
summary = orchestrator.get_summary(state)
print(summary)
```

### Option 3: Using PipelineState Directly

```python
from orchestrator.state import PipelineState
from orchestrator.graph import create_workflow_graph

# Create state
state = PipelineState(
    pdf_path="/path/to/document.pdf",
    output_dir="./output"
)

# Get compiled graph
graph = create_workflow_graph()

# Execute
final_state = graph.invoke(state)
```

## LangGraph Architecture

### Graph Structure

The workflow is defined as a StateGraph with conditional routing:

```
START
  ↓
Parser (check_parser) → Error Handler
  ↓
Chunker (check_chunker) → Error Handler
  ↓
Vector (check_vector) → Error Handler
  ↓
Planner (check_planner) → Error Handler
  ↓
Generator (check_generator) → Error Handler
  ↓
Script (no routing, non-critical)
  ↓
TTS (no routing, non-critical)
  ↓
PPTX (check_pptx) → Error Handler
  ↓
Finalize
  ↓
END
```

### Node Types

1. **Agent Nodes** - Execute actual processing
   - `parser`, `chunker`, `vector`, `planner`, `generator`, `script`, `tts`, `pptx`

2. **Conditional Nodes** - Route based on success/failure
   - Routing logic in functions like `check_parser()`, `check_chunker()`, etc.

3. **Error Handlers** - Handle stage failures gracefully
   - `parser_error`, `chunker_error`, `vector_error`, etc.

4. **Finalization** - Post-processing and output assembly
   - `finalize` node copies outputs and generates summaries

### Conditional Routing

Each critical stage has conditional routing:

```python
def check_parser(state: PipelineState) -> str:
    return "chunker" if state.parser_success else "parser_error"
```

This allows the graph to handle failures without stopping execution.

## Extending the System

### Adding a New Agent Node

1. Create wrapper function in `wrapper_agents.py`:

```python
def run_new_agent(state: PipelineState) -> PipelineState:
    try:
        state.current_stage = "New Agent"
        state.add_log("INFO", "NewAgent", "Starting...")
        
        # Execute agent
        new_agent = NewAgent()
        result = new_agent.process()
        
        state.new_agent_output = result
        state.new_agent_success = True
        state.add_log("SUCCESS", "NewAgent", "Completed")
        return state
    except Exception as e:
        state.new_agent_success = False
        state.error_message = str(e)
        state.add_log("ERROR", "NewAgent", error_msg)
        raise
```

2. Update `PipelineState` in `state.py`:

```python
@dataclass
class PipelineState:
    new_agent_output: Any = None
    new_agent_success: bool = False
    # ...
```

3. Update `graph.py` to add node and routing:

```python
graph.add_node("new_agent", run_new_agent)
graph.add_conditional_edges(
    "previous_stage",
    lambda s: "new_agent" if s.previous_success else "error",
    {"new_agent": "new_agent", "error": "error_handler"}
)
```

### Custom Callbacks

Add callbacks to track progress:

```python
def on_progress(stage: str, status: str):
    print(f"{stage}: {status}")

def on_complete(state: PipelineState):
    print(f"Done! PPTX: {state.pptx_path}")

state = orchestrator.execute(
    pdf_path="doc.pdf",
    callbacks={
        "on_complete": on_complete,
    }
)
```

## Performance Optimizations

### 1. Async Execution

The graph can be executed with async support (future enhancement):

```python
import asyncio
state = await graph.ainvoke(initial_state)
```

### 2. Caching Outputs

Intermediate outputs are cached per-stage, enabling:
- Re-running from specific stages
- Skipping completed stages

### 3. Parallel Vector Processing

Vector embeddings can be batched for faster processing:

```python
# In wrapper_agents.py, modify vector agent call
vector_agent.process(
    batch_size=32,  # Process 32 chunks at a time
    num_workers=4,  # Use 4 CPU cores
)
```

## Troubleshooting

### Issue: Agent not found

**Solution:** Verify agent directory paths in `wrapper_agents.py`

```python
def _get_agent_path(agent_name: str) -> Path:
    # Check agent_map has correct directory names
    agent_map = {
        "parser": "1- PDF Parser and Layout Analyzer Agent",
        # ... verify these match actual directories
    }
```

### Issue: State not updating

**Solution:** Ensure wrapper functions return modified state:

```python
def run_agent(state):
    # ... process ...
    state.field_name = result  # Update state
    return state  # Return modified state
```

### Issue: Memory issues with large PDFs

**Solution:** Process in batches or use vector store pagination:

```python
# Reduce batch sizes in vector agent
vector_agent.process(batch_size=16)
```

### Issue: Streamlit app not connecting to agents

**Solution:** Verify Python paths are correct:

```python
# In wrapper_agents.py
os.chdir(agent_path)
sys.path.insert(0, str(agent_path))
```

## Monitoring & Logging

### Real-time Logs

View execution logs in Streamlit UI:
- Expandable "Execution Logs" section
- Color-coded by level (INFO, SUCCESS, ERROR, WARN)
- Stage-by-stage progress indicator

### Log Files

Logs are saved to `output/{run_id}/metadata/pipeline_state_{run_id}.json`:

```json
{
  "run_id": "20240101_120000",
  "status": "completed",
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00.123456",
      "level": "INFO",
      "stage": "Parser",
      "message": "Starting PDF parsing..."
    },
    ...
  ],
  "stage_results": {
    "parser": true,
    "chunker": true,
    ...
  }
}
```

## Comparative Performance

### Before (Sequential Master Agent)
- Total time: ~8 minutes for typical PDF
- Linear dependency chain: no parallelization
- Error handling: stop on first failure

### After (LangGraph Orchestrator)
- Total time: ~8 minutes (same due to data dependencies)
- Structured state flow: easier to debug and extend
- Error handling: granular, non-critical stages continue
- Monitoring: real-time progress with detailed logs
- Extensibility: plug new stages without rewriting orchestrator

## API Reference

### WorkflowOrchestrator

```python
class WorkflowOrchestrator:
    def __init__(self, output_base_dir: str = "output")
    def execute(self, pdf_path: str, run_id: str = None, 
                callbacks: Dict = None) -> PipelineState
    def get_logs(self, state: PipelineState) -> list
    def get_summary(self, state: PipelineState) -> Dict
```

### PipelineState

```python
@dataclass
class PipelineState:
    pdf_path: str
    output_dir: str
    status: str  # "initialized", "running", "completed", "failed"
    
    # ... many more fields ...
    
    def add_log(self, level: str, stage: str, message: str)
    def to_dict() -> Dict
    def save_metadata()
```

## Migration from Old Master Agent

### Old Code
```python
orchestrator = MasterOrchestratorAgent()
success = orchestrator.run()
```

### New Code
```python
orchestrator = WorkflowOrchestrator()
state = orchestrator.execute("document.pdf")
if state.status == "completed":
    print(f"PPTX: {state.pptx_path}")
```

## Support & Debugging

For issues or errors:

1. Check logs in Streamlit UI or `output/{run_id}/metadata/`
2. Review stage_results in execution summary
3. Check individual agent output directories:
   - `Agentic Systems/1- PDF Parser.../parsed_blocks.json`
   - `Agentic Systems/2- Semantic Chunker.../semantic_chunks.json`
   - etc.

## Future Enhancements

Planned improvements for v2.1:

- [ ] Async execution of parallelizable stages
- [ ] Web-based progress streaming with WebSocket
- [ ] Agent result caching and incremental re-runs
- [ ] Custom agent pipeline configuration UI
- [ ] Real-time metrics dashboard
- [ ] Distributed execution support
- [ ] GPU acceleration for embeddings
- [ ] Advanced audio options (Google Cloud TTS, Azure, ElevenLabs)

## License

See parent project LICENSE file.

## Authors

- Mahmoud Alyosify
- Mirna Mohsen
- Orchestrator Refactoring: LangGraph v2.0
