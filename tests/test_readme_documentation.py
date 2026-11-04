"""Public README and diagram-contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = PROJECT_ROOT / "docs" / "diagrams"

DIAGRAMS = {
    "media-intelligence-workflow": {
        "Data Sources",
        "Ingestion & Indexing",
        "Search & Orchestration",
        "Evidence & Governance",
        "Delivery & Observability",
    },
    "search-governance-flow": {
        "Natural-language query",
        "Hybrid retrieval",
        "Evidence Validator",
        "Guardrails",
        "Human review",
        "Search response",
    },
}


@pytest.mark.parametrize(("name", "required_labels"), DIAGRAMS.items())
def test_excalidraw_source_is_editable(name: str, required_labels: set[str]) -> None:
    source_path = DIAGRAM_DIR / f"{name}.excalidraw"

    document = json.loads(source_path.read_text(encoding="utf-8"))

    assert document["type"] == "excalidraw"
    assert document["version"] == 2
    assert len(document["elements"]) >= 15
    labels = {
        element.get("text", "")
        for element in document["elements"]
        if element.get("type") == "text"
    }
    assert required_labels <= labels


@pytest.mark.parametrize(("name", "required_labels"), DIAGRAMS.items())
def test_svg_export_is_accessible(name: str, required_labels: set[str]) -> None:
    svg_path = DIAGRAM_DIR / "rendered" / f"{name}.svg"

    root = ElementTree.parse(svg_path).getroot()
    exported_text = " ".join(root.itertext())

    assert root.tag.endswith("svg")
    assert root.get("role") == "img"
    assert root.get("aria-labelledby")
    assert all(label in exported_text for label in required_labels)
