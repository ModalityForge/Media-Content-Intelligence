# Media Content Intelligence

Media Content Intelligence (MCI) is a rights-aware platform for finding,
reviewing, and governing advertisement, social-video, broadcast, OTT, and
sports-media assets. A user describes the people, brands, actions, duration,
territory, or usage constraints they need; MCI returns ranked source assets
with provenance, annotations, and an explicit review decision.

> **Current status:** this repository is a runnable, mock-first reference implementation.
> Its FastAPI service, Streamlit interface, deterministic
> metadata search, agent orchestration, validation, and local dataset tooling
> work today. It does not yet run production multimodal inference; ingestion
> workers, persistent databases, live-stream processing, and heavyweight ML
> models remain extension points.

[Project layout](docs/project-layout.md) ·
[Dataset and annotation guide](docs/datasets.md) ·
[Architecture](docs/architecture.md) ·
[Security](docs/security.md) ·
[Evaluation](docs/evaluation.md)

## What MCI delivers

- **Explainable media discovery:** ranked results point to exact local assets
  and retain titles, descriptions, dataset names, annotations, and source URLs.
- **Compound search intent:** requests can combine talent, actions, brands,
  exclusions, duration, territory, and intended usage.
- **Governed decisions:** missing visual or rights evidence fails safely and is
  routed to human review rather than silently approved.
- **Reproducible data acquisition:** capped downloaders build compact local
  advertisement, MicroLens, and SnapUGC subsets without publishing the media.
- **Operational visibility:** trace IDs, structured logs, health endpoints,
  feedback capture, and Prometheus metrics expose the runtime path.

## How media becomes a governed result

The workflow separates source acquisition, retrieval, evidence checks, and
delivery. That boundary matters: relevance identifies a candidate, while
evidence and rights determine whether it is safe to use.

![End-to-end Media Content Intelligence workflow](docs/diagrams/rendered/media-intelligence-workflow.svg)

[Editable Excalidraw source](docs/diagrams/media-intelligence-workflow.excalidraw)

The current retrieval path builds a real searchable catalog from local media
and uses deterministic metadata/BM25 scoring with Reciprocal Rank Fusion. The
vision, ASR, OCR, tracking, captioning, and dense-vector interfaces define the
next production layer; their default implementations are intentionally mocked
and do not influence which videos are returned by the primary search path.

## Search, evidence, and review

MCI uses two operative agent roles rather than many micro-agents:

- The **Media Orchestrator** parses the request, rewrites it, generates HyDE
  text, runs retrieval tools, fuses results, and builds the response.
- The **Evidence Validator** checks requested talent, actions, brands,
  exclusions, and rights, then decides whether human review is required.

Detection, transcription, retrieval, rights, and export capabilities remain
narrow MCP-style tools. They do not independently plan or make policy.

![Search, validation, governance, and human-review flow](docs/diagrams/rendered/search-governance-flow.svg)

[Editable Excalidraw source](docs/diagrams/search-governance-flow.excalidraw)

This fail-safe flow distinguishes “not verified” from “verified absent.” A
missing logo prediction, talent match, or licence record is never converted
into a positive assertion.

## Product demonstrations

These original product walkthroughs demonstrate the work completed in this
repository. They contain the MCI interface and synthetic/API presentation
material only—no downloaded advertisement or restricted social-media footage.
The MP4 files are hosted as GitHub Release assets so media binaries do not enter
the source history.

| Walkthrough | What it shows |
|---|---|
| [▶ Watch the search experience](https://github.com/ModalityForge/Media-Content-Intelligence/releases/download/demo-assets-v1/mci-search-demo.mp4) | Query interpretation, hybrid retrieval, ranked asset metadata, and explainable relevance. |
| [▶ Watch API governance and review](https://github.com/ModalityForge/Media-Content-Intelligence/releases/download/demo-assets-v1/mci-api-governance-demo.mp4) | Local API surface, deterministic evidence validation, rights handling, traceability, and human review. |

Restricted dataset videos and pretrained model artifacts are never included in
Git or Release assets.

## Run locally

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the API

> **API availability:** the API currently runs on localhost only and will be
> externally exposed soon. No public production endpoint is available yet.

```bash
uvicorn app.main:app --reload
```

- Local API: <http://localhost:8000>
- Local interactive documentation: <http://localhost:8000/docs>
- Local metrics: <http://localhost:8000/metrics>

These localhost interfaces are for development; the API will be externally
exposed soon with deployment, authentication, and access controls.

### 3. Start the interface

> **API dependency:** the Streamlit application currently calls the localhost
> API, which will be externally exposed soon.

```bash
streamlit run frontend/app.py
```

Open the local interface at <http://localhost:8501>. It expects the development
API at `http://localhost:8000`; that API will be externally exposed soon.

### 4. Search through the API

> **API availability:** this example calls the localhost development API. The
> same API will be externally exposed soon after the production access layer is
> available.

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Find coffee commercials", "max_results": 5}'
```

A successful response contains the original query, rewritten and HyDE forms,
ranked candidate assets, provenance, annotations, trace ID, and processing
latency.

## Local API surface

> **API availability:** every endpoint below currently belongs to the localhost
> development service and will be externally exposed soon. Production exposure
> will add authentication, deployment hardening, and explicit access policy.

| Endpoint | Purpose | Current output |
|---|---|---|
| `GET /` | Service identity | Name, version, and runtime status |
| `GET /health`, `/health/ready`, `/health/live` | Runtime health | Structured health response |
| `POST /search` | Media discovery | Ranked candidates, trace ID, and latency |
| `GET /search/suggestions` | Query assistance | Suggested search phrases |
| `GET /videos/{video_id}` | Exact local media | Streamed authorized local asset |
| `POST /ingest/video` | Ingestion boundary | Queued job metadata; worker is currently a placeholder |
| `/clips/*` | Clip operations | Mock-first clip/export metadata |
| `/alerts`, `/feedback` | Review signals | In-memory prototype records |
| `GET /metrics` | Observability | Prometheus exposition |

Every HTTP response receives an `X-Trace-ID` header. See
[project-layout.md](docs/project-layout.md) for all entry and exit points.

## Datasets and annotations

The local workspace is designed around compact, task-relevant subsets:

| Collection | Available annotations | Intended use |
|---|---|---|
| Advertisement subset | Source manifests and asset metadata | Creative search, OCR, logo, and ad-content experiments |
| MicroLens-50K subset | Titles, likes, views, provenance, hashes | Retrieval and popularity-feature research |
| SnapUGC subset | ECR, split, sparse title/description, provenance, hashes | Opening-hook and short-video retention modelling |

The downloaders prepare local media and joined manifests; they do not yet
automatically populate a production vector database. Engagement values are
metadata features, not relevance ground truth: MicroLens likes/views and
SnapUGC ECR represent different outcomes and must not be treated as the same
label.

```bash
# Advertisement subset options
python scripts/download_ad_datasets.py --help

# Research-only social-video subset options
python scripts/download_socmed_dataset.py --help
```

All downloaded media, generated catalogs, annotations, derived frames, model
weights, checkpoints, and embeddings remain local and are excluded from Git.
Review each publisher's terms before downloading or using source media.

## Entry points

| Entry point | Command | Output |
|---|---|---|
| FastAPI service | `uvicorn app.main:app --reload` | Local JSON API, OpenAPI, and metrics; external exposure is coming soon |
| Streamlit UI | `streamlit run frontend/app.py` | Local browser interface backed by the localhost API; the API will be externally exposed soon |
| Docker stack | `docker compose up --build` | API container, Redis, and local data/log mounts |
| Advertisement downloader | `python scripts/download_ad_datasets.py --help` | Capped local ad subset and catalog |
| Social-video downloader | `python scripts/download_socmed_dataset.py --help` | Research-only MicroLens/SnapUGC subset and annotations |
| Health probe | `python scripts/healthcheck.py` | Exit `0` when the local API is healthy; external API exposure is coming soon |

## Test and publish safely

```bash
pytest
python scripts/check_publish_safety.py
```

The versioned pre-push hook rejects tracked datasets, media, archives, model
weights, checkpoints, embeddings, and files larger than 10 MiB. Enable it in a
fresh clone with:

```bash
git config core.hooksPath .githooks
```

## Production extension path

The current interfaces are ready to be connected to production components:

- **Vision:** Grounding DINO, SAM2, ByteTrack, DeepSORT, MMPose
- **Audio and text:** Whisper/faster-whisper, OCR, multimodal captioning
- **Embeddings:** CLIP or video-language representations
- **Retrieval:** Qdrant, ChromaDB, or another persistent vector store
- **Data platform:** durable metadata DB, object storage, migrations, workers
- **LLM services:** governed query rewriting and response composition
- **Review operations:** persistent queue, reviewer identity, decisions, audit

## Project structure

```text
Media-Content-Intelligence/
├── app/              FastAPI assembly, configuration, schemas
├── api/              HTTP routes and middleware
├── agents/           Orchestrator, validator, state, A2A boundary
├── tools/            Retrieval, vision, audio, policy, output contracts
├── services/         RAG, rights, safety, alerts, feedback, cache
├── components/       Ingestion, preprocessing, indexing, vision, clipping
├── storage/          Catalog and persistence adapters
├── security/         Input/output guards, filters, audit logging
├── observability/    Logging, tracing, metrics, cost tracking
├── evaluation/       Offline and online evaluation modules
├── frontend/         Streamlit search and review interface
├── scripts/          Dataset and operational command-line tools
├── docs/             Architecture, diagrams, datasets, security, evaluation
├── tests/            Automated test suite
└── data/             Local-only raw, derived, indexed, restricted assets
```

## License

MIT
