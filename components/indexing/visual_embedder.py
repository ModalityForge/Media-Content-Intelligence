"""Visual embedder component."""

import random
from app.models import FrameEmbedding


class VisualEmbedder:
    """Generate visual embeddings."""

    def __init__(self, model_name: str = "clip-vit-b32"):
        self.model_name = model_name

    def embed_frame(self, frame_path: str) -> list[float]:
        """Embed a single frame."""
        return [random.random() for _ in range(512)]

    def embed_clip(self, clip_id: str) -> list[FrameEmbedding]:
        """Embed entire clip."""
        return []


visual_embedder = VisualEmbedder()