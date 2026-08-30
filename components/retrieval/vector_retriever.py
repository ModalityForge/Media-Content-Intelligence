"""Vector retriever component."""

from typing import Any


class VectorRetriever:
    """Vector-based retrieval."""

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search vectors."""
        return []


vector_retriever = VectorRetriever()