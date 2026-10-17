"""Sanitize node: scans requirements for prompt injection and PII leaks."""

import time
from typing import Any

from app.agents.state import AgentState, TraceStep
from app.core.logging import logger
from app.security.injection_detector import InjectionDetector
from app.security.pii_scanner import PIIScanner

detector = InjectionDetector()
pii_scanner = PIIScanner()


def sanitize_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: sanitize and scan incoming requirements."""
    start_time = time.time()
    requirements = state.get("requirements", [])
    sanitized_reqs: list[dict[str, Any]] = []
    warnings: list[str] = list(state.get("security_warnings", []))

    for req in requirements:
        text = req.get("text", "")
        req_id = req.get("req_id", "REQ")

        # 1. Prompt Injection Scan
        has_injection, injection_matches = detector.scan_text(text)
        if has_injection:
            msg = f"Security Alert on {req_id}: Prompt-injection pattern detected: {injection_matches}. Content has been neutralized."
            logger.warning(msg)
            warnings.append(msg)
            text = detector.sanitize_text(text)

        # 2. PII Scan
        has_pii, pii_matches = pii_scanner.scan(text)
        if has_pii:
            msg = f"Privacy Alert on {req_id}: {', '.join(pii_matches)}. Sensitive data redacted."
            logger.info(msg)
            warnings.append(msg)
            text = pii_scanner.redact(text)

        sanitized_reqs.append(
            {
                "req_id": req_id,
                "text": text,
                "category": req.get("category", "Lighting"),
                "flagged_injection": has_injection,
                "flagged_pii": has_pii,
            }
        )

    elapsed_ms = (time.time() - start_time) * 1000
    trace_step: TraceStep = {
        "node": "sanitize",
        "status": "success",
        "latency_ms": round(elapsed_ms, 2),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": f"Scanned {len(sanitized_reqs)} requirements. {len(warnings)} security/privacy notices.",
    }

    return {
        "requirements": sanitized_reqs,
        "security_warnings": warnings,
        "trace": state.get("trace", []) + [trace_step],
    }
