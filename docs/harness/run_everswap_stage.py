#!/usr/bin/env python3
"""Stage everswap clone: assemble shell -> persist to showcase/products/everswap,
dump each section's data to _secdata/*.json so the brain can author components.
One process (BoxLite singleton is in-process)."""
import asyncio, json, shutil
from pathlib import Path
from core.boxlite import create_sandbox
from mcp_server.tools.build_deploy import assemble_project
from mcp_server.tools.extraction import get_section_plan, get_section_data

SID = "everswap.com-1782793167-835ba6"
DEST = Path("/Users/eric/AI_development/perfect-web-clone-v4/showcase/products/everswap")
SECDATA = DEST / "_secdata"

async def main():
    sb = await create_sandbox(reset=True)
    res = await assemble_project(SID)
    work = Path(sb.work_dir)
    print("assemble ok:", res.get("ok"), "| work_dir:", work)

    # persist the assembled shell to a stable showcase dir
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(work, DEST, ignore=shutil.ignore_patterns("node_modules", "dist", ".git"))
    SECDATA.mkdir(parents=True, exist_ok=True)

    plan = get_section_plan(SID)
    secs = plan.get("sections", [])
    print("sections:", [s["name"] for s in secs])
    for s in secs:
        name = s["name"]
        data = get_section_data(SID, name)
        (SECDATA / f"{name}.json").write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        html = data.get("full_html") or data.get("html") or ""
        css = data.get("css_rules") or data.get("css") or []
        imgs = data.get("images") or data.get("assets") or []
        print(f"  {name:14s} html={len(html):6d}B  css_rules={len(css) if isinstance(css,list) else 'n/a'}  imgs={len(imgs) if isinstance(imgs,list) else 'n/a'}  keys={list(data.keys())[:8]}")

asyncio.run(main())
