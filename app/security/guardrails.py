"""Context guardrails: quarantines untrusted user text and retrieved context."""

from typing import Any


def escape_xml_delimiters(text: str) -> str:
    """Escape XML tag delimiters to prevent prompt delimiter breakout attacks."""
    escaped = text.replace("<", "&lt;").replace(">", "&gt;")
    return escaped


def format_guarded_requirement(req_id: str, text: str) -> str:
    """Format requirement inside strict passive XML boundaries."""
    sanitized = escape_xml_delimiters(text)
    return (
        f'<requirement id="{req_id}" role="passive_data" executable="false">\n'
        f"{sanitized}\n"
        f"</requirement>"
    )


def format_guarded_clauses(clauses: list[dict[str, Any]]) -> str:
    """Format retrieved regulation clauses inside strict passive XML boundaries."""
    if not clauses:
        return '<retrieved_clauses count="0">\nNo matching regulatory clauses found.\n</retrieved_clauses>'

    formatted = []
    for c in clauses:
        chunk_id = c.get("chunk_id", "UNKNOWN")
        doc = c.get("document", "UNECE Regulation")
        clause = c.get("clause_id", "")
        text = escape_xml_delimiters(c.get("text", ""))

        formatted.append(
            f'  <clause chunk_id="{chunk_id}" doc="{doc}" clause_id="{clause}">\n'
            f"    {text}\n"
            f"  </clause>"
        )

    return '<retrieved_clauses count="{}">\n{}\n</retrieved_clauses>'.format(
        len(clauses), "\n".join(formatted)
    )
