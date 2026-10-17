"""Analyze node: calls LLM with strict JSON schema to evaluate requirements."""

import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.config import settings
from app.core.cost import calculate_cost, estimate_tokens
from app.core.logging import logger
from app.llm.factory import get_llm_provider
from app.llm.prompts.v1_analysis import build_analysis_prompt
from app.llm.schemas import RequirementAnalysisResult


def analyze_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: analyzes each requirement against retrieved clauses."""
    start_time = time.time()
    requirements = state.get("requirements", [])
    retrieved_map = state.get("retrieved_clauses", {})
    all_findings: list[dict[str, Any]] = []

    llm = get_llm_provider()
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for req in requirements:
        req_id = req["req_id"]
        text = req["text"]
        clauses = retrieved_map.get(req_id, [])

        prompt = build_analysis_prompt(req_id=req_id, req_text=text, retrieved_clauses=clauses)
        p_tokens = estimate_tokens(prompt)
        total_prompt_tokens += p_tokens

        try:
            result = llm.generate(prompt, response_model=RequirementAnalysisResult)
            if isinstance(result, RequirementAnalysisResult):
                for issue in result.issues:
                    issue_dict = issue.model_dump()
                    all_findings.append(issue_dict)
                c_tokens = estimate_tokens(str(result.model_dump()))
                total_completion_tokens += c_tokens
        except Exception as e:
            logger.error("Analysis error on requirement %s: %s", req_id, e)

    elapsed_ms = (time.time() - start_time) * 1000
    cost = calculate_cost(
        prompt_tokens=total_prompt_tokens,
        completion_tokens=total_completion_tokens,
        model=settings.gemini_model if settings.llm_provider == "gemini" else "mock",
    )

    trace_step: TraceStep = {
        "node": "analyze",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "cost_usd": cost,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Flagged {len(all_findings)} initial findings across {len(requirements)} requirements.",
    }

    return {
        "findings": all_findings,
        "trace": state.get("trace", []) + [trace_step],
    }
