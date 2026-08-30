"""Cost tracking for API calls."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CostRecord:
    """Record of API call cost."""

    trace_id: str
    operation: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class CostTracker:
    """Track costs of API calls."""

    def __init__(self):
        self.records: list[CostRecord] = []
        self._total_cost = 0.0
        self._total_tokens = 0

    def record(
        self,
        trace_id: str,
        operation: str,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        model: str = "",
    ) -> CostRecord:
        """Record a cost."""
        record = CostRecord(
            trace_id=trace_id,
            operation=operation,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            model=model,
        )
        self.records.append(record)
        self._total_cost += cost_usd
        self._total_tokens += tokens_used
        return record

    def get_total_cost(self) -> float:
        """Get total cost."""
        return self._total_cost

    def get_total_tokens(self) -> int:
        """Get total tokens."""
        return self._total_tokens

    def get_trace_costs(self, trace_id: str) -> list[CostRecord]:
        """Get costs for a specific trace."""
        return [r for r in self.records if r.trace_id == trace_id]


cost_tracker = CostTracker()