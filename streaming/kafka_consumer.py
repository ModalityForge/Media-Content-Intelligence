"""Kafka consumer for streaming."""

from typing import Any


class KafkaConsumer:
    """Mock Kafka consumer."""

    def __init__(self, bootstrap_servers: str = "localhost:9092", topic: str = ""):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

    def consume(self) -> dict[str, Any]:
        """Consume message."""
        return {}


kafka_consumer = KafkaConsumer()