"""Feedback service."""

import uuid
from datetime import datetime, timezone
from typing import Any


class FeedbackService:
    """Service for managing user feedback."""

    def __init__(self):
        self.feedback: list[dict[str, Any]] = []

    def submit_feedback(
        self,
        query: str,
        clip_id: str,
        feedback_type: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """Submit user feedback."""
        record = {
            "feedback_id": f"fb-{uuid.uuid4().hex[:8]}",
            "query": query,
            "clip_id": clip_id,
            "feedback_type": feedback_type,
            "comment": comment,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.feedback.append(record)
        return record

    def get_feedback(
        self,
        query: str | None = None,
        clip_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get feedback with optional filtering."""
        filtered = self.feedback

        if query:
            filtered = [f for f in filtered if f["query"] == query]

        if clip_id:
            filtered = [f for f in filtered if f["clip_id"] == clip_id]

        return filtered[:limit]

    def get_stats(self) -> dict[str, Any]:
        """Get feedback statistics."""
        total = len(self.feedback)
        thumbs_up = sum(1 for f in self.feedback if f["feedback_type"] == "thumbs_up")
        thumbs_down = sum(1 for f in self.feedback if f["feedback_type"] == "thumbs_down")

        return {
            "total": total,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "positive_rate": thumbs_up / total if total > 0 else 0,
        }


feedback_service = FeedbackService()
