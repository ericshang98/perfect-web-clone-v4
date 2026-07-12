#!/usr/bin/env python3
"""Deterministic builder for the trykojiva.com/brush (Linfae) product page.

Adapted from build_dorro.py. trykojiva is a CUSTOM store (images live on
trykojiva.com/storage/... plus some Shopify /cdn/shop/), so the image harvest is
broadened to catch any absolute trykojiva/cdn image URL. sections_full.json ->
showcase/products/trykojiva (global union CSS + faithful section components via
dangerouslySetInnerHTML + localized images + generated App.jsx). No LLM, no MCP.
"""
import json, re, os, hashlib, urllib.request, urllib.parse, concurrent.futures

ROOT = "/Users/eric/AI_development/perfect-web-clone-v4"
SRC  = f"{ROOT}/core/extractor/_sources/trykojiva.com-1782715540-ab1ef0"
SB   = f"{ROOT}/showcase/products/trykojiva"
ORIGIN = "https://trykojiva.com"
IMGDIR = f"{SB}/public/assets/images"
os.makedirs(IMGDIR, exist_ok=True)
data = json.load(open(f"{SRC}/sections_full.json"))["sections"]

# ---------------------------------------------------------------- image localize
UA = {"User-Agent": "Mozilla/5.0"}
def absurl(u):
    u = u.strip().strip('"').strip("'")
    if u.startswith("//"): u = "https:" + u
    elif u.startswith("/"): u = ORIGIN + u
    u = u.replace("{width}", "1200")
    if "/cdn/shop/" in u and not u.lower().endswith(".svg"):
        sep = "&" if "?" in u else "?"
        u = f"{u}{sep}width=1000"
    return u

_name_to_url = {}
def _rawbase(u):
    p = urllib.parse.urlparse(u.split("?")[0])
    base = os.path.basename(p.path) or "img"
    base = base.replace("{width}", "1200")
    if not re.search(r"\.(png|jpg|jpeg|webp|svg|gif|avif)$", base, re.I):
        base += ".png"
    return base
def localname(u):
    full = absurl(u)
    base = _rawbase(full)
    prev = _name_to_url.get(base)
    if prev is not None and prev != full:
        h = hashlib.md5(full.encode()).hexdigest()[:6]
        name, ext = os.path.splitext(base)
        base = f"{name}.{h}{ext}"
    _name_to_url[base] = full
    return base

def is_img_url(v):
    """A harvestable image URL: absolute trykojiva/cdn/https image, or a
    root-relative /storage|/cdn|/assets path."""
    vl = v.lower().split("?")[0]
    if not re.search(r"\.(png|jpg|jpeg|webp|svg|gif|avif)$", vl):
        # allow shopify cdn urls that carry the ext before a transform param
        if "/cdn/shop/" not in v and "/storage/" not in v:
            return False
    if v.startswith("data:"):
        return False
    return (v.startswith("http") or v.startswith("//") or v.startswith("/"))

# The extractor already localized each section's <img src> to /assets/images/<base>
# and kept the REAL source url in images[]. So we map basename -> real url and
# download the real bytes to the path the HTML already references. (Harvesting the
# /assets/... pseudo-paths would hit a server placeholder — that was the blank-image
# bug: 34/71 came back as an identical 7912-byte placeholder.)
real_by_base = {}
for s in data:
    for im in s.get("images", []):
        u = (im.get("url") or "").strip()
        lu = (im.get("local_url") or "").strip()
        if not u:
            continue
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/") and not u.startswith("/assets/"):
            u = ORIGIN + u
        if not u.startswith("http"):
            continue
        # Register the real url under BOTH the local_url basename (what the HTML
        # references — may be hash-suffixed by the extractor) AND the real-url
        # basename, so every reference resolves regardless of which naming the
        # cleaned HTML kept.
        for name in (lu, u):
            if not name:
                continue
            base = os.path.basename(name.split("?")[0])
            if base and "." in base:
                real_by_base.setdefault(base, u)

def fetch(item):
    base, full = item
    dest = f"{IMGDIR}/{base}"
    if os.path.exists(dest) and os.path.getsize(dest) > 9000:
        return base, True
    try:
        req = urllib.request.Request(full, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read()
        if not b:
            return base, False
        with open(dest, "wb") as f:
            f.write(b)
        return base, True
    except Exception as e:
        print("   [img fail]", full[:80], type(e).__name__)
        return base, False

urlmap = {}  # kept for localize_html compatibility (html already localized → no-op)
ok = fail = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for base, good in ex.map(fetch, sorted(real_by_base.items())):
        if good:
            ok += 1
        else:
            fail += 1
print(f"[images] downloaded ok={ok} fail={fail} unique={len(real_by_base)}")

# ---------------------------------------------------------------- HTML cleaning
def localize_html(h):
    def repl_srcset(m):
        out_parts = []
        for part in m.group(1).split(","):
            seg = part.strip()
            if not seg: continue
            bits = seg.split(" ")
            u = bits[0]
            local = urlmap.get(u) or urlmap.get(u.replace(ORIGIN, ""))
            bits[0] = local if local else u
            out_parts.append(" ".join(bits))
        name = "srcset" if m.group(0).startswith("srcset") else "data-srcset"
        return f'{name}="{", ".join(out_parts)}"'
    h = re.sub(r'(?:data-srcset|srcset)="([^"]+)"', repl_srcset, h)
    def repl_attr(m):
        name, val = m.group(1), m.group(2)
        local = urlmap.get(val) or urlmap.get(val.replace(ORIGIN, ""))
        return f'{name}="{local}"' if local else m.group(0)
    h = re.sub(r'(data-src|data-original-src|data-original|src)="([^"]+)"', repl_attr, h)
    return h

def clean_section(s):
    h = s["full_html"]
    h = re.sub(r'<script\b[^>]*>.*?</script>', '', h, flags=re.S|re.I)
    h = re.sub(r'<style\b[^>]*>.*?</style>', '', h, flags=re.S|re.I)
    h = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', h, flags=re.S|re.I)
    h = re.sub(r'<meta\b[^>]*?/?>', '', h, flags=re.I)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    # defingerprint (harmless if absent)
    h = h.replace('shopify-section', 'site-section').replace('myshopify', 'site')
    h = re.sub(r'\sdata-(section-id|section-type|section-settings|shopify[\w-]*)="[^"]*"', '', h)
    h = re.sub(r'shopify', 'shop', h, flags=re.I)
    h = localize_html(h)
    def fix_img(m):
        tag = m.group(0)
        def largest_srcset(attr):
            mm = re.search(attr + r'="([^"]+)"', tag)
            if not mm: return None
            best = None; bestw = -1
            for part in mm.group(1).split(","):
                seg = part.strip().split(" ")
                u = seg[0]
                if "/assets/" not in u: continue
                w = 0
                if len(seg) > 1 and seg[1].endswith("w"):
                    try: w = int(seg[1][:-1])
                    except ValueError: w = 0
                if w >= bestw: bestw = w; best = u
            return best
        candidates = []
        for attr in ("data-original-src", "data-original", "data-src"):
            mm = re.search(attr + r'="([^"]+)"', tag)
            if mm and "/assets/" in mm.group(1):
                candidates.append(mm.group(1))
        for big in (largest_srcset("data-srcset"), largest_srcset("srcset")):
            if big: candidates.append(big)
        mm = re.search(r'\ssrc="([^"]+)"', tag)
        if mm and "/assets/" in mm.group(1):
            candidates.append(mm.group(1))
        def resolve(c):
            base = c.split('?')[0]
            if os.path.exists(f"{SB}/public{base}"):
                return base
            stem, ext = os.path.splitext(base)
            for sz in ("_1400x", "_1200x", "_1000x", "_800x", "_600x", "_400x"):
                if os.path.exists(f"{SB}/public{stem}{sz}{ext}"):
                    return f"{stem}{sz}{ext}"
            return None
        cand = None
        for c in candidates:
            r = resolve(c)
            if r: cand = r; break
        if cand:
            if re.search(r'\ssrc="[^"]*"', tag):
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{cand}"', tag, count=1)
            else:
                tag = tag[:4] + f' src="{cand}"' + tag[4:]
        tag = re.sub(r'\s(?:data-)?srcset="[^"]*"', '', tag)
        tag = re.sub(r'\s(?:data-)?sizes="[^"]*"', '', tag)
        def fix_style(sm):
            st = sm.group(1)
            st = re.sub(r'display:\s*none\s*!important;?', '', st, flags=re.I)
            st = re.sub(r'opacity:\s*0;?', 'opacity:1;', st, flags=re.I)
            return f'style="{st}"'
        tag = re.sub(r'style="([^"]*)"', fix_style, tag)
        final_src = re.search(r'\ssrc="([^"]*)"', tag)
        if not final_src or "/assets/" not in final_src.group(1):
            return ""
        return tag
    h = re.sub(r'<img\b[^>]*?/?>', fix_img, h)
    # reveal any content hidden by scroll-in animations
    h = re.sub(r'opacity:\s*0(?![.\d])', 'opacity:1', h)
    return h.strip()

# ---------------------------------------------------------------- global CSS
def split_rules(css):
    rules = []; i, n = 0, len(css); depth = 0; start = 0
    while i < n:
        c = css[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                rules.append(css[start:i+1].strip()); start = i+1
        i += 1
    tail = css[start:].strip()
    if tail: rules.append(tail)
    return [r for r in rules if r]

seen = set(); global_rules = []
for s in data:
    css = s.get("css_rules", "")
    if not css: continue
    for rule in split_rules(css):
        if rule.count('"') % 2 or rule.count("'") % 2:
            continue
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen: continue
        seen.add(key); global_rules.append(rule)

gcss = "\n".join(global_rules)
gcss = gcss.replace('shopify-section', 'site-section')
# keep only local/family in @font-face src; strip remote font urls
def fix_fontface(m):
    block = m.group(0)
    def keep_local(sm):
        parts = [p.strip() for p in sm.group(1).split(",")]
        kept = [p for p in parts if '/assets/' in p]
        if not kept:
            return 'src:' + parts[0] + ';' if parts else ''
        return 'src:' + ", ".join(kept) + ';'
    return re.sub(r'src:\s*([^;}]+);?', keep_local, block, count=1)
gcss = re.sub(r'@font-face\s*\{[^}]*\}', fix_fontface, gcss)
gcss = re.sub(r'url\(/cdn/[^)]*\)\s*format\("[^"]*"\),?', '', gcss)

header = "/* === trykojiva (Linfae) cleaned global theme CSS — deterministic union of section css_rules === */\n"
ENHANCE = """
/* === pwc rest-state / reveal overrides === */
html,body{opacity:1!important;visibility:visible!important}
[class*="fade" i],[class*="reveal" i],[class*="animate" i],[data-aos]{opacity:1!important;transform:none!important;visibility:visible!important}
img{max-width:100%;height:auto}
"""
final_css = "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n" + header + gcss + "\n" + ENHANCE
with open(f"{SB}/src/index.css", "w") as f:
    f.write(final_css)
print(f"[css] global rules={len(global_rules)} bytes={len(final_css)}")

# ---------------------------------------------------------------- components
for s in data:
    ns = s["namespace"]; comp = s["component_name"]
    inner = clean_section(s)
    js = json.dumps(inner)
    code = (
        f"// {comp} — deterministic faithful reconstruction (cleaned HTML + global theme CSS)\n"
        f"const __html = {js};\n\n"
        f"export default function {comp}() {{\n"
        f"  return <div className=\"pwc-section pwc-{ns}\" dangerouslySetInnerHTML={{{{ __html }}}} />;\n"
        f"}}\n"
    )
    d = f"{SB}/src/components/sections/{ns}"
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/{comp}.jsx", "w") as f:
        f.write(code)
print(f"[components] wrote {len(data)} section components")

# ---------------------------------------------------------------- App.jsx
ordered = sorted(data, key=lambda s: s["order"])
imports = "\n".join(
    f"import {s['component_name']} from './components/sections/{s['namespace']}/{s['component_name']}.jsx'"
    for s in ordered
)
renders = "\n      ".join(f"<{s['component_name']} />" for s in ordered)
app = (
    f"{imports}\n\n"
    f"export default function App() {{\n"
    f"  return (\n"
    f"    <>\n"
    f"      {renders}\n"
    f"    </>\n"
    f"  )\n"
    f"}}\n"
)
with open(f"{SB}/src/App.jsx", "w") as f:
    f.write(app)
print(f"[app] wrote App.jsx with {len(ordered)} sections")
print("[done]")
