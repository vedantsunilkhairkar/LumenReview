"""LumenReview Streamlit Application Entrypoint."""

import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st

from ui.seed_data import seed_database_if_empty
from ui.theme import apply_theme, render_sidebar

# Page config
st.set_page_config(
    page_title="LumenReview | Automotive Lighting AI Agent",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global custom styles
apply_theme()
render_sidebar()

# Ensure seed data exists on first launch
seed_database_if_empty()

# Home / Welcome Screen
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 2.5rem; border-radius: 12px; color: #FFFFFF; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
            <span style="font-size: 2.5rem;">💡</span>
            <div>
                <h1 style="color: #FFFFFF; font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">
                    Lumen<span style="color: #F5A623;">Review</span>
                </h1>
                <p style="color: #94A3B8; font-size: 1rem; margin: 0.25rem 0 0 0;">
                    Autonomous Homologation & Requirements Review Agent for Automotive Lighting Systems
                </p>
            </div>
        </div>
        <p style="color: #CBD5E1; font-size: 0.95rem; max-width: 820px; line-height: 1.6rem; margin-top: 1rem;">
            LumenReview accelerates automotive systems engineering by analyzing lighting specifications against
            UNECE Regulations (<b>R48</b> and <b>R112</b>). Built on LangGraph with stateful human-in-the-loop governance,
            hybrid RAG, and <b>100% programmatic citation verification</b>.
        </p>
        <div style="display: flex; gap: 0.8rem; margin-top: 1.25rem;">
            <a href="/New_Review" target="_self" style="background: #F5A623; color: #0F172A; font-weight: 700; text-decoration: none; padding: 0.6rem 1.25rem; border-radius: 8px; font-size: 0.9rem;">
                + Start New Review
            </a>
            <a href="/Dashboard" target="_self" style="background: rgba(255,255,255,0.1); color: #FFFFFF; font-weight: 600; text-decoration: none; padding: 0.6rem 1.25rem; border-radius: 8px; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.2);">
                View Dashboard
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="lr-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">Agentic Review Graph</div>
            <p style="font-size: 0.85rem; color: #64748B; line-height: 1.4rem;">
                State machine orchestrating ingestion, prompt-injection defense, hybrid retrieval, LLM analysis, and cross-requirement conflict detection.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="lr-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">Programmatic Verifier</div>
            <p style="font-size: 0.85rem; color: #64748B; line-height: 1.4rem;">
                Zero blind trust: every quoted regulation chunk ID and clause excerpt is verified against the knowledge base before human review.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="lr-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">Human-in-the-Loop Gate</div>
            <p style="font-size: 0.85rem; color: #64748B; line-height: 1.4rem;">
                Stateful interrupt halts execution until an engineer approves, rejects, or edits each finding. Full immutable decision audit log.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.markdown("### Quick Navigation")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    st.page_link("pages/1_Dashboard.py", label="Dashboard & KPIs", icon="📊")
with nav_col2:
    st.page_link("pages/2_New_Review.py", label="Start New Review", icon="📝")
with nav_col3:
    st.page_link("pages/3_Review_Workspace.py", label="Review Workspace", icon="🔬")
with nav_col4:
    st.page_link("pages/4_Knowledge_Base.py", label="UNECE Regulations", icon="📚")
