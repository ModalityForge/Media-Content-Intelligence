"""Tool tests."""

import pytest
from tools.mcp_registry import MCPToolRegistry
from tools.retrieval_tools import VectorSearchTool, BM25SearchTool
from tools.vision_tools import LogoDetectionTool
from tools.policy_tools import RightsCheckTool


def test_tool_registry_lists_tools():
    """Test tool registry lists tools."""
    registry = MCPToolRegistry()
    from tools.retrieval_tools import VectorSearchTool

    registry.register(VectorSearchTool())
    tools = registry.list_tools()
    assert len(tools) > 0
    assert any(t["name"] == "vector_search" for t in tools)


def test_vector_search_tool():
    """Test vector search tool."""
    tool = VectorSearchTool()
    result = tool.run({"query": "test", "top_k": 5})
    assert "results" in result
    assert len(result["results"]) > 0


def test_bm25_search_tool():
    """Test BM25 search tool."""
    tool = BM25SearchTool()
    result = tool.run({"query": "test", "top_k": 5})
    assert "results" in result


def test_logo_detection_tool():
    """Test logo detection tool."""
    tool = LogoDetectionTool()
    result = tool.run({"clip_ids": ["clip-001"], "target_brands": ["Adidas", "Nike"]})
    assert "detections" in result


def test_rights_check_tool():
    """Test rights check tool."""
    tool = RightsCheckTool()
    result = tool.run(
        {"clip_ids": ["clip-001"], "territory": "Germany", "duration_seconds": 30}
    )
    assert "results" in result
    assert result["results"][0]["rights_cleared"] is True