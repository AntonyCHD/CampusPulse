"""Ingest knowledge base documents into Milvus vector store.

Usage:
    python -m backend.app.storage.vector_store_ingest
    python -m backend.app.storage.vector_store_ingest --reset
"""

import argparse
import sys
from pathlib import Path

# Ensure backend is on path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.storage.vector_store import (
    MilvusVectorStore,
    load_knowledge_base_docs,
)
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

KB_DIR = project_root / "data" / "knowledge_base"


def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge base into Milvus")
    parser.add_argument("--reset", action="store_true", help="Delete existing data before ingest")
    args = parser.parse_args()

    # Load documents
    docs = load_knowledge_base_docs(str(KB_DIR))
    if not docs:
        print("No knowledge base documents found. Aborting.")
        return

    print(f"Found {len(docs)} documents to ingest:")
    for doc in docs:
        print(f"  [{doc.evidence_type}] {doc.title} ({len(doc.content)} chars)")

    # Initialize services
    print("\nConnecting to Milvus...")
    vector_store = MilvusVectorStore()
    if not vector_store.connect():
        print("ERROR: Cannot connect to Milvus. Is the Docker container running?")
        print("  Expected: milvus-standalone on localhost:19530")
        return

    current_count = vector_store.get_count()
    print(f"Current collection count: {current_count}")

    if args.reset and current_count > 0:
        print("Resetting collection...")
        vector_store.delete_all()
        print("Collection cleared.")

    if current_count > 0 and not args.reset:
        print("Documents already ingested. Use --reset to re-ingest.")
        return

    # Generate embeddings
    print("\nLoading BGE-M3 embedding model...")
    embedding_service = EmbeddingService()

    print("Generating embeddings...")
    texts = [doc.text_for_embedding for doc in docs]
    embeddings_np = embedding_service.encode_batch(texts, batch_size=8)
    embeddings = [emb.tolist() for emb in embeddings_np]

    # Insert into Milvus
    print(f"Inserting {len(docs)} documents into Milvus...")
    inserted = vector_store.insert(docs, embeddings)
    print(f"Successfully inserted {inserted} documents.")

    # Verify
    final_count = vector_store.get_count()
    print(f"Final collection count: {final_count}")

    # Quick search test
    print("\nRunning quick search test...")
    test_query = "学生宿舍断电怎么办"
    query_emb = embedding_service.encode(test_query, use_cache=True).tolist()
    results = vector_store.search(query_emb, top_k=3)
    print(f"Query: '{test_query}'")
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r['evidence_type']}] {r['title']} (score: {r['score']:.4f})")

    vector_store.disconnect()
    print("\nIngestion complete.")


if __name__ == "__main__":
    main()
