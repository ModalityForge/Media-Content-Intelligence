"""Validated data structures exchanged by MCI agents and HTTP endpoints.

These Pydantic models form the public contract between clients, the search
orchestrator, evidence validation, health monitoring, and feedback capture.
Field descriptions are surfaced automatically through the OpenAPI schema.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

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

    clip_id: str = Field(description="Stable identifier for this candidate clip")
    video_id: str = Field(description="Catalog identifier of the exact source video")
    start_time: float = Field(description="Candidate segment start time in seconds")
    end_time: float = Field(description="Candidate segment end time in seconds")
    score: float = Field(description="Normalized deterministic retrieval relevance score")
    relevance_reason: str = Field(description="Human-readable explanation of matched metadata")
    title: str | None = Field(default=None, description="Human-readable catalog title for the asset")
    file_path: str | None = Field(default=None, description="Authorized local path used for exact preview streaming")
    description: str | None = Field(default=None, description="Source-provided catalog description")
    source: str | None = Field(default=None, description="Publisher, archive, or local source label")
    source_url: str | None = Field(default=None, description="Exact publisher URL for the original media asset")
    source_page: str | None = Field(default=None, description="Publisher page describing the source item")
    asset_name: str | None = Field(default=None, description="Original filename or human-readable asset name")
    dataset: str | None = Field(default=None, description="Dataset partition from which the asset was indexed")
    content_type: str = Field(default="video", description="High-level media category such as advertisement or social media")
    mime_type: str | None = Field(default=None, description="Browser-compatible MIME type for preview playback")
    annotations: dict[str, Any] = Field(default_factory=dict, description="Source annotations retained without semantic reinterpretation")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Verified evidence attached by downstream inference or review")


class SearchResponse(BaseModel):
    """Search response with candidate clips."""

    query: str = Field(description="Original natural-language query supplied by the client")
    rewritten_query: str = Field(description="Deterministically expanded query used for retrieval")
    hyde_query: str | None = Field(default=None, description="Hypothetical ideal media description used for retrieval")
    candidate_clips: list[CandidateClip] = Field(description="Ranked, explainable candidate media segments")
    total_found: int = Field(description="Number of candidates found before response truncation")
    trace_id: str = Field(description="Request identifier propagated through logs and responses")
    processing_time_ms: float = Field(description="End-to-end API processing latency in milliseconds")


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

    criterion: str = Field(description="Stable name of the evidence or policy criterion")
    passed: bool = Field(description="Whether supplied evidence satisfied the criterion")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence supported by the supplied evidence")
    reason: str = Field(description="Human-readable basis for the validation decision")


class EvidenceValidationResult(BaseModel):
    """Result from evidence validation."""

    clip_id: str = Field(description="Candidate clip identifier to which this decision applies")
    overall_passed: bool = Field(description="Whether every evaluated criterion passed")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Mean confidence across evaluated validation criteria")
    results: list[ValidationResultItem] = Field(description="Individual evidence and policy decisions")
    requires_human_review: bool = Field(default=False, description="Whether automatic evidence is insufficient for approval")
    review_reason: str | None = Field(default=None, description="Explanation supplied when manual review is required")


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
    """Structured operational alert emitted for a media or policy event."""

    alert_id: str
    alert_type: str
    severity: str
    clip_id: str | None
    message: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    """Feedback on a search result."""

    query: str = Field(description="Search query associated with the user judgement")
    clip_id: str = Field(description="Candidate clip receiving the feedback")
    feedback: str = Field(..., description="thumbs_up, thumbs_down, or comment")
    comment: str | None = Field(default=None, description="Optional free-text explanation of the judgement")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Aggregate health state of this API process")
    version: str = Field(description="Semantic version of the running application")
    timestamp: datetime = Field(description="Timezone-aware UTC time at which health was evaluated")
    services: dict[str, str] = Field(description="Named component statuses included in the health decision")
