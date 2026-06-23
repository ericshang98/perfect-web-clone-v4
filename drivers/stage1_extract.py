"""Stage 1 driver: extract a URL, build the section plan, scaffold the sandbox,
and dump per-section data JSON so per-section subagents can read their own chunk.

Usage:
    PYTHONPATH=. .venv/bin/python drivers/stage1_extract.py <url> <sandbox_id>

Prints a machine-readable summary block at the end (SOURCE_ID / WORKDIR / SECDIR
/ the section table) for the orchestrator to read.
"""
from __future__ import annotations

import asyncio
import json
import sys

from mcp_server.tools.extraction import extract_page, get_section_plan, get_section_data
from core.extractor.storage import SourceStore, default_storage_root
from core.boxlite.sandbox_manager import BoxLiteSandbox


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.withnovu.com"
    sandbox_id = sys.argv[2] if len(sys.argv) > 2 else "withnovu"

    print(f"[stage1] extracting {url} ...", flush=True)
    r = extract_page(
        url,
        {
            "include_screenshot": True,
            "full_page_screenshot": True,
            "download_resources": True,
            "extract_css": True,
            "detect_theme": True,
        },
    )
    if not r.get("ok"):
        print("EXTRACT_FAILED", json.dumps(r)[:2000])
        sys.exit(1)
    sid = r["source_id"]
    summ = r.get("summary", {})
    print(f"[stage1] extracted ok. title={summ.get('title')!r} "
          f"size={summ.get('page_width')}x{summ.get('page_height')} "
          f"assets={summ.get('asset_counts')}", flush=True)

    print("[stage1] planning sections ...", flush=True)
    plan = get_section_plan(sid)
    if not plan.get("ok"):
        print("PLAN_FAILED", json.dumps(plan)[:2000])
        sys.exit(1)

    store = SourceStore(sid, default_storage_root())
    secdir = store.dir / "sections_data"
    secdir.mkdir(exist_ok=True)
    for s in plan["sections"]:
        d = get_section_data(sid, s["name"])
        (secdir / f"{s['name']}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Scaffold the sandbox at a deterministic work dir so subagents can write into it
    # and Stage 3 can reconnect() without wiping their files.
    sb = BoxLiteSandbox(sandbox_id)
    asyncio.run(sb.initialize(reset=True))

    print("\n==== STAGE1 SUMMARY ====")
    print("SOURCE_ID", sid)
    print("WORKDIR", sb.work_dir)
    print("SECDIR", secdir)
    print("SOURCE_DIR", store.dir)
    print("SECTION_COUNT", plan["section_count"])
    print("PAGE_TITLE", plan.get("page_title", ""))
    print("---- SECTIONS ----")
    for s in plan["sections"]:
        print(json.dumps({
            "order": s["order"],
            "name": s["name"],
            "namespace": s["namespace"],
            "type": s["section_type"],
            "component_name": s["component_name"],
            "component_path": s["component_path"],
            "counts": s["counts"],
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
