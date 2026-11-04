"""Mutable execution state shared across one orchestrated search request.

The dataclass records every major stage—parsed intent, rewritten queries, tool
plans, evidence, candidates, validation, guardrails, and final output—so a
request can be inspected without relying on implicit global agent state.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCIState:
    """Media Content Intelligence state."""

    trace_id: str = ""
    query: str = ""
    rewritten_query: str = ""
    hyde_query: str | None = None
    parsed_intent: dict[str, Any] = field(default_factory=dict)
    candidate_clips: list[dict[str, Any]] = field(default_factory=list)
    planned_tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    evidence_bundle: dict[str, Any] | None = None
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    guardrail_results: dict[str, Any] = field(default_factory=dict)
    final_answer: str = ""
    human_review_required: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "rewritten_query": self.rewritten_query,
            "hyde_query": self.hyde_query,
            "parsed_intent": self.parsed_intent,
            "candidate_clips": self.candidate_clips,
            "planned_tool_calls": self.planned_tool_calls,
            "tool_results": self.tool_results,
            "evidence_bundle": self.evidence_bundle,
            "validation_results": self.validation_results,
            "guardrail_results": self.guardrail_results,
            "final_answer": self.final_answer,
            "human_review_required": self.human_review_required,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MCIState":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
