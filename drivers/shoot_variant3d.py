"""Screenshot driver for variant3d verify-loop. Desktop@1440 + mobile@390,
full-page, wait_until=load (networkidle never settles with bg video/CDN srcSet)."""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/"
OUT = Path("/tmp/pwc3-sandboxes/variant3d/shots"); OUT.mkdir(parents=True, exist_ok=True)
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900, "is_mobile": False, "dsf": 1},
    "mobile": {"width": 390, "height": 844, "is_mobile": True, "dsf": 2},
}

async def shoot(browser, name, vp):
    ctx = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]},
        is_mobile=vp["is_mobile"], device_scale_factor=vp["dsf"])
    page = await ctx.new_page()
    try:
        await page.goto(URL, timeout=30000, wait_until="load")
    except Exception as e:
        print(f"[{name}] goto warn: {e}")
    await page.wait_for_timeout(2500)
    try:
        await page.evaluate("async()=>{const h=document.body.scrollHeight;"
            "for(let y=0;y<h;y+=800){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}window.scrollTo(0,0);}")
    except Exception as e:
        print(f"[{name}] scroll warn: {e}")
    await page.wait_for_timeout(1500)
    out = OUT / f"{name}_full.png"
    await page.screenshot(path=str(out), full_page=True)
    dims = await page.evaluate("()=>({w:document.documentElement.scrollWidth,h:document.body.scrollHeight})")
    errs = await page.evaluate("()=>window.__errs||null")
    print(f"[{name}] saved {out} render={dims['w']}x{dims['h']}")
    await ctx.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, vp in VIEWPORTS.items():
            await shoot(browser, name, vp)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
