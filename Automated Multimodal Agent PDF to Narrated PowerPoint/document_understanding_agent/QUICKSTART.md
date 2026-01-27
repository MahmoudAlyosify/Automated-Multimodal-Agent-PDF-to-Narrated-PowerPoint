# 🚀 Quick Start Guide

## 5 Minutes to Your First Document Understanding

### Step 1: Install (1 min)

```bash
cd document_understanding_agent
pip install -r requirements.txt
```

### Step 2: Prepare a PDF

Have a PDF file ready. Place it in the project directory or note its full path.

### Step 3: Create Python Script (2 min)

Create a file `process_my_pdf.py`:

```python
from dua import DocumentUnderstandingAgent
from dua.types import DUAInput

# 1. Initialize agent
agent = DocumentUnderstandingAgent()

# 2. Define input
input_data = DUAInput(
    pdf_path="your_document.pdf",    # ← Change this!
    language="en",
    domain="academic"                 # or: business, technical, legal, general
)

# 3. Process
output = agent.process(input_data)

# 4. Explore results
print(f"✓ Processed {output.metadata.num_pages} pages")
print(f"✓ Found {len(output.document_tree.sections)} sections")
print(f"✓ Confidence: {output.metadata.confidence:.1%}")
print()

# 5. Display structure
for section in output.document_tree.sections[:3]:  # First 3 sections
    print(f"\n## {section.title}")
    for block in section.blocks[:2]:  # First 2 blocks per section
        print(f"   [{block.type.value}] {block.text[:60]}...")

# 6. Save to JSON (optional)
import json
with open("output.json", "w") as f:
    json.dump(output.to_dict(), f, indent=2)
    print("\n✓ Full output saved to output.json")
```

### Step 4: Run (1 min)

```bash
python process_my_pdf.py
```

### Step 5: View Results (1 min)

```bash
# See formatted JSON output
cat output.json
```

---

## 📊 What You'll Get

```json
{
  "document_tree": {
    "sections": [
      {
        "title": "Introduction",
        "level": 1,
        "blocks": [
          {
            "type": "PARAGRAPH",
            "semantic_label": "EXPLANATION",
            "importance": 0.75,
            "text": "This document explains..."
          }
        ]
      }
    ]
  },
  "metadata": {
    "num_pages": 12,
    "has_tables": true,
    "has_images": false,
    "confidence": 0.94,
    "processing_time": 1.23
  }
}
```

---

## 🎯 Common Use Cases

### Academic Paper

```python
output = agent.process(DUAInput(
    pdf_path="research_paper.pdf",
    domain="academic"
))
# DUA identifies: definitions, questions, examples, conclusions
```

### Business Report

```python
output = agent.process(DUAInput(
    pdf_path="quarterly_report.pdf",
    domain="business"
))
# DUA identifies: key metrics, summaries, important notes
```

### Technical Documentation

```python
output = agent.process(DUAInput(
    pdf_path="api_docs.pdf",
    domain="technical"
))
# DUA identifies: code blocks, definitions, examples
```

---

## 🔧 Configuration

### Change Domain

```python
# Academic, business, technical, or legal
input_data = DUAInput(
    pdf_path="doc.pdf",
    domain="business"  # ← Change this
)
```

### Change Language

```python
input_data = DUAInput(
    pdf_path="doc.pdf",
    language="ar"  # Arabic (experimental)
)
```

### Adjust Agent Settings

```python
agent = DocumentUnderstandingAgent(
    use_ml=False,              # Enable ML (experimental)
    extract_images=True,       # Extract image references
    log_level="DEBUG"          # More verbose logging
)
```

---

## 📈 Output Breakdown

### Metadata
```python
meta = output.metadata

print(meta.num_pages)        # Total pages: 12
print(meta.has_tables)       # Contains tables: True
print(meta.has_images)       # Contains images: False
print(meta.confidence)       # 0.94 (94% confidence)
print(meta.processing_time)  # 1.23 seconds
```

### Document Structure
```python
tree = output.document_tree

for section in tree.sections:
    print(f"Title: {section.title}")
    print(f"Level: {section.level}")
    print(f"Blocks: {len(section.blocks)}")
    print(f"Subsections: {len(section.subsections)}")
```

### Block Details
```python
for block in section.blocks:
    print(f"Type: {block.type.value}")           # PARAGRAPH, HEADING, etc.
    print(f"Label: {block.semantic_label.value}") # EXPLANATION, DEFINITION, etc.
    print(f"Importance: {block.importance}")      # 0.0-1.0 score
    print(f"Text: {block.text[:100]}...")
```

---

## 🎨 Semantic Labels Explained

| Label | Meaning | Example |
|-------|---------|---------|
| EXPLANATION | General description | "The process works by..." |
| DEFINITION | Formal definition | "X is defined as..." |
| EXAMPLE | Example | "For instance,..." |
| QUESTION | Question | "What is...?" |
| ANSWER | Answer to question | "The answer is..." |
| IMPORTANT | Important note | "⚠️ Note that..." |
| CONCLUSION | Summary/conclusion | "In summary,..." |
| INTRODUCTION | Introduction | "This paper covers..." |

---

## 🐛 Troubleshooting

### PDF not found?
```python
import os
pdf_path = os.path.abspath("documents/my_file.pdf")
output = agent.process(DUAInput(pdf_path=pdf_path))
```

### Memory issues with large PDFs?
```python
# Use less verbose logging
agent = DocumentUnderstandingAgent(log_level="WARNING")
```

### Need more details?
```python
# Enable debug logging
agent = DocumentUnderstandingAgent(log_level="DEBUG")
output = agent.process(input_data)  # Will print lots of details
```

---

## 📚 Learn More

- **[README.md](README.md)** - Full documentation
- **[API_REFERENCE.md](API_REFERENCE.md)** - API details
- **[SETUP.md](SETUP.md)** - Setup guide

---

## ✨ You're Ready!

That's it! You now have Document Understanding working. 

Next steps:
1. Try with different PDF types
2. Explore the output structure
3. Integrate with other agents
4. Customize for your needs

🎉 Happy processing!

---

**Need help?** Check the documentation files listed above.
