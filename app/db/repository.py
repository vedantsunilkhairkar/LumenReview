"""Repository layer for database operations."""

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import DecisionRecord, FindingRecord, RequirementRecord, ReviewRunRecord


def utcnow():
    return datetime.now(UTC)


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_review(
        self,
        review_id: str,
        raw_input: str,
        requirements: list[dict[str, Any]],
        status: str = "initialized",
    ) -> ReviewRunRecord:
        review = ReviewRunRecord(
            id=review_id,
            status=status,
            raw_input=raw_input,
            total_requirements=len(requirements),
            created_at=utcnow(),
        )
        self.db.add(review)

        for req in requirements:
            r_rec = RequirementRecord(
                review_id=review_id,
                req_id=req["req_id"],
                text=req["text"],
                category=req.get("category", "Lighting"),
            )
            self.db.add(r_rec)

        self.db.commit()
        self.db.refresh(review)
        return review

    def save_findings(
        self,
        review_id: str,
        findings: list[dict[str, Any]],
        trace: list[dict[str, Any]] | None = None,
        status: str = "waiting_for_human",
    ):
        review = self.db.query(ReviewRunRecord).filter(ReviewRunRecord.id == review_id).first()
        if not review:
            return

        review.status = status
        review.total_findings = len(findings)
        if trace:
            review.trace_json = json.dumps(trace)

        # Remove previous findings if re-analyzing
        self.db.query(FindingRecord).filter(FindingRecord.review_id == review_id).delete()

        for f in findings:
            evidence = f.get("evidence") or {}
            rewrite = f.get("suggested_rewrite") or {}

            f_rec = FindingRecord(
                id=f["id"],
                review_id=review_id,
                req_id=f["req_id"],
                type=f.get("type", "ambiguous"),
                severity=f.get("severity", "minor"),
                title=f.get("title", ""),
                explanation=f.get("explanation", ""),
                market_scope=f.get("market_scope", "Global"),
                financial_impact_eur=f.get("financial_impact_eur"),
                financial_impact_type=f.get("financial_impact_type", "none"),
                chunk_id=evidence.get("chunk_id"),
                quote=evidence.get("quote"),
                document=evidence.get("document"),
                clause_id=evidence.get("clause_id"),
                suggested_rewrite=rewrite.get("text"),
                diff_explanation=rewrite.get("diff_explanation"),
                confidence=f.get("confidence", 0.9),
                citation_verified=f.get("citation_verified", False),
                citation_note=f.get("citation_verification_note"),
                human_decision=f.get("human_decision", "pending"),
                human_notes=f.get("human_notes"),
            )
            self.db.add(f_rec)

        self.db.commit()

    def record_decisions(
        self,
        review_id: str,
        decisions_map: dict[str, dict[str, Any]],
    ):
        for finding_id, dec in decisions_map.items():
            action = dec.get("decision", "approved")
            notes = dec.get("notes")
            edited_rewrite = dec.get("edited_rewrite")

            # Update finding record
            finding = (
                self.db.query(FindingRecord)
                .filter(FindingRecord.review_id == review_id, FindingRecord.id == finding_id)
                .first()
            )
            if finding:
                finding.human_decision = action
                finding.human_notes = notes
                if edited_rewrite:
                    finding.suggested_rewrite = edited_rewrite

            # Add audit decision log
            d_rec = DecisionRecord(
                review_id=review_id,
                finding_id=finding_id,
                decision=action,
                notes=notes,
                edited_rewrite=edited_rewrite,
                decided_at=utcnow(),
            )
            self.db.add(d_rec)

        self.db.commit()

    def complete_review(
        self,
        review_id: str,
        report_md: str,
        approved_count: int,
        trace: list[dict[str, Any]] | None = None,
    ):
        review = self.db.query(ReviewRunRecord).filter(ReviewRunRecord.id == review_id).first()
        if review:
            review.status = "completed"
            review.report_md = report_md
            review.approved_findings = approved_count
            review.completed_at = utcnow()
            if trace:
                review.trace_json = json.dumps(trace)
            self.db.commit()

    def get_review(self, review_id: str) -> ReviewRunRecord | None:
        return self.db.query(ReviewRunRecord).filter(ReviewRunRecord.id == review_id).first()

    def list_reviews(self, limit: int = 50) -> list[ReviewRunRecord]:
        return (
            self.db.query(ReviewRunRecord)
            .order_by(ReviewRunRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_review_findings(self, review_id: str) -> list[FindingRecord]:
        return self.db.query(FindingRecord).filter(FindingRecord.review_id == review_id).all()

    def get_audit_trail(self, review_id: str) -> list[DecisionRecord]:
        return (
            self.db.query(DecisionRecord)
            .filter(DecisionRecord.review_id == review_id)
            .order_by(DecisionRecord.decided_at.asc())
            .all()
        )
