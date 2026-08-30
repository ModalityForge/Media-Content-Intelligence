"""Metadata database storage."""

from typing import Any


class MetadataDB:
    """In-memory metadata database."""

    def __init__(self):
        self.data: dict[str, dict[str, Any]] = {}

    def insert(self, video_id: str, metadata: dict[str, Any]) -> None:
        """Insert metadata."""
        self.data[video_id] = metadata

    def get(self, video_id: str) -> dict[str, Any] | None:
        """Get metadata."""
        return self.data.get(video_id)

    def query(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Query metadata."""
        return list(self.data.values())


metadata_db = MetadataDB()