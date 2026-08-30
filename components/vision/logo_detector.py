"""Logo detector wrapper."""

from typing import Any


class LogoDetector:
    """Wrapper for logo detection (Grounding DINO mock)."""

    def detect(self, frame_path: str, target_brands: list[str]) -> list[dict[str, Any]]:
        """Detect logos."""
        return []


logo_detector = LogoDetector()