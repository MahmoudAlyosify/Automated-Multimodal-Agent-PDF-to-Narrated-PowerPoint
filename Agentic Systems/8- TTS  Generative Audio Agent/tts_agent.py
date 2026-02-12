# TTS Generative Audio Agent
"""
Agent that converts narration scripts into spoken audio using Suno Bark generative speech model.
Processes scripts.json and generates audio files with normalization and format conversion.
"""

import json
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Audio processing imports
try:
    import librosa
    import soundfile as sf
except ImportError:
    print("Installing required audio packages...")
    os.system("pip install librosa soundfile")
    import librosa
    import soundfile as sf

# TTS model
try:
    from bark import generate_audio
    import bark
except ImportError:
    print("Installing bark TTS model...")
    os.system("pip install bark-ml")
    from bark import generate_audio
    import bark

# Video processing for MP4 conversion
try:
    import ffmpeg
except ImportError:
    print("Installing ffmpeg-python...")
    os.system("pip install ffmpeg-python")
    import ffmpeg


class TTSAgent:
    """
    Text-to-Speech Agent that converts narration scripts into spoken audio.
    
    Uses Suno Bark for speech synthesis with:
    - Style: Neutral academic lecturer
    - Tone: Calm and clear
    - Speed: Medium
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
        
        # Bark model configuration
        self.voice_preset = "v2/en_speaker_1"  # Neutral academic lecturer voice
        self.sample_rate = 24000  # Bark default sample rate
        
        # Audio normalization settings
        self.target_loudness = -20.0  # dB (LUFS)
        self.compression_ratio = 4.0
        
        self.results = {
            "version": "1.0",
            "metadata": {
                "total_slides": 0,
                "total_audio_files": 0,
                "model": "Suno Bark",
                "voice_style": "Neutral academic lecturer"
            },
            "audio_files": []
        }
    
    def load_scripts(self) -> Dict:
        """Load scripts from JSON file."""
        try:
            with open(self.scripts_path, 'r', encoding='utf-8') as f:
                scripts_data = json.load(f)
            print(f"✓ Loaded {len(scripts_data['scripts'])} scripts from {self.scripts_path.name}")
            return scripts_data
        except Exception as e:
            print(f"✗ Error loading scripts: {e}")
            return None
    
    def normalize_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Normalize audio for consistent volume and clarity.
        
        Args:
            audio: Audio array
            sr: Sample rate
            
        Returns:
            Normalized audio array
        """
        # Remove DC offset
        audio = audio - np.mean(audio)
        
        # Normalize to [-1, 1]
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        
        # Apply gentle compression to improve clarity
        threshold = 0.7
        ratio = self.compression_ratio
        
        mask = np.abs(audio) > threshold
        audio[mask] = np.sign(audio[mask]) * (
            threshold + (np.abs(audio[mask]) - threshold) / ratio
        )
        
        # Normalize again after compression
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95  # Leave some headroom
        
        return audio
    
    def generate_speech(self, text: str, slide_id: int) -> Optional[np.ndarray]:
        """
        Generate speech audio from text using Bark.
        
        Args:
            text: Narration script text
            slide_id: Slide identifier for logging
            
        Returns:
            Audio array or None if generation fails
        """
        try:
            print(f"\n  Generating audio for slide {slide_id}...")
            
            # Preprocess text for better quality
            text = text.strip()
            # Break long text into sentences for better prosody
            if len(text) > 500:
                # Add slight pause between sentences
                text = text.replace(". ", ".\n ")
            
            # Generate audio using Bark
            audio_array = generate_audio(
                text,
                history_prompt=self.voice_preset,
                text_temp=0.7,  # Temperature for consistency
                waveform_temp=0.8  # Temperature for naturalness
            )
            
            # Normalize the audio
            audio_normalized = self.normalize_audio(audio_array, self.sample_rate)
            
            print(f"  ✓ Audio generated ({len(audio_normalized)/self.sample_rate:.1f}s)")
            return audio_normalized
            
        except Exception as e:
            print(f"  ✗ Error generating audio: {e}")
            return None
    
    def save_wav(self, audio: np.ndarray, output_path: Path) -> bool:
        """
        Save audio to WAV format.
        
        Args:
            audio: Audio array
            output_path: Path to save WAV file
            
        Returns:
            True if successful
        """
        try:
            sf.write(str(output_path), audio, self.sample_rate, subtype='PCM_16')
            print(f"  ✓ Saved WAV: {output_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Error saving WAV: {e}")
            return False
    
    def convert_to_mp4(self, wav_path: Path, mp4_path: Path) -> bool:
        """
        Convert WAV to MP4 using ffmpeg.
        
        Args:
            wav_path: Path to WAV file
            mp4_path: Path to save MP4 file
            
        Returns:
            True if successful
        """
        try:
            # Use ffmpeg to convert WAV to MP4
            # This creates an audio-only MP4 suitable for PPTX embedding
            stream = ffmpeg.input(str(wav_path))
            stream = ffmpeg.output(
                stream,
                str(mp4_path),
                acodec='aac',
                audio_bitrate='128k',
                q=5
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            print(f"  ✓ Converted to MP4: {mp4_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Error converting to MP4: {e}")
            # Fallback: If ffmpeg fails, try alternative approach
            try:
                os.system(f'ffmpeg -i "{wav_path}" -acodec aac -q:a 5 -y "{mp4_path}" -hide_banner -loglevel error')
                print(f"  ✓ Converted to MP4 (fallback): {mp4_path.name}")
                return True
            except:
                return False
    
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
            
            print(f"\n[Slide {slide_id}] {title}")
            
            if not script_text:
                print(f"  ✗ No script text found")
                continue
            
            # Generate speech audio
            audio_array = self.generate_speech(script_text, slide_id)
            if audio_array is None:
                continue
            
            # Create output filenames
            wav_filename = f"slide_{slide_id:02d}_{title.replace(' ', '_').lower()}.wav"
            mp4_filename = f"slide_{slide_id:02d}_{title.replace(' ', '_').lower()}.mp4"
            
            wav_path = self.output_dir / wav_filename
            mp4_path = self.output_dir / mp4_filename
            
            # Save WAV
            if not self.save_wav(audio_array, wav_path):
                continue
            
            # Convert to MP4
            if not self.convert_to_mp4(wav_path, mp4_path):
                print(f"  ⚠ MP4 conversion failed, but WAV saved")
            
            # Record result
            result_item = {
                "slide_id": slide_id,
                "title": title,
                "duration_seconds": len(audio_array) / self.sample_rate,
                "wav_file": wav_filename,
                "mp4_file": mp4_filename,
                "status": "completed"
            }
            self.results['audio_files'].append(result_item)
            successful_conversions += 1
        
        # Update metadata
        self.results['metadata']['total_audio_files'] = successful_conversions
        
        # Save results
        self.save_results()
        
        # Print summary
        print("\n" + "=" * 70)
        print("PROCESSING SUMMARY")
        print("=" * 70)
        print(f"Total Slides: {self.results['metadata']['total_slides']}")
        print(f"Audio Files Generated: {successful_conversions}")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print("=" * 70)
        
        return successful_conversions > 0
    
    def save_results(self) -> bool:
        """Save processing results to JSON."""
        try:
            results_path = self.output_dir / "audio_metadata.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"✓ Metadata saved: {results_path.name}")
            return True
        except Exception as e:
            print(f"✗ Error saving metadata: {e}")
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
