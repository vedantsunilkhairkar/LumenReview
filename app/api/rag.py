"""FastAPI router for RAG knowledge base management and search."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.rag.loader import RegulationLoader
from app.rag.retriever import HybridRetriever
from app.rag.vector_store import VectorStore

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])

# Reusable instances
_vector_store: VectorStore | None = None
_retriever: HybridRetriever | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(vector_store=get_vector_store())
    return _retriever


class IngestResponse(BaseModel):
    status: str
    chunks_indexed: int
    sources: list[dict[str, Any]]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Requirement or search phrase")
    top_k: int = Field(default=5, ge=1, le=20, description="Max clauses to retrieve")
    dense_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    bm25_weight: float = Field(default=0.4, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    chunk_id: str
    document: str
    clause_id: str
    section_title: str
    text: str
    fused_score: float
    page: int = 1


@router.post("/ingest", response_model=IngestResponse)
def ingest_regulations():
    """Ingest and chunk all regulation files from data/regulations into ChromaDB."""
    try:
        loader = RegulationLoader()
        chunks = loader.load_all()
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No regulation documents found in data/regulations directory.",
            )

        store = get_vector_store()
        count = store.add_chunks(chunks)

        # Refresh retriever BM25 index
        retriever = get_retriever()
        retriever._refresh_bm25_index()

        sources = store.list_sources()
        return IngestResponse(
            status="success",
            chunks_indexed=count,
            sources=sources,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during regulation ingestion: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sources")
def list_sources():
    """List all ingested regulation sources and chunk counts."""
    store = get_vector_store()
    return {
        "total_chunks": store.count(),
        "sources": store.list_sources(),
    }


@router.post("/search", response_model=list[SearchResultItem])
def search_regulations(req: SearchRequest):
    """Debug and test hybrid retrieval (dense vector + BM25 keyword rerank)."""
    retriever = get_retriever()
    results = retriever.retrieve(
        query=req.query,
        top_k=req.top_k,
        dense_weight=req.dense_weight,
        bm25_weight=req.bm25_weight,
    )
    return results
