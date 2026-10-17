"""Hybrid retriever combining ChromaDB dense vector search and BM25 sparse keyword search."""

import re
from typing import Any

from rank_bm25 import BM25Okapi

from app.core.logging import logger
from app.rag.vector_store import VectorStore


def tokenize_for_bm25(text: str) -> list[str]:
    """Tokenize query or document text for BM25 matching."""
    # Retain clause numbers like 6.2.6.1.2, units like %, lm, m, cd, lux, Hz
    tokens = re.findall(r"[\w\.\%\-]+", text.lower())
    return [t for t in tokens if len(t) > 1 or t in ["m", "v", "h"]]


class HybridRetriever:
    """Performs dense vector retrieval + BM25 keyword rerank with Reciprocal Rank Fusion."""

    def __init__(self, vector_store: VectorStore | None = None):
        self.vector_store = vector_store or VectorStore()
        self._bm25_index: BM25Okapi | None = None
        self._bm25_corpus_chunks: list[dict[str, Any]] = []
        self._refresh_bm25_index()

    def _refresh_bm25_index(self):
        chunks = self.vector_store.get_all_chunks()
        if not chunks:
            self._bm25_index = None
            self._bm25_corpus_chunks = []
            return

        tokenized_corpus = [
            tokenize_for_bm25(f"{c['clause_id']} {c['section_title']} {c['text']}") for c in chunks
        ]
        self._bm25_index = BM25Okapi(tokenized_corpus)
        self._bm25_corpus_chunks = chunks
        logger.info("Initialized BM25 index over %d regulation chunks.", len(chunks))

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ) -> list[dict[str, Any]]:
        """Perform hybrid retrieval with Reciprocal Rank Fusion (RRF)."""
        if self.vector_store.count() == 0:
            return []

        # If BM25 index is uninitialized but store has chunks, refresh
        if self._bm25_index is None or len(self._bm25_corpus_chunks) != self.vector_store.count():
            self._refresh_bm25_index()

        # 1. Dense Vector Search
        dense_candidates = self.vector_store.query(query, top_k=max(top_k * 2, 10))

        # 2. BM25 Search
        query_tokens = tokenize_for_bm25(query)
        bm25_scores: list[float] = []
        if self._bm25_index and query_tokens:
            bm25_scores = self._bm25_index.get_scores(query_tokens).tolist()

        # Build rank maps
        dense_rank_map: dict[str, int] = {
            c["chunk_id"]: rank for rank, c in enumerate(dense_candidates, start=1)
        }

        # Top BM25 candidates
        bm25_ranked_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )
        bm25_rank_map: dict[str, int] = {}
        for rank, idx in enumerate(bm25_ranked_indices[: max(top_k * 2, 10)], start=1):
            if idx < len(self._bm25_corpus_chunks):
                chunk_id = self._bm25_corpus_chunks[idx]["chunk_id"]
                bm25_rank_map[chunk_id] = rank

        # Merge candidate set
        all_candidate_ids = set(dense_rank_map.keys()).union(set(bm25_rank_map.keys()))
        chunk_lookup: dict[str, dict[str, Any]] = {c["chunk_id"]: c for c in dense_candidates}
        for idx in bm25_ranked_indices[: max(top_k * 2, 10)]:
            if idx < len(self._bm25_corpus_chunks):
                c = self._bm25_corpus_chunks[idx]
                if c["chunk_id"] not in chunk_lookup:
                    chunk_lookup[c["chunk_id"]] = {
                        "chunk_id": c["chunk_id"],
                        "text": c["text"],
                        "document": c["document"],
                        "clause_id": c["clause_id"],
                        "section_title": c["section_title"],
                        "page": c.get("page", 1),
                        "score": 0.0,
                        "match_type": "bm25",
                    }

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_constant = 60
        fused_candidates: list[dict[str, Any]] = []

        for cid in all_candidate_ids:
            chunk = chunk_lookup.get(cid)
            if not chunk:
                continue

            r_dense = dense_rank_map.get(cid, 999)
            r_bm25 = bm25_rank_map.get(cid, 999)

            score_dense = dense_weight / (rrf_constant + r_dense)
            score_bm25 = bm25_weight / (rrf_constant + r_bm25)
            fused_score = score_dense + score_bm25

            item = dict(chunk)
            item["fused_score"] = round(fused_score, 6)
            item["dense_rank"] = r_dense if r_dense < 999 else None
            item["bm25_rank"] = r_bm25 if r_bm25 < 999 else None
            fused_candidates.append(item)

        # Sort by fused score descending
        fused_candidates.sort(key=lambda x: x["fused_score"], reverse=True)
        return fused_candidates[:top_k]
