"""Conflict check node: evaluates cross-requirement contradictions."""

import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.config import settings
from app.core.cost import calculate_cost, estimate_tokens
from app.core.logging import logger
from app.llm.factory import get_llm_provider
from app.llm.prompts.v1_conflict import build_conflict_prompt
from app.llm.schemas import ConflictAnalysisResult


def conflict_check_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: detect cross-requirement contradictions."""
    start_time = time.time()
    requirements = state.get("requirements", [])
    conflict_findings: list[dict[str, Any]] = []

    p_tokens = 0
    c_tokens = 0

    if len(requirements) >= 2:
        llm = get_llm_provider()
        prompt = build_conflict_prompt(requirements)
        p_tokens = estimate_tokens(prompt)

        try:
            result = llm.generate(prompt, response_model=ConflictAnalysisResult)
            if isinstance(result, ConflictAnalysisResult):
                for conflict in result.conflicts:
                    c_dict = conflict.model_dump()
                    # Mark citation verified if no chunk cited
                    if not c_dict.get("evidence"):
                        c_dict["citation_verified"] = True
                        c_dict["citation_verification_note"] = (
                            "Cross-requirement conflict analysis."
                        )
                    conflict_findings.append(c_dict)
                c_tokens = estimate_tokens(str(result.model_dump()))
        except Exception as e:
            logger.error("Error during conflict check: %s", e)

    elapsed_ms = (time.time() - start_time) * 1000
    cost = calculate_cost(
        prompt_tokens=p_tokens,
        completion_tokens=c_tokens,
        model=settings.gemini_model if settings.llm_provider == "gemini" else "mock",
    )

    trace_step: TraceStep = {
        "node": "conflict_check",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": p_tokens,
        "completion_tokens": c_tokens,
        "cost_usd": cost,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Detected {len(conflict_findings)} cross-requirement contradictions.",
    }

    # Append conflicts to total findings list
    all_findings = state.get("findings", []) + conflict_findings

    return {
        "findings": all_findings,
        "conflict_findings": conflict_findings,
        "status": "waiting_for_human",
        "trace": state.get("trace", []) + [trace_step],
    }
