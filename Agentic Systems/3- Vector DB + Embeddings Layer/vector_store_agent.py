"""
Vector DB + Embeddings Layer Agent

Objective:
- Input: semantic_chunks.json (output from Semantic Chunker Agent)
- Output: FAISS vector index + metadata JSON
- Functionality: Create dense vector embeddings for chunks and store in a vector database
              for efficient retrieval in downstream agents.

Description:
This agent enables grounded retrieval by indexing semantic chunks using dense vector embeddings.
It ensures that downstream agents (Slide Planner, Generator, etc.) operate on retrieved 
source content rather than hallucinated knowledge.

Requirements:
1. Load semantic chunks from 'semantic_chunks.json'
2. Generate embeddings for each chunk using HuggingFace embedding model
3. Store embeddings in a FAISS vector database
4. Save metadata linking each vector to chunk_id and original text
5. Provide retrieval function that returns top-k most relevant chunks for a query

Implementation Guidelines:
- Use cosine similarity for retrieval
- Normalize embeddings
- Ensure reproducibility with a random seed
- Include function: query_vector_store(query_text, k=5)
"""

import json
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
import faiss
from sentence_transformers import SentenceTransformer


class VectorStoreAgent:
    """
    Agent responsible for creating and managing vector embeddings for semantic chunks.
    Uses FAISS for efficient similarity search.
    """
    
    # Class-level constants
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast, lightweight model
    EMBEDDING_DIM = 384  # Dimension of embeddings for all-MiniLM-L6-v2
    
    def __init__(self, semantic_chunks_path: str = "semantic_chunks.json", 
                 embedding_model: str = None):
        """
        Initialize the Vector Store Agent.
        
        Args:
            semantic_chunks_path: Path to semantic_chunks.json file
            embedding_model: HuggingFace model name. Defaults to all-MiniLM-L6-v2
        """
        self.semantic_chunks_path = semantic_chunks_path
        self.embedding_model_name = embedding_model or self.EMBEDDING_MODEL
        self.embedding_model = None  # Will be loaded on demand
        
        # Data structures
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None
        self.index: faiss.IndexFlatIP = None  # Inner product (cosine similarity) index
        self.metadata: List[Dict[str, Any]] = []
        
        # Set random seed for reproducibility
        np.random.seed(42)
    
    def load_embedding_model(self) -> bool:
        """
        Load the SentenceTransformer embedding model.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print("Embedding model loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            return False
    
    def load_semantic_chunks(self) -> bool:
        """
        Load semantic chunks from JSON file.
        
        Returns:
            bool: True if chunks loaded successfully
        """
        try:
            if not os.path.exists(self.semantic_chunks_path):
                print(f"Error: {self.semantic_chunks_path} not found")
                return False
            
            with open(self.semantic_chunks_path, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            if not self.chunks:
                print("Error: No chunks found in JSON file")
                return False
            
            print(f"Loaded {len(self.chunks)} semantic chunks")
            return True
        except Exception as e:
            print(f"Error loading semantic chunks: {str(e)}")
            return False
    
    def generate_embeddings(self) -> bool:
        """
        Generate embeddings for all semantic chunks.
        
        Returns:
            bool: True if embeddings generated successfully
        """
        try:
            if not self.chunks:
                print("Error: No chunks loaded. Call load_semantic_chunks() first.")
                return False
            
            if self.embedding_model is None:
                if not self.load_embedding_model():
                    return False
            
            # Extract texts from chunks
            texts = [chunk.get('text', '') for chunk in self.chunks]
            
            print(f"\nGenerating embeddings for {len(texts)} chunks...")
            # Generate embeddings using the model
            embeddings = self.embedding_model.encode(
                texts,
                normalize_embeddings=True,  # Normalize for cosine similarity
                show_progress_bar=True
            )
            
            # Convert to numpy array with float32 for FAISS
            self.embeddings = np.array(embeddings, dtype=np.float32)
            
            print(f"Generated embeddings shape: {self.embeddings.shape}")
            return True
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return False
    
    def create_faiss_index(self) -> bool:
        """
        Create a FAISS index from embeddings using cosine similarity (inner product).
        
        Returns:
            bool: True if index created successfully
        """
        try:
            if self.embeddings is None:
                print("Error: No embeddings available. Call generate_embeddings() first.")
                return False
            
            embedding_dim = self.embeddings.shape[1]
            
            # Create index using cosine similarity (normalized inner product)
            # IndexFlatIP is efficient for cosine similarity on normalized vectors
            self.index = faiss.IndexFlatIP(embedding_dim)
            
            # Add embeddings to index
            self.index.add(self.embeddings)
            
            print(f"Created FAISS index with {self.index.ntotal} vectors")
            return True
        except Exception as e:
            print(f"Error creating FAISS index: {str(e)}")
            return False
    
    def create_metadata(self) -> bool:
        """
        Create metadata linking vector indices to chunk information.
        
        Returns:
            bool: True if metadata created successfully
        """
        try:
            if not self.chunks:
                print("Error: No chunks loaded.")
                return False
            
            self.metadata = []
            for index_id, chunk in enumerate(self.chunks):
                metadata_entry = {
                    "index_id": index_id,
                    "chunk_id": chunk.get('chunk_id', index_id),
                    "page": chunk.get('page', 0),
                    "text": chunk.get('text', '')
                }
                self.metadata.append(metadata_entry)
            
            print(f"Created metadata for {len(self.metadata)} chunks")
            return True
        except Exception as e:
            print(f"Error creating metadata: {str(e)}")
            return False
    
    def save_index(self, index_path: str = "chunks.index") -> bool:
        """
        Save FAISS index to disk.
        
        Args:
            index_path: Path to save the index file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.index is None:
                print("Error: No index available. Call create_faiss_index() first.")
                return False
            
            os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else '.', 
                       exist_ok=True)
            
            faiss.write_index(self.index, index_path)
            print(f"Saved FAISS index to {index_path}")
            return True
        except Exception as e:
            print(f"Error saving index: {str(e)}")
            return False
    
    def save_metadata(self, metadata_path: str = "chunks_metadata.json") -> bool:
        """
        Save metadata to JSON file.
        
        Args:
            metadata_path: Path to save the metadata file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if not self.metadata:
                print("Error: No metadata available. Call create_metadata() first.")
                return False
            
            os.makedirs(os.path.dirname(metadata_path) if os.path.dirname(metadata_path) else '.', 
                       exist_ok=True)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Saved metadata to {metadata_path}")
            return True
        except Exception as e:
            print(f"Error saving metadata: {str(e)}")
            return False
    
    def save_embeddings(self, embeddings_path: str = "chunks_embeddings.npy") -> bool:
        """
        Save embeddings to numpy file for future use.
        
        Args:
            embeddings_path: Path to save the embeddings file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.embeddings is None:
                print("Error: No embeddings available.")
                return False
            
            os.makedirs(os.path.dirname(embeddings_path) if os.path.dirname(embeddings_path) else '.', 
                       exist_ok=True)
            
            np.save(embeddings_path, self.embeddings)
            print(f"Saved embeddings to {embeddings_path}")
            return True
        except Exception as e:
            print(f"Error saving embeddings: {str(e)}")
            return False
    
    def query_vector_store(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector store for top-k most relevant chunks.
        
        Args:
            query_text: The query string
            k: Number of results to return
            
        Returns:
            List of top-k relevant chunks with scores
        """
        try:
            if self.index is None:
                print("Error: No index available. Process chunks first.")
                return []
            
            if self.embedding_model is None:
                if not self.load_embedding_model():
                    return []
            
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(
                [query_text],
                normalize_embeddings=True
            )
            query_embedding = np.array(query_embedding, dtype=np.float32)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"Error querying vector store: {str(e)}")
            return []
    
    def process(self, 
                semantic_chunks_path: str = "semantic_chunks.json",
                index_output_path: str = "chunks.index",
                metadata_output_path: str = "chunks_metadata.json",
                embeddings_output_path: str = "chunks_embeddings.npy") -> bool:
        """
        Complete pipeline: load chunks, generate embeddings, create index, and save.
        
        Args:
            semantic_chunks_path: Path to input semantic_chunks.json
            index_output_path: Path to save FAISS index
            metadata_output_path: Path to save metadata JSON
            embeddings_output_path: Path to save embeddings numpy file
            
        Returns:
            bool: True if entire process succeeded
        """
        print("\n" + "="*60)
        print("VECTOR STORE + EMBEDDINGS AGENT")
        print("="*60)
        
        # Load chunks
        self.semantic_chunks_path = semantic_chunks_path
        if not self.load_semantic_chunks():
            return False
        
        # Generate embeddings
        if not self.generate_embeddings():
            return False
        
        # Create index
        if not self.create_faiss_index():
            return False
        
        # Create metadata
        if not self.create_metadata():
            return False
        
        # Save all outputs
        if not self.save_index(index_output_path):
            return False
        
        if not self.save_metadata(metadata_output_path):
            return False
        
        if not self.save_embeddings(embeddings_output_path):
            return False
        
        print("="*60)
        print("Vector Store creation complete!")
        print("="*60 + "\n")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_chunks": len(self.chunks),
            "embedding_model": self.embedding_model_name,
            "embedding_dim": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "index_size": self.index.ntotal if self.index is not None else 0,
            "metadata_entries": len(self.metadata)
        }


def load_vector_store(index_path: str = "chunks.index", 
                      metadata_path: str = "chunks_metadata.json") -> Tuple[faiss.IndexFlatIP, List[Dict]]:
    """
    Load pre-built vector store from disk.
    
    Args:
        index_path: Path to FAISS index file
        metadata_path: Path to metadata JSON file
        
    Returns:
        Tuple of (FAISS index, metadata list) or (None, []) if loading fails
    """
    try:
        # Load index
        if not os.path.exists(index_path):
            print(f"Error: Index file {index_path} not found")
            return None, []
        
        index = faiss.read_index(index_path)
        
        # Load metadata
        if not os.path.exists(metadata_path):
            print(f"Warning: Metadata file {metadata_path} not found")
            metadata = []
        else:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        print(f"Loaded vector store: {index.ntotal} vectors with metadata")
        return index, metadata
    except Exception as e:
        print(f"Error loading vector store: {str(e)}")
        return None, []


def query_loaded_vector_store(query_text: str, 
                              index: faiss.IndexFlatIP,
                              metadata: List[Dict],
                              embedding_model: SentenceTransformer = None,
                              k: int = 5) -> List[Dict[str, Any]]:
    """
    Query a pre-loaded vector store.
    
    Args:
        query_text: The query string
        index: FAISS index
        metadata: Metadata list
        embedding_model: SentenceTransformer model (loads if None)
        k: Number of results to return
        
    Returns:
        List of top-k relevant chunks
    """
    try:
        if embedding_model is None:
            embedding_model = SentenceTransformer(VectorStoreAgent.EMBEDDING_MODEL)
        
        # Generate query embedding
        query_embedding = embedding_model.encode(
            [query_text],
            normalize_embeddings=True
        )
        query_embedding = np.array(query_embedding, dtype=np.float32)
        
        # Search
        scores, indices = index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(metadata):
                result = metadata[idx].copy()
                result['score'] = float(score)
                result['rank'] = i + 1
                results.append(result)
        
        return results
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        return []


def main():
    """
    Main execution function for the Vector Store Agent.
    """
    # Initialize agent
    agent = VectorStoreAgent()
    
    # Process semantic chunks (adjust paths as needed)
    semantic_chunks_path = "../2- Semantic Chunker Agent/semantic_chunks.json"
    index_output_path = "chunks.index"
    metadata_output_path = "chunks_metadata.json"
    embeddings_output_path = "chunks_embeddings.npy"
    
    success = agent.process(
        semantic_chunks_path=semantic_chunks_path,
        index_output_path=index_output_path,
        metadata_output_path=metadata_output_path,
        embeddings_output_path=embeddings_output_path
    )
    
    if success:
        # Print statistics
        stats = agent.get_statistics()
        print("\nVector Store Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Embedding model: {stats['embedding_model']}")
        print(f"  Embedding dimension: {stats['embedding_dim']}")
        print(f"  Index size: {stats['index_size']}")
        print(f"  Metadata entries: {stats['metadata_entries']}")
        
        # Example query
        print("\n" + "="*60)
        print("EXAMPLE QUERY")
        print("="*60)
        query = "What is generative AI?"
        print(f"\nQuery: '{query}'")
        results = agent.query_vector_store(query, k=3)
        
        print(f"\nTop 3 results:")
        for result in results:
            print(f"\n  Rank {result['rank']} (Score: {result['score']:.4f})")
            print(f"  Chunk ID: {result['chunk_id']}, Page: {result['page']}")
            text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
            print(f"  Text: {text_preview}")


if __name__ == "__main__":
    main()
