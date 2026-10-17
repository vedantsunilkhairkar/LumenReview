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
        total_requirements=5,
        total_findings=4,
        approved_findings=3,
        report_md=(
            "# LumenReview Homologation Review Report\n"
            "**Review Run ID**: `REV-2026-DEMO-01`  \n"
            "**Evaluator**: LumenReview Agent v0.1.0 (Human Supervised)  \n\n"
            "## 1. Executive Summary\n"
            "The homologation review analyzed the NextGen Matrix LED Headlamp specifications against "
            "UNECE Regulation No. 48 and No. 112. Three regulatory deficiencies were confirmed and approved.\n\n"
            "## 2. Approved Regulatory Findings\n"
            "- **[CRITICAL] Missing Headlamp Cleaning for Flux > 2,000 lm** (UNECE R48 Clause 6.2.7.3)\n"
            "- **[CRITICAL] Direction-Indicator Flashing Frequency Out of Bounds** (UNECE R48 Clause 6.5.9)\n"
            "- **[MAJOR] Subjective Cut-off Aiming Criteria** (UNECE R48 Clause 6.2.6.1.2)\n"
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
