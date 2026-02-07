"""
Semantic Chunker Agent

Objective:
- Input: parsed_blocks.json (output from PDF Parser + Layout Analyzer)
- Output: semantically meaningful text chunks (JSON format)
- Functionality: Combine paragraphs, titles, and figure captions into coherent text units

Instructions:
1. Read parsed_blocks.json
2. Iterate through blocks in reading order
3. Merge consecutive blocks if they are small paragraphs or continuation lines
4. Use titles/headings as natural chunk separators
5. Keep figure captions with their related figures
6. Produce chunks with chunk_id, page, and text
7. Save to semantic_chunks.json
8. Maintain original page references
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


class SemanticChunkerAgent:
    """
    Agent responsible for creating semantically meaningful chunks from parsed PDF blocks.
    """
    
    def __init__(self, parsed_blocks_path: str = "parsed_blocks.json"):
        """
        Initialize the Semantic Chunker Agent.
        
        Args:
            parsed_blocks_path: Path to the parsed_blocks.json file
        """
        self.parsed_blocks_path = parsed_blocks_path
        self.blocks: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_id_counter = 0
        
    def load_parsed_blocks(self) -> bool:
        """
        Load parsed blocks from JSON file.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.parsed_blocks_path):
                print(f"Error: {self.parsed_blocks_path} not found")
                return False
            
            with open(self.parsed_blocks_path, 'r', encoding='utf-8') as f:
                self.blocks = json.load(f)
            
            print(f"Loaded {len(self.blocks)} blocks from {self.parsed_blocks_path}")
            return True
        except Exception as e:
            print(f"Error loading parsed blocks: {str(e)}")
            return False
    
    def is_empty_block(self, text: str) -> bool:
        """
        Check if a block is empty or non-informative.
        
        Args:
            text: Block text to check
            
        Returns:
            bool: True if block is empty or non-informative
        """
        # Remove whitespace and check length
        cleaned = text.strip()
        
        # Check if it's a standalone number or page marker
        if len(cleaned) == 0 or len(cleaned) <= 2:
            return True
        
        # Check if it's only numbers, dashes, or symbols
        if cleaned.replace('-', '').replace('•', '').replace('·', '').replace('.', '').isdigit():
            return True
        
        return False
    
    def is_title_or_heading(self, block: Dict[str, Any]) -> bool:
        """
        Determine if a block is a title or heading.
        
        Args:
            block: Block dictionary
            
        Returns:
            bool: True if block is a title/heading
        """
        block_type = block.get('block_type', '').lower()
        text = block.get('text', '').strip()
        
        # Check block type
        if 'title' in block_type or 'heading' in block_type or 'h1' in block_type or 'h2' in block_type:
            return True
        
        # Check if text is short and looks like a title (no period at end usually)
        if len(text) < 100 and not text.endswith('.'):
            # Count words to determine if it's likely a title
            word_count = len(text.split())
            if word_count <= 10 and text[0].isupper():
                return True
        
        return False
    
    def is_figure_caption(self, text: str) -> bool:
        """
        Check if text is a figure caption.
        
        Args:
            text: Block text
            
        Returns:
            bool: True if text appears to be a figure caption
        """
        text_lower = text.lower().strip()
        return text_lower.startswith('figure ') or text_lower.startswith('fig. ') or \
               text_lower.startswith('table ') or text_lower.startswith('image ')
    
    def is_small_block(self, text: str) -> bool:
        """
        Determine if a block is small enough to merge with neighbors.
        
        Args:
            text: Block text
            
        Returns:
            bool: True if block is small
        """
        word_count = len(text.split())
        # Consider blocks with less than 30 words as small
        return word_count < 30
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def create_semantic_chunks(self) -> bool:
        """
        Create semantic chunks from parsed blocks.
        
        Returns:
            bool: True if chunking was successful
        """
        if not self.blocks:
            print("No blocks loaded. Call load_parsed_blocks() first.")
            return False
        
        self.chunks = []
        self.chunk_id_counter = 0
        
        current_chunk_text = ""
        current_chunk_page = None
        i = 0
        
        while i < len(self.blocks):
            block = self.blocks[i]
            block_type = block.get('block_type', '')
            text = self.clean_text(block.get('text', ''))
            page = block.get('page', 0)
            
            # Skip empty blocks
            if self.is_empty_block(text):
                i += 1
                continue
            
            # If we encounter a title/heading, finalize current chunk and start new one
            if self.is_title_or_heading(block):
                # Save current chunk if it has content
                if current_chunk_text.strip():
                    self.chunks.append({
                        "chunk_id": self.chunk_id_counter,
                        "page": current_chunk_page,
                        "text": current_chunk_text.strip()
                    })
                    self.chunk_id_counter += 1
                
                # Start new chunk with title
                current_chunk_text = text
                current_chunk_page = page
                i += 1
                continue
            
            # Handle figure captions
            if self.is_figure_caption(text):
                # If there's existing content, finalize it
                if current_chunk_text.strip():
                    self.chunks.append({
                        "chunk_id": self.chunk_id_counter,
                        "page": current_chunk_page,
                        "text": current_chunk_text.strip()
                    })
                    self.chunk_id_counter += 1
                
                # Start new chunk with caption
                current_chunk_text = text
                current_chunk_page = page
                i += 1
                continue
            
            # For regular paragraphs
            if current_chunk_text:
                # Check if we should merge (small block or same page context)
                if self.is_small_block(text) and page == current_chunk_page:
                    # Merge with current chunk
                    current_chunk_text += " " + text
                else:
                    # Different context - start new chunk
                    self.chunks.append({
                        "chunk_id": self.chunk_id_counter,
                        "page": current_chunk_page,
                        "text": current_chunk_text.strip()
                    })
                    self.chunk_id_counter += 1
                    current_chunk_text = text
                    current_chunk_page = page
            else:
                # Starting first chunk
                current_chunk_text = text
                current_chunk_page = page
            
            i += 1
        
        # Don't forget the last chunk
        if current_chunk_text.strip():
            self.chunks.append({
                "chunk_id": self.chunk_id_counter,
                "page": current_chunk_page,
                "text": current_chunk_text.strip()
            })
        
        print(f"Created {len(self.chunks)} semantic chunks")
        return True
    
    def save_chunks(self, output_path: str = "semantic_chunks.json") -> bool:
        """
        Save semantic chunks to JSON file.
        
        Args:
            output_path: Path to save chunks JSON
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(self.chunks)} chunks to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving chunks: {str(e)}")
            return False
    
    def process(self, parsed_blocks_path: str = "parsed_blocks.json", 
                output_path: str = "semantic_chunks.json") -> bool:
        """
        Complete pipeline: load blocks, create chunks, and save output.
        
        Args:
            parsed_blocks_path: Path to input parsed_blocks.json
            output_path: Path to save semantic_chunks.json
            
        Returns:
            bool: True if entire process succeeded
        """
        print("\n" + "="*60)
        print("SEMANTIC CHUNKER AGENT")
        print("="*60)
        
        # Load blocks
        self.parsed_blocks_path = parsed_blocks_path
        if not self.load_parsed_blocks():
            return False
        
        # Create chunks
        if not self.create_semantic_chunks():
            return False
        
        # Save output
        if not self.save_chunks(output_path):
            return False
        
        print("="*60)
        print("Processing complete!")
        print("="*60 + "\n")
        return True
    
    def get_chunk_summary(self, max_length: int = 100) -> List[Dict[str, Any]]:
        """
        Get a summary of chunks for review.
        
        Args:
            max_length: Maximum length of summary text
            
        Returns:
            List of chunks with truncated text for review
        """
        summaries = []
        for chunk in self.chunks:
            summary = chunk.copy()
            if len(summary['text']) > max_length:
                summary['summary_text'] = summary['text'][:max_length] + "..."
            else:
                summary['summary_text'] = summary['text']
            summaries.append(summary)
        return summaries


def main():
    """
    Main execution function for the Semantic Chunker Agent.
    """
    # Initialize agent
    agent = SemanticChunkerAgent()
    
    # Process PDF blocks (adjust paths as needed)
    parsed_blocks_path = "../1- PDF Parser and Layout Analyzer Agent/parsed_blocks.json"
    output_path = "semantic_chunks.json"
    
    success = agent.process(
        parsed_blocks_path=parsed_blocks_path,
        output_path=output_path
    )
    
    if success:
        # Print summary
        print("\nChunk Summary:")
        summaries = agent.get_chunk_summary(max_length=100)
        for summary in summaries[:5]:  # Show first 5 chunks
            print(f"\nChunk {summary['chunk_id']} (Page {summary['page']}):")
            print(f"  {summary['summary_text']}")
        
        if len(summaries) > 5:
            print(f"\n... and {len(summaries) - 5} more chunks")


if __name__ == "__main__":
    main()
