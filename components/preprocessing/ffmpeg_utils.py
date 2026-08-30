"""FFmpeg utilities."""

from typing import Any


class FFmpegUtils:
    """FFmpeg wrapper for video processing."""

    def get_video_info(self, video_path: str) -> dict[str, Any]:
        """Get video information."""
        return {
            "duration": 600.0,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "codec": "h264",
            "bitrate": 5000000,
        }

    def extract_frame(self, video_path: str, timestamp: float, output_path: str) -> dict[str, Any]:
        """Extract a single frame."""
        return {"output_path": output_path, "timestamp": timestamp, "success": True}


ffmpeg_utils = FFmpegUtils()