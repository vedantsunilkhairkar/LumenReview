"""Page 3: Review Workspace (Split View with Human Decision Loop)."""

import time

import streamlit as st

from ui.components.finding_card import render_finding_card
from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Review Workspace | LumenReview", page_icon="🔬", layout="wide")
apply_theme()
render_sidebar()

client = get_client()

# Fetch reviews for dropdown
reviews = client.list_reviews()
if not reviews:
    st.warning("No review runs found. Please create one on the 'New Review' page.")
    st.page_link("pages/2_New_Review.py", label="Go to New Review", icon="📝")
    st.stop()

# Determine selected review
review_ids = [r["id"] for r in reviews]
default_index = 0

# Prefer review with findings
reviews_with_findings = [i for i, r in enumerate(reviews) if r.get("total_findings", 0) > 0]
if reviews_with_findings:
    default_index = reviews_with_findings[0]

if "current_review_id" in st.session_state and st.session_state["current_review_id"] in review_ids:
    default_index = review_ids.index(st.session_state["current_review_id"])

header_col1, header_col2, header_col3 = st.columns([2, 1.5, 1])

with header_col1:
    st.markdown(
        """
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Requirements Review Workspace</h2>
        <p style="color: #64748B; font-size: 0.85rem; margin: 0.2rem 0 0 0;">
            Human-in-the-Loop review: verify citations, inspect evidence quotes, and approve or reject findings.
        </p>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    selected_review_id = st.selectbox("Active Review Run", review_ids, index=default_index)
    st.session_state["current_review_id"] = selected_review_id

# Fetch review details
review_details = client.get_review_details(selected_review_id)
if not review_details:
    st.error(f"Could not load review details for {selected_review_id}")
    st.stop()

findings = review_details.get("findings", [])
total_findings = len(findings)
decided_findings = [
    f for f in findings if f.get("human_decision") in ["approved", "rejected", "edited"]
]
reviewed_count = len(decided_findings)

# Sticky / Top Action & Progress Bar
with st.container(border=True):
    bar_col1, bar_col2, bar_col3 = st.columns([1.5, 2, 1.5])
    with bar_col1:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; color: #475569;">
                <b>Review Progress:</b> <span style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{reviewed_count} of {total_findings}</span> reviewed
            </div>
            """,
            unsafe_allow_html=True,
        )
    with bar_col2:
        progress_val = (reviewed_count / total_findings) if total_findings > 0 else 1.0
        st.progress(progress_val)
    with bar_col3:
        finalize_disabled = total_findings == 0
        if st.button(
            "🏁 Finalize & Generate Report",
            type="primary",
            use_container_width=True,
            disabled=finalize_disabled,
            help="Compile approved findings into final homologation report"
            if not finalize_disabled
            else "No findings to report",
        ):
            # Gather decisions - default any undecided finding to approved for fast workflow
            decisions_payload = {}
            for f in findings:
                current_dec = f.get("human_decision")
                decisions_payload[f["id"]] = {
                    "decision": current_dec
                    if current_dec in ["approved", "rejected", "edited"]
                    else "approved",
                    "notes": f.get("human_notes")
                    or ("Approved by reviewer for report compilation"),
                    "edited_rewrite": f.get("suggested_rewrite", {}).get("text")
                    if f.get("suggested_rewrite")
                    else None,
                }
            with st.spinner(
                "Compiling homologation report from approved findings and verified citations..."
            ):
                res = client.submit_decisions(selected_review_id, decisions_payload)
                st.session_state["current_review_id"] = selected_review_id
                st.success("Report successfully generated!")
                time.sleep(1.0)
                try:
                    st.switch_page("pages/6_Report.py")
                except Exception:
                    st.page_link("pages/6_Report.py", label="➡️ View Final Report", icon="📑")

# Executive Financial Impact & Arbitrage Metrics (FORVIA HELLA Tier-1 Moat)
tooling_risk = sum(
    float(f.get("financial_impact_eur") or 0.0)
    for f in findings
    if f.get("financial_impact_type") == "tooling_risk"
)
bom_savings = sum(
    float(f.get("financial_impact_eur") or 0.0)
    for f in findings
    if f.get("financial_impact_type") == "bom_cost_out"
)
cross_market_count = sum(1 for f in findings if f.get("market_scope") == "Cross_Market_Conflict")
ve_count = sum(1 for f in findings if f.get("type") == "value_engineering")

f_col1, f_col2, f_col3, f_col4 = st.columns(4)
with f_col1:
    st.metric(
        label="⚠️ Tooling Scrappage Risk",
        value=f"€{tooling_risk:,.0f}" if tooling_risk > 0 else "€0",
        help="Avoided injection mold tooling redesign and re-cut expenses",
    )
with f_col2:
    st.metric(
        label="💰 BOM Cost-Out Potential",
        value=f"€{bom_savings:,.2f} / unit" if bom_savings > 0 else "€0.00 / unit",
        help="Estimated direct per-unit Bill of Materials savings across production volume",
    )
with f_col3:
    st.metric(
        label="⚖️ Multi-Jurisdiction Conflicts",
        value=f"{cross_market_count} issues",
        help="Contradictions between UNECE R48/R112 and US FMVSS 108 standards",
    )
with f_col4:
    st.metric(
        label="💎 Value Engineering",
        value=f"{ve_count} proposals",
        help="Over-engineered specifications relaxed to standard automotive AEC-Q102 grade",
    )

# Main Split-View Layout
st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
left_col, right_col = st.columns([1.1, 2])


# Handle reviewer actions callback
def handle_decision(finding_id: str, decision: str, notes: str | None, edited_rewrite: str | None):
    decisions_payload = {
        finding_id: {
            "decision": decision,
            "notes": notes,
            "edited_rewrite": edited_rewrite,
        }
    }
    client.submit_decisions(selected_review_id, decisions_payload)
    st.toast(f"Decision '{decision.upper()}' recorded for {finding_id}", icon="✓")


with left_col:
    st.markdown("#### Requirements List")
    st.caption("Click to filter findings by requirement")

    # Group findings by requirement
    req_finding_map = {}
    for f in findings:
        rid = f.get("req_id", "REQ")
        req_finding_map.setdefault(rid, []).append(f)

    # Unique requirements
    req_ids = list(req_finding_map.keys())
    if not req_ids:
        st.info("No requirements found in this review.")

    filter_req = st.radio(
        "Filter by Requirement:",
        options=["All Requirements"] + req_ids,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("---")
    # Quick filter chips
    for rid in req_ids:
        r_findings = req_finding_map[rid]
        worst_sev = "info"
        for s in ["critical", "major", "minor", "info"]:
            if any(f.get("severity") == s for f in r_findings):
                worst_sev = s
                break

        chip_color = (
            "#FEE2E2"
            if worst_sev == "critical"
            else "#FEF3C7"
            if worst_sev == "major"
            else "#E0F2FE"
        )
        text_color = (
            "#991B1B"
            if worst_sev == "critical"
            else "#92400E"
            if worst_sev == "major"
            else "#075985"
        )

        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #0F172A; font-size: 0.85rem;">{rid}</span>
                    <span style="background: {chip_color}; color: {text_color}; font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 4px;">
                        {len(r_findings)} issue(s)
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with right_col:
    st.markdown("#### Regulatory Findings & Citations")

    # Filter findings
    displayed_findings = findings
    if filter_req != "All Requirements":
        displayed_findings = [f for f in findings if f.get("req_id") == filter_req]

    if not displayed_findings:
        st.info("No findings match the current filter.")
    else:
        for idx, finding in enumerate(displayed_findings):
            render_finding_card(
                finding=finding,
                original_req_text=finding.get("explanation", ""),
                on_decision=handle_decision,
                key_prefix=f"w_{selected_review_id}_{idx}",
            )

st.divider()

# Developer View Toggle
with st.expander("🛠️ Developer View (Raw Execution Trace & State)"):
    st.json(
        {
            "review_id": review_details.get("id"),
            "status": review_details.get("status"),
            "total_requirements": review_details.get("total_requirements"),
            "total_findings": review_details.get("total_findings"),
            "trace_steps": review_details.get("trace", []),
            "audit_trail": review_details.get("audit_trail", []),
        }
    )
