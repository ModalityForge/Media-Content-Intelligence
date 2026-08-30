"""OCR processor component."""

from app.models import OCRSegment


class OCRProcessor:
    """Process OCR from video frames."""

    def process_frame(self, frame_path: str) -> list[OCRSegment]:
        """Process single frame for OCR."""
        return [
            OCRSegment(
                segment_id="ocr-1",
                video_id="video-001",
                frame_time=10.0,
                text="LIVE",
                bounding_box=(100, 50, 200, 80),
                confidence=0.95,
            )
        ]

    def process_clip(self, clip_id: str) -> list[OCRSegment]:
        """Process entire clip."""
        return []


ocr_processor = OCRProcessor()