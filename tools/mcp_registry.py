"""MCP Tool Registry."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from tools.base import BaseMCPTool
from observability.logger import get_logger

logger = get_logger(__name__)


class MCPToolRegistry:
    """Registry for MCP-style tools."""

    def __init__(self):
        self._tools: dict[str, BaseMCPTool] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)

    def register(self, tool: BaseMCPTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.info("Registered tool", tool_name=tool.name, description=tool.description)

    def get_tool(self, name: str) -> BaseMCPTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
            }
            for tool in self._tools.values()
        ]

    def run_tool(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a tool synchronously."""
        start_time = time.time()
        tool = self.get_tool(name)

        if not tool:
            logger.error("Tool not found", tool_name=name)
            return {"error": f"Tool '{name}' not found"}

        try:
            if not tool.validate_input(payload):
                logger.warning("Invalid input for tool", tool_name=name, payload=payload)
                return {"error": "Invalid input"}

            result = tool.run(payload)
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "Tool executed",
                tool_name=name,
                duration_ms=round(duration_ms, 2),
            )

            return result

        except Exception as e:
            logger.error("Tool execution failed", tool_name=name, error=str(e))
            return {"error": str(e)}

    async def run_tool_async(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a tool asynchronously."""
        tool = self.get_tool(name)

        if not tool:
            return {"error": f"Tool '{name}' not found"}

        try:
            return await tool.arun(payload)
        except Exception as e:
            logger.error("Async tool execution failed", tool_name=name, error=str(e))
            return {"error": str(e)}

    def run_tools_parallel(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run multiple tools in parallel."""
        results = []

        if not tool_calls:
            return results

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            tasks = [
                self.run_tool_async(call["tool_name"], call["payload"])
                for call in tool_calls
            ]
            results = loop.run_until_complete(asyncio.gather(*tasks))
        finally:
            loop.close()

        return results


_global_registry: MCPToolRegistry | None = None


def get_registry() -> MCPToolRegistry:
    """Get the global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = MCPToolRegistry()
        _register_default_tools(_global_registry)
    return _global_registry


def _register_default_tools(registry: MCPToolRegistry) -> None:
    """Register default tools."""
    from tools.retrieval_tools import (
        VectorSearchTool,
        BM25SearchTool,
        MetadataFilterTool,
        RRFFusionTool,
        RerankResultsTool,
    )
    from tools.vision_tools import (
        ObjectDetectionTool,
        LogoDetectionTool,
        TalentMatchTool,
        ActionClassificationTool,
        TrackingTool,
        PoseEstimationTool,
    )
    from tools.audio_ocr_tools import ASRTool, OCRTool, CaptionGenerationTool
    from tools.policy_tools import (
        RightsCheckTool,
        SponsorshipPolicyTool,
        ExclusionCheckTool,
        ContentRatingTool,
    )
    from tools.output_tools import (
        ClipGenerationTool,
        FaceBlurTool,
        ExportClipTool,
        SendAlertTool,
    )

    for tool_cls in [
        VectorSearchTool,
        BM25SearchTool,
        MetadataFilterTool,
        RRFFusionTool,
        RerankResultsTool,
        ObjectDetectionTool,
        LogoDetectionTool,
        TalentMatchTool,
        ActionClassificationTool,
        TrackingTool,
        PoseEstimationTool,
        ASRTool,
        OCRTool,
        CaptionGenerationTool,
        RightsCheckTool,
        SponsorshipPolicyTool,
        ExclusionCheckTool,
        ContentRatingTool,
        ClipGenerationTool,
        FaceBlurTool,
        ExportClipTool,
        SendAlertTool,
    ]:
        registry.register(tool_cls())