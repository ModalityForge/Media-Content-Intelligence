"""Coordinate query understanding, retrieval, validation, and guardrails.

The orchestrator converts a natural-language request into structured intent,
runs deterministic BM25/catalog retrieval and RRF fusion, constructs traceable
candidates, invokes the evidence validator, and applies output safety checks.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import re
import time
from typing import Any

from agents.state import MCIState
from agents.evidence_validator import EvidenceValidatorAgent
from agents.a2a_protocol import send_task
from services.query_rewriter import extract_filters, rewrite_query
from services.hyde_generator import generate_hyde
from tools.mcp_registry import get_registry
from observability.logger import get_logger

logger = get_logger(__name__)


class MediaOrchestratorAgent:
    """Main orchestrator for media content intelligence."""

    def __init__(self):
        """Initialize the public tool registry and deterministic validator."""
        self.name = "media_orchestrator"
        self.tool_registry = get_registry()
        self.evidence_validator = EvidenceValidatorAgent()

    def parse_query(self, query: str) -> dict[str, Any]:
        """Parse user query into structured intent."""
        intent = {
            "type": "search",
            "query": query,
            "talents": [],
            "brands": {"required": [], "excluded": []},
            "actions": [],
            "territory": None,
            "usage_type": "digital_highlights",
            "duration": None,
            "filters": extract_filters(query),
        }

        talents = re.findall(r"\b(Messi|Ronaldo|LeBron|Tiger|Kobe|Beckham)\b", query, re.IGNORECASE)
        intent["talents"] = list(set(talents))

        required_brands = re.findall(r"\b(Adidas|Pepsi|Coca-Cola|Apple|Samsung)\b", query, re.IGNORECASE)
        excluded_brands = re.findall(r"\b(Nike|Unilever|PepsiCo)\s+(?:excluded|not)", query, re.IGNORECASE)

        brand_match = re.search(r"(\w+) is (?:not|absent|excluded)", query, re.IGNORECASE)
        if brand_match:
            excluded_brands.append(brand_match.group(1))

        intent["brands"]["required"] = list(set(required_brands))
        intent["brands"]["excluded"] = list(set(excluded_brands))
        if intent["brands"]["required"]:
            intent["filters"]["brands"] = intent["brands"]["required"]
        else:
            intent["filters"].pop("brands", None)
        if intent["brands"]["excluded"]:
            intent["filters"]["excluded_brands"] = intent["brands"]["excluded"]

        actions = re.findall(r"\b(drinking|scoring|celebrating|running|celebrating)\b", query, re.IGNORECASE)
        intent["actions"] = list(set(actions))

        if "germany" in query.lower():
            intent["territory"] = "Germany"
        elif re.search(r"\b(?:us|usa|united states)\b", query, re.IGNORECASE):
            intent["territory"] = "USA"

        if "30-second" in query.lower() or "30s" in query.lower():
            intent["duration"] = 30

        return intent

    def rewrite_query(self, query: str) -> str:
        """Rewrite query for better retrieval."""
        return rewrite_query(query)

    def generate_hyde(self, query: str) -> str:
        """Generate HyDE hypothetical document."""
        return generate_hyde(query)

    def plan_tool_calls(
        self,
        parsed_intent: dict[str, Any],
        filters: dict[str, Any] | None = None,
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        """Plan deterministic retrieval calls.

        Mock vision tools are deliberately not run against placeholder clip
        ids. Random mock detections must never influence which video is shown.
        """
        payload = {
            "query": parsed_intent.get("query", ""),
            "top_k": top_k,
            "filters": filters or {},
        }
        return [
            {"tool_name": "vector_search", "payload": dict(payload)},
            {"tool_name": "bm25_search", "payload": dict(payload)},
        ]

    def run_tool_calls(self, planned_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute planned tool calls."""
        results = []

        for call in planned_calls:
            result = self.tool_registry.run_tool(call["tool_name"], call["payload"])
            results.append(
                {
                    "tool_name": call["tool_name"],
                    "payload": call["payload"],
                    "result": result,
                }
            )

        return results

    async def call_evidence_validator(self, evidence_bundle: dict[str, Any]) -> dict[str, Any]:
        """Send evidence to validator agent via A2A protocol."""

        async def validation_handler(payload: dict[str, Any]) -> dict[str, Any]:
            """Adapt the validator result to the A2A dictionary contract."""
            validation_result = self.evidence_validator.validate(payload)
            return validation_result.model_dump()

        result = await send_task(
            from_agent="media_orchestrator",
            to_agent="evidence_validator",
            task_payload=evidence_bundle,
            handler=validation_handler,
        )

        if result.get("status") == "completed":
            return result.get("output", {})
        return {
            "overall_passed": False,
            "overall_confidence": 0.0,
            "requires_human_review": True,
            "review_reason": result.get("error", "Evidence validation failed"),
        }

    def apply_guardrails(self, candidate_clips: list[dict]) -> dict[str, Any]:
        """Apply guardrails to candidate clips."""
        from security.input_guard import InputGuard
        from security.output_guard import OutputGuard

        input_guard = InputGuard()
        output_guard = OutputGuard()

        passed_count = 0
        blocked_clips = []

        for clip in candidate_clips:
            if output_guard.is_safe(clip):
                passed_count += 1
            else:
                blocked_clips.append(clip["clip_id"])

        return {
            "total_clips": len(candidate_clips),
            "passed": passed_count,
            "blocked": blocked_clips,
            "block_reasons": ["content_filter", "pii_filter"] if blocked_clips else [],
        }

    async def run(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        max_results: int = 10,
        trace_id: str = "",
    ) -> dict[str, Any]:
        """Execute full orchestration."""
        start_time = time.time()

        logger.info("Orchestrator starting", query=query, trace_id=trace_id)

        state = MCIState(trace_id=trace_id, query=query)

        parsed_intent = self.parse_query(query)
        state.parsed_intent = parsed_intent

        rewritten = self.rewrite_query(query)
        state.rewritten_query = rewritten

        hyde = self.generate_hyde(query)
        state.hyde_query = hyde

        effective_filters = dict(parsed_intent.get("filters", {}))
        effective_filters.update(filters or {})
        retrieval_limit = max(max_results, 20)
        plan = self.plan_tool_calls(parsed_intent, effective_filters, retrieval_limit)
        state.planned_tool_calls = plan

        tool_results = self.run_tool_calls(plan)
        state.tool_results = tool_results

        all_results = []
        for tr in tool_results:
            if "results" in tr.get("result", {}):
                all_results.extend(tr["result"]["results"])

        result_sets = [
            tr["result"]
            for tr in tool_results
            if any(item.get("clip_id") for item in tr.get("result", {}).get("results", []))
        ]
        rrf_result = self.tool_registry.run_tool(
            "rrf_fusion",
            {"result_sets": result_sets, "k": 60, "top_k": retrieval_limit},
        )
        fused_results = rrf_result.get("results", [])

        clip_ids = [r["clip_id"] for r in fused_results[:retrieval_limit]]

        for i, clip_id in enumerate(clip_ids):
            clip_result = fused_results[i] if i < len(fused_results) else {}
            candidate = {
                "clip_id": clip_id,
                "video_id": clip_result["video_id"],
                "file_path": clip_result.get("file_path", ""),
                "start_time": clip_result.get("start_time", 0.0),
                "end_time": clip_result.get("end_time", 30.0),
                "score": clip_result.get("score", clip_result.get("rrf_score", 0.8)),
                "title": clip_result.get("title", ""),
                "description": clip_result.get("description", ""),
                "source": clip_result.get("source", ""),
                "source_url": clip_result.get("source_url", ""),
                "source_page": clip_result.get("source_page", ""),
                "asset_name": clip_result.get("asset_name", ""),
                "dataset": clip_result.get("dataset", ""),
                "content_type": clip_result.get("content_type", "video"),
                "mime_type": clip_result.get("mime_type"),
                "annotations": clip_result.get("annotations", {}),
                "relevance_reason": clip_result.get(
                    "relevance_reason", f"Matched query: {query[:50]}"
                ),
            }
            state.candidate_clips.append(candidate)

        evidence_bundle = {
            "clip_id": clip_ids[0] if clip_ids else "unknown",
            "query": query,
            "retrieved_evidence": {"results": fused_results},
            "visual_evidence": {
                "logos": [],
                "talent_matches": [],
                "explanation": "No visual model inference was run during metadata search",
            },
            "rights_evidence": {
                "rights_cleared": False,
                "explanation": "Review the source license annotation before use",
            },
        }
        state.evidence_bundle = evidence_bundle

        validation_result = await self.call_evidence_validator(evidence_bundle)
        state.validation_results = [validation_result]

        guardrail_results = self.apply_guardrails(state.candidate_clips)
        state.guardrail_results = guardrail_results

        final_clips = [c for c in state.candidate_clips if c["clip_id"] not in guardrail_results.get("blocked", [])]

        final_answer = f"Found {len(final_clips)} candidate clips matching: {query}"

        state.final_answer = final_answer
        state.human_review_required = validation_result.get("requires_human_review", False)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Orchestrator completed",
            trace_id=trace_id,
            candidates=len(state.candidate_clips),
            final=len(final_clips),
            duration_ms=round(duration_ms, 2),
        )

        return {
            "query": query,
            "rewritten_query": rewritten,
            "hyde_query": hyde,
            "candidate_clips": final_clips[:max_results],
            "total_found": len(final_clips),
            "validation": validation_result,
            "guardrails": guardrail_results,
            "human_review_required": state.human_review_required,
        }
