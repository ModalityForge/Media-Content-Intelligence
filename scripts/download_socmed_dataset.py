#!/usr/bin/env python3
"""
download_socmed_dataset.py
==========================
Revision of download_ad_datasets.py for SOCIAL-MEDIA INFLUENCER / UGC
short-video datasets annotated with virality & engagement metrics
(views, likes, shares, collects, followers/fans, comments, watch-based
engagement), downloaded under a strict acquisition size budget (default
450 MiB) into an isolated, research-only project folder.

Datasets
--------
  AUTOMATED:
    microlens      MicroLens-50k / 100k (Westlake). Range-enabled split ZIPs
                   plus per-video likes/views, titles, and interactions.
                   The script reads the remote ZIP index and fetches only the
                   selected MP4 byte ranges under the size budget.
    snapugc       Official train/validation annotation CSVs plus a capped
                  sample of still-live Snapchat CDN videos. Train items have
                  ECR, title, and description annotations.

  MANUAL-DROP (place archive in <root>/manual_drop/, re-run to index):
    xsvideo        XS-Video / SPIR: views, likes, shares, collects, fans,
                   comments + 0-9 propagation influence rating.

Output layout
-------------
  <root>/
    catalog.json
    manual_drop/
    datasets/<name>/
      raw/                        media + metric files
      virality_metrics.csv       one row per downloaded video, joined metrics
      annotations_index.json     machine-readable per-item records
      annotation_assets.json     downloaded annotation-file inventory
      DATASET_INFO.md

Usage
-----
  pip install requests tqdm
  python scripts/download_socmed_dataset.py --datasets microlens \
         --size-budget-mb 450 --max-videos 100 --accept-research-terms

Legal / ethical notes (read me)
-------------------------------
* This script deliberately does NOT scrape TikTok/Instagram/YouTube live:
  that violates platform ToS and collects non-consented personal data.
  It uses published research datasets with anonymized user identifiers.
* All three datasets are RESEARCH-USE releases. Do not redistribute the
  media; keep the per-item metric files as your audit trail.
* Engagement metrics are snapshots from the collection window, not live.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("pip install requests tqdm"); sys.exit(1)
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kw): return x


MB = 1024 * 1024
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = PROJECT_ROOT / "data" / "restricted" / "social_media_influencer"

# ---------------------------------------------------------------------------
# MicroLens configuration
# ---------------------------------------------------------------------------
# Open directory published by the authors (see repo Downloader/quick_download):
#   wget -r -np -nH --cut-dirs=3 https://recsys.westlake.edu.cn/MicroLens-50k-Dataset/
MICROLENS_BASES = {
    "50k": "https://recsys.westlake.edu.cn/MicroLens-50k-Dataset/",
    "100k": "https://recsys.westlake.edu.cn/MicroLens-100k-Dataset/",
}
MICROLENS_ARCHIVES = {
    "50k": {"prefix": "MicroLens-50k_videos", "last_disk": 216},
    "100k": {"prefix": "MicroLens-100k_videos", "last_disk": 222},
}
MICROLENS_METADATA = {
    "50k": [
        "MicroLens-50k_likes_and_views.txt",
        "MicroLens-50k_titles.csv",
        "readme.txt",
    ],
    "100k": [
        "MicroLens-100k_likes_and_views.txt",
        "MicroLens-100k_title_en.csv",
        "MicroLens-100k_comment_en.txt",
        "tags_to_summary.csv",
        "readme.txt",
    ],
}
MICROLENS_INTERACTIONS = {
    "50k": "MicroLens-50k_pairs.tsv",
    "100k": "MicroLens-100k_pairs.tsv",
}
SNAPUGC_ANNOTATION_URLS = {
    "train": ("https://drive.usercontent.google.com/download?"
              "id=1Mv5Esq5gGuxRTayabRUb5NmHwEN3JdbD&export=download&confirm=t"),
    "val": ("https://drive.usercontent.google.com/download?"
            "id=1iY7qUfqivYzUqUID501dKQDpI3NQil7y&export=download&confirm=t"),
}
# Metric files the authors ship (likes/views per video). We match by pattern
# so filename tweaks upstream don't break us.
METRIC_FILE_PAT = re.compile(r"likes?_and_views?.*\.txt$", re.I)
VIDEO_EXT = (".mp4", ".webm", ".mkv", ".avi")
META_EXT = (".txt", ".csv", ".tsv", ".json")


@dataclass(frozen=True)
class RemoteZipEntry:
    name: str
    name_size: int
    disk: int
    local_offset: int
    compressed_size: int
    size: int
    compression: int
    flags: int
    crc32: int


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Tiny HTML index parser (for Apache/Nginx-style directory listings)
# ---------------------------------------------------------------------------
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for k, v in attrs:
                if k.lower() == "href" and v and not v.startswith(("?", "#")):
                    self.hrefs.append(v)


def crawl_index(base_url: str, session: requests.Session,
                max_depth: int = 3) -> list[str]:
    """Recursively list file URLs under an open HTTP directory."""
    seen_dirs, files = set(), []
    stack = [(base_url, 0)]
    base_host = urlparse(base_url).netloc
    while stack:
        url, depth = stack.pop()
        if url in seen_dirs or depth > max_depth:
            continue
        seen_dirs.add(url)
        try:
            r = session.get(url, timeout=60)
            r.raise_for_status()
        except Exception as e:  # noqa: BLE001
            print(f"  [!] index fetch failed {url}: {e}")
            continue
        p = LinkParser(); p.feed(r.text)
        for href in p.hrefs:
            full = urljoin(url, href)
            if urlparse(full).netloc != base_host:
                continue
            if not full.startswith(base_url):
                continue  # don't escape the dataset root (e.g. parent links)
            if full.endswith("/"):
                stack.append((full, depth + 1))
            else:
                files.append(full)
    return sorted(set(files))


def head_size(url: str, session: requests.Session) -> Optional[int]:
    try:
        r = session.head(url, timeout=30, allow_redirects=True)
        cl = r.headers.get("content-length")
        if r.ok and cl:
            return int(cl)
    except Exception:  # noqa: BLE001
        pass
    try:
        r = session.get(url, headers={"Range": "bytes=0-0"}, timeout=30)
        match = re.search(r"/(\d+)$", r.headers.get("content-range", ""))
        return int(match.group(1)) if r.status_code == 206 and match else None
    except Exception:  # noqa: BLE001
        return None


def fetch_range(url: str, byte_range: str,
                session: requests.Session) -> tuple[bytes, Optional[int]]:
    """Fetch one HTTP byte range and return payload plus total object size."""
    r = session.get(url, headers={"Range": f"bytes={byte_range}"}, timeout=120)
    r.raise_for_status()
    if r.status_code != 206:
        raise RuntimeError(f"server ignored byte range for {url}")
    match = re.search(r"/(\d+)$", r.headers.get("content-range", ""))
    return r.content, (int(match.group(1)) if match else None)


def remote_zip_index(base: str, variant: str,
                     session: requests.Session) -> tuple[list[RemoteZipEntry], str]:
    """Read the central directory of the authors' split ZIP via HTTP ranges."""
    config = MICROLENS_ARCHIVES[variant]
    archive_url = urljoin(base, f"{config['prefix']}.zip")
    tail, total_size = fetch_range(archive_url, "-131072", session)
    eocd_at = tail.rfind(b"PK\x05\x06")
    if eocd_at < 0:
        raise RuntimeError("ZIP end-of-central-directory record not found")
    (_, disk_no, cd_disk, _, total_entries, cd_size, cd_offset,
     _) = struct.unpack_from("<4s4H2LH", tail, eocd_at)
    if disk_no != config["last_disk"] or cd_disk != disk_no:
        raise RuntimeError("unexpected split-ZIP disk layout")
    if total_size is None or cd_offset + cd_size > total_size:
        raise RuntimeError("invalid remote ZIP central-directory bounds")
    directory, _ = fetch_range(
        archive_url, f"{cd_offset}-{cd_offset + cd_size - 1}", session)
    entries: list[RemoteZipEntry] = []
    pos = 0
    header = struct.Struct("<4s6H3L5H2L")
    while pos + header.size <= len(directory):
        values = header.unpack_from(directory, pos)
        if values[0] != b"PK\x01\x02":
            break
        (_, _, _, flags, compression, _, _, crc32, compressed_size, size,
         name_len, extra_len, comment_len, disk, _, _, local_offset) = values
        start = pos + header.size
        name_raw = directory[start:start + name_len]
        encoding = "utf-8" if flags & 0x800 else "cp437"
        name = name_raw.decode(encoding, errors="replace")
        entries.append(RemoteZipEntry(
            name=name, name_size=name_len, disk=disk, local_offset=local_offset,
            compressed_size=compressed_size, size=size,
            compression=compression, flags=flags, crc32=crc32,
        ))
        pos = start + name_len + extra_len + comment_len
    if len(entries) != total_entries:
        raise RuntimeError(
            f"parsed {len(entries)} of {total_entries} ZIP members")
    return entries, archive_url


def split_disk_url(base: str, variant: str, disk: int) -> str:
    config = MICROLENS_ARCHIVES[variant]
    prefix = config["prefix"]
    suffix = ".zip" if disk == config["last_disk"] else f".z{disk + 1:02d}"
    return urljoin(base, prefix + suffix)


def download_remote_zip_member(entry: RemoteZipEntry, base: str, variant: str,
                               dest: Path, session: requests.Session) -> int:
    """Download and verify one member from a range-enabled split ZIP."""
    if entry.flags & 0x1:
        raise RuntimeError("encrypted ZIP member is unsupported")
    disk_url = split_disk_url(base, variant, entry.disk)
    # The local extra field is an unsigned 16-bit length. Fetching its maximum
    # possible size together with the payload avoids a second high-latency
    # request for every member while adding at most 64 KiB of transfer.
    request_end = (entry.local_offset + 30 + entry.name_size + 65535
                   + entry.compressed_size - 1)
    member_bytes, _ = fetch_range(
        disk_url, f"{entry.local_offset}-{request_end}", session)
    local_header = member_bytes[:30]
    if len(local_header) != 30 or local_header[:4] != b"PK\x03\x04":
        raise RuntimeError("invalid local ZIP header")
    values = struct.unpack("<4s5H3L2H", local_header)
    name_len, extra_len = values[-2:]
    payload_start = 30 + name_len + extra_len
    payload = member_bytes[payload_start:payload_start + entry.compressed_size]
    if len(payload) != entry.compressed_size:
        raise RuntimeError("short ZIP member payload")
    if entry.compression == 0:
        content = payload
    elif entry.compression == 8:
        content = zlib.decompress(payload, -zlib.MAX_WBITS)
    else:
        raise RuntimeError(f"unsupported ZIP compression: {entry.compression}")
    if len(content) != entry.size:
        raise RuntimeError("ZIP member size mismatch")
    if zlib.crc32(content) & 0xFFFFFFFF != entry.crc32:
        raise RuntimeError("ZIP member CRC mismatch")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    tmp.write_bytes(content)
    tmp.replace(dest)
    return len(content)


def stream_download(url: str, dest: Path, session: requests.Session,
                    budget_left: int) -> int:
    """Download url -> dest; abort (and delete) if it exceeds budget_left.
    Returns bytes written (0 on skip/failure)."""
    if dest.exists() and dest.stat().st_size > 0:
        size = dest.stat().st_size
        if size > budget_left:
            print(f"  [!] existing file is outside remaining budget: {dest.name}")
            return 0
        return size
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    written = 0
    try:
        with session.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(chunk_size=MB):
                    written += len(chunk)
                    if written > budget_left:
                        raise RuntimeError("budget exceeded mid-file")
                    f.write(chunk)
        tmp.rename(dest)
        return written
    except Exception as e:  # noqa: BLE001
        if tmp.exists():
            tmp.unlink()
        print(f"  [!] skipped {dest.name}: {e}")
        return 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(MB), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_duration(path: Path) -> Optional[float]:
    """Return media duration in seconds when ffprobe is available."""
    if not shutil.which("ffprobe"):
        return None


def looks_like_video(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            header = f.read(32)
    except OSError:
        return False
    return b"ftyp" in header or header.startswith(b"\x1aE\xdf\xa3")
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            check=True, capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _safe_target(root: Path, member_name: str) -> Path:
    """Resolve an archive member and reject paths outside extraction root."""
    root_resolved = root.resolve()
    target = (root / member_name).resolve()
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError(f"unsafe archive member path: {member_name}")
    return target


def safe_extract_archive(archive: Path, dest: Path, max_bytes: int) -> int:
    """Extract regular files only, with traversal and expansion limits."""
    dest.mkdir(parents=True, exist_ok=True)
    extracted = 0
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            members = [m for m in z.infolist() if not m.is_dir()]
            if sum(m.file_size for m in members) > max_bytes:
                raise ValueError("archive expands beyond the configured budget")
            for member in members:
                _safe_target(dest, member.filename)
                # Unix symlinks are encoded in the upper mode bits.
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f"archive symlink rejected: {member.filename}")
                z.extract(member, dest)
                extracted += member.file_size
        return extracted
    if tarfile.is_tarfile(archive):
        with tarfile.open(archive) as t:
            members = [m for m in t.getmembers() if m.isfile()]
            if sum(m.size for m in members) > max_bytes:
                raise ValueError("archive expands beyond the configured budget")
            for member in t.getmembers():
                _safe_target(dest, member.name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f"non-regular archive member rejected: {member.name}")
            for member in members:
                t.extract(member, dest)
                extracted += member.size
        return extracted
    raise ValueError(f"unsupported archive type: {archive.name}")


# ---------------------------------------------------------------------------
# Metrics parsing / joining
# ---------------------------------------------------------------------------
def parse_metric_file(path: Path) -> dict[str, dict]:
    """Parse a likes_and_views-style txt/csv into {video_id: {metric: value}}.
    Tolerant to comma/tab/space delimiters and to a header row."""
    metrics: dict[str, dict] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return metrics
    if not lines:
        return metrics
    delim = "\t" if "\t" in lines[0] else ("," if "," in lines[0] else None)
    header: Optional[list[str]] = None
    first = lines[0].split(delim) if delim else lines[0].split()
    if any(not tok.replace(".", "").isdigit() for tok in first[1:] if tok):
        header = [h.strip().lower() for h in first]
        lines = lines[1:]
    for ln in lines:
        toks = ln.split(delim) if delim else ln.split()
        if len(toks) < 2:
            continue
        vid = toks[0].strip()
        vals = toks[1:]
        if header and len(header) - 1 == len(vals):
            row = {header[i + 1]: vals[i].strip() for i in range(len(vals))}
        else:
            # authors' format: id, likes, views (fallback: positional names)
            names = ["likes", "views", "shares", "comments", "collects",
                     "followers"][: len(vals)]
            row = dict(zip(names, (v.strip() for v in vals)))
        metrics[vid] = row
    return metrics


def parse_title_file(path: Path) -> dict[str, dict]:
    """Parse a two-or-more-column item/title CSV without guessing free text."""
    result: dict[str, dict] = {}
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
            except csv.Error:
                dialect = csv.excel
            records = list(csv.reader(f, dialect))
    except OSError:
        return result
    if not records:
        return result
    first = [value.strip().lower() for value in records[0]]
    has_header = any(value in {"id", "item_id", "video_id", "title"}
                     for value in first)
    id_idx = next((i for i, value in enumerate(first)
                   if value in {"id", "item_id", "video_id"}), 0)
    title_idx = next((i for i, value in enumerate(first)
                      if "title" in value), 1 if len(first) > 1 else 0)
    for record in records[1 if has_header else 0:]:
        if len(record) <= max(id_idx, title_idx):
            continue
        video_id = Path(record[id_idx].strip()).stem
        title = record[title_idx].strip()
        if video_id and title:
            result[video_id] = {"title": title}
    return result


def annotation_asset(path: Path, ds_dir: Path, kind: str,
                     joined_fields: list[str]) -> dict:
    return {
        "file": str(path.relative_to(ds_dir)),
        "kind": kind,
        "size_mb": round(path.stat().st_size / MB, 3),
        "sha256": sha256_file(path),
        "joined_fields": joined_fields,
    }


def write_outputs(ds_dir: Path, name: str, rows: list[dict],
                  info_md: str, stats: dict,
                  assets: Optional[list[dict]] = None) -> dict:
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    csv_path = ds_dir / "virality_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    (ds_dir / "annotations_index.json").write_text(json.dumps({
        "dataset": name, "generated": utcnow(), "stats": stats, "items": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    (ds_dir / "annotation_assets.json").write_text(json.dumps({
        "dataset": name, "generated": utcnow(), "assets": assets or [],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    (ds_dir / "DATASET_INFO.md").write_text(info_md, encoding="utf-8")
    print(f"  [+] {len(rows)} rows -> {csv_path}")
    return {"dataset": name, "items": len(rows), **stats}


# ---------------------------------------------------------------------------
# Handler: MicroLens (automated, size-budgeted)
# ---------------------------------------------------------------------------
def handle_microlens(root: Path, variant: str, budget_mb: int,
                     max_videos: Optional[int], max_file_mb: int,
                     max_duration_seconds: Optional[float],
                     include_interactions: bool, workers: int) -> dict:
    name = f"microlens_{variant}"
    ds = root / "datasets" / name
    raw = ds / "raw"; raw.mkdir(parents=True, exist_ok=True)
    for stale_part in raw.rglob("*.part"):
        stale_part.unlink()
    base = MICROLENS_BASES[variant]
    s = requests.Session()
    s.headers["User-Agent"] = "research-dataset-fetch/1.0"

    print(f"  [*] reading split-archive index {base}")
    remote_entries: list[RemoteZipEntry] = []
    vid_urls: list[str] = []
    try:
        all_entries, archive_url = remote_zip_index(base, variant, s)
        remote_entries = [entry for entry in all_entries
                          if entry.name.lower().endswith(VIDEO_EXT)]
        print(f"  [*] found {len(remote_entries)} videos in {archive_url}")
    except Exception as archive_error:  # noqa: BLE001
        print(f"  [!] split-archive index failed: {archive_error}")
        print(f"  [*] trying legacy open-directory discovery")
        urls = crawl_index(base, s)
        vid_urls = [u for u in urls if u.lower().endswith(VIDEO_EXT)]
    metadata_names = list(MICROLENS_METADATA[variant])
    if include_interactions:
        metadata_names.append(MICROLENS_INTERACTIONS[variant])
    meta_urls = [urljoin(base, filename) for filename in metadata_names]
    print(f"  [*] using {len(meta_urls)} official metadata files")

    # 1) metadata first (small; metric + interaction files)
    budget = budget_mb * MB
    used = 0
    metric_maps: dict[str, dict] = {}
    title_maps: dict[str, dict] = {}
    assets: list[dict] = []
    for mu in meta_urls:
        fname = Path(urlparse(mu).path).name
        dest = raw / "metadata" / fname
        remote_size = head_size(mu, s)
        if remote_size and remote_size > budget - used:
            print(f"  [!] metadata outside remaining budget: {fname}")
            continue
        got = stream_download(mu, dest, s, budget - used)
        used += got
        if not got or not dest.exists():
            continue
        kind, joined_fields = "other", []
        if METRIC_FILE_PAT.search(fname):
            metric_maps.update(parse_metric_file(dest))
            kind, joined_fields = "engagement", ["likes", "views"]
        elif re.search(r"titles?.*\.csv$", fname, re.I):
            title_maps.update(parse_title_file(dest))
            kind, joined_fields = "title", ["title"]
        elif "pair" in fname.lower():
            kind = "user_video_interactions"
        elif "comment" in fname.lower():
            kind = "comments"
        elif "tag" in fname.lower() or "summary" in fname.lower():
            kind = "tags_or_summary"
        assets.append(annotation_asset(dest, ds, kind, joined_fields))
    print(f"  [*] parsed engagement metrics for "
          f"{len(metric_maps)} video ids")
    print(f"  [*] parsed titles for {len(title_maps)} video ids")

    # 2) videos under remaining budget.
    #    Deterministic spread: sort then stride-sample so the subset spans
    #    the id space instead of taking the first N uploads.
    rows: list[dict] = []
    reserve = 5 * MB  # headroom so one long tail file can't bust the cap
    max_file_bytes = max_file_mb * MB
    video_sources: list[RemoteZipEntry | str] = remote_entries or vid_urls
    if remote_entries:
        eligible = [source for source in remote_entries
                    if source.size <= max_file_bytes]
        existing_names = {
            path.name for path in (raw / "videos").glob("*") if path.is_file()
        }
        existing = [source for source in eligible
                    if Path(source.name).name in existing_names]
        pool = [source for source in eligible
                if Path(source.name).name not in existing_names]
        target = max_videos or len(eligible)
        needed = max(0, target - len(existing))
        stride = max(1, len(pool) // max(needed, 1))
        candidates = existing[:target] + pool[::stride][:needed]
    else:
        target = max_videos or len(video_sources)
        stride = max(1, len(video_sources) // max(target, 1))
        candidates = video_sources[::stride]

    if remote_entries:
        selected: list[RemoteZipEntry] = []
        planned = used
        for source in candidates:
            if not isinstance(source, RemoteZipEntry):
                continue
            if source.size > max_file_bytes:
                continue
            if planned + source.size > budget - reserve:
                continue
            selected.append(source)
            planned += source.size
            if max_videos and len(selected) >= max_videos:
                break

        def fetch_member(source: RemoteZipEntry) -> tuple:
            fname = Path(source.name).name
            dest = raw / "videos" / fname
            existed = dest.exists()
            try:
                if existed and dest.stat().st_size == source.size:
                    got = dest.stat().st_size
                else:
                    worker_session = requests.Session()
                    worker_session.headers["User-Agent"] = (
                        "research-dataset-fetch/1.0")
                    got = download_remote_zip_member(
                        source, base, variant, dest, worker_session)
                    worker_session.close()
                duration = probe_duration(dest)
                if (max_duration_seconds is not None and duration is not None
                        and duration > max_duration_seconds):
                    if not existed:
                        dest.unlink()
                    return source, dest, 0, duration, "duration limit"
                return source, dest, got, duration, ""
            except Exception as e:  # noqa: BLE001
                return source, dest, 0, None, str(e)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(tqdm(pool.map(fetch_member, selected),
                                total=len(selected), desc="  videos"))
        for source, dest, got, duration, error in results:
            if not got:
                print(f"  [!] skipped {dest.name}: {error}")
                continue
            used += got
            vid_id = dest.stem
            row = {
                "video_id": vid_id,
                "file": str(dest.relative_to(ds)),
                "size_mb": round(got / MB, 2),
                "duration_seconds": (round(duration, 3)
                                     if duration is not None else ""),
                "sha256": sha256_file(dest),
                "source_url": split_disk_url(base, variant, source.disk),
                "archive_member": source.name,
                "archive_disk": source.disk,
            }
            row.update(metric_maps.get(vid_id, {}))
            row.update(title_maps.get(vid_id, {}))
            rows.append(row)
        candidates = []

    for source in tqdm(candidates, desc="  videos"):
        if used >= budget - reserve or (max_videos and len(rows) >= max_videos):
            break
        if isinstance(source, RemoteZipEntry):
            fname = Path(source.name).name
            size = source.size
            source_url = split_disk_url(base, variant, source.disk)
        else:
            fname = Path(urlparse(source).path).name
            size = head_size(source, s)
            source_url = source
        vid_id = Path(fname).stem
        if size and size > max_file_bytes:
            continue
        if size and used + size > budget - reserve:
            continue  # try a smaller one instead of stopping cold
        dest = raw / "videos" / fname
        existed = dest.exists()
        if existed and dest.stat().st_size <= min(budget - used, max_file_bytes):
            got = dest.stat().st_size
        elif isinstance(source, RemoteZipEntry):
            try:
                got = download_remote_zip_member(source, base, variant, dest, s)
            except Exception as e:  # noqa: BLE001
                print(f"  [!] skipped {fname}: {e}")
                continue
        else:
            got = stream_download(source, dest, s,
                                  min(budget - used, max_file_bytes))
        if not got:
            continue
        duration = probe_duration(dest)
        if (max_duration_seconds is not None and duration is not None
                and duration > max_duration_seconds):
            if not existed:
                dest.unlink()
            continue
        used += got
        row = {"video_id": vid_id,
               "file": str(dest.relative_to(ds)),
               "size_mb": round(got / MB, 2),
               "duration_seconds": (round(duration, 3)
                                    if duration is not None else ""),
               "sha256": sha256_file(dest),
               "source_url": source_url}
        if isinstance(source, RemoteZipEntry):
            row.update({"archive_member": source.name,
                        "archive_disk": source.disk})
        row.update(metric_maps.get(vid_id, {}))
        row.update(title_maps.get(vid_id, {}))
        rows.append(row)

    stats = {
        "variant": variant,
        "videos_downloaded": len(rows),
        "videos_with_metrics": sum(1 for r in rows if "likes" in r
                                   or "views" in r),
        "total_size_mb": round(used / MB, 1),
        "budget_mb": budget_mb,
        "max_file_mb": max_file_mb,
        "max_duration_seconds": max_duration_seconds,
        "remote_videos_available": len(video_sources),
        "annotation_assets": len(assets),
        "interactions_requested": include_interactions,
        "download_workers": workers,
    }
    info = f"""# MicroLens-{variant} (sampled subset)

* Source: {base} (official range-enabled split archive published by
  westlake-repl/MicroLens)
* Joined annotations: per-video likes, views, and titles.
* Optional metadata: the user-video interaction TSV is downloaded only with
  `--include-interactions`; 100K also publishes comments and tags/summaries.
* License/usage: research use; anonymized ids; do not redistribute media or
  a privately modified copy. Keep derived MCI outputs separate from raw data.
* Sampling: stride-sampled to fit a {budget_mb} MB budget on {utcnow()}.
* Filters: at most {max_file_mb} MiB per video; duration at most
  {max_duration_seconds or 'unlimited'} seconds when ffprobe can inspect it.
* Note: metrics are snapshots from the authors' collection window.
"""
    return write_outputs(ds, name, rows, info, stats, assets)


# ---------------------------------------------------------------------------
# Handler: SnapUGC (official annotations + size-budgeted social videos)
# ---------------------------------------------------------------------------
def parse_snapugc_annotations(path: Path, split: str) -> list[dict]:
    records: list[dict] = []
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace",
                       newline="") as f:
            for raw in csv.DictReader(f):
                row = {(key or "").strip().lower(): (value or "").strip()
                       for key, value in raw.items()}
                video_id = row.get("id", "")
                source_url = row.get("download_link", "")
                if video_id and source_url:
                    records.append({
                        "video_id": video_id,
                        "title": row.get("title", ""),
                        "description": row.get("description", ""),
                        "ecr": row.get("ecr", ""),
                        "split": split,
                        "source_url": source_url,
                    })
    except OSError:
        pass
    return records


def handle_snapugc(root: Path, budget_mb: int, max_videos: Optional[int],
                   max_file_mb: int, max_duration_seconds: Optional[float],
                   workers: int) -> dict:
    name = "snapugc"
    ds = root / "datasets" / name
    raw = ds / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for stale_part in raw.rglob("*.part"):
        stale_part.unlink()
    budget = budget_mb * MB
    used = 0
    assets: list[dict] = []
    records: list[dict] = []
    s = requests.Session()
    s.headers["User-Agent"] = "research-dataset-fetch/1.0"

    for split, url in SNAPUGC_ANNOTATION_URLS.items():
        dest = raw / "metadata" / f"{split}_data.csv"
        got = stream_download(url, dest, s, budget - used)
        if not got or not dest.exists():
            continue
        used += got
        split_records = parse_snapugc_annotations(dest, split)
        records.extend(split_records)
        fields = ["title", "description", "download_link"]
        if any(record.get("ecr") for record in split_records):
            fields.append("ecr")
        assets.append(annotation_asset(dest, ds, "snapugc_annotations", fields))

    # Prefer training items with ECR labels. Hash ordering gives a stable,
    # well-spread subset without relying on source-row order.
    candidates = [record for record in records if record.get("ecr")]
    existing_ids = {
        path.stem for path in (raw / "videos").glob("*.mp4") if path.is_file()
    }
    failed_path = ds / "failed_downloads.json"
    try:
        failed_ids = set(json.loads(failed_path.read_text(encoding="utf-8"))
                         .get("video_ids", []))
    except (OSError, json.JSONDecodeError):
        failed_ids = set()
    candidates = [record for record in candidates
                  if record["video_id"] in existing_ids
                  or record["video_id"] not in failed_ids]
    candidates.sort(key=lambda record: (
        record["video_id"] not in existing_ids,
        hashlib.sha256(record["video_id"].encode("utf-8")).digest(),
    ))
    target = max_videos or len(candidates)
    probe_pool = candidates[:max(target * 8, target)]

    def probe(record: dict) -> tuple[dict, Optional[int]]:
        worker_session = requests.Session()
        worker_session.headers["User-Agent"] = "research-dataset-fetch/1.0"
        size = head_size(record["source_url"], worker_session)
        worker_session.close()
        return record, size

    with ThreadPoolExecutor(max_workers=workers) as pool:
        sized = list(tqdm(pool.map(probe, probe_pool), total=len(probe_pool),
                          desc="  probing SnapUGC"))

    selected: list[dict] = []
    planned = used
    max_file_bytes = max_file_mb * MB
    for record, size in sized:
        assumed_size = size if size is not None else max_file_bytes
        if assumed_size > max_file_bytes:
            continue
        if planned + assumed_size > budget - 5 * MB:
            continue
        selected.append(record)
        planned += assumed_size
        if len(selected) >= target * 4:
            break

    def fetch(record: dict) -> tuple:
        dest = raw / "videos" / f"{record['video_id']}.mp4"
        existed = dest.exists()
        worker_session = requests.Session()
        worker_session.headers["User-Agent"] = "research-dataset-fetch/1.0"
        got = stream_download(record["source_url"], dest, worker_session,
                              max_file_bytes)
        worker_session.close()
        if not got or not looks_like_video(dest):
            if dest.exists() and not existed:
                dest.unlink()
            return record, dest, 0, None, existed
        duration = probe_duration(dest)
        if (max_duration_seconds is not None and duration is not None
                and duration > max_duration_seconds):
            if not existed:
                dest.unlink()
            return record, dest, 0, duration, existed
        return record, dest, got, duration, existed

    with ThreadPoolExecutor(max_workers=workers) as pool:
        downloads = list(tqdm(pool.map(fetch, selected), total=len(selected),
                              desc="  SnapUGC videos"))

    rows: list[dict] = []
    for record, dest, got, duration, existed in downloads:
        if not got:
            if not existed:
                failed_ids.add(record["video_id"])
            continue
        failed_ids.discard(record["video_id"])
        if len(rows) >= target:
            if not existed:
                dest.unlink()
            continue
        used += got
        rows.append({
            **record,
            "file": str(dest.relative_to(ds)),
            "size_mb": round(got / MB, 2),
            "duration_seconds": (round(duration, 3)
                                 if duration is not None else ""),
            "sha256": sha256_file(dest),
        })
    failed_path.write_text(json.dumps({
        "generated": utcnow(),
        "note": "IDs returning unavailable/invalid media; delete to retry.",
        "video_ids": sorted(failed_ids),
    }, indent=2), encoding="utf-8")

    stats = {
        "videos_downloaded": len(rows),
        "videos_with_ecr": sum(1 for row in rows if row.get("ecr")),
        "annotation_records": len(records),
        "total_size_mb": round(used / MB, 1),
        "budget_mb": budget_mb,
        "max_file_mb": max_file_mb,
        "max_duration_seconds": max_duration_seconds,
        "annotation_assets": len(assets),
        "unavailable_video_ids": len(failed_ids),
        "download_workers": workers,
    }
    info = f"""# SnapUGC (sampled subset)

* Source: https://github.com/dasongli1/SnapUGC_Engagement
* Joined annotations: ECR, title, description, and official download URL.
* ECR is published for the train split; the validation CSV has no ECR field.
* The public files inspected by this downloader do not expose NAWP labels.
* License/usage: research use; do not redistribute the source media.
* Sampling: stable hash sample under a {budget_mb} MiB acquisition cap.
* Filters: at most {max_file_mb} MiB per video; duration at most
  {max_duration_seconds or 'unlimited'} seconds when ffprobe can inspect it.
"""
    return write_outputs(ds, name, rows, info, stats, assets)


# ---------------------------------------------------------------------------
# Handler: manual-drop dataset (XS-Video)
# ---------------------------------------------------------------------------
MANUAL_SPECS = {
    "xsvideo": {
        "title": "XS-Video (SPIR propagation influence)",
        "hint": ("Obtain the release via the paper's repository "
                 "(arXiv:2503.23746) and drop the archive in manual_drop/ "
                 "as xsvideo*.zip"),
        "metrics_note": "views, likes, shares, collects, fans, comments, "
                        "0-9 influence level",
        "glob": "xsvideo*",
    },
}


def handle_manual(root: Path, name: str, budget_mb: int) -> dict:
    spec = MANUAL_SPECS[name]
    ds = root / "datasets" / name
    raw = ds / "raw"; raw.mkdir(parents=True, exist_ok=True)
    drop = root / "manual_drop"

    archives = [p for p in drop.glob(spec["glob"])
                if p.suffix in (".zip", ".tar", ".gz", ".tgz")]
    extracted_bytes = 0
    for a in archives:
        print(f"  [*] unpacking {a.name}")
        try:
            extracted_bytes += safe_extract_archive(
                a, raw, budget_mb * MB - extracted_bytes)
        except Exception as e:  # noqa: BLE001
            print(f"  [!] unpack failed: {e}")

    rows: list[dict] = []
    assets: list[dict] = []
    for p in raw.rglob("*"):
        indexable = (".csv", ".txt", ".json", ".jsonl") + VIDEO_EXT
        if p.is_file() and p.suffix.lower() in indexable:
            kind = ("video" if p.suffix.lower() in VIDEO_EXT
                    else "annotation")
            rows.append({"video_id": p.stem,
                         "file": str(p.relative_to(ds)),
                         "size_mb": round(p.stat().st_size / MB, 3),
                         "sha256": sha256_file(p),
                         "kind": kind})
            if kind == "annotation":
                assets.append(annotation_asset(p, ds, "unparsed", []))
    if not rows:
        print(f"  [i] {name}: pending. {spec['hint']}")
    info = f"""# {spec['title']}

* Status: {'indexed' if rows else 'PENDING manual download'}
* Engagement annotations: {spec['metrics_note']}
* Acquisition: {spec['hint']}
* License/usage: research use; do not redistribute media.
"""
    return write_outputs(ds, name, rows, info,
                         {"files": len(rows),
                          "extracted_size_mb": round(extracted_bytes / MB, 2),
                          "status": "ok" if rows else "pending"}, assets)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Download influencer/UGC video datasets with virality "
                    "metrics under a size budget.")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help=f"Isolated dataset root (default: {DEFAULT_ROOT})")
    ap.add_argument("--datasets", nargs="+", default=["microlens"],
                    choices=["microlens", "xsvideo", "snapugc", "all"])
    ap.add_argument("--microlens-variant", choices=["50k", "100k"],
                    default="50k")
    ap.add_argument("--size-budget-mb", type=int, default=450,
                    help="Acquisition/extraction cap in MiB (default: 450).")
    ap.add_argument("--max-videos", type=int, default=None,
                    help="Optional cap on number of videos (e.g. 100).")
    ap.add_argument("--max-file-mb", type=int, default=5,
                    help="Maximum individual downloaded video size in MiB.")
    ap.add_argument("--max-duration-seconds", type=float, default=60.0,
                    help="Maximum video duration when ffprobe is installed.")
    ap.add_argument("--include-interactions", action="store_true",
                    help="Also fetch the large user-video interaction TSV.")
    ap.add_argument("--workers", type=int, default=4,
                    help="Concurrent network operations (1-16).")
    ap.add_argument("--accept-research-terms", action="store_true",
                    help="Confirm research-only/non-redistribution terms.")
    args = ap.parse_args()

    if not (100 <= args.size_budget_mb <= 5000):
        print("[!] --size-budget-mb should be sensible (100-5000).")
        return 2
    if args.max_file_mb <= 0 or args.max_file_mb > args.size_budget_mb:
        print("[!] --max-file-mb must be positive and within the budget.")
        return 2
    if args.max_duration_seconds < 0:
        print("[!] --max-duration-seconds must be zero or positive.")
        return 2
    if not (1 <= args.workers <= 16):
        print("[!] --workers must be between 1 and 16.")
        return 2

    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / "manual_drop").mkdir(exist_ok=True)
    wanted = (["microlens", "xsvideo", "snapugc"]
              if "all" in args.datasets else args.datasets)
    if any(name in wanted for name in ("microlens", "snapugc")) \
            and not args.accept_research_terms:
        print("[!] Automated research datasets require "
              "--accept-research-terms. Read the official dataset "
              "declarations before downloading.")
        return 2
    if args.max_duration_seconds and not shutil.which("ffprobe"):
        print("  [!] ffprobe unavailable; duration filtering will be skipped")

    catalog_path = args.root / "catalog.json"
    prior_summaries: dict[str, dict] = {}
    try:
        prior = json.loads(catalog_path.read_text(encoding="utf-8"))
        prior_summaries = {item["dataset"]: item
                           for item in prior.get("datasets", [])
                           if isinstance(item, dict) and item.get("dataset")}
    except (OSError, json.JSONDecodeError):
        pass
    for name in wanted:
        print(f"\n=== {name} ===")
        try:
            if name == "microlens":
                summary = handle_microlens(args.root, args.microlens_variant,
                                           args.size_budget_mb,
                                           args.max_videos,
                                           args.max_file_mb,
                                           (args.max_duration_seconds or None),
                                           args.include_interactions,
                                           args.workers)
            elif name == "snapugc":
                summary = handle_snapugc(
                    args.root, args.size_budget_mb, args.max_videos,
                    args.max_file_mb, (args.max_duration_seconds or None),
                    args.workers)
            else:
                summary = handle_manual(args.root, name, args.size_budget_mb)
        except KeyboardInterrupt:
            print("\ninterrupted."); return 130
        except Exception as e:  # noqa: BLE001
            print(f"  [!] handler crashed: {e}")
            summary = {"dataset": name, "error": str(e)}
        prior_summaries[summary.get("dataset", name)] = summary

    catalog = {
        "generated": utcnow(),
        "last_run": {"datasets": wanted, "size_budget_mb": args.size_budget_mb},
        "datasets": list(prior_summaries.values()),
    }
    catalog_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[+] catalog -> {catalog_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
