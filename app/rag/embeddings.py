"""Embedding abstractions: SentenceTransformers with deterministic offline fallback."""

import hashlib
import math
import re
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.logging import logger


class BaseEmbeddingEngine(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text documents."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        pass


class DeterministicEmbedding(BaseEmbeddingEngine):
    """Lightweight 384-dimensional deterministic embedding using token hashes.

    Ensures 100% offline functionality, zero cold-start delay in tests and CI,
    and semantic stability across test runs.
    """

    DIM = 384

    def _embed_single(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for token in tokens:
            # Hash token to dimension indices
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.DIM
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign

            # Bigram feature
            h2 = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx2 = (h2 >> 4) % self.DIM
            vec[idx2] += 0.5 * (1.0 if ((h2 >> 12) & 1) else -1.0)

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_single(text)


class SentenceTransformerEmbedding(BaseEmbeddingEngine):
    """Production embedding model using HuggingFace sentence-transformers."""

    _singleton_model = None

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if SentenceTransformerEmbedding._singleton_model is not None:
            self._model = SentenceTransformerEmbedding._singleton_model
            return

        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading SentenceTransformer model: %s", self.model_name)
                SentenceTransformerEmbedding._singleton_model = SentenceTransformer(self.model_name)
                self._model = SentenceTransformerEmbedding._singleton_model
            except Exception as e:
                logger.warning(
                    "Could not load SentenceTransformer %s (%s). Falling back to DeterministicEmbedding.",
                    self.model_name,
                    e,
                )
                self._model = False

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        if self._model:
            embeddings = self._model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        return DeterministicEmbedding().embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        self._load_model()
        if self._model:
            embedding = self._model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        return DeterministicEmbedding().embed_query(text)


def get_embedding_engine() -> BaseEmbeddingEngine:
    """Return embedding engine based on environment and availability."""
    import os

    if os.getenv("APP_ENV") == "test" or settings.app_env == "test":
        return DeterministicEmbedding()

    try:
        import sentence_transformers  # noqa: F401

        return SentenceTransformerEmbedding(settings.embedding_model)
    except ImportError:
        logger.info("sentence-transformers not installed; using DeterministicEmbedding.")
        return DeterministicEmbedding()
