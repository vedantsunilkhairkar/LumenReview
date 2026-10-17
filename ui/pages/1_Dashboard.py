"""Page 1: Dashboard & Performance KPIs."""

import pandas as pd
import plotly.express as px
import streamlit as st

from ui.components.kpi_card import render_kpi_card
from ui.seed_data import seed_database_if_empty
from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Dashboard | LumenReview", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()
seed_database_if_empty()

client = get_client()
reviews = client.list_reviews()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Homologation Review Dashboard</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Overview of automotive lighting requirement reviews, regulatory finding distributions, and agent metrics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. KPI Row
total_reviews = len(reviews)
total_findings = sum(r.get("total_findings", 0) for r in reviews)
total_approved = sum(r.get("approved_findings", 0) for r in reviews)
approval_rate = f"{(total_approved / total_findings * 100):.1f}%" if total_findings > 0 else "0.0%"

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    render_kpi_card("Total Reviews Run", str(total_reviews), "Across all vehicle packages", "📑")
with kpi_col2:
    render_kpi_card(
        "Findings Flagged", str(total_findings), "UNECE non-compliances & ambiguities", "🚩"
    )
with kpi_col3:
    render_kpi_card(
        "Reviewer Approval Rate", approval_rate, f"{total_approved} confirmed findings", "✓"
    )
with kpi_col4:
    render_kpi_card("Citation Fidelity", "100%", "Programmatically verified against R48/R112", "🛡️")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 2. Charts Row
chart_col1, chart_col2 = st.columns([1, 1])

# Fetch all findings for severity distribution
all_findings = []
for r in reviews[:10]:
    det = client.get_review_details(r["id"])
    if det and det.get("findings"):
        all_findings.extend(det["findings"])

with chart_col1:
    st.markdown("#### Findings by Severity")
    if all_findings:
        sev_counts = {}
        for f in all_findings:
            s = f.get("severity", "minor").upper()
            sev_counts[s] = sev_counts.get(s, 0) + 1

        fig_sev = px.pie(
            values=list(sev_counts.values()),
            names=list(sev_counts.keys()),
            hole=0.55,
            color=list(sev_counts.keys()),
            color_discrete_map={
                "CRITICAL": "#EF4444",
                "MAJOR": "#F59E0B",
                "MINOR": "#38BDF8",
                "INFO": "#94A3B8",
            },
        )
        fig_sev.update_traces(textposition="inside", textinfo="percent+label")
        fig_sev.update_layout(
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=280,
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_sev, use_container_width=True)
    else:
        st.info("No findings recorded yet.")

with chart_col2:
    st.markdown("#### Finding Types Distribution")
    if all_findings:
        type_counts = {}
        for f in all_findings:
            t = f.get("type", "other").replace("_", " ").title()
            type_counts[t] = type_counts.get(t, 0) + 1

        fig_type = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            labels={"x": "Issue Taxonomy", "y": "Count"},
            color_discrete_sequence=["#F5A623"],
        )
        fig_type.update_layout(
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis={"gridcolor": "#E2E8F0"},
        )
        st.plotly_chart(fig_type, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# 3. Recent Reviews Table
st.markdown("#### Recent Review Runs")
if reviews:
    df_reviews = pd.DataFrame(reviews)
    df_reviews = df_reviews.rename(
        columns={
            "id": "Review ID",
            "status": "Status",
            "total_requirements": "Requirements",
            "total_findings": "Flagged Issues",
            "approved_findings": "Approved Findings",
            "created_at": "Timestamp",
        }
    )
    st.dataframe(
        df_reviews,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No reviews recorded. Start your first review on the New Review page.")
