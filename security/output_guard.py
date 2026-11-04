"""Prevent sensitive credential-shaped fields from leaving the public API.

Candidate dictionaries are inspected by key name for passwords, API keys,
secrets, tokens, and credentials. Callers may reject the complete object or
obtain a copy in which restricted values are redacted.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from typing import Any


class OutputGuard:
    """Guard against sensitive outputs."""

    RESTRICTED_FIELDS = [
        "password",
        "api_key",
        "secret",
        "token",
        "credential",
    ]

    def __init__(self):
        """Create a stateless guard using the restricted-field vocabulary."""

    def is_safe(self, data: dict[str, Any]) -> bool:
        """Check if output data is safe."""
        for key in data.keys():
            key_lower = key.lower()
            if any(r in key_lower for r in self.RESTRICTED_FIELDS):
                return False
        return True

    def filter(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter out restricted fields."""
        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(r in key_lower for r in self.RESTRICTED_FIELDS):
                filtered[key] = "[REDACTED]"
            else:
                filtered[key] = value
        return filtered


output_guard = OutputGuard()
