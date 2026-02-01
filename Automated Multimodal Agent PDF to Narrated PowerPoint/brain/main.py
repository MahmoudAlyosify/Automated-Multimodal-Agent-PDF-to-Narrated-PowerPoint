import json
import sys
import os
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mistral client
api_key = os.getenv("oLkrmVZUB7vIsTkuDHzj0umj4XivvobI")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set. Please set it in a .env file or environment.")

client = Mistral(api_key=api_key)

def generate_slides_json(extracted_content):
    """
    Use Mistral AI 7B to generate slide JSON from extracted content.
    """
    schema = """
{
  "ppt": {
    "size": { "width": 1280, "height": 720, "unit": "px" },
    "defaultUnit": "px",
    "theme": {
      "colors": {
        "primary": "#0066CC",
        "secondary": "#FF6B35",
        "accent": "#00D9FF",
        "dark": "#1A1A2E",
        "light": "#FFFFFF"
      }
    },
    "slides": [
      {
        "id": "slide-1",
        "title": "Title Slide",
        "background": { "color": "#0066CC" },
        "elements": [
          {
            "type": "text",
            "text": "AI & Generative AI",
            "box": { "x": 100, "y": 200, "w": 1080, "h": 120 },
            "style": { "fontSize": 72, "align": "center", "bold": true, "color": "#FFFFFF" }
          }
        ]
      }
    ]
  }
}
"""

    prompt = f"""
You are an expert at creating PowerPoint presentations from document content. Based on the following extracted content from a PDF, generate a complete JSON specification for a PowerPoint presentation.

Extracted Content:
{json.dumps(extracted_content, indent=2)}

Requirements:
- Create an appropriate number of slides based on the content.
- Include a title slide.
- Organize content logically across slides.
- Use the exact JSON schema provided below.
- Ensure all elements have proper positioning, colors, and styles.
- Make the presentation visually appealing and professional.

JSON Schema:
{schema}

Output only the JSON, no additional text.
"""

    response = client.chat.complete(
        model="mistral-small",  # Mistral 7B model
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the JSON from the response
    generated_json = response.choices[0].message.content.strip()

    # Try to parse it as JSON
    try:
        slides_data = json.loads(generated_json)
        return slides_data
    except json.JSONDecodeError as e:
        print(f"Error parsing generated JSON: {e}")
        print("Generated content:", generated_json)
        raise

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_json_file> <output_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Load input JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        extracted_content = json.load(f)

    # Generate slides JSON
    slides_json = generate_slides_json(extracted_content)

    # Write output JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(slides_json, f, indent=2)

    print(f"Slide JSON generated and saved to {output_file}")

if __name__ == "__main__":
    main()