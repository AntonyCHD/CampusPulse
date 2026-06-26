"""Milvus vector store for knowledge base retrieval.

Uses the local Milvus standalone container via pymilvus MilvusClient (high-level API)
and BGE-M3 for embedding generation.  Uses auto_id=True so Milvus assigns INT64
primary keys automatically.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pymilvus import MilvusClient

from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "campus_knowledge_base"
DIMENSION = 1024
MILVUS_URI = "http://localhost:19530"


@dataclass
class KnowledgeDocument:
    """A document stored in the knowledge base."""

    doc_id: str
    title: str
    source: str
    content: str
    evidence_type: str
    chunk_index: int = 0

    @property
    def text_for_embedding(self) -> str:
        return f"{self.title}\n{self.content}"


class MilvusVectorStore:
    """Vector store backed by Milvus for knowledge base retrieval."""

    def __init__(
        self,
        uri: str = MILVUS_URI,
        collection_name: str = COLLECTION_NAME,
        dimension: int = DIMENSION,
    ):
        self.uri = uri
        self.collection_name = collection_name
        self.dimension = dimension
        self._client: MilvusClient | None = None

    @property
    def client(self) -> MilvusClient:
        if self._client is None:
            self._client = MilvusClient(uri=self.uri)
        return self._client

    def connect(self) -> bool:
        """Verify Milvus connectivity and ensure the collection exists."""
        try:
            self.client.list_collections()
            logger.info(f"Connected to Milvus at {self.uri}")
            self._ensure_collection()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            return False

    def disconnect(self):
        """Close the Milvus client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        if self.client.has_collection(self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            metric_type="COSINE",
            auto_id=True,
        )
        logger.info(f"Created collection '{self.collection_name}' (dim={self.dimension})")

    def insert(
        self,
        docs: list[KnowledgeDocument],
        embeddings: list[list[float]],
    ) -> int:
        """Insert documents with their embeddings into Milvus.

        With auto_id=True we do NOT supply the "id" field; Milvus generates it.
        The doc_id is stored in a separate field for retrieval.
        """
        if len(docs) != len(embeddings):
            raise ValueError(f"Mismatch: {len(docs)} docs vs {len(embeddings)} embeddings")

        data = []
        for doc, emb in zip(docs, embeddings):
            data.append({
                "vector": emb,
                "doc_id": doc.doc_id,
                "title": doc.title,
                "source": doc.source,
                "content": doc.content,
                "evidence_type": doc.evidence_type,
                "chunk_index": doc.chunk_index,
            })

        try:
            result = self.client.insert(
                collection_name=self.collection_name,
                data=data,
            )
            count = result["insert_count"]
            logger.info(f"Inserted {count} documents into '{self.collection_name}'")
            return count
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return 0

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        evidence_type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar documents by vector."""
        filter_expr = None
        if evidence_type_filter:
            filter_expr = f'evidence_type == "{evidence_type_filter}"'

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                limit=top_k,
                filter=filter_expr,
                output_fields=["doc_id", "title", "source", "content", "evidence_type"],
            )
            hits = []
            for hit in results[0]:
                entity = hit.get("entity", hit)
                hits.append({
                    "evidence_id": entity.get("doc_id", str(hit.get("id", ""))),
                    "title": entity.get("title", ""),
                    "source": entity.get("source", ""),
                    "content": entity.get("content", ""),
                    "evidence_type": entity.get("evidence_type", ""),
                    "score": round(float(hit.get("distance", 0.0)), 4),
                })
            return hits
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_count(self) -> int:
        """Return the number of documents using a lightweight query."""
        try:
            if not self.client.has_collection(self.collection_name):
                return 0
            q = self.client.query(
                collection_name=self.collection_name,
                filter="id >= 0",
                output_fields=["id"],
                limit=100,
            )
            return len(q)
        except Exception:
            return 0

    def delete_all(self):
        """Drop and recreate the collection."""
        try:
            if self.client.has_collection(self.collection_name):
                self.client.drop_collection(self.collection_name)
                logger.info(f"Dropped collection '{self.collection_name}'")
            self._ensure_collection()
        except Exception as e:
            logger.error(f"Delete failed: {e}")


# ---------------------------------------------------------------------------
# Knowledge base ingestion helpers
# ---------------------------------------------------------------------------

def load_knowledge_base_docs(kb_dir: str) -> list[KnowledgeDocument]:
    """Load all markdown files from the knowledge base directory structure."""
    kb_path = Path(kb_dir)
    docs: list[KnowledgeDocument] = []

    dir_type_map = {
        "policies": "policy",
        "notices": "notice",
        "response_templates": "response_template",
        "history_cases": "history_case",
    }

    for dir_name, ev_type in dir_type_map.items():
        dir_path = kb_path / dir_name
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.glob("*.md")):
            content = md_file.read_text(encoding="utf-8").strip()
            if not content:
                continue
            title = md_file.stem.replace("_", " ").title()
            doc_id = hashlib.md5(f"{dir_name}/{md_file.name}".encode()).hexdigest()[:16]
            docs.append(KnowledgeDocument(
                doc_id=doc_id,
                title=title,
                source=f"中国传媒大学{dir_name}",
                content=content,
                evidence_type=ev_type,
            ))

    logger.info(f"Loaded {len(docs)} knowledge base documents from {kb_dir}")
    return docs
