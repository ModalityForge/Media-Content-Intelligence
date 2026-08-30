"""Base MCP Tool class."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseMCPTool(ABC, Generic[T]):
    """Base class for MCP-style tools."""

    name: str = ""
    description: str = ""
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Synchronous tool execution."""
        pass

    async def arun(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Asynchronous tool execution. Default implementation calls run."""
        return self.run(input_data)

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input against input schema."""
        required_fields = self.input_schema.get("required", [])
        for field in required_fields:
            if field not in input_data:
                return False
        return True

    def get_schema(self) -> dict[str, Any]:
        """Get the tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }