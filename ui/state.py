"""Streamlit session state helpers and API integration client."""

import os
from typing import Any

import httpx
import streamlit as st

from app.db.repository import ReviewRepository
from app.db.session import SessionLocal, init_db

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


class LumenClient:
    """Client for LumenReview API with seamless local database fallback."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def get_health(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/health")
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass
        return {"status": "healthy", "mode": "embedded"}

    def list_reviews(self) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/reviews")
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        # Fallback to direct DB
        init_db()
        db = SessionLocal()
        try:
            repo = ReviewRepository(db)
            runs = repo.list_reviews()
            return [
                {
                    "id": r.id,
                    "status": r.status,
                    "total_requirements": r.total_requirements,
                    "total_findings": r.total_findings,
                    "approved_findings": r.approved_findings,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                }
                for r in runs
            ]
        finally:
            db.close()

    def get_review_details(self, review_id: str) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/reviews/{review_id}")
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        # Direct DB fallback
        init_db()
        db = SessionLocal()
        try:
            import json

            from app.api.reviews import serialize_finding

            repo = ReviewRepository(db)
            review = repo.get_review(review_id)
            if not review:
                return None
            findings = repo.get_review_findings(review_id)
            audit = repo.get_audit_trail(review_id)
            trace = json.loads(review.trace_json) if review.trace_json else []

            return {
                "id": review.id,
                "status": review.status,
                "total_requirements": review.total_requirements,
                "total_findings": review.total_findings,
                "approved_findings": review.approved_findings,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "completed_at": review.completed_at.isoformat() if review.completed_at else None,
                "findings": [serialize_finding(f) for f in findings],
                "trace": trace,
                "audit_trail": [
                    {
                        "finding_id": a.finding_id,
                        "decision": a.decision,
                        "notes": a.notes,
                        "decided_at": a.decided_at.isoformat() if a.decided_at else None,
                    }
                    for a in audit
                ],
                "report_md": review.report_md,
            }
        finally:
            db.close()

    def start_review(self, raw_input: str) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=60.0) as client:
                r = client.post(f"{self.base_url}/reviews", json={"raw_input": raw_input})
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        # Direct Agent execution fallback
        from app.api.reviews import CreateReviewRequest
        from app.api.reviews import start_review as direct_start

        db = SessionLocal()
        try:
            return direct_start(CreateReviewRequest(raw_input=raw_input), db=db)
        finally:
            db.close()

    def submit_decisions(self, review_id: str, decisions: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(
                    f"{self.base_url}/reviews/{review_id}/decisions", json={"decisions": decisions}
                )
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        from app.api.reviews import SubmitDecisionsRequest
        from app.api.reviews import submit_decisions as direct_submit

        db = SessionLocal()
        try:
            return direct_submit(review_id, SubmitDecisionsRequest(decisions=decisions), db=db)
        finally:
            db.close()

    def get_sources(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=3.0) as client:
                r = client.get(f"{self.base_url}/rag/sources")
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        from app.rag.vector_store import VectorStore

        store = VectorStore()
        return {
            "total_chunks": store.count(),
            "sources": store.list_sources(),
        }

    def search_regulations(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.post(
                    f"{self.base_url}/rag/search",
                    json={"query": query, "top_k": top_k},
                )
                if r.status_code == 200:
                    return r.json()
        except Exception:
            pass

        from app.rag.retriever import HybridRetriever

        retriever = HybridRetriever()
        return retriever.retrieve(query=query, top_k=top_k)


def get_client() -> LumenClient:
    if "lumen_client" not in st.session_state:
        st.session_state["lumen_client"] = LumenClient()
    return st.session_state["lumen_client"]
