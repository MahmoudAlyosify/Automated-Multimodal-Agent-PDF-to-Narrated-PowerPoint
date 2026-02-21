#!/usr/bin/env python3
"""
Quick Setup Script for LangGraph Orchestrator

This script helps you get the orchestrator up and running quickly.
Run: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False

def main():
    """Main setup routine."""
    print("\n" + "="*60)
    print("🎬 PDF to Narrated PowerPoint - LangGraph Orchestrator")
    print("="*60)
    
    orchestrator_dir = Path(__file__).parent
    
    # Check if orchestrator directory exists
    if not orchestrator_dir.exists():
        print("❌ Cannot find orchestrator directory")
        sys.exit(1)
    
    print(f"\n📁 Orchestrator Directory: {orchestrator_dir}")
    
    # 1. Check Python version
    print(f"\n🐍 Python Version: {sys.version}")
    if sys.version_info < (3, 10):
        print("⚠️  Warning: Python 3.10+ is recommended")
    
    # 2. Install requirements
    os.chdir(orchestrator_dir)
    
    print("\n📦 Installing Dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing packages"):
        print("\n⚠️  Some packages failed to install. Try running:")
        print(f"   {sys.executable} -m pip install -r requirements.txt --upgrade")
    
    # 3. Verify important packages
    print("\n✔️  Verifying critical packages...")
    critical_packages = ['langgraph', 'streamlit', 'transformers', 'pyttsx3']
    all_ok = True
    
    for pkg in critical_packages:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some critical packages are missing. Please install them manually.")
        sys.exit(1)
    
    # 4. Check agent directories
    print("\n🤖 Checking Agent Directories...")
    parent_dir = orchestrator_dir.parent / "Agentic Systems"
    expected_agents = [
        "1- PDF Parser and Layout Analyzer Agent",
        "2- Semantic Chunker Agent",
        "3- Vector DB + Embeddings Layer",
        "4- Slide Planner Agent",
        "5- Slide Generator Agent",
        "6- PPTX Builder Agent",
        "7- Script Agent for each slide in PPTX",
        "8- TTS  Generative Audio Agent",
    ]
    
    all_present = True
    for agent_dir in expected_agents:
        path = parent_dir / agent_dir
        if path.exists():
            print(f"   ✅ {agent_dir}")
        else:
            print(f"   ❌ {agent_dir} (not found)")
            all_present = False
    
    if not all_present:
        print("\n⚠️  Some agent directories are missing. Make sure you have all 8 agents.")
    
    # 5. Create output directory
    print("\n📁 Creating Output Directory...")
    output_dir = orchestrator_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Output directory: {output_dir}")
    
    # 6. Summary
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    print("\n🚀 To start the application:")
    print(f"\n   cd {orchestrator_dir}")
    print("   streamlit run app.py")
    
    print("\n📖 For more information:")
    print("   - README.md - Overview and quick start")
    print("   - INTEGRATION_GUIDE.md - Detailed integration guide")
    
    print("\n💡 Tips:")
    print("   - Upload a PDF file through the web interface")
    print("   - Monitor progress in real-time")
    print("   - Download PPTX and audio files when complete")
    print("   - Check logs for detailed execution information")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
