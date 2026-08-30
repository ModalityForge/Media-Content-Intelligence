"""Reciprocal Rank Fusion."""

from typing import Any


def rrf_fuse(result_sets: list[list[dict[str, Any]]], k: int = 60) -> list[dict[str, Any]]:
    """Fuse results using RRF."""
    scores: dict[str, float] = {}
    for results in result_sets:
        for rank, r in enumerate(results, 1):
            clip_id = r.get("clip_id", "")
            scores[clip_id] = scores.get(clip_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)