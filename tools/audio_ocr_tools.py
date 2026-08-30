"""Audio and OCR MCP tools."""

import random
import uuid
from typing import Any

from tools.base import BaseMCPTool


class ASRTool(BaseMCPTool):
    """Automatic Speech Recognition tool."""

    name = "asr"
    description = "Transcribe audio from video clips"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            "language": {"type": "string", "default": "en"},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"transcripts": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute ASR."""
        clip_ids = input_data.get("clip_ids", [])
        language = input_data.get("language", "en")

        sample_phrases = [
            "Great goal by the home team!",
            "The crowd goes wild!",
            "An incredible save by the goalkeeper.",
            "That's a fantastic pass!",
            "What a match this has been!",
        ]

        transcripts = []
        for clip_id in clip_ids:
            num_segments = random.randint(2, 5)
            for i in range(num_segments):
                transcripts.append(
                    {
                        "clip_id": clip_id,
                        "segment_id": f"{clip_id}-seg-{i}",
                        "start_time": round(i * 6, 2),
                        "end_time": round((i + 1) * 6, 2),
                        "text": random.choice(sample_phrases),
                        "language": language,
                        "confidence": round(random.uniform(0.8, 0.98), 2),
                    }
                )

        return {"transcripts": transcripts, "model": "mock-whisper"}


class OCRTool(BaseMCPTool):
    """Optical Character Recognition tool."""

    name = "ocr"
    description = "Extract text from video frames"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
            " languages": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"texts": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute OCR."""
        clip_ids = input_data.get("clip_ids", [])

        sample_texts = [
            "LIVE",
            "Score: 2-1",
            "Stadium Name",
            "Sponsor Brand",
            "Match Time: 45:00",
        ]

        texts = []
        for clip_id in clip_ids:
            for _ in range(random.randint(1, 3)):
                texts.append(
                    {
                        "clip_id": clip_id,
                        "text": random.choice(sample_texts),
                        "timestamp": round(random.uniform(0, 30), 2),
                        "confidence": round(random.uniform(0.75, 0.95), 2),
                        "bounding_box": [100, 100, 300, 50],
                    }
                )

        return {"texts": texts, "model": "mock-ocr"}


class CaptionGenerationTool(BaseMCPTool):
    """Caption generation tool."""

    name = "caption_generation"
    description = "Generate video captions"
    input_schema = {
        "type": "object",
        "properties": {
            "clip_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["clip_ids"],
    }
    output_schema = {"type": "object", "properties": {"captions": {"type": "array"}}}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute caption generation."""
        clip_ids = input_data.get("clip_ids", [])

        sample_captions = [
            "A soccer player celebrates after scoring a goal.",
            "The athlete drinks from a branded bottle.",
            "Fans cheer in the stadium during an exciting match.",
            "The player shows the team logo on their jersey.",
            "A close-up of the scoreboard showing the current time.",
        ]

        captions = []
        for clip_id in clip_ids:
            captions.append(
                {
                    "clip_id": clip_id,
                    "caption": random.choice(sample_captions),
                    "timestamp_start": 0,
                    "timestamp_end": 30,
                }
            )

        return {"captions": captions, "model": "mock-video-llava"}