"""Create and expose the public Media Content Intelligence FastAPI service.

The application serves health, deterministic catalog search, exact authorized
video previews, feedback, and Prometheus metrics. Placeholder operational
routes are intentionally excluded from the public API until their backing
workers and persistence are production-ready.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config import settings
from app.dependencies import generate_trace_id, set_trace_id
from observability.logger import get_logger
from observability.metrics import init_metrics

from api.routes import feedback, health, search, videos

logger = get_logger(__name__)

REQUEST_COUNT = Counter(
    "mci_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "mci_request_latency_seconds", "Request latency", ["method", "endpoint"]
)


class TraceMetricsMiddleware:
    """Add tracing and metrics without buffering streamed video responses."""

    def __init__(self, app: ASGIApp):
        """Wrap the downstream ASGI application without buffering responses."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Attach a trace ID and record status and latency for one HTTP request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        trace_id = headers.get("X-Trace-ID", generate_trace_id())
        set_trace_id(trace_id)
        scope.setdefault("state", {})["trace_id"] = trace_id
        start_time = time.time()
        status_code = 500

        async def send_with_trace(message: Message) -> None:
            """Intercept response-start messages to add tracing metadata."""
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)["X-Trace-ID"] = trace_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_trace)
        finally:
            REQUEST_COUNT.labels(
                method=scope.get("method", ""),
                endpoint=scope.get("path", ""),
                status=status_code,
            ).inc()
            REQUEST_LATENCY.labels(
                method=scope.get("method", ""),
                endpoint=scope.get("path", ""),
            ).observe(time.time() - start_time)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting MCI-v2.0", app_name=settings.app_name)
    init_metrics()
    yield
    logger.info("Shutting down MCI-v2.0")


app = FastAPI(
    title=settings.app_name,
    description="MCI-v2.0: Media Content Intelligence platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TraceMetricsMiddleware)


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(videos.router, prefix="/videos", tags=["Videos"])


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/")
async def root():
    """Return the public service identity, semantic version, and status."""
    return {
        "service": settings.app_name,
        "version": "2.0.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
    )
