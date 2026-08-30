"""Notification service."""

from typing import Any
from datetime import datetime


class NotificationService:
    """Service for sending notifications."""

    def __init__(self):
        self.notifications: list[dict[str, Any]] = []

    def send_notification(
        self,
        recipient: str,
        notification_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a notification."""
        notification = {
            "notification_id": f"notif-{len(self.notifications) + 1:06d}",
            "recipient": recipient,
            "type": notification_type,
            "message": message,
            "metadata": metadata or {},
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent",
        }

        self.notifications.append(notification)
        return notification

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> dict[str, Any]:
        """Send email notification (mock)."""
        return self.send_notification(
            recipient=to,
            notification_type="email",
            message=subject,
            metadata={"body": body},
        )

    def send_webhook(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send webhook notification (mock)."""
        return self.send_notification(
            recipient=url,
            notification_type="webhook",
            message="Webhook payload",
            metadata=payload,
        )

    def get_notifications(
        self,
        recipient: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get notifications."""
        filtered = self.notifications

        if recipient:
            filtered = [n for n in filtered if n["recipient"] == recipient]

        return filtered[:limit]


notification_service = NotificationService()