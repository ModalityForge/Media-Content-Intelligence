"""Verify local media discovery, metadata extraction, and catalog search.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import pytest

from storage.video_catalog import VideoCatalog


def test_catalog_discovers_user_supplied_media_recursively(tmp_path):
    """A fresh user can add smoke media anywhere below the configured data root."""
    isolated_root = tmp_path / "isolated-user-data"
    smoke_dir = isolated_root / "raw" / "smoke"
    smoke_dir.mkdir(parents=True)
    media_path = smoke_dir / "coffee-commercial.mp4"
    media_path.write_bytes(b"synthetic test bytes")

    local_catalog = VideoCatalog(
        base_dir=str(isolated_root),
        social_media_dir=str(tmp_path / "missing-social-root"),
    )

    results = local_catalog.search("coffee commercials", top_k=5)
    assert len(results) == 1
    assert results[0]["file_path"] == str(media_path.resolve())


def test_catalog_indexes_local_videos(smoke_catalog):
    """The catalog should index playable local media."""
    assert len(smoke_catalog.records) > 0
    assert any(r.is_playable() for r in smoke_catalog.records)


def test_catalog_search_returns_query_relevant_results(smoke_catalog):
    """BM25 search should return deterministic, query-relevant results."""
    results = smoke_catalog.search("coffee", top_k=5)
    assert len(results) > 0
    assert "coffee" in results[0]["title"].lower()
    assert all(r["video_id"] for r in results)
    assert all(r["file_path"] for r in results)
    assert len({r["title"] for r in results}) == len(results)
    assert len({r["source_url"] for r in results}) == len(results)


def test_catalog_search_is_deterministic(smoke_catalog):
    """Same query must return the same ranked result set."""
    a = [r["clip_id"] for r in smoke_catalog.search("insurance", top_k=10)]
    b = [r["clip_id"] for r in smoke_catalog.search("insurance", top_k=10)]
    assert a == b


def test_catalog_search_no_match_returns_empty(smoke_catalog):
    """A query with no matching content returns no results (not random junk)."""
    assert smoke_catalog.search("zzzxqqqqww", top_k=5) == []


def test_catalog_rejects_generic_false_positives(smoke_catalog):
    """A generic word such as commercial must not pull unrelated ads."""
    results = smoke_catalog.search("insurance commercial", top_k=10)
    assert results
    assert all("insurance" in result["title"].lower() for result in results)


def test_catalog_indexes_social_annotations_and_exact_files(smoke_catalog):
    """Social search should use annotations and retain the exact playable file."""
    results = smoke_catalog.search("LeBron guard Steph", top_k=5)
    assert results
    assert results[0]["dataset"] == "snapugc"
    assert smoke_catalog.get(results[0]["video_id"]).file_path == results[0]["file_path"]


def test_advertisement_query_does_not_return_general_social_video(smoke_catalog):
    """Advertisement intent prevents unrelated social content from leaking in."""
    results = smoke_catalog.search("Samsung advertisement", top_k=10)
    assert results
    assert all(result["content_type"] == "advertisement" for result in results)


def test_duration_words_do_not_block_relevant_results(smoke_catalog):
    """Duration phrasing acts as a filter without becoming a required text token."""
    results = smoke_catalog.search(
        "30-second coffee commercials",
        top_k=10,
        filters={"max_duration": 30},
    )
    assert results
    assert all("coffee" in result["title"].lower() for result in results)
