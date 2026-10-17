"""PII and secret scanner for uploaded requirements."""

import re

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "api_key_or_token": re.compile(
        r"\b(?:api[_-]?key|secret|token|bearer)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?",
        re.IGNORECASE,
    ),
    "ipv4_address": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    ),
}


class PIIScanner:
    """Scans requirement inputs for personal or confidential data."""

    def scan(self, text: str) -> tuple[bool, list[str]]:
        findings = []
        for pii_type, pattern in PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                findings.append(f"Detected {len(matches)} instance(s) of potential {pii_type}")
        return len(findings) > 0, findings

    def redact(self, text: str) -> str:
        redacted = text
        for pii_type, pattern in PII_PATTERNS.items():
            redacted = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted)
        return redacted
