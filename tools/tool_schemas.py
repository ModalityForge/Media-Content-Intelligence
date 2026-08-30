"""Tool schemas for MCP tools."""

SCHEMAS = {
    "vector_search": {
        "name": "vector_search",
        "description": "Search using vector embeddings",
        "input": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Number of results"},
                "filters": {"type": "object", "description": "Metadata filters"},
            },
            "required": ["query"],
        },
        "output": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clip_id": {"type": "string"},
                            "score": {"type": "number"},
                            "video_id": {"type": "string"},
                            "timestamp": {"type": "number"},
                        },
                    },
                },
            },
        },
    },
    "bm25_search": {
        "name": "bm25_search",
        "description": "Search using BM25 text retrieval",
        "input": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer"},
                "index_name": {"type": "string"},
            },
            "required": ["query"],
        },
        "output": {
            "type": "object",
            "properties": {
                "results": {"type": "array"},
            },
        },
    },
    "logo_detection": {
        "name": "logo_detection",
        "description": "Detect logos in video clips",
        "input": {
            "type": "object",
            "properties": {
                "clip_ids": {"type": "array", "items": {"type": "string"}},
                "target_brands": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["clip_ids"],
        },
        "output": {
            "type": "object",
            "properties": {
                "detections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clip_id": {"type": "string"},
                            "brand": {"type": "string"},
                            "confidence": {"type": "number"},
                            "timestamp": {"type": "number"},
                        },
                    },
                },
            },
        },
    },
    "rights_check": {
        "name": "rights_check",
        "description": "Check rights clearance for clips",
        "input": {
            "type": "object",
            "properties": {
                "clip_ids": {"type": "array", "items": {"type": "string"}},
                "territory": {"type": "string"},
                "usage_type": {"type": "string"},
                "duration_seconds": {"type": "number"},
            },
            "required": ["clip_ids", "territory"],
        },
        "output": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clip_id": {"type": "string"},
                            "rights_cleared": {"type": "boolean"},
                            "explanation": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
    "clip_generation": {
        "name": "clip_generation",
        "description": "Generate video clips from timestamps",
        "input": {
            "type": "object",
            "properties": {
                "video_id": {"type": "string"},
                "start_time": {"type": "number"},
                "end_time": {"type": "number"},
                "format": {"type": "string"},
            },
            "required": ["video_id", "start_time", "end_time"],
        },
        "output": {
            "type": "object",
            "properties": {
                "clip_id": {"type": "string"},
                "download_url": {"type": "string"},
            },
        },
    },
}


def get_schema(tool_name: str) -> dict:
    """Get schema for a tool."""
    return SCHEMAS.get(tool_name, {})