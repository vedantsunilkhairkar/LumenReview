"""Page 6: Final Homologation Report Preview & Export."""

import streamlit as st

from app.agents.nodes.report import export_pdf_report
from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Report | LumenReview", page_icon="📑", layout="wide")
apply_theme()
render_sidebar()

client = get_client()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Homologation Review Report</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Export finalized review documentation compiled from human-approved findings and verified UNECE citations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

reviews = client.list_reviews()
if not reviews:
    st.warning("No reviews found.")
    st.stop()

# Select review
review_ids = [r["id"] for r in reviews]
default_index = 0

# Prefer a completed review with report_md
completed_indices = [i for i, r in enumerate(reviews) if r.get("status") == "completed"]
if completed_indices:
    default_index = completed_indices[0]

if "current_review_id" in st.session_state and st.session_state["current_review_id"] in review_ids:
    default_index = review_ids.index(st.session_state["current_review_id"])

selected_id = st.selectbox("Select Review Run:", review_ids, index=default_index)
review_details = client.get_review_details(selected_id)

if not review_details:
    st.error("Could not load review report.")
    st.stop()

report_md = review_details.get("report_md")
findings = review_details.get("findings", [])
approved_findings = [f for f in findings if f.get("human_decision") in ["approved", "edited"]]

if not report_md:
    st.info(
        f"Review '{selected_id}' has not been finalized yet. Complete human review in the workspace first."
    )
    st.page_link("pages/3_Review_Workspace.py", label="Go to Review Workspace", icon="🔬")
    st.stop()

# Action Row: Export buttons
col_exp1, col_exp2, col_exp3 = st.columns([2, 1, 1])

# Generate PDF bytes
report_data = {
    "review_id": selected_id,
    "generated_at": review_details.get("completed_at", ""),
    "total_requirements": review_details.get("total_requirements", 0),
    "total_findings_flagged": review_details.get("total_findings", 0),
    "total_findings_approved": len(approved_findings),
    "findings": approved_findings,
    "executive_summary": "Homologation review completed for automotive lighting requirements.",
    "markdown_content": report_md,
}
pdf_bytes = export_pdf_report(report_data)

with col_exp2:
    st.download_button(
        label="📥 Download Markdown (.md)",
        data=report_md,
        file_name=f"LumenReview_{selected_id}.md",
        mime="text/markdown",
        use_container_width=True,
    )

with col_exp3:
    st.download_button(
        label="📄 Download PDF (.pdf)",
        data=pdf_bytes,
        file_name=f"LumenReview_{selected_id}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Preview Tabs
tab1, tab2 = st.tabs(["📄 Formatted Report View", "💻 Raw Markdown Source"])

with tab1:
    with st.container(border=True):
        st.markdown(report_md)

with tab2:
    st.code(report_md, language="markdown")
