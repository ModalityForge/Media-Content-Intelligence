"""Stream loader component."""

from typing import Any


class StreamLoader:
    """Load live streams."""

    def connect(self, stream_url: str) -> dict[str, Any]:
        """Connect to a stream."""
        return {
            "stream_url": stream_url,
            "status": "connected",
            "latency_ms": 500,
        }

    def disconnect(self, stream_url: str) -> None:
        """Disconnect from stream."""
        pass


stream_loader = StreamLoader()