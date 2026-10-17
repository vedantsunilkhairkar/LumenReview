"""Benchmark runner for executing evaluation matrix and comparing configurations."""

import json
import time
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.agents.graph import execute_review_analysis
from app.db.models import EvalRunRecord
from app.db.session import SessionLocal
from app.evaluation.dataset import EvalDatasetLoader, EvalItem
from app.evaluation.metrics import (
    compute_citation_and_hallucination_metrics,
    compute_issue_classification_metrics,
    compute_latency_percentiles,
    compute_retrieval_metrics,
)


class BenchmarkRunner:
    def __init__(self, db: Session | None = None):
        self.db = db
        self.dataset_loader = EvalDatasetLoader()

    def run_benchmark(
        self,
        config_name: str = "LumenReview-Default",
        top_k: int = 5,
        verify_citations: bool = True,
    ) -> dict[str, Any]:
        items: list[EvalItem] = self.dataset_loader.load()
        if not items:
            raise ValueError("No evaluation items loaded from dataset.")

        pred_issues_per_item: list[list[str]] = []
        expected_issues_per_item: list[list[str]] = []
        retrieved_clauses_per_item: list[list[str]] = []
        expected_clauses_per_item: list[list[str]] = []
        all_findings: list[dict[str, Any]] = []
        item_latencies_ms: list[float] = []
        item_results: list[dict[str, Any]] = []

        total_cost = 0.0
        successful_runs = 0

        for item in items:
            t0 = time.time()
            run_id = f"EVAL-{uuid.uuid4().hex[:6].upper()}"

            # Execute pipeline
            state = execute_review_analysis(
                run_id=run_id,
                raw_input=f"{item.req_id}: {item.text}",
            )
            elapsed_ms = (time.time() - t0) * 1000
            item_latencies_ms.append(elapsed_ms)

            findings = state.get("findings", [])
            retrieved_map = state.get("retrieved_clauses", {})
            retrieved_list = retrieved_map.get(item.req_id, [])
            retrieved_cids = [c.get("clause_id", "") for c in retrieved_list]

            preds = [f.get("type") for f in findings if f.get("type")]
            pred_issues_per_item.append(preds)
            expected_issues_per_item.append(item.expected_issues)

            retrieved_clauses_per_item.append(retrieved_cids)
            expected_clauses_per_item.append(item.expected_clause_ids)

            all_findings.extend(findings)
            successful_runs += 1

            for step in state.get("trace", []):
                total_cost += step.get("cost_usd", 0.0)

            # Failure / Discrepancy tracking
            is_match = set(preds) == set(item.expected_issues)
            item_results.append(
                {
                    "req_id": item.req_id,
                    "text": item.text,
                    "expected_issues": item.expected_issues,
                    "predicted_issues": preds,
                    "is_match": is_match,
                    "latency_ms": round(elapsed_ms, 2),
                    "findings_count": len(findings),
                }
            )

        # Calculate all metrics
        issue_metrics = compute_issue_classification_metrics(
            pred_issues_per_item, expected_issues_per_item
        )
        retrieval_metrics = compute_retrieval_metrics(
            retrieved_clauses_per_item, expected_clauses_per_item, k=top_k
        )
        citation_metrics = compute_citation_and_hallucination_metrics(all_findings)
        latency_metrics = compute_latency_percentiles(item_latencies_ms)

        completion_rate = round(successful_runs / len(items), 4)

        result_summary = {
            "eval_id": f"EV-{time.strftime('%Y%m%d%H%M%S')}",
            "config_name": config_name,
            "total_samples": len(items),
            "task_completion_rate": completion_rate,
            "f1_score": issue_metrics["f1_score"],
            "precision": issue_metrics["precision"],
            "recall": issue_metrics["recall"],
            "citation_correctness": citation_metrics["citation_correctness"],
            "hallucination_rate": citation_metrics["hallucination_rate"],
            "hit_at_k": retrieval_metrics[f"hit_at_{top_k}"],
            "mrr": retrieval_metrics["mrr"],
            "latency_p50_ms": latency_metrics["latency_p50_ms"],
            "latency_p95_ms": latency_metrics["latency_p95_ms"],
            "latency_avg_ms": latency_metrics["latency_avg_ms"],
            "total_cost_usd": round(total_cost, 6),
            "item_results": item_results,
        }

        # Persist to DB if session provided
        db_session = self.db or SessionLocal()
        try:
            record = EvalRunRecord(
                id=result_summary["eval_id"],
                config_name=config_name,
                dataset_name="eval_set.jsonl",
                f1_score=result_summary["f1_score"],
                precision=result_summary["precision"],
                recall=result_summary["recall"],
                citation_correctness=result_summary["citation_correctness"],
                hallucination_rate=result_summary["hallucination_rate"],
                avg_latency_ms=result_summary["latency_avg_ms"],
                total_cost_usd=result_summary["total_cost_usd"],
                metrics_json=json.dumps(result_summary),
            )
            db_session.add(record)
            db_session.commit()
        finally:
            if not self.db:
                db_session.close()

        return result_summary
