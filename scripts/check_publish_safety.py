#!/usr/bin/env python3
"""Reject unsafe artifacts before the public repository is published.

The command inspects Git-tracked paths—not merely working-tree files—and fails
when it finds dataset directories, media, archives, model artifacts, embeddings,
evaluation records, or files above the configured public size threshold.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_BYTES = 10 * 1024 * 1024

BANNED_PREFIXES = (
    "data/",
    "dataset/",
    "datasets/",
    "model/",
    "models/",
    "pretrained/",
    "pretrained_models/",
    "checkpoints/",
    "weights/",
    "embeddings/",
    "runs/",
    "wandb/",
    "mlruns/",
)
BANNED_PATHS = {"evaluation/golden_dataset.json"}
BANNED_SUFFIXES = {
    ".7z", ".arrow", ".avi", ".avro", ".bin", ".ckpt", ".csv",
    ".faiss", ".feather", ".flac", ".gz", ".h5", ".index",
    ".joblib", ".jsonl", ".keras", ".mkv", ".mlmodel", ".mov",
    ".mp3", ".mp4", ".npy", ".npz", ".onnx", ".parquet", ".pb",
    ".pickle", ".pkl", ".pt", ".pth", ".rar", ".safetensors",
    ".tar", ".tflite", ".tgz", ".tsv", ".wav", ".webm", ".zip",
}

# These paths are intentionally retained only in the author's local working
# copy. They contain broader research, ingestion, evaluation, and operational
# implementations that are not required by the reproducible public app.
LOCAL_ONLY_PREFIXES = (
    "api/middleware/",
    "components/",
    "docs/superpowers/",
    "evaluation/",
    "frontend/pages/",
    "prompts/",
    "streaming/",
)
LOCAL_ONLY_PATHS = {
    "CLAUDE.md",
    "agents/graph.py",
    "agents/prompts.py",
    "api/routes/alerts.py",
    "api/routes/clips.py",
    "api/routes/ingest.py",
    "app/models.py",
    "observability/cost_tracker.py",
    "observability/trace.py",
    "scripts/create_golden_dataset.py",
    "scripts/download_ad_datasets.py",
    "scripts/download_socmed_dataset.py",
    "scripts/index_archive.py",
    "scripts/migrate.py",
    "scripts/run_live_stream.py",
    "scripts/seed.py",
    "security/audit_logger.py",
    "security/content_filter.py",
    "security/pii_filter.py",
    "security/policy_rules.py",
    "services/alert_service.py",
    "services/brand_safety_service.py",
    "services/feedback_service.py",
    "services/notification_service.py",
    "services/rag_pipeline.py",
    "services/rights_service.py",
    "services/semantic_cache.py",
    "storage/metadata_db.py",
    "storage/object_store.py",
    "storage/redis_cache.py",
    "storage/vector_db.py",
    "tests/test_brand_safety.py",
    "tests/test_cache.py",
    "tests/test_ingestion.py",
    "tests/test_preprocessing.py",
    "tests/test_retrieval.py",
    "tests/test_rights.py",
    "tests/test_tools.py",
    "tools/audio_ocr_tools.py",
    "tools/output_tools.py",
    "tools/policy_tools.py",
    "tools/tool_schemas.py",
    "tools/vision_tools.py",
}


def tracked_files() -> list[str]:
    """Return every path recorded in the Git index using NUL-safe decoding."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def violations(paths: list[str]) -> list[str]:
    """Return human-readable publication-policy violations for tracked paths."""
    problems: list[str] = []
    for relative in paths:
        normalized = PurePosixPath(relative).as_posix()
        suffix = PurePosixPath(normalized).suffix.lower()
        if normalized in LOCAL_ONLY_PATHS or normalized.startswith(LOCAL_ONLY_PREFIXES):
            problems.append(f"local-only implementation is tracked: {normalized}")
        elif normalized in BANNED_PATHS:
            problems.append(f"dataset fixture is tracked: {normalized}")
        elif normalized.startswith(BANNED_PREFIXES):
            problems.append(f"banned artifact directory is tracked: {normalized}")
        elif suffix in BANNED_SUFFIXES:
            problems.append(f"banned artifact extension is tracked: {normalized}")

        local_path = PROJECT_ROOT / relative
        if local_path.is_file() and local_path.stat().st_size > MAX_TRACKED_BYTES:
            problems.append(f"tracked file exceeds 10 MiB: {normalized}")
    return problems


def main() -> int:
    """Print the safety verdict and return a shell-compatible process status."""
    problems = violations(tracked_files())
    if problems:
        print("Publication safety check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Publication safety check passed: code and documentation only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
