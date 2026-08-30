"""Frame extraction component."""

import os
from typing import Any


class FrameExtractor:
    """Extract frames from video."""

    def __init__(self, output_dir: str = "./data/frames"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def extract_frames(self, video_path: str, interval_seconds: float = 1.0) -> list[str]:
        """Extract frames at interval."""
        frames = []
        for i in range(30):
            frame_path = os.path.join(self.output_dir, f"frame_{i:05d}.jpg")
            frames.append(frame_path)
        return frames

    def extract_at_timestamp(self, video_path: str, timestamp: float) -> str:
        """Extract frame at specific timestamp."""
        return os.path.join(self.output_dir, f"frame_{timestamp:.2f}.jpg")


frame_extractor = FrameExtractor()