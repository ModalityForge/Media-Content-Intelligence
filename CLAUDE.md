# CLAUDE.md - Coding Agent Instructions

You are an expert senior Python engineer and agentic AI system architect working on MCI-v2.0: Media Content Intelligence platform.

## Architecture Principles

1. **Preserve MCI-v2.0 Architecture**: One Media Orchestrator Agent, One Evidence Validator Agent
2. **No Unnecessary Micro-Agents**: Logo, talent, action, rights, sponsorship detection must be MCP tools, not separate agents
3. **Add New Capabilities as MCP Tools First**: Before creating new agents, implement as MCP tool bundles
4. **Use A2A Only for Autonomous Agents**: Only between Media Orchestrator and Evidence Validator for stateful, long-running tasks

## Coding Requirements

1. **All Tools Must Have Typed Schemas**: Use input_schema and output_schema in BaseMCPTool
2. **All Agent Decisions Must Be Traceable**: Include trace_id throughout
3. **All Rights Decisions Must Be Auditable**: Log to audit_logger
4. **Tests Required for New Tools**: Add pytest tests in tests/ directory
5. **Type Hints and Docstrings**: Required for all new code

## Extension Pattern

To add a new capability:

1. Create MCP tool in `tools/` (e.g., `tools/new_capability_tools.py`)
2. Register in `tools/mcp_registry.py`
3. Add tool to orchestrator's `plan_tool_calls()` in `agents/media_orchestrator.py`
4. Add tests in `tests/test_tools.py`
5. Document in `docs/mcp_tools.md`

## Model Integration

When adding real models:
1. Create wrapper in `components/` (e.g., `components/vision/new_model.py`)
2. Add mock fallback in `tools/` for development
3. Configuration flag in `app/config.py` (ENABLE_MOCK_MODELS)

## Testing

- All tools must have basic functionality tests
- Agent orchestration must test tool call sequence
- Rights/brand safety must test policy enforcement
- Run `pytest` before committing

## Dependencies

Keep requirements.txt minimal - use optional dependencies for heavy ML models that can be mocked in development.