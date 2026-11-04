"""Public logging and metrics interface for MCI.

The package exposes the structured logger and Prometheus instruments used by
the runnable API. Experimental tracing and cost-accounting implementations are
kept outside the public runtime boundary.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

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
]
