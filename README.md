<h1 align="center">Media Content Intelligence</h1>

<p align="center">
  Explainable media discovery through deterministic retrieval, typed agent orchestration, and evidence review.
</p>

<p align="center">
  <a href="#built-with"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.10 or newer"></a>
  <a href="#api-reference"><img src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&amp;logoColor=white" alt="FastAPI service"></a>
  <a href="#usage"><img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&amp;logoColor=white" alt="Streamlit interface"></a>
  <a href="#about-the-project"><img src="https://img.shields.io/badge/Status-Mock--first_reference-2563EB" alt="Status: mock-first reference application"></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-0D9488" alt="MIT license"></a>
</p>

<p align="center">
  <a href="#getting-started">Quick start</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#api-reference">API reference</a> ·
  <a href="#my-contribution">My contribution</a> ·
  <a href="#contact">Contact</a>
</p>

## Table of Contents

- [About the project](#about-the-project)
- [Key capabilities](#key-capabilities)
- [Product demonstration](#product-demonstration)
- [Architecture](#architecture)
- [Search and governance](#search-and-governance)
- [My contribution](#my-contribution)
- [Built with](#built-with)
- [Getting started](#getting-started)
- [Usage](#usage)
- [API reference](#api-reference)
- [Evaluation and reproducibility](#evaluation-and-reproducibility)
- [Roadmap](#roadmap)
- [Documentation](#documentation)
- [Contact](#contact)
- [License](#license)

## About the Project

Media teams need to find relevant footage across advertisements, sports, and
creator content while understanding its source and suitability for reuse.
A useful search result needs a clear explanation of the match and a clear
account of what the available evidence can support.

**Media Content Intelligence (MCI)** turns a natural-language request into
ranked, playable media results with metadata, provenance, and retrieval
explanations. It brings the search workflow into a FastAPI service and a
Streamlit workspace, with separate orchestration and evidence-validation roles.

> **Implementation status:** MCI is a runnable, mock-first reference application
> with deterministic ranking over a real media catalog.
> It does not yet run production multimodal inference.
> Datasets and pretrained models are not distributed; users supply media they are permitted to process.

## Key Capabilities

| Capability | What works today |
|---|---|
| Natural-language discovery | Query parsing and metadata search across titles, descriptions, and source labels; retains available annotations |
| Deterministic ranking | BM25-backed catalog scoring, metadata filters, stable ordering, and Reciprocal Rank Fusion (RRF) |
| Agent orchestration | A Media Orchestrator coordinates registered tools and sends a typed A2A task to an Evidence Validator |
| Evidence governance | Internal validation requests human review when supplied evidence fails required checks; visual and rights clearance are not inferred from a text match |
| Media inspection | Exact catalog asset previews, source links, annotation inspection, and relevance feedback in Streamlit |
| Observability | Response trace IDs, structured logs, request counters, latency metrics, and health endpoints |

## Product Demonstration

**Release publication is pending.** A recorded walkthrough is planned as a
GitHub Release asset. The application can be explored through the
[quick start](#getting-started) today. Restricted dataset videos will never be
included in Git or Release assets.

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>

## Architecture

![Media Intelligence Architecture: experience, orchestration, retrieval intelligence, evidence governance, and observability](docs/diagrams/rendered/media-intelligence-workflow.svg)

[Editable Excalidraw source](docs/diagrams/media-intelligence-workflow.excalidraw)

| Layer | Responsibility |
|---|---|
| Experience | FastAPI/OpenAPI contracts and the Streamlit search workspace |
| Orchestration | Intent and filter extraction, deterministic query variants, tool dispatch, and typed agent task/result exchange |
| Retrieval intelligence | In-memory catalog, metadata scoring, BM25 retrieval, and RRF ordering |
| Evidence governance | Evidence checks, output guards, and an internal human-review signal |
| Observability | Trace propagation, structured events, metrics, and feedback capture |

The application separates retrieval, orchestration, validation, and delivery
through explicit Python contracts. Both retrieval adapters currently use the
same BM25-backed catalog scorer; the `vector_search` name is an integration
contract for a future embedding index. Query rewrite and HyDE-style description
variants are generated deterministically and returned for inspection.

## Search and Governance

![Explainable Search Decision Flow: query, retrieval branches, rank fusion, evidence assessment, and human review](docs/diagrams/rendered/search-governance-flow.svg)

[Editable Excalidraw source](docs/diagrams/search-governance-flow.excalidraw)

1. **Media Orchestrator** extracts supported intent and filters, invokes
   `vector_search` and `bm25_search`, and combines their rankings with
   `rrf_fusion`.
2. **Evidence Validator** evaluates the supplied evidence bundle against
   requested talent, actions, brands, exclusions, and rights criteria. In the
   current search path, visual evidence is unavailable and rights are uncleared,
   so validation requires human review.

These agents are deterministic Python components communicating through typed
A2A task/result structures. The MCP-style registry is an internal tool
abstraction; it is not a networked MCP server or an autonomous LLM service.
Only the three retrieval tools above are registered.

Retrieval relevance, evidence confidence, and rights status have separate
meanings. A metadata match cannot verify a visible logo, a person, an action,
or permission to reuse footage. Validation currently remains in the
orchestrator result: the HTTP search schema exposes candidates and provenance,
but does not yet expose the validation or human-review fields. Its results
should therefore be reviewed before reuse.

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>

## My Contribution

**Prosenjit Banerjee — architecture, data-science design, and implementation.**

- **Designed the application architecture:** separated API/UI delivery,
  retrieval tools, orchestration, evidence validation, and observability into
  explicit contracts.
- **Implemented the retrieval workflow:** built media catalog discovery,
  query-sensitive BM25 metadata scoring, filtering, stable candidate identifiers,
  RRF fusion, and explanations tied to source records.
- **Built the agent coordination:** implemented the Media Orchestrator,
  Evidence Validator, typed A2A messages, query rewriting, and deterministic
  HyDE-style descriptions.
- **Defined the evidence and annotation model:** kept provenance and source
  annotations visible, separated relevance from verification, and made missing
  visual and rights evidence trigger review in the orchestrator.
- **Delivered the runnable application and engineering evidence:** implemented
  FastAPI routes, the Streamlit client, exact-asset preview serving, traceable
  metrics/logging, contract tests, documentation, and editable architecture visuals.

The production extension design applies VLM, computer-vision (CV), retrieval,
and agent-system knowledge to the same contracts. The following work is
**planned**, with its engineering decisions made explicit:

| Extension | Production design considerations |
|---|---|
| VLM and CV evidence | Align sampled frames, OCR/ASR, logo/object detection, and action evidence to source timecodes; preserve model/version provenance and distinguish predictions from reviewed observations |
| Multimodal retrieval | Add CLIP-style embeddings and a persistent vector index; evaluate lexical, dense, and fused retrieval on a labelled set with Recall@K and nDCG |
| Production agents | Add bounded model/tool calls, timeouts, retries, idempotent tasks, and trace propagation while retaining typed A2A contracts and review on insufficient evidence |
| Governance and evaluation | Calibrate evidence thresholds, measure false approvals, integrate authoritative rights records, and record reviewer decisions in a durable audit trail |

## Built With

| Area | Current technologies |
|---|---|
| Language and API | Python 3.10+, FastAPI, Uvicorn |
| User interface | Streamlit, HTTPX |
| Retrieval | `rank-bm25`, in-memory catalog, deterministic metadata scoring, RRF |
| Contracts and configuration | Pydantic v2, `pydantic-settings`, typed A2A messages, MCP-style tool registry |
| Observability | Structlog, Prometheus client, `X-Trace-ID` response headers |
| Verification and visuals | Pytest, pytest-asyncio, SVG, Excalidraw |

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>

## Getting Started

### Prerequisites

- Python **3.10 or newer**, Git, and a terminal.
- A few short videos you are permitted to process. MP4 or WebM is recommended
  for browser previews.
- Two terminal sessions for the API and interface. The commands below use Bash;
  activate `.venv` with the equivalent command on other shells.

### Install

```bash
git clone https://github.com/ModalityForge/Media-Content-Intelligence.git
cd Media-Content-Intelligence
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Add Smoke Media

```bash
mkdir -p data/raw/smoke
```

Copy your permitted videos into that directory before starting the API. For
example, a coffee video named `coffee-video.mp4` supports the query below.
Descriptive filenames provide the minimal text signals; they do not create
visual annotations. The catalog discovers MP4, WebM, OGG/OGV, MOV, MKV, and AVI
files, with preview support depending on browser codecs. Restart the API after
adding media to rebuild its in-memory catalog. See the
[data and annotation contract](docs/datasets.md) for richer catalog integration.

### Start the API

The API currently runs on localhost and will be **externally exposed soon**.
Authentication and deployment access controls are planned before public service
availability.

```bash
uvicorn app.main:app --reload
```

Local service links — the API will be externally exposed soon:

- API: <http://localhost:8000>
- Interactive OpenAPI documentation: <http://localhost:8000/docs>
- Prometheus metrics: <http://localhost:8000/metrics>

### Start the Interface

In a second terminal, from the project directory:

```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

Open <http://localhost:8501>. The UI calls the API at
`http://localhost:8000`, which will be externally exposed soon.

## Usage

In Streamlit, enter **coffee video**, choose a result limit, and select
**Search**. Inspect each result's relevance explanation, source information,
annotations, and preview. Submit thumbs-up/down feedback for a selected result.
The included UI examples describe intended search needs; they do not establish
that visual or rights evidence has been verified.

To query the localhost API directly — it will be externally exposed soon:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "coffee video", "max_results": 5}'
```

The JSON response includes `query`, `rewritten_query`, `hyde_query`,
`candidate_clips`, `total_found`, `trace_id`, and `processing_time_ms`.
Candidates retain available source metadata, annotations, and a
`relevance_reason`; scores represent retrieval relevance. An empty catalog or
unmatched query returns an empty candidate list. Review decisions remain
internal as described in [search and governance](#search-and-governance).

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>

## API Reference

Every endpoint below currently belongs to the localhost development API,
which will be **externally exposed soon**. Every HTTP response receives an
`X-Trace-ID` header. Interactive request/response schemas are available at
<http://localhost:8000/docs>.

| Method | Endpoint | Purpose / current output |
|---|---|---|
| `GET` | `/` | Service name, version, and runtime status |
| `GET` | `/health`, `/health/ready`, `/health/live` | Structured process health responses |
| `POST` | `/search` | Ranked candidates, query variants, provenance, trace ID, and latency |
| `GET` | `/search/suggestions?q=...` | Template-based query suggestions |
| `GET` | `/videos/` | Catalog records and preview availability |
| `GET` | `/videos/{video_id}` | Exact catalogued asset, with byte-range support; unknown assets return `404` |
| `POST` | `/feedback` | Record a relevance judgement and return an acknowledgement |
| `GET` | `/feedback` | Read feedback, optionally filtered by query or clip ID |
| `GET` | `/feedback/stats` | Aggregate thumbs-up/down counts |
| `GET` | `/metrics` | Prometheus metrics exposition |

Feedback is held in memory and resets with the API process. Health responses
are process probes; they do not certify model servers or external databases.

## Evaluation and Reproducibility

Run from the project root with the virtual environment active:

```bash
python -m pytest
python -m pytest tests/test_readme_documentation.py -q
python scripts/healthcheck.py
```

The health probe requires the running development API. Tests create temporary
synthetic catalog fixtures, so a fresh clone can check the application contract
without a dataset or pretrained model. These fixtures verify search, ranking,
agent transitions, API contracts, exact-asset serving, guards, traceability, and
documentation; they are not a video-quality or multimodal-accuracy benchmark.

For a smoke evaluation, use your permitted videos, try matching and unrelated
queries, verify that results point to the expected assets, and inspect source
annotations. A labelled set would support Precision@K, Recall@K, MRR, and nDCG;
no measured production retrieval or VLM benchmark is claimed here.

## Roadmap

- [x] Runnable FastAPI and Streamlit search application.
- [x] Deterministic catalog retrieval, RRF, typed agent coordination, and internal evidence review.
- [x] Trace IDs, structured logs, metrics, feedback, and public contract tests.
- [ ] Expose validation and human-review decisions consistently through the API and UI.
- [ ] Publish a recorded demonstration using permitted media as a GitHub Release asset.
- [ ] Add embedding-backed retrieval, VLM/CV evidence, OCR/ASR, and persistent indexing.
- [ ] Establish labelled retrieval/evidence evaluation and authoritative rights integration.
- [ ] Add authentication, deployment hardening, and external API access.

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>

## Documentation

| Guide | What to inspect |
|---|---|
| [Architecture](docs/architecture.md) | Runtime flow, agent roles, and production extension points |
| [Tool registry](docs/mcp_tools.md) | The three registered retrieval tools and their contracts |
| [Data and annotations](docs/datasets.md) | User-supplied media, provenance, and annotation semantics |
| [Evaluation](docs/evaluation.md) | Included checks and smoke-evaluation guidance |
| [Security](docs/security.md) | Runtime guards, evidence policy, and deployment requirements |
| [Project layout](docs/project-layout.md) | Application modules, entry points, and outputs |

## Contact

**Prosenjit Banerjee** — project author and principal designer/implementer.

[prosenjit.banerjee@gmail.com](mailto:prosenjit.banerjee@gmail.com) ·
[Project repository](https://github.com/ModalityForge/Media-Content-Intelligence)

## License

MIT, as declared in the [project metadata](pyproject.toml).

<p align="right"><a href="#media-content-intelligence">Back to top</a></p>
