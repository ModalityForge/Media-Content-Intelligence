# Project Layout, Entry Points, and Outputs

This document maps the repository as it is implemented. “Output” means either an HTTP response, a generated artifact, or a process exit status.

## Repository layout

```text
media-content-intelligence-mci-v2/
├── app/
│   ├── main.py                 FastAPI application and process entry point
│   ├── config.py               Environment-backed settings
│   ├── schemas.py              API request/response contracts
│   └── models.py               Internal media domain models
├── api/
│   ├── middleware/             Authentication, rate limits, request context
│   └── routes/                 Health, ingest, search, clips, alerts, feedback
├── agents/
│   ├── media_orchestrator.py   Main query-planning and tool-dispatch agent
│   ├── evidence_validator.py   Candidate-evidence validation agent
│   ├── a2a_protocol.py         Orchestrator-to-validator task boundary
│   ├── graph.py                Lightweight sequential orchestration graph
│   └── state.py                Shared execution state
├── tools/                      MCP-style tool registry and tool bundles
├── services/                   RAG, policy, safety, alert and feedback services
├── components/
│   ├── ingestion/              Video/stream/metadata loading and job registry
│   ├── preprocessing/          Scenes, frames, audio, OCR, transcripts
│   ├── indexing/               Text/visual embeddings, captions and metadata
│   ├── retrieval/              Vector/BM25 search, RRF, reranking, rights filter
│   ├── vision/                 Detection, segmentation, tracking and pose
│   └── clipping/               Clip, thumbnail and export helpers
├── storage/                    Object, metadata, vector and Redis adapters
├── security/                   Guards, PII/content filters and audit logging
├── streaming/                  Kafka/Flink/live-window integration points
├── observability/              Logs, traces, metrics and cost tracking
├── frontend/                   Streamlit application and review pages
├── prompts/                    Agent and policy prompt templates
├── evaluation/                 Golden fixture and evaluator modules
├── scripts/                    Dataset and operational command-line entries
├── docs/                       Project and subsystem documentation
├── tests/                      Pytest suite
└── data/                       Local-only source and generated data
```

## Runtime flow

```text
Client or Streamlit
  -> FastAPI route
  -> MediaOrchestratorAgent
  -> query rewrite + HyDE + tool plan
  -> MCP tool registry
  -> retrieval / vision / policy tools
  -> EvidenceValidatorAgent over A2A boundary
  -> output guardrails
  -> SearchResponse JSON
```

The default tool/model implementations are lightweight or mocked. The repository demonstrates contracts and orchestration; it does not yet run the complete ingestion/indexing stack against the downloaded datasets automatically.

## Service entry and exit points

| Entry | Invocation | Successful exit/output |
|---|---|---|
| API process | `uvicorn app.main:app --reload` or `python -m app.main` | HTTP service on port 8000 |
| Frontend process | `streamlit run frontend/app.py` | Streamlit UI on port 8501; API base defaults to `http://localhost:8000` |
| Container stack | `docker compose up --build` | API plus Redis; local `data/` and `logs/` mounts |
| Root API | `GET /` | Service name, version and running status |
| Health APIs | `GET /health`, `/health/ready`, `/health/live` | `HealthResponse` JSON |
| Search API | `POST /search` | Rewritten query, HyDE text, candidate clips, trace ID and latency |
| Suggestions API | `GET /search/suggestions?q=...` | Suggested query strings |
| Ingest API | `POST /ingest/video` | Queued job identifier; background processing is currently a placeholder |
| Ingest job APIs | `GET` or `DELETE /ingest/job/{job_id}` | Mock job status or cancellation response |
| Clip APIs | `/clips/export`, `/clips/{clip_id}` | Export/status metadata; current implementation is mock-first |
| Alert APIs | `/alerts` | In-memory alert records |
| Feedback APIs | `/feedback` | In-memory feedback records and statistics |
| Metrics API | `GET /metrics` | Prometheus text exposition |

Every API response receives an `X-Trace-ID` header from `app/main.py` middleware.

## Command-line entry and exit points

| Script | Purpose | Output / exit behavior |
|---|---|---|
| `scripts/download_ad_datasets.py` | Build a capped advertisement-media subset | Dataset files, manifest/catalog and exit `0`; validation/configuration errors return non-zero |
| `scripts/download_socmed_dataset.py` | Build capped MicroLens/SnapUGC subsets | `data/restricted/social_media_influencer/`, catalogs and joined CSVs; exit `0`, `2` for bad arguments, `130` on interruption |
| `scripts/create_golden_dataset.py` | Regenerate evaluation fixture | Writes `evaluation/golden_dataset.json` |
| `scripts/healthcheck.py` | Test API health | Exit `0` when healthy, `1` on failure |
| `scripts/index_archive.py` | Archive-indexing integration point | Prints mock completion; currently not a production indexer |
| `scripts/run_live_stream.py` | Live-stream integration point | Prints mock completion; currently not a stream processor |
| `scripts/seed.py` | Seed-development integration point | Prints sample records; no persistent database write yet |
| `scripts/migrate.py` | Migration integration point | Prints placeholder result; no migration framework wired yet |

## Generated-data exits

```text
data/
├── raw/                         Source media; advertisement subset lives here
├── restricted/                  Research-only/non-redistributable media
├── processed/                   Normalized media and metadata
├── frames/                      Extracted frames
├── audio/                       Extracted audio
├── transcripts/                 ASR output
├── ocr/                         OCR output
├── captions/                    Generated captions
└── indexes/                     Retrieval indexes and embeddings
```

All generated-data directories are ignored by Git. Only downloader code, schemas, and documentation belong in the repository.

## Configuration boundary

Settings are loaded by `app/config.py` from environment variables and an optional local `.env`. Important variables include `OPENAI_API_KEY`, `VECTOR_DB_URL`, `METADATA_DB_URL`, `REDIS_URL`, `OBJECT_STORE_PATH`, `ENABLE_MOCK_MODELS`, and `LOG_LEVEL`. Never commit `.env` or credentials.
