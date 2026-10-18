"""Pydantic v2 schemas for requirements review, findings, evidence, and rewrites."""

from typing import Literal

from pydantic import BaseModel, Field

IssueType = Literal[
    "ambiguous",
    "missing_info",
    "conflict",
    "non_testable",
    "non_compliant",
    "value_engineering",
]

Severity = Literal["critical", "major", "minor", "info"]

ReviewStatus = Literal["pending", "approved", "rejected", "edited"]

MarketScope = Literal["Global", "UNECE", "FMVSS_108", "Cross_Market_Conflict"]
FinancialImpactType = Literal["tooling_risk", "bom_cost_out", "warranty_risk", "none"]


class Evidence(BaseModel):
    chunk_id: str = Field(..., description="ID of the retrieved regulation chunk")
    quote: str = Field(..., description="Exact or verbatim short quote from the regulation chunk")
    document: str = Field(default="UNECE Regulation", description="Regulation document name")
    clause_id: str = Field(default="", description="Specific clause number (e.g. 6.2.6.1.2)")
    page: int = Field(default=1, description="Source page number if available")


class SuggestedRewrite(BaseModel):
    text: str = Field(..., description="Precise, compliant, and testable suggested rewrite")
    diff_explanation: str = Field(
        ..., description="Brief rationale explaining why this rewrite resolves the issue"
    )


class FindingItem(BaseModel):
    id: str = Field(..., description="Unique finding ID (e.g. F-REQ01-1)")
    req_id: str = Field(..., description="Identifier of the requirement being reviewed")
    type: IssueType = Field(..., description="Taxonomy classification of the detected issue")
    severity: Severity = Field(..., description="Impact severity of the finding")
    title: str = Field(..., description="Concise summary title of the finding")
    explanation: str = Field(
        ..., description="Detailed engineering rationale of the deficiency or non-compliance"
    )
    market_scope: MarketScope | None = Field(
        default="Global", description="Target market regulatory scope or conflict classification"
    )
    financial_impact_eur: float | None = Field(
        default=None,
        description="Estimated financial impact in Euros (tooling risk or BOM savings)",
    )
    financial_impact_type: FinancialImpactType | None = Field(
        default="none",
        description="Category of financial impact: tooling_risk | bom_cost_out | warranty_risk | none",
    )
    evidence: Evidence | None = Field(
        default=None, description="Direct cited evidence from retrieved regulation clauses"
    )
    suggested_rewrite: SuggestedRewrite | None = Field(
        default=None, description="Recommended engineering rewrite resolving the issue"
    )
    confidence: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Model confidence score in [0.0, 1.0]"
    )
    citation_verified: bool = Field(
        default=False,
        description="Whether the cited chunk and quote were programmatically verified",
    )
    citation_verification_note: str | None = Field(
        default=None, description="Verification details or error explanation"
    )
    human_decision: ReviewStatus = Field(
        default="pending",
        description="Human reviewer decision: pending | approved | rejected | edited",
    )
    human_notes: str | None = Field(
        default=None, description="Optional notes or modifications provided by the reviewer"
    )


class RequirementItem(BaseModel):
    req_id: str = Field(..., description="Requirement identifier (e.g. REQ-001)")
    text: str = Field(..., description="Raw requirement statement")
    category: str | None = Field(
        default="Lighting", description="Subsystem (e.g. Headlamp, Turn Signal, DRL)"
    )


class RequirementAnalysisResult(BaseModel):
    req_id: str
    issues: list[FindingItem] = Field(default_factory=list)
    compliance_summary: str = Field(default="Review complete.")


class ConflictAnalysisResult(BaseModel):
    conflicts: list[FindingItem] = Field(default_factory=list)


class FinalReport(BaseModel):
    review_id: str
    title: str
    generated_at: str
    total_requirements: int
    total_findings_flagged: int
    total_findings_approved: int
    findings: list[FindingItem]
    executive_summary: str
    markdown_content: str
