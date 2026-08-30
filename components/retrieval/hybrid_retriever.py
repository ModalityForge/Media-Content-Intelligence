"""Hybrid retriever component."""

from typing import Any


class HybridRetriever:
    """Combine vector and BM25 retrieval."""

    def retrieve(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Execute hybrid retrieval."""
        return []


hybrid_retriever = HybridRetriever()