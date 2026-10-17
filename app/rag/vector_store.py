"""ChromaDB vector store integration for automotive regulation clauses."""

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.core.logging import logger
from app.rag.chunker import RegulationChunk
from app.rag.embeddings import BaseEmbeddingEngine, get_embedding_engine


class VectorStore:
    COLLECTION_NAME = "unece_regulations"

    def __init__(
        self,
        persist_dir: str | None = None,
        embedding_engine: BaseEmbeddingEngine | None = None,
    ):
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        self.embedding_engine = embedding_engine or get_embedding_engine()
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB initialized at %s with collection %s", self.persist_dir, self.COLLECTION_NAME
        )

    def add_chunks(self, chunks: list[RegulationChunk]) -> int:
        """Add or update regulation chunks with precomputed embeddings."""
        if not chunks:
            return 0

        ids = [chunk.chunk_id for chunk in chunks]
        texts = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document": chunk.document,
                "clause_id": chunk.clause_id,
                "section_title": chunk.section_title,
                "page": chunk.page,
            }
            for chunk in chunks
        ]

        logger.info("Embedding %d regulation chunks...", len(texts))
        embeddings = self.embedding_engine.embed_documents(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info("Successfully indexed %d chunks into ChromaDB.", len(chunks))
        return len(chunks)

    def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Dense vector search using query text."""
        count = self.collection.count()
        if count == 0:
            return []

        effective_k = min(top_k, count)
        query_embedding = self.embedding_engine.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=effective_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: list[dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return hits

        for i, chunk_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            doc_text = results["documents"][0][i] if results.get("documents") else ""
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            # Convert cosine distance to similarity score in [0, 1]
            similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))

            hits.append(
                {
                    "chunk_id": chunk_id,
                    "text": doc_text,
                    "document": metadata.get("document", "Unknown"),
                    "clause_id": metadata.get("clause_id", ""),
                    "section_title": metadata.get("section_title", ""),
                    "page": metadata.get("page", 1),
                    "score": round(similarity, 4),
                    "match_type": "vector",
                }
            )

        return hits

    def get_chunk_by_id(self, chunk_id: str) -> dict[str, Any] | None:
        """Fetch exact chunk by ID (used for programmatic citation verification)."""
        res = self.collection.get(ids=[chunk_id], include=["documents", "metadatas"])
        if res and res.get("ids") and len(res["ids"]) > 0:
            metadata = res["metadatas"][0] if res.get("metadatas") else {}
            return {
                "chunk_id": res["ids"][0],
                "text": res["documents"][0] if res.get("documents") else "",
                "document": metadata.get("document", ""),
                "clause_id": metadata.get("clause_id", ""),
                "section_title": metadata.get("section_title", ""),
                "page": metadata.get("page", 1),
            }
        return None

    def get_all_chunks(self) -> list[dict[str, Any]]:
        """Retrieve all indexed chunks (e.g. for BM25 corpus initialization)."""
        count = self.collection.count()
        if count == 0:
            return []

        res = self.collection.get(include=["documents", "metadatas"])
        items = []
        for i, chunk_id in enumerate(res.get("ids", [])):
            metadata = res["metadatas"][i] if res.get("metadatas") else {}
            items.append(
                {
                    "chunk_id": chunk_id,
                    "text": res["documents"][i] if res.get("documents") else "",
                    "document": metadata.get("document", ""),
                    "clause_id": metadata.get("clause_id", ""),
                    "section_title": metadata.get("section_title", ""),
                    "page": metadata.get("page", 1),
                }
            )
        return items

    def count(self) -> int:
        return self.collection.count()

    def list_sources(self) -> list[dict[str, Any]]:
        """List distinct sources with chunk counts."""
        all_chunks = self.get_all_chunks()
        source_counts: dict[str, int] = {}
        for c in all_chunks:
            doc = c.get("document", "Unknown")
            source_counts[doc] = source_counts.get(doc, 0) + 1

        return [
            {"document": doc, "chunk_count": count} for doc, count in sorted(source_counts.items())
        ]
