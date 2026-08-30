"""Distributed tracing utilities."""

import contextlib
import uuid
from contextvars import ContextVar
from typing import Any

trace_context: ContextVar[dict[str, Any]] = ContextVar("trace_context", default={})


class TraceSpan:
    """Trace span."""

    def __init__(self, name: str, trace_id: str, parent_id: str | None = None):
        self.name = name
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.span_id = uuid.uuid4().hex[:8]
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.attributes: dict[str, Any] = {}

    def __enter__(self):
        import time

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        self.end_time = time.time()

    @property
    def duration_ms(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


def get_trace_id() -> str:
    """Get current trace ID."""
    ctx = trace_context.get()
    return ctx.get("trace_id", "")


def get_span_id() -> str:
    """Get current span ID."""
    ctx = trace_context.get()
    return ctx.get("span_id", "")


@contextlib.contextmanager
def trace(name: str, **attributes):
    """Create a trace span."""
    ctx = trace_context.get()
    trace_id = ctx.get("trace_id", uuid.uuid4().hex[:12])

    span = TraceSpan(name, trace_id)
    span.attributes.update(attributes)

    new_ctx = {**ctx, "trace_id": trace_id, "span_id": span.span_id}
    token = trace_context.set(new_ctx)

    try:
        yield span
    finally:
        trace_context.reset(token)


def create_trace_id() -> str:
    """Create a new trace ID."""
    return f"mci-{uuid.uuid4().hex[:12]}"