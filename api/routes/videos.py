"""Serve exact authorized local assets selected by catalog search.

The endpoint resolves only catalogued identifiers, validates byte ranges, and
returns explicit 404/416 failures instead of substituting an unrelated video.
It supports browser seeking while keeping reads bounded to the requested range.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

import mimetypes
import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from storage.video_catalog import catalog

router = APIRouter()

MEDIA_TYPES = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ogv": "video/ogg",
    ".ogg": "video/ogg",
    ".mov": "video/quicktime",
}

def _resolve_preview(video_id: str) -> str | None:
    """Resolve a video_id to a local, playable media file.

    Unknown or stale ids deliberately return no path. Serving an arbitrary
    fallback file makes a valid search result appear to contain the wrong
    video, which is worse than an explicit 404.
    """
    record = catalog.get(video_id)
    if record is not None and record.is_playable():
        return record.file_path

    return None


def _requested_range(range_header: str | None, file_size: int) -> tuple[int, int]:
    """Parse one HTTP byte range, falling back to the complete file."""
    if not range_header or not range_header.startswith("bytes="):
        return 0, file_size - 1
    value = range_header.removeprefix("bytes=").split(",", 1)[0]
    start_text, separator, end_text = value.partition("-")
    if not separator:
        return 0, file_size - 1
    try:
        if start_text:
            start = int(start_text)
            end = int(end_text) if end_text else file_size - 1
        else:
            suffix_length = int(end_text)
            start = max(0, file_size - suffix_length)
            end = file_size - 1
    except ValueError:
        return 0, file_size - 1
    return max(0, start), min(end, file_size - 1)


@router.get("/{video_id}")
async def get_video(video_id: str, request: Request) -> Response:
    """Stream a playable preview video for a clip's video_id."""
    path = _resolve_preview(video_id)

    if path is None or not os.path.isfile(path):
        raise HTTPException(
            status_code=404,
            detail=f"No preview video available for '{video_id}'",
        )

    ext = os.path.splitext(path)[1].lower()
    media_type = MEDIA_TYPES.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"
    file_size = os.path.getsize(path)
    start, end = _requested_range(request.headers.get("range"), file_size)
    if start >= file_size or end < start:
        raise HTTPException(status_code=416, detail="Requested range is not satisfiable")
    is_partial = start != 0 or end != file_size - 1
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Disposition": f'inline; filename="{os.path.basename(path)}"',
    }
    if is_partial:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    # Downloaded preview assets are capped at 5 MiB, so a bounded range read
    # avoids framework streaming deadlocks without creating memory pressure.
    with open(path, "rb") as handle:
        handle.seek(start)
        content = handle.read(end - start + 1)

    return Response(
        content=content,
        status_code=206 if is_partial else 200,
        media_type=media_type,
        headers=headers,
    )


@router.get("/")
async def list_videos() -> dict:
    """List available catalog videos and their streamability."""
    videos = catalog.list_videos()
    return {"count": len(videos), "videos": videos}
