#!/usr/bin/env python3
"""Reject tracked datasets, media, pretrained models, and large artifacts."""

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


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def violations(paths: list[str]) -> list[str]:
    problems: list[str] = []
    for relative in paths:
        normalized = PurePosixPath(relative).as_posix()
        suffix = PurePosixPath(normalized).suffix.lower()
        if normalized in BANNED_PATHS:
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
