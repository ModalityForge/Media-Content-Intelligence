"""Policy rules for rights and content."""

from typing import Any


RIGHTS_RULES = {
    "germany_digital_highlights": {
        "max_duration_seconds": 30,
        "territories": ["Germany"],
        "usage_types": ["digital_highlights"],
    },
    "usa_digital_highlights": {
        "max_duration_seconds": 90,
        "territories": ["USA"],
        "usage_types": ["digital_highlights"],
    },
}

CONTENT_RULES = {
    "min_duration_seconds": 5,
    "max_duration_seconds": 3600,
}


class PolicyRules:
    """Policy rules engine."""

    @staticmethod
    def check_rights(territory: str, usage: str, duration: float) -> dict[str, Any]:
        """Check rights policy."""
        key = f"{territory.lower()}_{usage.lower()}"
        rule = RIGHTS_RULES.get(key)

        if not rule:
            return {"allowed": False, "reason": "No policy for territory/usage"}

        max_dur = rule.get("max_duration_seconds")
        if max_dur and duration > max_dur:
            return {"allowed": False, "reason": f"Duration {duration}s exceeds max {max_dur}s"}

        return {"allowed": True, "max_duration": max_dur}


policy_rules = PolicyRules()