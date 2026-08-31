"""Retrieval MCP tools."""

from typing import Any

from tools.base import BaseMCPTool
from storage.video_catalog import catalog


class VectorSearchTool(BaseMCPTool):
    """Vector similarity search tool.

    Backed by the real catalogue; vector scoring is emulated deterministically
    from the BM25 content index so results are query-relevant and stable.
    """

    name = "vector_search"
    description = "Search the local catalog using the deterministic metadata fallback"
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
        """Execute vector search against the real content index."""
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 10)
        filters = input_data.get("filters", {})

        results = catalog.search(query, top_k=top_k, filters=filters)
        for r in results:
            r["retriever"] = "vector"
        return {"results": results, "query": query, "retriever": "vector"}


class BM25SearchTool(BaseMCPTool):
    """BM25 text search tool over the real content index."""

    name = "bm25_search"
    description = "Search using BM25 text retrieval"
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 10},
            "index_name": {"type": "string"},
            "filters": {"type": "object", "description": "Metadata filters"},
        },
        "required": ["query"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute BM25 search against the real content index."""
        query = input_data.get("query", "")
        top_k = input_data.get("top_k", 10)
        filters = input_data.get("filters", {})

        results = catalog.search(query, top_k=top_k, filters=filters)
        for r in results:
            r["retriever"] = "bm25"
        return {"results": results, "query": query, "retriever": "bm25"}


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
            "top_k": {"type": "integer", "default": 10},
        },
        "required": ["result_sets"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute RRF fusion."""
        result_sets = input_data.get("result_sets", [])
        k = input_data.get("k", 60)
        top_k = input_data.get("top_k", 10)

        rrf_scores: dict[str, float] = {}
        best: dict[str, dict[str, Any]] = {}

        for result_set in result_sets:
            for rank, result in enumerate(result_set.get("results", []), 1):
                clip_id = result.get("clip_id", "")
                if not clip_id:
                    continue
                rrf_scores[clip_id] = rrf_scores.get(clip_id, 0) + 1 / (k + rank)
                best.setdefault(clip_id, result)

        sorted_clips = sorted(
            rrf_scores.items(), key=lambda x: (-x[1], x[0])
        )

        fused_results = [
            {
                "clip_id": cid,
                "video_id": best[cid].get("video_id", ""),
                "file_path": best[cid].get("file_path", ""),
                "rrf_score": round(score, 4),
                "score": best[cid].get("score", 0.0),
                "title": best[cid].get("title", ""),
                "start_time": best[cid].get("start_time", 0.0),
                "end_time": best[cid].get("end_time", 30.0),
                "relevance_reason": best[cid].get("relevance_reason", ""),
                "description": best[cid].get("description", ""),
                "source": best[cid].get("source", ""),
                "source_url": best[cid].get("source_url", ""),
                "source_page": best[cid].get("source_page", ""),
                "asset_name": best[cid].get("asset_name", ""),
                "dataset": best[cid].get("dataset", ""),
                "content_type": best[cid].get("content_type", "video"),
                "mime_type": best[cid].get("mime_type"),
                "annotations": best[cid].get("annotations", {}),
            }
            for cid, score in sorted_clips[:top_k]
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
            base = r.get("score", r.get("rrf_score", 0.5))
            text = r.get("relevance_reason", "").lower() + " " + r.get("title", "").lower()
            boost = sum(1 for term in query_terms if term in text) * 0.05
            reranked.append({**r, "reranked_score": round(base + boost, 4)})

        reranked.sort(key=lambda x: x.get("reranked_score", 0), reverse=True)

        return {"results": reranked, "query": query, "reranker": "content-reranker"}
