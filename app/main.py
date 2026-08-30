"""FastAPI application entry point."""

import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from app.config import settings
from app.dependencies import generate_trace_id, set_trace_id
from observability.logger import get_logger
from observability.metrics import init_metrics

from api.routes import health, ingest, search, clips, alerts, feedback

logger = get_logger(__name__)

REQUEST_COUNT = Counter(
    "mci_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "mci_request_latency_seconds", "Request latency", ["method", "endpoint"]
)


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


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """Add trace ID to request."""
    trace_id = request.headers.get("X-Trace-ID", generate_trace_id())
    set_trace_id(trace_id)
    request.state.trace_id = trace_id

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    response.headers["X-Trace-ID"] = trace_id
    return response


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(clips.router, prefix="/clips", tags=["Clips"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/")
async def root():
    """Root endpoint."""
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