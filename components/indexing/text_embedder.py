"""Text embedder component."""

import random


class TextEmbedder:
    """Generate text embeddings."""

    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """Embed text."""
        return [random.random() for _ in range(1536)]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed batch of texts."""
        return [self.embed_text(t) for t in texts]


text_embedder = TextEmbedder()
