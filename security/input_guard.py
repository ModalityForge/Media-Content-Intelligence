"""Input guard - protects against prompt injection and malicious inputs."""

import re
from typing import Any


class InputGuard:
    """Guard against malicious inputs."""

    BLOCKED_PATTERNS = [
        r"ignore\s+(?:previous|above|all)\s+(?:instructions?|rules?|constraints?)",
        r"disregard\s+(?:your|from)",
        r"forget\s+(?:everything|your|all)",
        r"system\s*:\s*",
        r"you\s+are\s+(?:now|actually)",
        r"play\s+role\s+of",
        r"new\s+instructions?:",
    ]

    def __init__(self):
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]

    def is_safe(self, query: str) -> bool:
        """Check if input is safe."""
        if not query or len(query.strip()) == 0:
            return False

        for pattern in self.blocked_patterns:
            if pattern.search(query):
                return False

        return True

    def sanitize(self, query: str) -> str:
        """Sanitize input query."""
        sanitized = query.strip()

        for pattern in self.blocked_patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)

        return sanitized

    def validate(self, query: str) -> dict[str, Any]:
        """Validate and return detailed result."""
        if not query or len(query.strip()) == 0:
            return {"safe": False, "reason": "Empty query"}

        for i, pattern in enumerate(self.blocked_patterns):
            if pattern.search(query):
                return {
                    "safe": False,
                    "reason": "Blocked pattern detected",
                    "pattern_index": i,
                }

        return {"safe": True, "reason": "Query is safe"}


input_guard = InputGuard()