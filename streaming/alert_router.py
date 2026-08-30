"""Alert router for streaming."""

from typing import Any


class AlertRouter:
    """Route alerts to appropriate handlers."""

    def route(self, alert: dict[str, Any]) -> None:
        """Route alert."""
        pass


alert_router = AlertRouter()