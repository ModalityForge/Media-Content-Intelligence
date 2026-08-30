"""Redis cache storage."""

from typing import Any


class RedisCache:
    """In-memory cache (fallback for Redis)."""

    def __init__(self):
        self.cache: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        """Get value."""
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value."""
        self.cache[key] = value

    def delete(self, key: str) -> None:
        """Delete key."""
        self.cache.pop(key, None)


redis_cache = RedisCache()