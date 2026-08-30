"""RAG pipeline service."""

from typing import Any

from services.query_rewriter import rewrite_query, extract_filters
from services.hyde_generator import generate_hyde
from tools.mcp_registry import get_registry
from observability.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Retrieval Augmented Generation pipeline."""

    def __init__(self):
        self.tool_registry = get_registry()

    def retrieve(self, query: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute retrieval."""
        filters = filters or {}

        rewritten = rewrite_query(query)
        hyde = generate_hyde(query)

        vector_result = self.tool_registry.run_tool(
            "vector_search",
            {"query": hyde, "top_k": 20, "filters": filters},
        )

        bm25_result = self.tool_registry.run_tool(
            "bm25_search",
            {"query": rewritten, "top_k": 20},
        )

        rrf_result = self.tool_registry.run_tool(
            "rrf_fusion",
            {
                "result_sets": [
                    vector_result,
                    bm25_result,
                ],
                "k": 60,
            },
        )

        fused = rrf_result.get("results", [])

        reranked_result = self.tool_registry.run_tool(
            "rerank_results",
            {"results": fused, "query": query},
        )

        return reranked_result.get("results", [])

    def retrieve_with_filters(
        self,
        query: str,
        max_duration: int | None = None,
        territory: str | None = None,
        brands_required: list[str] | None = None,
        brands_excluded: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve with specific filters."""
        filters = {}
        if max_duration:
            filters["max_duration"] = max_duration
        if territory:
            filters["territory"] = territory

        results = self.retrieve(query, filters)

        if brands_required or brands_excluded:
            filtered_results = []
            for r in results:
                clip_id = r.get("clip_id", "")
                logo_result = self.tool_registry.run_tool(
                    "logo_detection",
                    {
                        "clip_ids": [clip_id],
                        "target_brands": (brands_required or []) + (brands_excluded or []),
                    },
                )
                detections = logo_result.get("detections", [])
                detected_brands = [d.get("brand", "") for d in detections]

                if brands_required:
                    if not any(b in detected_brands for b in brands_required):
                        continue

                if brands_excluded:
                    if any(b in detected_brands for b in brands_excluded):
                        continue

                filtered_results.append(r)

            results = filtered_results

        return results


def run_rag_query(
    query: str,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a RAG query."""
    pipeline = RAGPipeline()

    rewritten = rewrite_query(query)
    hyde = generate_hyde(query)

    results = pipeline.retrieve(query, filters)

    return {
        "query": query,
        "rewritten_query": rewritten,
        "hyde_query": hyde,
        "results": results,
        "total": len(results),
    }