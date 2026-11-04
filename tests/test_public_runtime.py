"""Contract tests for the deliberately limited public application surface.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from __future__ import annotations

import subprocess
import sys
import ast
from pathlib import Path

from app.main import app
from app.schemas import (
    CandidateClip,
    EvidenceValidationResult,
    FeedbackRequest,
    HealthResponse,
    SearchRequest,
    SearchResponse,
    ValidationResultItem,
)
from tools.mcp_registry import get_registry


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Prosenjit Banerjee <prosenjit.banerjee@gmail.com>"
PUBLIC_RUNTIME_FILES = [
    "app/__init__.py",
    "app/config.py",
    "app/dependencies.py",
    "app/main.py",
    "app/schemas.py",
    "api/__init__.py",
    "api/routes/__init__.py",
    "api/routes/feedback.py",
    "api/routes/health.py",
    "api/routes/search.py",
    "api/routes/videos.py",
    "agents/__init__.py",
    "agents/a2a_protocol.py",
    "agents/evidence_validator.py",
    "agents/media_orchestrator.py",
    "agents/state.py",
    "services/__init__.py",
    "services/hyde_generator.py",
    "services/query_rewriter.py",
    "tools/__init__.py",
    "tools/base.py",
    "tools/mcp_registry.py",
    "tools/retrieval_tools.py",
    "storage/__init__.py",
    "storage/video_catalog.py",
    "security/__init__.py",
    "security/input_guard.py",
    "security/output_guard.py",
    "observability/__init__.py",
    "observability/logger.py",
    "observability/metrics.py",
    "frontend/app.py",
    "scripts/check_publish_safety.py",
    "scripts/healthcheck.py",
]


def test_public_api_excludes_unimplemented_operational_routes() -> None:
    """The public build exposes only routes supported by the retained runtime."""
    paths = set(app.openapi()["paths"])

    assert "/search" in paths
    assert "/videos/{video_id}" in paths
    assert "/health" in paths
    assert "/feedback" in paths
    assert not any(path.startswith("/ingest") for path in paths)
    assert not any(path.startswith("/clips") for path in paths)
    assert not any(path.startswith("/alerts") for path in paths)


def test_public_tool_registry_contains_only_deterministic_retrieval_tools() -> None:
    """Random mock model tools must not be registered in the public runtime."""
    tool_names = {tool["name"] for tool in get_registry().list_tools()}

    assert tool_names == {"vector_search", "bm25_search", "rrf_fusion"}


def test_importing_public_app_does_not_load_local_only_modules() -> None:
    """A clean public checkout must not import modules that will remain local."""
    local_only_modules = {
        "agents.graph",
        "observability.trace",
        "services.rag_pipeline",
        "storage.vector_db",
        "security.audit_logger",
        "tools.vision_tools",
        "tools.audio_ocr_tools",
        "tools.policy_tools",
        "tools.output_tools",
    }
    probe = (
        "import app.main,sys; "
        f"blocked={sorted(local_only_modules)!r}; "
        "loaded=sorted(set(blocked).intersection(sys.modules)); "
        "assert not loaded, loaded"
    )

    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout


def test_runtime_boundary_files_identify_the_author() -> None:
    """Files defining the public boundary carry explicit ownership metadata."""
    boundary_files = [
        "app/main.py",
        "agents/__init__.py",
        "api/routes/__init__.py",
        "observability/__init__.py",
        "security/__init__.py",
        "services/__init__.py",
        "storage/__init__.py",
        "tools/mcp_registry.py",
    ]

    for relative_path in boundary_files:
        source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert AUTHOR in source, relative_path


def test_every_public_runtime_symbol_is_documented_and_attributed() -> None:
    """Retained modules and their symbols explain ownership and behaviour."""
    for relative_path in PUBLIC_RUNTIME_FILES:
        source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=relative_path)
        module_docstring = ast.get_docstring(tree) or ""

        assert AUTHOR in module_docstring, relative_path
        assert len(module_docstring) >= 80, relative_path

        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node) or ""
                assert len(docstring.strip()) >= 20, (
                    f"{relative_path}:{node.lineno} {node.name}"
                )


def test_public_api_schema_fields_explain_their_contract() -> None:
    """Every client-visible field contributes a useful OpenAPI description."""
    public_models = [
        SearchRequest,
        CandidateClip,
        SearchResponse,
        ValidationResultItem,
        EvidenceValidationResult,
        FeedbackRequest,
        HealthResponse,
    ]

    for model in public_models:
        for name, field in model.model_fields.items():
            assert field.description and len(field.description) >= 12, (
                f"{model.__name__}.{name}"
            )
