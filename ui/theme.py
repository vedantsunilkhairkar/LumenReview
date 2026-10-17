"""Enterprise theme styles for LumenReview (Linear/Notion inspired)."""

import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import streamlit as st


def apply_theme():
    """Inject enterprise styling into Streamlit DOM."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top navbar / header cleanup */
    header[data-testid="stHeader"] {
        background-color: transparent;
    }

    /* Dark Navy Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border-right: 1px solid #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    /* Main background */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Cards */
    .lr-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .lr-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }

    /* Amber Accent and Highlights */
    .lr-accent {
        color: #F5A623;
        font-weight: 600;
    }

    /* KPI Cards */
    .lr-kpi-container {
        display: flex;
        flex-direction: column;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
    }
    .lr-kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.25rem;
    }
    .lr-kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 2.2rem;
    }
    .lr-kpi-subtext {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.25rem;
    }

    /* Badges */
    .lr-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .lr-badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
    }
    .lr-badge-major {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
    }
    .lr-badge-minor {
        background-color: #E0F2FE;
        color: #075985;
        border: 1px solid #BAE6FD;
    }
    .lr-badge-info {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
    }
    .lr-badge-verified {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
    }
    .lr-badge-unverified {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #F87171;
    }

    /* Step Stepper */
    .lr-stepper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
    }
    .lr-step-item {
        display: flex;
        align-items: center;
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
    }
    .lr-step-active {
        color: #F5A623 !important;
    }
    .lr-step-done {
        color: #10B981 !important;
    }

    /* Diff View */
    .lr-diff-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.75rem;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .lr-diff-del {
        background-color: #FEE2E2;
        color: #991B1B;
        text-decoration: line-through;
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
    }
    .lr-diff-add {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #F5A623 !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover {
        background-color: #D98207 !important;
        color: #FFFFFF !important;
    }

    /* Clean, high-contrast form inputs & textareas */
    div[data-baseweb="textarea"],
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input,
    .stTextArea textarea,
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="textarea"] textarea:focus,
    div[data-baseweb="input"] input:focus,
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #F5A623 !important;
        box-shadow: 0 0 0 2px rgba(245, 166, 35, 0.25) !important;
        outline: none !important;
    }

    div[data-baseweb="textarea"] textarea::placeholder,
    div[data-baseweb="input"] input::placeholder,
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }

    /* BaseWeb Select dropdowns */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_sidebar():
    """Render branded dark-navy sidebar with logo and status badge."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1.5rem 0;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.8rem;">💡</span>
                    <div>
                        <div style="font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF;">
                            Lumen<span style="color: #F5A623;">Review</span>
                        </div>
                        <div style="font-size: 0.7rem; color: #94A3B8; font-weight: 500;">
                            Automotive Lighting AI Homologation
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 1.25rem;">
                <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">ACTIVE STANDARD</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #F5A623;">UNECE R48 & R112</div>
                <div style="font-size: 0.65rem; color: #10B981;">● Ingestion Active & Verified</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
