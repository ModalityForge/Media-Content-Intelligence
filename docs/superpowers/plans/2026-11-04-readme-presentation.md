# README Presentation Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a clear, visually balanced README with accurate localhost/external-API messaging, editable Excalidraw diagrams, and original GitHub Release-hosted demo videos.

**Architecture:** Keep diagram source and render artifacts versioned in `docs/diagrams/`; keep video binaries outside Git and publish them as Release assets. Add automated documentation assertions that validate diagram JSON/SVG files, API notices, release URLs, and restricted-media language.

**Tech Stack:** Markdown, Excalidraw JSON, SVG, pytest, ffmpeg, GitHub CLI

**Spec:** `docs/superpowers/specs/2026-11-04-readme-presentation-design.md`

## Global Constraints

- Do not commit downloaded advertisements, social-media videos, annotations, model weights, embeddings, or demo video binaries.
- Every API exposure must say the API is currently localhost-only and will be externally exposed soon.
- Excalidraw JSON is canonical; SVG is the GitHub-rendered export.
- Demo videos contain only original product/API walkthrough material and live as GitHub Release assets.
- Preserve unrelated existing worktree changes.

## Review Focus

- GitHub README rendering: diagrams and video links must resolve from repository-relative or Release URLs.
- API wording: no localhost URL may appear without the external-exposure-soon context in the surrounding section.
- Excalidraw validity: sources must parse as JSON and contain editable elements.
- Publication boundary: README must not imply restricted source videos are published.
- Accuracy: mock-first and deterministic metadata-search limitations must remain explicit.

---

### Task 1: Documentation contract and visual assets

**Files:**
- Create: `tests/test_readme_documentation.py`
- Create: `docs/diagrams/media-intelligence-workflow.excalidraw`
- Create: `docs/diagrams/search-governance-flow.excalidraw`
- Create: `docs/diagrams/rendered/media-intelligence-workflow.svg`
- Create: `docs/diagrams/rendered/search-governance-flow.svg`

**Interfaces:**
- Produces: two editable Excalidraw JSON documents and two README-renderable SVGs.

- [ ] Write tests that require valid Excalidraw JSON, non-empty editable elements, matching SVG exports, and accessible diagram labels.
- [ ] Run the tests and verify they fail because the diagram files are absent.
- [ ] Create both diagram source files and SVG exports.
- [ ] Run the documentation tests and verify the diagram assertions pass.

### Task 2: README narrative and API lifecycle language

**Files:**
- Modify: `README.md`
- Test: `tests/test_readme_documentation.py`

**Interfaces:**
- Consumes: rendered diagram paths from Task 1.
- Produces: public project overview, local API notices, diagram explanations, and demo-gallery contract.

- [ ] Extend the tests to require both diagram embeds, local-only/external-soon notices, mock-first accuracy, release-asset video links, and the restricted-media boundary.
- [ ] Run tests and verify they fail against the old README.
- [ ] Rewrite the README using the approved structure and copy.
- [ ] Run the documentation tests and complete pytest suite.

### Task 3: Original demos, Release publication, and link verification

**Files:**
- Create outside Git: `/tmp/mci-demo-assets/mci-search-demo.mp4`
- Create outside Git: `/tmp/mci-demo-assets/mci-api-governance-demo.mp4`
- Modify: `README.md` only if final Release URLs differ from the planned URLs.

**Interfaces:**
- Consumes: local FastAPI/Streamlit application and README release-link contract.
- Produces: GitHub Release `demo-assets-v1` with two original demonstration videos.

- [ ] Run the local application and capture original UI/API frames without restricted video playback.
- [ ] Assemble two short MP4 walkthroughs with ffmpeg and inspect codec, dimensions, duration, and size.
- [ ] Commit and push documentation assets after publication-safety and full-suite verification.
- [ ] Create/update the GitHub Release and upload both MP4 assets.
- [ ] Verify both release URLs return successfully and README tests still pass.

### Task 4: Final verification and review

**Files:**
- Review: all changed files

**Interfaces:**
- Consumes: completed documentation, diagrams, release URLs, and test results.
- Produces: reviewed, publish-safe GitHub documentation.

- [ ] Run Markdown/link checks available locally, JSON parsing, XML parsing, full pytest, and publication safety.
- [ ] Review the complete diff for accuracy, visual-text balance, and accidental restricted-data references.
- [ ] Confirm GitHub branch and Release assets match the final README.
