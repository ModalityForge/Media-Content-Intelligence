"""Object detector wrapper."""

from typing import Any


class ObjectDetector:
    """Wrapper for object detection (mock)."""

    def detect(self, frame_path: str) -> list[dict[str, Any]]:
        """Detect objects."""
        return [{"class": "person", "confidence": 0.9, "bbox": [100, 100, 200, 200]}]


object_detector = ObjectDetector()