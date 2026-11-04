"""Protect the public README, architecture diagrams, and documentation links.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

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
        "Experience",
        "Orchestration",
        "Retrieval Intelligence",
        "Evidence Governance",
        "Observability",
        "Ranked, explainable media results",
    },
    "search-governance-flow": {
        "Natural-language query",
        "Intent + filters",
        "Metadata search",
        "BM25 search",
        "RRF rank fusion",
        "Evidence assessment",
        "Evidence sufficient?",
        "Ranked response",
        "Human review required",
    },
}


@pytest.mark.parametrize(("name", "required_labels"), DIAGRAMS.items())
def test_excalidraw_source_is_editable(name: str, required_labels: set[str]) -> None:
    """Every architecture visual retains a valid editable Excalidraw source."""
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
    assert all(
        element.get("roughness") == 0
        for element in document["elements"]
        if element.get("type") != "text" and "roughness" in element
    )


@pytest.mark.parametrize(("name", "required_labels"), DIAGRAMS.items())
def test_svg_export_is_accessible(name: str, required_labels: set[str]) -> None:
    """Every rendered diagram exposes accessible labels and expected content."""
    svg_path = DIAGRAM_DIR / "rendered" / f"{name}.svg"

    root = ElementTree.parse(svg_path).getroot()
    exported_text = " ".join(root.itertext())

    assert root.tag.endswith("svg")
    assert root.get("role") == "img"
    assert root.get("aria-labelledby")
    assert all(label in exported_text for label in required_labels)


@pytest.mark.parametrize("name", DIAGRAMS)
def test_svg_export_uses_clean_enterprise_canvas(name: str) -> None:
    """Rendered diagrams use the approved canvas and clean SVG styling."""
    svg_path = DIAGRAM_DIR / "rendered" / f"{name}.svg"
    root = ElementTree.parse(svg_path).getroot()
    source = svg_path.read_text(encoding="utf-8")
    assert root.get("width") == "1600" and root.get("height") == "900"
    assert root.get("viewBox") == "0 0 1600 900"
    assert "feTurbulence" not in source
    assert "feDisplacementMap" not in source


def test_readme_excludes_internal_repository_strategy_disclosure() -> None:
    """Internal repository strategy details stay out of the public README."""
    readme = " ".join(README_PATH.read_text(encoding="utf-8").lower().split())
    for phrase in ("retrieval strategy", "dataset research"):
        assert phrase not in readme


@pytest.mark.parametrize("name", DIAGRAMS)
def test_excalidraw_drawables_use_zero_roughness(name: str) -> None:
    """Editable drawable elements use clean zero roughness."""
    source_path = DIAGRAM_DIR / f"{name}.excalidraw"
    document = json.loads(source_path.read_text(encoding="utf-8"))
    assert all(
        element["roughness"] == 0
        for element in document["elements"]
        if element.get("type") != "text" and "roughness" in element
    )


def test_readme_has_approved_portfolio_template_structure() -> None:
    """The public README follows the approved portfolio template structure."""
    readme = README_PATH.read_text(encoding="utf-8").lower()
    sections = (
        "hero navigation", "table of contents", "about the project", "key capabilities",
        "architecture", "my contribution", "built with", "getting started", "usage",
        "api reference", "evaluation and reproducibility", "roadmap", "documentation",
        "contact", "license", "back to top",
    )
    assert all(section in readme for section in sections)


def test_readme_embeds_both_visual_explanations() -> None:
    """The README balances its narrative with both architecture visuals."""
    readme = README_PATH.read_text(encoding="utf-8")

    assert "docs/diagrams/rendered/media-intelligence-workflow.svg" in readme
    assert "docs/diagrams/rendered/search-governance-flow.svg" in readme
    assert "Editable Excalidraw source" in readme


def test_readme_explains_local_api_lifecycle_at_every_localhost_exposure() -> None:
    """Every localhost reference states that external exposure is forthcoming."""
    lines = README_PATH.read_text(encoding="utf-8").splitlines()
    localhost_lines = [index for index, line in enumerate(lines) if "localhost" in line]

    assert localhost_lines
    for index in localhost_lines:
        context = " ".join(lines[max(0, index - 6) : index + 7]).lower()
        assert "externally exposed soon" in context


def test_readme_does_not_advertise_unpublished_demo_assets() -> None:
    """Pending release videos must not be represented by broken public links."""
    readme = " ".join(README_PATH.read_text(encoding="utf-8").split())

    assert "releases/download/demo-assets-v1" not in readme
    assert "release publication is pending" in readme.lower()
    assert "restricted dataset videos" in readme.lower()
    assert "will never be included in git or release assets" in readme.lower()


def test_readme_states_current_implementation_boundary() -> None:
    """The README distinguishes the runnable demo from future production ML."""
    readme = " ".join(README_PATH.read_text(encoding="utf-8").lower().split())

    assert "mock-first reference application" in readme
    assert "deterministic ranking" in readme
    assert "does not yet run production multimodal inference" in readme
