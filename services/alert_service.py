"""Alert service."""

import uuid
from datetime import datetime
from typing import Any


class AlertService:
    """Service for managing alerts."""

    def __init__(self):
        self.alerts: list[dict[str, Any]] = []

    def create_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info",
        clip_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new alert."""
        alert = {
            "alert_id": f"alert-{uuid.uuid4().hex[:8]}",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "clip_id": clip_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "acknowledged": False,
        }

        self.alerts.append(alert)
        return alert

    def get_alerts(
        self,
        alert_type: str | None = None,
        severity: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get alerts with optional filtering."""
        filtered = self.alerts

        if alert_type:
            filtered = [a for a in filtered if a["alert_type"] == alert_type]

        if severity:
            filtered = [a for a in filtered if a["severity"] == severity]

        return filtered[:limit]

    def acknowledge(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                return True
        return False

    def get_unacknowledged_count(self) -> int:
        """Get count of unacknowledged alerts."""
        return sum(1 for a in self.alerts if not a.get("acknowledged", False))


alert_service = AlertService()