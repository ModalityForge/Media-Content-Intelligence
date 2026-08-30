"""Audit logger for security events."""

import json
import os
from datetime import datetime
from typing import Any


class AuditLogger:
    """Log security audit events."""

    def __init__(self, log_path: str = "logs/audit.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(
        self,
        event_type: str,
        actor: str,
        action: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an audit event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "result": result,
            "details": details or {},
        }

        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def log_query(self, query: str, result: str, trace_id: str) -> None:
        """Log a search query."""
        self.log("query", "user", "search", result, {"query": query[:100], "trace_id": trace_id})

    def log_rights_check(self, clip_id: str, territory: str, result: str) -> None:
        """Log rights check."""
        self.log("rights", "system", "check_rights", result, {"clip_id": clip_id, "territory": territory})

    def log_guardrail(self, clip_id: str, guardrail_type: str, result: str) -> None:
        """Log guardrail action."""
        self.log("guardrail", "system", guardrail_type, result, {"clip_id": clip_id})


audit_logger = AuditLogger()