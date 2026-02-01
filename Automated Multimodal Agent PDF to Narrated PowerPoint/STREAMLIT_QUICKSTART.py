#!/usr/bin/env python3
"""
Quick Start Guide for Streamlit GUI

This file demonstrates how to use the Streamlit interface.
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   STREAMLIT GUI QUICK START GUIDE                         ║
║                  PDF to PowerPoint Converter Web Interface                ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 WHAT YOU CAN DO WITH THE GUI:

  ✓ Upload PDF files (drag & drop or select)
  ✓ Extract document content automatically
  ✓ Generate professional PowerPoint presentations
  ✓ Preview extracted content structure
  ✓ Download .pptx files directly
  ✓ Download extracted data as JSON
  ✓ Configure processing parameters

═══════════════════════════════════════════════════════════════════════════

🚀 STARTING THE STREAMLIT APP:

  1. Open a terminal/command prompt
  2. Navigate to the project directory:
     
     cd "d:\\Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint"
     cd "Automated Multimodal Agent PDF to Narrated PowerPoint"

  3. Run the Streamlit app:
     
     python -m streamlit run streamlit_app.py

  4. Your browser will open automatically at http://localhost:8501
     (If not, open the URL manually)

═══════════════════════════════════════════════════════════════════════════

📝 STEP-BY-STEP USAGE:

  STEP 1: UPLOAD PDF
  ──────────────────
  • Click "Choose a PDF file" in the Upload & Process tab
  • Select a PDF from your computer
  • View file information (size, pages, format)

  STEP 2: CONFIGURE (OPTIONAL)
  ────────────────────────────
  Use the Settings sidebar to:
  • Select document domain (general, academic, technical, etc.)
  • Specify language (en, es, fr, etc.)
  • Choose page range (start and end page)

  STEP 3: PROCESS PDF
  ──────────────────
  • Click "🔄 Process PDF" button
  • Wait for extraction to complete
  • View extraction summary:
    - Pages processed
    - Content blocks extracted
    - Confidence level
    - Metadata

  STEP 4: GENERATE POWERPOINT
  ──────────────────────────
  • Click "⚡ Generate PowerPoint" button
  • System creates professional presentation
  • View slide count and status
  • Files are ready for download

  STEP 5: DOWNLOAD RESULTS
  ────────────────────────
  • Switch to "📥 Download" tab
  • Download PowerPoint (.pptx file)
  • Download extracted content (JSON file)
  • View processing summary

═══════════════════════════════════════════════════════════════════════════

🎨 INTERFACE OVERVIEW:

  ┌─────────────────────────────────────────────────────────────────────┐
  │ SIDEBAR (Settings)                                                  │
  ├─────────────────────────────────────────────────────────────────────┤
  │ • Document Domain selector                                          │
  │ • Language code input                                               │
  │ • Page range configuration                                          │
  │ • API Key status                                                    │
  │ • About section                                                     │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │ MAIN TABS                                                            │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                      │
  │ 📤 Upload & Process                                                 │
  │    • Upload PDF files                                              │
  │    • Configure processing                                          │
  │    • Extract content                                               │
  │    • Generate PowerPoint                                           │
  │                                                                      │
  │ 📋 Preview                                                          │
  │    • View extracted metadata                                       │
  │    • Browse document structure                                     │
  │    • Inspect content blocks                                        │
  │    • View raw JSON data                                            │
  │                                                                      │
  │ 📥 Download                                                         │
  │    • Download PowerPoint presentation                              │
  │    • Download extracted content                                    │
  │    • Processing summary                                            │
  │                                                                      │
  └─────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

💡 TIPS & FEATURES:

  ✓ PDF Drag & Drop: Drag PDF files directly to upload area
  ✓ Progress Feedback: Real-time processing status and spinners
  ✓ File Information: View page count, file size automatically
  ✓ Error Handling: Clear error messages if something goes wrong
  ✓ Multiple Files: Process different PDFs one after another
  ✓ Session Persistence: Results stay available while browsing tabs
  ✓ One-Click Download: Easy download buttons for all outputs

═══════════════════════════════════════════════════════════════════════════

⚙️ CONFIGURATION OPTIONS:

  Document Domain:
  • general    - Default, works for most documents
  • academic   - Papers, theses, textbooks
  • business   - Reports, proposals, presentations
  • technical  - Manuals, specifications, guides
  • legal      - Contracts, agreements, documents

  Language:
  • en - English (default)
  • es - Spanish
  • fr - French
  • de - German
  • etc. (any language code)

  Page Range:
  • Start Page: First page to process (0-indexed)
  • End Page:   Last page to process (-1 for all)

═══════════════════════════════════════════════════════════════════════════

🔧 ADVANCED OPTIONS:

  API Key Configuration:
  • Create .env file with: MISTRAL_API_KEY=your_key
  • Enables AI-powered presentation design
  • Get key from: https://console.mistral.ai/

  Port Configuration:
  python -m streamlit run streamlit_app.py --server.port 8502

  Logging Level:
  python -m streamlit run streamlit_app.py --logger.level=warning

═══════════════════════════════════════════════════════════════════════════

📊 OUTPUT FILES:

  Generated Automatically:
  • output_demo.pptx        - PowerPoint presentation
  • extracted_content.json  - Extracted document data
  • ppt_input.json          - Presentation structure

  Available for Download:
  • Your_File_presentation.pptx - Professional PowerPoint
  • Your_File_content.json       - Document structure

═══════════════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

  Q: "Port already in use" error?
  A: Use a different port with --server.port flag

  Q: Upload button doesn't work?
  A: Check browser console (F12) for errors, try refreshing page

  Q: PowerPoint generation fails?
  A: Ensure PDF was processed successfully, check console logs

  Q: API Key warning?
  A: Normal - system works without it, adds AI features with key

  Q: Slow processing?
  A: Try processing fewer pages, clear browser cache (C key)

═══════════════════════════════════════════════════════════════════════════

🎯 COMMON WORKFLOWS:

  Workflow 1: Single Document
  ──────────────────────────
  1. Open GUI (http://localhost:8501)
  2. Upload PDF
  3. Click "Process PDF"
  4. Click "Generate PowerPoint"
  5. Go to Download tab
  6. Download .pptx file
  7. Open in Microsoft PowerPoint or similar

  Workflow 2: Batch Processing
  ────────────────────────────
  1. Open GUI
  2. Process PDF #1 → Download
  3. Press C (clear cache)
  4. Upload PDF #2
  5. Repeat for each PDF

  Workflow 3: Extract Only
  ────────────────────────
  1. Open GUI
  2. Upload PDF
  3. Click "Process PDF"
  4. Go to Preview tab
  5. View document structure
  6. Download JSON in Download tab

═══════════════════════════════════════════════════════════════════════════

📚 ADDITIONAL RESOURCES:

  For More Information:
  • STREAMLIT_GUI.md         - Detailed GUI documentation
  • README_MAIN.md           - System overview
  • QUICKSTART.md            - Getting started guide
  • ARCHITECTURE.md          - Technical architecture
  • EXAMPLES.md              - Real-world usage examples

═══════════════════════════════════════════════════════════════════════════

🎉 YOU'RE ALL SET!

The Streamlit GUI is now running at: http://localhost:8501

Simply:
1. Upload a PDF
2. Click "Process PDF"
3. Click "Generate PowerPoint"
4. Download your presentation

Enjoy! 🚀

═══════════════════════════════════════════════════════════════════════════
""")
