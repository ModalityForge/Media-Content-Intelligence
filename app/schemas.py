"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class VideoIngestRequest(BaseModel):
    """Request to ingest a video."""

    video_path: str = Field(..., description="Path to the video file or URL")
    source_type: str = Field(default="file", description="Type: file, stream, or url")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Video metadata")
    priority: int = Field(default=5, description="Ingestion priority 1-10")


class VideoIngestResponse(BaseModel):
    """Response from video ingestion."""

    job_id: str
    status: str
    message: str
    created_at: datetime


class SearchRequest(BaseModel):
    """Search query request."""

    query: str = Field(..., description="Natural language search query")
    filters: dict[str, Any] = Field(default_factory=dict, description="Search filters")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum results")
    intent_type: str | None = Field(default=None, description="Parsed intent type")


class CandidateClip(BaseModel):
    """A candidate clip from search."""

    clip_id: str
    video_id: str
    start_time: float
    end_time: float
    score: float
    relevance_reason: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response with candidate clips."""

    query: str
    rewritten_query: str
    hyde_query: str | None = None
    candidate_clips: list[CandidateClip]
    total_found: int
    trace_id: str
    processing_time_ms: float


class ToolCallRecord(BaseModel):
    """Record of a tool call."""

    tool_name: str
    input_payload: dict[str, Any]
    output: dict[str, Any]
    duration_ms: float


class EvidenceValidationRequest(BaseModel):
    """Request for evidence validation."""

    evidence_bundle: dict[str, Any]
    validation_criteria: list[str]


class ValidationResultItem(BaseModel):
    """Result for a single validation check."""

    criterion: str
    passed: bool
    confidence: float
    reason: str


class EvidenceValidationResult(BaseModel):
    """Result from evidence validation."""

    clip_id: str
    overall_passed: bool
    overall_confidence: float
    results: list[ValidationResultItem]
    requires_human_review: bool = False
    review_reason: str | None = None


class ClipExportRequest(BaseModel):
    """Request to export a clip."""

    clip_id: str
    format: str = Field(default="mp4", description="Export format")
    quality: str = Field(default="high", description="Quality: low, medium, high")
    include_watermark: bool = Field(default=False)
    apply_face_blur: bool = Field(default=False)


class ClipExportResponse(BaseModel):
    """Response from clip export."""

    export_id: str
    status: str
    download_url: str | None
    expires_at: datetime | None


class AlertEvent(BaseModel):
    """Alert event."""

    alert_id: str
    alert_type: str
    severity: str
    clip_id: str | None
    message: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    """Feedback on a search result."""

    query: str
    clip_id: str
    feedback: str = Field(..., description="thumbs_up, thumbs_down, or comment")
    comment: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    services: dict[str, str]