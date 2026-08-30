"""Retrieval MCP tools."""

import random
import uuid
from typing import Any

from tools.base import BaseMCPTool
from app.config import settings


class VectorSearchTool(BaseMCPTool):
    """Vector similarity search tool."""

    name = "vector_search"
    description = "Search for clips using vector embeddings"
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "top_k": {"type": "integer", "description": "Number of results", "default": 10},
            "filters": {"type": "object", "description": "Metadata filters"},
        },
        "required": ["query"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "results": {"type": "array"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute vector search."""
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 10)

        mock_results = [
            {
                "clip_id": f"clip-{uuid.uuid4().hex[:6]}",
                "video_id": f"video-{random.randint(1, 5):03d}",
                "score": round(random.uniform(0.7, 0.95), 3),
                "start_time": round(random.uniform(0, 300), 2),
                "end_time": round(random.uniform(30, 330), 2),
                "relevance_reason": f"Semantic match for '{query}'",
            }
            for _ in range(min(top_k, 5))
        ]

        return {"results": mock_results, "query": query, "retriever": "vector"}


class BM25SearchTool(BaseMCPTool):
    """BM25 text search tool."""

    name = "bm25_search"
    description = "Search using BM25 text retrieval"
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 10},
            "index_name": {"type": "string"},
        },
        "required": ["query"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute BM25 search."""
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 10)

        mock_results = [
            {
                "clip_id": f"clip-{uuid.uuid4().hex[:6]}",
                "video_id": f"video-{random.randint(1, 5):03d}",
                "score": round(random.uniform(0.6, 0.85), 3),
                "start_time": round(random.uniform(0, 300), 2),
                "end_time": round(random.uniform(30, 330), 2),
                "relevance_reason": f"BM25 text match for '{query}'",
            }
            for _ in range(min(top_k, 4))
        ]

        return {"results": mock_results, "query": query, "retriever": "bm25"}


class MetadataFilterTool(BaseMCPTool):
    """Metadata filtering tool."""

    name = "metadata_filter"
    description = "Filter clips by metadata"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "filters": {"type": "object"},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Filter by metadata."""
        clip_ids = input_data.get("clip_ids", [])
        filters = input_data.get("filters", {})

        return {
            "results": [
                {"clip_id": cid, "passed": True, "matched_filters": filters}
                for cid in clip_ids
            ],
            "filters_applied": filters,
        }


class RRFFusionTool(BaseMCPTool):
    """Reciprocal Rank Fusion tool."""

    name = "rrf_fusion"
    description = "Fuse results from multiple retrievers using RRF"
    input_schema = {
        "type": "object",
        "properties": {
            "result_sets": {"type": "array"},
            "k": {"type": "integer", "default": 60},
        },
        "required": ["result_sets"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute RRF fusion."""
        result_sets = input_data.get("result_sets", [])
        k = input_data.get("k", 60)

        rrf_scores: dict[str, float] = {}

        for result_set in result_sets:
            for rank, result in enumerate(result_set.get("results", []), 1):
                clip_id = result.get("clip_id", "")
                rrf_scores[clip_id] = rrf_scores.get(clip_id, 0) + 1 / (k + rank)

        sorted_clips = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        fused_results = [
            {"clip_id": cid, "rrf_score": round(score, 4)}
            for cid, score in sorted_clips[:10]
        ]

        return {"results": fused_results, "fusion_method": "rrf", "k": k}


class RerankResultsTool(BaseMCPTool):
    """Rerank search results."""

    name = "rerank_results"
    description = "Rerank retrieved clips for relevance"
    input_schema = {
        "type": "object",
        "properties": {
            "results": {"type": "array"},
            "query": {"type": "string"},
        },
        "required": ["results", "query"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Rerank results."""
        results = input_data.get("results", [])
        query = input_data.get("query", "")

        query_terms = set(query.lower().split())

        reranked = []
        for r in results:
            original_score = r.get("score", 0.5)
            text = r.get("relevance_reason", "").lower()
            boost = sum(1 for term in query_terms if term in text) * 0.05
            reranked.append({**r, "reranked_score": round(original_score + boost, 4)})

        reranked.sort(key=lambda x: x.get("reranked_score", 0), reverse=True)

        return {"results": reranked, "query": query, "reranker": "mock-reranker"}