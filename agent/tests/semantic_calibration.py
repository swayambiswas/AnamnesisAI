import os
import sys
from datetime import datetime

from agent.providers.embeddings import GeminiEmbeddingProvider
from agent.reranker import cosine_similarity


def run_calibration():
    print("--- Phase 3 Semantic Calibration Suite ---")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("LIMITATION: GEMINI_API_KEY not found.")
        print("Cannot responsibly calibrate the relevance threshold without real embeddings.")
        print("Using the safe default of 0.45 until real data is available.")
        sys.exit(0)

    try:
        provider = GeminiEmbeddingProvider()
        print("Successfully initialized GeminiEmbeddingProvider.")
    except Exception as e:
        print(f"Failed to initialize provider: {e}")
        sys.exit(1)

    queries = [
        "What programming language am I currently using?",
        "What is my favorite animal?",
    ]

    memories = [
        "I currently use Python for my projects.", # Direct semantic match for Q1
        "I mainly code in Python.", # Paraphrase for Q1
        "I like snakes.", # Related but incorrect for Q1
        "I have a dog.", # Direct match for Q2
        "I love cats and dogs.", # Multiple matches for Q2
        "The sky is blue.", # Unrelated
    ]

    print("\nExtracting embeddings...")
    try:
        query_embeddings = {q: provider.get_embedding(q) for q in queries}
        memory_embeddings = {m: provider.get_embedding(m) for m in memories}
    except Exception as e:
        print(f"Failed to fetch embeddings: {e}")
        sys.exit(1)

    print("\nSimilarity Matrix:")
    for q in queries:
        print(f"\nQuery: '{q}'")
        results = []
        for m in memories:
            score = cosine_similarity(query_embeddings[q], memory_embeddings[m])
            results.append((m, score))
        results.sort(key=lambda x: x[1], reverse=True)
        for m, score in results:
            print(f"  {score:.4f} -> {m}")

    print("\nCalibration Complete. Adjust RankingConfig if needed based on these real similarities.")


if __name__ == "__main__":
    run_calibration()

