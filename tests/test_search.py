"""Search tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_returns_candidate_clips():
    """Test search returns candidate clips."""
    response = client.post(
        "/search",
        json={"query": "Find Messi drinking Pepsi", "max_results": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidate_clips" in data
    assert len(data["candidate_clips"]) > 0


def test_search_query_parsing():
    """Test search query parsing."""
    response = client.post(
        "/search",
        json={"query": "Find 30-second clips where Messi drinks Pepsi"},
    )
    assert response.status_code == 200