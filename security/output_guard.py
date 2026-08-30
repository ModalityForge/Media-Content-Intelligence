"""Output guard - filters restricted fields."""

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
        pass

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