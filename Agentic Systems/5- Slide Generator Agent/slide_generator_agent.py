"""
SLIDE GENERATOR AGENT - Advanced PPT Designer
==============================================

PURPOSE:
Converts slide blueprints from Slide Planner Agent into
professional PPT-ready JSON with advanced design features.

INPUT:
- Slide blueprint JSON from Slide Planner Agent (slide_plan.json)

OUTPUT:
Complete presentation JSON with:
- Smart gradients and backgrounds
- Professional color themes
- Advanced typography
- Transitions and animations
- Shadows and effects
- SmartArt and grouped elements
- Icons and shapes

DESIGN PHILOSOPHY:
- Modern, clean aesthetic
- Professional color harmonies
- Optimal readability
- Visual hierarchy and balance
- Academic credibility

Author: AI Agent Implementation System
"""

import json
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
# DESIGN CONFIGURATION
# ============================================================================

class DesignConfig:
    """Professional PPT design configuration"""
    
    # Slide dimensions
    SLIDE_WIDTH = 1280
    SLIDE_HEIGHT = 720
    UNIT = "px"
    
    # Color themes (professional)
    THEME_COLORS = {
        "primary": "#3B82F6",      # Blue
        "secondary": "#10B981",    # Green
        "accent": "#F59E0B",       # Amber
        "danger": "#EF4444",       # Red
        "light_bg": "#f7fafc",     # Light gray
        "dark_text": "#1f2937",    # Dark gray
        "white": "#ffffff"         # White
    }
    
    # Fonts
    FONTS = {
        "heading": "Microsoft YaHei",
        "body": "Arial"
    }


# ============================================================================
# SLIDE GENERATOR AGENT - ADVANCED
# ============================================================================

class SlideGeneratorAgent:
    """Generates professional PPT presentations from slide blueprints"""
    
    def __init__(self):
        self.slide_plan = []
        self.presentation = None
    
    def load_plan(self, plan_file: str = "slide_plan.json") -> bool:
        """Load slide plan from JSON file"""
        
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                self.slide_plan = json.load(f)
            
            logger.info(f"Loaded {len(self.slide_plan)} slides from {plan_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load slide plan: {e}")
            return False
    
    def generate_presentation(self) -> Dict[str, Any]:
        """Generate complete presentation with advanced design"""
        
        logger.info("Generating advanced PPT presentation...")
        
        self.presentation = {
            "version": "1.0",
            "ppt": {
                "size": {
                    "width": DesignConfig.SLIDE_WIDTH,
                    "height": DesignConfig.SLIDE_HEIGHT,
                    "unit": DesignConfig.UNIT
                },
                "defaultUnit": DesignConfig.UNIT,
                "theme": {
                    "colors": DesignConfig.THEME_COLORS,
                    "fonts": DesignConfig.FONTS
                },
                "slides": []
            }
        }
        
        # Generate slides
        for idx, slide_data in enumerate(self.slide_plan, 1):
            slide = self._generate_slide(slide_data, idx)
            self.presentation["ppt"]["slides"].append(slide)
            logger.info(f"  Generated slide {idx}/{len(self.slide_plan)}")
        
        return self.presentation
    
    def _generate_slide(self, slide_data: Dict, slide_number: int) -> Dict[str, Any]:
        """Generate a single slide with professional design"""
        
        position = slide_data.get('position', 'content')
        title = slide_data.get('title', 'Slide')
        
        if position == "intro":
            return self._design_title_slide(slide_data, slide_number)
        elif position == "conclusion":
            return self._design_conclusion_slide(slide_data, slide_number)
        else:
            return self._design_content_slide(slide_data, slide_number)
    
    def _design_title_slide(self, slide_data: Dict, slide_number: int) -> Dict[str, Any]:
        """Design title/introduction slide with gradient background"""
        
        title = slide_data.get('title', 'Presentation')
        intent = slide_data.get('intent', 'Welcome')
        
        slide = {
            "id": f"slide-{slide_number}",
            "title": title,
            "background": {
                "gradient": {
                    "type": "linear",
                    "angle": 135,
                    "stops": [
                        {"color": "#667eea", "position": 0},
                        {"color": "#764ba2", "position": 100}
                    ]
                }
            },
            "transition": {
                "type": "fade",
                "duration": 0.8
            },
            "elements": []
        }
        
        # Main title with shadow and rotation
        slide["elements"].append({
            "type": "text",
            "text": title,
            "box": {
                "x": 640,
                "y": 180,
                "w": 600,
                "h": 120
            },
            "style": {
                "fontSize": 56,
                "align": "center",
                "color": "#ffffff",
                "bold": True,
                "font": DesignConfig.FONTS["heading"]
            },
            "shadow": {
                "x": 2,
                "y": 2,
                "blur": 5,
                "color": "#00000040"
            },
            "rotation": -1
        })
        
        # Subtitle
        slide["elements"].append({
            "type": "text",
            "text": intent[:100],
            "box": {
                "x": 640,
                "y": 330,
                "w": 600,
                "h": 80
            },
            "style": {
                "fontSize": 28,
                "align": "center",
                "color": "#ffffff",
                "font": DesignConfig.FONTS["body"]
            },
            "shadow": {
                "x": 1,
                "y": 1,
                "blur": 3,
                "color": "#00000030"
            }
        })
        
        # Decorative line
        slide["elements"].append({
            "type": "line",
            "points": [
                {"x": 300, "y": 450},
                {"x": 980, "y": 450}
            ],
            "stroke": "#ffffff",
            "strokeWidth": 2,
            "strokeStyle": "solid"
        })
        
        return slide
    
    def _design_content_slide(self, slide_data: Dict, slide_number: int) -> Dict[str, Any]:
        """Design content slide with professional layout"""
        
        title = slide_data.get('title', 'Slide')
        key_points = slide_data.get('key_points', [])
        key_concepts = slide_data.get('key_concepts', [])
        intent = slide_data.get('intent', '')
        
        slide = {
            "id": f"slide-{slide_number}",
            "title": title,
            "background": {
                "color": "#f7fafc"
            },
            "transition": {
                "type": "slideInRight",
                "duration": 0.6
            },
            "elements": []
        }
        
        # Header background
        slide["elements"].append({
            "type": "shape",
            "shapeType": "rect",
            "box": {
                "x": 0,
                "y": 0,
                "w": DesignConfig.SLIDE_WIDTH,
                "h": 100
            },
            "fill": "#3B82F6",
            "border": None
        })
        
        # Title
        slide["elements"].append({
            "type": "text",
            "text": title,
            "box": {
                "x": 60,
                "y": 20,
                "w": 1160,
                "h": 80
            },
            "style": {
                "fontSize": 44,
                "align": "left",
                "color": "#ffffff",
                "bold": True,
                "font": DesignConfig.FONTS["heading"]
            }
        })
        
        # Intent/subtitle
        if intent:
            slide["elements"].append({
                "type": "text",
                "text": intent[:120],
                "box": {
                    "x": 60,
                    "y": 110,
                    "w": 1160,
                    "h": 40
                },
                "style": {
                    "fontSize": 14,
                    "color": "#10B981",
                    "italic": True,
                    "font": DesignConfig.FONTS["body"]
                }
            })
        
        # Key concepts as tags/badges
        concepts_y = 160
        concepts_x = 60
        for idx, concept in enumerate(key_concepts[:3]):
            if idx > 0 and (idx % 3 == 0):
                concepts_y += 45
                concepts_x = 60
            
            concept_short = concept[:35]
            
            slide["elements"].append({
                "type": "shape",
                "shapeType": "roundRect",
                "box": {
                    "x": concepts_x,
                    "y": concepts_y,
                    "w": 350,
                    "h": 35
                },
                "fill": "#F59E0B",
                "border": {
                    "width": 1,
                    "color": "#F59E0B",
                    "style": "solid"
                }
            })
            
            slide["elements"].append({
                "type": "text",
                "text": concept_short,
                "box": {
                    "x": concepts_x + 15,
                    "y": concepts_y + 5,
                    "w": 320,
                    "h": 25
                },
                "style": {
                    "fontSize": 12,
                    "color": "#ffffff",
                    "bold": True,
                    "align": "left",
                    "font": DesignConfig.FONTS["body"]
                }
            })
            
            concepts_x += 370
        
        # Key points with bullets
        points_y = 260
        for idx, point in enumerate(key_points[:5]):
            point_short = point[:95]
            
            # Bullet marker
            slide["elements"].append({
                "type": "shape",
                "shapeType": "circle",
                "box": {
                    "x": 80,
                    "y": points_y + 5,
                    "w": 8,
                    "h": 8
                },
                "fill": "#10B981"
            })
            
            # Bullet text
            slide["elements"].append({
                "type": "text",
                "text": point_short,
                "box": {
                    "x": 110,
                    "y": points_y,
                    "w": 1100,
                    "h": 35
                },
                "style": {
                    "fontSize": 16,
                    "color": "#1f2937",
                    "align": "left",
                    "font": DesignConfig.FONTS["body"]
                }
            })
            
            points_y += 45
        
        # Bottom accent line
        slide["elements"].append({
            "type": "line",
            "points": [
                {"x": 60, "y": 700},
                {"x": 1220, "y": 700}
            ],
            "stroke": "#10B981",
            "strokeWidth": 3,
            "strokeStyle": "solid"
        })
        
        # Slide number
        slide["elements"].append({
            "type": "text",
            "text": f"{slide_number}",
            "box": {
                "x": 1200,
                "y": 690,
                "w": 60,
                "h": 30
            },
            "style": {
                "fontSize": 16,
                "color": "#3B82F6",
                "align": "right",
                "bold": True,
                "font": DesignConfig.FONTS["body"]
            }
        })
        
        return slide
    
    def _design_conclusion_slide(self, slide_data: Dict, slide_number: int) -> Dict[str, Any]:
        """Design conclusion slide with emphasis"""
        
        title = slide_data.get('title', 'Conclusion')
        key_points = slide_data.get('key_points', [])
        
        slide = {
            "id": f"slide-{slide_number}",
            "title": title,
            "background": {
                "gradient": {
                    "type": "linear",
                    "angle": 45,
                    "stops": [
                        {"color": "#1f2937", "position": 0},
                        {"color": "#111827", "position": 100}
                    ]
                }
            },
            "transition": {
                "type": "fade",
                "duration": 1
            },
            "elements": []
        }
        
        # Accent bar
        slide["elements"].append({
            "type": "shape",
            "shapeType": "rect",
            "box": {
                "x": 0,
                "y": 0,
                "w": 12,
                "h": DesignConfig.SLIDE_HEIGHT
            },
            "fill": "#F59E0B"
        })
        
        # Title
        slide["elements"].append({
            "type": "text",
            "text": title,
            "box": {
                "x": 80,
                "y": 60,
                "w": 1100,
                "h": 100
            },
            "style": {
                "fontSize": 52,
                "align": "left",
                "color": "#F59E0B",
                "bold": True,
                "font": DesignConfig.FONTS["heading"]
            },
            "shadow": {
                "x": 2,
                "y": 2,
                "blur": 4,
                "color": "#00000050"
            }
        })
        
        # Key takeaways
        takeaway_y = 210
        for point in key_points[:4]:
            point_short = point[:90]
            
            slide["elements"].append({
                "type": "text",
                "text": "✓",
                "box": {
                    "x": 80,
                    "y": takeaway_y,
                    "w": 30,
                    "h": 30
                },
                "style": {
                    "fontSize": 24,
                    "color": "#10B981",
                    "bold": True
                }
            })
            
            slide["elements"].append({
                "type": "text",
                "text": point_short,
                "box": {
                    "x": 130,
                    "y": takeaway_y,
                    "w": 1050,
                    "h": 30
                },
                "style": {
                    "fontSize": 16,
                    "color": "#ffffff",
                    "align": "left",
                    "font": DesignConfig.FONTS["body"]
                }
            })
            
            takeaway_y += 50
        
        # Thank you message
        slide["elements"].append({
            "type": "text",
            "text": "Thank You",
            "box": {
                "x": 80,
                "y": 580,
                "w": 1100,
                "h": 80
            },
            "style": {
                "fontSize": 48,
                "align": "center",
                "color": "#ffffff",
                "italic": True,
                "font": DesignConfig.FONTS["heading"]
            },
            "shadow": {
                "x": 3,
                "y": 3,
                "blur": 6,
                "color": "#00000050"
            }
        })
        
        return slide
    
    def save_presentation(self, output_path: str = "presentation.json") -> bool:
        """Save generated presentation to JSON file"""
        
        if not self.presentation:
            logger.error("No presentation to save")
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.presentation, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved presentation to {output_path}")
            logger.info(f"Total slides: {len(self.presentation['ppt']['slides'])}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save presentation: {e}")
            return False
    
    def display_summary(self):
        """Display presentation generation summary"""
        
        if not self.presentation:
            print("No presentation generated")
            return
        
        print("\n" + "="*80)
        print("SLIDE GENERATOR AGENT - PRESENTATION SUMMARY")
        print("="*80)
        
        slides = self.presentation['ppt']['slides']
        print(f"\nTotal Slides: {len(slides)}")
        print(f"Dimensions: {self.presentation['ppt']['size']['width']}x{self.presentation['ppt']['size']['height']} px")
        print(f"\nColor Theme:")
        for color_name, color_value in self.presentation['ppt']['theme']['colors'].items():
            print(f"  {color_name}: {color_value}")
        
        print(f"\nSlides:")
        for slide in slides:
            num_elements = len(slide.get('elements', []))
            print(f"  [{slide['id']}] {slide['title']} - {num_elements} elements")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Advanced Slide Generator Agent - Professional PPT Design',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python slide_generator_agent.py                  # Default mode
  python slide_generator_agent.py --input slide_plan.json
  python slide_generator_agent.py --output presentation.json
        """
    )
    
    parser.add_argument(
        '--input',
        default='../4- Slide Planner Agent/slide_plan.json',
        help='Input slide plan file'
    )
    
    parser.add_argument(
        '--output',
        default='presentation.json',
        help='Output presentation file'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("SLIDE GENERATOR AGENT - Advanced PPT Designer")
    print("="*80)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    
    # Create agent
    generator = SlideGeneratorAgent()
    
    # Load slide plan
    if not generator.load_plan(args.input):
        logger.error("Failed to load slide plan")
        return
    
    # Generate presentation
    presentation = generator.generate_presentation()
    
    # Save presentation
    if not generator.save_presentation(args.output):
        logger.error("Failed to save presentation")
        return
    
    # Display summary
    generator.display_summary()
    
    print("\n" + "="*80)
    print("✅ PRESENTATION GENERATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
