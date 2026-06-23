"""Stage 3 driver (variant3d): reconnect to the section-populated sandbox,
assemble shared files, inject the site's REAL self-hosted Founders Grotesk fonts
+ the original :root tokens (generated from the extracted css.json), run the
fidelity gates, and build.

Usage:
    PYTHONPATH=. .venv/bin/python drivers/stage3_assemble_variant3d.py <source_id> [sandbox_id]
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from core.boxlite import sandbox_manager as sm
from core.boxlite.sandbox_manager import BoxLiteSandbox
from core.extractor.storage import SourceStore, default_storage_root
from mcp_server.tools.build_deploy import assemble_project, build_project
from mcp_server.tools.verify import verify_links, verify_assets

# Real self-hosted Founders Grotesk woff2 files (extractor downloaded them →
# assemble_project copies them into public/assets/fonts/).
F_LIGHT = "686c219df9bdb9fa5102f481_founders-grotesk-light.woff2"   # 300
F_REG = "686c219d89f15b050a6f238e_founders-grotesk-regular.woff2"  # 400
F_MED = "686c219da6746409f2240933_founders-grotesk-medium.woff2"   # 500


def _ff(fname, weight):
    return (
        f"@font-face{{font-family:'Founders Grotesk';"
        f"src:url('/assets/fonts/{fname}') format('woff2');"
        f"font-weight:{weight};font-style:normal;font-display:swap;}}\n"
    )


def build_root_tokens(source_dir: Path) -> str:
    """Reproduce the original :root custom properties from the extracted css.json,
    skipping Webflow's mangled `<deleted|...>` duplicate names."""
    css = json.loads((source_dir / "css.json").read_text(encoding="utf-8"))
    seen = {}
    for v in css.get("variables", []):
        name = v.get("name", "")
        if "<deleted" in name or v.get("scope") != ":root":
            continue
        # last write wins, matches cascade order
        seen[name] = v.get("value", "")
    lines = "".join(f"  {n}:{val};\n" for n, val in seen.items())
    return ":root{\n" + lines + "}\n"


def build_head(source_dir: Path) -> str:
    return (
        "<style>\n"
        + _ff(F_LIGHT, "300")
        + _ff(F_REG, "400")
        + _ff(F_MED, "500")
        # a few subagents may have guessed weights; Founders Grotesk only ships 300/400/500
        + _ff(F_MED, "600")
        + _ff(F_MED, "700")
        + build_root_tokens(source_dir)
        # base page: dark theme, light text, self-hosted display font.
        # overflow-x:clip + max-width:100vw kills the marquee/horizontal-line
        # overflow band on mobile (learned on db-longbow).
        + "  html,body{margin:0;padding:0;background:#000;color:#f5f3f0;\n"
        "    overflow-x:clip;max-width:100vw;\n"
        "    font-family:'Founders Grotesk',Arial,sans-serif;font-weight:400;\n"
        "    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;}\n"
        "  #root{overflow-x:clip;}\n"
        "  *{box-sizing:border-box;}\n"
        "  a{color:inherit;text-decoration:none;}\n"
        "</style>\n"
    )


def inject_head(work_dir: Path, source_dir: Path) -> str:
    html_path = work_dir / "index.html"
    html = html_path.read_text(encoding="utf-8")
    if "Founders Grotesk" in html:
        return "head already injected"
    html = html.replace(
        "<title>Perfect Web Clone v3</title>",
        "<title>VARIANT3D — Software that knits</title>",
    )
    html = html.replace("</head>", build_head(source_dir) + "</head>")
    html_path.write_text(html, encoding="utf-8")
    return "head injected (Founders Grotesk + :root tokens)"


async def main() -> None:
    sid = sys.argv[1]
    sbid = sys.argv[2] if len(sys.argv) > 2 else "variant3d"
    source_dir = SourceStore(sid, default_storage_root()).dir

    sb = BoxLiteSandbox(sbid)
    sm._sandboxes[sb.sandbox_id] = sb
    sm._singleton_id = sb.sandbox_id
    await sb.reconnect()
    print(f"[stage3] reconnected work_dir={sb.work_dir}")

    a = await assemble_project(sid)
    print(f"[stage3] ASSEMBLE ok={a['ok']} written={a['written_files']}")
    if a["missing_section_files"]:
        print(f"[stage3] MISSING section files: {a['missing_section_files']}")

    fdir = sb.work_dir / "public" / "assets" / "fonts"
    print(f"[stage3] public fonts present={fdir.exists()} "
          f"count={len(list(fdir.glob('*'))) if fdir.exists() else 0}")

    print("[stage3]", inject_head(sb.work_dir, source_dir))

    vl = await verify_links(sid)
    print(f"[stage3] VERIFY_LINKS ok={vl.get('ok')} :: {vl.get('summary')}")
    if not vl.get("ok"):
        print("   failing:", json.dumps(vl.get("failing"), ensure_ascii=False)[:1800])
        print("   unreadable:", vl.get("unreadable"))

    va = await verify_assets(sid)
    print(f"[stage3] VERIFY_ASSETS ok={va.get('ok')} :: {va.get('summary')}")
    if not va.get("ok"):
        print("   failing:", json.dumps(va.get("failing"), ensure_ascii=False)[:1800])
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
