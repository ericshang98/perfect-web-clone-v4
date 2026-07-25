"""
Sandbox MCP tools for Perfect Web Clone v4.

This module exposes the BoxLite sandbox (``core.boxlite``) to Claude Code as a
set of MCP tools over stdio. It is a thin, **purely deterministic** wrapper: it
threads arguments through to the singleton sandbox, applies the section
isolation contract on writes, and shapes return values into JSON-serializable
dicts (or inline images, for screenshots) that Claude Code can read directly.

THE IRON RULE
-------------
Nothing in this module calls an LLM / Anthropic / OpenAI API. There is no model
inference here at all. Every "decision" is a string check, a filesystem
operation, or a subprocess call. All reasoning — writing the React code, judging
whether the clone looks like the original, deciding what to fix — happens in
Claude Code, which drives these tools. The tools are the hands and eyes; Claude
Code is the brain.

Tools registered by :func:`register`:

* ``sandbox_write_file(path, content, namespace?)`` — write into the sandbox,
  gated by ``contracts.validate_write_path`` when a ``namespace`` is supplied so
  section authoring cannot write outside
  ``src/components/sections/{namespace}/``.
* ``sandbox_read_file(path)`` — read a text file from the sandbox.
* ``sandbox_list_files(glob?)`` — list files matching a glob.
* ``sandbox_exec(cmd, timeout?, background?)`` — run a shell command in the
  sandbox work dir.
* ``start_preview()`` — start the Vite dev server (install + ``npm run dev``).
* ``preview_status()`` — report the current dev-server URL / running state.
* ``preview_screenshot(path?, viewport?, full_page?)`` — capture the preview as
  an inline image so Claude Code can see it for fidelity comparison.

Registration pattern
---------------------
``server.py`` owns the single ``FastMCP`` instance and the shared sandbox
lifecycle (``create_sandbox``). It calls :func:`register(mcp)` from this module
to attach these tools. Each tool lazily resolves the active singleton sandbox
via ``core.boxlite.get_sandbox`` and returns a clear, self-correcting error
string if no sandbox has been created yet — so a missing ``create_sandbox()``
never crashes the tool call, it just tells Claude Code what to do.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from core.boxlite import BoxLiteSandbox, get_sandbox
from mcp_server.contracts import validate_write_path

# ``Image`` is FastMCP's helper for returning an inline image content block to
# the client. Imported lazily-tolerantly so importing this module never hard
# fails if the optional helper path changes across mcp versions.
try:  # pragma: no cover - import shape varies by mcp version
    from mcp.server.fastmcp.utilities.types import Image
except Exception:  # pragma: no cover
    try:
        from mcp.server.fastmcp import Image  # type: ignore
    except Exception:  # pragma: no cover
        Image = None  # type: ignore


# ---------------------------------------------------------------------------
# Internal helpers (no LLM, no network)
# ---------------------------------------------------------------------------

def _resolve_sandbox() -> BoxLiteSandbox:
    """Return the active singleton sandbox or raise a self-correcting error.

    Raising here is converted by each tool into a structured error payload, so
    Claude Code is told exactly what to do ("call create_sandbox() first")
    instead of seeing an opaque traceback.
    """
    sb = get_sandbox()
    if sb is None:
        raise RuntimeError(
            "No sandbox exists yet. Create one before using sandbox tools "
            "(the clone flow's setup step calls create_sandbox())."
        )
    return sb


def _err(message: str) -> Dict[str, Any]:
    """Shape a deterministic, machine-readable error payload."""
    return {"ok": False, "error": message}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

async def sandbox_write_file(
    path: str,
    content: str,
    namespace: Optional[str] = None,
) -> Dict[str, Any]:
    """Write ``content`` to ``path`` inside the sandbox.

    Isolation gate: when ``namespace`` is provided, the section-scoped write is
    first validated by
    ``contracts.validate_write_path(namespace, path)``. That deterministic check
    enforces the section contract:

    * the path must live strictly inside ``src/components/sections/{namespace}/``;
    * shared / assembly files (``App.jsx``, ``main.jsx``, ``index.css``,
      ``package.json`` …) are rejected — only ``assemble_project()`` writes those;
    * ``..`` traversal and disallowed extensions are rejected.

    On rejection the file is NOT written and the contract's human-readable reason
    is returned so Claude Code can self-correct.

    When ``namespace`` is omitted the write is unrestricted — reserved for
    deterministic assembly/setup and harness-ledger writes, not section code.

    Args:
        path: Project-relative write path (e.g.
            ``src/components/sections/hero/Hero.jsx``). Leading ``/`` is allowed.
        content: Full text content to write (overwrites any existing file).
        namespace: The writing section's namespace. When set, the isolation
            contract is enforced; when ``None``, the write is unrestricted.

    Returns:
        ``{"ok": True, "path": <normalized path>, "bytes": <len>}`` on success,
        or ``{"ok": False, "error": <reason>}`` if rejected or the write failed.
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    write_path = path
    if namespace is not None:
        result = validate_write_path(namespace, path)
        if not result.ok:
            return _err(result.error)
        write_path = result.normalized_path

    ok = await sb.write_file(write_path, content)
    if not ok:
        return _err(f"Failed to write {write_path!r} (see sandbox logs).")
    return {"ok": True, "path": write_path, "bytes": len(content)}


async def sandbox_read_file(path: str) -> Dict[str, Any]:
    """Read the text content of ``path`` from the sandbox.

    Args:
        path: Project-relative file path (leading ``/`` allowed).

    Returns:
        ``{"ok": True, "path": ..., "content": <text>}`` on success, or
        ``{"ok": False, "error": ...}`` if the file does not exist / is not text.
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    content = await sb.read_file(path)
    if content is None:
        return _err(f"File not found or not readable as text: {path!r}.")
    return {"ok": True, "path": path, "content": content}


async def sandbox_list_files(glob: str = "**/*") -> Dict[str, Any]:
    """List sandbox files matching a glob pattern.

    Hidden entries and ``node_modules`` are excluded. Use ``**/*`` for the whole
    tree, or narrow it, e.g. ``src/components/sections/**/*.jsx``.

    Args:
        glob: Glob pattern relative to the sandbox work dir. Defaults to ``**/*``.

    Returns:
        ``{"ok": True, "glob": ..., "count": N, "files": [...]}`` where each entry
        is ``{"name", "path", "type", "size"}``.
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    entries = await sb.list_files(glob)
    files: List[Dict[str, Any]] = [
        {"name": e.name, "path": e.path, "type": e.type, "size": e.size}
        for e in entries
    ]
    return {"ok": True, "glob": glob, "count": len(files), "files": files}


async def sandbox_exec(
    cmd: str,
    timeout: float = 60.0,
    background: bool = False,
) -> Dict[str, Any]:
    """Run a shell command inside the sandbox work dir.

    Use this for ``npm install``, ``npm run build``, ``vite``, etc. Long-running
    processes (a dev server) should pass ``background=True``; prefer the dedicated
    ``start_preview()`` tool for the Vite dev server, though.

    Args:
        cmd: The shell command to execute.
        timeout: Max seconds to wait for a foreground command (ignored when
            ``background`` is True). Defaults to 60.
        background: If True, launch detached and return immediately.

    Returns:
        ``{"ok": <exit==0>, "exit_code", "stdout", "stderr", "duration_ms"}``.
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    result = await sb.exec(cmd, timeout=timeout, background=background)
    return {
        "ok": result.success,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration_ms": result.duration_ms,
    }


async def start_preview() -> Dict[str, Any]:
    """Start the Vite dev server and forward its fixed port.

    Deterministic sequence: free the port, ``npm install``, ``npm run dev`` in the
    background, then register the forwarded preview URL. Idempotent — an already
    running server is a no-op.

    Returns:
        ``{"ok", "url", "exit_code", "stdout", "stderr"}``. ``url`` is the
        localhost preview URL (or ``None`` if the server failed to come up).
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    result = await sb.start_preview()
    return {
        "ok": result.success,
        "url": sb.state.preview_url,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


async def preview_status() -> Dict[str, Any]:
    """Report the current preview / dev-server state.

    Returns:
        ``{"ok": True, "url", "is_loading", "has_error", "error_message"}``.
        ``url`` is non-null once the dev server is up.
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    state = sb.preview_status()
    return {
        "ok": True,
        "url": state.url,
        "is_loading": state.is_loading,
        "has_error": state.has_error,
        "error_message": state.error_message,
    }


async def preview_screenshot(
    path: Optional[str] = None,
    viewport: Literal["desktop", "mobile"] = "desktop",
    full_page: bool = False,
) -> Any:
    """Capture a screenshot of the running preview, returned as an inline image.

    The image is handed back to Claude Code as an inline image content block so
    it can be viewed directly and compared against the original page for the
    fidelity verify-loop. Capture is per-viewport (``desktop`` 1440x900 /
    ``mobile`` 390x844) so desktop and mobile fidelity can be checked separately.

    Requires the dev server to be running — call ``start_preview()`` first.

    Args:
        path: Optional project-relative path to also persist the JPEG bytes to
            disk inside the sandbox (e.g. ``shots/hero-desktop.jpg``).
        viewport: ``"desktop"`` or ``"mobile"``. Defaults to ``"desktop"``.
        full_page: Capture the full scrollable page rather than just the viewport.

    Returns:
        On success, a FastMCP ``Image`` (inline image) when the helper is
        available, otherwise a dict carrying ``base64_data``. On failure, a
        ``{"ok": False, "error": ...}`` dict (e.g. preview not started, Playwright
        missing).
    """
    try:
        sb = _resolve_sandbox()
    except RuntimeError as e:
        return _err(str(e))

    shot = await sb.screenshot(path=path, viewport=viewport, full_page=full_page)
    if shot.error or not shot.base64_data:
        return _err(shot.error or "Screenshot produced no image data.")

    if Image is not None:
        import base64

        try:
            return Image(
                data=base64.b64decode(shot.base64_data),
                format="jpeg",
            )
        except Exception:  # pragma: no cover - fall through to dict form
            pass

    # Fallback: hand back the raw payload so Claude Code still gets the bytes.
    return {
        "ok": True,
        "mime_type": shot.mime_type,
        "base64_data": shot.base64_data,
        "width": shot.width,
        "height": shot.height,
        "viewport": shot.viewport,
        "saved_path": shot.saved_path,
        "page_title": shot.page_title,
    }


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: Any) -> None:
    """Register all sandbox tools on the given ``FastMCP`` instance.

    ``server.py`` owns the single ``FastMCP`` object and calls this to attach the
    sandbox toolset. Each function above is registered under its own name with
    its docstring as the tool description.

    Args:
        mcp: A ``mcp.server.fastmcp.FastMCP`` instance.
    """
    mcp.tool()(sandbox_write_file)
    mcp.tool()(sandbox_read_file)
    mcp.tool()(sandbox_list_files)
    mcp.tool()(sandbox_exec)
    mcp.tool()(start_preview)
    mcp.tool()(preview_status)
    mcp.tool()(preview_screenshot)


__all__ = [
    "sandbox_write_file",
    "sandbox_read_file",
    "sandbox_list_files",
    "sandbox_exec",
    "start_preview",
    "preview_status",
    "preview_screenshot",
    "register",
]
