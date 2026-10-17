"""Health and readiness endpoint."""

from fastapi import APIRouter

from app.core.config import settings
from app.rag.vector_store import VectorStore

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """System health, environment info, and knowledge base status."""
    store = VectorStore()
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "indexed_regulation_chunks": store.count(),
    }
