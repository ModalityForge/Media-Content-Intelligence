# Public Project Layout, Entry Points, and Outputs

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

This document describes the files present in a fresh public clone. The author's
extended research implementation is intentionally local-only and is not part of
this contract.

## Tracked runtime layout

```text
Media-Content-Intelligence/
├── app/                       FastAPI assembly, settings, schemas, dependencies
├── api/routes/                Health, search, video, and feedback routes
├── agents/                    Orchestrator, validator, shared state, A2A messages
├── tools/                     Retrieval contracts, implementations, registry
├── services/                  Query rewriting and HyDE text generation
├── storage/video_catalog.py   Local media discovery and deterministic search
├── security/                  Input and output boundary guards
├── observability/             Structured logging and Prometheus metrics
├── frontend/app.py            Streamlit application
├── scripts/                   Health probe and publication-safety check
├── docs/                      Public architecture and operating documentation
└── tests/                     Focused public-runtime contract tests
```

## Runtime flow

```text
User or Streamlit
  -> FastAPI route
  -> input guard
  -> MediaOrchestratorAgent
  -> query rewrite + HyDE
  -> vector_search + bm25_search
  -> rrf_fusion
  -> EvidenceValidatorAgent
  -> output guard
  -> SearchResponse JSON
```

The public retrieval path is deterministic and operates on the in-memory
catalog built from ignored local media. The “vector” tool is a lightweight
metadata scorer in this edition; it is an integration boundary for a future
embedding-backed index.

## Service entries and exits

All APIs currently run on localhost and will be externally exposed soon after
authentication and deployment controls are added.

| Entry | Invocation | Successful output |
|---|---|---|
| API process | `uvicorn app.main:app --reload` | HTTP service on localhost port 8000 |
| Frontend process | `streamlit run frontend/app.py` | UI on localhost port 8501 |
| Root API | `GET /` | Service identity and status |
| Health APIs | `GET /health`, `/health/ready`, `/health/live` | Structured health JSON |
| Search API | `POST /search` | Query variants, candidates, validation, trace ID, latency |
| Suggestions API | `GET /search/suggestions?q=...` | Suggested query strings |
| Video API | `GET /videos/{video_id}` | Exact authorized local asset |
| Feedback API | `POST /feedback` | In-memory acknowledgement |
| Metrics API | `GET /metrics` | Prometheus text exposition |

Every response receives an `X-Trace-ID` header from `app/main.py`.

## Command-line entries and exits

| Script | Purpose | Exit behavior |
|---|---|---|
| `scripts/healthcheck.py` | Probe the localhost health endpoint | `0` when healthy, `1` on failure |
| `scripts/check_publish_safety.py` | Inspect Git-tracked paths | `0` only for an approved code/documentation surface |

## Local data boundary

The application scans `data/` for user-supplied media. The entire directory is
ignored. A typical smoke-test layout is:

```text
data/
└── raw/
    └── smoke/
        ├── coffee-commercial.mp4
        └── sports-highlight.webm
```

No media, annotation export, model, embedding, archive, or generated catalog is
tracked.

## Local-only implementation

The working tree may contain ignored acquisition, ingestion, preprocessing,
vision, streaming, evaluation, and persistence code. Those files are not
required to run this public application, are absent from a clone, and are
rejected by the publication-safety check if accidentally staged.

`CLAUDE.md` is explicitly local-only and is not part of the public project.

## Configuration boundary

`app/config.py` reads environment variables and an optional ignored `.env`.
Use `.env.example` as the non-secret template. Never commit credentials.

