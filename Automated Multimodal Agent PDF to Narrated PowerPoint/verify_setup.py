#!/usr/bin/env python3
"""
Comprehensive system verification script.
Tests all components of the PDF-to-Narrated-PowerPoint system.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

class SystemVerifier:
    """Verify all system components."""
    
    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.root_dir = Path(__file__).parent.absolute()
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, test_fn, description: str = ""):
        """Run a test and record result."""
        try:
            result = test_fn()
            if result:
                self.results[name] = (True, description or "✓ OK")
                self.passed += 1
                print(f"✓ {name}: {description or 'OK'}")
            else:
                self.results[name] = (False, "Test failed")
                self.failed += 1
                print(f"✗ {name}: Test failed")
        except Exception as e:
            self.results[name] = (False, str(e))
            self.failed += 1
            print(f"✗ {name}: {e}")
    
    def verify_python(self) -> bool:
        """Verify Python version."""
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"\nPython Version: {version}")
        return sys.version_info >= (3, 8)
    
    def verify_venv(self) -> bool:
        """Verify running in virtual environment."""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        if in_venv:
            print(f"Virtual Environment: {sys.prefix}")
        return in_venv
    
    def verify_directories(self) -> bool:
        """Verify all required directories exist."""
        dirs = [
            "document_understanding_agent",
            "brain",
            "JSON To PPT"
        ]
        for d in dirs:
            dir_path = self.root_dir / d
            if not dir_path.exists():
                print(f"  ✗ Missing: {d}")
                return False
            print(f"  ✓ {d}")
        return True
    
    def verify_files(self) -> bool:
        """Verify all required files exist."""
        files = {
            "document_understanding_agent/src/dua/__init__.py": "Document Understanding Agent",
            "brain/main.py": "Brain Agent",
            "JSON To PPT/main.py": "JSON to PPT Agent",
            "orchestrator.py": "Orchestrator",
            "requirements.txt": "Requirements",
            ".env": "Environment Configuration"
        }
        
        all_exist = True
        for file_path, description in files.items():
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"  ✓ {description}: {file_path}")
            else:
                print(f"  ✗ Missing: {file_path} ({description})")
                if not file_path.endswith(".env"):  # .env is optional initially
                    all_exist = False
        return all_exist
    
    def verify_imports(self) -> bool:
        """Verify critical imports work."""
        print("\nVerifying imports:")
        imports = {
            "pymupdf": "PyMuPDF",
            "pdfplumber": "PDFPlumber",
            "numpy": "NumPy",
            "mistralai": "Mistral AI",
            "dotenv": "Python-dotenv",
            "pptx": "Python-pptx",
            "pillow": "Pillow",
            "requests": "Requests"
        }
        
        all_ok = True
        for import_name, description in imports.items():
            try:
                __import__(import_name)
                print(f"  ✓ {description}")
            except ImportError:
                print(f"  ✗ {description} (not installed)")
                all_ok = False
        
        return all_ok
    
    def verify_api_key(self) -> bool:
        """Verify Mistral API key is configured."""
        try:
            from dotenv import load_dotenv
            load_dotenv(self.root_dir / ".env")
            api_key = os.getenv("MISTRAL_API_KEY")
            if api_key and api_key.strip():
                masked = api_key[:10] + "..." + api_key[-5:]
                print(f"\nMISTRAL_API_KEY: {masked}")
                return True
            else:
                print("\nMISTRAL_API_KEY: NOT SET")
                print("  To configure: Edit .env file with MISTRAL_API_KEY=your_key")
                return False
        except Exception as e:
            print(f"\nMISTRAL_API_KEY check failed: {e}")
            return False
    
    def verify_orchestrator(self) -> bool:
        """Verify orchestrator can be imported."""
        try:
            sys.path.insert(0, str(self.root_dir))
            from orchestrator import PDFToPresentation
            print("\nOrchestrator: Can import successfully")
            return True
        except Exception as e:
            print(f"\nOrchestrator: Import failed: {e}")
            return False
    
    def verify_dua(self) -> bool:
        """Verify Document Understanding Agent."""
        try:
            sys.path.insert(0, str(self.root_dir / "document_understanding_agent" / "src"))
            from dua import DocumentUnderstandingAgent
            agent = DocumentUnderstandingAgent()
            status = agent.get_status()
            print(f"\nDocument Understanding Agent: Initialized")
            print(f"  Modules: {len(status.get('modules', []))} loaded")
            return True
        except Exception as e:
            print(f"\nDocument Understanding Agent: Failed - {e}")
            return False
    
    def verify_mistral(self) -> bool:
        """Verify Mistral AI connection (without API call)."""
        try:
            from mistralai import Mistral
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                print("\nMistral AI: API key not configured")
                return False
            
            client = Mistral(api_key=api_key)
            print("\nMistral AI: Client initialized successfully")
            return True
        except Exception as e:
            print(f"\nMistral AI: {e}")
            return False
    
    def verify_pptx(self) -> bool:
        """Verify Python-pptx."""
        try:
            from pptx import Presentation
            prs = Presentation()
            print(f"\nPowerPoint: Can create presentations")
            print(f"  Default slide width: {prs.slide_width}")
            return True
        except Exception as e:
            print(f"\nPowerPoint: {e}")
            return False
    
    def run_all(self):
        """Run all verification tests."""
        print("=" * 70)
        print("PDF-to-Narrated-PowerPoint System Verification")
        print("=" * 70)
        
        # Environment
        print("\n[1] ENVIRONMENT")
        self.test("Python Version", self.verify_python, f"{sys.version.split()[0]}")
        self.test("Virtual Environment", self.verify_venv, "Using virtual environment")
        
        # Structure
        print("\n[2] PROJECT STRUCTURE")
        self.test("Directories", self.verify_directories)
        self.test("Files", self.verify_files)
        
        # Dependencies
        print("\n[3] DEPENDENCIES")
        self.test("Python Imports", self.verify_imports)
        
        # Configuration
        print("\n[4] CONFIGURATION")
        self.test("API Key", self.verify_api_key)
        
        # Components
        print("\n[5] COMPONENTS")
        self.test("Orchestrator", self.verify_orchestrator)
        self.test("Document Understanding", self.verify_dua)
        self.test("Mistral AI", self.verify_mistral)
        self.test("PowerPoint", self.verify_pptx)
        
        # Summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        total = self.passed + self.failed
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        
        if self.failed == 0:
            print("\n✓ All checks passed! System is ready to use.")
            print("\nQuick start:")
            print("  python orchestrator.py input.pdf output.pptx")
            return True
        else:
            print(f"\n⚠ {self.failed} check(s) failed. Please review above.")
            print("\nFailing checks:")
            for name, (passed, msg) in self.results.items():
                if not passed:
                    print(f"  - {name}: {msg}")
            return False
    
    def print_help(self):
        """Print help for common issues."""
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("""
Common Issues and Solutions:

1. MISTRAL_API_KEY not set
   → Create .env file with: MISTRAL_API_KEY=your_key
   → Get key from: https://console.mistral.ai/

2. Missing imports (pymupdf, mistralai, etc.)
   → Run: pip install -r requirements.txt

3. Document Understanding Agent import fails
   → Run: cd document_understanding_agent && pip install -e .

4. Streamlit not found
   → Run: pip install streamlit

5. Virtual environment not activated
   → Windows: .venv\\Scripts\\activate
   → Unix/Mac: source .venv/bin/activate

For more help, see:
- SETUP.md - Complete setup instructions
- ARCHITECTURE.md - System architecture
- QUICKSTART.md - Quick examples
- EXAMPLES.md - Detailed workflows
        """)


def main():
    """Main entry point."""
    verifier = SystemVerifier()
    success = verifier.run_all()
    verifier.print_help()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
