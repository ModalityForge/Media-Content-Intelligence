"""Clip generator component."""

from typing import Any


class ClipGenerator:
    """Generate video clips."""

    def generate(self, video_id: str, start: float, end: float) -> str:
        """Generate clip."""
        return f"clip-{video_id}-{start}-{end}"


clip_generator = ClipGenerator()