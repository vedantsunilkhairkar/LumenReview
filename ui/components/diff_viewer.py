"""Requirement Diff viewer component."""

import difflib
from typing import Any

import streamlit as st


def render_diff_viewer(
    original_text: str,
    suggested_rewrite: dict[str, Any] | None,
):
    """Render inline visual diff showing original vs suggested compliant rewrite."""
    if not suggested_rewrite or not suggested_rewrite.get("text"):
        return

    new_text = suggested_rewrite.get("text", "")
    explanation = suggested_rewrite.get("diff_explanation", "")

    # Word-level comparison
    orig_words = original_text.split()
    new_words = new_text.split()
    matcher = difflib.SequenceMatcher(None, orig_words, new_words)

    diff_html_parts = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            diff_html_parts.append(" ".join(orig_words[i1:i2]))
        elif tag == "delete":
            deleted = " ".join(orig_words[i1:i2])
            diff_html_parts.append(f'<span class="lr-diff-del">{deleted}</span>')
        elif tag == "insert":
            inserted = " ".join(new_words[j1:j2])
            diff_html_parts.append(f'<span class="lr-diff-add">{inserted}</span>')
        elif tag == "replace":
            deleted = " ".join(orig_words[i1:i2])
            inserted = " ".join(new_words[j1:j2])
            diff_html_parts.append(
                f'<span class="lr-diff-del">{deleted}</span> <span class="lr-diff-add">{inserted}</span>'
            )

    diff_rendered = " ".join(diff_html_parts)

    st.markdown(
        f"""
        <div style="margin-top: 0.6rem; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.75rem;">
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 0.35rem;">
                Suggested Compliant Rewrite & Diff
            </div>
            <div style="font-size: 0.85rem; line-height: 1.4rem; color: #1E293B; margin-bottom: 0.4rem;">
                {diff_rendered}
            </div>
            <div style="font-size: 0.75rem; color: #64748B;">
                <b>Rationale:</b> {explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
