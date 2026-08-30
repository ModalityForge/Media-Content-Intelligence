"""Semantic caching service."""

import hashlib
import time
from typing import Any


class SemanticCache:
    """Simple in-memory semantic cache."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache: dict[str, dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def _make_key(self, query: str, filters: dict[str, Any] | None = None) -> str:
        """Generate cache key."""
        key_parts = [query]
        if filters:
            key_parts.append(str(sorted(filters.items())))
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, filters: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Get cached result."""
        key = self._make_key(query, filters)

        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                return entry["result"]
            else:
                del self.cache[key]

        return None

    def set(
        self,
        query: str,
        result: dict[str, Any],
        filters: dict[str, Any] | None = None,
    ) -> None:
        """Set cache result."""
        key = self._make_key(query, filters)
        self.cache[key] = {
            "result": result,
            "timestamp": time.time(),
        }

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
        }


cache = SemanticCache()