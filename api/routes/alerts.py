"""Alert endpoints."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas import AlertEvent

router = APIRouter()

alerts_storage: list[dict] = []


@router.get("", response_model=list[AlertEvent])
async def get_alerts(
    alert_type: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> list[AlertEvent]:
    """Get alerts."""
    filtered = alerts_storage
    if alert_type:
        filtered = [a for a in filtered if a.get("alert_type") == alert_type]
    if severity:
        filtered = [a for a in filtered if a.get("severity") == severity]

    return [
        AlertEvent(
            alert_id=a["alert_id"],
            alert_type=a["alert_type"],
            severity=a["severity"],
            clip_id=a.get("clip_id"),
            message=a["message"],
            created_at=a["created_at"],
            metadata=a.get("metadata", {}),
        )
        for a in filtered[:limit]
    ]


@router.post("", response_model=AlertEvent)
async def create_alert(alert: AlertEvent) -> AlertEvent:
    """Create an alert."""
    if not alert.alert_id:
        alert.alert_id = f"alert-{uuid.uuid4().hex[:8]}"
    if not alert.created_at:
        alert.created_at = datetime.now(timezone.utc)

    alerts_storage.append(alert.model_dump())
    return alert


@router.get("/{alert_id}")
async def get_alert(alert_id: str) -> dict:
    """Get a specific alert."""
    for alert in alerts_storage:
        if alert["alert_id"] == alert_id:
            return alert
    return {"error": "Alert not found"}


@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str) -> dict:
    """Acknowledge an alert."""
    for alert in alerts_storage:
        if alert["alert_id"] == alert_id:
            alert["acknowledged"] = True
            alert["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
            return {"status": "acknowledged"}
    return {"error": "Alert not found"}
