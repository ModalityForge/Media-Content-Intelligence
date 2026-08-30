"""Rights service for policy checking."""

from typing import Any

from app.config import settings


TERRITORY_POLICIES = {
    "germany": {
        "digital_highlights": {"max_duration_seconds": 30, "allowed": True},
        "social_media": {"max_duration_seconds": 60, "allowed": True},
        "broadcast": {"max_duration_seconds": None, "allowed": True},
    },
    "usa": {
        "digital_highlights": {"max_duration_seconds": 90, "allowed": True},
        "social_media": {"max_duration_seconds": 120, "allowed": True},
        "broadcast": {"max_duration_seconds": None, "allowed": True},
    },
    "uk": {
        "digital_highlights": {"max_duration_seconds": 30, "allowed": True},
        "social_media": {"max_duration_seconds": 60, "allowed": True},
        "broadcast": {"max_duration_seconds": None, "allowed": True},
    },
}


def check_territory_rights(
    territory: str,
    usage_type: str,
    duration_seconds: float,
) -> dict[str, Any]:
    """Check rights for a territory/usage/duration combination."""
    territory_lower = territory.lower()
    usage_lower = usage_type.lower().replace(" ", "_")

    if territory_lower not in TERRITORY_POLICIES:
        return {
            "rights_cleared": False,
            "explanation": f"Territory '{territory}' not supported",
        }

    policy = TERRITORY_POLICIES[territory_lower]

    if usage_lower not in policy:
        return {
            "rights_cleared": False,
            "explanation": f"Usage type '{usage_type}' not supported for {territory}",
        }

    usage_policy = policy[usage_lower]

    if not usage_policy.get("allowed", False):
        return {
            "rights_cleared": False,
            "explanation": f"Usage type '{usage_type}' not allowed for {territory}",
        }

    max_duration = usage_policy.get("max_duration_seconds")
    if max_duration and duration_seconds > max_duration:
        return {
            "rights_cleared": False,
            "explanation": f"Duration {duration_seconds}s exceeds max {max_duration}s for {territory} {usage_type}",
        }

    return {
        "rights_cleared": True,
        "territory": territory,
        "usage_type": usage_type,
        "max_duration_seconds": max_duration,
        "explanation": f"Rights cleared for {territory} {usage_type}" + (f" (max {max_duration}s)" if max_duration else ""),
    }


def get_allowed_territories() -> list[str]:
    """Get list of allowed territories."""
    return list(TERRITORY_POLICIES.keys())


def get_allowed_usage_types(territory: str) -> list[str]:
    """Get allowed usage types for a territory."""
    if territory.lower() in TERRITORY_POLICIES:
        return list(TERRITORY_POLICIES[territory.lower()].keys())
    return []