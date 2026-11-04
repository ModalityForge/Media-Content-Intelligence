"""Verify local media discovery, metadata extraction, and catalog search.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import pytest

from storage.video_catalog import catalog


def test_catalog_indexes_local_videos():
    """The catalog should index playable local media."""
    assert len(catalog.records) > 0
    assert any(r.is_playable() for r in catalog.records)


def test_catalog_search_returns_query_relevant_results():
    """BM25 search should return deterministic, query-relevant results."""
    results = catalog.search("coffee", top_k=5)
    assert len(results) > 0
    assert "coffee" in results[0]["title"].lower()
    assert all(r["video_id"] for r in results)
    assert all(r["file_path"] for r in results)
    assert len({r["title"] for r in results}) == len(results)
    assert len({r["source_url"] for r in results}) == len(results)


def test_catalog_search_is_deterministic():
    """Same query must return the same ranked result set."""
    a = [r["clip_id"] for r in catalog.search("insurance", top_k=10)]
    b = [r["clip_id"] for r in catalog.search("insurance", top_k=10)]
    assert a == b


def test_catalog_search_no_match_returns_empty():
    """A query with no matching content returns no results (not random junk)."""
    assert catalog.search("zzzxqqqqww", top_k=5) == []


def test_catalog_rejects_generic_false_positives():
    """A generic word such as commercial must not pull unrelated ads."""
    results = catalog.search("insurance commercial", top_k=10)
    assert results
    assert all("insurance" in result["title"].lower() for result in results)


def test_catalog_indexes_social_annotations_and_exact_files():
    """Social search should use annotations and retain the exact playable file."""
    results = catalog.search("LeBron guard Steph", top_k=5)
    assert results
    assert results[0]["dataset"] == "snapugc"
    assert catalog.get(results[0]["video_id"]).file_path == results[0]["file_path"]


def test_advertisement_query_does_not_return_general_social_video():
    results = catalog.search("Samsung advertisement", top_k=10)
    assert results
    assert all(result["content_type"] == "advertisement" for result in results)


def test_duration_words_do_not_block_relevant_results():
    results = catalog.search(
        "30-second coffee commercials",
        top_k=10,
        filters={"max_duration": 30},
    )
    assert results
    assert all("coffee" in result["title"].lower() for result in results)
