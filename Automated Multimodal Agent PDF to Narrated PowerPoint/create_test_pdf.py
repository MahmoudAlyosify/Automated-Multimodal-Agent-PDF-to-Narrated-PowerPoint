#!/usr/bin/env python3
"""Create a simple test PDF for the system."""

import sys
from pathlib import Path

# Try to create a simple PDF using pymupdf
try:
    import fitz  # PyMuPDF
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Page 1
    page = doc.new_page()
    text = """Introduction to Machine Learning

Machine Learning is a subset of artificial intelligence that focuses on the 
development of algorithms and statistical models that enable computers to 
improve their performance on tasks through experience.

Key Concepts:
- Supervised Learning: Learning from labeled data
- Unsupervised Learning: Finding patterns in unlabeled data
- Reinforcement Learning: Learning through interaction with environment
"""
    page.insert_text((50, 50), text, fontsize=11)
    
    # Page 2
    page = doc.new_page()
    text2 = """Applications of Machine Learning

1. Natural Language Processing
   - Text classification
   - Sentiment analysis
   - Machine translation

2. Computer Vision
   - Image recognition
   - Object detection
   - Face recognition

3. Predictive Analytics
   - Stock price prediction
   - Customer behavior analysis
   - Demand forecasting
"""
    page.insert_text((50, 50), text2, fontsize=11)
    
    # Page 3
    page = doc.new_page()
    text3 = """Future of Machine Learning

The future of machine learning holds tremendous potential:

- Deep Learning: Neural networks with multiple layers
- Quantum Machine Learning: Utilizing quantum computing
- Federated Learning: Training on distributed data
- Explainable AI: Making models more interpretable

These advancements will shape the technology landscape 
for decades to come.
"""
    page.insert_text((50, 50), text3, fontsize=11)
    
    # Save the PDF
    output_path = Path(__file__).parent / "test_input.pdf"
    doc.save(str(output_path))
    doc.close()
    
    print(f"Test PDF created: {output_path}")
    print(f"  File size: {output_path.stat().st_size} bytes")
    print(f"  Pages: 3")
    sys.exit(0)
    
except Exception as e:
    print(f"Error creating PDF: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
