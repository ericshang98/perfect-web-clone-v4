"""Perfect Web Clone v3 — MCP server package.

This package exposes the deterministic MCP toolbelt that Claude Code drives to
clone web pages. The single ``FastMCP`` instance lives in :mod:`mcp_server.server`
and is started over stdio via ``python -m mcp_server.server``.

THE IRON RULE: nothing in this package calls an LLM / Anthropic / OpenAI / any
model API. Every tool is pure, deterministic Python. All reasoning — writing
component code, judging fidelity, deciding what to fix — happens in Claude Code,
the brain. These tools are only the hands and eyes.
"""

__all__ = ["server"]
