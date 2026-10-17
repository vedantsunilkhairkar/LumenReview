"""Page 4: UNECE Regulations Knowledge Base & Hybrid Search Debugger."""

import pandas as pd
import streamlit as st

from ui.state import get_client
from ui.theme import apply_theme, render_sidebar

st.set_page_config(page_title="Knowledge Base | LumenReview", page_icon="📚", layout="wide")
apply_theme()
render_sidebar()

client = get_client()

st.markdown(
    """
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0;">Automotive Regulations Knowledge Base</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin: 0.25rem 0 0 0;">
            Inspect ingested UNECE standards, clause hierarchies, chunk distributions, and test hybrid RAG search.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. Sources Overview
sources_data = client.get_sources()
total_chunks = sources_data.get("total_chunks", 0)
sources = sources_data.get("sources", [])

kpi_col1, kpi_col2, kpi_col3 = st.columns([1, 1, 1.5])

with kpi_col1:
    st.metric(
        "Total Ingested Clauses", str(total_chunks), help="Atomic regulation chunks in ChromaDB"
    )
with kpi_col2:
    st.metric("Regulatory Standards", str(len(sources)), help="Indexed standard documents")
with kpi_col3:
    if st.button("🔄 Re-Index Knowledge Base", use_container_width=True):
        from app.rag.loader import RegulationLoader
        from app.rag.vector_store import VectorStore

        loader = RegulationLoader()
        chunks = loader.load_all()
        store = VectorStore()
        count = store.add_chunks(chunks)
        st.success(f"Indexed {count} regulation clauses.")
        st.rerun()

st.markdown("#### Ingested Regulatory Documents")
if sources:
    df_sources = pd.DataFrame(sources)
    st.dataframe(df_sources, use_container_width=True, hide_index=True)
else:
    st.info("No documents currently indexed.")

st.divider()

# 2. Interactive Hybrid Search Debugger
st.markdown("#### Hybrid Retrieval Debugger (Vector + BM25)")
st.caption("Test semantic similarity and exact keyword retrieval against indexed UNECE clauses.")

SAMPLE_QUERIES = [
    "Dipped-beam luminous flux exceeding 2000 lm cleaning device",
    "Direction-indicator flashing frequency in periods per minute or Hz",
    "Passing beam cut-off vertical inclination mounting height below 0.8m",
    "Daytime running lamp automatic shut off when headlamps switch on",
    "Stop lamp mounting height limits and visibility angles",
]

sample_query = st.selectbox("Sample Homologation Queries:", ["-- Custom Query --"] + SAMPLE_QUERIES)

default_q = "" if sample_query == "-- Custom Query --" else sample_query
search_text = st.text_input(
    "Search Query:", value=default_q, placeholder="e.g. dipped-beam luminous flux cleaning..."
)

slider_col1, slider_col2 = st.columns([1, 1])
with slider_col1:
    top_k = st.slider("Top Results (K)", 1, 10, 5)

if search_text:
    with st.spinner("Executing hybrid retrieval..."):
        results = client.search_regulations(search_text, top_k=top_k)

    if not results:
        st.info("No matching regulation clauses found.")
    else:
        st.markdown(f"**Found {len(results)} matching regulation clauses:**")
        for idx, res in enumerate(results, start=1):
            score = res.get("fused_score", res.get("score", 0.0))
            chunk_id = res.get("chunk_id", "")
            doc = res.get("document", "")
            clause_id = res.get("clause_id", "")
            title = res.get("section_title", "")
            text = res.get("text", "")

            with st.container(border=True):
                col_head1, col_head2 = st.columns([3, 1])
                with col_head1:
                    st.markdown(f"**{idx}. {doc} — Clause {clause_id}** (`{chunk_id}`)")
                    st.caption(title)
                with col_head2:
                    st.metric("RRF Score", f"{score:.4f}")

                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border-left: 3px solid #F5A623; padding: 0.6rem 0.8rem; border-radius: 4px; font-size: 0.85rem; color: #334155;">
                        {text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
