"""Verify query-aware retrieval and ranking through the public search API.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import pytest
import httpx

from app.main import app


async def search(payload: dict):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post("/search", json=payload)


async def test_search_returns_candidate_clips():
    """Test search returns query-relevant candidate clips."""
    response = await search({"query": "Find coffee commercials", "max_results": 5})
    assert response.status_code == 200
    data = response.json()
    assert "candidate_clips" in data
    assert len(data["candidate_clips"]) > 0
    assert "coffee" in data["candidate_clips"][0]["title"].lower()


async def test_search_query_parsing():
    """Test search query parsing."""
    response = await search({"query": "Insurance commercial"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidate_clips"]) > 0
    assert all("insurance" in clip["title"].lower() for clip in data["candidate_clips"])


async def test_search_does_not_return_unrelated_video():
    response = await search({"query": "Messi drinking Pepsi"})
    assert response.status_code == 200
    assert response.json()["candidate_clips"] == []


async def test_social_search_returns_annotated_video():
    response = await search({"query": "LeBron guard Steph"})
    assert response.status_code == 200
    clip = response.json()["candidate_clips"][0]
    assert clip["dataset"] == "snapugc"
    assert "LeBron" in clip["title"]
