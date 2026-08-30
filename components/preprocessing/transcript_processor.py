"""Transcript processor component."""

from app.models import TranscriptSegment


class TranscriptProcessor:
    """Process transcripts from video."""

    def process_audio(self, audio_path: str) -> list[TranscriptSegment]:
        """Process audio to transcript."""
        return [
            TranscriptSegment(
                segment_id="ts-1",
                video_id="video-001",
                start_time=0.0,
                end_time=5.0,
                text="Great goal by the home team!",
                language="en",
                confidence=0.9,
            )
        ]

    def align_timestamps(self, transcript: list[TranscriptSegment]) -> list[TranscriptSegment]:
        """Align transcript timestamps."""
        return transcript


transcript_processor = TranscriptProcessor()