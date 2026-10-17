"""Tests for LLM schemas, prompts, and MockLLM deterministic responses."""

from app.llm.factory import get_llm_provider
from app.llm.mock import MockLLM
from app.llm.prompts.v1_analysis import build_analysis_prompt
from app.llm.prompts.v1_conflict import build_conflict_prompt
from app.llm.schemas import (
    ConflictAnalysisResult,
    RequirementAnalysisResult,
)


def test_mock_llm_high_flux_missing_cleaning():
    llm = MockLLM()
    prompt = build_analysis_prompt(
        req_id="REQ-HEADLAMP-01",
        req_text="The principal dipped-beam LED modules shall produce 2,500 lumens.",
        retrieved_clauses=[
            {
                "chunk_id": "R48-6.2.7",
                "document": "UNECE Regulation No. 48",
                "clause_id": "6.2.7.3",
                "text": "Dipped-beam headlamps with a light source or LED module(s) producing the principal dipped-beam and having a total objective luminous flux which exceeds 2,000 lumens must only be installed in conjunction with the installation of headlamp cleaning devices according to Regulation No. 45.",
            }
        ],
    )

    result = llm.generate(prompt, response_model=RequirementAnalysisResult)
    assert isinstance(result, RequirementAnalysisResult)
    assert result.req_id == "REQ-HEADLAMP-01"
    assert len(result.issues) >= 1

    issue = result.issues[0]
    assert issue.type == "non_compliant"
    assert issue.severity == "critical"
    assert issue.evidence is not None
    assert issue.evidence.chunk_id == "R48-6.2.7"
    assert "cleaning" in issue.explanation.lower()
    assert issue.suggested_rewrite is not None
    assert "cleaning" in issue.suggested_rewrite.text.lower()


def test_mock_llm_ambiguous_requirement():
    llm = MockLLM()
    prompt = build_analysis_prompt(
        req_id="REQ-FOG-02",
        req_text="Front fog lamps shall provide sufficient illumination under normal conditions.",
        retrieved_clauses=[],
    )

    result = llm.generate(prompt, response_model=RequirementAnalysisResult)
    assert isinstance(result, RequirementAnalysisResult)
    assert len(result.issues) >= 1
    issue = result.issues[0]
    assert issue.type == "ambiguous"
    assert issue.suggested_rewrite is not None
    assert "lux" in issue.suggested_rewrite.text


def test_mock_llm_conflict_detection():
    llm = MockLLM()
    requirements = [
        {"req_id": "REQ-01", "text": "Daytime running lamps shall remain on at all times."},
        {
            "req_id": "REQ-02",
            "text": "When low beam headlamps are switched on, daytime running lamps must switch off.",
        },
    ]
    prompt = build_conflict_prompt(requirements)
    result = llm.generate(prompt, response_model=ConflictAnalysisResult)

    assert isinstance(result, ConflictAnalysisResult)
    assert len(result.conflicts) >= 1
    conflict = result.conflicts[0]
    assert conflict.type == "conflict"
    assert conflict.severity in ["critical", "major"]


def test_llm_factory_fallback_to_mock():
    # When api_key is missing, should safely fallback to MockLLM
    provider = get_llm_provider("gemini", api_key=None)
    assert isinstance(provider, MockLLM)

    mock_provider = get_llm_provider("mock")
    assert isinstance(mock_provider, MockLLM)
