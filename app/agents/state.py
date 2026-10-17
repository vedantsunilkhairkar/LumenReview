"""Agent state definitions for LangGraph orchestration."""

from typing import Any

from typing_extensions import TypedDict


class TraceStep(TypedDict):
    node: str
    status: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: str
    details: str | None


class AgentState(TypedDict):
    run_id: str
    raw_input: str
    requirements: list[dict[str, Any]]
    current_req: dict[str, Any] | None
    retrieved_clauses: dict[str, list[dict[str, Any]]]
    findings: list[dict[str, Any]]
    conflict_findings: list[dict[str, Any]]
    approvals: dict[
        str, dict[str, Any]
    ]  # finding_id -> {decision: approved|rejected|edited, notes: str}
    report: dict[str, Any] | None
    trace: list[TraceStep]
    status: str  # initialized | analyzing | waiting_for_human | completed | failed
    security_warnings: list[str]
    errors: list[str]
