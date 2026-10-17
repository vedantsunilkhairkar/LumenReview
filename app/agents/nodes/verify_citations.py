"""Programmatic Citation Verifier: verifies cited chunk IDs and quotes against ground truth."""

import difflib
import re
import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.config import settings
from app.core.logging import logger
from app.rag.vector_store import VectorStore

_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


def normalize_text(text: str) -> str:
    """Normalize whitespace and punctuation for quote verification."""
    text = text.lower()
    text = re.sub(r"[^\w\s\.\%\-]", " ", text)
    return " ".join(text.split())


def compute_string_similarity(a: str, b: str) -> float:
    """Compute normalized sequence similarity ratio."""
    norm_a = normalize_text(a)
    norm_b = normalize_text(b)
    if not norm_a or not norm_b:
        return 0.0
    if norm_a in norm_b or norm_b in norm_a:
        return 1.0
    return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()


def verify_single_finding(finding: dict[str, Any], store: VectorStore) -> dict[str, Any]:
    """Programmatically verify evidence citations for a finding.

    Never trust the LLM's citations blindly.
    """
    updated = dict(finding)
    evidence = updated.get("evidence")

    # If no regulatory clause cited (e.g. ambiguity or testability without citation)
    if not evidence or not evidence.get("chunk_id"):
        updated["citation_verified"] = True
        updated["citation_verification_note"] = (
            "N/A: General engineering analysis (no clause cited)."
        )
        return updated

    chunk_id = evidence.get("chunk_id", "").strip()
    quoted_text = evidence.get("quote", "").strip()

    # 1. Verify chunk ID exists in knowledge base
    chunk = store.get_chunk_by_id(chunk_id)
    if not chunk:
        logger.warning("Citation verification FAILED: Chunk ID %s not found in store.", chunk_id)
        updated["citation_verified"] = False
        updated["confidence"] = min(updated.get("confidence", 0.9), 0.10)
        updated["citation_verification_note"] = (
            f"HALLUCINATED CHUNK: Cited chunk ID '{chunk_id}' was not found in the ingested regulations database."
        )
        return updated

    # Chunk exists, verify document/clause metadata
    source_text = chunk.get("text", "")
    norm_source = normalize_text(source_text)
    norm_quote = normalize_text(quoted_text)

    # 2. Check verbatim or normalized substring match
    if norm_quote and norm_quote in norm_source:
        updated["citation_verified"] = True
        updated["citation_verification_note"] = (
            f"VERIFIED: Verbatim quote confirmed in {chunk.get('document')} (Clause {chunk.get('clause_id')})."
        )
        # Ensure document and clause_id match real chunk
        evidence["document"] = chunk.get("document", evidence.get("document"))
        evidence["clause_id"] = chunk.get("clause_id", evidence.get("clause_id"))
        return updated

    # 3. Fuzzy match for minor paraphrasing or OCR quirks
    similarity = compute_string_similarity(norm_quote, norm_source)
    min_sim = settings.min_citation_similarity

    if similarity >= min_sim:
        updated["citation_verified"] = True
        updated["citation_verification_note"] = (
            f"VERIFIED: High-fidelity quote match ({int(similarity * 100)}%) against {chunk.get('document')} (Clause {chunk.get('clause_id')})."
        )
        evidence["document"] = chunk.get("document", evidence.get("document"))
        evidence["clause_id"] = chunk.get("clause_id", evidence.get("clause_id"))
    else:
        logger.warning(
            "Citation verification FAILED: Quote not found in chunk %s (sim=%.2f). Quote: '%s'",
            chunk_id,
            similarity,
            quoted_text[:60],
        )
        updated["citation_verified"] = False
        updated["confidence"] = min(updated.get("confidence", 0.9), 0.20)
        updated["citation_verification_note"] = (
            f"UNVERIFIED QUOTE: Quoted text was not found in chunk '{chunk_id}' ({int(similarity * 100)}% match < {int(min_sim * 100)}% threshold)."
        )

    return updated


def verify_citations_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: programmatically verify all cited findings."""
    start_time = time.time()
    findings = state.get("findings", [])
    store = get_vector_store()

    verified_findings: list[dict[str, Any]] = []
    verified_count = 0
    hallucinated_count = 0

    for f in findings:
        checked = verify_single_finding(f, store)
        if checked.get("citation_verified", False):
            verified_count += 1
        else:
            hallucinated_count += 1
        verified_findings.append(checked)

    elapsed_ms = (time.time() - start_time) * 1000
    trace_step: TraceStep = {
        "node": "verify_citations",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Verified {verified_count} citations. Flagged/downgraded {hallucinated_count} unverified citations.",
    }

    return {
        "findings": verified_findings,
        "trace": state.get("trace", []) + [trace_step],
    }
