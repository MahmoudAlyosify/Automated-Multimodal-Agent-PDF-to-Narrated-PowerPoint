# LangGraph Architecture Documentation

## System Overview

The LangGraph orchestrator replaces the subprocess-based orchestrator with a graph-based state machine that provides better control flow, error handling, and type safety.

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         USER INITIATES CONVERSION                               │
│  (CLI, Streamlit, FastAPI, or direct Python API)                               │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │   INITIALIZE STATE             │
                    │   • pdf_path                   │
                    │   • output_pptx                │
                    │   • start_page, end_page       │
                    │   • domain, language           │
                    │   • errors = []                │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │          [NODE 1: DOCUMENT UNDERSTANDING AGENT]        │
        │                                                         │
        │  Function: document_understanding_node()              │
        │                                                         │
        │  Processing:                                           │
        │  ├─ Load PDF with PyMuPDF                              │
        │  ├─ Extract pages and content                          │
        │  ├─ Analyze layout (spatial relationships)             │
        │  ├─ Classify blocks (heading, body, list, etc)        │
        │  ├─ Apply semantic labeling                            │
        │  └─ Build document tree structure                      │
        │                                                         │
        │  Output State Variables:                              │
        │  ├─ document_extracted: bool ✓                        │
        │  ├─ extracted_content: Dict[str, Any]                 │
        │  └─ document_error: Optional[str]                     │
        │                                                         │
        │  Success Indicators:                                  │
        │  ├─ ✓ "Sections extracted: N"                        │
        │  └─ ✓ "Document extraction completed successfully"    │
        └────────────────┬──────────────────────────────────────┘
                         │
                    ┌────▼─────────────┐
                    │ CONDITIONAL EDGE │
                    │ should_run_brain_ │
                    │ agent()           │
                    └────┬────────────┬─┘
                         │            │
                  Success │            │ Failed
                         │            │
                    YES  │            │  NO
                         │            │
            ┌────────────▼┐   ┌──────▼────────────┐
            │  Continue   │   │   Jump to END     │
            │  to Brain   │   │ (Skip remaining)  │
            │   Agent     │   │  status="skipped" │
            └────────────┬┘   └───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────────────────┐
        │             [NODE 2: BRAIN AGENT]                      │
        │          (Mistral AI 7B Model)                         │
        │                                                         │
        │  Function: brain_agent_node()                         │
        │                                                         │
        │  Processing:                                           │
        │  ├─ Analyze extracted document structure               │
        │  ├─ Determine optimal slide count and layout           │
        │  ├─ Create slide hierarchy                             │
        │  ├─ Design visual layout for each slide                │
        │  ├─ Select color scheme                                │
        │  ├─ Apply typography rules                             │
        │  ├─ Generate speaker notes                             │
        │  └─ Create JSON slide specification                    │
        │                                                         │
        │  Output State Variables:                              │
        │  ├─ slides_designed: bool ✓                           │
        │  ├─ slides_json: Dict[str, Any]                       │
        │  └─ brain_error: Optional[str]                        │
        │                                                         │
        │  Success Indicators:                                  │
        │  ├─ ✓ "Slides generated: N"                          │
        │  └─ ✓ "Presentation design completed successfully"    │
        └────────────────┬──────────────────────────────────────┘
                         │
                    ┌────▼─────────────┐
                    │ CONDITIONAL EDGE │
                    │ should_run_ppt_   │
                    │ agent()           │
                    └────┬────────────┬─┘
                         │            │
                  Success │            │ Failed
                         │            │
                    YES  │            │  NO
                         │            │
            ┌────────────▼┐   ┌──────▼────────────┐
            │  Continue   │   │   Jump to END     │
            │  to PPT     │   │ (Skip rendering)  │
            │  Agent      │   │  status="skipped" │
            └────────────┬┘   └───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────────────────┐
        │            [NODE 3: JSON TO PPT AGENT]                 │
        │                                                         │
        │  Function: ppt_rendering_node()                       │
        │                                                         │
        │  Processing:                                           │
        │  ├─ Parse slides JSON specification                    │
        │  ├─ Create PowerPoint presentation object              │
        │  ├─ Add slides with computed layouts                   │
        │  ├─ Apply styles and colors                            │
        │  ├─ Insert text with formatting                        │
        │  ├─ Embed images (if present)                          │
        │  ├─ Configure fonts and sizes                          │
        │  ├─ Save to .pptx file                                 │
        │  └─ Verify output file                                 │
        │                                                         │
        │  Output State Variables:                              │
        │  ├─ ppt_created: bool ✓                               │
        │  ├─ ppt_error: Optional[str]                          │
        │  └─ final_output: Optional[str]                       │
        │                                                         │
        │  Success Indicators:                                  │
        │  ├─ ✓ "Output file: /path/to/output.pptx"            │
        │  └─ ✓ "PowerPoint rendering completed successfully"   │
        └────────────────┬──────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────────────────┐
        │                   [END NODE]                           │
        │                                                         │
        │  Return Complete OrchestrationState:                  │
        │  ├─ status: "completed"                               │
        │  ├─ final_output: "/path/to/output.pptx"              │
        │  ├─ errors: []  (if successful)                       │
        │  └─ All intermediate state variables                   │
        │                                                         │
        │  OR                                                    │
        │                                                         │
        │  ├─ status: "document_extraction_failed"              │
        │  ├─ errors: ["error message"]                        │
        │  └─ early termination                                 │
        └────────────────┬──────────────────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────┐
        │  RETURN RESULTS TO CALLER            │
        │  User receives final state dict      │
        │  Can access:                         │
        │  - result['final_output']            │
        │  - result['status']                  │
        │  - result['extracted_content']       │
        │  - result['slides_json']             │
        │  - result['errors']                  │
        └──────────────────────────────────────┘
```

---

## State Transitions

### Success Path
```
initialized
    ↓
[Node 1: Document Agent] → document_extracted
    ↓
[Node 2: Brain Agent] → slides_designed
    ↓
[Node 3: PPT Agent] → completed ✓
    ↓
END with final_output = /path/to/output.pptx
```

### Partial Success Paths
```
initialized
    ↓
[Node 1 FAILS] → document_extraction_failed ✗
    ↓
[Node 2 SKIPPED] → [Node 3 SKIPPED]
    ↓
END with errors list
```

```
initialized
    ↓
[Node 1: SUCCESS] → document_extracted ✓
    ↓
[Node 2: FAILS] → brain_design_failed ✗
    ↓
[Node 3 SKIPPED]
    ↓
END with errors list
```

---

## Conditional Edge Logic

### Edge 1: After Document Agent
```python
def should_run_brain_agent(state):
    if state['document_extracted']:
        return "brain_agent"        # ✓ Proceed to brain agent
    else:
        return "end"                # ✗ Skip to end
```

### Edge 2: After Brain Agent
```python
def should_run_ppt_agent(state):
    if state['slides_designed']:
        return "ppt_agent"          # ✓ Proceed to PPT agent
    else:
        return "end"                # ✗ Skip to end
```

---

## Error Propagation

```
Error in Step 1
    ↓
state['document_error'] = "error message"
state['errors'].append("error message")
state['document_extracted'] = False
    ↓
Conditional edge evaluates: document_extracted = False
    ↓
Routes to "end" instead of "brain_agent"
    ↓
State returned to caller with error details
```

---

## Performance Characteristics

### Node Execution Times
| Node | Typical Time | Factors |
|------|------------|---------|
| Document Understanding | 2-5s/page | PDF size, complexity |
| Brain Agent | 5-10s | Slide count, detail level |
| PPT Rendering | 1-2s | Slide count, images |
| **Total** | **30-60s** | **10-page document** |

### Memory Usage
- **In-Memory State**: ~5-10 MB for typical document
- **Temporary Files**: Minimal (processed in-memory)
- **Final Output**: ~2-5 MB (PPTX file)

---

## Comparison with Old Orchestrator

### Old (subprocess-based)
```
orchestrator.py
    ↓
subprocess.run(document_agent.py) → writes JSON to disk
    ↓
subprocess.run(brain_agent.py) → reads JSON, writes new JSON to disk
    ↓
subprocess.run(ppt_agent.py) → reads JSON, writes PPTX
    ↓
Result
```

**Issues:**
- Slow inter-process communication
- State stored in temporary files
- Limited error handling
- Difficult to debug
- No type safety

### New (LangGraph-based)
```
langgraph_orchestrator.py
    ↓
StateGraph with typed OrchestrationState
    ↓
[document_agent_node] → updates state in memory
    ↓
[brain_agent_node] → reads updated state, outputs
    ↓
[ppt_rendering_node] → reads slides JSON, renders
    ↓
Result (with full state history)
```

**Advantages:**
- Fast in-process execution
- Type-safe state management
- Automatic error handling
- Conditional routing
- Easy to extend and test
- Better performance
- Visual graph debugging

---

## State at Each Stage

### Initial State
```python
{
    "pdf_path": "document.pdf",
    "output_pptx": "output.pptx",
    "start_page": None,
    "end_page": None,
    "domain": "general",
    "language": "en",
    "venv_path": None,
    
    # All flags false, all content None
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
```

### After Node 1 (Success)
```python
{
    # All inputs remain
    ...
    
    "document_extracted": True,     # ✓ Updated
    "extracted_content": {          # ✓ Populated
        "document_tree": {...},
        "metadata": {...}
    },
    "document_error": None,
    
    # Rest unchanged
    "slides_designed": False,
    ...
    "status": "document_extracted"  # ✓ Updated
}
```

### After Node 2 (Success)
```python
{
    # Previous state retained
    "document_extracted": True,
    "extracted_content": {...},
    
    # Updated by Node 2
    "slides_designed": True,        # ✓ Updated
    "slides_json": {                # ✓ Populated
        "ppt": {
            "slides": [...]
        }
    },
    "brain_error": None,
    
    "ppt_created": False,           # Not yet
    ...
    "status": "slides_designed"     # ✓ Updated
}
```

### After Node 3 (Success)
```python
{
    # All previous state retained
    "document_extracted": True,
    "extracted_content": {...},
    "slides_designed": True,
    "slides_json": {...},
    
    # Final updates
    "ppt_created": True,            # ✓ Updated
    "ppt_error": None,
    "final_output": "/path/to/output.pptx",  # ✓ Set
    
    "status": "completed",          # ✓ Final status
    "errors": []                    # ✓ No errors
}
```

---

## Graph Visualization

When running with `--debug` flag:

```
                ┌──────────────────┐
                │ document_agent   │
                └────────┬─────────┘
                         │
                    ┌────▼────────┐
                    │  Conditional│
                    │ (doc_success)│
                    └───┬──────┬──┘
                    yes │      │ no
                    ┌───▼──┐  │
                    │brain_│  │
                    │agent │  │
                    └───┬──┘  │
                        │    ┌─┴──┐
                    ┌───▼────┐   │
                    │Condition│   │
                    │(brain_ok)   │
                    └─┬──────┬──┘  │
                  yes│      │ no   │
                  ┌──▼─┐    │  ┌──┘
                  │ppt_│    │  │
                  │agent    │  │
                  └──┬──┘    │  │
                     │  ┌────┘  │
                     └──┼───────┘
                        │
                     ┌──▼──┐
                     │ END  │
                     └──────┘
```

---

## Extension Points

### Add Custom Preprocessing Node
```python
def custom_preprocessing(state):
    # Transform or validate state
    return {...state, "custom_field": value}

workflow.add_node("preprocess", custom_preprocessing)
workflow.set_entry_point("preprocess")
workflow.add_edge("preprocess", "document_agent")
```

### Add Custom Post-Processing Node
```python
def custom_postprocessing(state):
    # Process final results
    return {...state, "postprocessed": True}

workflow.add_node("postprocess", custom_postprocessing)
workflow.add_edge("ppt_agent", "postprocess")
workflow.add_edge("postprocess", END)
```

### Add Domain-Specific Branching
```python
def route_by_domain(state):
    if state['domain'] == 'academic':
        return "academic_brain"
    elif state['domain'] == 'business':
        return "business_brain"
    else:
        return "brain_agent"

workflow.add_conditional_edges("document_agent", route_by_domain, {...})
```

---

## Debugging Aids

### 1. Print State at Each Node
```python
logger.info(f"State: {state}")
```

### 2. Stream Execution
```python
for step, state in graph.stream(initial_state):
    print(f"Step: {step}")
    print(f"Status: {state['status']}")
```

### 3. Visualize Graph
```bash
python langgraph_orchestrator.py in.pdf out.pptx --debug
```

### 4. Check Individual Outputs
```python
result = run_orchestration(...)
print(json.dumps(result['extracted_content'], indent=2))
print(json.dumps(result['slides_json'], indent=2))
```

---

## Next Steps

1. **Review** [LANGGRAPH_GUIDE.md](LANGGRAPH_GUIDE.md) for detailed usage
2. **Check** [LANGGRAPH_QUICKREF.md](LANGGRAPH_QUICKREF.md) for quick commands
3. **Test** with `python langgraph_orchestrator.py sample.pdf output.pptx --debug`
4. **Extend** with custom nodes for your domain
5. **Monitor** performance and add logging as needed

---

**Architecture Version:** 1.0  
**LangGraph Version:** 0.0.32+  
**Last Updated:** 2026-02-02
