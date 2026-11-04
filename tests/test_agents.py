"""Verify the public orchestration and evidence-validation agent contracts.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

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


def test_orchestrator_does_not_parse_us_inside_another_word(orchestrator):
    """Territory detection only accepts complete country names."""
    intent = orchestrator.parse_query("Find business software commercials")
    assert intent["territory"] is None
    assert "territory" not in intent["filters"]


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
    assert not result.overall_passed
    assert result.requires_human_review


def test_evidence_validator_never_invents_missing_evidence(validator):
    """Missing model evidence must fail consistently instead of passing randomly."""
    evidence_bundle = {
        "clip_id": "clip-002",
        "query": "Find Messi drinking Pepsi",
        "visual_evidence": {"logos": [], "talent_matches": [], "actions": []},
        "rights_evidence": {"rights_cleared": True},
    }

    results = [validator.validate(evidence_bundle) for _ in range(10)]

    assert all(not result.overall_passed for result in results)
    assert all(result.requires_human_review for result in results)
    assert all(result.model_dump() == results[0].model_dump() for result in results)


def test_evidence_validator_checks_the_requested_brand(validator):
    """A different detected logo does not satisfy the requested brand criterion."""
    result = validator.validate(
        {
            "clip_id": "clip-003",
            "query": "Find a Pepsi commercial",
            "visual_evidence": {"logos": ["Adidas"]},
            "rights_evidence": {"rights_cleared": True},
        }
    )

    brand_result = next(
        item for item in result.results if item.criterion == "required_brands_visible"
    )
    assert not brand_result.passed
    assert result.requires_human_review


def test_evidence_validator_requires_review():
    """Test human review requirement."""
    validator = EvidenceValidatorAgent()
    assert validator.requires_human_review(
        type("Result", (), {"overall_confidence": 0.6, "results": []})()
    )
