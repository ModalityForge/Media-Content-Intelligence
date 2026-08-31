"""Agent tests."""

import pytest
from agents.media_orchestrator import MediaOrchestratorAgent
from agents.evidence_validator import EvidenceValidatorAgent


@pytest.fixture
def orchestrator():
    return MediaOrchestratorAgent()


@pytest.fixture
def validator():
    return EvidenceValidatorAgent()


async def test_orchestrator_calls_validator(orchestrator):
    """Test orchestrator calls evidence validator."""
    result = await orchestrator.run(
        query="Find Messi drinking Pepsi",
        max_results=5,
        trace_id="test-001",
    )
    assert "validation" in result


def test_orchestrator_parses_query(orchestrator):
    """Test orchestrator query parsing."""
    intent = orchestrator.parse_query("Find Messi drinking Pepsi")
    assert "Messi" in intent["talents"]
    assert "Pepsi" in intent["brands"]["required"]


def test_evidence_validator_validate():
    """Test evidence validator."""
    validator = EvidenceValidatorAgent()
    evidence_bundle = {
        "clip_id": "clip-001",
        "query": "Find Messi drinking Pepsi",
        "visual_evidence": {"logos": ["Adidas"], "talent_matches": ["Messi"]},
        "rights_evidence": {"rights_cleared": True},
    }
    result = validator.validate(evidence_bundle)
    assert result.clip_id == "clip-001"


def test_evidence_validator_requires_review():
    """Test human review requirement."""
    validator = EvidenceValidatorAgent()
    assert validator.requires_human_review(
        type("Result", (), {"overall_confidence": 0.6, "results": []})()
    )