import json
from pathlib import Path

import faiss
import numpy as np

from embeddings import create_embedding


VECTOR_STORE_DIR = Path(__file__).parent / "vector_store"

INDEX_FILE = VECTOR_STORE_DIR / "qlik_faiss.index"
DOCUMENTS_FILE = VECTOR_STORE_DIR / "documents.json"


def search_knowledge(query: str, top_k: int = 3):

    # Load FAISS index
    index = faiss.read_index(str(INDEX_FILE))

    # Load original documents
    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    # Create embedding for user's question
    query_embedding = create_embedding(query)

    # Convert to FAISS-compatible format
    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    # Search for nearest documents
    distances, indices = index.search(
        query_vector,
        top_k
    )

    results = []

    for distance, idx in zip(
        distances[0],
        indices[0]
    ):

        if idx == -1:
            continue

        results.append({
            "distance": float(distance),
            "document": documents[int(idx)]
        })

    return results


if __name__ == "__main__":

    query = "I forgot my Qlik Sense password"

    results = search_knowledge(
        query,
        top_k=3
    )

    print("Search results for:")
    print(query)

    print("=" * 60)

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"\nResult {i}")
        print(f"Distance: {result['distance']:.4f}")
        print(result["document"])