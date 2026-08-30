"""Thumbnail generator component."""

from typing import Any


class ThumbnailGenerator:
    """Generate thumbnails."""

    def generate(self, clip_id: str, timestamp: float = 0.0) -> str:
        """Generate thumbnail."""
        return f"thumb_{clip_id}.jpg"


thumbnail_generator = ThumbnailGenerator()