"""
Test script to demonstrate Vector Store querying functionality.
"""

from vector_store_agent import load_vector_store, query_loaded_vector_store, VectorStoreAgent
from sentence_transformers import SentenceTransformer

# Load the vector store
index, metadata = load_vector_store("chunks.index", "chunks_metadata.json")

if index and metadata:
    # Load embedding model for queries
    embedding_model = SentenceTransformer(VectorStoreAgent.EMBEDDING_MODEL)
    
    # Test queries
    test_queries = [
        "What is generative AI?",
        "How do language models work?",
        "Explain transformers and attention mechanisms",
        "What are the applications of GenAI?"
    ]
    
    print("\n" + "="*80)
    print("VECTOR STORE QUERY TESTS")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 80)
        
        # Get top 3 results
        results = query_loaded_vector_store(query, index, metadata, embedding_model, k=3)
        
        for result in results:
            print(f"\n  Rank {result['rank']} | Score: {result['score']:.4f}")
            print(f"  Chunk ID: {result['chunk_id']} | Page: {result['page']}")
            text_preview = result['text'][:120] + "..." if len(result['text']) > 120 else result['text']
            print(f"  Text: {text_preview}")
        
        print("\n" + "="*80 + "\n")
else:
    print("Failed to load vector store")
