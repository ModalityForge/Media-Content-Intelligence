"""Ingestion tests."""

import pytest
from components.ingestion.video_loader import VideoLoader
from components.ingestion.job_registry import JobRegistry


def test_video_loader_register():
    """Test video registration."""
    loader = VideoLoader()
    video_id = loader.register("/path/to/video.mp4")
    assert video_id.startswith("video-")


def test_job_registry_create():
    """Test job creation."""
    registry = JobRegistry()
    job_id = registry.create_job("/path/to/video.mp4", priority=5)
    assert job_id.startswith("job-")
    job = registry.get_job(job_id)
    assert job is not None
    assert job["status"] == "queued"


def test_job_registry_update_progress():
    """Test progress update."""
    registry = JobRegistry()
    job_id = registry.create_job("/path/to/video.mp4")
    registry.update_progress(job_id, 0.5)
    job = registry.get_job(job_id)
    assert job["progress"] == 0.5