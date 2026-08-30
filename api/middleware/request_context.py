"""Request context middleware."""

import uuid
from typing import Callable

from fastapi import Request, Response


class RequestContextMiddleware:
    """Middleware to add request context."""

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("X-Trace-ID", f"mci-{uuid.uuid4().hex[:12]}")
        request.state.trace_id = trace_id
        request.state.request_id = str(uuid.uuid4())

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Request-ID"] = request.state.request_id

        return response
