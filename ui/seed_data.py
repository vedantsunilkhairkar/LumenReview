"""Seed demo data to guarantee a rich first-launch experience."""

import json

from app.db.models import (
    DecisionRecord,
    EvalRunRecord,
    FindingRecord,
    RequirementRecord,
    ReviewRunRecord,
)
from app.db.session import SessionLocal, init_db


def _seed_demo_review(db):
    review_id = "REV-2026-DEMO-01"
    review = ReviewRunRecord(
        id=review_id,
        status="completed",
        raw_input="NextGen Adaptive Matrix LED Lighting Specification",
        total_requirements=7,
        total_findings=6,
        approved_findings=5,
        report_md=(
            "# LumenReview Homologation Review Report\n"
            "**Review Run ID**: `REV-2026-DEMO-01`  \n"
            "**Evaluator**: LumenReview Agent v0.1.0 (Human Supervised)  \n\n"
            "## 1. Executive Summary\n"
            "The homologation review analyzed the NextGen Matrix LED Headlamp specifications against "
            "UNECE Regulation No. 48, UNECE Regulation No. 112, and US FMVSS 108. Five regulatory and "
            "cost-optimization findings were confirmed and approved, identifying €280,000 in tooling "
            "scrappage risk mitigation and €2.85/unit in BOM cost-out potential.\n\n"
            "## 2. Review Metrics, Homologation Gate & Financial Impact\n\n"
            "| Metric | Value |\n"
            "|---|---|\n"
            "| Total Requirements Ingested | 7 |\n"
            "| Initial Issues Flagged | 6 |\n"
            "| Approved by Reviewer | 5 |\n"
            "| Cross-Jurisdiction Arbitrage (UNECE vs. FMVSS 108) | 1 issue flagged |\n"
            "| Value Engineering Cost-Out Opportunities | 1 proposal |\n"
            "| Tooling Scrappage Risk Mitigated | **€280,000.00** |\n"
            "| Direct BOM Cost-Out Potential | **€2.85 / unit** |\n"
            "| Citation Verification Rate | 100% Programmatically Verified |\n\n"
            "## 3. Approved Regulatory Findings & Corrective Rewrites\n"
            "- **[CRITICAL] Missing Headlamp Cleaning for Flux > 2,000 lm** (UNECE R48 Clause 6.2.7.3)\n"
            "- **[CRITICAL] Direction-Indicator Flashing Frequency Out of Bounds** (UNECE R48 Clause 6.5.9)\n"
            "- **[CRITICAL] FMVSS 108 vs UNECE R48 Arbitrage: Turn Signal Area < 22 cm²** (FMVSS 108 S6.1.1.4, ⚠️ Tooling Risk: €280,000)\n"
            "- **[MAJOR] Subjective Cut-off Aiming Criteria** (UNECE R48 Clause 6.2.6.1.2)\n"
            "- **[MINOR] Value Engineering: Over-Engineered LED Binning Spec** (💰 BOM Savings: €2.85/unit)\n"
        ),
        trace_json=json.dumps(
            [
                {
                    "node": "ingest_requirements",
                    "status": "success",
                    "latency_ms": 12.4,
                    "prompt_tokens": 120,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "timestamp": "2026-10-17 11:00:01",
                    "details": "Ingested 5 requirements.",
                },
                {
                    "node": "sanitize",
                    "status": "success",
                    "latency_ms": 8.1,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "timestamp": "2026-10-17 11:00:02",
                    "details": "0 prompt injection patterns detected.",
                },
                {
                    "node": "retrieve",
                    "status": "success",
                    "latency_ms": 45.2,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "timestamp": "2026-10-17 11:00:03",
                    "details": "Hybrid retrieval matched 15 clauses.",
                },
                {
                    "node": "analyze",
                    "status": "success",
                    "latency_ms": 320.5,
                    "prompt_tokens": 1450,
                    "completion_tokens": 380,
                    "cost_usd": 0.000223,
                    "timestamp": "2026-10-17 11:00:04",
                    "details": "Flagged 4 candidate findings.",
                },
                {
                    "node": "verify_citations",
                    "status": "success",
                    "latency_ms": 15.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "timestamp": "2026-10-17 11:00:05",
                    "details": "Verified 4 citations (100% verified).",
                },
                {
                    "node": "conflict_check",
                    "status": "success",
                    "latency_ms": 110.2,
                    "prompt_tokens": 420,
                    "completion_tokens": 90,
                    "cost_usd": 0.000058,
                    "timestamp": "2026-10-17 11:00:06",
                    "details": "Detected 1 pairwise contradiction.",
                },
                {
                    "node": "human_review",
                    "status": "success",
                    "latency_ms": 5.4,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_usd": 0.0,
                    "timestamp": "2026-10-17 11:02:10",
                    "details": "Reviewer approved 3 findings, rejected 1.",
                },
                {
                    "node": "generate_report",
                    "status": "success",
                    "latency_ms": 190.8,
                    "prompt_tokens": 850,
                    "completion_tokens": 410,
                    "cost_usd": 0.000187,
                    "timestamp": "2026-10-17 11:02:12",
                    "details": "Compiled final Markdown and PDF report.",
                },
            ]
        ),
    )
    db.add(review)

    # Requirements
    reqs = [
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-001",
            text="The principal dipped-beam LED modules shall produce an objective luminous flux of 2,500 lumens.",
            category="Headlamp",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-002",
            text="Front direction indicators shall flash at an operating frequency of 2.5 Hz.",
            category="Turn Signal",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-003",
            text="The vertical cut-off line of the passing beam must maintain sufficient inclination under normal load conditions.",
            category="Headlamp",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-004",
            text="Daytime running lamps shall remain illuminated continuously whenever the engine is active, even if main headlamps are switched on.",
            category="DRL",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-005",
            text="The stop lamp apparent surface shall be located at a mounting height of 280 mm above the ground.",
            category="Signal",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-006",
            text="The front turn signal optical surface area shall be 15 cm2 integrated within the headlamp bezel for global platform vehicles.",
            category="Signal",
        ),
        RequirementRecord(
            review_id=review_id,
            req_id="REQ-007",
            text="Principal high-beam LED emitters shall require single-bin chromaticity sorting and liquid cooling at 150°C junction temperature.",
            category="Headlamp",
        ),
    ]
    db.add_all(reqs)

    # Findings
    findings = [
        FindingRecord(
            id="F-REQ001-1",
            review_id=review_id,
            req_id="REQ-001",
            type="non_compliant",
            severity="critical",
            market_scope="UNECE",
            financial_impact_eur=450000.0,
            financial_impact_type="warranty_risk",
            title="Missing Mandatory Headlamp Cleaning for Flux > 2,000 lm",
            explanation="Dipped-beam luminous flux of 2,500 lm strictly requires an automated headlamp cleaning device per UNECE R48 Clause 6.2.7.3.",
            chunk_id="R48-6.2.7",
            quote="objective luminous flux which exceeds 2,000 lumens must only be installed in conjunction with the installation of headlamp cleaning devices",
            document="UNECE Regulation No. 48",
            clause_id="6.2.7.3",
            suggested_rewrite="The principal dipped-beam LED modules shall produce an objective luminous flux of 2,500 lumens and shall be equipped with a headlamp cleaning system conforming to Regulation No. 45.",
            diff_explanation="Added mandatory headlamp cleaner requirement.",
            confidence=0.98,
            citation_verified=True,
            citation_note="VERIFIED: Verbatim quote confirmed in UNECE Regulation No. 48 (Clause 6.2.7.3).",
            human_decision="approved",
            human_notes="Approved for homologation sign-off. Compliance package updated.",
        ),
        FindingRecord(
            id="F-REQ002-1",
            review_id=review_id,
            req_id="REQ-002",
            type="non_compliant",
            severity="critical",
            market_scope="UNECE",
            title="Direction-Indicator Flash Rate Exceeds Statutory Limit",
            explanation="Specified flash rate of 2.5 Hz exceeds the maximum statutory upper bound of 2.0 Hz (1.5 +/- 0.5 Hz) mandated by UNECE R48 Clause 6.5.9.",
            chunk_id="R48-6.5.9",
            quote="flashing frequency shall be 90 +/- 30 periods per minute (1.5 +/- 0.5 Hz)",
            document="UNECE Regulation No. 48",
            clause_id="6.5.9",
            suggested_rewrite="Front direction indicators shall flash at an operating frequency of 1.5 +/- 0.5 Hz (90 +/- 30 periods per minute).",
            diff_explanation="Aligned flashing frequency with 1.5 Hz statutory center frequency.",
            confidence=0.99,
            citation_verified=True,
            citation_note="VERIFIED: Verbatim quote confirmed in UNECE Regulation No. 48 (Clause 6.5.9).",
            human_decision="approved",
            human_notes="Flashing frequency revised in BCM software calibration parameter.",
        ),
        FindingRecord(
            id="F-REQ003-1",
            review_id=review_id,
            req_id="REQ-003",
            type="ambiguous",
            severity="major",
            market_scope="Global",
            title="Subjective Term 'Sufficient Inclination' in Headlamp Cut-off Aiming",
            explanation="'Sufficient inclination' lacks objective numerical tolerances. UNECE R48 Clause 6.2.6 requires initial downward inclination between -0.5% and -2.5% depending on mounting height.",
            chunk_id="R48-6.2.6",
            quote="initial downward inclination of the cut-off of the dipped-beam to be set to the unladen vehicle",
            document="UNECE Regulation No. 48",
            clause_id="6.2.6.1.2",
            suggested_rewrite="The vertical cut-off line of the passing beam shall have an initial downward inclination of -1.0% +/- 0.25% at unladen vehicle curb weight.",
            diff_explanation="Replaced vague qualitative term with exact photometric angle and tolerance.",
            confidence=0.92,
            citation_verified=True,
            citation_note="VERIFIED: Verbatim quote confirmed in UNECE Regulation No. 48 (Clause 6.2.6.1.2).",
            human_decision="edited",
            human_notes="Updated initial aim parameter to -1.2% for SUV chassis.",
        ),
        FindingRecord(
            id="F-REQ005-1",
            review_id=review_id,
            req_id="REQ-005",
            type="non_compliant",
            severity="major",
            market_scope="UNECE",
            title="Stop Lamp Mounting Height Below Minimum Statutory Limit",
            explanation="Specified mounting height of 280 mm is below the 350 mm statutory minimum specified in UNECE R48 Clause 6.7.4.2.",
            chunk_id="R48-6.7.4",
            quote="not less than 350 mm and not more than 1,500 mm above the ground",
            document="UNECE Regulation No. 48",
            clause_id="6.7.4.2",
            suggested_rewrite="The stop lamp apparent surface shall be located at a mounting height of not less than 350 mm above the ground.",
            diff_explanation="Corrected lower mounting threshold.",
            confidence=0.95,
            citation_verified=True,
            citation_note="VERIFIED: Verbatim quote confirmed in UNECE Regulation No. 48 (Clause 6.7.4.2).",
            human_decision="rejected",
            human_notes="Overruled: Vehicle package uses Category N3G off-road waiver for temporary auxiliary test rig.",
        ),
        FindingRecord(
            id="F-REQ006-1",
            review_id=review_id,
            req_id="REQ-006",
            type="conflict",
            severity="critical",
            market_scope="Cross_Market_Conflict",
            financial_impact_eur=280000.0,
            financial_impact_type="tooling_risk",
            title="FMVSS 108 vs UNECE R48 Arbitrage: Turn Signal Lens Area Below 22 cm²",
            explanation="Front turn signal optical lens area of 15 cm2 is permissible under UNECE R48 but directly violates US FMVSS 108 S6.1.1.4 (statutory minimum 22 cm2 / 3.5 sq. in. for vehicles < 2032 mm). This prevents common global platform tooling, risking €280,000 in injection mold redesign expenses.",
            chunk_id="FMVSS108-S6.1.1.4",
            quote="must have an effective projected luminous lens area of not less than 22 cm2 (3.5 sq. in.)",
            document="Federal Motor Vehicle Safety Standard No. 108 - Lamps, Reflective Devices, and Associated Equipment (FMVSS 108)",
            clause_id="S6.1.1.4",
            suggested_rewrite="The front turn signal lamp shall have an effective projected luminous lens area of not less than 22 cm2 (3.5 sq. in.) to ensure unified UNECE R48 and US FMVSS 108 homologation compliance.",
            diff_explanation="Harmonized turn signal optical area to satisfy US FMVSS 108 without breaking UNECE compliance, avoiding tool modification.",
            confidence=0.98,
            citation_verified=True,
            citation_note="VERIFIED: Verbatim quote confirmed in FMVSS 108 (Clause S6.1.1.4).",
            human_decision="approved",
            human_notes="Approved: Headlamp bezel CAD updated to 23 cm2 lens aperture for common platform tooling.",
        ),
        FindingRecord(
            id="F-REQ007-1",
            review_id=review_id,
            req_id="REQ-007",
            type="value_engineering",
            severity="minor",
            market_scope="Global",
            financial_impact_eur=2.85,
            financial_impact_type="bom_cost_out",
            title="Value Engineering: Over-Engineered LED Binning Spec (€2.85/unit BOM Savings)",
            explanation="Requirement specifies premium single-bin LED chromaticity tolerances and active liquid thermal headroom. Automotive Grade 1 (AEC-Q102) with 3-step MacAdam ellipse binning satisfies all UNECE/FMVSS colorimetry regulations at an estimated Bill-of-Materials (BOM) cost reduction of €2.85 per headlamp unit.",
            suggested_rewrite="LED emitters shall conform to standard 3-step MacAdam ellipse chromaticity grouping with AEC-Q102 passive conduction thermal management.",
            diff_explanation="Relaxed over-engineered LED procurement constraints to standard automotive AEC-Q102, yielding €2.85/unit direct BOM savings.",
            confidence=0.94,
            citation_verified=True,
            citation_note="N/A: General engineering analysis (no clause cited).",
            human_decision="approved",
            human_notes="Approved: Purchasing confirmed €2.85/unit savings across 250,000 annual production volume (€712,500 total).",
        ),
    ]
    db.add_all(findings)

    # Decisions audit log
    decisions = [
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ001-1",
            decision="approved",
            notes="Confirmed mandatory cleaning device.",
        ),
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ002-1",
            decision="approved",
            notes="Corrected nominal flash rate.",
        ),
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ003-1",
            decision="edited",
            notes="Modified initial aim to -1.2%.",
        ),
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ005-1",
            decision="rejected",
            notes="Off-road vehicle exemption applicable.",
        ),
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ006-1",
            decision="approved",
            notes="Harmonized lens area to 23 cm2 for FMVSS 108.",
        ),
        DecisionRecord(
            review_id=review_id,
            finding_id="F-REQ007-1",
            decision="approved",
            notes="Accepted BOM cost-out proposal (€2.85/unit savings).",
        ),
    ]
    db.add_all(decisions)


def _seed_eval_runs(db):
    eval1 = EvalRunRecord(
        id="EV-20261017-HYBRID",
        config_name="LumenReview-Hybrid-Verified (RRF + Verifier, top_k=5)",
        dataset_name="eval_set.jsonl",
        f1_score=0.941,
        precision=0.947,
        recall=0.935,
        citation_correctness=1.00,
        hallucination_rate=0.00,
        avg_latency_ms=342.5,
        total_cost_usd=0.000421,
        metrics_json=json.dumps(
            {
                "eval_id": "EV-20261017-HYBRID",
                "config_name": "LumenReview-Hybrid-Verified (RRF + Verifier, top_k=5)",
                "f1_score": 0.941,
                "precision": 0.947,
                "recall": 0.935,
                "citation_correctness": 1.00,
                "hallucination_rate": 0.00,
                "avg_latency_ms": 342.5,
                "total_cost_usd": 0.000421,
                "item_results": [
                    {
                        "req_id": "EVAL-001",
                        "text": "Dipped-beam flux 2500 lumens.",
                        "expected_issues": ["non_compliant"],
                        "predicted_issues": ["non_compliant"],
                        "is_match": True,
                        "latency_ms": 310.2,
                    },
                    {
                        "req_id": "EVAL-002",
                        "text": "Direction-indicator flashing 2.5 Hz.",
                        "expected_issues": ["non_compliant"],
                        "predicted_issues": ["non_compliant"],
                        "is_match": True,
                        "latency_ms": 290.1,
                    },
                    {
                        "req_id": "EVAL-003",
                        "text": "Fog lamps sufficient illumination.",
                        "expected_issues": ["ambiguous"],
                        "predicted_issues": ["ambiguous"],
                        "is_match": True,
                        "latency_ms": 305.4,
                    },
                    {
                        "req_id": "EVAL-004",
                        "text": "Weatherproof and never fail.",
                        "expected_issues": ["non_testable"],
                        "predicted_issues": ["non_testable"],
                        "is_match": True,
                        "latency_ms": 340.0,
                    },
                    {
                        "req_id": "EVAL-005",
                        "text": "DRL remain on with headlamp.",
                        "expected_issues": ["non_compliant"],
                        "predicted_issues": ["non_compliant"],
                        "is_match": True,
                        "latency_ms": 330.1,
                    },
                ],
            }
        ),
    )
    eval2 = EvalRunRecord(
        id="EV-20261017-DENSE",
        config_name="Baseline-Dense-Only (No BM25, top_k=3)",
        dataset_name="eval_set.jsonl",
        f1_score=0.782,
        precision=0.810,
        recall=0.756,
        citation_correctness=0.857,
        hallucination_rate=0.143,
        avg_latency_ms=485.0,
        total_cost_usd=0.000385,
        metrics_json=json.dumps(
            {
                "eval_id": "EV-20261017-DENSE",
                "config_name": "Baseline-Dense-Only (No BM25, top_k=3)",
                "f1_score": 0.782,
                "precision": 0.810,
                "recall": 0.756,
                "citation_correctness": 0.857,
                "hallucination_rate": 0.143,
                "avg_latency_ms": 485.0,
                "total_cost_usd": 0.000385,
                "item_results": [],
            }
        ),
    )
    db.add_all([eval1, eval2])


def seed_database_if_empty():
    """Seed initial sample review, findings, and evaluation benchmarks."""
    init_db()
    db = SessionLocal()
    try:
        demo_review = (
            db.query(ReviewRunRecord).filter(ReviewRunRecord.id == "REV-2026-DEMO-01").first()
        )
        if not demo_review:
            _seed_demo_review(db)

        existing_evals = db.query(EvalRunRecord).count()
        if existing_evals == 0:
            _seed_eval_runs(db)

        db.commit()
    finally:
        db.close()
