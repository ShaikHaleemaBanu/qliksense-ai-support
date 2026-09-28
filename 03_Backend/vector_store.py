import json
from pathlib import Path

import faiss
import numpy as np

from knowledge_base import load_knowledge_base
from embeddings import create_embedding


# Where to save the vector store
VECTOR_STORE_DIR = Path(__file__).parent / "vector_store"

INDEX_FILE = VECTOR_STORE_DIR / "qlik_faiss.index"
DOCUMENTS_FILE = VECTOR_STORE_DIR / "documents.json"


def create_documents():
    """
    Convert Excel rows into searchable text documents.
    """

    df = load_knowledge_base()

    documents = []

    for _, row in df.iterrows():

        document = (
            f"Category: {row['Category']}\n"
            f"Issue: {row['Issue']}\n"
            f"Step Number: {row['Step_Number']}\n"
            f"Troubleshooting Step: {row['Troubleshooting_Step']}\n"
            f"Expected Result: {row['Expected_Result']}\n"
            f"Escalation: {row['Escalation']}"
        )

        documents.append(document)

    return documents


def build_vector_store():

    print("Loading knowledge base...")

    documents = create_documents()

    print(f"Found {len(documents)} documents.")

    embeddings = []

    for index, document in enumerate(documents):

        print(
            f"Creating embedding "
            f"{index + 1}/{len(documents)}..."
        )

        embedding = create_embedding(document)

        embeddings.append(embedding)

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print("Embeddings created successfully.")

    # Get embedding dimension
    dimension = embeddings.shape[1]

    print(f"Embedding dimension: {dimension}")

    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)

    # Add embeddings
    index.add(embeddings)

    # Create directory
    VECTOR_STORE_DIR.mkdir(
        exist_ok=True
    )

    # Save FAISS index
    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    # Save documents
    with open(
        DOCUMENTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Vector store created successfully!")
    print(f"FAISS index: {INDEX_FILE}")
    print(f"Documents: {DOCUMENTS_FILE}")


if __name__ == "__main__":

    build_vector_store()