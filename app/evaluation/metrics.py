"""Evaluation metrics calculation for automotive requirements review."""

from typing import Any

import numpy as np


def compute_retrieval_metrics(
    retrieved_clause_ids_per_item: list[list[str]],
    expected_clause_ids_per_item: list[list[str]],
    k: int = 5,
) -> dict[str, float]:
    """Compute Hit@K and Mean Reciprocal Rank (MRR) for clause retrieval."""
    hits = 0
    reciprocal_ranks = []
    total_evaluable = 0

    for retrieved, expected in zip(
        retrieved_clause_ids_per_item, expected_clause_ids_per_item, strict=False
    ):
        if not expected:
            continue
        total_evaluable += 1

        top_k_retrieved = retrieved[:k]
        has_hit = any(any(exp in r or r in exp for exp in expected) for r in top_k_retrieved)
        if has_hit:
            hits += 1

        # MRR
        rr = 0.0
        for rank, r in enumerate(retrieved, start=1):
            if any(exp in r or r in exp for exp in expected):
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

    hit_at_k = hits / total_evaluable if total_evaluable > 0 else 1.0
    mrr = float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 1.0

    return {
        f"hit_at_{k}": round(hit_at_k, 4),
        "mrr": round(mrr, 4),
    }


def compute_issue_classification_metrics(
    predicted_issues_per_item: list[list[str]],
    expected_issues_per_item: list[list[str]],
) -> dict[str, float]:
    """Compute Precision, Recall, and F1 on issue classification."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for preds, targets in zip(predicted_issues_per_item, expected_issues_per_item, strict=False):
        pred_set = set(preds)
        target_set = set(targets)

        tp = len(pred_set.intersection(target_set))
        fp = len(pred_set - target_set)
        fn = len(target_set - pred_set)

        true_positives += tp
        false_positives += fp
        false_negatives += fn

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 1.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 1.0
    )
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def compute_citation_and_hallucination_metrics(
    all_findings: list[dict[str, Any]],
) -> dict[str, float]:
    """Compute citation correctness rate and hallucination rate."""
    total_findings = len(all_findings)
    if total_findings == 0:
        return {"citation_correctness": 1.0, "hallucination_rate": 0.0}

    findings_with_evidence = [
        f for f in all_findings if f.get("evidence") and f.get("evidence", {}).get("chunk_id")
    ]
    if not findings_with_evidence:
        return {"citation_correctness": 1.0, "hallucination_rate": 0.0}

    verified_count = sum(1 for f in findings_with_evidence if f.get("citation_verified", False))
    unverified_count = len(findings_with_evidence) - verified_count

    correctness = verified_count / len(findings_with_evidence)
    hallucination_rate = unverified_count / len(findings_with_evidence)

    return {
        "citation_correctness": round(correctness, 4),
        "hallucination_rate": round(hallucination_rate, 4),
        "total_citations_evaluated": len(findings_with_evidence),
        "verified_citations": verified_count,
    }


def compute_latency_percentiles(latencies_ms: list[float]) -> dict[str, float]:
    """Compute p50 and p95 latency in milliseconds."""
    if not latencies_ms:
        return {"latency_p50_ms": 0.0, "latency_p95_ms": 0.0, "latency_avg_ms": 0.0}

    p50 = float(np.percentile(latencies_ms, 50))
    p95 = float(np.percentile(latencies_ms, 95))
    avg = float(np.mean(latencies_ms))

    return {
        "latency_p50_ms": round(p50, 2),
        "latency_p95_ms": round(p95, 2),
        "latency_avg_ms": round(avg, 2),
    }
