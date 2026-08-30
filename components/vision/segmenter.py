"""Segmenter wrapper."""

from typing import Any


class Segmenter:
    """Wrapper for segmentation (SAM2 mock)."""

    def segment(self, frame_path: str) -> list[dict[str, Any]]:
        """Segment objects."""
        return []


segmenter = Segmenter()