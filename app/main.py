"""Main FastAPI application entrypoint for LumenReview."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.evaluation import router as evaluation_router
from app.api.health import router as health_router
from app.api.rag import router as rag_router
from app.api.requirements import router as requirements_router
from app.api.reviews import router as reviews_router
from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db
from app.rag.loader import RegulationLoader
from app.rag.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite tables and pre-index regulations if needed
    logger.info("Initializing LumenReview database schema...")
    init_db()

    store = VectorStore()
    if store.count() == 0:
        logger.info("Vector store is empty on startup. Ingesting starter regulations...")
        try:
            loader = RegulationLoader()
            chunks = loader.load_all()
            if chunks:
                store.add_chunks(chunks)
        except Exception as e:
            logger.warning("Could not auto-ingest regulations on startup: %s", e)

    yield

    # Shutdown
    logger.info("LumenReview API service shutting down.")


app = FastAPI(
    title="LumenReview API",
    description="Requirements Review Agent for Automotive Lighting Systems (UNECE R48/R112)",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health_router)
app.include_router(requirements_router)
app.include_router(reviews_router)
app.include_router(rag_router)
app.include_router(evaluation_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to LumenReview API",
        "docs": "/docs",
        "health": "/health",
        "version": settings.app_version,
    }
