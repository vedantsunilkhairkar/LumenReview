"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.db.session import init_db
from app.main import app


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "LumenReview"


def test_requirements_upload(client):
    sample_text = """
    REQ-01: Low beam headlamp shall have luminous flux of 2500 lumens.
    REQ-02: Turn signal flashing frequency shall be 1.5 Hz.
    """
    response = client.post("/requirements/upload", data={"raw_text": sample_text})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 2
    assert data["requirements"][0]["req_id"] == "REQ-01"


def test_full_review_lifecycle_api(client):
    # 1. Start review
    payload = {
        "raw_input": "REQ-LAMP-01: Principal dipped-beam shall produce 2500 lumens without washing system."
    }
    create_resp = client.post("/reviews", json=payload)
    assert create_resp.status_code == 200
    review_data = create_resp.json()
    review_id = review_data["review_id"]
    assert review_data["status"] == "waiting_for_human"
    assert review_data["total_findings"] >= 1

    finding_id = review_data["findings"][0]["id"]

    # 2. Check details
    get_resp = client.get(f"/reviews/{review_id}")
    assert get_resp.status_code == 200
    details = get_resp.json()
    assert details["id"] == review_id
    assert len(details["findings"]) >= 1
    assert len(details["trace"]) > 0

    # 3. Post decisions
    decisions_payload = {
        "decisions": {
            finding_id: {
                "decision": "approved",
                "notes": "Verified against UNECE R48 6.2.7.3.",
            }
        }
    }
    decision_resp = client.post(f"/reviews/{review_id}/decisions", json=decisions_payload)
    assert decision_resp.status_code == 200
    dec_result = decision_resp.json()
    assert dec_result["status"] == "completed"
    assert dec_result["approved_findings_count"] == 1
    assert "Executive Summary" in dec_result["report"]["markdown_content"]

    # 4. Download report as Markdown
    md_resp = client.get(f"/reviews/{review_id}/report?format=md")
    assert md_resp.status_code == 200
    assert "LumenReview Homologation Review Report" in md_resp.text

    # 5. Download report as PDF
    pdf_resp = client.get(f"/reviews/{review_id}/report?format=pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")


def test_rag_search_endpoint(client):
    search_payload = {
        "query": "What is the requirement for dipped-beam luminous flux exceeding 2000 lumens?",
        "top_k": 3,
    }
    resp = client.post("/rag/search", json=search_payload)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    assert any("6.2.7" in r["clause_id"] or "2,000" in r["text"] for r in results)
