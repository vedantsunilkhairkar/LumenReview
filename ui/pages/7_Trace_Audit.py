"""Page 7: Execution Trace Timeline & Human Review Audit Trail."""

import pandas as pd
import streamlit as st

from ui.components.kpi_card import render_kpi_card
from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Trace & Audit | LumenReview", page_icon="⏱️", layout="wide")
apply_theme()
render_sidebar()

client = get_client()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Agent Execution Trace & Audit Log</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Inspect node-by-node execution latencies, token consumption, model costs, and immutable human decision history.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

reviews = client.list_reviews()
if not reviews:
    st.warning("No reviews found.")
    st.stop()

review_ids = [r["id"] for r in reviews]
default_index = 0
if "current_review_id" in st.session_state and st.session_state["current_review_id"] in review_ids:
    default_index = review_ids.index(st.session_state["current_review_id"])

selected_id = st.selectbox("Select Review Run:", review_ids, index=default_index)
review_details = client.get_review_details(selected_id)

if not review_details:
    st.error("Could not load details for this review.")
    st.stop()

trace_steps = review_details.get("trace", [])
audit_trail = review_details.get("audit_trail", [])

# Overall Metrics Row
total_latency = sum(step.get("latency_ms", 0.0) for step in trace_steps)
total_tokens = sum(
    step.get("prompt_tokens", 0) + step.get("completion_tokens", 0) for step in trace_steps
)
total_cost = sum(step.get("cost_usd", 0.0) for step in trace_steps)

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    render_kpi_card(
        "Total Nodes Executed", str(len(trace_steps)), "LangGraph StateGraph steps", "⚡"
    )
with col_k2:
    render_kpi_card(
        "Total Latency", f"{total_latency:.1f} ms", f"{total_latency / 1000:.2f} seconds", "⏱️"
    )
with col_k3:
    render_kpi_card("Total Tokens", f"{total_tokens:,}", "Prompt + Completion tokens", "🔢")
with col_k4:
    render_kpi_card("Estimated Cost", f"${total_cost:.5f}", "USD based on model rates", "💰")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 1. Timeline of Agent Steps
st.markdown("#### 1. LangGraph Execution Timeline")
if trace_steps:
    df_trace = pd.DataFrame(trace_steps)
    df_trace = df_trace.rename(
        columns={
            "node": "Workflow Node",
            "status": "Status",
            "latency_ms": "Latency (ms)",
            "prompt_tokens": "Prompt Tokens",
            "completion_tokens": "Completion Tokens",
            "cost_usd": "Cost ($)",
            "timestamp": "Timestamp",
            "details": "Step Summary",
        }
    )
    st.dataframe(df_trace, use_container_width=True, hide_index=True)
else:
    st.info("No trace steps available for this review.")

st.divider()

# 2. Reviewer Decision Audit Trail
st.markdown("#### 2. Human Decision Audit Trail")
st.caption(
    "Immutable record of every reviewer approval, rejection, and modification for homologation compliance."
)

if audit_trail:
    df_audit = pd.DataFrame(audit_trail)
    df_audit = df_audit.rename(
        columns={
            "finding_id": "Finding ID",
            "decision": "Reviewer Action",
            "notes": "Engineering Justification",
            "decided_at": "Decision Timestamp",
        }
    )
    st.dataframe(df_audit, use_container_width=True, hide_index=True)
else:
    st.info(
        "No human decisions recorded yet. Decisions will appear here once reviewed in the Workspace."
    )
