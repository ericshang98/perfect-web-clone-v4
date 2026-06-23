"""Stage 4 driver: start the Vite dev server and capture full-page desktop +
mobile screenshots for the fidelity verify-loop.

Usage:
    PYTHONPATH=. .venv/bin/python drivers/stage4_preview.py [sandbox_id]
"""
from __future__ import annotations

import asyncio
import sys

from core.boxlite import sandbox_manager as sm
from core.boxlite.sandbox_manager import BoxLiteSandbox


async def main() -> None:
    sbid = sys.argv[1] if len(sys.argv) > 1 else "withnovu"
    sb = BoxLiteSandbox(sbid)
    sm._sandboxes[sb.sandbox_id] = sb
    sm._singleton_id = sb.sandbox_id
    await sb.reconnect()

    print("[stage4] starting preview ...", flush=True)
    r = await sb.start_preview()
    print(f"[stage4] preview success={r.success} url={sb.state.preview_url} exit={r.exit_code}")
    if not r.success:
        print("STDERR:", (r.stderr or "")[-2000:])
        print("STDOUT:", (r.stdout or "")[-1000:])
        return

    st = sb.preview_status()
    print(f"[stage4] status has_error={st.has_error} msg={st.error_message}")

    for vp in ("desktop", "mobile"):
        shot = await sb.screenshot(path=f"shots/{vp}.jpg", viewport=vp, full_page=True)
        print(f"[stage4] {vp}: error={shot.error} saved={shot.saved_path} "
              f"{shot.width}x{shot.height}")


if __name__ == "__main__":
    asyncio.run(main())
