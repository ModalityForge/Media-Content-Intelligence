"""Face blur wrapper."""

from typing import Any


class FaceBlur:
    """Wrapper for face blurring."""

    def blur(self, clip_id: str, intensity: float = 0.8) -> dict[str, Any]:
        """Blur faces."""
        return {"clip_id": clip_id, "faces_blurred": 0}


face_blur = FaceBlur()