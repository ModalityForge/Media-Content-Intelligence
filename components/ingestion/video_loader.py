"""Video loader component."""

import os
from typing import Any


class VideoLoader:
    """Load video files."""

    def __init__(self, base_path: str = "./data/raw"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def load(self, video_path: str) -> dict[str, Any]:
        """Load a video file."""
        return {
            "video_id": os.path.basename(video_path),
            "path": video_path,
            "exists": os.path.exists(video_path),
            "size_bytes": os.path.getsize(video_path) if os.path.exists(video_path) else 0,
        }

    def register(self, video_path: str, metadata: dict[str, Any] | None = None) -> str:
        """Register a video for processing."""
        video_id = f"video-{hash(video_path) % 100000:05d}"
        return video_id


video_loader = VideoLoader()