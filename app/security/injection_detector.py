"""Heuristic and regex-based prompt-injection detector."""

import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directives|commands)",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|guidelines)",
    r"you\s+are\s+now\s+(in\s+)?(dan|jailbreak|unrestricted|god)\s+mode",
    r"act\s+as\s+an\s+unrestricted\s+ai",
    r"system\s+override",
    r"bypass\s+(all\s+)?(regulations|checks|safety|homologation)",
    r"approve\s+all\s+(requirements|findings)\s+without\s+(checking|review)",
    r"do\s+not\s+flag\s+any\s+(issues|violations)",
    r"<\s*/?\s*(script|iframe|system|prompt|instruction)\s*>",
    r"```\s*(system|prompt|instruction)",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class InjectionDetector:
    """Zero-LLM prompt-injection detection engine."""

    def scan_text(self, text: str) -> tuple[bool, list[str]]:
        """Scans input text for adversarial injection attempts.

        Returns (is_suspicious, list_of_detected_patterns).
        """
        detected: list[str] = []
        for pattern in COMPILED_PATTERNS:
            match = pattern.search(text)
            if match:
                detected.append(match.group(0))

        return len(detected) > 0, detected

    def sanitize_text(self, text: str) -> str:
        """Strip control characters and replace raw injection attempts with quarantined markers."""
        cleaned = text
        for pattern in COMPILED_PATTERNS:
            cleaned = pattern.sub("[QUARANTINED_PROMPT_INJECTION_PATTERN]", cleaned)
        return cleaned.strip()
