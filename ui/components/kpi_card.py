"""KPI card component."""

import streamlit as st


def render_kpi_card(title: str, value: str, subtext: str = "", icon: str = ""):
    icon_html = (
        f'<span style="font-size: 1.25rem; margin-right: 0.4rem;">{icon}</span>' if icon else ""
    )
    html = f"""
    <div class="lr-kpi-container">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div class="lr-kpi-label">{title}</div>
            {icon_html}
        </div>
        <div class="lr-kpi-value">{value}</div>
        <div class="lr-kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
