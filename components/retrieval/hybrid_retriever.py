"""Hybrid retriever component."""

from typing import Any

from storage.video_catalog import catalog


class HybridRetriever:
    """Combine vector and BM25 retrieval."""

    def retrieve(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Execute hybrid retrieval."""
        return catalog.search(query, top_k=top_k)


hybrid_retriever = HybridRetriever()
