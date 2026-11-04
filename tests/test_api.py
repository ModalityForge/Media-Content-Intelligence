"""Exercise the public FastAPI endpoints through an in-process ASGI client.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import pytest
import httpx

from app.main import app
from storage.video_catalog import catalog


async def request(method: str, path: str, **kwargs):
    """Issue an in-process ASGI request without a live server."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **kwargs)


async def test_health_endpoint():
    """Test health endpoint."""
    response = await request("GET", "/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


async def test_root_endpoint():
    """Test root endpoint."""
    response = await request("GET", "/")
    assert response.status_code == 200


async def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = await request("GET", "/metrics")
    assert response.status_code == 200


async def test_video_preview_endpoint_returns_exact_catalog_video():
    """A catalog id streams its own file, not a hashed fallback video."""
    record = next(record for record in catalog.records if record.is_playable())
    response = await request("GET", f"/videos/{record.video_id}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/")
    with open(record.file_path, "rb") as handle:
        assert response.content[:64] == handle.read(64)


async def test_unknown_video_id_returns_404():
    response = await request("GET", "/videos/video-does-not-exist")
    assert response.status_code == 404


async def test_video_preview_supports_byte_ranges():
    record = next(record for record in catalog.records if record.is_playable())
    response = await request(
        "GET",
        f"/videos/{record.video_id}",
        headers={"Range": "bytes=0-63"},
    )
    assert response.status_code == 206
    assert len(response.content) == 64
    assert response.headers["content-range"].startswith("bytes 0-63/")
