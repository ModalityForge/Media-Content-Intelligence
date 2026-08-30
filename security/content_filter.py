"""Content filter for unsafe content."""

from typing import Any


BLOCKED_CONTENT_TAGS = ["violence", "nsfw", "hate", "illegal", "self_harm"]


class ContentFilter:
    """Filter unsafe content."""

    def __init__(self):
        self.blocked_tags = BLOCKED_CONTENT_TAGS

    def is_safe(self, content_tags: list[str]) -> bool:
        """Check if content is safe."""
        return not any(tag in self.blocked_tags for tag in content_tags)

    def filter_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter out unsafe results."""
        filtered = []
        for r in results:
            tags = r.get("content_tags", [])
            if self.is_safe(tags):
                filtered.append(r)
        return filtered


content_filter = ContentFilter()