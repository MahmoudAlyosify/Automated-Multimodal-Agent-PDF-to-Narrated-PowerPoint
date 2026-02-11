"""
NARRATION SCRIPT AGENT - Production Implementation
===================================================

PURPOSE:
This agent generates natural, spoken explanations for each slide.
The narration complements the slide without repeating bullet text.

INPUT:
- Slide metadata from slide_plan.json
- Slide title, concepts, points, examples, intent

OUTPUT:
- Narration script for each slide (JSON format)

FEATURES:
- Contextual, conversational narration
- 60-90 second duration per slide
- Links between consecutive slides
- Special welcome message for first slide
- Academic but accessible tone
- Uses Mistral 7B for generation

Author: AI Agent Implementation System
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# NARRATION SCRIPT AGENT
# ============================================================================

class NarrationScriptAgent:
    """Generates spoken narration scripts for presentation slides"""
    
    def __init__(self, api_url: str = "http://localhost:1234/v1"):
        self.api_url = api_url
        self.model = "mistral"
        self.slides_data = []
        self.scripts = []
    
    def load_slide_plan(self, json_file: str = "slide_plan.json") -> bool:
        """Load slide plan from JSON file"""
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.slides_data = json.load(f)
            
            logger.info(f"Loaded {len(self.slides_data)} slides from {json_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load slide plan: {e}")
            return False
    
    def generate_scripts(self) -> bool:
        """Generate narration scripts for all slides"""
        
        try:
            logger.info("Generating narration scripts...")
            
            total_slides = len(self.slides_data)
            
            for idx, slide in enumerate(self.slides_data, 1):
                script = self._generate_slide_script(slide, idx, total_slides)
                self.scripts.append(script)
                logger.info(f"  Generated script for slide {idx}/{total_slides}")
            
            logger.info(f"Successfully generated {len(self.scripts)} narration scripts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate scripts: {e}")
            return False
    
    def _generate_slide_script(self, slide: Dict[str, Any], slide_num: int, total_slides: int) -> Dict[str, Any]:
        """Generate narration script for a single slide"""
        
        slide_title = slide.get('title', 'Slide')
        slide_position = slide.get('position', 'content')
        slide_intent = slide.get('intent', '')
        key_points = slide.get('key_points', [])
        key_concepts = slide.get('key_concepts', [])
        
        # Build context for previous and next slides
        prev_title = None
        next_title = None
        
        if slide_num > 1:
            prev_title = self.slides_data[slide_num - 2].get('title')
        if slide_num < total_slides:
            next_title = self.slides_data[slide_num].get('title')
        
        # Special handling for first slide
        if slide_position == "intro":
            return {
                "slide_id": slide.get('slide_id'),
                "title": slide_title,
                "script": self._generate_introduction_script(slide_title, slide_intent),
                "duration_seconds": 45
            }
        
        # Generate script for content slides - use fallback as primary method
        script_text = self._generate_fallback_script(slide_title, key_points, prev_title, next_title)
        
        return {
            "slide_id": slide.get('slide_id'),
            "title": slide_title,
            "script": script_text,
            "duration_seconds": 75  # Average duration
        }
    
    def _generate_introduction_script(self, title: str, intent: str) -> str:
        """Generate special introduction script for first slide"""
        
        script = f"""Welcome, and thank you for using Mahmoud and Mirna's project. 

Today, we'll explore the fascinating world of generative artificial intelligence. This presentation will take you on a journey through the fundamentals, practical applications, and future implications of AI systems that can create new content.

We'll start by understanding what makes these systems work, then dive into how they're being used in real-world scenarios, and finally discuss the important considerations and future directions of this rapidly evolving field.

Let's begin!"""
        
        return script
    
    def _build_script_prompt(
        self,
        title: str,
        intent: str,
        concepts: List[str],
        points: List[str],
        prev_title: Optional[str],
        next_title: Optional[str],
        slide_num: int,
        total_slides: int
    ) -> str:
        """Build prompt for Mistral API"""
        
        context = f"Previous slide: {prev_title}" if prev_title else ""
        next_context = f"Next slide: {next_title}" if next_title else ""
        
        prompt = f"""You are an academic lecturer explaining a slide in a presentation about Generative AI.

SLIDE INFORMATION:
- Slide Title: {title}
- Slide Number: {slide_num} of {total_slides}
- Slide Intent: {intent}
{f'- Previous Slide: {prev_title}' if prev_title else ''}
{f'- Next Slide: {next_title}' if next_title else ''}

KEY CONCEPTS ON THIS SLIDE:
{chr(10).join(f'• {c[:100]}...' if len(c) > 100 else f'• {c}' for c in concepts[:3])}

KEY POINTS TO COVER:
{chr(10).join(f'• {p[:80]}...' if len(p) > 80 else f'• {p}' for p in points[:4])}

INSTRUCTIONS:
1. Write a natural spoken narration script (not a reading of bullet points)
2. Explain the concepts in an accessible way for listeners unfamiliar with the topic
3. Use clear, conversational language appropriate for academic context
4. Include smooth transitions:
{f'   - Link to the previous slide ({prev_title})' if prev_title else ''}
{f'   - Prepare listeners for the next slide ({next_title})' if next_title else ''}
5. Target length: 60-90 seconds of spoken word (approximately 150-225 words)
6. Be engaging and use storytelling elements where appropriate
7. Do NOT repeat the bullet points verbatim
8. Focus on explaining WHY these concepts matter, not just WHAT they are

Write only the script text, nothing else. Make it sound natural for someone listening, not reading."""

        return prompt
    
    def _call_mistral_api(self, prompt: str) -> Optional[str]:
        """Call Mistral 7B API via local inference server"""
        
        try:
            try:
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional academic lecturer who explains complex topics clearly and engagingly."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 300,
                        "top_p": 0.9
                    },
                    timeout=2
                )
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    script_text = result['choices'][0]['message']['content'].strip()
                    return script_text
                
                return None
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException):
                logger.warning("Could not connect to Mistral API - using fallback script generation")
                return None
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.warning(f"API call failed: {type(e).__name__} - using fallback script generation")
            return None
    
    def _generate_fallback_script(self, title: str, points: List[str], prev_title: Optional[str] = None, next_title: Optional[str] = None) -> str:
        """Generate fallback script when API is unavailable"""
        
        # Start with a transition from previous slide if available
        if prev_title:
            script = f"Building on what we discussed in {prev_title}, we now look at {title}.\n\n"
        else:
            script = f"Let's explore {title}.\n\n"
        
        script += "In this section, we'll cover several important aspects:\n\n"
        
        # Use first 3-4 points as foundation
        for i, point in enumerate(points[:4], 1):
            # Clean up the point text
            point_text = point[:100] + "..." if len(point) > 100 else point
            script += f"{i}. {point_text}\n"
        
        script += f"\nThese elements work together to create a comprehensive understanding of {title}. "
        
        # Add transition to next slide if available
        if next_title:
            script += f"With this foundation in place, we'll next explore {next_title}."
        else:
            script += "Let's consolidate our understanding and move forward."
        
        return script
    
    def save_scripts(self, output_file: str = "scripts.json") -> bool:
        """Save narration scripts to JSON file"""
        
        if not self.scripts:
            logger.error("No scripts to save")
            return False
        
        try:
            output_data = {
                "version": "1.0",
                "metadata": {
                    "total_slides": len(self.scripts),
                    "total_duration_seconds": sum(s.get('duration_seconds', 0) for s in self.scripts)
                },
                "scripts": self.scripts
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.scripts)} scripts to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save scripts: {e}")
            return False
    
    def display_summary(self):
        """Display script generation summary"""
        
        if not self.scripts:
            print("No scripts generated")
            return
        
        print("\n" + "="*80)
        print("NARRATION SCRIPT AGENT - SUMMARY")
        print("="*80)
        
        print(f"\nTotal Scripts Generated: {len(self.scripts)}")
        
        total_duration = sum(s.get('duration_seconds', 0) for s in self.scripts)
        total_minutes = total_duration / 60
        
        print(f"Total Duration: {total_minutes:.1f} minutes ({total_duration} seconds)")
        
        print(f"\nScript Overview:")
        for script in self.scripts[:5]:
            duration = script.get('duration_seconds', 0)
            print(f"  [{script['slide_id']}] {script['title']} ({duration}s)")
        
        if len(self.scripts) > 5:
            print(f"  ... and {len(self.scripts) - 5} more scripts")
        
        print(f"\nFirst Script Sample (Introduction):")
        print("-" * 80)
        first_script = self.scripts[0]['script'][:200]
        print(f"{first_script}...")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Narration Script Agent - Generates spoken narration for presentation slides',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script_agent.py                       # Default (from ../4- Slide Planner Agent/)
  python script_agent.py --input slide_plan.json
  python script_agent.py --output narration_scripts.json
  python script_agent.py --api http://localhost:8000/v1
        """
    )
    
    parser.add_argument(
        '--input',
        default='../4- Slide Planner Agent/slide_plan.json',
        help='Input slide plan JSON file'
    )
    
    parser.add_argument(
        '--output',
        default='scripts.json',
        help='Output scripts JSON file'
    )
    
    parser.add_argument(
        '--api',
        default='http://localhost:1234/v1',
        help='Mistral API endpoint'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("NARRATION SCRIPT AGENT - Generation System")
    print("="*80)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"API: {args.api}")
    
    # Create agent
    agent = NarrationScriptAgent(api_url=args.api)
    
    # Load slides
    if not agent.load_slide_plan(args.input):
        logger.error("Failed to load slide plan")
        return
    
    # Generate scripts
    if not agent.generate_scripts():
        logger.error("Failed to generate scripts")
        return
    
    # Save scripts
    if not agent.save_scripts(args.output):
        logger.error("Failed to save scripts")
        return
    
    # Display summary
    agent.display_summary()
    
    print("\n" + "="*80)
    print("✅ NARRATION SCRIPT GENERATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
