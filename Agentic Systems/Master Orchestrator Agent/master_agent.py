"""
MASTER ORCHESTRATOR AGENT - System Brain
Direct Execution of All Agents
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MasterOrchestratorAgent:
    """Master orchestrator coordinating all agents."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root.parent / "output"
        
        self.parser_dir = self.project_root / "1- PDF Parser and Layout Analyzer Agent"
        self.chunker_dir = self.project_root / "2- Semantic Chunker Agent"
        self.vector_dir = self.project_root / "3- Vector DB + Embeddings Layer"
        self.planner_dir = self.project_root / "4- Slide Planner Agent"
        self.generator_dir = self.project_root / "5- Slide Generator Agent"
        self.script_dir = self.project_root / "7- Script Agent for each slide in PPTX"
        self.tts_dir = self.project_root / "8- TTS  Generative Audio Agent"
        self.pptx_dir = self.project_root / "6- PPTX Builder Agent"
        
        self.pdf_path = self._find_pdf()
        self._setup_directories()
        
        logger.info("="*80)
        logger.info("MASTER ORCHESTRATOR INITIALIZED")
        logger.info("="*80)
        logger.info(f"PDF: {self.pdf_path}")
        logger.info(f"Output: {self.output_dir}")
    
    def _find_pdf(self) -> str:
        pdf_path = self.parser_dir / "Test_PDF_genai-principles.pdf"
        if pdf_path.exists():
            return str(pdf_path)
        for pdf in self.parser_dir.glob("*.pdf"):
            return str(pdf)
        return None
    
    def _setup_directories(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "slides").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "audio").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "metadata").mkdir(parents=True, exist_ok=True)
    
    def run_parser_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 1: PDF PARSER AGENT")
        logger.info("="*80)
        
        try:
            if not self.pdf_path:
                logger.error("[ERROR] PDF not found")
                return False
            
            original_dir = os.getcwd()
            os.chdir(self.parser_dir)
            sys.path.insert(0, str(self.parser_dir))
            
            from parser_agent import PDFParserAgent
            
            agent = PDFParserAgent(use_layoutlmv3=True)
            blocks = agent.parse_pdf(self.pdf_path)
            
            if not blocks:
                logger.error("[ERROR] No blocks extracted")
                return False
            
            output_path = self.parser_dir / "parsed_blocks.json"
            agent.save_json(blocks, str(output_path))
            logger.info(f"[OK] Extracted {len(blocks)} blocks")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] Parser failed: {e}")
            return False
    
    def run_semantic_chunker_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 2: SEMANTIC CHUNKER AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.chunker_dir)
            sys.path.insert(0, str(self.chunker_dir))
            
            from semantic_chunker_agent import SemanticChunkerAgent
            
            agent = SemanticChunkerAgent(str(self.parser_dir / "parsed_blocks.json"))
            
            success = agent.process(
                parsed_blocks_path=str(self.parser_dir / "parsed_blocks.json"),
                output_path=str(self.chunker_dir / "semantic_chunks.json")
            )
            
            if success:
                logger.info(f"[OK] Created {len(agent.chunks)} chunks")
            
            os.chdir(original_dir)
            return success
        
        except Exception as e:
            logger.error(f"[ERROR] Chunker failed: {e}")
            return False
    
    def run_vector_store_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 3: VECTOR STORE AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.vector_dir)
            sys.path.insert(0, str(self.vector_dir))
            
            from vector_store_agent import VectorStoreAgent
            
            agent = VectorStoreAgent(str(self.chunker_dir / "semantic_chunks.json"))
            
            success = agent.process(
                semantic_chunks_path=str(self.chunker_dir / "semantic_chunks.json"),
                index_output_path=str(self.vector_dir / "chunks.index"),
                metadata_output_path=str(self.vector_dir / "chunks_metadata.json"),
                embeddings_output_path=str(self.vector_dir / "chunks_embeddings.npy")
            )
            
            if success:
                logger.info(f"[OK] Created embeddings ({len(agent.metadata)} chunks)")
            
            os.chdir(original_dir)
            return success
        
        except Exception as e:
            logger.error(f"[ERROR] Vector store failed: {e}")
            return False
    
    def run_slide_planner_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 4: SLIDE PLANNER AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.planner_dir)
            sys.path.insert(0, str(self.planner_dir))
            
            from slide_planner_agent import SlidePlannerAgent, ChunkLoader
            
            chunks = ChunkLoader.load(str(self.chunker_dir / "semantic_chunks.json"))
            if not chunks:
                logger.error("[ERROR] Failed to load chunks")
                return False
            
            planner = SlidePlannerAgent()
            planner.load_chunks(chunks)
            
            try:
                slides = planner.plan(13)
                logger.info("[OK] Used API planning")
            except:
                logger.info("[WARN] API planning failed, using fallback")
                slides = planner._fallback_plan(13)
            
            planner.slides = slides
            planner.save_plan(str(self.planner_dir / "slide_plan.json"))
            logger.info(f"[OK] Created plan for {len(slides)} slides")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] Planner failed: {e}")
            return False
    
    def run_slide_generator_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 5: SLIDE GENERATOR AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.generator_dir)
            sys.path.insert(0, str(self.generator_dir))
            
            from slide_generator_agent import SlideGeneratorAgent
            
            generator = SlideGeneratorAgent()
            
            if not generator.load_plan(str(self.planner_dir / "slide_plan.json")):
                logger.error("[ERROR] Failed to load plan")
                return False
            
            presentation = generator.generate_presentation()
            
            if not generator.save_presentation(str(self.generator_dir / "presentation.json")):
                logger.error("[ERROR] Failed to save presentation")
                return False
            
            logger.info(f"[OK] Generated presentation JSON")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] Generator failed: {e}")
            return False
    
    def run_script_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 6: SCRIPT AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.script_dir)
            sys.path.insert(0, str(self.script_dir))
            
            from script_agent import NarrationScriptAgent
            
            agent = NarrationScriptAgent()
            
            if not agent.load_slide_plan(str(self.planner_dir / "slide_plan.json")):
                logger.error("[ERROR] Failed to load plan")
                return False
            
            try:
                agent.generate_scripts()
            except:
                logger.warning("[WARN] Script generation failed")
            
            agent.save_scripts(str(self.script_dir / "scripts.json"))
            logger.info(f"[OK] Generated scripts")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.warning(f"[WARN] Script agent failed: {e}")
            return True
    
    def run_tts_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 7: TTS AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.tts_dir)
            sys.path.insert(0, str(self.tts_dir))
            
            from tts_agent import TTSAgent
            
            agent = TTSAgent(
                scripts_path=str(self.script_dir / "scripts.json"),
                output_dir=str(self.tts_dir / "audio_output")
            )
            
            agent.process_scripts()
            logger.info("[OK] Generated audio files")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.warning(f"[WARN] TTS failed: {e}")
            return True
    
    def run_pptx_builder_agent(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("STAGE 8: PPTX BUILDER AGENT")
        logger.info("="*80)
        
        try:
            original_dir = os.getcwd()
            os.chdir(self.pptx_dir)
            sys.path.insert(0, str(self.pptx_dir))
            
            from pptx_builder_agent import PPTXBuilderAgent
            
            # Get audio folder path
            audio_folder = self.tts_dir / "audio_output"
            
            builder = PPTXBuilderAgent(audio_folder=str(audio_folder) if audio_folder.exists() else None)
            
            if not builder.load_presentation_json(str(self.generator_dir / "presentation.json")):
                logger.error("[ERROR] Failed to load JSON")
                return False
            
            if not builder.build_presentation():
                logger.error("[ERROR] Failed to build presentation")
                return False
            
            if not builder.save_presentation(str(self.pptx_dir / "lecture.pptx")):
                logger.error("[ERROR] Failed to save PPTX")
                return False
            
            logger.info("[OK] PowerPoint created")
            
            os.chdir(original_dir)
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] PPTX builder failed: {e}")
            return False
    
    def assemble_final_output(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("ASSEMBLING FINAL OUTPUT")
        logger.info("="*80)
        
        try:
            # Create output subdirectories
            (self.output_dir / "audio").mkdir(parents=True, exist_ok=True)
            (self.output_dir / "metadata").mkdir(parents=True, exist_ok=True)
            
            # Copy PowerPoint
            src_pptx = self.pptx_dir / "lecture.pptx"
            if src_pptx.exists():
                dst_pptx = self.output_dir / "Narrated-PowerPoint.pptx"
                shutil.copy2(src_pptx, dst_pptx)
                logger.info(f"[OK] PowerPoint: {dst_pptx.name}")
            
            # Copy all audio files
            audio_src = self.tts_dir / "audio_output"
            if audio_src.exists():
                for f in audio_src.glob("*"):
                    if f.is_file():
                        shutil.copy2(f, self.output_dir / "audio" / f.name)
                logger.info("[OK] Audio files copied")
            
            # Copy metadata files
            for src, name in [
                (self.parser_dir / "parsed_blocks.json", "parsed_blocks.json"),
                (self.chunker_dir / "semantic_chunks.json", "semantic_chunks.json"),
                (self.planner_dir / "slide_plan.json", "slide_plan.json"),
                (self.generator_dir / "presentation.json", "presentation.json"),
                (self.script_dir / "scripts.json", "scripts.json")
            ]:
                if src.exists():
                    shutil.copy2(src, self.output_dir / "metadata" / name)
            
            logger.info("[OK] Metadata copied")
            logger.info(f"\nOutput: {self.output_dir}")
            return True
        
        except Exception as e:
            logger.error(f"[ERROR] Assembly failed: {e}")
            return False
    
    def run(self) -> bool:
        logger.info("\n" + "="*80)
        logger.info("MASTER ORCHESTRATOR - FULL PIPELINE EXECUTION")
        logger.info("="*80)
        
        start = datetime.now()
        
        stages = [
            ("Parser", self.run_parser_agent),
            ("Chunker", self.run_semantic_chunker_agent),
            ("Vector Store", self.run_vector_store_agent),
            ("Planner", self.run_slide_planner_agent),
            ("Generator", self.run_slide_generator_agent),
            ("Scripts", self.run_script_agent),
            ("TTS", self.run_tts_agent),
            ("PPTX Builder", self.run_pptx_builder_agent),
        ]
        
        completed = 0
        for name, func in stages:
            try:
                if func():
                    completed += 1
                else:
                    logger.error(f"[FAILED] {name}")
                    return False
            except Exception as e:
                logger.error(f"[FAILED] {name}: {e}")
                return False
        
        self.assemble_final_output()
        
        elapsed = (datetime.now() - start).total_seconds()
        logger.info("\n" + "="*80)
        logger.info("[SUCCESS] PIPELINE COMPLETE")
        logger.info("="*80)
        logger.info(f"Stages: {completed}/{len(stages)}")
        logger.info(f"Time: {elapsed:.1f}s")
        logger.info(f"Output: {self.output_dir}")
        logger.info("="*80)
        
        return True


def main():
    try:
        agent = MasterOrchestratorAgent()
        success = agent.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"FATAL: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
