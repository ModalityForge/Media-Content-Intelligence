"""Audio extraction component."""

import os
from typing import Any


class AudioExtractor:
    """Extract audio from video."""

    def __init__(self, output_dir: str = "./data/audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def extract_audio(self, video_path: str) -> str:
        """Extract audio track."""
        audio_path = os.path.join(self.output_dir, "audio.wav")
        return audio_path

    def extract_segment(self, video_path: str, start: float, end: float) -> str:
        """Extract audio segment."""
        return os.path.join(self.output_dir, f"audio_{start}_{end}.wav")


audio_extractor = AudioExtractor()