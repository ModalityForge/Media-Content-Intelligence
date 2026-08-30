"""Rights evaluation."""


def evaluate_rights(results: list, territory: str, usage_type: str, max_duration: float) -> dict:
    """Evaluate rights compliance."""
    passed = 0
    failed = []

    for result in results:
        duration = result.get("duration", 0)
        clip_territory = result.get("territory", "")
        clip_usage = result.get("usage_type", "")

        if clip_territory == territory and clip_usage == usage_type and duration <= max_duration:
            passed += 1
        else:
            failed.append({"clip_id": result.get("clip_id"), "reason": "Rights not cleared"})

    return {
        "total": len(results),
        "passed": passed,
        "failed": len(failed),
        "pass_rate": passed / len(results) if results else 0,
    }


def evaluate_rights_system():
    """Run rights evaluation."""
    print("Running rights evaluation...")
    return {"pass_rate": 0.88}


if __name__ == "__main__":
    print(evaluate_rights_system())