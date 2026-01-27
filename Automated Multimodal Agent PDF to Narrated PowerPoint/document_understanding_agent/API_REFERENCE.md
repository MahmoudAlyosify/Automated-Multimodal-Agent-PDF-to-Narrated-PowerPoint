# API Reference

## Document Understanding Agent

### Class: `DocumentUnderstandingAgent`

Main orchestrator for document understanding.

#### Constructor

```python
DocumentUnderstandingAgent(
    use_ml: bool = False,
    extract_images: bool = True,
    log_level: str = "INFO"
)
```

**Parameters**:
- `use_ml` (bool): Use ML models for ambiguous classification (default: False)
- `extract_images` (bool): Extract image references (default: True)
- `log_level` (str): Logging level - "DEBUG", "INFO", "WARNING", "ERROR" (default: "INFO")

#### Methods

##### `process(dua_input: DUAInput) -> DUAOutput`

Process a PDF document.

**Parameters**:
- `dua_input` (DUAInput): Input with pdf_path, language, domain

**Returns**:
- `DUAOutput`: Structured document with tree and metadata

**Raises**:
- `FileNotFoundError`: PDF doesn't exist
- `RuntimeError`: Processing failed

**Example**:
```python
from dua import DocumentUnderstandingAgent
from dua.types import DUAInput

agent = DocumentUnderstandingAgent()
output = agent.process(DUAInput(
    pdf_path="lecture.pdf",
    language="en",
    domain="academic"
))
```

---

##### `process_dict(input_dict: Dict[str, Any]) -> Dict[str, Any]`

Process PDF from dictionary (API compatible).

**Parameters**:
- `input_dict` (Dict): Dictionary with keys: pdf_path, language, domain

**Returns**:
- `Dict`: JSON-serializable output dictionary

**Example**:
```python
output_dict = agent.process_dict({
    "pdf_path": "document.pdf",
    "language": "en",
    "domain": "general"
})

import json
json.dump(output_dict, open("output.json", "w"))
```

---

##### `get_status() -> Dict[str, Any]`

Get agent status.

**Returns**:
- `Dict`: Status information

**Example**:
```python
status = agent.get_status()
print(status["version"])  # "1.0.0"
print(status["modules"])  # List of modules
```

---

## Data Types

### Input Types

#### `DUAInput`

Input contract for the agent.

```python
@dataclass
class DUAInput:
    pdf_path: str                  # Path to PDF file
    language: str = "en"           # Document language
    domain: str = "general"        # Domain (academic, business, technical, legal)
    extract_images: bool = True    # Whether to extract images
    analyze_tables: bool = True    # Whether to analyze tables
```

**Example**:
```python
from dua.types import DUAInput

input_data = DUAInput(
    pdf_path="research.pdf",
    language="en",
    domain="academic",
    extract_images=True,
    analyze_tables=True
)
```

---

### Output Types

#### `DUAOutput`

Complete output from the agent.

```python
@dataclass
class DUAOutput:
    document_tree: DocumentTree      # Hierarchical document structure
    metadata: DocumentMetadata       # Document metadata and confidence
    raw_text: str                    # Full extracted text
    error: Optional[str] = None      # Error message if failed
    warnings: List[str] = []         # Processing warnings
    
    def to_dict() -> Dict[str, Any]  # Convert to JSON-serializable dict
```

**Example**:
```python
output = agent.process(dua_input)
print(output.metadata.confidence)    # 0.94
print(output.metadata.num_pages)     # 12
print(len(output.document_tree.sections))  # 5
```

---

#### `DocumentTree`

Hierarchical document structure.

```python
@dataclass
class DocumentTree:
    sections: List[DocumentSection]  # Top-level sections
    metadata: DocumentMetadata       # Document metadata
```

---

#### `DocumentSection`

Section of a document.

```python
@dataclass
class DocumentSection:
    title: str                              # Section title
    level: int                              # Nesting level (1=top)
    blocks: List[DocumentBlock]             # Content blocks
    subsections: List['DocumentSection'] = [] # Nested subsections
```

**Example**:
```python
section = output.document_tree.sections[0]
print(section.title)          # "Introduction"
print(section.level)          # 1
print(len(section.blocks))    # 5
print(len(section.subsections))  # 2
```

---

#### `DocumentBlock`

Individual content block.

```python
@dataclass
class DocumentBlock:
    type: BlockType                     # PARAGRAPH, HEADING, IMAGE, etc.
    semantic_label: SemanticLabel       # EXPLANATION, DEFINITION, etc.
    importance: float                   # 0.0-1.0 importance score
    text: Optional[str] = None          # Block text
    path: Optional[str] = None          # Image path
    caption: Optional[str] = None       # Image caption
    metadata: Dict[str, Any] = {}       # Additional metadata
```

**Example**:
```python
for block in section.blocks:
    print(f"{block.type.value}: {block.semantic_label.value} ({block.importance:.2f})")
    if block.text:
        print(f"  {block.text[:50]}...")
```

---

#### `DocumentMetadata`

Document metadata and statistics.

```python
@dataclass
class DocumentMetadata:
    num_pages: int                  # Total pages
    has_tables: bool                # Contains tables
    has_images: bool                # Contains images
    has_lists: bool                 # Contains lists
    languages: List[str]            # Detected languages
    confidence: float               # Overall confidence (0.0-1.0)
    processing_time: float          # Processing time in seconds
```

**Example**:
```python
meta = output.metadata
print(f"Pages: {meta.num_pages}")
print(f"Confidence: {meta.confidence:.1%}")
print(f"Processing: {meta.processing_time:.2f}s")
print(f"Has tables: {meta.has_tables}")
```

---

### Enumerations

#### `BlockType`

Type of content block.

```python
class BlockType(str, Enum):
    PARAGRAPH = "PARAGRAPH"     # Regular paragraph
    HEADING = "HEADING"         # Section heading
    TITLE = "TITLE"             # Document title
    IMAGE = "IMAGE"             # Image/figure
    TABLE = "TABLE"             # Table
    LIST = "LIST"               # Bulleted/numbered list
    CODE = "CODE"               # Code block
    QUOTE = "QUOTE"             # Quoted text
    FOOTER = "FOOTER"           # Page footer
    HEADER = "HEADER"           # Page header
    UNKNOWN = "UNKNOWN"         # Unknown type
```

---

#### `SemanticLabel`

Semantic meaning of content.

```python
class SemanticLabel(str, Enum):
    EXPLANATION = "EXPLANATION"      # General explanation
    DEFINITION = "DEFINITION"        # Formal definition
    EXAMPLE = "EXAMPLE"              # Example
    IMPORTANT = "IMPORTANT"          # Important note
    QUESTION = "QUESTION"            # Question
    ANSWER = "ANSWER"                # Answer
    SUMMARY = "SUMMARY"              # Summary
    INTRODUCTION = "INTRODUCTION"    # Introduction
    CONCLUSION = "CONCLUSION"        # Conclusion
    METADATA = "METADATA"            # Metadata (header/footer)
    UNKNOWN = "UNKNOWN"              # Unknown semantic
```

---

#### `LayoutRole`

Spatial role in document layout.

```python
class LayoutRole(str, Enum):
    MAIN_HEADING = "MAIN_HEADING"    # Main heading
    SUBHEADING = "SUBHEADING"        # Subheading
    BODY_TEXT = "BODY_TEXT"          # Body text
    SIDEBAR = "SIDEBAR"              # Sidebar
    CAPTION = "CAPTION"              # Image caption
    FOOTER = "FOOTER"                # Page footer
    HEADER = "HEADER"                # Page header
    UNKNOWN = "UNKNOWN"              # Unknown role
```

---

## Module APIs

### `PDFLoader`

Extracts raw blocks from PDF files.

```python
from dua.modules import PDFLoader

loader = PDFLoader(extract_images=True)

# Load PDF
blocks = loader.load("document.pdf")  # Returns List[RawBlock]

# Get metadata
meta = loader.get_pdf_metadata("document.pdf")
print(meta["num_pages"])
```

---

### `LayoutAnalyzer`

Analyzes spatial layout.

```python
from dua.modules import LayoutAnalyzer

analyzer = LayoutAnalyzer()
analyzed_blocks = analyzer.analyze(raw_blocks)  # List[AnalyzedBlock]
```

---

### `BlockClassifier`

Classifies blocks using rules + ML.

```python
from dua.modules import BlockClassifier

classifier = BlockClassifier(use_ml=False)
classified_blocks = classifier.classify(analyzed_blocks)  # List[ClassifiedBlock]
```

---

### `SemanticLabeler`

Refines semantic labels by context.

```python
from dua.modules import SemanticLabeler

labeler = SemanticLabeler(domain="academic", language="en")
refined_blocks = labeler.label(classified_blocks)  # List[ClassifiedBlock]
```

---

### `StructureBuilder`

Builds hierarchical document tree.

```python
from dua.modules import StructureBuilder

builder = StructureBuilder()
sections = builder.build(classified_blocks)  # List[DocumentSection]
```

---

### `ConfidenceEstimator`

Estimates confidence scores.

```python
from dua.modules import ConfidenceEstimator

estimator = ConfidenceEstimator()
metadata = estimator.estimate(
    classified_blocks,
    num_pages=12,
    has_tables=True,
    has_images=False,
    has_lists=True
)  # Returns DocumentMetadata
```

---

## Error Handling

```python
try:
    output = agent.process(dua_input)
except FileNotFoundError as e:
    print(f"PDF not found: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Complete Example

```python
import json
from dua import DocumentUnderstandingAgent
from dua.types import DUAInput

# Initialize
agent = DocumentUnderstandingAgent(
    use_ml=False,
    extract_images=True,
    log_level="INFO"
)

# Process
output = agent.process(DUAInput(
    pdf_path="lecture.pdf",
    language="en",
    domain="academic"
))

# Results
print(f"✓ Processed {output.metadata.num_pages} pages")
print(f"✓ Found {len(output.document_tree.sections)} sections")
print(f"✓ Confidence: {output.metadata.confidence:.1%}")

# Save
with open("output.json", "w") as f:
    json.dump(output.to_dict(), f, indent=2)

# Iterate sections
for section in output.document_tree.sections:
    print(f"\n## {section.title}")
    for block in section.blocks[:3]:
        print(f"  [{block.type.value}] {block.text[:60]}...")
```

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
