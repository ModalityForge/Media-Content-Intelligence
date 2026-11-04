"""Prometheus instruments describing the public MCI execution path.

Counters, histograms, and gauges capture agent tasks, tool calls, retrieval,
validation, guardrails, cache behaviour, and active work. Application startup
invokes :func:`init_metrics` as an explicit extension hook.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from prometheus_client import Counter, Histogram, Gauge

TASK_COUNT = Counter(
    "mci_tasks_total", "Total tasks processed", ["task_type", "status"]
)

TOOL_CALLS = Counter(
    "mci_tool_calls_total", "Total tool calls", ["tool_name", "status"]
)

TOOL_LATENCY = Histogram(
    "mci_tool_latency_seconds", "Tool call latency", ["tool_name"]
)

AGENT_STEPS = Counter(
    "mci_agent_steps_total", "Agent orchestration steps", ["agent_name", "step"]
)

RETRIEVAL_RESULTS = Histogram(
    "mci_retrieval_results", "Retrieval results count", ["retriever_type"]
)

VALIDATION_PASS_RATE = Histogram(
    "mci_validation_pass_rate", "Validation pass rate", ["validation_type"]
)

GUARDRAIL_BLOCKS = Counter(
    "mci_guardrail_blocks_total", "Guardrail blocks", ["guardrail_type", "reason"]
)

CACHE_HITS = Counter(
    "mci_cache_hits_total", "Cache hits", ["cache_type"]
)

CACHE_MISSES = Counter(
    "mci_cache_misses_total", "Cache misses", ["cache_type"]
)

ACTIVE_JOBS = Gauge(
    "mci_active_jobs", "Active ingestion jobs"
)

def init_metrics():
    """Provide an explicit, idempotent application-startup metrics hook."""
    pass
