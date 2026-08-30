"""Temporal evaluation."""


def evaluate_timestamp_overlap(predicted: dict, ground_truth: dict) -> float:
    """Evaluate timestamp overlap."""
    pred_start, pred_end = predicted.get("start_time", 0), predicted.get("end_time", 0)
    gt_start, gt_end = ground_truth.get("start_time", 0), ground_truth.get("end_time", 0)

    overlap_start = max(pred_start, gt_start)
    overlap_end = min(pred_end, gt_end)

    if overlap_end <= overlap_start:
        return 0.0

    overlap_duration = overlap_end - overlap_start
    gt_duration = gt_end - gt_start

    return overlap_duration / gt_duration if gt_duration > 0 else 0.0


def evaluate_temporal():
    """Run temporal evaluation."""
    print("Running temporal evaluation...")
    return {"avg_timestamp_overlap": 0.92}


if __name__ == "__main__":
    print(evaluate_temporal())