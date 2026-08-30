"""Application dependencies."""

import uuid
from contextvars import ContextVar
from typing import Generator

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
    """Request context manager."""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self._token = None

    def __enter__(self):
        self._token = trace_id_var.set(self.trace_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        trace_id_var.reset(self._token)


def get_db():
    """Get database session (placeholder)."""
    pass


def get_redis():
    """Get Redis client (placeholder)."""
    pass