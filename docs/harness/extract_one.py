"""Extract ONE url with a hard cap, printing a compact triage line.

Runs the deterministic core extractor directly (NOT through the MCP server, so a
wedged server can't stall us) inside a per-call asyncio timeout. The caller ALSO
wraps this in a shell `timeout` so a hung Playwright can never hang forever.

Usage:  .venv/bin/python docs/harness/extract_one.py <url> [deadline_s]
"""
import asyncio
import json
import sys

from core.extractor.service import ExtractorService
from core.extractor.models import ExtractOptions


async def _run(url: str, deadline: float):
    svc = ExtractorService()
    opts = ExtractOptions(
        settle_ms=4000,
        nav_timeout_ms=30000,
        max_images=120,
        max_fonts=20,
    )
    return await asyncio.wait_for(svc.extract(url, opts), timeout=deadline)


def main():
    url = sys.argv[1]
    deadline = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
    try:
        res = asyncio.run(_run(url, deadline))
    except asyncio.TimeoutError:
        print(json.dumps({"url": url, "ok": False, "error": f"timeout after {deadline}s"}))
        return
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"url": url, "ok": False, "error": f"{type(exc).__name__}: {exc}"}))
        return

    s = res.summary if hasattr(res, "summary") else res
    # summary may be a pydantic model or dict-like; normalize
    g = (lambda k, d=None: getattr(s, k, None) if not isinstance(s, dict) else s.get(k, d))
    cls = g("site_classification") or {}
    if not isinstance(cls, dict):
        cls = {"site_type": getattr(cls, "site_type", None),
               "can_clone_well": getattr(cls, "can_clone_well", None),
               "ceiling": getattr(cls, "ceiling", None)}
    out = {
        "url": url,
        "ok": True,
        "source_id": g("source_id"),
        "title": g("title"),
        "success": g("success"),
        "page_height": g("page_height"),
        "block_count": g("block_count"),
        "total_elements": g("total_elements"),
        "site_type": cls.get("site_type"),
        "can_clone_well": cls.get("can_clone_well"),
        "ceiling": cls.get("ceiling"),
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
