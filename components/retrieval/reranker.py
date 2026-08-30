"""Reranker component."""

from typing import Any


class Reranker:
    """Rerank search results."""

    def rerank(self, results: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        """Rerank results."""
        return results


reranker = Reranker()