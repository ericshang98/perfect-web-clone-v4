"""Stage 3 driver: reconnect to the section-populated sandbox, assemble the shared
files, inject global fonts, run the fidelity gates, and build.

Usage:
    PYTHONPATH=. .venv/bin/python drivers/stage3_assemble.py <source_id> [sandbox_id]
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from core.boxlite import sandbox_manager as sm
from core.boxlite.sandbox_manager import BoxLiteSandbox
from mcp_server.tools.build_deploy import assemble_project, build_project
from mcp_server.tools.verify import verify_links, verify_assets

GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@300;400;500;600;700&'
    'family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">\n'
    "<style>\n"
    "  html,body{margin:0;padding:0;background:#ffffff;color:#010703;\n"
    "    font-family:'Inter',ui-sans-serif,system-ui,-apple-system,sans-serif;\n"
    "    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;}\n"
    "  *{box-sizing:border-box;}\n"
    "</style>\n"
)


def inject_fonts(work_dir: Path) -> str:
    """Add Google Fonts (Inter + Lora) + base body styles to index.html <head>."""
    html_path = work_dir / "index.html"
    html = html_path.read_text(encoding="utf-8")
    if "fonts.googleapis.com" in html:
        return "fonts already present"
    # also set a real page title
    html = html.replace(
        "<title>Perfect Web Clone v3</title>",
        "<title>Novu | Talk your day. Own your time.</title>",
    )
    html = html.replace("</head>", GOOGLE_FONTS + "</head>")
    html_path.write_text(html, encoding="utf-8")
    return "fonts injected"


async def main() -> None:
    sid = sys.argv[1]
    sbid = sys.argv[2] if len(sys.argv) > 2 else "withnovu"

    sb = BoxLiteSandbox(sbid)
    sm._sandboxes[sb.sandbox_id] = sb
    sm._singleton_id = sb.sandbox_id
    await sb.reconnect()
    print(f"[stage3] reconnected work_dir={sb.work_dir}")

    a = await assemble_project(sid)
    print(f"[stage3] ASSEMBLE ok={a['ok']} written={a['written_files']}")
    if a["missing_section_files"]:
        print(f"[stage3] MISSING section files: {a['missing_section_files']}")

    print("[stage3]", inject_fonts(sb.work_dir))

    vl = await verify_links(sid)
    print(f"[stage3] VERIFY_LINKS ok={vl.get('ok')} :: {vl.get('summary')}")
    if not vl.get("ok"):
        print("   failing:", json.dumps(vl.get("failing"), ensure_ascii=False)[:1500])
        print("   unreadable:", vl.get("unreadable"))

    va = await verify_assets(sid)
    print(f"[stage3] VERIFY_ASSETS ok={va.get('ok')} :: {va.get('summary')}")
    if not va.get("ok"):
        print("   failing:", json.dumps(va.get("failing"), ensure_ascii=False)[:1500])
        print("   unreadable:", va.get("unreadable"))

    print("[stage3] building (npm install + vite build) ...", flush=True)
    b = await build_project()
    print(f"[stage3] BUILD success={b['success']} exit={b['exit_code']} dist={b['dist_dir']}")
    if not b["success"]:
        print("   ERRORS:", json.dumps(b["errors"], ensure_ascii=False)[:3000])
        print("   STDERR_TAIL:", b["stderr_tail"][-1500:])
        print("   STDOUT_TAIL:", b["stdout_tail"][-1000:])


if __name__ == "__main__":
    asyncio.run(main())
