"""FastAPI router for evaluation benchmark runs and metric retrieval."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import verify_api_key
from app.db.models import EvalRunRecord
from app.db.session import get_db
from app.evaluation.runner import BenchmarkRunner

router = APIRouter(prefix="/eval", tags=["Evaluation Harness"])


class RunBenchmarkRequest(BaseModel):
    config_name: str = Field(
        default="LumenReview-Default", description="Label for benchmark configuration"
    )
    top_k: int = Field(default=5, ge=1, le=10)
    verify_citations: bool = Field(default=True)


@router.post("/run", dependencies=[Depends(verify_api_key)])
def trigger_benchmark(req: RunBenchmarkRequest, db=Depends(get_db)):
    """Run benchmark against data/eval/eval_set.jsonl and compute evaluation metrics."""
    try:
        runner = BenchmarkRunner(db=db)
        results = runner.run_benchmark(
            config_name=req.config_name,
            top_k=req.top_k,
            verify_citations=req.verify_citations,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/runs", dependencies=[Depends(verify_api_key)])
def list_eval_runs(limit: int = 50, db=Depends(get_db)):
    """List historical evaluation runs."""
    records = db.query(EvalRunRecord).order_by(EvalRunRecord.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "config_name": r.config_name,
            "dataset_name": r.dataset_name,
            "f1_score": r.f1_score,
            "precision": r.precision,
            "recall": r.recall,
            "citation_correctness": r.citation_correctness,
            "hallucination_rate": r.hallucination_rate,
            "avg_latency_ms": r.avg_latency_ms,
            "total_cost_usd": r.total_cost_usd,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/runs/{eval_id}", dependencies=[Depends(verify_api_key)])
def get_eval_run_details(eval_id: str, db=Depends(get_db)):
    """Fetch complete benchmark details and item results by eval_id."""
    record = db.query(EvalRunRecord).filter(EvalRunRecord.id == eval_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Eval run '{eval_id}' not found.")

    return record.get_metrics()
