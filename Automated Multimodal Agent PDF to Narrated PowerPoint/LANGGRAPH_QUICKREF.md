# LangGraph Orchestrator - Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

---

## Quick Start

### Command Line (Fastest)
```bash
python langgraph_orchestrator.py input.pdf output.pptx --debug
```

### Python Code
```python
from langgraph_orchestrator import run_orchestration

result = run_orchestration("input.pdf", "output.pptx")
print(result['final_output'])  # Path to generated PowerPoint
```

---

## Common Commands

| Task | Command |
|------|---------|
| Basic conversion | `python langgraph_orchestrator.py input.pdf output.pptx` |
| With page range | `python langgraph_orchestrator.py in.pdf out.pptx --start-page 5 --end-page 20` |
| Academic domain | `python langgraph_orchestrator.py in.pdf out.pptx --domain academic` |
| Business domain | `python langgraph_orchestrator.py in.pdf out.pptx --domain business` |
| With debug | `python langgraph_orchestrator.py in.pdf out.pptx --debug` |
| Spanish language | `python langgraph_orchestrator.py in.pdf out.pptx --language es` |

---

## State Flow

```
User Input
    ↓
[1] Document Understanding Agent
    ├─ Success? → [2] Brain Agent
    └─ Failed? → Return Error
                 ↓
            [3] JSON to PPT Agent
                ├─ Success? → Return .pptx file ✓
                └─ Failed? → Return Error
```

---

## Return Value Structure

```python
result = {
    "status": "completed",           # Workflow status
    "pdf_path": "input.pdf",         # Input file
    "output_pptx": "output.pptx",    # Output file
    
    # Step results
    "document_extracted": True,       # Doc extraction success
    "slides_designed": True,          # Brain agent success
    "ppt_created": True,              # PPT rendering success
    
    # Final output
    "final_output": "output.pptx",   # Generated file path
    
    # Errors (if any)
    "errors": [],                     # List of error messages
}
```

---

## Check Results

```python
if result['status'] == 'completed':
    print(f"✓ Done! File: {result['final_output']}")
else:
    print(f"✗ Failed: {result['status']}")
    for err in result['errors']:
        print(f"  - {err}")
```

---

## Stream Progress (Real-time)

```python
from langgraph_orchestrator import create_orchestration_graph

graph = create_orchestration_graph()

for step, state in graph.stream({
    "pdf_path": "input.pdf",
    "output_pptx": "output.pptx",
    # ... other required fields
}):
    print(f"Step: {step}")
    print(f"Status: {state['status']}")
```

---

## Graph Visualization

```bash
python langgraph_orchestrator.py input.pdf output.pptx --debug
```

Shows:
- Node connections
- Data flow
- Conditional routing paths

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError` | PDF doesn't exist | Check file path |
| `MISTRAL_API_KEY not set` | Missing API key | Set env var or .env file |
| `Document extraction failed` | Bad PDF format | Verify PDF integrity |
| `PPT rendering failed` | No write permissions | Check output directory |

---

## Environment Variables

Create `.env` file:
```
MISTRAL_API_KEY=your-api-key-here
```

Or set in terminal:
```bash
# Windows PowerShell
$env:MISTRAL_API_KEY = "your-api-key"

# Linux/Mac
export MISTRAL_API_KEY="your-api-key"
```

---

## Performance

- **Document Extraction:** ~2-5 seconds per page
- **Brain Agent (Design):** ~5-10 seconds
- **PPT Rendering:** ~1-2 seconds
- **Total:** ~30-60 seconds for 10-page document

---

## Integration Example

### Streamlit App
```python
import streamlit as st
from langgraph_orchestrator import run_orchestration

uploaded = st.file_uploader("Upload PDF", type="pdf")
if uploaded:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded.getvalue())
    
    if st.button("Convert"):
        result = run_orchestration("temp.pdf", "out.pptx")
        
        if result['status'] == 'completed':
            st.success("✓ Done!")
            with open(result['final_output'], 'rb') as f:
                st.download_button("Download", f, "output.pptx")
```

### FastAPI
```python
from fastapi import FastAPI, File
from langgraph_orchestrator import run_orchestration

app = FastAPI()

@app.post("/convert")
async def convert(pdf: UploadFile):
    await pdf.write("temp.pdf")
    result = run_orchestration("temp.pdf", "output.pptx")
    return {"status": result["status"], "output": result["final_output"]}
```

---

## Debugging Tips

1. **Enable debug mode:**
   ```bash
   python langgraph_orchestrator.py in.pdf out.pptx --debug
   ```

2. **Check logs:** Look for `✓` (success) and `✗` (error) markers

3. **Stream execution:**
   ```python
   for step, state in graph.stream(initial_state):
       print(f"{step}: {state['status']}")
   ```

4. **Inspect state:** Print state after each node
   ```python
   print(result['extracted_content'])  # Document data
   print(result['slides_json'])        # Generated slides
   ```

---

## Architecture Layers

```
┌─────────────────────────────────────────┐
│  Application Layer (Your Code)          │
│  - Streamlit, FastAPI, CLI              │
├─────────────────────────────────────────┤
│  Orchestration Layer (LangGraph)        │
│  - State management                     │
│  - Conditional routing                  │
│  - Error handling                       │
├─────────────────────────────────────────┤
│  Agent Layer                            │
│  - Document Understanding               │
│  - Brain (Mistral AI)                   │
│  - JSON to PPT                          │
├─────────────────────────────────────────┤
│  Model Layer                            │
│  - PyMuPDF (PDF processing)             │
│  - Mistral API (reasoning)              │
│  - python-pptx (rendering)              │
└─────────────────────────────────────────┘
```

---

**Need Help?** See [LANGGRAPH_GUIDE.md](LANGGRAPH_GUIDE.md) for detailed documentation.
