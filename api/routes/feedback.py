"""In-memory relevance-feedback endpoints for the public demonstration API.

The routes accept user judgements about returned clips and expose simple
aggregate counts. Persistence is intentionally outside this public smoke
runtime, so callers must not treat records as durable across restarts.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas import FeedbackRequest

router = APIRouter()

feedback_storage: list[dict] = []


@router.post("")
async def submit_feedback(request: FeedbackRequest) -> dict:
    """Submit feedback on a search result."""
    feedback_id = f"fb-{uuid.uuid4().hex[:8]}"

    record = {
        "feedback_id": feedback_id,
        "query": request.query,
        "clip_id": request.clip_id,
        "feedback": request.feedback,
        "comment": request.comment,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    feedback_storage.append(record)

    return {
        "feedback_id": feedback_id,
        "status": "recorded",
        "message": "Feedback recorded successfully",
    }


@router.get("")
async def get_feedback(
    query: str | None = None,
    clip_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Get feedback records."""
    filtered = feedback_storage

    if query:
        filtered = [f for f in filtered if f.get("query") == query]
    if clip_id:
        filtered = [f for f in filtered if f.get("clip_id") == clip_id]

    return filtered[:limit]


@router.get("/stats")
async def get_feedback_stats() -> dict:
    """Get feedback statistics."""
    thumbs_up = sum(1 for f in feedback_storage if f.get("feedback") == "thumbs_up")
    thumbs_down = sum(1 for f in feedback_storage if f.get("feedback") == "thumbs_down")

    return {
        "total": len(feedback_storage),
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
    }
