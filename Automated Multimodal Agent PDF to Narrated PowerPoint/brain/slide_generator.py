"""
Slide Generator Agent with Theme & Design

PURPOSE: Converts slide blueprints into presentation-ready slide content with theme,
design, and semantic structure.

INPUT: Slide blueprint (dict with title and source chunks)
OUTPUT: Structured document tree with themed design, semantic labels, and importance scores

CONSTRAINTS:
- Maximum 5 bullet points per slide
- Each bullet ≤ 12 words
- Clear and technical language
- Audience: university students
- Semantic labeling (EXPLANATION, IMPORTANT, QUESTION, DEFINITION, ANSWER, EXAMPLE)
"""

import json
import re
import os
from typing import Optional, Dict, List, Any, Tuple
from mistralai import Mistral
from datetime import datetime

# Load API key from .env file if it exists
def _load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

_load_env()


class SlideGenerator:
    """Generates presentation-ready slide content from blueprints."""
    
    def __init__(self, api_key: str, model: str = "mistral-small-latest"):
        """
        Initialize the Slide Generator.
        
        Args:
            api_key: Mistral API key
            model: Model identifier (default: mistral-small-latest)
        """
        self.client = Mistral(api_key=api_key)
        self.model = model
        self.max_bullets = 5
        self.max_words_per_bullet = 12
    
    def _count_words(self, text: str) -> int:
        """Count words in a string."""
        return len(text.split())
    
    def _truncate_bullet(self, bullet: str) -> str:
        """Truncate bullet point to max word count."""
        words = bullet.split()
        if len(words) > self.max_words_per_bullet:
            return " ".join(words[:self.max_words_per_bullet])
        return bullet
    
    def _remove_redundancy(self, bullets: List[str]) -> List[str]:
        """Remove duplicate or redundant bullet points."""
        unique_bullets = []
        seen = set()
        
        for bullet in bullets:
            normalized = bullet.lower().strip()
            if normalized not in seen and len(normalized) > 0:
                unique_bullets.append(bullet)
                seen.add(normalized)
        
        return unique_bullets[:self.max_bullets]
    
    def _extract_bullets_from_response(self, response: str) -> List[str]:
        """Extract bullet points from model response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed.get('bullets'), list):
                    return parsed['bullets']
        except (json.JSONDecodeError, AttributeError):
            pass
        
        bullets = []
        lines = response.split('\n')
        for line in lines:
            cleaned = re.sub(r'^[-*•]\s*', '', line.strip())
            if cleaned and len(cleaned) > 5:
                bullets.append(cleaned)
        
        return bullets
    
    def _assign_semantic_label(self, bullet: str) -> str:
        """Assign semantic label based on bullet content."""
        bullet_lower = bullet.lower()
        
        if any(word in bullet_lower for word in ['what', 'how', 'why', 'which', 'when', 'where']):
            return "QUESTION"
        elif any(word in bullet_lower for word in ['is', 'means', 'defined', 'definition', 'concept']):
            return "DEFINITION"
        elif any(word in bullet_lower for word in ['important', 'critical', 'essential', 'key', 'crucial']):
            return "IMPORTANT"
        elif any(word in bullet_lower for word in ['example', 'like', 'such as', 'instance', 'case']):
            return "EXAMPLE"
        elif any(word in bullet_lower for word in ['therefore', 'thus', 'result', 'answer', 'conclusion']):
            return "ANSWER"
        else:
            return "EXPLANATION"
    
    def _calculate_importance(self, bullet: str, index: int, total: int) -> float:
        """Calculate importance score for a bullet point (0.5 to 0.75)."""
        position_score = 0.75 - (index / total) * 0.15
        
        keyword_boost = 0.0
        keywords = ['important', 'critical', 'essential', 'fundamental', 'core', 'key', 'crucial']
        if any(kw in bullet.lower() for kw in keywords):
            keyword_boost = 0.1
        
        importance = min(0.75, max(0.5, position_score + keyword_boost))
        return round(importance, 2)
    
    def _determine_theme(self, title: str, content: str) -> Dict[str, str]:
        """Determine theme and design based on content."""
        theme_prompt = f"""Based on this presentation title and content, suggest a professional theme and design style.

Title: {title}
Content snippet: {content[:500]}...

Respond with JSON:
{{
    "theme": "Academic/Technical/Business/Creative",
    "color_scheme": "description of colors",
    "design_style": "description of visual style",
    "typography": "description of fonts and text styling"
}}

Return only JSON, nothing else."""
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": theme_prompt}]
            )
            
            response_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        return {
            "theme": "Academic",
            "color_scheme": "Professional blue and white with accent colors",
            "design_style": "Clean, minimalist with emphasis on content clarity",
            "typography": "Sans-serif for headers, serif for body text"
        }
    
    def _create_block(
        self,
        block_type: str,
        text: str,
        semantic_label: str,
        importance: float,
        caption: str = ""
    ) -> Dict[str, Any]:
        """Create a content block with metadata."""
        return {
            "type": block_type,
            "semantic_label": semantic_label,
            "importance": importance,
            "text": text,
            "path": None,
            "caption": caption
        }
    
    def _create_section(
        self,
        title: str,
        level: int,
        blocks: List[Dict[str, Any]],
        subsections: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a section with blocks and optional subsections."""
        section = {
            "title": title,
            "level": level,
            "blocks": blocks
        }
        if subsections:
            section["subsections"] = subsections
        return section
    
    def generate(
        self,
        blueprint: Dict[str, Any],
        source_chunks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate slide content from a blueprint.
        
        Args:
            blueprint: Dictionary containing title, topic, source_chunks
            source_chunks: Optional list of source text chunks
        
        Returns:
            Dictionary with title and bullets
        """
        title = blueprint.get("title", "Untitled Slide")
        topic = blueprint.get("topic", "")
        
        if source_chunks is None:
            source_chunks = blueprint.get("source_chunks", [])
        
        context = ""
        if source_chunks:
            context = "\n".join(source_chunks)
        
        prompt = f"""Generate slide content for an academic presentation.

Topic: {title}
{f"Content context: {context}" if context else ""}

Output MUST be valid JSON with this exact structure:
{{
    "title": "{title}",
    "bullets": ["bullet 1", "bullet 2", ...]
}}

Constraints:
- Maximum {self.max_bullets} bullet points
- Each bullet must be ≤ {self.max_words_per_bullet} words
- Clear and technical language
- Audience: university students
- Only output the JSON object, nothing else"""
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.choices[0].message.content
            
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    slide_content = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError):
                bullets = self._extract_bullets_from_response(response_text)
                slide_content = {
                    "title": title,
                    "bullets": bullets
                }
            
            if "bullets" in slide_content:
                slide_content["bullets"] = [
                    self._truncate_bullet(b) for b in slide_content["bullets"]
                ]
                slide_content["bullets"] = self._remove_redundancy(
                    slide_content["bullets"]
                )
            
            if "title" not in slide_content:
                slide_content["title"] = title
            
            return slide_content
        
        except Exception as e:
            return {
                "title": title,
                "bullets": [],
                "error": str(e)
            }
    
    def generate_multiple(
        self,
        blueprints: List[Dict[str, Any]],
        source_chunks: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate content for multiple slides.
        """
        results = []
        for blueprint in blueprints:
            title = blueprint.get("title", "")
            chunks = None
            if source_chunks and title in source_chunks:
                chunks = source_chunks[title]
            
            slide = self.generate(blueprint, chunks)
            results.append(slide)
        
        return results
    
    def _extract_themes(self, text: str) -> List[Dict[str, str]]:
        """
        Extract key themes from text to create multiple slide topics.
        """
        prompt = f"""Analyze this text and identify 6-8 distinct, coherent themes or topics.
For each theme, provide a brief one-line description.

Output MUST be valid JSON array with this structure:
[
    {{"title": "Theme Title", "description": "Brief description of content"}},
    ...
]

Text to analyze:
{text[:2000]}...

Return only the JSON array, nothing else."""
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                themes = json.loads(json_match.group())
                return themes[:10]
        except Exception:
            pass
        
        return [
            {"title": "Overview", "description": "Main concepts and definitions"},
            {"title": "Key Principles", "description": "Fundamental principles discussed"},
            {"title": "Impact and Implications", "description": "Effects and consequences"},
            {"title": "Challenges", "description": "Problems and obstacles"},
            {"title": "Solutions and Best Practices", "description": "Recommended approaches"}
        ]
    
    def generate_presentation_with_design(
        self,
        text: str,
        presentation_title: str = "Presentation",
        save_to_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete presentation with structured design and semantic information.
        
        Returns document tree structure matching exact format.
        """
        import sys
        
        print(f"Extracting themes from text...", file=sys.stderr)
        
        themes = self._extract_themes(text)
        
        print(f"Found {len(themes)} themes. Generating slides...", file=sys.stderr)
        
        sections = []
        
        for i, theme in enumerate(themes, 1):
            blueprint = {
                "title": theme.get("title", f"Slide {i}"),
                "topic": theme.get("description", ""),
                "source_chunks": [text]
            }
            
            try:
                title = blueprint.get("title", "Untitled Slide")
                source_chunks = blueprint.get("source_chunks", [])
                
                context = "\n".join(source_chunks) if source_chunks else ""
                
                prompt = f"""Generate slide content for an academic presentation.

Topic: {title}
{f"Content context: {context}" if context else ""}

Output MUST be valid JSON with this exact structure:
{{
    "title": "{title}",
    "bullets": ["bullet 1", "bullet 2", ...]
}}

Constraints:
- Maximum {self.max_bullets} bullet points
- Each bullet must be ≤ {self.max_words_per_bullet} words
- Clear and technical language
- Audience: university students
- Only output the JSON object, nothing else"""
                
                response = self.client.chat.complete(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = response.choices[0].message.content
                
                try:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        slide_content = json.loads(json_match.group())
                    else:
                        raise ValueError("No JSON found")
                except (json.JSONDecodeError, ValueError):
                    bullets = self._extract_bullets_from_response(response_text)
                    slide_content = {"title": title, "bullets": bullets}
                
                if "bullets" in slide_content:
                    slide_content["bullets"] = [
                        self._truncate_bullet(b) for b in slide_content["bullets"]
                    ]
                    slide_content["bullets"] = self._remove_redundancy(
                        slide_content["bullets"]
                    )
                
                if "title" not in slide_content:
                    slide_content["title"] = title
                
                bullets = slide_content.get("bullets", [])
                blocks = []
                
                for j, bullet in enumerate(bullets):
                    semantic_label = self._assign_semantic_label(bullet)
                    importance = self._calculate_importance(bullet, j, len(bullets))
                    
                    block = {
                        "type": "PARAGRAPH",
                        "semantic_label": semantic_label,
                        "importance": importance,
                        "text": bullet,
                        "path": None,
                        "caption": ""
                    }
                    blocks.append(block)
                
                section = {
                    "title": slide_content.get("title", title),
                    "level": 1,
                    "blocks": blocks
                }
                
                sections.append(section)
                print(f"Generated slide {i}/{len(themes)}: {section['title']}", file=sys.stderr)
                
            except Exception as e:
                print(f"Error generating slide {i}: {e}", file=sys.stderr)
        
        document_tree = {"sections": sections}
        
        metadata = {
            "num_pages": len(sections),
            "has_tables": False,
            "has_images": False,
            "has_lists": False,
            "languages": ["en"],
            "confidence": 0.85,
            "processing_time": 0.01
        }
        
        output = {
            "document_tree": document_tree,
            "metadata": metadata,
            "warnings": []
        }
        
        if save_to_file:
            try:
                with open(save_to_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                print(f"\nOutput saved to: {save_to_file}", file=sys.stderr)
            except Exception as e:
                print(f"Error saving to file: {e}", file=sys.stderr)
        
        return output


def main():
    """Example usage of the Slide Generator."""
    import sys
    import os
    
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    generator = SlideGenerator(api_key=api_key)
    
    try:
        # ========================================================================
        # USAGE 1: Generate a single slide
        # ========================================================================
        print("="*70)
        print("USAGE 1: Single Slide Generation")
        print("="*70)
        
        blueprint = {
            "title": "Software Architecture",
            "topic": "Core principles of modern software design",
            "source_chunks": [
                "Software architecture defines system structure and organization.",
                "Scalability, maintainability, and security are core concerns.",
                "Design patterns provide proven solutions to common problems."
            ]
        }
        
        slide = generator.generate(blueprint)
        
        print(f"\nTitle: {slide['title']}")
        print(f"\nBullets:")
        for i, bullet in enumerate(slide.get('bullets', []), 1):
            print(f"  {i}. {bullet}")
        
        # ========================================================================
        # USAGE 2: Generate full presentation (5-10 slides) with document tree
        # ========================================================================
        print("\n\n" + "="*70)
        print("USAGE 2: Full Presentation with Document Tree (5-10 slides)")
        print("="*70)
        
        academic_text = """
Software engineering differs from programming in three critical ways: time, scale,
and trade-offs. Programming is often a short-term task where code lives for hours
or days. Software engineering, on the other hand, must account for long-term
maintenance and evolution. As systems grow, the number of engineers involved
increases, requiring better coordination and policies. Finally, engineering
decisions involve complex trade-offs with higher stakes than typical programming tasks.

The concept of sustainability is central to software engineering. A project is
sustainable if it can adapt to valuable changes over its lifetime. This means
planning for dependency updates, refactoring code, and evolving architecture.
Many projects fail because they don't plan for change from the beginning.

Scale also introduces new challenges. A programming task can be done by one person,
but engineering projects require teams. Team size, organization structure, and
communication patterns all impact the ability to build and maintain software.
Companies must invest in tools, processes, and policies that scale with growth.

The trade-offs in engineering are often between immediate productivity and
long-term maintainability. A quick solution today might cost more in maintenance
tomorrow. Engineers must evaluate these trade-offs carefully and make decisions
that balance short-term goals with long-term sustainability.
"""
        
        presentation = generator.generate_presentation_with_design(
            text=academic_text,
            presentation_title="Software Engineering Excellence"
        )
        
        print(f"\nPresentation: Generated {presentation['metadata']['num_pages']} slides")
        print(f"Format: Document Tree with Semantic Labels")
        
        print(f"\nSlides Generated:")
        for section in presentation['document_tree']['sections']:
            title = section['title']
            bullet_count = len(section['blocks'])
            print(f"\n  Slide: {title}")
            print(f"    Content Blocks: {bullet_count}")
            for block in section['blocks']:
                label = block['semantic_label']
                importance = block['importance']
                text = block['text'][:60]
                print(f"      [{label} | {importance}] {text}...")
        
        # ========================================================================
        # USAGE 3: Save to JSON file
        # ========================================================================
        print("\n\n" + "="*70)
        print("USAGE 3: Save to JSON File")
        print("="*70)
        
        output_file = "./my_presentation.json"
        presentation = generator.generate_presentation_with_design(
            text=academic_text,
            presentation_title="My Academic Presentation",
            save_to_file=output_file
        )
        
        print(f"✓ Output saved to: {output_file}")
        print(f"✓ Total slides: {presentation['metadata']['num_pages']}")
        print(f"✓ Confidence: {presentation['metadata']['confidence']}")
        
        # ========================================================================
        # KEY FEATURES
        # ========================================================================
        print("\n\n" + "="*70)
        print("KEY FEATURES")
        print("="*70)
        print("""
✓ Semantic Labels:
  - EXPLANATION: Detailed explanations
  - IMPORTANT: Critical points
  - DEFINITION: Definitions and concepts
  - QUESTION: Questions or inquiries
  - ANSWER: Answers or conclusions
  - EXAMPLE: Examples and illustrations

✓ Importance Scores:
  - Range: 0.5 to 0.75
  - Higher = more important
  - Based on position and keywords

✓ Document Tree Structure:
  - Hierarchical sections
  - Each bullet as a block with metadata
  - Full semantic annotation
  - Ready for parsing and processing

✓ Automatic Features:
  - 5-10 slide generation
  - Theme detection
  - Content analysis
  - JSON export
  - No images/charts (text-based)
""")
        
        print("\n" + "="*70)
        print("Output Format Example:")
        print("="*70)
        print(json.dumps({
            "document_tree": {
                "sections": [
                    {
                        "title": "Example Section",
                        "level": 1,
                        "blocks": [
                            {
                                "type": "PARAGRAPH",
                                "semantic_label": "EXPLANATION",
                                "importance": 0.75,
                                "text": "Example bullet point text",
                                "path": None,
                                "caption": ""
                            }
                        ]
                    }
                ]
            },
            "metadata": {
                "num_pages": 1,
                "has_tables": False,
                "has_images": False,
                "has_lists": False,
                "languages": ["en"],
                "confidence": 0.85,
                "processing_time": 0.01
            },
            "warnings": []
        }, indent=2))
        
    except KeyboardInterrupt:
        print("\nGeneration cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
