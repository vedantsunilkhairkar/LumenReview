"""SQLAlchemy ORM models for requirements, reviews, findings, and evaluation runs."""

import json
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


def utcnow():
    return datetime.now(UTC)


class ReviewRunRecord(Base):
    __tablename__ = "review_runs"

    id = Column(String(64), primary_key=True)
    status = Column(
        String(32), default="initialized"
    )  # initialized | analyzing | waiting_for_human | completed | failed
    raw_input = Column(Text, nullable=True)
    total_requirements = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    approved_findings = Column(Integer, default=0)
    report_md = Column(Text, nullable=True)
    trace_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    requirements = relationship(
        "RequirementRecord", back_populates="review", cascade="all, delete-orphan"
    )
    findings = relationship("FindingRecord", back_populates="review", cascade="all, delete-orphan")
    decisions = relationship(
        "DecisionRecord", back_populates="review", cascade="all, delete-orphan"
    )


class RequirementRecord(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), ForeignKey("review_runs.id"), nullable=False, index=True)
    req_id = Column(String(64), nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String(64), default="Lighting")
    created_at = Column(DateTime, default=utcnow)

    review = relationship("ReviewRunRecord", back_populates="requirements")


class FindingRecord(Base):
    __tablename__ = "findings"

    review_id = Column(String(64), ForeignKey("review_runs.id"), primary_key=True, index=True)
    id = Column(String(64), primary_key=True)
    req_id = Column(String(64), nullable=False, index=True)
    type = Column(
        String(32), nullable=False
    )  # ambiguous | missing_info | conflict | non_testable | non_compliant | value_engineering
    severity = Column(String(16), nullable=False)  # critical | major | minor | info
    title = Column(String(256), nullable=False)
    explanation = Column(Text, nullable=False)
    market_scope = Column(
        String(64), default="Global"
    )  # Global | UNECE | FMVSS_108 | Cross_Market_Conflict
    financial_impact_eur = Column(Float, nullable=True)  # EUR value
    financial_impact_type = Column(
        String(32), default="none"
    )  # tooling_risk | bom_cost_out | warranty_risk | none
    chunk_id = Column(String(64), nullable=True)
    quote = Column(Text, nullable=True)
    document = Column(String(128), nullable=True)
    clause_id = Column(String(64), nullable=True)
    suggested_rewrite = Column(Text, nullable=True)
    diff_explanation = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    citation_verified = Column(Boolean, default=False)
    citation_note = Column(Text, nullable=True)
    human_decision = Column(String(16), default="pending")  # pending | approved | rejected | edited
    human_notes = Column(Text, nullable=True)

    review = relationship("ReviewRunRecord", back_populates="findings")


class DecisionRecord(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), ForeignKey("review_runs.id"), nullable=False, index=True)
    finding_id = Column(String(64), nullable=False)
    decision = Column(String(16), nullable=False)  # approved | rejected | edited
    notes = Column(Text, nullable=True)
    edited_rewrite = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=utcnow)

    review = relationship("ReviewRunRecord", back_populates="decisions")


class EvalRunRecord(Base):
    __tablename__ = "eval_runs"

    id = Column(String(64), primary_key=True)
    config_name = Column(String(128), nullable=False)
    dataset_name = Column(String(128), default="eval_set.jsonl")
    f1_score = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    citation_correctness = Column(Float, default=0.0)
    hallucination_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    total_cost_usd = Column(Float, default=0.0)
    metrics_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    def get_metrics(self) -> dict:
        return json.loads(self.metrics_json) if self.metrics_json else {}
