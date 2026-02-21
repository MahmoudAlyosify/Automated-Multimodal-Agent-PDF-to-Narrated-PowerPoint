# Automated Multimodal Agent: PDF to Narrated PowerPoint

## Overview

Transform PDF documents into engaging, narrated PowerPoint presentations automatically. This advanced system uses a multi-agent architecture to parse, analyze, plan, and generate professional presentations with AI-generated voiceovers.

### Key Features
- **Intelligent PDF Parsing**: Extracts text, layout, and structural information from PDFs
- **Smart Content Chunking**: Semantically organizes content for logical slide flow
- **Vector-based Retrieval**: Uses embeddings for intelligent content mapping
- **Automated Slide Planning**: Generates optimized slide layouts and content distribution
- **Professional Presentation Generation**: Creates PPTX files with formatted content
- **AI Narration**: Generates natural-sounding audio narration for each slide using TTS
- **End-to-End Orchestration**: Seamless integration of all components through a master agent

## Team

- **Mahmoud Alyosify**
- **Mirna Mohsen**

## System Architecture

The system is built on a multi-agent orchestration framework with the following agents:

1. **PDF Parser & Layout Analyzer Agent**: Extracts and analyzes PDF content structure
2. **Semantic Chunker Agent**: Breaks down content into meaningful semantic blocks
3. **Vector DB & Embeddings Layer**: Creates and manages vector embeddings for content
4. **Slide Planner Agent**: Plans slide layouts and content organization
5. **Slide Generator Agent**: Creates presentation structure and content
6. **PPTX Builder Agent**: Builds the actual PowerPoint file
7. **Script Agent**: Generates narration scripts for each slide
8. **TTS Generative Audio Agent**: Creates audio files from scripts
9. **Master Orchestrator Agent**: Coordinates all agents and manages the workflow

## Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)

### Installation

```bash
# Clone or navigate to the project directory
cd "Automated-Multimodal-Agent-PDF-to-Narrated-PowerPoint"

# Install dependencies
pip install -r requirements.txt
```

### Usage

```python
# Run the master orchestrator
python "Agentic Systems/Master Orchestrator Agent/master_agent.py"
```

Provide your PDF file path when prompted, and the system will automatically:
1. Parse the PDF
2. Extract and chunk content
3. Plan the presentation structure
4. Generate slides
5. Create narration scripts
6. Generate audio files
7. Output the final narrated PowerPoint presentation

## Output Structure

All generated files are organized in the `output/` directory:
- `slides/`: Generated PPTX file(s)
- `audio/`: Audio files for narration
- `metadata/`: Intermediate processing files and metadata

## Documentation

For detailed implementation guides and technical documentation, refer to:
- [Complete System Documentation](README_COMPLETE.md)
- [System Architecture Details](SYSTEM_COMPLETE.md)
- [Audio Integration Guide](AUDIO_INTEGRATION_GUIDE.md)
- [Quick Start Audio Setup](QUICK_START_AUDIO.md)

## Project Directory

```
Agentic Systems/
├── 1- PDF Parser and Layout Analyzer Agent/
├── 2- Semantic Chunker Agent/
├── 3- Vector DB + Embeddings Layer/
├── 4- Slide Planner Agent/
├── 5- Slide Generator Agent/
├── 6- PPTX Builder Agent/
├── 7- Script Agent for each slide in PPTX/
├── 8- TTS Generative Audio Agent/
└── Master Orchestrator Agent/
output/
├── slides/
├── audio/
└── metadata/
```

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

---

**Last Updated**: February 2026
