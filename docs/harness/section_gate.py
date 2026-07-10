#!/usr/bin/env python3
"""
Per-section render + SSIM gate — minimal prototype.

The point: give each section its OWN eyes. Crop the SAME section from the
registered ground-truth raster and from the local clone, align them, and run
the framework's own deterministic SSIM gate (core.gates.fidelity / the pwc4
`score_fidelity` tool). It returns a score + per-band worst_regions that
localize WHERE the section diverges — no human eyeballing required.

This is the unit a section sub-agent should loop against (柱 3 / 柱 5):
    reconstruct → render-this-section → score vs ref → fix worst band → repeat
    until score >= τ; the GATE decides done, not the sub-agent.

Demo (Signature Collar / section-7) auto-caught: clone renders an extra product
card in the black left panel that the real site does not → score 0.39, worst
bands at the bottom (where the card sits).

Usage:
    python section_gate.py <section_name> <clone_selector> <ref_png> <y0> <y1>
    # ref_png = the registered ground-truth full-page raster (extractor output)
    # y0..y1  = that section's vertical band in the ref raster (until `bounds`
    #           is captured per-section — pipeline hole A — pass it explicitly)
"""
import sys, json, subprocess
from PIL import Image
from playwright.sync_api import sync_playwright

CLONE_URL = "http://localhost:5192"


def crop_clone(selector, out):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(CLONE_URL, wait_until="networkidle", timeout=30000)
        pg.wait_for_timeout(2500)
        for sel in [".pwc-popup__close"]:
            try: pg.click(sel, timeout=1200)
            except Exception: pass
        box = pg.evaluate(
            "(s)=>{const e=document.querySelector(s);if(!e)return null;"
            "const r=e.getBoundingClientRect();"
            "return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height};}",
            selector,
        )
        pg.screenshot(path="/tmp/_clone_full.png", full_page=True)
        b.close()
    im = Image.open("/tmp/_clone_full.png").convert("RGB")
    im.crop((int(box["x"]), int(box["y"]), int(box["x"] + box["w"]), int(box["y"] + box["h"]))).save(out)
    return box


def align(ref_png, cand_png, out_ref, out_cand, width=1000):
    r = Image.open(ref_png).convert("RGB")
    c = Image.open(cand_png).convert("RGB")
    norm = lambda im: im.resize((width, int(im.height * width / im.width)))
    r, c = norm(r), norm(c)
    h = min(r.height, c.height)
    r.crop((0, 0, width, h)).save(out_ref)
    c.crop((0, 0, width, h)).save(out_cand)
    return width, h


def main():
    name, selector, ref_full, y0, y1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    Image.open(ref_full).convert("RGB").crop((0, y0, 1440, y1)).save(f"/tmp/_{name}_ref.png")
    crop_clone(selector, f"/tmp/_{name}_cand.png")
    align(f"/tmp/_{name}_ref.png", f"/tmp/_{name}_cand.png", f"/tmp/_{name}_REF.png", f"/tmp/_{name}_CAND.png")
    # score via the framework's own gate (deterministic, LLM-free)
    from core.gates import fidelity
    REF, CAND = f"/tmp/_{name}_REF.png", f"/tmp/_{name}_CAND.png"
    score = fidelity.score(REF, CAND)
    worst = fidelity.worst_regions(REF, CAND, rows=10)
    tau = 0.9
    print(json.dumps({
        "section": name, "score": round(score, 4), "tau": tau,
        "pass": score >= tau,
        "worst_regions": worst[:3],  # the bands a sub-agent would fix first
    }, indent=1))


if __name__ == "__main__":
    main()
