"""Tests for LangGraph agent workflow orchestration and human review gate."""

import pytest

from app.agents.graph import execute_review_analysis, resume_review_with_decisions
from app.agents.nodes.report import export_pdf_report
from app.rag.loader import RegulationLoader
from app.rag.vector_store import VectorStore


@pytest.fixture(scope="module", autouse=True)
def setup_regulations_corpus():
    """Ensure regulation knowledge base has chunks indexed for test run."""
    store = VectorStore()
    if store.count() == 0:
        loader = RegulationLoader()
        chunks = loader.load_all()
        store.add_chunks(chunks)


def test_agent_graph_execution_and_human_review_loop():
    input_text = """
    REQ-001: The principal dipped-beam LED modules shall produce 2,500 lumens luminous flux.
    REQ-002: Daytime running lamps shall remain on at all times under normal conditions.
    """

    run_id = "TEST-RUN-GRAPH-01"

    # 1. Run pipeline up to human review interrupt
    state = execute_review_analysis(run_id=run_id, raw_input=input_text)

    assert state["run_id"] == run_id
    assert len(state["requirements"]) == 2
    assert len(state["findings"]) >= 1

    # Check trace steps were recorded
    nodes_executed = [step["node"] for step in state["trace"]]
    assert "ingest_requirements" in nodes_executed
    assert "sanitize" in nodes_executed
    assert "retrieve" in nodes_executed
    assert "analyze" in nodes_executed
    assert "verify_citations" in nodes_executed
    assert "conflict_check" in nodes_executed
    assert "human_review" in nodes_executed

    # Verify at least one finding has verified citations
    verified_flags = [f.get("citation_verified") for f in state["findings"]]
    assert any(verified_flags)

    # 2. Simulate human reviewer decisions
    finding_id = state["findings"][0]["id"]
    approvals = {
        finding_id: {
            "decision": "approved",
            "notes": "Confirmed non-compliance with UNECE R48 6.2.7.3 in homologation review.",
        }
    }

    # 3. Resume graph execution to generate report
    resumed_state = resume_review_with_decisions(
        run_id=run_id,
        approvals=approvals,
        current_state=state,
    )

    assert resumed_state["status"] == "completed"
    assert resumed_state["report"] is not None
    report = resumed_state["report"]
    assert report["total_findings_approved"] >= 1
    assert "Executive Summary" in report["markdown_content"]
    assert "Sign-Off" in report["markdown_content"]

    # 4. Verify PDF export generates valid bytes
    pdf_bytes = export_pdf_report(report)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
