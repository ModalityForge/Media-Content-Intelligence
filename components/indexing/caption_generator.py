"""Caption generator component."""

from typing import Any


class CaptionGenerator:
    """Generate video captions."""

    def generate_caption(self, clip_id: str) -> str:
        """Generate caption for clip."""
        return "A video clip showing sports action with brand visibility."

    def generate_captions_batch(self, clip_ids: list[str]) -> dict[str, str]:
        """Generate captions for multiple clips."""
        return {cid: self.generate_caption(cid) for cid in clip_ids}


caption_generator = CaptionGenerator()