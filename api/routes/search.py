"""Search endpoints."""

import time
import uuid

from fastapi import APIRouter, Depends
from fastapi import Request

from app.schemas import SearchRequest, SearchResponse, CandidateClip
from app.dependencies import get_request_id
from agents.media_orchestrator import MediaOrchestratorAgent

router = APIRouter()

orchestrator = MediaOrchestratorAgent()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    http_request: Request,
) -> SearchResponse:
    """Search for media clips."""
    start_time = time.time()

    trace_id = get_request_id(http_request)
    http_request.state.trace_id = trace_id

    result = await orchestrator.run(
        query=request.query,
        filters=request.filters,
        max_results=request.max_results,
        trace_id=trace_id,
    )

    processing_time = (time.time() - start_time) * 1000

    return SearchResponse(
        query=result.get("query", request.query),
        rewritten_query=result.get("rewritten_query", request.query),
        hyde_query=result.get("hyde_query"),
        candidate_clips=[
            CandidateClip(
                clip_id=c["clip_id"],
                video_id=c["video_id"],
                start_time=c["start_time"],
                end_time=c["end_time"],
                score=c["score"],
                relevance_reason=c["relevance_reason"],
                title=c.get("title"),
                file_path=c.get("file_path"),
                description=c.get("description"),
                source=c.get("source"),
                source_url=c.get("source_url"),
                source_page=c.get("source_page"),
                asset_name=c.get("asset_name"),
                dataset=c.get("dataset"),
                content_type=c.get("content_type", "video"),
                mime_type=c.get("mime_type"),
                annotations=c.get("annotations", {}),
                evidence=c.get("evidence", {}),
            )
            for c in result.get("candidate_clips", [])
        ],
        total_found=result.get("total_found", 0),
        trace_id=trace_id,
        processing_time_ms=processing_time,
    )


@router.get("/suggestions")
async def get_query_suggestions(q: str) -> dict:
    """Get query suggestions."""
    return {
        "suggestions": [
            f"{q} Messi Pepsi",
            f"{q} sports highlights",
            f"{q} brand logos",
        ]
    }
