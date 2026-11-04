"""Request-scoped dependencies and trace-context helpers for FastAPI.

The module creates stable request identifiers, propagates them through an
async-safe context variable, and exposes a minimal context-manager dependency
used by extension points without opening database or cache connections.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import uuid
from contextvars import ContextVar
from fastapi import Request

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    """Get or generate trace ID for current request."""
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set trace ID for current request."""
    trace_id_var.set(trace_id)


def generate_trace_id() -> str:
    """Generate a new trace ID."""
    return f"mci-{uuid.uuid4().hex[:12]}"


def get_request_id(request: Request) -> str:
    """Extract request ID from headers or generate new one."""
    return request.headers.get("X-Trace-ID", generate_trace_id())


class RequestContext:
    """Temporarily bind one trace identifier to the current async context."""

    def __init__(self, trace_id: str):
        """Store the trace identifier that will be bound on context entry."""
        self.trace_id = trace_id
        self._token = None

    def __enter__(self):
        """Bind the trace identifier and retain the reset token."""
        self._token = trace_id_var.set(self.trace_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore the previous trace context regardless of request outcome."""
        trace_id_var.reset(self._token)
