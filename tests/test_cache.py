"""Cache tests."""

import pytest
from services.semantic_cache import SemanticCache


def test_cache_set_and_get():
    """Test cache set and get."""
    cache = SemanticCache(ttl_seconds=60)
    cache.set("test query", {"results": ["clip-1"]})
    result = cache.get("test query")
    assert result is not None
    assert result["results"] == ["clip-1"]


def test_cache_miss():
    """Test cache miss."""
    cache = SemanticCache(ttl_seconds=60)
    result = cache.get("nonexistent query")
    assert result is None


def test_cache_with_filters():
    """Test cache with filters."""
    cache = SemanticCache(ttl_seconds=60)
    cache.set("test query", {"results": ["clip-1"]}, {"territory": "Germany"})
    result = cache.get("test query", {"territory": "Germany"})
    assert result is not None


def test_cache_clear():
    """Test cache clear."""
    cache = SemanticCache(ttl_seconds=60)
    cache.set("test query", {"results": []})
    cache.clear()
    result = cache.get("test query")
    assert result is None