"""BM25 retriever component."""

from typing import Any

from storage.video_catalog import catalog


class BM25Retriever:
    """BM25 text retrieval."""

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search with BM25."""
        return catalog.search(query, top_k=top_k)


bm25_retriever = BM25Retriever()
