"""Tests for programmatic citation verification."""

import pytest

from app.agents.nodes.verify_citations import verify_single_finding
from app.rag.chunker import RegulationChunk
from app.rag.embeddings import DeterministicEmbedding
from app.rag.vector_store import VectorStore


@pytest.fixture
def test_store(tmp_path):
    temp_dir = str(tmp_path / "chroma_test_citations")
    store = VectorStore(persist_dir=temp_dir, embedding_engine=DeterministicEmbedding())
    chunks = [
        RegulationChunk(
            chunk_id="R48-6.2.7",
            document="UNECE Regulation No. 48",
            clause_id="6.2.7.3",
            section_title="Dipped-Beam Cleaning",
            text="Dipped-beam headlamps with a light source or LED module(s) producing the principal dipped-beam and having a total objective luminous flux which exceeds 2,000 lumens must only be installed in conjunction with the installation of headlamp cleaning devices according to Regulation No. 45.",
        ),
        RegulationChunk(
            chunk_id="R48-6.5.9",
            document="UNECE Regulation No. 48",
            clause_id="6.5.9",
            section_title="Direction-Indicator Flashing",
            text="The frequency of the light flash must be 90 +/- 30 periods per minute (1.5 +/- 0.5 Hz).",
        ),
    ]
    store.add_chunks(chunks)
    return store


def test_valid_exact_citation(test_store):
    finding = {
        "id": "F-01",
        "req_id": "REQ-01",
        "confidence": 0.95,
        "evidence": {
            "chunk_id": "R48-6.5.9",
            "quote": "frequency of the light flash must be 90 +/- 30 periods per minute (1.5 +/- 0.5 Hz)",
            "document": "UNECE Regulation No. 48",
            "clause_id": "6.5.9",
        },
    }

    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is True
    assert "VERIFIED: Verbatim quote confirmed" in verified["citation_verification_note"]
    assert verified["confidence"] == 0.95


def test_hallucinated_chunk_id(test_store):
    finding = {
        "id": "F-02",
        "req_id": "REQ-02",
        "confidence": 0.90,
        "evidence": {
            "chunk_id": "R999-NONEXISTENT",
            "quote": "Some invented regulatory requirement",
            "document": "Fake Reg",
            "clause_id": "999",
        },
    }

    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is False
    assert verified["confidence"] <= 0.10
    assert "HALLUCINATED CHUNK" in verified["citation_verification_note"]


def test_existing_chunk_with_hallucinated_quote(test_store):
    finding = {
        "id": "F-03",
        "req_id": "REQ-03",
        "confidence": 0.95,
        "evidence": {
            "chunk_id": "R48-6.2.7",
            "quote": "Headlamps must emit green or purple laser light during nighttime driving.",
            "document": "UNECE Regulation No. 48",
            "clause_id": "6.2.7.3",
        },
    }

    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is False
    assert verified["confidence"] <= 0.20
    assert "UNVERIFIED QUOTE" in verified["citation_verification_note"]


def test_fuzzy_quote_matching(test_store):
    # Minor casing and punctuation differences
    finding = {
        "id": "F-04",
        "req_id": "REQ-04",
        "confidence": 0.90,
        "evidence": {
            "chunk_id": "R48-6.5.9",
            "quote": "frequency of the light flash must be 90 +/- 30 periods per minute 1.5 +/- 0.5 hz",
            "document": "UNECE Regulation No. 48",
            "clause_id": "6.5.9",
        },
    }

    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is True


def test_value_engineering_without_citation(test_store):
    finding = {
        "id": "F-VE-01",
        "req_id": "REQ-VE-01",
        "type": "value_engineering",
        "severity": "minor",
        "title": "Value Engineering: Relax Over-Specified LED Binning",
        "explanation": "Relaxing from single-bin to AEC-Q102 3-step MacAdam ellipse saves €2.85/unit BOM cost.",
        "financial_impact_eur": 2.85,
        "financial_impact_type": "bom_cost_out",
        "evidence": None,
        "confidence": 0.94,
    }
    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is True
    assert "General engineering analysis" in verified["citation_verification_note"]


def test_fmvss_citation_verification(test_store):
    test_store.add_chunks(
        [
            RegulationChunk(
                chunk_id="FMVSS108-S6.1.1.4",
                document="FMVSS 108",
                clause_id="S6.1.1.4",
                section_title="Turn Signal Area",
                text="Front turn signal lamps must have an effective projected luminous lens area of not less than 22 cm2 (3.5 sq. in.).",
            )
        ]
    )
    finding = {
        "id": "F-FMVSS-01",
        "req_id": "REQ-TS-01",
        "type": "conflict",
        "severity": "critical",
        "financial_impact_eur": 280000.0,
        "financial_impact_type": "tooling_risk",
        "confidence": 0.98,
        "evidence": {
            "chunk_id": "FMVSS108-S6.1.1.4",
            "quote": "effective projected luminous lens area of not less than 22 cm2",
            "document": "FMVSS 108",
            "clause_id": "S6.1.1.4",
        },
    }
    verified = verify_single_finding(finding, test_store)
    assert verified["citation_verified"] is True
    assert "VERIFIED: Verbatim quote confirmed" in verified["citation_verification_note"]
