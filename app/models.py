"""Domain models and dataclasses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class VideoAsset:
    """Video asset model."""

    video_id: str
    source_path: str
    source_type: str
    duration_seconds: float
    width: int
    height: int
    fps: float
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneChunk:
    """Scene chunk within a video."""

    scene_id: str
    video_id: str
    start_time: float
    end_time: float
    scene_type: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscriptSegment:
    """Transcript segment."""

    segment_id: str
    video_id: str
    start_time: float
    end_time: float
    text: str
    language: str
    confidence: float


@dataclass
class OCRSegment:
    """OCR text segment from video frames."""

    segment_id: str
    video_id: str
    frame_time: float
    text: str
    bounding_box: tuple[int, int, int, int]
    confidence: float


@dataclass
class FrameEmbedding:
    """Frame embedding for vector search."""

    video_id: str
    frame_time: float
    embedding: list[float]
    embedding_model: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RightsMetadata:
    """Rights metadata for a video."""

    video_id: str
    territories: list[str]
    usage_types: list[str]
    start_date: datetime | None
    end_date: datetime | None
    max_duration_seconds: float | None
    restrictions: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrandSafetyPolicy:
    """Brand safety policy."""

    policy_id: str
    prohibited_brands: list[str] = field(default_factory=list)
    required_brands: list[str] = field(default_factory=list)
    excluded_logos: list[str] = field(default_factory=list)
    allowed_content_types: list[str] = field(default_factory=list)
    blocked_content_types: list[str] = field(default_factory=list)


@dataclass
class AgentState:
    """Agent execution state."""

    trace_id: str
    query: str
    rewritten_query: str | None = None
    hyde_query: str | None = None
    parsed_intent: dict[str, Any] | None = None
    candidate_clips: list[dict[str, Any]] = field(default_factory=list)
    planned_tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    evidence_bundle: dict[str, Any] | None = None
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    guardrail_results: dict[str, Any] | None = None
    final_answer: str | None = None
    human_review_required: bool = False
    error: str | None = None


@dataclass
class EvidenceBundle:
    """Bundle of evidence for validation."""

    clip_id: str
    query: str
    retrieved_evidence: dict[str, Any]
    visual_evidence: dict[str, Any] = field(default_factory=dict)
    audio_evidence: dict[str, Any] = field(default_factory=dict)
    text_evidence: dict[str, Any] = field(default_factory=dict)
    rights_evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionJob:
    """Ingestion job tracking."""

    job_id: str
    video_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    progress: float = 0.0
    error: str | None = None