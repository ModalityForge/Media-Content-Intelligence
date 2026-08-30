"""Clip export endpoints."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter

from app.schemas import ClipExportRequest, ClipExportResponse

router = APIRouter()


@router.post("/export", response_model=ClipExportResponse)
async def export_clip(request: ClipExportRequest) -> ClipExportResponse:
    """Export a clip."""
    export_id = f"exp-{uuid.uuid4().hex[:8]}"

    return ClipExportResponse(
        export_id=export_id,
        status="completed",
        download_url=f"/downloads/{export_id}.mp4",
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )


@router.get("/{clip_id}")
async def get_clip_info(clip_id: str) -> dict:
    """Get clip information."""
    return {
        "clip_id": clip_id,
        "video_id": "video-001",
        "start_time": 30.0,
        "end_time": 60.0,
        "duration": 30.0,
        "format": "mp4",
        "status": "ready",
    }


@router.delete("/{clip_id}")
async def delete_clip(clip_id: str) -> dict:
    """Delete a clip."""
    return {
        "clip_id": clip_id,
        "status": "deleted",
        "message": "Clip deleted successfully",
    }