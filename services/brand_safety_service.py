"""Brand safety service."""

from typing import Any


DEFAULT_PROHIBITED_BRANDS = [
    "Nike",
    "Under Armour",
    "Reebok",
]

DEFAULT_EXCLUDED_CONTENT = [
    "violence",
    "nsfw",
    "controversial",
]


class BrandSafetyService:
    """Brand safety checking service."""

    def __init__(
        self,
        prohibited_brands: list[str] | None = None,
        excluded_content: list[str] | None = None,
    ):
        self.prohibited_brands = prohibited_brands or DEFAULT_PROHIBITED_BRANDS
        self.excluded_content = excluded_content or DEFAULT_EXCLUDED_CONTENT

    def check_brand_safety(
        self,
        clip_id: str,
        detected_brands: list[str],
        content_tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Check if a clip passes brand safety requirements."""
        found_prohibited = [b for b in detected_brands if b in self.prohibited_brands]

        if found_prohibited:
            return {
                "passed": False,
                "clip_id": clip_id,
                "reason": f"Prohibited brands found: {found_prohibited}",
                "prohibited_brands": found_prohibited,
            }

        if content_tags:
            found_excluded = [c for c in content_tags if c in self.excluded_content]
            if found_excluded:
                return {
                    "passed": False,
                    "clip_id": clip_id,
                    "reason": f"Excluded content found: {found_excluded}",
                    "excluded_content": found_excluded,
                }

        return {
            "passed": True,
            "clip_id": clip_id,
            "reason": "Brand safety check passed",
        }

    def check_required_brands(
        self,
        clip_id: str,
        required_brands: list[str],
        detected_brands: list[str],
    ) -> dict[str, Any]:
        """Check if required brands are present."""
        if not required_brands:
            return {"passed": True, "clip_id": clip_id, "reason": "No required brands"}

        missing = [b for b in required_brands if b not in detected_brands]

        if missing:
            return {
                "passed": False,
                "clip_id": clip_id,
                "reason": f"Required brands missing: {missing}",
                "missing_brands": missing,
            }

        return {
            "passed": True,
            "clip_id": clip_id,
            "reason": f"All required brands present: {required_brands}",
        }

    def check_excluded_brands(
        self,
        clip_id: str,
        excluded_brands: list[str],
        detected_brands: list[str],
    ) -> dict[str, Any]:
        """Check if excluded brands are absent."""
        if not excluded_brands:
            return {"passed": True, "clip_id": clip_id, "reason": "No excluded brands"}

        found = [b for b in excluded_brands if b in detected_brands]

        if found:
            return {
                "passed": False,
                "clip_id": clip_id,
                "reason": f"Excluded brands found: {found}",
                "found_brands": found,
            }

        return {
            "passed": True,
            "clip_id": clip_id,
            "reason": f"No excluded brands present: {excluded_brands}",
        }


brand_safety_service = BrandSafetyService()