"""Human review node: applies reviewer decisions (approve/reject/edit) before report generation."""

import time
from typing import Any

from app.agents.state import AgentState, TraceStep


def human_review_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: processes reviewer approvals, rejections, and modifications."""
    start_time = time.time()
    findings = state.get("findings", [])
    approvals = state.get("approvals", {})

    updated_findings: list[dict[str, Any]] = []
    approved_count = 0
    rejected_count = 0
    edited_count = 0

    for f in findings:
        fid = f["id"]
        item = dict(f)

        if fid in approvals:
            decision = approvals[fid]
            action = decision.get("decision", "approved")
            notes = decision.get("notes")
            edited_rewrite = decision.get("edited_rewrite")

            item["human_decision"] = action
            item["human_notes"] = notes

            if action == "approved":
                approved_count += 1
            elif action == "rejected":
                rejected_count += 1
            elif action == "edited":
                edited_count += 1
                if edited_rewrite and item.get("suggested_rewrite"):
                    item["suggested_rewrite"]["text"] = edited_rewrite
        else:
            # If no explicit decision yet, leave as pending
            item["human_decision"] = item.get("human_decision", "pending")

        updated_findings.append(item)

    elapsed_ms = (time.time() - start_time) * 1000
    trace_step: TraceStep = {
        "node": "human_review",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Processed human reviews: {approved_count} approved, {rejected_count} rejected, {edited_count} edited.",
    }

    status_val = "generating_report" if approvals else "waiting_for_human"

    return {
        "findings": updated_findings,
        "status": status_val,
        "trace": state.get("trace", []) + [trace_step],
    }
