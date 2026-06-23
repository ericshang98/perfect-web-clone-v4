"""Perfect Web Clone v3 — MCP server entry point.

Creates the single ``FastMCP`` server named ``"pwc3"`` and registers every
deterministic tool from :mod:`mcp_server.tools` (extraction, sandbox,
build/deploy), then serves them over **stdio** so Claude Code can connect via
``.mcp.json``.

Run it with::

    python -m mcp_server.server

THE IRON RULE
-------------
Nothing in this server — or in any tool it registers — calls an LLM / Anthropic /
OpenAI / any model API. The tools are pure, deterministic Python: they render,
chunk, write the sandbox, execute, screenshot, build, diagnose, and (optionally)
deploy. ALL reasoning — writing React code, judging whether the clone looks like
the original, deciding what to fix — happens in Claude Code, the brain. This
server is only the wiring that exposes the hands and eyes.

Registered tools (17 total)
---------------------------
Extraction / chunking (``tools.extraction``):
    * ``extract_page``        — Playwright render a URL → ``source_id`` + summary.
    * ``get_section_plan``    — deterministic per-section chunking plan.
    * ``get_section_data``    — full, self-contained data for one section.

Sandbox (``tools.sandbox``):
    * ``sandbox_write_file``  — write into the sandbox (namespace-isolated).
    * ``sandbox_read_file``   — read a text file from the sandbox.
    * ``sandbox_list_files``  — list files matching a glob.
    * ``sandbox_exec``        — run a shell command in the sandbox work dir.
    * ``start_preview``       — start the Vite dev server, return its URL.
    * ``preview_status``      — report the dev-server URL / running state.
    * ``preview_screenshot``  — capture the preview as an inline image.

Build / assemble / diagnose / deploy (``tools.build_deploy``):
    * ``assemble_project``    — deterministically stitch sections into App.jsx/index.css.
    * ``build_project``       — ``npm run build`` + reflect back build errors.
    * ``get_build_errors``    — three-layer (terminal/browser/static) error detection.
    * ``diagnose``            — aggregate structural health report.
    * ``deploy``              — OPTIONAL thin Cloudflare Pages publish (never auto).

Fidelity gates (``tools.verify``):
    * ``verify_links``        — deterministic check that each section kept its
      REAL links (no fabricated ``#`` / ``javascript:`` placeholders).
    * ``verify_assets``       — deterministic check that each section uses the
      DOWNLOADED local assets instead of hotlinking the live origin.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_server.tools import build_deploy, extraction, sandbox, verify

# --------------------------------------------------------------------------- #
# The single shared FastMCP instance. Tools attach to this object.
# --------------------------------------------------------------------------- #
mcp = FastMCP("pwc3")


def register_tools(server: FastMCP) -> list[str]:
    """Register every deterministic tool on ``server`` and return their names.

    Three sources, three registration shapes (we honor each module's own API):

    * ``tools.extraction``   — exposes plain functions, no ``register`` helper;
      we attach each with ``server.tool()`` directly.
    * ``tools.sandbox``      — provides its own ``register(mcp)`` helper; we call it
      so the sandbox toolset is wired exactly as that module intends.
    * ``tools.build_deploy`` — exposes plain functions, no ``register`` helper;
      we attach each with ``server.tool()`` directly.

    Returns:
        The ordered list of registered tool names (for logging / verification).
    """
    registered: list[str] = []

    # 1) Extraction / chunking tools — registered directly.
    extraction_tools = (
        extraction.extract_page,
        extraction.get_section_plan,
        extraction.get_section_data,
    )
    for fn in extraction_tools:
        server.tool()(fn)
        registered.append(fn.__name__)

    # 2) Sandbox tools — registered via the module's own register() helper, which
    #    attaches all seven sandbox functions. We mirror its known set for the
    #    returned name list so callers see the full inventory.
    sandbox.register(server)
    registered.extend(
        [
            "sandbox_write_file",
            "sandbox_read_file",
            "sandbox_list_files",
            "sandbox_exec",
            "start_preview",
            "preview_status",
            "preview_screenshot",
        ]
    )

    # 3) Build / assemble / diagnose / deploy tools — registered directly.
    build_deploy_tools = (
        build_deploy.assemble_project,
        build_deploy.build_project,
        build_deploy.get_build_errors,
        build_deploy.diagnose,
        build_deploy.deploy,
    )
    for fn in build_deploy_tools:
        server.tool()(fn)
        registered.append(fn.__name__)

    # 4) Fidelity gates — deterministic verification of the generated clone.
    for fn in (verify.verify_links, verify.verify_assets):
        server.tool()(fn)
        registered.append(fn.__name__)

    return registered


# Register at import time so the tools are present whether the server is started
# via ``python -m mcp_server.server`` or imported elsewhere (e.g. tests).
REGISTERED_TOOLS = register_tools(mcp)


def main() -> None:
    """Console-script / module entry point: serve the tools over stdio.

    Wired by both ``python -m mcp_server.server`` (see ``__main__`` below) and the
    ``pwc3-mcp`` console script in ``pyproject.toml``. Claude Code connects to this
    process over stdio per ``.mcp.json``.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
