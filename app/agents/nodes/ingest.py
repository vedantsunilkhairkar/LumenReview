"""Ingest requirements node: parses raw text or structured inputs into atomic requirements."""

import csv
import io
import re
import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.cost import estimate_tokens


def parse_requirements_text(raw_text: str) -> list[dict[str, Any]]:
    """Parse text/CSV into atomic requirement objects with IDs."""
    requirements: list[dict[str, Any]] = []
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Check if input is CSV
    if len(lines) > 1 and ("," in lines[0] or "\t" in lines[0]):
        try:
            reader = csv.DictReader(io.StringIO(raw_text))
            for i, row in enumerate(reader, start=1):
                # Try finding text column
                text_col = None
                for key in ["text", "requirement", "description", "statement", "Requirement"]:
                    if key in row and row[key]:
                        text_col = row[key].strip()
                        break
                if not text_col:
                    text_col = list(row.values())[0].strip()

                req_id = row.get("id") or row.get("req_id") or f"REQ-{i:03d}"
                category = row.get("category") or "Lighting"
                if text_col:
                    requirements.append({"req_id": req_id, "text": text_col, "category": category})
            if requirements:
                return requirements
        except Exception:
            pass

    # Standard line-by-line / bullet parsing
    current_id_idx = 1
    for line in lines:
        # Match pattern like REQ-001: ... or 1. ... or [REQ-1] ...
        id_match = re.match(r"^(?:\[?([A-Za-z0-9_\-]+)\]?[:\.\)]\s*|\d+[\.\)]\s*)(.+)$", line)
        if id_match:
            custom_id = id_match.group(1)
            content = id_match.group(2).strip()
            req_id = custom_id if custom_id else f"REQ-{current_id_idx:03d}"
            current_id_idx += 1
            requirements.append({"req_id": req_id, "text": content, "category": "Lighting"})
        else:
            # Plain sentence or bullet point
            clean_text = line.lstrip("-*•> ").strip()
            if len(clean_text) > 10:
                requirements.append(
                    {
                        "req_id": f"REQ-{current_id_idx:03d}",
                        "text": clean_text,
                        "category": "Lighting",
                    }
                )
                current_id_idx += 1

    return requirements


def ingest_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: ingest raw requirements."""
    start_time = time.time()
    raw = state.get("raw_input", "")
    existing = state.get("requirements", [])

    if existing and len(existing) > 0:
        parsed = existing
    else:
        parsed = parse_requirements_text(raw)

    elapsed_ms = (time.time() - start_time) * 1000
    tokens = estimate_tokens(raw)

    trace_step: TraceStep = {
        "node": "ingest_requirements",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": tokens,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Parsed {len(parsed)} atomic requirements.",
    }

    return {
        "requirements": parsed,
        "status": "analyzing",
        "trace": state.get("trace", []) + [trace_step],
    }
