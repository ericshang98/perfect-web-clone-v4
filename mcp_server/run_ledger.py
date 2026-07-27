"""Shared fail-closed helpers for source-scoped Harness run ownership."""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _normalize_url(value: str) -> str:
    parsed = urlsplit(str(value or "").strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.query,
            "",
        )
    )


async def require_owned_preview_url(
    sandbox: Any,
    requested_url: str | None,
) -> tuple[str | None, str | None]:
    """Resolve the sandbox preview and reject caller-selected foreign targets."""

    owned = str(
        getattr(getattr(sandbox, "state", None), "preview_url", None) or ""
    ).strip()
    if not owned and hasattr(sandbox, "read_file"):
        try:
            metadata = json.loads(
                await sandbox.read_file(".pwc/preview.json") or ""
            )
        except (json.JSONDecodeError, TypeError):
            metadata = {}
        if isinstance(metadata, dict):
            owned = str(metadata.get("url") or "").strip()
    if not owned:
        return None, "sandbox-owned preview URL is unavailable; start_preview first."
    requested = str(requested_url or "").strip()
    if requested and _normalize_url(requested) != _normalize_url(owned):
        return None, "requested URL does not match the sandbox-owned preview URL."
    return owned, None


__all__ = ["require_owned_preview_url"]
