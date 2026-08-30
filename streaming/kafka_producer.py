"""Kafka producer for streaming."""

from typing import Any


class KafkaProducer:
    """Mock Kafka producer."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers

    def send(self, topic: str, value: dict[str, Any]) -> None:
        """Send message."""
        pass


kafka_producer = KafkaProducer()