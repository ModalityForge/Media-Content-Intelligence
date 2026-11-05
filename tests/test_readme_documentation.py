"""Protect the public README, architecture diagrams, and documentation links.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from __future__ import annotations

import json
import re
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
    """Internal repository strategy details stay out of all public visuals."""
    paths = [README_PATH]
    paths.extend(DIAGRAM_DIR / "rendered" / f"{name}.svg" for name in DIAGRAMS)
    paths.extend(DIAGRAM_DIR / f"{name}.excalidraw" for name in DIAGRAMS)
    public_text = " ".join(path.read_text(encoding="utf-8") for path in paths)
    forbidden_concepts = (
        r"\b(?:git[ -]?ignore|gitignore)\b",
        r"\b(?:git[ -]?ignore(?:d)?|ignored|uncommitted)\s+(?:files?|code|implementation)\b",
        r"\bprivate\s+(?:code|implementation)\b",
        r"\brestricted\s+storage\b",
        r"\b(?:raw|restricted)\s+(?:media|videos?|assets)\b.{0,100}\b(?:stay|stays|remain|remains|kept|local)\b",
        r"\b(?:media|storage)\b.{0,100}\b(?:stay|stays|remain|remains|kept)\s+local\b",
        r"\bdownload\s+(?:strategy|logic|tooling)\b",
    )
    for concept in forbidden_concepts:
        assert re.search(concept, public_text, re.I) is None


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
    """The README has real section headings and links into those sections."""
    readme = README_PATH.read_text(encoding="utf-8")
    heading_ids: dict[str, str] = {}
    heading_lines: list[tuple[int, str, str]] = []
    for index, line in enumerate(readme.splitlines()):
        markdown = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        html = re.search(r"<h[1-6](?:\s+id=[\"']([^\"']+)[\"'])?[^>]*>(.*?)</h[1-6]>", line, re.I)
        if markdown:
            title = re.sub(r"[`*_]", "", markdown.group(1)).strip()
            slug = re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")
        elif html:
            title = re.sub(r"<[^>]+>", "", html.group(2)).strip()
            slug = html.group(1) or re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")
        else:
            continue
        heading_ids[title.lower()] = slug
        heading_lines.append((index, title.lower(), slug))

    required_headings = (
        "table of contents", "about the project", "key capabilities", "architecture",
        "my contribution", "built with", "getting started", "usage", "api reference",
        "evaluation and reproducibility", "roadmap", "documentation", "contact", "license",
    )
    assert all(section in heading_ids for section in required_headings)

    def anchor_links(text: str) -> list[tuple[str, str]]:
        """Return Markdown and HTML fragment links as normalized label-target pairs."""
        markdown_links = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", text, re.I)
        html_links = re.findall(r"<a\b[^>]*href=[\"']#([^\"']+)[\"'][^>]*>(.*?)</a>", text, re.I | re.S)
        return [(label.strip().lower(), target) for label, target in markdown_links] + [
            (re.sub(r"<[^>]+>", "", label).strip().lower(), target)
            for target, label in html_links
        ]

    links = anchor_links(readme)
    first_section_line = min(index for index, title, _ in heading_lines if title != "media content intelligence")
    hero_text = "\n".join(readme.splitlines()[:first_section_line])
    hero_targets = {target for _, target in anchor_links(hero_text)}
    assert len(hero_targets & set(heading_ids.values())) >= 4

    top_slug = heading_lines[0][2]
    assert any("back to top" in label and target == top_slug for label, target in links)


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
