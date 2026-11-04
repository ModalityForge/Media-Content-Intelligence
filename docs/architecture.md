# Media Content Intelligence Architecture

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

## Public architecture

MCI is a deterministic, agent-shaped media-search application. The public build
separates query orchestration, retrieval, evidence validation, and delivery so
each layer can later be replaced by a production implementation.

```text
Local user media
  -> VideoCatalog
  -> FastAPI / Streamlit query
  -> InputGuard
  -> MediaOrchestratorAgent
       -> QueryRewriter
       -> HyDEGenerator
       -> vector_search
       -> bm25_search
       -> rrf_fusion
  -> EvidenceValidatorAgent
  -> OutputGuard
  -> SearchResponse + trace + metrics
```

## Operative agents

### Media Orchestrator

Parses search intent, produces deterministic query variants, invokes the public
retrieval tools, fuses their rankings, and builds candidate records.

### Evidence Validator

Compares candidate annotations with requested talent, actions, brands,
exclusions, and rights conditions. Missing or ambiguous evidence produces a
human-review requirement.

The two roles communicate through typed A2A task/result data structures. They
are deterministic orchestration objects, not autonomous LLM processes.

## Registered tools

Only three tools are operative in the public registry:

- `vector_search`: lightweight semantic-style metadata scoring;
- `bm25_search`: lexical catalog scoring;
- `rrf_fusion`: deterministic reciprocal-rank fusion.

Vision, ASR, OCR, dense embeddings, durable databases, streaming, clipping, and
rights engines are production extension points rather than public
implementations.

## Safety and observability

The input guard rejects empty or known instruction-injection queries. The
output guard prevents restricted fields from crossing the API boundary. Each
response has a trace ID; structured logs and Prometheus counters expose runtime
behavior.

## Production extension path

The typed interfaces permit future integration of vision-language models,
CLIP-style embeddings, OCR/ASR, object tracking, persistent vector storage,
licence systems, and reviewer workflows. Those integrations must preserve the
fail-safe rule that unavailable evidence cannot become a positive assertion.

