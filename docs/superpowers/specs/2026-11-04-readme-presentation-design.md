# README Presentation Refresh — Design

## Intent

Present Media Content Intelligence as an understandable, credible project for
developers, evaluators, and prospective users. The README must clearly state
what works locally today, what will be externally exposed in a future release,
and how the media-search workflow operates without publishing restricted data.

## Goals

- Replace the text-only architecture description with balanced explanatory
  diagrams.
- State at every API exposure that the API currently runs on localhost and
  will be exposed externally soon.
- Add a concise, publishable demo-gallery section that points to original
  walkthrough videos hosted as GitHub Release assets.
- Preserve the existing no-dataset/no-model publication boundary.

## Non-goals

- Do not publish downloaded advertisements, social-media videos, annotations,
  model weights, or embeddings.
- Do not claim that mock model integrations are production inference.
- Do not add a real public API endpoint in this change.

## Approaches considered

1. **Production-ready README refresh (selected):** focused narrative, two
   diagrams, local-versus-external API notices, and Release-hosted original
   walkthroughs. This provides the best project overview without turning the
   README into a full developer portal.
2. Documentation-only refresh with static screenshots. Safer but does not meet
   the requested video demonstration goal.
3. Full developer portal README. More extensive API and deployment detail than
   is appropriate for the project landing page.

## Design

### README structure

1. Product statement and implementation-status callout.
2. “What it does” outcomes and core capabilities.
3. System workflow diagram: data sources through review and observability.
4. Local API and UI quick start, with an externally-exposed-soon notice next
   to every URL and API example.
5. Search-decision diagram: query, retrieval, evidence validation, guardrails,
   review, and response.
6. Demo gallery: original walkthrough videos linked from the GitHub Release.
7. Dataset and publication boundary; development, tests, and extension points.

### Diagram assets

Create two editable `.excalidraw` source files under `docs/diagrams/`, plus
README-renderable SVG exports in `docs/diagrams/rendered/`:

- `media-intelligence-workflow`: end-to-end architecture and data flow.
- `search-governance-flow`: search and evidence/rights decision flow.

The SVGs are visual renderings of the same content. Excalidraw source remains
the editable canonical form.

### Demo media

- Record only original product demonstrations: local Streamlit/API search,
  result metadata, and safe-review behaviour.
- Upload media as GitHub Release assets under a `demo-assets` release; do not
  commit video files to Git.
- README will reference the final Release-asset URLs after upload.
- Until the videos have been recorded and uploaded, the README will include a
  clearly marked “Demo assets pending publication” section rather than
  fabricated or broken links.

### Security and accuracy

- The README will state that localhost endpoints are development interfaces;
  external access is planned but not yet available.
- Diagrams and captions distinguish the current deterministic catalog search
  from future production ML/indexing integrations.
- Dataset and model publication controls remain unchanged.

## Acceptance criteria

- Every URL/API command in the README has accurate local-only/external-soon
  context.
- Both diagrams render in GitHub Markdown and source `.excalidraw` files are
  editable.
- README media does not include restricted dataset content.
- Release asset workflow is documented and all referenced URLs are valid once
  assets are uploaded.
- Markdown links and diagrams render cleanly; publication safety still passes.
