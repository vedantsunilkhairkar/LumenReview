"""Interactive Finding Card component with review decisions."""

from collections.abc import Callable
from typing import Any

import streamlit as st

from ui.components.diff_viewer import render_diff_viewer
from ui.components.evidence_panel import render_evidence_panel
from ui.components.severity_badge import (
    render_decision_badge,
    render_issue_type_badge,
    render_severity_badge,
)


def render_finding_card(
    finding: dict[str, Any],
    original_req_text: str = "",
    on_decision: Callable[[str, str, str | None, str | None], None] | None = None,
    key_prefix: str = "",
):
    fid = finding["id"]
    req_id = finding.get("req_id", "REQ")
    severity = finding.get("severity", "minor")
    issue_type = finding.get("type", "ambiguous")
    title = finding.get("title", "")
    explanation = finding.get("explanation", "")
    confidence = finding.get("confidence", 0.9)
    is_verified = finding.get("citation_verified", False)
    verification_note = finding.get("citation_verification_note")
    evidence = finding.get("evidence")
    rewrite = finding.get("suggested_rewrite")
    human_decision = finding.get("human_decision", "pending")
    finding.get("human_notes")

    sev_badge = render_severity_badge(severity)
    type_badge = render_issue_type_badge(issue_type)
    dec_badge = render_decision_badge(human_decision)
    confidence_pct = int(confidence * 100)

    st.markdown(
        f"""
        <div class="lr-card" style="border-left: 4px solid {"#EF4444" if severity == "critical" else "#F59E0B" if severity == "major" else "#38BDF8"};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    {sev_badge}
                    {type_badge}
                    <code style="background: #F1F5F9; color: #475569; font-weight: 600; padding: 0.15rem 0.4rem; border-radius: 4px;">{req_id}</code>
                    <span style="font-size: 0.75rem; color: #64748B;">ID: {fid}</span>
                </div>
                <div>{dec_badge}</div>
            </div>
            <div style="font-size: 1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">
                {title}
            </div>
            <div style="font-size: 0.85rem; color: #334155; line-height: 1.4rem; margin-bottom: 0.5rem;">
                {explanation}
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 600;">CONFIDENCE:</span>
                <div style="flex-grow: 1; max-width: 140px; background: #E2E8F0; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: #F5A623; width: {confidence_pct}%; height: 100%;"></div>
                </div>
                <span style="font-size: 0.75rem; font-weight: 700; color: #0F172A;">{confidence_pct}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cited Evidence Panel
    render_evidence_panel(evidence, is_verified, verification_note)

    # Suggested Rewrite & Diff
    render_diff_viewer(original_req_text, rewrite)

    # Interactive Human Decision Bar
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("✓ Approve", key=f"{key_prefix}_btn_app_{fid}", use_container_width=True):
            if on_decision:
                on_decision(fid, "approved", "Approved by reviewer", None)
            st.rerun()

    with col2:
        if st.button("✕ Reject", key=f"{key_prefix}_btn_rej_{fid}", use_container_width=True):
            if on_decision:
                on_decision(fid, "rejected", "Rejected by reviewer", None)
            st.rerun()

    with col3:
        with st.popover("✏️ Edit & Approve", use_container_width=True):
            st.markdown(f"**Edit Finding & Rewrite for {fid}**")
            default_text = rewrite.get("text", original_req_text) if rewrite else original_req_text
            edited_text = st.text_area(
                "Compliant Requirement Text", value=default_text, key=f"edit_text_{fid}"
            )
            notes = st.text_input(
                "Reviewer Rationale",
                value="Modified text per engineering homologation criteria.",
                key=f"notes_{fid}",
            )
            if st.button("Save & Approve", key=f"save_edit_{fid}", type="primary"):
                if on_decision:
                    on_decision(fid, "edited", notes, edited_text)
                st.rerun()
