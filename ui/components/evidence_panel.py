"""Evidence inspector panel with highlighted source quotes and verification badges."""

from typing import Any

import streamlit as st

from ui.components.severity_badge import render_verification_badge


def render_evidence_panel(
    evidence: dict[str, Any] | None,
    is_verified: bool,
    verification_note: str | None = None,
):
    """Render structured evidence card with source document, clause ID, and highlighted quote."""
    if not evidence or not evidence.get("chunk_id"):
        st.markdown(
            """
            <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 0.75rem; margin-top: 0.5rem;">
                <div style="font-size: 0.8rem; color: #64748B;">ℹ️ <i>No direct regulatory clause cited (Intrinsic engineering ambiguity or testability finding).</i></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    doc_name = evidence.get("document", "UNECE Regulation")
    clause_id = evidence.get("clause_id", "")
    chunk_id = evidence.get("chunk_id", "")
    quote = evidence.get("quote", "")
    page = evidence.get("page", 1)

    verification_badge = render_verification_badge(is_verified)
    note_html = (
        f'<div style="font-size: 0.75rem; color: #475569; margin-top: 0.4rem;"><b>Audit Note:</b> {verification_note}</div>'
        if verification_note
        else ""
    )

    with st.expander(f"📑 Cited Evidence: {doc_name} (Clause {clause_id})", expanded=False):
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                    <div>
                        <span style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">{doc_name}</span>
                        <span style="color: #64748B; font-size: 0.8rem; margin-left: 0.4rem;">Clause {clause_id} (Page {page})</span>
                    </div>
                    <div>{verification_badge}</div>
                </div>
                <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.4rem;">
                    Chunk ID: <code style="background: #F1F5F9; color: #0F172A; padding: 0.15rem 0.4rem; border-radius: 4px;">{chunk_id}</code>
                </div>
                <div style="background: #FFFBEB; border-left: 4px solid #F5A623; padding: 0.65rem 0.85rem; border-radius: 4px; font-size: 0.85rem; color: #78350F; font-style: italic;">
                    "{quote}"
                </div>
                {note_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
