"""
SLIDE PLANNER AGENT - Production Implementation
==============================================

PURPOSE:
This agent performs high-level reasoning and planning.
It transforms retrieved knowledge into a structured presentation plan.
This is the primary "thinking" agent in the system.

INPUT:
- Retrieved semantic chunks from Vector Store
- Constraints: Target slide count (5-10), Educational lecture format

OUTPUT:
Slide blueprint defining intent and structure for each slide.

OUTPUT SCHEMA:
{
  "slide_id": 3,
  "title": "System Architecture",
  "intent": "Explain the overall workflow",
  "source_chunks": [4, 9, 12],
  "key_concepts": ["Workflow", "Architecture"],
  "content_summary": "Overview of how components interact"
}

IMPLEMENTATION: Mistral 7B with optimized two-stage planning
Author: AI Agent Implementation System
"""

import json
import requests
import re
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Global configuration for Slide Planner Agent"""
    MISTRAL_API_KEY = "WoLxsdeJgRskhI0PCpI1ndGstBl7mzuo"
    MISTRAL_MODEL = "mistral-large-latest"
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_SLIDES = 13  # Increased for richer content (was 9)
    API_TIMEOUT = 180
    RATE_LIMIT_DELAY = 0.2  # Reduced for faster execution
    RICH_MODE = True  # Generate rich, detailed content for studying


# ============================================================================
# CORE API HANDLER
# ============================================================================

class MistralAPI:
    """Handles all Mistral API communication"""
    
    @staticmethod
    def call(prompt: str, system_prompt: str = "", temperature: float = 0.3,
             max_tokens: int = 2000) -> Optional[str]:
        """Make a safe Mistral API call with error handling"""
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": Config.MISTRAL_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                Config.API_URL,
                headers=headers,
                json=payload,
                timeout=Config.API_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            logger.error("API timeout - retrying...")
            time.sleep(1)
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to Mistral API")
            return None
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            return None


# ============================================================================
# JSON EXTRACTION UTILITY
# ============================================================================

class JSONExtractor:
    """Robust JSON extraction with multiple fallback strategies"""
    
    @staticmethod
    def extract(text: str) -> Optional[Any]:
        """Extract JSON from text with graceful degradation"""
        
        if not text:
            return None
        
        # Strategy 1: Direct parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Strategy 2: Remove markdown fences
        try:
            cleaned = re.sub(r'```json\s*', '', text)
            cleaned = re.sub(r'```\s*', '', cleaned)
            return json.loads(cleaned)
        except:
            pass
        
        # Strategy 3: Extract array
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        
        # Strategy 4: Extract object
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        
        return None


# ============================================================================
# CHUNK LOADER
# ============================================================================

class ChunkLoader:
    """Load and preprocess semantic chunks"""
    
    @staticmethod
    def load(filepath: str) -> List[Dict[str, Any]]:
        """Load chunks from metadata file"""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            filtered = []
            for chunk in chunks:
                text = chunk.get('text', '').strip()
                if len(text) > 30:  # Filter out very short chunks
                    filtered.append({
                        'chunk_id': chunk.get('chunk_id', len(filtered)),
                        'text': text,
                        'page': chunk.get('page', 0),
                        'index_id': chunk.get('index_id', len(filtered))
                    })
            
            logger.info(f"Loaded {len(filtered)} chunks from {filepath}")
            return filtered
            
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {filepath}")
            return []


# ============================================================================
# SLIDE PLANNER AGENT
# ============================================================================

class SlidePlannerAgent:
    """
    Main Slide Planner Agent
    Transforms semantic chunks into structured slide blueprints
    """
    
    def __init__(self):
        self.api = MistralAPI()
        self.chunks = []
        self.slides = []
    
    def load_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Load semantic chunks"""
        
        self.chunks = chunks
        logger.info(f"Planner loaded {len(chunks)} chunks")
        return len(chunks) > 0
    
    def plan(self, target_slides: int = 9) -> List[Dict[str, Any]]:
        """
        Main planning method
        Generates slide blueprint
        """
        
        if not self.chunks:
            logger.error("No chunks loaded")
            return []
        
        logger.info(f"Planning {target_slides} slides from {len(self.chunks)} chunks...")
        
        # Step 1: Generate slide outline
        outline = self._generate_outline(target_slides)
        if not outline:
            logger.error("Failed to generate outline")
            return self._fallback_plan(target_slides)
        
        logger.info(f"Generated outline with {len(outline)} slides")
        
        # Step 2: Enrich each slide
        slides = self._enrich_slides(outline)
        
        self.slides = slides
        logger.info(f"Planning complete: {len(slides)} slides")
        
        return slides
    
    def _generate_outline(self, num_slides: int) -> Optional[List[Dict]]:
        """Generate high-level slide outline"""
        
        logger.info("Stage 1: Generating outline...")
        
        # Sample chunks for context
        chunk_samples = "\n\n".join([
            f"[{c['chunk_id']}] {c['text'][:200]}..."
            for c in self.chunks[:20]
        ])
        
        system_prompt = f"""You are a presentation structure expert.
Your task is to design a {num_slides}-slide lecture outline for RICH, DETAILED study material.

Rules:
- Return ONLY a JSON array
- No markdown, no explanations
- Exactly {num_slides} slides
- Each slide: slide_id, title, position (intro/content/conclusion)
- Create DETAILED content slides (not summary slides)

Format:
[
  {{"slide_id": 1, "title": "...", "position": "intro"}},
  {{"slide_id": 2, "title": "...", "position": "content"}},
  ...
]"""
        
        user_prompt = f"""Create a {num_slides}-slide outline for study material.
Make it DETAILED and RICH in content - suitable for in-depth learning and research.

Content excerpt:
{chunk_samples}

Structure:
- Slide 1: Introduction to topic
- Slides 2-{num_slides-1}: Detailed content sections (break into specific subtopics, examples, applications)
- Slide {num_slides}: Summary & Key Takeaways

Generate MORE slides for RICHER content. Each slide should cover ONE specific topic in depth.
Return ONLY the JSON array."""
        
        try:
            response = self.api.call(
                user_prompt,
                system_prompt,
                temperature=0.2,
                max_tokens=1000
            )
            
            if not response:
                return None
            
            outline = JSONExtractor.extract(response)
            
            if isinstance(outline, list) and len(outline) >= num_slides - 2:
                return outline[:num_slides]
            
            return None
            
        except Exception as e:
            logger.error(f"Outline generation failed: {e}")
            return None
    
    def _enrich_slides(self, outline: List[Dict]) -> List[Dict[str, Any]]:
        """Enrich each slide with content details"""
        
        logger.info("Stage 2: Enriching slides...")
        
        enriched_slides = []
        
        for i, slide in enumerate(outline, 1):
            logger.info(f"  Enriching slide {i}/{len(outline)}...")
            enriched = self._create_slide(slide)
            enriched_slides.append(enriched)
            time.sleep(Config.RATE_LIMIT_DELAY)
        
        return enriched_slides
    
    def _create_slide(self, basic_slide: Dict) -> Dict[str, Any]:
        """Create a detailed slide from basic slide - Extract REAL content from chunks"""
        
        # Find relevant chunks (more for rich content)
        relevant_chunks = self._find_relevant_chunks(basic_slide['title'], k=8)  # Increased from 5
        
        # Build rich chunk context with clear separation
        chunk_context = "SOURCE MATERIAL FROM PDF:\n"
        chunk_context += "-" * 50 + "\n"
        for idx, c in enumerate(relevant_chunks, 1):
            chunk_context += f"[Chunk {idx}] {c['text']}\n"
            chunk_context += "-" * 50 + "\n"
        
        system_prompt = """Your role is to CREATE STUDY MATERIAL by extracting and narratively presenting content from provided PDF source material.

CRITICAL RULES:
1. Extract content DIRECTLY from the source material - do NOT generate or fabricate content
2. Write in beautiful, clear narrative style - not bullet points or lists
3. Key concepts should be actual terms/ideas from the source
4. Key points should be actual statements/claims from the source
5. Examples should reference source material
6. If information is not in source, say so

Return ONLY valid JSON:
{
  "intent": "Clear learning objective (2-3 sentences describing what learner should master)",
  "key_concepts": ["Actual concept from source", "Another real concept", ...],
  "key_points": ["Actual key point extracted from source", "Another real point", ...],
  "examples": ["Real example or case from source material"]
}"""
        
        user_prompt = f"""Create RICH STUDY MATERIAL for this slide by extracting from provided source material.

SLIDE TITLE: {basic_slide['title']}

{chunk_context}

TASK:
1. Read the source material carefully
2. Extract the 5 most important concepts mentioned
3. Extract 5 key points/claims/findings from the source
4. Find 2-3 good examples or applications mentioned in the source
5. Write a 2-3 sentence learning intent based on what the source teaches

IMPORTANT:
- ALL content must come from the source material
- Write concepts and points in natural, flowing language (not telegraphic)
- Make it suitable for studying and learning
- Include depth and detail from the source
- Be specific and detailed, not generic

Return the JSON object with extracted, real content."""
        
        try:
            response = self.api.call(
                user_prompt,
                system_prompt,
                temperature=0.3,
                max_tokens=1200
            )
            
            if not response:
                enrichment = {}
            else:
                enrichment = JSONExtractor.extract(response) or {}
            
            if isinstance(enrichment, list):
                enrichment = enrichment[0] if enrichment else {}
            
            # Combine basic slide with enrichment
            slide = {
                "slide_id": basic_slide.get('slide_id', 1),
                "title": basic_slide.get('title', 'Slide'),
                "position": basic_slide.get('position', 'content'),
                "intent": enrichment.get('intent', 'Core concept explanation'),
                "key_concepts": enrichment.get('key_concepts', []),
                "key_points": enrichment.get('key_points', []),
                "examples": enrichment.get('examples', []),
                "source_chunks": [c['chunk_id'] for c in relevant_chunks],
                "content_summary": enrichment.get('intent', '')
            }
            
            return slide
            
        except Exception as e:
            logger.error(f"Slide enrichment failed: {e}")
            return {
                "slide_id": basic_slide.get('slide_id', 1),
                "title": basic_slide.get('title', 'Slide'),
                "position": basic_slide.get('position', 'content'),
                "intent": "",
                "key_concepts": [],
                "key_points": [],
                "examples": [],
                "source_chunks": [],
                "content_summary": ""
            }
    
    def _find_relevant_chunks(self, title: str, k: int = 5) -> List[Dict]:
        """Find chunks relevant to slide title"""
        
        # Simple keyword-based matching (could be improved with actual similarity)
        keywords = title.lower().split()
        
        scored_chunks = []
        for chunk in self.chunks:
            chunk_text = chunk.get('text', '').lower()
            score = sum(1 for kw in keywords if kw in chunk_text and len(kw) > 2)
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top-k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        relevant = [c[0] for c in scored_chunks[:k]]
        
        # Fallback to first chunks if no keyword matches
        if not relevant:
            relevant = self.chunks[:k]
        
        return relevant
    
    def _fallback_plan(self, num_slides: int) -> List[Dict[str, Any]]:
        """Generate fallback plan by extracting REAL content from chunks"""
        
        logger.warning("Extracting content from PDF chunks for slides...")
        
        slides = []
        
        # Enhanced structure with more detailed slides
        structure = [
            ("Introduction", "Overview and context of the topic", "intro"),
            ("Fundamentals - Part 1", "Core concepts and foundational terminology", "content"),
            ("Fundamentals - Part 2", "Essential principles and frameworks", "content"),
            ("Theory and Background", "Historical context and theoretical foundations", "content"),
            ("Key Principles", "Main principles and guidelines", "content"),
            ("Implementation Methods", "Practical approaches and methodologies", "content"),
            ("Advanced Techniques", "Advanced implementations and optimizations", "content"),
            ("Real-World Applications", "Case studies and practical examples", "content"),
            ("Applications Continued", "More application examples and use cases", "content"),
            ("Best Practices", "Recommended practices and common pitfalls", "content"),
            ("Limitations and Challenges", "Constraints, limitations, and solutions", "content"),
            ("Future Developments", "Emerging trends and research directions", "content"),
            ("Conclusion", "Summary, key takeaways, and next steps", "conclusion"),
        ]
        
        for i in range(1, num_slides + 1):
            if i - 1 < len(structure):
                title, intent_guide, position = structure[i - 1]
            else:
                title = f"Advanced Topic {i - len(structure)}"
                intent_guide = "Detailed exploration of specialized concepts"
                position = "content"
            
            # Find relevant chunks for this slide
            related_chunks = self._find_relevant_chunks(title, k=8)
            
            # Extract real content from chunks
            concepts = self._extract_real_concepts(related_chunks, title)
            key_points = self._extract_real_points(related_chunks, title)
            intent = self._build_narrative_intent(related_chunks, intent_guide, title)
            examples = self._extract_real_examples(related_chunks)
            
            slides.append({
                "slide_id": i,
                "title": title,
                "position": position,
                "intent": intent,
                "key_concepts": concepts,
                "key_points": key_points,
                "examples": examples,
                "source_chunks": [c.get('chunk_id') for c in related_chunks],
                "content_summary": intent
            })
        
        return slides[:num_slides]
    
    def _extract_real_concepts(self, chunks: List[Dict], title: str) -> List[str]:
        """Extract real key concepts from PDF chunks"""
        concepts = []
        
        for chunk in chunks[:5]:
            text = chunk.get('text', '')
            if text:
                # Extract sentences and find meaningful phrases
                sentences = text.split('.')
                for sent in sentences[:3]:
                    sent = sent.strip()
                    if len(sent) > 20 and len(concepts) < 5:
                        # Clean and shorten the sentence
                        concept = sent[:90]
                        if concept and concept not in concepts:
                            concepts.append(concept)
                            break
        
        # Fill gaps if needed
        while len(concepts) < 5:
            concepts.append(f"Key aspect of {title}")
        
        return concepts[:5]
    
    def _extract_real_points(self, chunks: List[Dict], title: str) -> List[str]:
        """Extract real key points from PDF chunks with detail"""
        points = []
        
        for chunk in chunks:
            text = chunk.get('text', '')
            if text:
                sentences = text.split('.')
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 25 and len(points) < 5:
                        # Keep more detail - up to 160 chars
                        point = sent[:160] if len(sent) > 160 else sent
                        if point and point not in points:
                            points.append(point)
        
        # Fill gaps with meaningful content
        while len(points) < 5:
            points.append(f"Important aspect of {title}")
        
        return points[:5]
    
    def _extract_real_examples(self, chunks: List[Dict]) -> List[str]:
        """Extract real examples from chunks"""
        examples = []
        
        # Look for example-indicating keywords
        example_keywords = ['example', 'such as', 'for instance', 'like', 'case', 'scenario', 'application']
        
        for chunk in chunks:
            text = chunk.get('text', '')
            text_lower = text.lower()
            
            # Check if chunk contains example indicators
            if any(kw in text_lower for kw in example_keywords):
                # Extract first sentence mentioning example
                for sent in text.split('.'):
                    sent = sent.strip()
                    if len(sent) > 30 and any(kw in sent.lower() for kw in example_keywords):
                        example = sent[:150]
                        if example and example not in examples:
                            examples.append(example)
                            break
            
            if len(examples) >= 2:
                break
        
        # Fallback: use meaningful chunk excerpts as examples
        if len(examples) < 2:
            for chunk in chunks:
                text = chunk.get('text', '')
                if text and len(text) > 60:
                    example = text[:150]
                    if example and example not in examples:
                        examples.append(example)
                    if len(examples) >= 2:
                        break
        
        return examples[:3] if examples else ["Relevant example from source material"]
    
    def _build_narrative_intent(self, chunks: List[Dict], guide: str, title: str) -> str:
        """Build a narrative learning intent from actual chunk content"""
        
        # Extract meaningful content from first chunk
        if chunks:
            first_chunk = chunks[0].get('text', '')
            if first_chunk:
                sentences = first_chunk.split('.')
                # Get first 1-2 sentences for context
                narrative = sentences[0].strip()
                if len(narrative) > 60:
                    # Add guide intent
                    intent = f"{guide}. {narrative[:120]}..."
                    return intent
        
        # Fallback
        return f"{guide} about {title}"
    
    def save_plan(self, output_path: str) -> bool:
        """Save slide plan to JSON file"""
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.slides, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.slides)} slides to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
            return False
    
    def display_summary(self):
        """Display slide plan summary"""
        
        print("\n" + "="*80)
        print("SLIDE PLAN SUMMARY")
        print("="*80)
        
        for slide in self.slides:
            print(f"\n[{slide['slide_id']}] {slide['title']}")
            print(f"  Position: {slide.get('position', 'content')}")
            if slide.get('intent'):
                print(f"  Intent: {slide['intent'][:70]}...")
            if slide.get('key_concepts'):
                concepts = ", ".join(slide['key_concepts'][:3])
                print(f"  Concepts: {concepts}")
            if slide.get('source_chunks'):
                chunks = ", ".join(map(str, slide['source_chunks'][:3]))
                print(f"  Source chunks: {chunks}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='Slide Planner Agent - Transforms chunks into structured slide plans',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python slide_planner_agent.py                    # Default
  python slide_planner_agent.py --input chunks.json --slides 7
  python slide_planner_agent.py --output-dir ./output
  python slide_planner_agent.py --demo              # Generate demo output
        """
    )
    
    parser.add_argument(
        '--input',
        default='chunks_metadata.json',
        help='Input chunks file (default: chunks_metadata.json)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '--output',
        default='slide_plan.json',
        help='Output file name (default: slide_plan.json)'
    )
    
    parser.add_argument(
        '--slides',
        type=int,
        default=13,
        help='Number of slides (default: 13, range: 5-20 for rich content)'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Generate demo output without API calls'
    )
    
    args = parser.parse_args()
    
    # Validate slides count
    if args.slides < 5 or args.slides > 20:
        logger.error("Slide count must be between 5 and 20")
        return
    
    print("\n" + "="*80)
    print("SLIDE PLANNER AGENT - Production Implementation")
    print("="*80)
    print(f"Input: {args.input}")
    print(f"Target slides: {args.slides}")
    print(f"Output: {args.output_dir}/{args.output}")
    if args.demo:
        print("Mode: DEMO (No API calls)")
    
    # Load chunks
    chunks = ChunkLoader.load(args.input)
    if not chunks:
        logger.error("Failed to load chunks")
        return
    
    # Create and run planner
    planner = SlidePlannerAgent()
    planner.load_chunks(chunks)
    
    # Use demo mode or API-based planning
    if args.demo:
        slides = planner._fallback_plan(args.slides)
        logger.info("Generated demo slide plan")
    else:
        try:
            slides = planner.plan(args.slides)
        except KeyboardInterrupt:
            logger.warning("Planning interrupted, using fallback...")
            slides = planner._fallback_plan(args.slides)
        except Exception as e:
            logger.warning(f"Planning failed ({e}), using fallback...")
            slides = planner._fallback_plan(args.slides)
    
    if not slides:
        logger.error("Failed to generate slide plan")
        return
    
    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / args.output
    planner.slides = slides
    planner.save_plan(str(output_path))
    
    # Display summary
    planner.display_summary()
    
    print("\n" + "="*80)
    print("✅ SLIDE PLANNING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
