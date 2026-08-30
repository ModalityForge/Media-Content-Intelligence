"""Ingestion endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks

from app.schemas import VideoIngestRequest, VideoIngestResponse

router = APIRouter()


@router.post("/video", response_model=VideoIngestResponse)
async def ingest_video(
    request: VideoIngestRequest,
    background_tasks: BackgroundTasks,
) -> VideoIngestResponse:
    """Ingest a video for processing."""
    job_id = f"job-{uuid.uuid4().hex[:8]}"

    def process_video():
        pass

    background_tasks.add_task(process_video)

    return VideoIngestResponse(
        job_id=job_id,
        status="queued",
        message="Video ingestion job queued",
        created_at=datetime.utcnow(),
    )


@router.get("/job/{job_id}")
async def get_job_status(job_id: str) -> dict:
    """Get ingestion job status."""
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 0.5,
        "message": "Processing video frames",
    }


@router.delete("/job/{job_id}")
async def cancel_job(job_id: str) -> dict:
    """Cancel an ingestion job."""
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled",
    }