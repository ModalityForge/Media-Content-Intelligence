"""Evidence Validator Agent."""

import re
from typing import Any

from app.schemas import EvidenceValidationResult, ValidationResultItem
from observability.logger import get_logger

logger = get_logger(__name__)


class EvidenceValidatorAgent:
    """Validates evidence for clips."""

    def __init__(self):
        self.name = "evidence_validator"

    def validate(
        self,
        evidence_bundle: dict[str, Any],
        validation_criteria: list[str] | None = None,
    ) -> EvidenceValidationResult:
        """Validate evidence bundle."""
        clip_id = evidence_bundle.get("clip_id", "unknown")
        query = evidence_bundle.get("query", "")
        criteria = validation_criteria or []

        logger.info("Validating evidence", clip_id=clip_id, criteria=criteria)

        results = []

        talent_required = any(
            t in query.lower() for t in ["messi", "ronaldo", "talent", "player", "athlete"]
        )
        action_required = any(
            a in query.lower()
            for a in ["drinking", "celebrating", "scoring", "running", "action"]
        )
        required_brands = re.findall(
            r"\b(adidas|pepsi|coca-cola|coke|apple|samsung)\b",
            query,
            re.IGNORECASE,
        )
        brand_required = bool(required_brands)
        excluded_brand = "nike" in query.lower()

        if "talent_present" in criteria or talent_required:
            visual = evidence_bundle.get("visual_evidence", {})
            talent_matches = visual.get("talent_matches", [])
            passed = bool(talent_matches)
            results.append(
                ValidationResultItem(
                    criterion="talent_present",
                    passed=passed,
                    confidence=0.85 if passed else 0.0,
                    reason=(
                        f"Talent detected: {len(talent_matches)} matches"
                        if passed
                        else "No verified talent evidence"
                    ),
                )
            )

        if "action_detected" in criteria or action_required:
            visual = evidence_bundle.get("visual_evidence", {})
            actions = visual.get("actions", [])
            passed = bool(actions)
            results.append(
                ValidationResultItem(
                    criterion="action_detected",
                    passed=passed,
                    confidence=0.8 if passed else 0.0,
                    reason=f"Action classified: {actions}" if passed else "No verified action evidence",
                )
            )

        if "required_brands_visible" in criteria or brand_required:
            visual = evidence_bundle.get("visual_evidence", {})
            logos = visual.get("logos", [])
            expected = [brand.lower() for brand in required_brands]
            detected = [str(logo).lower() for logo in logos]
            passed = (
                any(brand in logo for brand in expected for logo in detected)
                if expected
                else bool(detected)
            )
            results.append(
                ValidationResultItem(
                    criterion="required_brands_visible",
                    passed=passed,
                    confidence=0.9 if passed else 0.0,
                    reason=(
                        "Required brand detected"
                        if passed
                        else "No verified evidence for the required brand"
                    ),
                )
            )

        if "excluded_brands_absent" in criteria or excluded_brand:
            visual = evidence_bundle.get("visual_evidence", {})
            logos = visual.get("logos", [])
            passed = not any("nike" in str(l).lower() for l in logos)
            results.append(
                ValidationResultItem(
                    criterion="excluded_brands_absent",
                    passed=passed,
                    confidence=0.9,
                    reason="Excluded brand not present" if passed else "Excluded brand detected",
                )
            )

        rights = evidence_bundle.get("rights_evidence", {})
        rights_cleared = rights.get("rights_cleared", False)
        results.append(
            ValidationResultItem(
                criterion="rights_cleared",
                passed=rights_cleared,
                confidence=0.95,
                reason=rights.get("explanation", "Rights check completed"),
            )
        )
        overall_passed = all(result.passed for result in results)
        overall_confidence = (
            sum(result.confidence for result in results) / len(results) if results else 0.0
        )

        human_review = self.requires_human_review(
            EvidenceValidationResult(
                clip_id=clip_id,
                overall_passed=overall_passed,
                overall_confidence=overall_confidence,
                results=results,
            )
        )

        return EvidenceValidationResult(
            clip_id=clip_id,
            overall_passed=overall_passed,
            overall_confidence=overall_confidence,
            results=results,
            requires_human_review=human_review,
            review_reason="Low confidence or failed critical criteria" if human_review else None,
        )

    def score_clip(self, candidate: dict[str, Any]) -> float:
        """Score a candidate clip."""
        base_score = candidate.get("score", 0.5)
        evidence = candidate.get("evidence", {})

        talent_bonus = 0.1 if evidence.get("has_talent") else 0
        action_bonus = 0.1 if evidence.get("has_action") else 0
        rights_bonus = 0.15 if evidence.get("rights_cleared") else -0.2

        return min(1.0, base_score + talent_bonus + action_bonus + rights_bonus)

    def requires_human_review(self, result: EvidenceValidationResult) -> bool:
        """Determine if human review is needed."""
        if result.overall_confidence < 0.7:
            return True

        if any(not item.passed for item in result.results):
            return True

        return False
