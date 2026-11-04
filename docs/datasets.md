# Public Data and Annotation Contract

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

The public repository ships no dataset, downloaded media, model, embedding, or
dataset-acquisition script. Users provide media they are permitted to process,
and all resulting files remain under the ignored local `data/` boundary.

## Minimal smoke dataset

For a reproducible local demonstration, place a few short videos beneath
`data/`, for example:

```text
data/raw/smoke/
├── coffee-commercial.mp4
├── running-shoe-social-ad.mp4
└── football-highlight.webm
```

The catalog recursively discovers MP4, WebM, MOV, MKV, and AVI files. It derives
a stable identifier, title tokens, basic file metadata, and a playable local
path. Descriptive filenames provide useful search signals when no sidecar
annotation exists.

## Candidate annotation model

The search response can carry the following annotation families:

| Field family | Examples | Project use |
|---|---|---|
| Identity | `video_id`, dataset name, source URL, checksum | Provenance and deduplication |
| Semantics | title, description, tags, caption, OCR text | Lexical and future multimodal retrieval |
| Entities | people, brands, objects | Talent/brand constraints and evidence checks |
| Actions | drinking, running, presenting | Intent matching and temporal verification |
| Media | duration, resolution, file size, MIME type | Filtering and delivery |
| Rights | territory, usage, expiry, licence state | Fail-safe review decisions |
| Engagement | views, likes, continuation rate | Research features, never relevance truth by default |

Missing evidence means “not verified,” not “verified absent.” In particular,
filenames and text metadata cannot prove that a logo, person, or action is
visually present.

## Adding richer annotations

The public catalog is intentionally small and in-memory. Authorized users can
extend `storage/video_catalog.py` to join their own JSON or database records,
provided they preserve:

1. a stable `video_id`;
2. a local playable path;
3. source and licence provenance;
4. a clear distinction between observed, predicted, and missing annotations;
5. dataset-specific engagement semantics.

## Publication and rights boundary

- Keep raw media, frames, audio, transcripts, OCR, embeddings, and indexes
  beneath ignored local directories.
- Do not redistribute third-party advertisements or creator videos without
  permission.
- Do not infer or publish sensitive personal attributes.
- Review the source licence and platform terms for every user-supplied asset.
- Run `python scripts/check_publish_safety.py` before every push.

The author's private dataset research and acquisition tooling remain local and
are intentionally not reproducible from this public repository.

