"""Stage 3 driver (db-longbow): reconnect to the section-populated sandbox,
assemble shared files, inject the site's REAL self-hosted fonts + :root tokens,
run the fidelity gates, and build.

Usage:
    PYTHONPATH=. .venv/bin/python drivers/stage3_assemble_dblongbow.py <source_id> [sandbox_id]
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

# Real Webflow font files (downloaded by the extractor → copied to public/assets/fonts/).
F_BEBAS = "68d5044c46e94386fcc9e255_BebasNeueBold.woff2"
F_GAR = "68cbd2d6d43d3e1c4dece3f9_EBGaramond-VariableFont_wght_0.woff2"
F_GAR_IT = "68cbd2d6ca5c9415efbde692_EBGaramond-Italic-VariableFont_wght_0.woff2"
F_MONO_R = "68d4fe3fc7192bf716553e5d_geist-mono-v4-latin-regular.woff2"
F_MONO_5 = "68d4fe3f9c866d51f0e22c43_geist-mono-v4-latin-500.woff2"
F_MONO_6 = "68d4fe3f0a03fb374f9e1144_geist-mono-v4-latin-600.woff2"


def _ff(family, fname, weight="400", style="normal"):
    return (
        f"@font-face{{font-family:'{family}';"
        f"src:url('/assets/fonts/{fname}') format('woff2');"
        f"font-weight:{weight};font-style:{style};font-display:swap;}}\n"
    )


HEAD = (
    # --- real self-hosted fonts (Bebas Neue / EB Garamond / Geist Mono) ---
    "<style>\n"
    + _ff("Bebas Neue", F_BEBAS, "400 700")
    + _ff("BebasNeueBold", F_BEBAS, "700")
    + _ff("Ebgaramond Variablefont Wght 0", F_GAR, "400 800", "normal")
    + _ff("Ebgaramond Variablefont Wght 0", F_GAR_IT, "400 800", "italic")
    + _ff("EB Garamond", F_GAR, "400 800", "normal")
    + _ff("EB Garamond", F_GAR_IT, "400 800", "italic")
    # a couple of subagents guessed "Lora" for the italic serif display — alias to the real EB Garamond italic
    + _ff("Lora", F_GAR, "400 700", "normal")
    + _ff("Lora", F_GAR_IT, "400 700", "italic")
    + _ff("Geist Mono", F_MONO_R, "400")
    + _ff("Geist Mono", F_MONO_5, "500")
    + _ff("Geist Mono", F_MONO_6, "600")
    + _ff("Geist Mono V4", F_MONO_R, "400")
    + _ff("Geist Mono V4", F_MONO_5, "500")
    + _ff("Geist Mono V4", F_MONO_6, "600")
    # --- original :root tokens (fonts + colors) ---
    + ":root{\n"
    '  --font-family--1:"Bebas Neue",sans-serif;\n'
    "  --font-family--1-test:BebasNeueBold,Arial,sans-serif;\n"
    '  --font-family--2:"Ebgaramond Variablefont Wght 0",Arial,sans-serif;\n'
    '  --font-family--2-variable:"Ebgaramond Variablefont Wght 0",Arial,sans-serif;\n'
    '  --font-family--3:"Geist Mono",sans-serif;\n'
    '  --font-family--3-test:"Geist Mono V4",Arial,sans-serif;\n'
    "  --background:#888c8f; --background-alt:#000;\n"
    "  --background-alt-01:#00000003; --background-alt-05:#0000000d; --background-alt-25:#00000040;\n"
    "  --primary:#fff; --primary-5:#ffffff0d; --primary-10:#ffffff1a; --primary-15:#ffffff26;\n"
    "  --primary-20:#fff3; --primary-40:#fff6; --primary-60:#fff9;\n"
    "  --grey:#191919; --grey-20:#3a3a3a33;\n"
    "  --size--header-height:64px;\n"
    "}\n"
    "  html,body{margin:0;padding:0;background:#888c8f;color:#fff;\n"
    "    overflow-x:hidden;max-width:100vw;\n"
    "    font-family:'Geist Mono',ui-monospace,monospace;\n"
    "    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;}\n"
    "  *{box-sizing:border-box;}\n"
    "  a{color:inherit;text-decoration:none;}\n"
    "</style>\n"
)


def inject_head(work_dir: Path) -> str:
    html_path = work_dir / "index.html"
    html = html_path.read_text(encoding="utf-8")
    if "BebasNeueBold" in html:
        return "head already injected"
    html = html.replace(
        "<title>Perfect Web Clone v3</title>",
        "<title>Longbow | British Hand-Built Featherweight Sports Cars</title>",
    )
    html = html.replace("</head>", HEAD + "</head>")
    html_path.write_text(html, encoding="utf-8")
    return "head injected (fonts + :root tokens)"


async def main() -> None:
    sid = sys.argv[1]
    sbid = sys.argv[2] if len(sys.argv) > 2 else "db-longbow"

    sb = BoxLiteSandbox(sbid)
    sm._sandboxes[sb.sandbox_id] = sb
    sm._singleton_id = sb.sandbox_id
    await sb.reconnect()
    print(f"[stage3] reconnected work_dir={sb.work_dir}")

    a = await assemble_project(sid)
    print(f"[stage3] ASSEMBLE ok={a['ok']} written={a['written_files']}")
    if a["missing_section_files"]:
        print(f"[stage3] MISSING section files: {a['missing_section_files']}")

    # confirm fonts landed in public/assets/fonts after assemble copied assets
    fdir = sb.work_dir / "public" / "assets" / "fonts"
    print(f"[stage3] public fonts present={fdir.exists()} "
          f"count={len(list(fdir.glob('*'))) if fdir.exists() else 0}")

    print("[stage3]", inject_head(sb.work_dir))

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
