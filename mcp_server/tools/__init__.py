"""Deterministic MCP tool implementations for Perfect Web Clone v3.

Each module here groups a set of pure, no-LLM tool functions that
:mod:`mcp_server.server` registers on the shared ``FastMCP`` instance:

* :mod:`mcp_server.tools.extraction`   — ``extract_page`` / ``get_section_plan`` /
  ``get_section_data`` (Playwright render + the deterministic section-chunking
  "ace card").
* :mod:`mcp_server.tools.sandbox`      — ``sandbox_write_file`` / ``sandbox_read_file`` /
  ``sandbox_list_files`` / ``sandbox_exec`` / ``start_preview`` / ``preview_status`` /
  ``preview_screenshot`` (the BoxLite sandbox surface, with namespace isolation).
* :mod:`mcp_server.tools.build_deploy` — ``assemble_project`` / ``build_project`` /
  ``get_build_errors`` / ``diagnose`` / ``deploy`` (assembly, build gate, three-layer
  error detection, optional Cloudflare Pages deploy).

THE IRON RULE: no module here calls an LLM / Anthropic / OpenAI / any model API.
"""

__all__ = ["extraction", "sandbox", "build_deploy"]
