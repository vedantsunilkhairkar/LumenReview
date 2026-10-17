"""Visual LangGraph execution step tracker component."""

import streamlit as st

NODES_ORDER = [
    ("ingest_requirements", "1. Ingest"),
    ("sanitize", "2. Sanitize"),
    ("retrieve", "3. Retrieve"),
    ("analyze", "4. Analyze"),
    ("verify_citations", "5. Verify"),
    ("conflict_check", "6. Conflict"),
    ("human_review", "7. Human Review"),
    ("generate_report", "8. Report"),
]


def render_step_tracker(completed_nodes: list[str], current_node: str = ""):
    """Render horizontal visual stepper representing the LangGraph workflow."""
    steps_html = []
    for node_id, label in NODES_ORDER:
        if node_id in completed_nodes:
            status_style = "color: #10B981; font-weight: 700;"
            icon = "✓"
        elif node_id == current_node:
            status_style = "color: #F5A623; font-weight: 700;"
            icon = "●"
        else:
            status_style = "color: #94A3B8; font-weight: 500;"
            icon = "○"

        steps_html.append(
            f'<div style="display: flex; flex-direction: column; align-items: center; gap: 0.2rem; font-size: 0.75rem; {status_style}">'
            f"<span>{icon}</span>"
            f"<span>{label}</span>"
            f"</div>"
        )

    joined = '<div style="color: #CBD5E1; font-size: 0.8rem; margin: 0 0.3rem;">→</div>'.join(
        steps_html
    )

    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.85rem 1.25rem; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center; overflow-x: auto;">
            {joined}
        </div>
        """,
        unsafe_allow_html=True,
    )
