"""Page 2: New Requirement Review & Analysis Runner."""

import time

import pandas as pd
import streamlit as st

from app.agents.nodes.ingest import parse_requirements_text
from ui.components.step_tracker import render_step_tracker
from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="New Review | LumenReview", page_icon="📝", layout="wide")
apply_theme()
render_sidebar()

client = get_client()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Start New Requirements Review</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Upload or paste automotive lighting system requirements to launch automated homologation analysis.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

SAMPLE_REQUIREMENTS = """REQ-001: The principal dipped-beam LED modules shall produce an objective luminous flux of 2,500 lumens.
REQ-002: The direction-indicator lamps shall operate at a flashing frequency of 2.5 Hz across all operating conditions.
REQ-003: Front daytime running lamps must remain illuminated at full intensity when dipped-beam headlamps are turned on.
REQ-004: Dipped-beam cut-off line must provide sufficient illumination under normal load conditions.
REQ-005: Stop lamp apparent surface mounting height shall be set to 280 mm above ground level.
"""

col_main, col_config = st.columns([2.5, 1])

with col_config:
    st.markdown("#### Review Configuration")
    with st.container(border=True):
        st.selectbox(
            "LLM Provider", ["mock (Offline / Test)", "gemini", "openai", "anthropic"], index=0
        )
        top_k = st.slider("Top-K Clauses Retrieved", min_value=1, max_value=10, value=5)
        bm25_enabled = st.toggle("Enable BM25 Hybrid Rerank", value=True)
        verify_citations = st.toggle("Enforce Citation Verification", value=True)
        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Target Regulations: <b>UNECE R48 (Installation)</b> and <b>UNECE R112 (Headlamps)</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_main:
    st.markdown("#### Input Requirements")

    input_mode = st.radio(
        "Input Format", ["Paste Text / Bullets", "Upload CSV / TXT File"], horizontal=True
    )

    raw_text = ""
    if input_mode == "Paste Text / Bullets":
        if st.button("📋 Load Sample Automotive Lighting Requirements"):
            st.session_state["raw_input_text"] = SAMPLE_REQUIREMENTS

        default_text = st.session_state.get("raw_input_text", "")
        raw_text = st.text_area(
            "Requirement Statements (Numbered or prefixed with REQ-XXX):",
            value=default_text,
            height=200,
            placeholder="REQ-001: Principal dipped-beam shall produce 2500 lumens...",
        )
    else:
        uploaded_file = st.file_uploader("Upload requirements (.txt or .csv)", type=["txt", "csv"])
        if uploaded_file:
            raw_text = uploaded_file.read().decode("utf-8", errors="replace")
            st.success(f"Loaded {uploaded_file.name}")

    parsed_reqs = []
    if raw_text:
        parsed_reqs = parse_requirements_text(raw_text)
        if parsed_reqs:
            st.markdown(f"**Parsed Requirements Preview ({len(parsed_reqs)} items):**")
            df = pd.DataFrame(parsed_reqs)
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if st.button(
        "🚀 Run Agentic Analysis",
        type="primary",
        use_container_width=True,
        disabled=len(parsed_reqs) == 0,
    ):
        # Progress Tracker Placeholder
        stepper_placeholder = st.empty()
        status_box = st.empty()

        # Step 1: Ingest
        stepper_placeholder.markdown("### Agent Orchestration Progress")
        render_step_tracker(["ingest_requirements"], "sanitize")
        status_box.info("Ingesting and normalizing atomic requirements...")
        time.sleep(0.3)

        # Step 2: Sanitize
        render_step_tracker(["ingest_requirements", "sanitize"], "retrieve")
        status_box.info("Scanning for prompt-injection patterns and PII leaks...")
        time.sleep(0.3)

        # Step 3: Retrieve
        render_step_tracker(["ingest_requirements", "sanitize", "retrieve"], "analyze")
        status_box.info(
            f"Executing hybrid RAG retrieval over UNECE R48/R112 knowledge base (top_k={top_k})..."
        )

        # Execute review
        try:
            res = client.start_review(raw_text)
            review_id = res.get("review_id")

            # Step 4, 5, 6, 7
            render_step_tracker(
                [
                    "ingest_requirements",
                    "sanitize",
                    "retrieve",
                    "analyze",
                    "verify_citations",
                    "conflict_check",
                ],
                "human_review",
            )
            status_box.success(
                f"Analysis completed! Flagged {res.get('total_findings', 0)} finding(s). Ready for human review."
            )

            st.session_state["current_review_id"] = review_id
            st.toast(f"Review {review_id} created successfully!", icon="✅")

            time.sleep(1.0)
            try:
                st.switch_page("pages/3_Review_Workspace.py")
            except Exception:
                st.page_link(
                    "pages/3_Review_Workspace.py",
                    label=f"➡️ Click here to Open Review Workspace for {review_id}",
                    icon="🔬",
                )
        except Exception as e:
            st.error(f"Error launching review: {e}")
