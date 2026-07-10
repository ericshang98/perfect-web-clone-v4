"""Stable per-section gate v3 — compares the clone against FROZEN references.

v2 still wobbled run-to-run because it re-photographed the live site every run
(lazy images load differently each time). v3 fixes that: the real references were
captured ONCE and saved under docs/harness/refs/. v3 only captures the clone and
scores it against the frozen refs → same clone + same code => same score.

This is "hole A done right": freeze the ground truth, then only ever compare
against the frozen copy. Re-freeze (run freeze_refs) only when the real site or
the captured section set genuinely changes.

Run from repo root:  .venv/bin/python docs/harness/scale_v3.py
"""
import os
from PIL import Image
from playwright.sync_api import sync_playwright
from core.gates import fidelity

REFDIR = "docs/harness/refs"
# frozen-ref name -> clone selector
TARGETS = [
    ("granite",   ".pwc-section-5"),
    ("quality",   ".pwc-section-6"),
    ("product",   ".pwc-product"),
    ("product2",  ".pwc-product-2"),
    ("signature", ".pwc-section-7"),
    ("footer",    ".pwc-footer"),
]
UNSTICK = ("()=>{document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position;"
           "if(p==='sticky'||p==='fixed')e.style.setProperty('position','static','important');});}")


def cap_clone(outdir):
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("http://localhost:5192", wait_until="networkidle", timeout=30000)
        pg.wait_for_timeout(2500)
        try: pg.click(".pwc-popup__close", timeout=1200)
        except Exception: pass
        for name, sel in TARGETS:
            el = pg.query_selector(sel)
            if not el: continue
            pg.evaluate(UNSTICK)
            el.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
            pg.evaluate(UNSTICK); pg.wait_for_timeout(200)
            el.screenshot(path=f"{outdir}/{name}.png")
        b.close()


def fair_align(ref_png, clone_png, W=800):
    r = Image.open(ref_png).convert("RGB"); c = Image.open(clone_png).convert("RGB")
    H = int(r.height * W / r.width)
    r2, c2 = r.resize((W, H)), c.resize((W, H))   # force both into the frozen ref's frame
    r2.save("/tmp/_R.png"); c2.save("/tmp/_C.png")
    sbs = Image.new("RGB", (W * 2 + 16, H), (255, 255, 255)); sbs.paste(r2, (0, 0)); sbs.paste(c2, (W + 16, 0))
    return "/tmp/_R.png", "/tmp/_C.png", sbs


def main():
    cap_clone("/tmp/clone_sections")
    os.makedirs("/tmp/health3/sbs", exist_ok=True)
    print("=== STABLE SECTION GATE v3 (frozen refs, τ=0.90) ===")
    print(f"{'section':<12}{'SSIM':>7}  verdict")
    for name, sel in TARGETS:
        ref = f"{REFDIR}/{name}.png"; cand = f"/tmp/clone_sections/{name}.png"
        if not (os.path.exists(ref) and os.path.exists(cand)):
            print(f"{name:<12}{'  --':>7}  (missing)"); continue
        R, C, sbs = fair_align(ref, cand)
        sbs.save(f"/tmp/health3/sbs/{name}.png")
        sc = fidelity.score(R, C)
        print(f"{name:<12}{sc:>7.3f}  {'PASS' if sc >= 0.9 else 'FAIL'}")
    print("side-by-sides: /tmp/health3/sbs/<section>.png")


if __name__ == "__main__":
    main()
