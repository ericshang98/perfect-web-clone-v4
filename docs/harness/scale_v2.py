"""Trustworthy per-section gate v2 — fix the 'scale' before trusting any score.
Removes the 3 contaminants that made v1 noisy:
  (1) popup        -> block klaviyo/attentive at the network layer (never shows)
  (2) sticky header overlap -> un-stick all headers before capturing
  (3) bad alignment -> crop each section at its OWN bounds, then resize BOTH to
                       the real section's frame so content aligns proportionally.
"""
import os, json
from PIL import Image
from playwright.sync_api import sync_playwright
from core.gates import fidelity

# clone section selector  ->  keyword identifying the same REAL section by text
TARGETS = [
    ("granite/s5",   ".pwc-section-5", "now in granite"),
    ("quality/s6",   ".pwc-section-6", "quality is our love"),
    ("product/XS",   ".pwc-product",   "extra small"),
    ("product-2/ML", ".pwc-product-2", "medium — extra"),
    ("signature/s7", ".pwc-section-7", "signature collar"),
    ("footer",       ".pwc-footer",    "le monde"),
]
BLOCK = ("klaviyo", "attentive", "attn.tv", "wisepops", "privy", "justuno")
UNSTICK = """()=>{document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position;
  if(p==='sticky'||p==='fixed'){e.style.setProperty('position','static','important');}});}"""

def block_popups(route):
    if any(d in route.request.url for d in BLOCK):
        return route.abort()
    return route.continue_()

def cap_real(outdir):
    os.makedirs(outdir, exist_ok=True); got={}
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={"width":1440,"height":900})
        pg.route("**/*", block_popups)
        pg.goto("https://www.pagerie.com", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(5000)
        h=pg.evaluate("document.body.scrollHeight")
        for y in range(0,h+1000,600): pg.mouse.wheel(0,600); pg.wait_for_timeout(130)
        pg.wait_for_timeout(1200)
        for s in pg.query_selector_all(".shopify-section"):
            try:
                box=s.bounding_box()
                if not box or box["height"]<200: continue
                t=(s.inner_text() or "").strip().replace("\n"," ").lower()
                for name,sel,kw in TARGETS:
                    if kw in t and kw not in got:
                        pg.evaluate(UNSTICK)
                        s.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
                        pg.evaluate(UNSTICK); pg.wait_for_timeout(200)
                        path=f"{outdir}/{kw[:6]}.png"; s.screenshot(path=path); got[kw]=path
            except: pass
        b.close()
    return got

def cap_clone(outdir):
    os.makedirs(outdir, exist_ok=True); got={}
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={"width":1440,"height":900})
        pg.goto("http://localhost:5192", wait_until="networkidle", timeout=30000); pg.wait_for_timeout(2500)
        try: pg.click(".pwc-popup__close", timeout=1200)
        except: pass
        for name,sel,kw in TARGETS:
            el=pg.query_selector(sel)
            if not el: continue
            pg.evaluate(UNSTICK)
            el.scroll_into_view_if_needed(); pg.wait_for_timeout(350)
            pg.evaluate(UNSTICK); pg.wait_for_timeout(150)
            path=f"{outdir}/{kw[:6]}.png"; el.screenshot(path=path); got[kw]=path
        b.close()
    return got

def fair_align(real_png, clone_png, W=800):
    r=Image.open(real_png).convert("RGB"); c=Image.open(clone_png).convert("RGB")
    H=int(r.height*W/r.width)                 # real section's frame
    r2=r.resize((W,H)); c2=c.resize((W,H))    # force BOTH into the same frame
    r2.save("/tmp/_R.png"); c2.save("/tmp/_C.png")
    sbs=Image.new("RGB",(W*2+16,H),(255,255,255)); sbs.paste(r2,(0,0)); sbs.paste(c2,(W+16,0))
    return "/tmp/_R.png","/tmp/_C.png", sbs

real=cap_real("/tmp/health2/real"); clone=cap_clone("/tmp/health2/clone")
print("=== TRUSTWORTHY SECTION GATE v2 (popup-blocked, un-stuck, frame-aligned, τ=0.90) ===")
print(f"{'section':<15}{'SSIM':>7}  {'verdict':<6}")
os.makedirs("/tmp/health2/sbs", exist_ok=True)
for name,sel,kw in TARGETS:
    if kw not in real or kw not in clone:
        print(f"{name:<15}{'  --':>7}  (no match)"); continue
    R,C,sbs=fair_align(real[kw], clone[kw])
    sbs.save(f"/tmp/health2/sbs/{kw[:6]}.png")
    sc=fidelity.score(R,C)
    print(f"{name:<15}{sc:>7.3f}  {('PASS' if sc>=.9 else 'FAIL'):<6}")
