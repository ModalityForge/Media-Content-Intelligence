"""Public README and diagram-contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = PROJECT_ROOT / "docs" / "diagrams"
README_PATH = PROJECT_ROOT / "README.md"

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


def test_readme_embeds_both_visual_explanations() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "docs/diagrams/rendered/media-intelligence-workflow.svg" in readme
    assert "docs/diagrams/rendered/search-governance-flow.svg" in readme
    assert "Editable Excalidraw source" in readme


def test_readme_explains_local_api_lifecycle_at_every_localhost_exposure() -> None:
    lines = README_PATH.read_text(encoding="utf-8").splitlines()
    localhost_lines = [index for index, line in enumerate(lines) if "localhost" in line]

    assert localhost_lines
    for index in localhost_lines:
        context = " ".join(lines[max(0, index - 6) : index + 7]).lower()
        assert "externally exposed soon" in context


def test_readme_links_release_demos_without_publishing_restricted_media() -> None:
    readme = " ".join(README_PATH.read_text(encoding="utf-8").split())
    release_base = (
        "https://github.com/ModalityForge/Media-Content-Intelligence/"
        "releases/download/demo-assets-v1/"
    )

    assert release_base + "mci-search-demo.mp4" in readme
    assert release_base + "mci-api-governance-demo.mp4" in readme
    assert "original product walkthrough" in readme.lower()
    assert "restricted dataset videos" in readme.lower()
    assert "never included in git or release assets" in readme.lower()


def test_readme_states_current_implementation_boundary() -> None:
    readme = " ".join(README_PATH.read_text(encoding="utf-8").lower().split())

    assert "mock-first reference implementation" in readme
    assert "deterministic metadata" in readme
    assert "does not yet run production multimodal inference" in readme
