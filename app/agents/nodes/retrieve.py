"""Retrieve node: runs hybrid retrieval for each requirement against regulation chunks."""

import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.config import settings
from app.rag.retriever import HybridRetriever
from app.rag.vector_store import VectorStore

_retriever: HybridRetriever | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(vector_store=VectorStore())
    return _retriever


def retrieve_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: hybrid retrieval of regulation clauses."""
    start_time = time.time()
    requirements = state.get("requirements", [])
    retrieved_map: dict[str, list[dict[str, Any]]] = {}
    retriever = get_retriever()

    top_k = settings.top_k_retrieval
    for req in requirements:
        req_id = req["req_id"]
        text = req["text"]
        clauses = retriever.retrieve(query=text, top_k=top_k)
        retrieved_map[req_id] = clauses

    elapsed_ms = (time.time() - start_time) * 1000
    trace_step: TraceStep = {
        "node": "retrieve",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Retrieved top-{top_k} regulation clauses for {len(requirements)} requirements.",
    }

    return {
        "retrieved_clauses": retrieved_map,
        "trace": state.get("trace", []) + [trace_step],
    }
