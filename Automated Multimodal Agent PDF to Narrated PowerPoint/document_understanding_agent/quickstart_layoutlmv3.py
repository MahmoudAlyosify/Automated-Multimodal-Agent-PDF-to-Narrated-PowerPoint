#!/usr/bin/env python
"""
Quick start for Document Understanding Agent with LayoutLMv3

Usage:
    python quickstart_layoutlmv3.py
"""

import sys
import os

print("""
╔════════════════════════════════════════════════════════════════╗
║   Document Understanding Agent with Microsoft LayoutLMv3       ║
║                                                                ║
║   🤖 Advanced PDF Understanding with Visual AI                ║
╚════════════════════════════════════════════════════════════════╝
""")

print("📋 Features:")
print("  ✓ LayoutLMv3 - Multimodal document understanding")
print("  ✓ Visual layout analysis")
print("  ✓ Element classification")
print("  ✓ Structure detection")
print("  ✓ Web interface (Streamlit)")
print()

# Check dependencies
print("🔍 Checking dependencies...")

required_packages = {
    "streamlit": "Streamlit web framework",
    "transformers": "HuggingFace transformers",
    "torch": "PyTorch deep learning",
    "fitz": "PDF processing (PyMuPDF)",
    "numpy": "Numerical computing"
}

missing = []
for pkg, desc in required_packages.items():
    try:
        __import__(pkg)
        print(f"  ✓ {pkg:15} - {desc}")
    except ImportError:
        print(f"  ✗ {pkg:15} - {desc} [MISSING]")
        missing.append(pkg)

if missing:
    print()
    print(f"⚠️  Missing packages: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

print()
print("✅ All dependencies installed!")
print()

# Initialize LayoutLMv3
print("🤖 Initializing LayoutLMv3...")
print("   (First-time download may take a few minutes)")
print()

from src.dua.modules.layoutlmv3_analyzer import LayoutLMv3Analyzer

analyzer = LayoutLMv3Analyzer()
info = analyzer.get_model_info()

if info["available"]:
    print("✅ LayoutLMv3 Ready!")
    print(f"   Model: {info['model_name']}")
    print(f"   Capabilities:")
    for cap in info['capabilities']:
        print(f"     • {cap}")
else:
    print("⚠️  LayoutLMv3 not available")
    print("   Will use rule-based analysis")

print()
print("🚀 Starting Streamlit app...")
print("   → Opening at http://localhost:8501")
print()

# Start Streamlit
os.system("streamlit run streamlit_app.py")
