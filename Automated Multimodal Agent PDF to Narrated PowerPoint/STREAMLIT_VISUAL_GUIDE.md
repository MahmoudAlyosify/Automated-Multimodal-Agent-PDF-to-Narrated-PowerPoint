# 📊 Streamlit GUI - Visual Guide

## 🎨 User Interface Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│                  🌐 PDF to PowerPoint Converter                          │
│                  http://localhost:8501                                   │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┬────────────────────────────────────────────┐
│                             │                                            │
│  SIDEBAR                    │              MAIN CONTENT                  │
│  ⚙️ Settings               │                                            │
│  ────────────────────      │  📊 PDF to PowerPoint Converter            │
│  Document Domain:          │  Convert your PDF documents into            │
│  [▼ general              ]  │  professional PowerPoint presentations     │
│                             │                                            │
│  Language Code:            │  ┌─ 📤 Upload & Process ─────────────────┐ │
│  [______ en _____]         │  │                                       │ │
│                             │  │  Step 1: Upload PDF                 │ │
│  Page Range:               │  │  ┌───────────────────────────────┐   │ │
│  Start: [0      ]          │  │  │ 📁 Choose a PDF file          │   │ │
│  End:   [-1     ]          │  │  └───────────────────────────────┘   │ │
│                             │  │                                       │ │
│  API Configuration:        │  │  Drag and drop a file here, or       │ │
│  ✓ Mistral API: OFF       │  │  click to select files                │ │
│                             │  │                                       │ │
│  About:                    │  │  ┌─────────────────────────────────┐ │ │
│  System for PDF to PPT     │  │  │ File Size: 100 KB               │ │ │
│  conversion                │  │  │ Pages: 5                        │ │ │
│                             │  │  │ Format: PDF                     │ │ │
└─────────────────────────────┤  │  └─────────────────────────────────┘ │ │
                             │  │                                       │ │
                             │  │  Step 2: Process Document              │ │
                             │  │  [🔄 Process PDF]                     │ │
                             │  │                                       │ │
                             │  │  Step 3: Generate PowerPoint           │ │
                             │  │  [⚡ Generate PowerPoint]             │ │
                             │  │                                       │ │
                             │  └─────────────────────────────────────┘ │
                             │                                            │
                             │  📋 Preview │ 📥 Download                 │
                             │                                            │
└────────────────────────────────────────────────────────────────────────┘
```

## 📤 Upload & Process Tab

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Step 1: Upload PDF                                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ 📁 Choose a PDF file                                               │ │
│  │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│  │                                                                    │ │
│  │  Drag and drop a file here, or click to select files              │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ✓ File uploaded: document.pdf                                         │
│                                                                          │
│  ┌─────────────┬─────────────┬─────────────┐                           │
│  │ File Size   │ Total Pages │ Format      │                           │
│  │─────────────┼─────────────┼─────────────┤                           │
│  │ 250.5 KB    │ 12          │ PDF         │                           │
│  └─────────────┴─────────────┴─────────────┘                           │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│ Step 2: Process Document                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [🔄 Process PDF                                               Button] │
│                                                                          │
│  ⏳ Processing...                                                        │
│  📖 Extracting content from PDF...                                      │
│                                                                          │
│  ✓ Content extracted successfully!                                      │
│                                                                          │
│  ┌─────────────┬──────────────┬─────────────┬──────────────┐            │
│  │ Pages       │ Content Blks │ Confidence  │ Has Tables   │            │
│  │─────────────┼──────────────┼─────────────┼──────────────┤            │
│  │ 12          │ 45           │ 78.5%       │ No           │            │
│  └─────────────┴──────────────┴─────────────┴──────────────┘            │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│ Step 3: Generate PowerPoint                                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [⚡ Generate PowerPoint                                       Button] │
│                                                                          │
│  🎨 Creating PowerPoint presentation...                                  │
│                                                                          │
│  ✓ PowerPoint created successfully!                                     │
│  📊 Generated 12 slides                                                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📋 Preview Tab

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Extracted Content Preview                                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ Metadata Summary:                                                        │
│ ┌─────────────┬──────────────┬─────────────┬──────────────┐             │
│ │ Pages       │ Confidence   │ Tables      │ Images       │             │
│ │─────────────┼──────────────┼─────────────┼──────────────┤             │
│ │ 12          │ 78.5%        │ No          │ No           │             │
│ └─────────────┴──────────────┴─────────────┴──────────────┘             │
│                                                                          │
│ Document Structure:                                                      │
│                                                                          │
│ ┌─ 📑 Introduction (Level 1)         [Collapse]                        │ │
│ │                                                                       │ │
│ │  Block 1 (PARAGRAPH)                                                │ │
│ │  "This document provides a comprehensive overview of..."             │ │
│ │                                                                       │ │
│ │  [Details]  [Show More...]                                          │ │
│ │                                                                       │ │
│ │  ─────────────────────────────────────────────────────────          │ │
│ │                                                                       │ │
│ │  Block 2 (HEADING)                                                  │ │
│ │  "Key Concepts and Definitions"                                     │ │
│ │                                                                       │ │
│ │  [Details]                                                          │ │
│ │                                                                       │ │
│ └ ─────────────────────────────────────────────────────────            │
│                                                                          │
│ ┌─ 📑 Chapter 1                     [Collapse]                         │ │
│ │ [Expandable section]                                                │ │
│ └ ─────────────────────────────────────────────────────────            │
│                                                                          │
│ [Raw JSON Data                     [Expand]]                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📥 Download Tab

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Download Results                                                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ ┌────────────────────────┐  ┌────────────────────────┐                 │
│ │ 📊 PowerPoint          │  │ 📄 Extracted Content   │                 │
│ │    Presentation        │  │    (JSON)              │                 │
│ ├────────────────────────┤  ├────────────────────────┤                 │
│ │                        │  │                        │                 │
│ │ [📥 Download      ]    │  │ [📥 Download JSON  ]   │                 │
│ │  PowerPoint            │  │                        │                 │
│ │                        │  │ ✓ Ready to download    │                 │
│ │ ✓ Ready:               │  │                        │                 │
│ │  document_pres.pptx    │  │                        │                 │
│ │                        │  │                        │                 │
│ └────────────────────────┘  └────────────────────────┘                 │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│ Processing Summary                                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ Input: document.pdf              Output: document_presentation.pptx    │
│ Pages Processed: 12              Confidence: 78.5%                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Processing Flow

```
┌──────────┐
│ PDF FILE │
└────┬─────┘
     │
     v
┌────────────────────────────────────┐
│ DOCUMENT UNDERSTANDING AGENT       │
│ • Extract text                     │
│ • Analyze layout                   │
│ • Classify content blocks          │
│ • Extract metadata                 │
└────────┬─────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│ EXTRACTED CONTENT (JSON)           │
│ • Document structure               │
│ • Sections and blocks              │
│ • Metadata                         │
│ • Confidence scores                │
└────────┬─────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│ PRESENTATION DESIGN                │
│ • Create slide layout              │
│ • Format content                   │
│ • Add styling                      │
└────────┬─────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│ JSON TO PPT GENERATOR              │
│ • Build presentation               │
│ • Render slides                    │
│ • Generate .pptx file              │
└────────┬─────────────────────────┘
         │
         v
┌──────────────────┐
│ POWERPOINT FILE  │
│ (Ready to use)   │
└──────────────────┘
```

## 🔄 User Actions Flow

```
    START
      │
      v
   ┌──────────────┐
   │ Open GUI in  │
   │ Browser      │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Upload PDF   │
   │ File         │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Configure    │──no──┐
   │ Settings?    │      │
   └──┬───────────┘      │
      │                   │
      yes                 │
      │                   │
      v                   │
   ┌──────────────┐       │
   │ Select Domain,<──────┘
   │ Language, etc.
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Process PDF  │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Extract Done │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Generate PPT │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Go to        │
   │ Download Tab │
   └──────┬───────┘
          │
          v
   ┌──────────────┐
   │ Download     │
   │ Files        │
   └──────┬───────┘
          │
          v
      END
```

## 💾 File Management

```
Project Directory
│
├─ streamlit_app.py ..................... GUI Application
├─ run_gui.bat .......................... Windows Launcher
├─ run_gui.ps1 .......................... PowerShell Launcher
│
├─ Generated Files (Auto-created):
│  ├─ output_demo.pptx .................. PowerPoint Presentation
│  ├─ extracted_content.json ............ Extracted Data
│  ├─ ppt_input.json .................... PPT Structure
│  └─ [your_file]_presentation.pptx .... Downloaded PPT
│
└─ Documentation:
   ├─ STREAMLIT_GUI.md .................. Full Documentation
   ├─ STREAMLIT_SETUP.md ................ Setup Guide
   └─ STREAMLIT_QUICKSTART.py ........... Quick Start
```

---

**🎨 Visual Guide Complete!**

The GUI provides an intuitive, user-friendly interface for converting PDFs to PowerPoint presentations with just a few clicks.
