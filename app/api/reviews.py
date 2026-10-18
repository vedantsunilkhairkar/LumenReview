"""FastAPI router for review runs, human decisions, and report generation."""

import json
import time
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field

from app.agents.graph import execute_review_analysis, resume_review_with_decisions
from app.agents.nodes.report import export_pdf_report
from app.api.deps import verify_api_key
from app.core.logging import logger
from app.db.models import FindingRecord
from app.db.repository import ReviewRepository
from app.db.session import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])


# Request & Response Schemas
class CreateReviewRequest(BaseModel):
    raw_input: str | None = Field(default=None, description="Raw text of requirements to review")
    requirements: list[dict[str, Any]] | None = Field(
        default=None, description="Pre-parsed list of requirements"
    )


class FindingDecisionInput(BaseModel):
    decision: Literal["approved", "rejected", "edited"] = Field(..., description="Reviewer action")
    notes: str | None = Field(default=None, description="Reviewer comments or justification")
    edited_rewrite: str | None = Field(
        default=None, description="Modified requirement text if edited"
    )


class SubmitDecisionsRequest(BaseModel):
    decisions: dict[str, FindingDecisionInput] = Field(
        ..., description="Map of finding_id -> decision"
    )


def serialize_finding(f: FindingRecord) -> dict[str, Any]:
    evidence = None
    if f.chunk_id:
        evidence = {
            "chunk_id": f.chunk_id,
            "quote": f.quote,
            "document": f.document,
            "clause_id": f.clause_id,
        }

    suggested_rewrite = None
    if f.suggested_rewrite:
        suggested_rewrite = {
            "text": f.suggested_rewrite,
            "diff_explanation": f.diff_explanation or "",
        }

    return {
        "id": f.id,
        "req_id": f.req_id,
        "type": f.type,
        "severity": f.severity,
        "title": f.title,
        "explanation": f.explanation,
        "market_scope": f.market_scope or "Global",
        "financial_impact_eur": f.financial_impact_eur,
        "financial_impact_type": f.financial_impact_type or "none",
        "evidence": evidence,
        "suggested_rewrite": suggested_rewrite,
        "confidence": f.confidence,
        "citation_verified": f.citation_verified,
        "citation_verification_note": f.citation_note,
        "human_decision": f.human_decision,
        "human_notes": f.human_notes,
    }


@router.post("", dependencies=[Depends(verify_api_key)])
def start_review(req: CreateReviewRequest, db=Depends(get_db)):
    """Start a new requirement review run using the LangGraph state machine."""
    raw = req.raw_input or ""
    if not raw and not req.requirements:
        raise HTTPException(
            status_code=400, detail="Must provide either raw_input or requirements."
        )

    repo = ReviewRepository(db)
    unique_suffix = uuid.uuid4().hex[:6].upper()
    run_id = f"REV-{time.strftime('%Y%m%d')}-{unique_suffix}"

    try:
        # Run graph pipeline up to human review interrupt
        state = execute_review_analysis(
            run_id=run_id,
            raw_input=raw,
            requirements=req.requirements,
        )

        # Persist review and initial findings into SQLite
        repo.create_review(
            review_id=run_id,
            raw_input=raw,
            requirements=state.get("requirements", []),
            status=state.get("status", "waiting_for_human"),
        )

        repo.save_findings(
            review_id=run_id,
            findings=state.get("findings", []),
            trace=state.get("trace", []),
            status=state.get("status", "waiting_for_human"),
        )

        return {
            "review_id": run_id,
            "status": state.get("status", "waiting_for_human"),
            "total_requirements": len(state.get("requirements", [])),
            "total_findings": len(state.get("findings", [])),
            "findings": state.get("findings", []),
            "security_warnings": state.get("security_warnings", []),
            "trace": state.get("trace", []),
        }
    except Exception as e:
        logger.error("Error executing review run %s: %s", run_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", dependencies=[Depends(verify_api_key)])
def list_reviews(limit: int = 50, db=Depends(get_db)):
    """List recent review runs with summary KPIs."""
    repo = ReviewRepository(db)
    runs = repo.list_reviews(limit=limit)
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


@router.get("/{review_id}", dependencies=[Depends(verify_api_key)])
def get_review_details(review_id: str, db=Depends(get_db)):
    """Fetch status, trace, requirements, and findings for a specific review run."""
    repo = ReviewRepository(db)
    review = repo.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found.")

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


@router.post("/{review_id}/decisions", dependencies=[Depends(verify_api_key)])
def submit_decisions(
    review_id: str,
    req: SubmitDecisionsRequest,
    db=Depends(get_db),
):
    """Submit human review decisions (approve/reject/edit) and resume graph to compile report."""
    repo = ReviewRepository(db)
    review = repo.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found.")

    decisions_dict = {fid: item.model_dump() for fid, item in req.decisions.items()}

    # 1. Save decisions to DB
    repo.record_decisions(review_id, decisions_dict)

    # 2. Reconstruct state to resume LangGraph
    findings = [serialize_finding(f) for f in repo.get_review_findings(review_id)]
    requirements = [
        {"req_id": r.req_id, "text": r.text, "category": r.category} for r in review.requirements
    ]
    trace = json.loads(review.trace_json) if review.trace_json else []

    current_state = {
        "run_id": review_id,
        "raw_input": review.raw_input or "",
        "requirements": requirements,
        "current_req": None,
        "retrieved_clauses": {},
        "findings": findings,
        "conflict_findings": [],
        "approvals": decisions_dict,
        "report": None,
        "trace": trace,
        "status": "waiting_for_human",
        "security_warnings": [],
        "errors": [],
    }

    try:
        # 3. Resume LangGraph to generate report
        resumed_state = resume_review_with_decisions(
            run_id=review_id,
            approvals=decisions_dict,
            current_state=current_state,
        )

        report = resumed_state.get("report") or {}
        report_md = report.get("markdown_content", "")
        approved_count = report.get("total_findings_approved", 0)

        # 4. Save final report and mark review completed
        repo.complete_review(
            review_id=review_id,
            report_md=report_md,
            approved_count=approved_count,
            trace=resumed_state.get("trace", trace),
        )

        return {
            "status": "completed",
            "review_id": review_id,
            "approved_findings_count": approved_count,
            "report_md": report_md,
            "report": report,
        }
    except Exception as e:
        logger.error("Error resuming review graph for %s: %s", review_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{review_id}/report", dependencies=[Depends(verify_api_key)])
def download_report(
    review_id: str,
    format: Literal["md", "pdf"] = Query(default="md"),
    db=Depends(get_db),
):
    """Download the finalized review report in Markdown or PDF format."""
    repo = ReviewRepository(db)
    review = repo.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review '{review_id}' not found.")

    if not review.report_md:
        raise HTTPException(
            status_code=400,
            detail="Report has not been generated yet. Reviewer decisions must be submitted first.",
        )

    if format == "md":
        return Response(
            content=review.report_md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=LumenReview_{review_id}.md"},
        )
    elif format == "pdf":
        findings = [serialize_finding(f) for f in repo.get_review_findings(review_id)]
        approved_findings = [
            f for f in findings if f.get("human_decision") in ["approved", "edited"]
        ]

        report_data = {
            "review_id": review_id,
            "generated_at": review.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            if review.completed_at
            else "",
            "total_requirements": review.total_requirements,
            "total_findings_flagged": review.total_findings,
            "total_findings_approved": review.approved_findings,
            "findings": approved_findings,
            "executive_summary": "Homologation review completed for automotive lighting requirements.",
            "markdown_content": review.report_md,
        }

        pdf_bytes = export_pdf_report(report_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=LumenReview_{review_id}.pdf"},
        )
