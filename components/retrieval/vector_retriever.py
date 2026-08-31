"""Vector retriever component."""

from typing import Any

from storage.video_catalog import catalog


class VectorRetriever:
    """Vector-based retrieval."""

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search vectors."""
        # Until embeddings have been generated, use the truthful metadata
        # fallback rather than returning random or synthetic vector hits.
        return catalog.search(query, top_k=top_k)


vector_retriever = VectorRetriever()
