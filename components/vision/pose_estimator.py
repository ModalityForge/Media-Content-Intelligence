"""Pose estimator wrapper."""

from typing import Any


class PoseEstimator:
    """Wrapper for pose estimation (MMPose mock)."""

    def estimate(self, frame_path: str) -> list[dict[str, Any]]:
        """Estimate poses."""
        return []


pose_estimator = PoseEstimator()