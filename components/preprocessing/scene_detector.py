"""Scene detection component."""

from typing import Any


class SceneDetector:
    """Detect scenes in video."""

    def detect_scenes(self, video_path: str) -> list[dict[str, Any]]:
        """Detect scene boundaries."""
        scenes = []
        for i in range(10):
            scenes.append({
                "scene_id": f"scene-{i}",
                "start_time": i * 60.0,
                "end_time": (i + 1) * 60.0,
                "confidence": 0.9,
            })
        return scenes


scene_detector = SceneDetector()