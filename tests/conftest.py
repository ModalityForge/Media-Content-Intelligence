"""Create an isolated, licence-free smoke catalog for the public test suite.

The fixture writes a few byte-level placeholder files at test time, so a fresh
clone can verify search and byte-range delivery without committing media or
depending on the author's local datasets.

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from __future__ import annotations

import json

import pytest

import api.routes.videos as video_routes
import storage.video_catalog as video_catalog_module
import tools.retrieval_tools as retrieval_tools
from storage.video_catalog import VideoCatalog


@pytest.fixture(autouse=True)
def smoke_catalog(tmp_path, monkeypatch) -> VideoCatalog:
    """Build and inject a temporary catalog for every public contract test."""
    ad_dir = tmp_path / "data" / "raw" / "ad_subset"
    ad_dir.mkdir(parents=True)
    manifest_rows = []
    for sequence, title, duration in (
        (1, "Coffee Commercial", 20.0),
        (2, "Insurance Commercial", 25.0),
        (3, "Samsung Advertisement", 15.0),
    ):
        media_path = ad_dir / f"{sequence:03d}_{title.lower().replace(' ', '_')}.mp4"
        media_path.write_bytes((title.encode("utf-8") + b"\0") * 16)
        manifest_rows.append(
            {
                "source": "synthetic_public_test",
                "source_id": str(sequence),
                "title": title,
                "local_path": str(media_path),
                "duration_seconds": duration,
                "mime_type": "video/mp4",
                "license_name": "generated-test-fixture",
            }
        )
    (ad_dir / "manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in manifest_rows),
        encoding="utf-8",
    )

    social_dir = tmp_path / "data" / "restricted" / "social_media_influencer"
    dataset_dir = social_dir / "datasets" / "snapugc"
    social_video = dataset_dir / "raw" / "videos" / "lebron-guard-steph.mp4"
    social_video.parent.mkdir(parents=True)
    social_video.write_bytes((b"synthetic social test video\0") * 8)
    (dataset_dir / "annotations_index.json").write_text(
        json.dumps(
            {
                "dataset": "snapugc",
                "items": [
                    {
                        "video_id": "lebron-guard-steph",
                        "file": "raw/videos/lebron-guard-steph.mp4",
                        "title": "LeBron guard Steph social video",
                        "split": "test",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    catalog = VideoCatalog(base_dir=str(ad_dir.parent), social_media_dir=str(social_dir))
    monkeypatch.setattr(video_catalog_module, "catalog", catalog)
    monkeypatch.setattr(retrieval_tools, "catalog", catalog)
    monkeypatch.setattr(video_routes, "catalog", catalog)
    return catalog
