# TTS Generative Audio Agent
"""
Agent that converts narration scripts into spoken audio using text-to-speech.
Processes scripts.json and generates audio files in WAV format.
Uses pyttsx3 for offline, reliable speech synthesis.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# TTS Engine
try:
    import pyttsx3
except ImportError:
    print("Installing pyttsx3 text-to-speech engine...")
    os.system("pip install pyttsx3")
    import pyttsx3

# Audio file support
try:
    import soundfile as sf
    import numpy as np
except ImportError:
    print("Installing audio packages...")
    os.system("pip install soundfile numpy")
    import soundfile as sf
    import numpy as np


class TTSAgent:
    """
    Text-to-Speech Agent that converts narration scripts into spoken audio.
    
    Uses pyttsx3 for reliable, offline speech synthesis with:
    - Clear, professional tone
    - Controlled speech rate
    - Output: WAV format (44.1 kHz, 16-bit)
    """
    
    def __init__(self, scripts_path: str, output_dir: str = "audio_output"):
        """
        Initialize TTS Agent.
        
        Args:
            scripts_path: Path to scripts.json file
            output_dir: Directory to save generated audio files
        """
        self.scripts_path = Path(scripts_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speech rate (words per minute)
        self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        self.results = {
            "version": "2.0",
            "metadata": {
                "total_slides": 0,
                "total_audio_files": 0,
                "model": "pyttsx3 (Offline TTS)",
                "format": "WAV (44.1 kHz, 16-bit)",
                "speech_rate": "150 WPM"
            },
            "audio_files": []
        }
    
    def load_scripts(self) -> Dict:
        """Load scripts from JSON file."""
        try:
            with open(self.scripts_path, 'r', encoding='utf-8') as f:
                scripts_data = json.load(f)
            print(f"[OK] Loaded {len(scripts_data['scripts'])} scripts from {self.scripts_path.name}")
            return scripts_data
        except Exception as e:
            print(f"[ERROR] Error loading scripts: {e}")
            return None
    
    def generate_speech(self, text: str, output_path: Path) -> bool:
        """
        Generate speech audio from text using pyttsx3.
        
        Args:
            text: Narration script text
            output_path: Path to save audio file
            
        Returns:
            True if generation successful, False otherwise
        """
        try:
            # Clean text for better speech quality
            text = text.strip()
            
            # Use pyttsx3 to generate speech to file
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            # Verify file was created
            if output_path.exists() and output_path.stat().st_size > 0:
                duration = self._estimate_duration(text)
                print(f"[OK] Audio generated: {output_path.name} (~{duration:.1f}s)")
                return True
            else:
                print(f"[WARN] Audio file not created for {output_path.name}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error generating audio: {e}")
            return False
    
    def _estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on text length.
        Average: 150 WPM = 2.5 words per second
        """
        words = len(text.split())
        estimated_duration = words / 2.5
        return estimated_duration
    
    def process_scripts(self) -> bool:
        """
        Main process: Load scripts and generate audio for each.
        
        Returns:
            True if processing completed successfully
        """
        print("=" * 70)
        print("TTS GENERATIVE AUDIO AGENT - PROCESSING STARTED")
        print("=" * 70)
        
        # Load scripts
        scripts_data = self.load_scripts()
        if not scripts_data:
            return False
        
        scripts = scripts_data.get('scripts', [])
        self.results['metadata']['total_slides'] = len(scripts)
        
        successful_conversions = 0
        
        # Process each script
        for script_item in scripts:
            slide_id = script_item.get('slide_id')
            title = script_item.get('title', 'Unknown')
            script_text = script_item.get('script', '')
            
            # Skip if no script text
            if not script_text:
                print(f"[SKIP] Slide {slide_id}: No script text")
                continue
            
            print(f"\nSlide {slide_id}: {title}")
            print(f"  Text length: {len(script_text)} characters")
            
            # Generate audio file
            audio_filename = f"slide_{slide_id:02d}_audio.wav"
            audio_path = self.output_dir / audio_filename
            
            # Generate speech
            if self.generate_speech(script_text, audio_path):
                successful_conversions += 1
                
                # Record in results
                self.results['audio_files'].append({
                    "slide_id": slide_id,
                    "title": title,
                    "audio_file": audio_filename,
                    "text_length": len(script_text),
                    "estimated_duration": self._estimate_duration(script_text)
                })
        
        self.results['metadata']['total_audio_files'] = successful_conversions
        
        # Save results metadata
        self.save_results()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"Audio Generation Complete: {successful_conversions}/{len(scripts)} successful")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print("=" * 70)
        
        return successful_conversions > 0
    
    def save_results(self) -> bool:
        """Save processing results to JSON."""
        try:
            results_path = self.output_dir / "audio_metadata.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"[OK] Metadata saved: {results_path.name}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving metadata: {e}")
            return False


def main():
    """Main execution function."""
    
    # Define paths
    project_root = Path(__file__).parent.parent
    scripts_path = project_root / "7- Script Agent for each slide in PPTX" / "scripts.json"
    output_dir = Path(__file__).parent / "audio_output"
    
    # Create and run TTS Agent
    agent = TTSAgent(
        scripts_path=str(scripts_path),
        output_dir=str(output_dir)
    )
    
    # Process all scripts
    success = agent.process_scripts()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
