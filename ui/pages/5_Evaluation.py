"""Page 5: Evaluation Benchmark Matrix & Configuration Comparison."""

import pandas as pd
import plotly.express as px
import streamlit as st

from app.db.models import EvalRunRecord
from app.db.session import SessionLocal, init_db
from app.evaluation.runner import BenchmarkRunner
from ui.components.kpi_card import render_kpi_card
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Evaluation | LumenReview", page_icon="📈", layout="wide")
apply_theme()
render_sidebar()
init_db()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Agent Evaluation & Benchmarking Harness</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Benchmark agent performance on ground-truth automotive test datasets. Compare retrieval algorithms, latency, and citation fidelity.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch historical runs
db = SessionLocal()
try:
    runs = db.query(EvalRunRecord).order_by(EvalRunRecord.created_at.desc()).all()
    runs_data = [
        {
            "Run ID": r.id,
            "Configuration": r.config_name,
            "F1 Score": f"{r.f1_score:.3f}",
            "Precision": f"{r.precision:.3f}",
            "Recall": f"{r.recall:.3f}",
            "Citation Accuracy": f"{r.citation_correctness * 100:.1f}%",
            "Hallucination Rate": f"{r.hallucination_rate * 100:.1f}%",
            "Avg Latency (ms)": f"{r.avg_latency_ms:.1f}",
            "Cost ($)": f"${r.total_cost_usd:.5f}",
            "Timestamp": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            "_raw_record": r,
        }
        for r in runs
    ]
finally:
    db.close()

# Top Action: Run New Benchmark
with st.container(border=True):
    col_run1, col_run2, col_run3 = st.columns([2, 1, 1])
    with col_run1:
        config_name = st.selectbox(
            "Select Benchmark Configuration to Run:",
            [
                "LumenReview-Hybrid-Verified (RRF + Verifier, top_k=5)",
                "LumenReview-Dense-Only (No BM25, top_k=5)",
                "LumenReview-Unverified (No Citation Verification, top_k=5)",
                "LumenReview-Minimal-Retrieval (top_k=2)",
            ],
        )
    with col_run2:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Run Benchmark Now", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner(f"Executing benchmark across eval_set.jsonl ({config_name})..."):
            runner = BenchmarkRunner()
            top_k_val = 2 if "top_k=2" in config_name else 5
            verify_val = "No Citation Verification" not in config_name
            res = runner.run_benchmark(
                config_name=config_name, top_k=top_k_val, verify_citations=verify_val
            )
            st.success(
                f"Benchmark completed! F1 Score: {res['f1_score']:.3f} | Citation Accuracy: {res['citation_correctness'] * 100:.1f}%"
            )
            st.rerun()

# 1. Summary KPI cards for latest run
if runs_data:
    latest = runs_data[0]["_raw_record"]
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        render_kpi_card(
            "Benchmark F1 Score",
            f"{latest.f1_score:.3f}",
            "Harmonic mean of precision & recall",
            "🎯",
        )
    with k_col2:
        render_kpi_card(
            "Citation Correctness",
            f"{latest.citation_correctness * 100:.1f}%",
            "Verified against UNECE source chunks",
            "🛡️",
        )
    with k_col3:
        render_kpi_card(
            "Hallucination Rate",
            f"{latest.hallucination_rate * 100:.1f}%",
            "Claims lacking grounded regulatory text",
            "⚠️",
        )
    with k_col4:
        render_kpi_card(
            "Avg Latency", f"{latest.avg_latency_ms:.0f} ms", "Per requirement review cycle", "⏱️"
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 2. Comparison Table
    st.markdown("#### Configuration Benchmark Comparison")
    df_runs = pd.DataFrame(runs_data).drop(columns=["_raw_record"])
    st.dataframe(df_runs, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 3. Bar Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Precision, Recall, and F1 by Configuration")
        chart_df = []
        for r in runs[:6]:
            chart_df.extend(
                [
                    {
                        "Configuration": r.config_name[:25],
                        "Metric": "Precision",
                        "Value": r.precision,
                    },
                    {"Configuration": r.config_name[:25], "Metric": "Recall", "Value": r.recall},
                    {
                        "Configuration": r.config_name[:25],
                        "Metric": "F1 Score",
                        "Value": r.f1_score,
                    },
                ]
            )
        if chart_df:
            fig_bar = px.bar(
                pd.DataFrame(chart_df),
                x="Configuration",
                y="Value",
                color="Metric",
                barmode="group",
                color_discrete_map={
                    "Precision": "#38BDF8",
                    "Recall": "#F5A623",
                    "F1 Score": "#10B981",
                },
            )
            fig_bar.update_layout(
                margin={"t": 10, "b": 10, "l": 10, "r": 10},
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis={"range": [0, 1.05], "gridcolor": "#E2E8F0"},
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.markdown("#### Latency vs. Citation Correctness")
        scatter_data = [
            {
                "Configuration": r.config_name,
                "Latency (ms)": r.avg_latency_ms,
                "Citation Correctness": r.citation_correctness,
            }
            for r in runs[:10]
        ]
        if scatter_data:
            fig_sc = px.scatter(
                pd.DataFrame(scatter_data),
                x="Latency (ms)",
                y="Citation Correctness",
                text="Configuration",
                color_discrete_sequence=["#F5A623"],
            )
            fig_sc.update_traces(textposition="top center", marker={"size": 12})
            fig_sc.update_layout(
                margin={"t": 10, "b": 10, "l": 10, "r": 10},
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis={"range": [0, 1.1], "gridcolor": "#E2E8F0"},
            )
            st.plotly_chart(fig_sc, use_container_width=True)

    st.divider()

    # 4. Failure-Case & Discrepancy Explorer
    st.markdown("#### Failure-Case & Discrepancy Explorer")
    st.caption(
        "Inspect individual evaluation test cases where predictions diverged from ground truth."
    )

    latest_metrics = latest.get_metrics()
    item_results = latest_metrics.get("item_results", [])

    if item_results:
        discrepancies = [it for it in item_results if not it.get("is_match")]
        st.write(
            f"Showing **{len(discrepancies)}** discrepancies out of **{len(item_results)}** test requirements:"
        )

        for disc in item_results:
            match_icon = "✅" if disc.get("is_match") else "⚠️"
            with st.expander(
                f"{match_icon} {disc.get('req_id')}: {disc.get('text')[:70]}...",
                expanded=not disc.get("is_match"),
            ):
                st.markdown(f"**Full Requirement Text**: `{disc.get('text')}`")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Expected Issues**: `{disc.get('expected_issues')}`")
                with c2:
                    st.markdown(f"**Predicted Issues**: `{disc.get('predicted_issues')}`")
                with c3:
                    st.markdown(f"**Latency**: `{disc.get('latency_ms')} ms`")
else:
    st.info(
        "No evaluation runs recorded. Click 'Run Benchmark Now' above to generate baseline metrics."
    )
