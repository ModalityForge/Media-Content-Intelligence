"""Job registry for tracking ingestion jobs."""

import uuid
from datetime import datetime
from typing import Any


class JobRegistry:
    """Registry for ingestion jobs."""

    def __init__(self):
        self.jobs: dict[str, dict[str, Any]] = {}

    def create_job(self, video_path: str, priority: int = 5) -> str:
        """Create a new job."""
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        self.jobs[job_id] = {
            "job_id": job_id,
            "video_path": video_path,
            "status": "queued",
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0.0,
        }
        return job_id

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def update_progress(self, job_id: str, progress: float) -> None:
        """Update job progress."""
        if job_id in self.jobs:
            self.jobs[job_id]["progress"] = progress


job_registry = JobRegistry()