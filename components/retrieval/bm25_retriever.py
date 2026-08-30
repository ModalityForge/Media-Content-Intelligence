"""BM25 retriever component."""

from typing import Any


class BM25Retriever:
    """BM25 text retrieval."""

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search with BM25."""
        return []


bm25_retriever = BM25Retriever()