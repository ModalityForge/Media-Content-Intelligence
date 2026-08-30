"""Metadata loader component."""

from typing import Any


class MetadataLoader:
    """Load and process video metadata."""

    def load_metadata(self, video_path: str) -> dict[str, Any]:
        """Load metadata from video."""
        return {
            "video_id": video_path,
            "duration_seconds": 600.0,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "codec": "h264",
        }

    def extract_embedded_metadata(self, video_path: str) -> dict[str, Any]:
        """Extract embedded metadata."""
        return {"title": "Sample Video", "description": "Sample description", "tags": []}


metadata_loader = MetadataLoader()