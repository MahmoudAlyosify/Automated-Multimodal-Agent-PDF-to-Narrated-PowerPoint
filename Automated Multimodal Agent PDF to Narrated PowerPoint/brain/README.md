# Brain Agent

The Brain Agent is the central reasoning and orchestration unit of the Automated Multimodal Agent system. It is implemented using Mistral AI 7B and is responsible for analyzing extracted PDF content and generating presentation-ready slide definitions in JSON format.

## Responsibilities

- Receive JSON output from the Document Understanding Agent
- Analyze and reason over the extracted content using Mistral AI 7B
- Generate comprehensive slide JSON specifications including:
  - Number of slides
  - Slide titles and content
  - Layout structure and element positioning
  - Colors, fonts, and styling
  - Visual hierarchy

## Input

- JSON file from `document_understanding_agent` containing structured extracted content from PDFs

## Output

- JSON file conforming to the slide specification schema, ready for the PPT Conversion Agent

## Implementation

Built with Mistral AI 7B for advanced reasoning and content generation capabilities.

## Usage

Run the main script with the input JSON file:

```bash
python main.py input.json output.json
```

The output JSON will be transferred to the PPT Conversion Agent for PowerPoint generation.