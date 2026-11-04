"""Deterministic search catalog over the locally downloaded media.

The catalog indexes both the advertisement subset and the separately stored
social-media datasets. Search is metadata based: it never pretends that a
visual embedding or model prediction exists when one has not been generated.
Results remain explainable and point to the exact local file that was ranked.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlparse

from rank_bm25 import BM25Okapi

from app.config import settings

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_PLAYABLE_EXTS = {".mp4", ".webm", ".ogg", ".ogv", ".mov"}
_BROWSER_PREVIEW_EXTS = {".mp4", ".webm", ".ogg", ".ogv"}
_MIME_TYPES = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ogg": "video/ogg",
    ".ogv": "video/ogg",
    ".mov": "video/quicktime",
}

# Words that describe a request rather than the requested scene or subject.
_STOP_WORDS = {
    "a",
    "all",
    "an",
    "and",
    "any",
    "are",
    "at",
    "be",
    "by",
    "can",
    "for",
    "find",
    "from",
    "get",
    "give",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "please",
    "search",
    "sec",
    "second",
    "seconds",
    "show",
    "that",
    "the",
    "this",
    "to",
    "want",
    "where",
    "with",
}

_TOKEN_NORMALIZATION = {
    "ad": "advertisement",
    "ads": "advertisement",
    "advert": "advertisement",
    "adverts": "advertisement",
    "advertisements": "advertisement",
    "advertising": "advertisement",
    "commercial": "advertisement",
    "commercials": "advertisement",
    "clips": "video",
    "videos": "video",
    "cars": "car",
    "automobile": "car",
    "automobiles": "car",
    "vehicle": "car",
    "vehicles": "car",
    "influencers": "influencer",
    "goals": "goal",
    "drinks": "drinking",
    "drank": "drinking",
}

_GENERIC_MEDIA_TERMS = {
    "advertisement",
    "clip",
    "content",
    "influencer",
    "media",
    "short",
    "social",
    "ugc",
    "video",
}

_QUERY_EXPANSIONS = {
    "car": {"car", "auto", "automotive"},
    "drinking": {"drinking", "drink", "beverage", "hydration"},
    "football": {"football", "soccer"},
    "goal": {"goal", "scoring", "score"},
    "makeup": {"makeup", "cosmetic", "cosmetics", "beauty"},
    "phone": {"phone", "mobile", "smartphone"},
}


@dataclass
class VideoRecord:
    """One searchable video backed by an exact local file."""

    video_id: str
    file_path: str
    title: str = ""
    description: str = ""
    creator: str = ""
    source: str = ""
    source_url: str = ""
    source_page: str = ""
    asset_name: str = ""
    dataset: str = ""
    content_type: str = "video"
    duration_seconds: float | None = None
    mime_type: str | None = None
    annotations: dict[str, Any] = field(default_factory=dict)
    display_text: str = ""

    def is_playable(self) -> bool:
        """Return whether a browser preview can stream this exact file."""
        return (
            Path(self.file_path).suffix.lower() in _BROWSER_PREVIEW_EXTS
            and Path(self.file_path).is_file()
        )


def _resolve_path(value: str | os.PathLike[str]) -> Path:
    """Resolve absolute or project-relative paths without requiring existence."""
    path = Path(value).expanduser()
    return path if path.is_absolute() else (_PROJECT_ROOT / path).resolve()


def _tokenize(text: str) -> list[str]:
    """Tokenize and lightly normalize English metadata."""
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return [_TOKEN_NORMALIZATION.get(token, token) for token in raw]


def _unique(values: Iterable[str]) -> list[str]:
    """Return non-empty strings once each while preserving input order."""
    return list(dict.fromkeys(values))


def _safe_float(value: Any) -> float | None:
    """Convert optional metadata to float, returning ``None`` when invalid."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _slug(value: str, limit: int = 48) -> str:
    """Create a bounded lowercase identifier suitable for stable catalog keys."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:limit] or "video"


class VideoCatalog:
    """Metadata catalog with relevance-gated BM25 ranking."""

    def __init__(
        self,
        base_dir: str | None = None,
        manifest: str | None = None,
        social_media_dir: str | None = None,
    ):
        """Load configured local sources and build an in-memory BM25 index."""
        self.base_dir = _resolve_path(base_dir or settings.object_store_path)
        self.manifest_path = _resolve_path(
            manifest or self.base_dir / "ad_subset" / "manifest.jsonl"
        )
        self.social_media_dir = _resolve_path(
            social_media_dir or settings.social_media_store_path
        )
        self.records: list[VideoRecord] = []
        self._by_video_id: dict[str, VideoRecord] = {}
        self._known_paths: set[str] = set()
        self._bm25: BM25Okapi | None = None
        self._tokenized_docs: list[list[str]] = []
        self._load()

    def _load(self) -> None:
        """Discover advertisement and social-video records from configured roots."""
        self._load_advertisements()
        self._load_social_media()
        self._build_index()

    def _load_advertisements(self) -> None:
        """Load manifest-backed ads without collapsing distinct variants."""
        rows = self._read_jsonl(self.manifest_path)
        grouped: dict[tuple[str, str, str, float | None], dict[str, Any]] = {}

        for row in rows:
            file_path = self._row_path(row, self.base_dir / "ad_subset")
            if file_path is None:
                continue
            duration = _safe_float(row.get("duration_seconds"))
            key = (
                str(row.get("source", "")),
                str(row.get("source_id", "")),
                str(row.get("title", "")),
                round(duration, 2) if duration is not None else None,
            )
            previous = grouped.get(key)
            if previous is None or self._format_preference(file_path) > self._format_preference(
                Path(previous["_file_path"])
            ):
                grouped[key] = {**row, "_file_path": str(file_path)}

        duplicate_titles = Counter(
            (str(row.get("source_id", "")), str(row.get("title", "")))
            for row in grouped.values()
        )
        for row in grouped.values():
            path = Path(row["_file_path"])
            seq = self._sequence_from_filename(path.name)
            title = str(row.get("title") or self._title_from_filename(path.name))
            source_url = str(row.get("download_url") or "")
            asset_name = self._asset_name(source_url)
            display_title = title.removeprefix("File:")
            duplicate_key = (str(row.get("source_id", "")), str(row.get("title", "")))
            if duplicate_titles[duplicate_key] > 1 and asset_name:
                display_title = asset_name
            self._add_record(
                VideoRecord(
                    video_id=f"ad-{seq}-{_slug(title)}",
                    file_path=str(path),
                    title=display_title,
                    description=str(row.get("description") or ""),
                    creator=str(row.get("creator") or ""),
                    source=str(row.get("source") or "advertisement_subset"),
                    source_url=source_url,
                    source_page=str(row.get("source_page") or ""),
                    asset_name=asset_name,
                    dataset="ad_subset",
                    content_type="advertisement",
                    duration_seconds=_safe_float(row.get("duration_seconds")),
                    mime_type=str(row.get("mime_type") or _MIME_TYPES.get(path.suffix.lower(), "")),
                    annotations={
                        "license_name": row.get("license_name"),
                        "license_url": row.get("license_url"),
                    },
                )
            )

        # Keep locally added media searchable even if it predates the manifest.
        ad_dir = self.base_dir / "ad_subset"
        if ad_dir.is_dir():
            for path in sorted(ad_dir.iterdir()):
                if path.suffix.lower() not in _PLAYABLE_EXTS:
                    continue
                if str(path.resolve()) in self._known_paths:
                    continue
                title = self._title_from_filename(path.name)
                self._add_record(
                    VideoRecord(
                        video_id=f"ad-{self._sequence_from_filename(path.name)}-{_slug(title)}",
                        file_path=str(path.resolve()),
                        title=title,
                        source="local",
                        dataset="ad_subset",
                        content_type="advertisement",
                        mime_type=_MIME_TYPES.get(path.suffix.lower()),
                    )
                )

    def _load_social_media(self) -> None:
        """Load the downloaded MicroLens and SnapUGC annotation indexes."""
        datasets_dir = self.social_media_dir / "datasets"
        if not datasets_dir.is_dir():
            return
        for index_path in sorted(datasets_dir.glob("*/annotations_index.json")):
            self._load_social_index(index_path)

    def _load_social_index(self, index_path: Path) -> None:
        """Join one social annotation index to corresponding playable files."""
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        dataset = str(payload.get("dataset") or index_path.parent.name)
        for item in payload.get("items", []):
            relative_file = item.get("file")
            if not relative_file:
                continue
            path = (index_path.parent / str(relative_file)).resolve()
            if not path.is_file() or path.suffix.lower() not in _PLAYABLE_EXTS:
                continue
            raw_id = str(item.get("video_id") or path.stem)
            title = str(item.get("title") or "").strip()
            description = str(item.get("description") or "").strip()
            display_title = title or description or f"{dataset} video {raw_id}"
            annotations = {
                key: item.get(key)
                for key in ("likes", "views", "ecr", "split", "size_mb", "sha256")
                if item.get(key) not in (None, "")
            }
            self._add_record(
                VideoRecord(
                    video_id=f"{_slug(dataset, 24)}-{_slug(raw_id, 40)}",
                    file_path=str(path),
                    title=display_title,
                    description=description if description != display_title else "",
                    source=dataset,
                    source_url=str(item.get("source_url") or ""),
                    asset_name=path.name,
                    dataset=dataset,
                    content_type="social_media",
                    duration_seconds=_safe_float(item.get("duration_seconds")),
                    mime_type=_MIME_TYPES.get(path.suffix.lower()),
                    annotations=annotations,
                )
            )

    def _add_record(self, record: VideoRecord) -> None:
        """Validate, de-duplicate, normalize, and register one local video record."""
        resolved = str(Path(record.file_path).resolve())
        if resolved in self._known_paths or not Path(resolved).is_file():
            return
        record.file_path = resolved
        if record.video_id in self._by_video_id:
            suffix = _slug(Path(resolved).stem, 16)
            record.video_id = f"{record.video_id}-{suffix}"
        record.display_text = self._build_display_text(record)
        self.records.append(record)
        self._by_video_id[record.video_id] = record
        self._known_paths.add(resolved)

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        """Read dictionary rows from JSON Lines while skipping corrupt entries."""
        if not path.is_file():
            return []
        rows: list[dict[str, Any]] = []
        try:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, dict):
                        rows.append(row)
        except OSError:
            return []
        return rows

    @staticmethod
    def _row_path(row: dict[str, Any], fallback_dir: Path) -> Path | None:
        """Resolve a manifest row to an existing playable local asset."""
        local_path = row.get("local_path")
        candidates = []
        if local_path:
            candidates.append(_resolve_path(str(local_path)))
            candidates.append(fallback_dir / Path(str(local_path)).name)
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() in _PLAYABLE_EXTS:
                return candidate.resolve()
        return None

    @staticmethod
    def _format_preference(path: Path) -> int:
        """Rank media formats so duplicate assets choose the best preview."""
        return {".mp4": 4, ".webm": 3, ".ogg": 2, ".ogv": 2, ".mov": 1}.get(
            path.suffix.lower(), 0
        )

    @staticmethod
    def _sequence_from_filename(basename: str) -> str:
        """Extract a leading sequence number or derive a stable filename slug."""
        match = re.match(r"(\d+)", basename)
        return match.group(1) if match else _slug(Path(basename).stem, 12)

    @staticmethod
    def _title_from_filename(basename: str) -> str:
        """Convert downloader filenames into human-readable fallback titles."""
        name = Path(basename).stem
        parts = name.split("_", 1)
        if len(parts) > 1 and parts[0].isdigit():
            name = parts[1]
        name = re.sub(
            r"^(internet_archive|wikimedia_commons)_", "", name, flags=re.IGNORECASE
        )
        return name.replace("_", " ").strip()

    @staticmethod
    def _asset_name(source_url: str) -> str:
        """Return the human-readable name of one remote media asset."""
        if not source_url:
            return ""
        name = Path(unquote(urlparse(source_url).path)).stem
        return name.replace("_", " ").strip()

    @staticmethod
    def _build_display_text(record: VideoRecord) -> str:
        """Assemble weighted metadata without inventing visual evidence."""
        tags = (
            "advertisement commercial ad"
            if record.content_type == "advertisement"
            else "social media influencer short video user generated content ugc"
        )
        return " ".join(
            value
            for value in (
                record.title,
                record.title,  # Titles are the most trustworthy annotation.
                record.description,
                record.creator,
                record.source,
                record.dataset,
                tags,
            )
            if value
        )

    def _build_index(self) -> None:
        """Tokenize display documents and initialize BM25 when content exists."""
        self._tokenized_docs = [_tokenize(record.display_text) for record in self.records]
        if self._tokenized_docs and any(self._tokenized_docs):
            self._bm25 = BM25Okapi(self._tokenized_docs)

    @staticmethod
    def _term_group(term: str) -> set[str]:
        """Return deterministic synonyms used to broaden one query term."""
        return _QUERY_EXPANSIONS.get(term, {term})

    @staticmethod
    def _matches_filters(record: VideoRecord, filters: dict[str, Any]) -> bool:
        """Evaluate dataset, source, type, duration, playability, and brands."""
        def accepted(field_value: str, requested: Any) -> bool:
            """Match one record field against an optional scalar or list filter."""
            if requested in (None, "", []):
                return True
            values = requested if isinstance(requested, (list, tuple, set)) else [requested]
            return field_value.lower() in {str(value).lower() for value in values}

        if not accepted(record.dataset, filters.get("dataset")):
            return False
        if not accepted(record.source, filters.get("source")):
            return False
        if not accepted(record.content_type, filters.get("content_type")):
            return False
        if filters.get("playable") is True and not record.is_playable():
            return False

        max_duration = _safe_float(filters.get("max_duration"))
        min_duration = _safe_float(filters.get("min_duration"))
        if max_duration is not None and (
            record.duration_seconds is None or record.duration_seconds > max_duration
        ):
            return False
        if min_duration is not None and (
            record.duration_seconds is None or record.duration_seconds < min_duration
        ):
            return False

        doc_terms = set(_tokenize(record.display_text))
        brands = filters.get("brands") or filters.get("required_brands") or []
        if isinstance(brands, str):
            brands = [brands]
        if brands and not all(
            tokens and tokens[0] in doc_terms
            for tokens in (_tokenize(str(brand)) for brand in brands)
        ):
            return False
        excluded = filters.get("excluded_brands") or []
        if isinstance(excluded, str):
            excluded = [excluded]
        if any(
            tokens and tokens[0] in doc_terms
            for tokens in (_tokenize(str(brand)) for brand in excluded)
        ):
            return False
        return True

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return metadata-relevant videos, never arbitrary positive-score hits."""
        if self._bm25 is None or not self.records or top_k <= 0:
            return []

        filters = filters or {}
        terms = _unique(
            term
            for term in _tokenize(query)
            if term not in _STOP_WORDS
            and not (term.isdigit() and filters.get("max_duration") is not None)
        )
        if not terms:
            return []
        specific_terms = [term for term in terms if term not in _GENERIC_MEDIA_TERMS]
        generic_terms = [term for term in terms if term in _GENERIC_MEDIA_TERMS]
        required_specific = (
            len(specific_terms)
            if 0 < len(specific_terms) <= 3
            else math.ceil(len(specific_terms) / 2)
        )

        expanded_query = _unique(
            expanded for term in terms for expanded in sorted(self._term_group(term))
        )
        raw_scores = self._bm25.get_scores(expanded_query)
        max_bm25 = max((float(score) for score in raw_scores if score > 0), default=0.0)
        ranked: list[tuple[float, str, dict[str, Any]]] = []

        for index, record in enumerate(self.records):
            if not self._matches_filters(record, filters):
                continue
            advertisement_requested = "advertisement" in generic_terms
            social_media_requested = "influencer" in generic_terms or "ugc" in generic_terms or (
                "social" in generic_terms and "media" in generic_terms
            )
            if (
                advertisement_requested
                and not social_media_requested
                and record.content_type != "advertisement"
            ):
                continue
            if (
                social_media_requested
                and not advertisement_requested
                and record.content_type != "social_media"
            ):
                continue
            doc_terms = set(self._tokenized_docs[index])
            matched_specific = [
                term for term in specific_terms if self._term_group(term) & doc_terms
            ]
            matched_generic = [term for term in generic_terms if term in doc_terms]

            if specific_terms and len(matched_specific) < required_specific:
                continue
            if not specific_terms and generic_terms and not matched_generic:
                continue

            coverage_terms = specific_terms or generic_terms
            matched_terms = matched_specific or matched_generic
            coverage = len(matched_terms) / max(1, len(coverage_terms))
            bm25 = max(0.0, float(raw_scores[index]))
            bm25_normalized = bm25 / max_bm25 if max_bm25 else 0.0
            phrase = " ".join(specific_terms)
            doc_phrase = " ".join(self._tokenized_docs[index])
            phrase_boost = 1.0 if phrase and phrase in doc_phrase else 0.0
            score = round(
                min(1.0, 0.65 * coverage + 0.30 * bm25_normalized + 0.05 * phrase_boost),
                4,
            )
            result = {
                "clip_id": f"clip-{record.video_id}",
                "video_id": record.video_id,
                "file_path": record.file_path,
                "score": score,
                "title": record.title,
                "description": record.description,
                "source": record.source,
                "source_url": record.source_url,
                "source_page": record.source_page,
                "asset_name": record.asset_name,
                "dataset": record.dataset,
                "content_type": record.content_type,
                "mime_type": record.mime_type,
                "annotations": dict(record.annotations),
                "start_time": 0.0,
                "end_time": float(record.duration_seconds or 30.0),
                "relevance_reason": (
                    f"Matched {', '.join(matched_terms)} in {record.dataset} metadata"
                ),
                "retriever": "bm25-metadata",
            }
            ranked.append((score, record.video_id, result))

        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [result for _, _, result in ranked[:top_k]]

    def get(self, video_id: str) -> VideoRecord | None:
        """Return the exact record for a stable identifier when present."""
        return self._by_video_id.get(video_id)

    def list_videos(self) -> list[dict[str, Any]]:
        """Return public metadata and preview availability for every record."""
        return [
            {
                "video_id": record.video_id,
                "title": record.title,
                "creator": record.creator,
                "source": record.source,
                "source_url": record.source_url,
                "source_page": record.source_page,
                "asset_name": record.asset_name,
                "dataset": record.dataset,
                "content_type": record.content_type,
                "mime_type": record.mime_type,
                "duration_seconds": record.duration_seconds,
                "playable": record.is_playable(),
            }
            for record in self.records
        ]


catalog = VideoCatalog()
