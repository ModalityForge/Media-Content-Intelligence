"""Policy and rights MCP tools."""

import random
import uuid
from typing import Any

from tools.base import BaseMCPTool


class RightsCheckTool(BaseMCPTool):
    """Rights checking tool."""

    name = "rights_check"
    description = "Check rights clearance for clips"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "territory": {"type": "string", "description": "Target territory"},
            "usage_type": {"type": "string", "description": "Usage type"},
            "duration_seconds": {"type": "number", "description": "Clip duration"},
        },
        "required": ["clip_ids", "territory"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute rights check."""
        clip_ids = input_data.get("clip_ids", [])
        territory = input_data.get("territory", "")
        usage_type = input_data.get("usage_type", "digital_highlights")
        duration_seconds = input_data.get("duration_seconds", 30)

        results = []

        for clip_id in clip_ids:
            rights_cleared = True
            explanation = f"Rights cleared for {territory} {usage_type}"

            if territory.lower() == "germany":
                if duration_seconds > 30:
                    rights_cleared = False
                    explanation = "Germany digital highlights limited to 30 seconds"
                else:
                    rights_cleared = True
                    explanation = "Germany digital highlights allowed within 30s limit"

            if usage_type not in ["digital_highlights", "social_media", "broadcast"]:
                rights_cleared = False
                explanation = f"Usage type '{usage_type}' not authorized"

            results.append(
                {
                    "clip_id": clip_id,
                    "rights_cleared": rights_cleared,
                    "territory": territory,
                    "usage_type": usage_type,
                    "duration_seconds": duration_seconds,
                    "explanation": explanation,
                }
            )

        return {"results": results, "policy": "standard-rights"}


class SponsorshipPolicyTool(BaseMCPTool):
    """Sponsorship policy checking tool."""

    name = "sponsorship_policy"
    description = "Check sponsorship brand requirements"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "required_brands": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute sponsorship check."""
        clip_ids = input_data.get("clip_ids", [])
        required_brands = input_data.get("required_brands", [])

        results = []
        for clip_id in clip_ids:
            if required_brands:
                found_brands = random.sample(required_brands, random.randint(0, len(required_brands)))
                missing = [b for b in required_brands if b not in found_brands]
                passed = len(missing) == 0
                results.append(
                    {
                        "clip_id": clip_id,
                        "passed": passed,
                        "found_brands": found_brands,
                        "missing_brands": missing,
                    }
                )
            else:
                results.append(
                    {
                        "clip_id": clip_id,
                        "passed": True,
                        "found_brands": [],
                        "missing_brands": [],
                    }
                )

        return {"results": results}


class ExclusionCheckTool(BaseMCPTool):
    """Exclusion checking tool."""

    name = "exclusion_check"
    description = "Check for excluded brands/content"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "excluded_brands": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute exclusion check."""
        clip_ids = input_data.get("clip_ids", [])
        excluded_brands = input_data.get("excluded_brands", [])

        results = []
        for clip_id in clip_ids:
            found_excluded = []
            if excluded_brands and random.random() > 0.7:
                found_excluded = [random.choice(excluded_brands)]

            passed = len(found_excluded) == 0
            results.append(
                {
                    "clip_id": clip_id,
                    "passed": passed,
                    "found_excluded_brands": found_excluded,
                }
            )

        return {"results": results}


class ContentRatingTool(BaseMCPTool):
    """Content rating tool."""

    name = "content_rating"
    description = "Check content ratings"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "required_rating": {"type": "string"},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"results": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute content rating check."""
        clip_ids = input_data.get("clip_ids", [])
        required_rating = input_data.get("required_rating", "G")

        ratings = ["G", "PG", "PG-13", "R"]

        results = []
        for clip_id in clip_ids:
            rating = random.choice(ratings)
            rating_order = {"G": 0, "PG": 1, "PG-13": 2, "R": 3}
            passed = rating_order.get(rating, 3) <= rating_order.get(required_rating, 0)
            results.append(
                {
                    "clip_id": clip_id,
                    "rating": rating,
                    "passed": passed,
                }
            )

        return {"results": results}