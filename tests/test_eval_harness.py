"""Evaluation harness and CI regression threshold guard tests."""

from app.evaluation.dataset import EvalDatasetLoader
from app.evaluation.metrics import (
    compute_issue_classification_metrics,
    compute_retrieval_metrics,
)
from app.evaluation.runner import BenchmarkRunner


def test_eval_dataset_schema_and_loading():
    loader = EvalDatasetLoader()
    items = loader.load()

    assert len(items) >= 10
    for item in items:
        assert item.req_id.startswith("EVAL-")
        assert len(item.text) > 10
        assert isinstance(item.expected_issues, list)
        assert isinstance(item.expected_clause_ids, list)


def test_metrics_computations():
    preds = [["non_compliant"], ["ambiguous"], []]
    targets = [["non_compliant"], ["ambiguous"], []]
    metrics = compute_issue_classification_metrics(preds, targets)
    assert metrics["f1_score"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0

    retrieved = [["6.2.7.3", "5.15"], ["6.5.9"]]
    expected = [["6.2.7.3"], ["6.5.9"]]
    ret_metrics = compute_retrieval_metrics(retrieved, expected, k=2)
    assert ret_metrics["hit_at_2"] == 1.0
    assert ret_metrics["mrr"] == 1.0


def test_benchmark_runner_and_ci_regression_guard():
    """CI Regression Test: Fails CI if F1 score falls below threshold."""
    runner = BenchmarkRunner()
    results = runner.run_benchmark(
        config_name="CI-Regression-Suite", top_k=5, verify_citations=True
    )

    assert results["total_samples"] >= 10
    assert results["task_completion_rate"] == 1.0

    # Strict CI quality thresholds
    assert results["f1_score"] >= 0.70, (
        f"F1 score {results['f1_score']} fell below CI regression threshold 0.70!"
    )
    assert results["citation_correctness"] >= 0.80, (
        f"Citation accuracy {results['citation_correctness']} fell below 0.80!"
    )
    assert results["hallucination_rate"] <= 0.20, (
        f"Hallucination rate {results['hallucination_rate']} exceeded 0.20!"
    )
