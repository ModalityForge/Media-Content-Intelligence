"""Tracker wrapper."""

from typing import Any


class Tracker:
    """Wrapper for tracking (ByteTrack/DeepSORT mock)."""

    def track(self, clip_id: str) -> list[dict[str, Any]]:
        """Track objects."""
        return []


tracker = Tracker()