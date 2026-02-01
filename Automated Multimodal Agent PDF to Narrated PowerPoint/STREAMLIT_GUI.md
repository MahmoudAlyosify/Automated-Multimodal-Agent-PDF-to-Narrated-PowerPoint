# 📊 Streamlit GUI - PDF to PowerPoint Converter

## Overview

A user-friendly web interface for the PDF-to-Narrated-PowerPoint System built with **Streamlit**. Upload PDFs and instantly convert them to professional PowerPoint presentations.

## Features

### ✨ Main Features
- **📤 PDF Upload** - Drag and drop or select PDF files
- **🔄 Automatic Processing** - Extract content using the Document Understanding Agent
- **⚡ PowerPoint Generation** - Create presentations in seconds
- **📥 Easy Download** - Download PowerPoint and extracted JSON data
- **👀 Content Preview** - View extracted content structure
- **⚙️ Configurable Settings** - Choose domain, language, and page range

### 🎨 Three-Tab Interface

1. **📤 Upload & Process Tab**
   - Upload PDF files
   - View file information (size, page count, format)
   - Configure processing parameters
   - Process PDF and generate PowerPoint
   - Real-time progress feedback

2. **📋 Preview Tab**
   - View extracted document metadata
   - Browse document structure and sections
   - Inspect individual content blocks
   - View raw JSON data

3. **📥 Download Tab**
   - Download generated PowerPoint presentations
   - Download extracted content as JSON
   - View processing summary
   - Access file information

## Running the Application

### Start the GUI

```bash
# From the project directory
cd "Automated Multimodal Agent PDF to Narrated PowerPoint"

# Run the Streamlit app
python -m streamlit run streamlit_app.py
```

The app will be available at: **http://localhost:8501**

### Alternative Methods

```bash
# Suppress logging
python -m streamlit run streamlit_app.py --logger.level=warning

# Specify port
python -m streamlit run streamlit_app.py --server.port 8502

# Run with custom theme
python -m streamlit run streamlit_app.py --theme.base dark
```

## How to Use

### Step 1: Upload PDF
1. Click on "Choose a PDF file" in the **Upload & Process** tab
2. Select a PDF from your computer
3. File information (size, pages, format) will be displayed

### Step 2: Configure Settings (Optional)
Use the sidebar to customize:
- **Document Domain**: general, academic, business, technical, legal
- **Language Code**: en, es, fr, etc.
- **Page Range**: Specify which pages to process (or process all)

### Step 3: Process PDF
1. Click the **"Process PDF"** button
2. The Document Understanding Agent will extract:
   - Document structure
   - Content blocks
   - Tables and images information
   - Confidence metrics
3. View extraction summary

### Step 4: Generate PowerPoint
1. Click the **"Generate PowerPoint"** button
2. A professional presentation will be created with:
   - Title slide
   - Content slides from extracted sections
   - Formatted text and structure
3. See generation status and slide count

### Step 5: Download Results
Switch to the **Download** tab to:
- 📊 Download the PowerPoint presentation (`.pptx`)
- 📄 Download extracted content as JSON
- 📊 Review processing summary

## Configuration

### Environment Variables

Create a `.env` file in the project directory:

```env
# Required for advanced features
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional Streamlit settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_LOGGER_LEVEL=warning
```

### Settings Sidebar

Configure extraction parameters:
- **Domain**: Type of document (academic, business, etc.)
- **Language**: Document language (en, es, fr, etc.)
- **Start Page**: First page to process (0-indexed)
- **End Page**: Last page to process (-1 for all)

## System Components

The GUI integrates three AI agents:

### 1. Document Understanding Agent
- Extracts document structure and content
- Analyzes layouts and classifies blocks
- Identifies tables, images, and text elements
- Returns confidence metrics

### 2. Brain Agent (Optional)
- Uses Mistral AI 7B for intelligent design
- Requires `MISTRAL_API_KEY` in `.env`
- Creates optimized presentation layouts

### 3. JSON to PPT Generator
- Converts structured data to PowerPoint
- Supports text, charts, shapes, tables, images
- Professional slide formatting
- Configurable themes

## Output Files

The application generates and allows download of:

### Generated Files
- **`output_demo.pptx`** - Generated PowerPoint presentation
- **`extracted_content.json`** - Extracted document content
- **`ppt_input.json`** - PPT input data structure

### Download Format
- **PowerPoint**: `.pptx` (Office Open XML format)
- **Content**: `.json` (Structured data)

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python -m streamlit run streamlit_app.py --server.port 8502
```

### PDF Upload Fails
- Ensure PDF file is not corrupted
- Check file size (should be < 100MB recommended)
- Try uploading a different PDF

### PowerPoint Generation Error
- Check that all dependencies are installed
- Review the error message in the console
- Ensure PDF was processed successfully

### API Key Warning
- This is normal if you haven't set `MISTRAL_API_KEY`
- The system works without it (uses demo presentation)
- To enable AI design, see Configuration section

## Keyboard Shortcuts

Streamlit provides built-in shortcuts:
- `C` - Clear cache and rerun
- `R` - Rerun app
- `Ctrl+M` - Toggle menu

## Browser Compatibility

Tested and working on:
- ✓ Chrome/Chromium
- ✓ Firefox
- ✓ Safari
- ✓ Edge

## Tips & Best Practices

### For Best Results
1. **Clear PDFs** - Ensure PDFs have good text extraction
2. **Reasonable Size** - Keep to 100 pages or fewer for faster processing
3. **Single Language** - Each PDF should be primarily one language
4. **Standard Layout** - Documents with standard layouts process better

### Performance Tips
- Process smaller page ranges first to test
- Use "academic" or "technical" domain for specific content types
- Enable Mistral API key for better presentation design

### Handling Large Documents
- Use page range to process sections at a time
- Combine multiple presentations if needed
- Check console for processing time metrics

## Advanced Usage

### Processing Multiple Files
1. Process one PDF completely
2. Use "Clear Cache" button (or press C)
3. Upload and process next PDF
4. Download results between files

### Batch Processing
For automated batch processing, use the CLI orchestrator:
```bash
python orchestrator.py input.pdf output.pptx
```

### Custom Presentation Styling
Edit the `ppt_input.json` file directly for advanced styling:
- Font sizes and colors
- Custom layouts
- Element positioning
- Theme customization

## System Requirements

- Python 3.8+
- 2GB+ RAM recommended
- Modern web browser
- ~500MB disk space

## Dependencies

See `requirements.txt` for complete list:
- streamlit (1.0+)
- pymupdf
- python-pptx
- mistralai (optional)
- dotenv

## Support & Documentation

For more information:
- See [README_MAIN.md](../README_MAIN.md) for system overview
- Check [QUICKSTART.md](../QUICKSTART.md) for quick setup
- Review [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details

## License

See LICENSE file in project root.

---

**PDF-to-Narrated-PowerPoint System v1.0**
*Streamlit GUI Interface*
