"""Observability module."""

from observability.logger import get_logger
from observability.metrics import (
    TASK_COUNT,
    TOOL_CALLS,
    TOOL_LATENCY,
    AGENT_STEPS,
    RETRIEVAL_RESULTS,
    VALIDATION_PASS_RATE,
    GUARDRAIL_BLOCKS,
    CACHE_HITS,
    CACHE_MISSES,
    ACTIVE_JOBS,
)
from observability.trace import trace, get_trace_id, create_trace_id

__all__ = [
    "get_logger",
    "TASK_COUNT",
    "TOOL_CALLS",
    "TOOL_LATENCY",
    "AGENT_STEPS",
    "RETRIEVAL_RESULTS",
    "VALIDATION_PASS_RATE",
    "GUARDRAIL_BLOCKS",
    "CACHE_HITS",
    "CACHE_MISSES",
    "ACTIVE_JOBS",
    "trace",
    "get_trace_id",
    "create_trace_id",
]