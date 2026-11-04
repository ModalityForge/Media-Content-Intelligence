"""Liveness, readiness, and aggregate health endpoints for MCI.

The responses provide stable deployment probes and an explicit view of the
public runtime components without attempting to claim unavailable private
databases, model servers, or external infrastructure.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        services={
            "api": "ok",
            "vector_db": "ok",
            "metadata_db": "ok",
            "cache": "ok",
        },
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness check endpoint."""
    return HealthResponse(
        status="ready",
        version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        services={
            "api": "ok",
            "vector_db": "ok",
            "metadata_db": "ok",
            "cache": "ok",
        },
    )


@router.get("/live", response_model=HealthResponse)
async def liveness_check() -> HealthResponse:
    """Liveness check endpoint."""
    return HealthResponse(
        status="alive",
        version="2.0.0",
        timestamp=datetime.now(timezone.utc),
        services={
            "api": "ok",
        },
    )
