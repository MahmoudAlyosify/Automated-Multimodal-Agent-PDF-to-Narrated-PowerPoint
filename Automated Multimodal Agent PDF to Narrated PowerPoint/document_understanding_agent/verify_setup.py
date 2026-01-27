#!/usr/bin/env python
"""
Verify LayoutLMv3 Integration Setup
Checks all components and dependencies
"""

import sys
import os

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or version.minor < 10:
        print("  ⚠️  Recommended Python 3.10+")
    return True

def check_imports():
    """Check all required imports"""
    print("\n📦 Checking imports...")
    
    required = {
        "streamlit": "Web interface",
        "transformers": "LayoutLMv3 model",
        "torch": "Deep learning framework",
        "fitz": "PDF processing",
        "numpy": "Numerical computing",
        "PIL": "Image processing",
    }
    
    all_ok = True
    for module, desc in required.items():
        try:
            __import__(module)
            print(f"  ✓ {module:20} - {desc}")
        except ImportError:
            print(f"  ✗ {module:20} - {desc} [MISSING]")
            all_ok = False
    
    return all_ok

def check_files():
    """Check required files exist"""
    print("\n📂 Checking files...")
    
    files = {
        "streamlit_app.py": "Main Streamlit app",
        "src/dua/agent.py": "DUA orchestrator",
        "src/dua/modules/layoutlmv3_analyzer.py": "LayoutLMv3 module",
        "LAYOUTLMV3_GUIDE.md": "LayoutLMv3 documentation",
        "init_layoutlmv3.py": "Model initialization",
    }
    
    all_ok = True
    for filepath, desc in files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filepath:40} - {desc} ({size:,} bytes)")
        else:
            print(f"  ✗ {filepath:40} - {desc} [MISSING]")
            all_ok = False
    
    return all_ok

def check_layoutlmv3():
    """Check LayoutLMv3 module"""
    print("\n🤖 Checking LayoutLMv3...")
    
    try:
        from src.dua.modules.layoutlmv3_analyzer import LayoutLMv3Analyzer
        
        print("  ✓ LayoutLMv3Analyzer imported successfully")
        
        analyzer = LayoutLMv3Analyzer()
        info = analyzer.get_model_info()
        
        print(f"  Model: {info['model_name']}")
        print(f"  Available: {info['available']}")
        
        if info['available']:
            print("  ✓ LayoutLMv3 ready to use!")
            return True
        else:
            print("  ⚠️  LayoutLMv3 not available (will use fallback)")
            return True  # Not critical
            
    except Exception as e:
        print(f"  ✗ Error checking LayoutLMv3: {str(e)}")
        return False

def check_dua():
    """Check DUA components"""
    print("\n📊 Checking DUA Components...")
    
    components = [
        ("src.dua.agent", "DocumentUnderstandingAgent"),
        ("src.dua.types", "DUAInput"),
        ("src.dua.config", "Presets"),
        ("src.dua.modules.pdf_loader", "PDFLoader"),
        ("src.dua.modules.layout_analyzer", "LayoutAnalyzer"),
        ("src.dua.modules.block_classifier", "BlockClassifier"),
    ]
    
    all_ok = True
    for module, cls in components:
        try:
            mod = __import__(module, fromlist=[cls])
            getattr(mod, cls)
            print(f"  ✓ {module:45} - {cls}")
        except Exception as e:
            print(f"  ✗ {module:45} - {cls} [ERROR: {str(e)[:30]}...]")
            all_ok = False
    
    return all_ok

def check_gpu():
    """Check GPU availability"""
    print("\n⚡ Checking GPU...")
    
    try:
        import torch
        available = torch.cuda.is_available()
        
        if available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print(f"  ✓ GPU available: {device_count} device(s)")
            print(f"    → {device_name}")
            print("    💡 LayoutLMv3 will run 50-100x faster!")
        else:
            print("  ℹ️  No GPU detected - using CPU")
            print("    💡 Processing will be slower but still functional")
        
        return True
    except Exception as e:
        print(f"  ℹ️  GPU check failed: {str(e)}")
        return True

def print_summary(results):
    """Print summary"""
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_ok = all(results.values())
    
    status = "✅ ALL CHECKS PASSED" if all_ok else "⚠️  SOME ISSUES FOUND"
    print(f"\n{status}\n")
    
    for check, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check}")
    
    print("\n" + "="*60)
    
    if all_ok:
        print("\n🚀 Ready to use! Run:")
        print("   python -m streamlit run streamlit_app.py")
    else:
        print("\n⚠️  Fix the issues above before running the app")
        print("   See LAYOUTLMV3_GUIDE.md for troubleshooting")

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("LayoutLMv3 Integration Verification")
    print("="*60 + "\n")
    
    results = {
        "Python": check_python(),
        "Required Imports": check_imports(),
        "Project Files": check_files(),
        "DUA Components": check_dua(),
        "LayoutLMv3": check_layoutlmv3(),
        "GPU Support": check_gpu(),
    }
    
    print_summary(results)

if __name__ == "__main__":
    main()
