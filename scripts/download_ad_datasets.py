#!/usr/bin/env python3
"""Build a small advertising-media dataset under a strict byte budget.

The previous version snapshotted whole datasets, so ``--max-items`` did not
limit download size. This version discovers individual files first, checks
their byte size and license metadata, and only then downloads them.

Defaults: at most 100 files, strictly under 490 MB, at most 5 MB per file,
and videos no longer than 60 seconds when duration metadata is available.
Short advertising videos are selected first; advertising posters and flyers
fill the remaining quota. A JSONL manifest records provenance and licensing.

Examples:
    python scripts/download_ad_datasets.py --dry-run
    python scripts/download_ad_datasets.py
    python scripts/download_ad_datasets.py --max-items 500 --max-file-mb 0.9
    python scripts/download_ad_datasets.py --media video --max-duration 5
    python scripts/download_ad_datasets.py --sources commons,archive

Copyright permission does not remove trademark, publicity or privacy rights.
Review manifest.jsonl and each source page before redistribution or commercial
use. The script deliberately does not download YouTube/social-platform URLs.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import html
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
ARCHIVE_SEARCH_API = "https://archive.org/advancedsearch.php"
ARCHIVE_METADATA_API = "https://archive.org/metadata/{identifier}"
USER_AGENT = "MCI-v2-ad-subset/1.0 (file-level open-media downloader)"

COMMONS_VIDEO_CATEGORIES = (
    "Advertising videos",
    "Television advertisements",
    "Wikipedia advertisements",
)
COMMONS_IMAGE_CATEGORIES = (
    "Advertising posters",
    "Food and drink advertising posters",
    "Sports posters",
)
COMMONS_SEARCHES = (
    "advertisement filetype:video",
    '"promotional video" filetype:video',
    '"social media" campaign filetype:video',
    '"public service announcement" filetype:video',
)

VIDEO_MIMES = {"video/webm", "video/ogg", "application/ogg", "video/mp4"}
IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
OUTPUT_EXTENSIONS = {
    ".webm", ".ogv", ".ogg", ".mp4", ".jpg", ".jpeg", ".png", ".webp", ".gif"
}
BAD_LICENSE_MARKERS = (
    "copyright violations",
    "license review needed",
    "unknown copyright status",
    "no permission",
)


@dataclass(frozen=True)
class MediaItem:
    """A downloadable file and the provenance needed to audit its use."""

    source: str
    source_id: str
    title: str
    media_type: str
    mime_type: str
    size_bytes: int
    duration_seconds: float | None
    download_url: str
    source_page: str
    license_name: str
    license_url: str
    creator: str
    description: str


def plain_text(value: str) -> str:
    """Turn compact HTML metadata into readable text."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch one JSON API response using only the Python standard library."""
    if params:
        url = f"{url}?{urlencode(params, doseq=True)}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def metadata_value(metadata: dict[str, Any], key: str) -> str:
    value = metadata.get(key, {})
    return str(value.get("value", "")) if isinstance(value, dict) else ""


def commons_item(page: dict[str, Any]) -> MediaItem | None:
    """Parse and license-check one Wikimedia Commons API result."""
    image_info = page.get("imageinfo") or []
    if not image_info:
        return None
    info = image_info[0]
    metadata = info.get("extmetadata") or {}
    mime = str(info.get("mime", "")).lower()
    media_type = "video" if mime in VIDEO_MIMES else "image" if mime in IMAGE_MIMES else ""
    if not media_type:
        return None

    license_name = plain_text(metadata_value(metadata, "LicenseShortName"))
    usage_terms = plain_text(metadata_value(metadata, "UsageTerms"))
    categories = plain_text(metadata_value(metadata, "Categories")).lower()
    if not (license_name or usage_terms):
        return None
    if any(marker in categories for marker in BAD_LICENSE_MARKERS):
        return None

    duration = info.get("duration")
    return MediaItem(
        source="wikimedia_commons",
        source_id=str(page.get("pageid", "")),
        title=str(page.get("title", "File:untitled")),
        media_type=media_type,
        mime_type=mime,
        size_bytes=int(info.get("size", 0) or 0),
        duration_seconds=float(duration) if duration is not None else None,
        download_url=str(info.get("url", "")),
        source_page=str(info.get("descriptionurl", "")),
        license_name=license_name or usage_terms,
        license_url=plain_text(metadata_value(metadata, "LicenseUrl")),
        creator=plain_text(metadata_value(metadata, "Artist")),
        description=plain_text(metadata_value(metadata, "ImageDescription")),
    )


def commons_query(params: dict[str, Any], max_pages: int) -> Iterable[MediaItem]:
    """Yield a bounded number of pages from one Commons discovery query."""
    continuation: dict[str, Any] = {}
    for _ in range(max_pages):
        payload = fetch_json(
            COMMONS_API,
            {
                "action": "query",
                "format": "json",
                "formatversion": 2,
                "prop": "imageinfo",
                "iiprop": "url|size|mime|mediatype|extmetadata",
                "iiextmetadatalanguage": "en",
                **params,
                **continuation,
            },
        )
        for page in payload.get("query", {}).get("pages", []):
            item = commons_item(page)
            if item:
                yield item
        continuation = payload.get("continue", {})
        if not continuation:
            break
        time.sleep(0.05)


def discover_commons() -> Iterable[MediaItem]:
    """Discover advertising clips and graphics from curated Commons pools."""
    for category in COMMONS_VIDEO_CATEGORIES + COMMONS_IMAGE_CATEGORIES:
        yield from commons_query(
            {
                "generator": "categorymembers",
                "gcmtitle": f"Category:{category}",
                "gcmnamespace": 6,
                "gcmtype": "file",
                "gcmlimit": 100,
            },
            max_pages=2,
        )
    for search in COMMONS_SEARCHES:
        yield from commons_query(
            {
                "generator": "search",
                "gsrsearch": search,
                "gsrnamespace": 6,
                "gsrlimit": 100,
            },
            max_pages=1,
        )


def archive_license_allowed(license_url: str) -> bool:
    """Allow PD/CC0/CC-BY/CC-BY-SA; reject NC and ND licenses."""
    value = license_url.lower().rstrip("/")
    if "creativecommons" not in value:
        return False
    if any(marker in value for marker in ("by-nc", "by-nd", "nc-", "nd-")):
        return False
    return any(marker in value for marker in ("publicdomain", "/zero/", "/by/", "/by-sa/"))


def archive_document_item(document: dict[str, Any]) -> MediaItem | None:
    """Select one smallest usable video derivative from an Archive item."""
    identifier = str(document.get("identifier", ""))
    license_url = str(document.get("licenseurl", ""))
    if not identifier or not archive_license_allowed(license_url):
        return None
    try:
        item_metadata = fetch_json(
            ARCHIVE_METADATA_API.format(identifier=quote(identifier, safe=""))
        )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None
    creator = str(item_metadata.get("metadata", {}).get("creator", ""))
    choices: list[tuple[int, str, float | None]] = []
    for file_info in item_metadata.get("files", []):
        name = str(file_info.get("name", ""))
        extension = Path(urlparse(name).path).suffix.lower()
        if extension not in {".mp4", ".webm", ".ogv", ".ogg"}:
            continue
        try:
            size = int(file_info.get("size", 0) or 0)
        except (TypeError, ValueError):
            continue
        if size <= 0:
            continue
        duration: float | None = None
        try:
            if file_info.get("length") is not None:
                duration = float(file_info["length"])
        except (TypeError, ValueError):
            pass
        choices.append((size, name, duration))
    if not choices:
        return None
    size, name, duration = min(choices, key=lambda choice: choice[0])
    extension = Path(urlparse(name).path).suffix.lower()
    return MediaItem(
        source="internet_archive",
        source_id=identifier,
        title=str(document.get("title") or name),
        media_type="video",
        mime_type="video/mp4" if extension == ".mp4" else "video/webm",
        size_bytes=size,
        duration_seconds=duration,
        download_url=f"https://archive.org/download/{quote(identifier)}/{quote(name)}",
        source_page=f"https://archive.org/details/{quote(identifier)}",
        license_name=license_url,
        license_url=license_url,
        creator=creator,
        description=plain_text(str(document.get("description", ""))),
    )


def discover_archive(max_pages: int) -> Iterable[MediaItem]:
    """Discover individual small video files in explicitly licensed IA items."""
    query = (
        "mediatype:movies AND (subject:commercials OR subject:advertising "
        "OR title:commercial OR title:advertisement) "
        "AND (licenseurl:*creativecommons* OR licenseurl:*publicdomain*)"
    )
    documents: list[dict[str, Any]] = []
    for page_number in range(1, max_pages + 1):
        result = fetch_json(
            ARCHIVE_SEARCH_API,
            {
                "q": query,
                "fl[]": ["identifier", "title", "licenseurl", "description"],
                "rows": 50,
                "page": page_number,
                "output": "json",
            },
        )
        page_documents = result.get("response", {}).get("docs", [])
        if not page_documents:
            break
        documents.extend(page_documents)

    # A small pool avoids the several-minute serial scan without hammering IA.
    with ThreadPoolExecutor(max_workers=6) as executor:
        for item in executor.map(archive_document_item, documents):
            if item is not None:
                yield item


def select_items(
    discovered: Iterable[MediaItem],
    max_items: int,
    byte_budget: int,
    max_file_bytes: int,
    max_duration: float,
    media: str,
    video_target: int,
) -> list[MediaItem]:
    """Filter, deduplicate and choose short/small videos before images."""
    unique: dict[str, MediaItem] = {}
    for item in discovered:
        if not item.download_url or not 0 < item.size_bytes <= max_file_bytes:
            continue
        if item.media_type == "video":
            if item.duration_seconds is None and max_duration <= 5:
                continue
            if item.duration_seconds is not None and item.duration_seconds > max_duration:
                continue
        if media != "both" and item.media_type != media:
            continue
        unique.setdefault(item.download_url.split("?", 1)[0], item)

    videos = sorted(
        (item for item in unique.values() if item.media_type == "video"),
        key=lambda item: (
            item.duration_seconds is None,
            item.duration_seconds or float("inf"),
            item.size_bytes,
        ),
    )
    images = sorted(
        (item for item in unique.values() if item.media_type == "image"),
        key=lambda item: item.size_bytes,
    )

    selected: list[MediaItem] = []
    used_bytes = 0

    def add(pool: Iterable[MediaItem], stop_at: int) -> None:
        nonlocal used_bytes
        for item in pool:
            if len(selected) >= min(stop_at, max_items):
                break
            if used_bytes + item.size_bytes <= byte_budget:
                selected.append(item)
                used_bytes += item.size_bytes

    if media != "image":
        add(videos, min(video_target, max_items))
    if media != "video":
        add(images, max_items)
    add((item for item in videos if item not in selected), max_items)
    return selected


def output_name(item: MediaItem, ordinal: int) -> str:
    """Create a stable, filesystem-safe output filename."""
    extension = Path(urlparse(item.download_url).path).suffix.lower()
    if extension not in OUTPUT_EXTENSIONS:
        extension = ".bin"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", item.title.removeprefix("File:"))
    stem = stem.strip("._-")[:100] or f"item_{ordinal:04d}"
    if stem.lower().endswith(extension):
        stem = stem[: -len(extension)]
    return f"{ordinal:04d}_{item.source}_{stem}{extension}"


def download(
    item: MediaItem,
    destination: Path,
    remaining_bytes: int,
    retries: int,
) -> int:
    """Stream a file with bounded 429/5xx backoff and hard byte limits."""
    request = Request(item.download_url, headers={"User-Agent": USER_AGENT})
    partial = destination.with_suffix(destination.suffix + ".part")
    for attempt in range(retries + 1):
        written = 0
        try:
            with urlopen(request, timeout=90) as response, partial.open("wb") as output:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > remaining_bytes:
                    raise ValueError("server-reported size exceeds remaining dataset budget")
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > item.size_bytes + 1024 or written > remaining_bytes:
                        raise ValueError("actual download exceeded advertised size or budget")
                    output.write(chunk)
            os.replace(partial, destination)
            return written
        except HTTPError as error:
            partial.unlink(missing_ok=True)
            retryable = error.code == 429 or 500 <= error.code < 600
            if not retryable or attempt >= retries:
                raise
            retry_after = error.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 10.0 * (attempt + 1)
            except ValueError:
                delay = 10.0 * (attempt + 1)
            delay = min(max(delay, 2.0), 60.0)
            print(
                f"Rate limited for {item.title}; retrying in {delay:.0f}s "
                f"({attempt + 1}/{retries})...",
                file=sys.stderr,
            )
            time.sleep(delay)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    raise RuntimeError("unreachable download retry state")


def existing_dataset_bytes(output: Path) -> int:
    """Count downloaded media so resumed runs preserve the total cap."""
    if not output.exists():
        return 0
    return sum(
        path.stat().st_size
        for path in output.iterdir()
        if path.is_file() and path.name != "manifest.jsonl" and not path.name.endswith(".part")
    )


def existing_urls(manifest_path: Path) -> set[str]:
    """Read completed URLs from a prior manifest for resumable operation."""
    urls: set[str] = set()
    if not manifest_path.exists():
        return urls
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("download_url"):
            urls.add(str(record["download_url"]).split("?", 1)[0])
    return urls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/ad_subset"))
    parser.add_argument("--sources", default="commons", help="commons, archive, or commons,archive")
    parser.add_argument("--media", choices=("both", "video", "image"), default="both")
    parser.add_argument("--max-items", type=int, default=100)
    parser.add_argument("--video-target", type=int, default=70)
    parser.add_argument("--max-total-mb", type=float, default=490.0)
    parser.add_argument("--max-file-mb", type=float, default=5.0)
    parser.add_argument("--max-duration", type=float, default=60.0)
    parser.add_argument("--archive-pages", type=int, default=2)
    parser.add_argument("--request-delay", type=float, default=1.5)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_items < 1 or args.video_target < 0 or args.max_duration <= 0:
        raise SystemExit("item counts must be non-negative and duration must be positive")
    if args.request_delay < 0 or args.retries < 0:
        raise SystemExit("request delay and retries cannot be negative")
    if not 0 < args.max_total_mb < 500:
        raise SystemExit("--max-total-mb must be positive and strictly below 500")
    if not 0 < args.max_file_mb <= args.max_total_mb:
        raise SystemExit("--max-file-mb must be positive and no larger than the total")

    sources = {part.strip().lower() for part in args.sources.split(",") if part.strip()}
    invalid = sources - {"commons", "archive"}
    if not sources or invalid:
        raise SystemExit(f"unsupported sources: {', '.join(sorted(invalid)) or args.sources}")

    total_budget = int(args.max_total_mb * 1_000_000)
    manifest_path = args.output / "manifest.jsonl"
    already_used = existing_dataset_bytes(args.output)
    remaining_budget = total_budget - already_used
    if remaining_budget <= 0:
        print(f"Dataset already uses {already_used / 1_000_000:.1f} MB; budget exhausted.")
        return 0

    prior_urls = existing_urls(manifest_path)
    remaining_items = args.max_items - len(prior_urls)
    if remaining_items <= 0:
        print(f"Dataset already has {len(prior_urls)} manifested files; item cap reached.")
        return 0
    discovered: list[MediaItem] = []
    try:
        if "commons" in sources:
            print("Discovering Wikimedia Commons advertising media...", file=sys.stderr)
            discovered.extend(discover_commons())
        if "archive" in sources:
            print("Discovering explicitly licensed Internet Archive media...", file=sys.stderr)
            discovered.extend(discover_archive(args.archive_pages))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"Discovery failed: {error}", file=sys.stderr)
        return 1

    new_candidates = [
        item for item in discovered if item.download_url.split("?", 1)[0] not in prior_urls
    ]
    selected = select_items(
        new_candidates,
        max_items=remaining_items,
        byte_budget=remaining_budget,
        max_file_bytes=int(args.max_file_mb * 1_000_000),
        max_duration=args.max_duration,
        media=args.media,
        video_target=min(args.video_target, remaining_items),
    )
    planned = sum(item.size_bytes for item in selected)
    videos = sum(item.media_type == "video" for item in selected)
    print(
        f"Discovered {len(discovered)} records; selected {len(selected)} new files "
        f"({videos} videos, {len(selected) - videos} images), {planned / 1_000_000:.1f} MB."
    )

    if args.dry_run:
        for item in selected:
            print(json.dumps(asdict(item), ensure_ascii=False))
        return 0

    args.output.mkdir(parents=True, exist_ok=True)
    downloaded_bytes = 0
    downloaded_count = 0
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for ordinal, item in enumerate(selected, len(prior_urls) + 1):
            destination = args.output / output_name(item, ordinal)
            try:
                written = download(
                    item,
                    destination,
                    remaining_budget - downloaded_bytes,
                    retries=args.retries,
                )
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
                print(f"Skipping {item.title}: {error}", file=sys.stderr)
                time.sleep(args.request_delay)
                continue
            manifest.write(
                json.dumps(
                    {**asdict(item), "local_path": str(destination), "downloaded_bytes": written},
                    ensure_ascii=False,
                )
                + "\n"
            )
            manifest.flush()
            downloaded_bytes += written
            downloaded_count += 1
            print(f"Downloaded {downloaded_count:04d}: {destination.name} ({written / 1_000_000:.2f} MB)")
            time.sleep(args.request_delay)

    print(
        f"Finished: {downloaded_count} new files, {downloaded_bytes / 1_000_000:.1f} MB; "
        f"dataset total <= {(already_used + downloaded_bytes) / 1_000_000:.1f} MB."
    )
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
