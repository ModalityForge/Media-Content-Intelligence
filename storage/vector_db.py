"""Vector database storage."""

from typing import Any


class VectorDB:
    """In-memory vector database."""

    def __init__(self):
        self.vectors: dict[str, list[float]] = {}
        self.metadata: dict[str, dict[str, Any]] = {}

    def add(self, clip_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Add vector."""
        self.vectors[clip_id] = vector
        if metadata:
            self.metadata[clip_id] = metadata

    def search(self, query_vector: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        """Search vectors."""
        return []


vector_db = VectorDB()