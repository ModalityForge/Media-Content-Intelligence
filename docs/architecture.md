# MCI-v2.0 Architecture

## Overview

MCI-v2.0 (Media Content Intelligence) is an agentic platform for semantic video retrieval, rights-aware search, brand safety, and clip review.

## Architecture Principles

1. **Simplified Agentic Architecture**: One Media Orchestrator Agent, One Evidence Validator Agent
2. **MCP-Style Tools**: Tool bundles for retrieval, vision, audio/OCR, rights/policy, output/clipping
3. **Selective A2A**: Only between real agents (Media Orchestrator -> Evidence Validator)
4. **No Micro-Agents**: Logo, talent, action, rights, sponsorship detection are MCP tools, not separate agents

## System Flow

```
Video Archive / Live Streams
    -> Ingestion & Indexing Pipeline
    -> Vector DB / Metadata DB
    -> User Query
    -> Media Orchestrator Agent
    -> MCP Tool Bundles
    -> Evidence Validator Agent
    -> Guardrails
    -> HITL Review (if low confidence)
    -> AgentOps Observability
```

## Core Components

### Agents

1. **Media Orchestrator Agent**
   - Parses compound user queries
   - Rewrites queries for better retrieval
   - Generates HyDE (Hypothetical Document Embeddings)
   - Plans and dispatches tool calls
   - Composes final answer

2. **Evidence Validator Agent**
   - Validates evidence for each candidate clip
   - Checks compound conditions (talent, action, brands, rights)
   - Determines human review requirements

### MCP Tool Bundles

- **Retrieval Tools**: Vector search, BM25, RRF fusion, reranking
- **Vision Tools**: Object detection, logo detection, talent matching, action classification, tracking, pose estimation
- **Audio/OCR Tools**: ASR, OCR, caption generation
- **Policy Tools**: Rights check, sponsorship policy, exclusion check, content rating
- **Output Tools**: Clip generation, face blur, export, alerts

### Guardrails

- Input guard: Prompt injection detection
- Output guard: PII/restricted field filtering
- Brand safety: Prohibited/excluded brand detection
- Rights: Territory/usage/duration enforcement

## Extension Points

To add real models:

1. **Vision**: Replace mock wrappers with Grounding DINO, SAM2, ByteTrack, DeepSORT, MMPose
2. **Audio**: Replace mock with Whisper, faster-whisper
3. **Embedding**: Replace mock with CLIP, Video-LLaVA
4. **Vector DB**: Add Qdrant, ChromaDB clients

## LangGraph Integration

The current graph is lightweight Python. To upgrade:

```python
# from langgraph.graph import StateGraph
# graph = StateGraph(MCIState)
# graph.add_node("parse_query", parse_query_node)
# ...
```