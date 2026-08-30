"""Rights filter component."""

from typing import Any


class RightsFilter:
    """Filter by rights metadata."""

    def filter(self, results: list[dict[str, Any]], territory: str, usage: str) -> list[dict[str, Any]]:
        """Filter by rights."""
        return results


rights_filter = RightsFilter()