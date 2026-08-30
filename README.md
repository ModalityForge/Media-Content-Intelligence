# MCI-v2.0: Media Content Intelligence Platform

MCI-v2.0 is an agentic platform for semantic video retrieval, rights-aware search, brand safety enforcement, and clip review for broadcast, OTT, and sports media.

> **Implementation status:** this repository is a runnable, mock-first reference implementation. The FastAPI and Streamlit entry points work, while ingestion workers, live-stream processing, database migrations, and heavyweight ML integrations are extension points or placeholders.

Detailed project maps:

- [Folder structure, entry points, and outputs](docs/project-layout.md)
- [Dataset inventory, annotations, and usage](docs/datasets.md)
- [Architecture](docs/architecture.md)

## Why MCI-v2.0?

MCI-v2.0 uses a simplified agentic architecture:

- **One Media Orchestrator Agent**: Central coordinator that parses queries, rewrites for retrieval, generates HyDE embeddings, dispatches tools, and composes answers
- **One Evidence Validator Agent**: Validates that candidate clips meet all requirements (talent, action, brands, rights)
- **MCP-Style Tool Bundles**: Retrieval, vision, audio/OCR, policy, and output tools as unified interfaces
- **Selective A2A**: Only between real agents (Orchestrator → Validator), not for every small capability
- **No Micro-Agents**: Logo detection, talent matching, action classification, rights checking are tools, not separate agents

## Architecture

```
Video Archive / Live Streams
    -> Ingestion & Indexing Pipeline
    -> Vector DB / Metadata DB
    -> User Query
    -> Media Orchestrator Agent
       -> MCP Tool Bundles (retrieval, vision, audio, policy, output)
    -> Evidence Validator Agent
    -> Guardrails (input, output, brand safety, rights)
    -> HITL Review (if low confidence)
    -> AgentOps Observability
```

## Features

- Semantic video search with hybrid retrieval (vector + BM25 + RRF)
- Rights-aware filtering by territory, usage type, and duration
- Brand safety enforcement (prohibited/excluded brands)
- Compound query understanding (talent + action + brands + rights)
- HyDE (Hypothetical Document Embeddings) for better retrieval
- Evidence validation with confidence scoring
- Human-in-the-loop review for low-confidence results
- Prometheus metrics and structured logging

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload
```

API available at: http://localhost:8000

Interactive API documentation is available at http://localhost:8000/docs.

## Running the Frontend

```bash
streamlit run frontend/app.py
```

Frontend available at: http://localhost:8501

## Testing

```bash
pytest
```

## Primary Entry Points and Outputs

| Entry point | Command | Primary output / exit |
|---|---|---|
| FastAPI service | `uvicorn app.main:app --reload` | JSON APIs on `:8000`, OpenAPI docs, Prometheus `/metrics` |
| Streamlit UI | `streamlit run frontend/app.py` | Browser UI on `:8501`; calls the FastAPI service |
| Docker stack | `docker compose up --build` | API container, Redis, mounted `data/` and `logs/` |
| Advertisement subset | `python scripts/download_ad_datasets.py --help` | `data/raw/ad_subset/` by default/configuration |
| Social-video subset | `python scripts/download_socmed_dataset.py --help` | `data/restricted/social_media_influencer/` |
| Evaluation fixture | `python scripts/create_golden_dataset.py` | `evaluation/golden_dataset.json` |
| Health check | `python scripts/healthcheck.py` | Process exit `0` when healthy, `1` otherwise |

See [docs/project-layout.md](docs/project-layout.md) for every CLI and API boundary.

## Local Datasets

Dataset media and generated annotations are deliberately excluded from Git. The current local workspace contains:

- An advertisement subset in `data/raw/ad_subset/`.
- 100 MicroLens-50K videos with likes, views, and titles.
- 30 SnapUGC videos with ECR labels and available title/description metadata.
- A combined social-video footprint of approximately 331 MB, kept under `data/restricted/` because of research-use and redistribution restrictions.

The generated catalogs and media remain local. A GitHub clone contains the downloader code and documentation, not the restricted videos. See [docs/datasets.md](docs/datasets.md) for schemas, commands, and licensing boundaries.

Before publishing, run:

```bash
python scripts/check_publish_safety.py
```

The repository’s versioned pre-push hook runs the same check and rejects tracked datasets, media, archives, model weights, checkpoints, embeddings, and files larger than 10 MiB. Enable it in a fresh clone with `git config core.hooksPath .githooks`.

## Example Query

```
Find 30-second clips where Messi is drinking from a Pepsi bottle, Adidas logo is visible, Nike is not visible, and the clip is cleared for Germany digital highlights.
```

## Example API Call

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Find Messi drinking Pepsi", "max_results": 5}'
```

## Extension Points

To add real AI models, uncomment in `requirements.txt`:

- **Vision**: Grounding DINO, SAM2, ByteTrack, DeepSORT, MMPose
- **Audio**: Whisper, faster-whisper
- **Embedding**: CLIP, Video-LLaVA
- **Vector DB**: Qdrant, ChromaDB
- **LLM**: OpenAI (for query rewriting, answer composition)

## Project Structure

```
media-content-intelligence-mci-v2/
├── app/              # FastAPI assembly, settings, schemas, domain models
├── api/              # HTTP routes and middleware
├── agents/           # Orchestrator, evidence validator, state, A2A protocol
├── tools/            # MCP-style retrieval/vision/audio/policy/output tools
├── services/         # RAG, rights, brand-safety, alerts, feedback, cache
├── components/       # Ingestion, preprocessing, indexing, retrieval, clipping
├── storage/          # Object, vector, metadata, and Redis adapters
├── security/         # Input/output guards, PII/content filters, audit logging
├── streaming/        # Kafka/Flink/live-window integration points
├── observability/    # Logging, tracing, metrics, and cost tracking
├── evaluation/       # Golden fixture and offline/online evaluators
├── frontend/         # Streamlit application and review pages
├── prompts/          # Agent and policy prompt templates
├── scripts/          # Downloaders and operational CLIs
├── docs/             # Architecture, datasets, security, tools, evaluations
├── tests/            # Pytest test suite
└── data/             # Local-only raw, derived, indexed, and restricted data
```

## License

MIT
