# LangGraph Orchestration Guide

## Overview

This guide explains how to use the new **LangGraph-based orchestration system** for the PDF-to-Narrated-PowerPoint agent pipeline.

LangGraph provides:
- **State-based workflows** - Type-safe state management across agents
- **Conditional routing** - Smart edge logic to skip failed steps
- **Built-in error handling** - Automatic error tracking and propagation
- **Visual debugging** - Graph visualization for workflow understanding
- **Production-ready** - Designed for reliable agent orchestration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            LangGraph Orchestration System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  INPUT: PDF File                                            │
│    │                                                         │
│    ├─► ┌─────────────────────────────────────┐             │
│    │   │ Document Understanding Agent        │             │
│    │   │ (Extract layout, structure, text)   │             │
│    │   └──────────────┬──────────────────────┘             │
│    │                  │                                      │
│    │         ┌────────▼────────┐                           │
│    │         │ Check Success?  │                           │
│    │         └────────┬────────┘                           │
│    │           Yes    │    No                              │
│    │           ┌──────┘      └─► END (FAILED)             │
│    │           │                                            │
│    │    ┌──────▼──────────────────┐                        │
│    │    │ Brain Agent              │                        │
│    │    │ (Mistral AI - Design)    │                        │
│    │    └──────┬───────────────────┘                        │
│    │           │                                            │
│    │    ┌──────▼────────┐                                   │
│    │    │ Check Success?│                                   │
│    │    └──────┬────────┘                                   │
│    │      Yes  │    No                                      │
│    │      ┌────┘      └─► END (FAILED)                     │
│    │      │                                                 │
│    │   ┌──▼─────────────────────┐                          │
│    │   │ JSON to PPT Agent       │                          │
│    │   │ (Render PowerPoint)     │                          │
│    │   └──┬────────────────────┬┘                          │
│    │      │                    │                            │
│    │      │              ┌─────▼──────┐                    │
│    │      │              │ Check Success?                  │
│    │      │              └─────┬──────┘                    │
│    │      │                Yes │                            │
│    │      │                    │                            │
│    │      │         ┌──────────▼────────┐                  │
│    │      └────────►│ END (SUCCESS) ✓   │                  │
│    │                │ Return PPTX file  │                  │
│    │                └───────────────────┘                  │
│    │                                                         │
│  OUTPUT: PowerPoint File (.pptx)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

1. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```python
   python -c "from langgraph.graph import StateGraph; print('LangGraph installed ✓')"
   ```

---

## Usage

### 1. Command Line Usage

**Basic usage:**
```bash
python langgraph_orchestrator.py input.pdf output.pptx
```

**With options:**
```bash
python langgraph_orchestrator.py input.pdf output.pptx \
    --domain academic \
    --language en \
    --start-page 1 \
    --end-page 10 \
    --debug
```

**Options:**
- `--domain`: Document domain - `academic`, `business`, `technical`, or `general` (default: `general`)
- `--language`: Language code (default: `en`)
- `--start-page`: Start page number (1-indexed, optional)
- `--end-page`: End page number (1-indexed, optional)
- `--venv`: Path to virtual environment (optional)
- `--debug`: Enable debug output with graph visualization

**Example:**
```bash
python langgraph_orchestrator.py my_document.pdf presentation.pptx \
    --domain business \
    --start-page 5 \
    --end-page 25 \
    --debug
```

### 2. Python API Usage

**Simple usage:**
```python
from langgraph_orchestrator import run_orchestration

result = run_orchestration(
    pdf_path="document.pdf",
    output_pptx="output.pptx"
)

print(f"Status: {result['status']}")
print(f"Output: {result['final_output']}")
```

**Advanced usage with options:**
```python
from langgraph_orchestrator import run_orchestration

result = run_orchestration(
    pdf_path="document.pdf",
    output_pptx="output.pptx",
    start_page=5,
    end_page=25,
    domain="academic",
    language="en",
    debug=True
)

# Check results
if result['status'] == 'completed':
    print(f"✓ Success! Output: {result['final_output']}")
else:
    print(f"✗ Failed: {result['status']}")
    for error in result['errors']:
        print(f"  - {error}")
```

### 3. Working with the Graph Directly

**Access individual nodes:**
```python
from langgraph_orchestrator import create_orchestration_graph

graph = create_orchestration_graph()

# Invoke the graph
state = {
    "pdf_path": "document.pdf",
    "output_pptx": "output.pptx",
    "start_page": None,
    "end_page": None,
    "domain": "general",
    "language": "en",
    "venv_path": None,
    "document_extracted": False,
    "extracted_content": None,
    "document_error": None,
    "slides_designed": False,
    "slides_json": None,
    "brain_error": None,
    "ppt_created": False,
    "ppt_error": None,
    "final_output": None,
    "status": "initialized",
    "errors": []
}

result = graph.invoke(state)
```

### 4. Stream Results for Real-time Updates

```python
from langgraph_orchestrator import create_orchestration_graph

graph = create_orchestration_graph()

initial_state = {...}  # as above

for step, state in graph.stream(initial_state):
    print(f"Step: {step}")
    print(f"Status: {state.get('status')}")
```

---

## State Structure

The `OrchestrationState` TypedDict contains:

### Input Parameters
```python
pdf_path: str                    # Path to input PDF
output_pptx: str                 # Path to output PowerPoint
start_page: Optional[int]        # Start page (1-indexed)
end_page: Optional[int]          # End page (1-indexed)
domain: str                      # Document domain
language: str                    # Language code
venv_path: Optional[str]         # Virtual environment path
```

### Step 1: Document Understanding
```python
document_extracted: bool                  # Success flag
extracted_content: Optional[Dict[str, Any]]  # Extracted JSON
document_error: Optional[str]             # Error message
```

### Step 2: Brain Agent
```python
slides_designed: bool                     # Success flag
slides_json: Optional[Dict[str, Any]]     # Designed slides JSON
brain_error: Optional[str]                # Error message
```

### Step 3: PPT Rendering
```python
ppt_created: bool                         # Success flag
ppt_error: Optional[str]                  # Error message
final_output: Optional[str]               # Output file path
```

### Workflow Metadata
```python
status: str                      # Current workflow status
errors: list[str]                # All errors encountered
```

---

## Workflow Status Values

| Status | Meaning |
|--------|---------|
| `initialized` | Workflow started |
| `document_extracted` | Document Understanding completed ✓ |
| `document_extraction_failed` | Document Understanding failed ✗ |
| `slides_designed` | Brain Agent completed ✓ |
| `brain_design_failed` | Brain Agent failed ✗ |
| `completed` | Full workflow completed ✓ |
| `ppt_rendering_failed` | PPT rendering failed ✗ |
| `orchestration_failed` | Orchestration crashed ✗ |
| `skipped` | Step skipped due to prior failure |

---

## Error Handling

### Automatic Error Tracking

All errors are automatically tracked in `state['errors']`:

```python
result = run_orchestration(pdf_path="bad.pdf", output_pptx="out.pptx")

if result['errors']:
    print("Errors encountered:")
    for error in result['errors']:
        print(f"  {error}")
```

### Graceful Degradation

If a step fails, subsequent steps are automatically skipped:

1. If Document Understanding fails → Brain Agent is skipped → PPT rendering is skipped
2. If Brain Agent fails → PPT rendering is skipped
3. Each step checks the prior step's success before executing

### Debug Output

Enable debug output to see detailed logs:

```python
result = run_orchestration(
    pdf_path="document.pdf",
    output_pptx="output.pptx",
    debug=True
)
```

Or from CLI:
```bash
python langgraph_orchestrator.py document.pdf output.pptx --debug
```

---

## Integrating with Existing Code

### Replace Old Orchestrator

**Old (subprocess-based):**
```python
from orchestrator import PDFToPresentation

presenter = PDFToPresentation()
result = presenter.run(pdf_path="document.pdf", output_pptx="output.pptx")
```

**New (LangGraph-based):**
```python
from langgraph_orchestrator import run_orchestration

result = run_orchestration(pdf_path="document.pdf", output_pptx="output.pptx")
```

### In Streamlit App

```python
import streamlit as st
from langgraph_orchestrator import run_orchestration

st.title("PDF to PowerPoint Converter")

pdf_file = st.file_uploader("Upload PDF", type="pdf")
if pdf_file:
    with open("temp.pdf", "wb") as f:
        f.write(pdf_file.getbuffer())
    
    if st.button("Convert"):
        with st.spinner("Processing..."):
            result = run_orchestration(
                pdf_path="temp.pdf",
                output_pptx="output.pptx"
            )
        
        if result['status'] == 'completed':
            st.success(f"✓ Conversion successful!")
            st.download_button(
                "Download PowerPoint",
                open(result['final_output'], 'rb'),
                file_name="output.pptx"
            )
        else:
            st.error(f"Conversion failed: {result['status']}")
```

---

## Performance Monitoring

### Log Execution Time

```python
import time
from langgraph_orchestrator import run_orchestration

start = time.time()
result = run_orchestration(pdf_path="document.pdf", output_pptx="output.pptx")
elapsed = time.time() - start

print(f"Total execution time: {elapsed:.2f}s")
```

### Stream Progress

```python
from langgraph_orchestrator import create_orchestration_graph

graph = create_orchestration_graph()

for step, state in graph.stream({...}):
    print(f"[{step}] {state.get('status')}")
```

---

## Troubleshooting

### Issue: "No module named 'langgraph'"

**Solution:** Install LangGraph
```bash
pip install langgraph langchain langchain-core
```

### Issue: "Document extraction failed"

**Solutions:**
1. Verify PDF file exists: `Path(pdf_path).exists()`
2. Check PDF is readable: `Try opening with PyMuPDF`
3. Enable debug mode: `run_orchestration(..., debug=True)`

### Issue: "Mistral API key not set"

**Solution:** Set environment variable
```bash
export MISTRAL_API_KEY="your-key-here"
```

Or in `.env` file:
```
MISTRAL_API_KEY=your-key-here
```

### Issue: "PPT rendering failed"

**Solution:**
1. Check output path is writable: `Path(output_pptx).parent.exists()`
2. Verify disk space available
3. Check file permissions

---

## Advanced Features

### Custom Node Functions

You can extend the orchestrator with custom nodes:

```python
from langgraph_orchestrator import create_orchestration_graph
from langgraph.graph import StateGraph

def custom_preprocessing_node(state):
    # Your custom preprocessing logic
    return {**state, "custom_field": "value"}

# Add custom node
workflow = StateGraph(OrchestrationState)
workflow.add_node("custom", custom_preprocessing_node)
workflow.set_entry_point("custom")
workflow.add_edge("custom", "document_agent")
# ... rest of configuration
```

### Conditional Routing

Modify routing logic:

```python
def should_use_special_mode(state):
    if state['domain'] == 'academic':
        return "academic_agent"
    else:
        return "document_agent"

workflow.add_conditional_edges("entry", should_use_special_mode, {...})
```

---

## Comparison: Old vs New Orchestrator

| Feature | Old (subprocess) | New (LangGraph) |
|---------|-----------------|-----------------|
| State Management | Manual dictionaries | Type-safe TypedDict |
| Error Handling | Basic try-catch | Automatic propagation |
| Node Communication | Temp files | In-memory state |
| Debugging | Logs only | Graph visualization |
| Type Safety | None | Full typing |
| Error Recovery | None | Conditional routing |
| Extensibility | Hard | Easy (add nodes) |
| Testing | Difficult | Simple |
| Performance | Slow (IPC) | Fast (in-process) |

---

## Next Steps

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Test with sample:** `python langgraph_orchestrator.py sample.pdf output.pptx --debug`
3. **Integrate with your app:** Use `run_orchestration()` in your code
4. **Monitor performance:** Use streaming for real-time updates
5. **Customize nodes:** Add domain-specific preprocessing

---

## Support

For issues or questions:
1. Check [LangGraph docs](https://github.com/langchain-ai/langgraph)
2. Review error messages in debug mode
3. Check log files for detailed information

---

**Created:** 2026-02-02  
**LangGraph Version:** 0.0.32+  
**Status:** Production Ready ✓
