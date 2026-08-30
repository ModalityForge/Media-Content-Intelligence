"""Retrieval tests."""

import pytest
from components.retrieval.rrf import rrf_fuse


def test_rrf_fuse():
    """Test RRF fusion."""
    result_sets = [
        [{"clip_id": "clip-1", "score": 0.9}, {"clip_id": "clip-2", "score": 0.8}],
        [{"clip_id": "clip-2", "score": 0.7}, {"clip_id": "clip-3", "score": 0.6}],
    ]
    fused = rrf_fuse(result_sets, k=60)
    assert len(fused) > 0
    clip_ids = [c[0] for c in fused]
    assert "clip-2" in clip_ids


def test_hyde_generator():
    """Test HyDE generator."""
    from services.hyde_generator import generate_hyde

    hyde = generate_hyde("Find Messi drinking Pepsi")
    assert len(hyde) > 0
    assert "video" in hyde.lower()


def test_query_rewriter():
    """Test query rewriter."""
    from services.query_rewriter import rewrite_query

    rewritten = rewrite_query("Find Messi drinking Pepsi")
    assert "Messi" in rewritten
    assert "football" in rewritten.lower()