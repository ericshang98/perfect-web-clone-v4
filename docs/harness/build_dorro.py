#!/usr/bin/env python3
"""Deterministic builder for the Pagerie 'The Dorro' product page.

Generalized from build_pagerie.py: sections_full.json -> persistent showcase
sandbox (global union CSS + faithful section components via dangerouslySetInnerHTML
+ localized images + generated App.jsx). No LLM.
"""
import json, re, os, hashlib, urllib.request, urllib.parse, concurrent.futures

ROOT = "/Users/eric/AI_development/perfect-web-clone-v4"
SRC  = f"{ROOT}/core/extractor/_sources/www.pagerie.com-1782632059-a91e37"
SB   = f"{ROOT}/showcase/products/pagerie-dorro"
IMGDIR = f"{SB}/public/assets/images"
os.makedirs(IMGDIR, exist_ok=True)
data = json.load(open(f"{SRC}/sections_full.json"))["sections"]

# ---------------------------------------------------------------- image localize
UA = {"User-Agent": "Mozilla/5.0"}
def absurl(u):
    u = u.strip().strip('"').strip("'")
    if u.startswith("//"): u = "https:" + u
    elif u.startswith("/"): u = "https://www.pagerie.com" + u
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
    """Stable filename WITHOUT a hash (so cleaned refs match disk). Only add a
    short hash when two distinct urls collide on the same basename."""
    full = absurl(u)
    base = _rawbase(full)
    prev = _name_to_url.get(base)
    if prev is not None and prev != full:
        h = hashlib.md5(full.encode()).hexdigest()[:6]
        name, ext = os.path.splitext(base)
        base = f"{name}.{h}{ext}"
    _name_to_url[base] = full
    return base

ATTR_RE = re.compile(r'(?:data-src|src|data-original|href)="([^"]+)"')
SRCSET_RE = re.compile(r'(?:data-srcset|srcset)="([^"]+)"')
urls = set()
for s in data:
    h = s["full_html"]
    for m in ATTR_RE.finditer(h):
        v = m.group(1)
        if "/cdn/shop/" in v or "pagerie.com/cdn/shop" in v:
            urls.add(v)
    for m in SRCSET_RE.finditer(h):
        for part in m.group(1).split(","):
            v = part.strip().split(" ")[0]
            if "/cdn/shop/" in v:
                urls.add(v)
for s in data:
    for im in s.get("images", []):
        u = im.get("url","")
        if "/cdn/shop/" in u:
            urls.add(u.replace("https://www.pagerie.com",""))

urlmap = {}
# precompute names serially (localname mutates a collision table → not thread-safe)
_localnames = {u: localname(u) for u in sorted(urls)}
def fetch(u):
    full = absurl(u)
    fname = _localnames[u]
    dest = f"{IMGDIR}/{fname}"
    local = f"/assets/images/{fname}"
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return u, local
    try:
        req = urllib.request.Request(full, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read()
        with open(dest, "wb") as f:
            f.write(b)
        return u, local
    except Exception:
        return u, None

ok = fail = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for u, local in ex.map(fetch, sorted(urls)):
        if local:
            urlmap[u] = local; ok += 1
        else:
            fail += 1
print(f"[images] downloaded ok={ok} fail={fail} unique={len(urls)}")

# ---------------------------------------------------------------- HTML cleaning
def localize_html(h):
    def repl_srcset(m):
        out_parts = []
        for part in m.group(1).split(","):
            seg = part.strip()
            if not seg: continue
            bits = seg.split(" ")
            u = bits[0]; key = u
            if key not in urlmap:
                key = u.replace("https://www.pagerie.com","")
            local = urlmap.get(key) or urlmap.get(u)
            bits[0] = local if local else u
            out_parts.append(" ".join(bits))
        name = "srcset" if m.group(0).startswith("srcset") else "data-srcset"
        return f'{name}="{", ".join(out_parts)}"'
    h = re.sub(r'(?:data-srcset|srcset)="([^"]+)"', repl_srcset, h)
    def repl_attr(m):
        name, val = m.group(1), m.group(2)
        key = val
        if key not in urlmap:
            key = val.replace("https://www.pagerie.com","")
        local = urlmap.get(key) or urlmap.get(val)
        return f'{name}="{local}"' if local else m.group(0)
    h = re.sub(r'(data-src|src|data-original)="([^"]+)"', repl_attr, h)
    return h

def clean_section(s):
    h = s["full_html"]
    h = re.sub(r'<script\b[^>]*>.*?</script>', '', h, flags=re.S|re.I)
    h = re.sub(r'<style\b[^>]*>.*?</style>', '', h, flags=re.S|re.I)
    h = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', h, flags=re.S|re.I)
    h = re.sub(r'<meta\b[^>]*?/?>', '', h, flags=re.I)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    h = h.replace('shopify-section', 'site-section').replace('myshopify', 'site')
    h = re.sub(r'\sdata-(section-id|section-type|section-settings|shopify[\w-]*)="[^"]*"', '', h)
    h = re.sub(r'\sdata-(section-id|section-type)=""', '', h)
    h = re.sub(r'shopify', 'shop', h, flags=re.I)
    h = localize_html(h)
    def fix_img(m):
        tag = m.group(0)
        # choose the best on-disk local source for this <img>. lazysizes images
        # carry the real image in data-original-src / data-srcset, NOT src, so
        # without JS they render blank. Prefer the full-res data-original-src,
        # then the largest localized srcset candidate, then any existing local.
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
        # build an ordered candidate list and pick the FIRST that exists on disk
        candidates = []
        for attr in ("data-original-src", "data-src"):
            mm = re.search(attr + r'="([^"]+)"', tag)
            if mm and "/assets/" in mm.group(1):
                candidates.append(mm.group(1))
        for big in (largest_srcset("data-srcset"), largest_srcset("srcset")):
            if big: candidates.append(big)
        mm = re.search(r'\ssrc="([^"]+)"', tag)
        if mm and "/assets/" in mm.group(1):
            candidates.append(mm.group(1))
        def resolve(c):
            """Return an on-disk /assets path for c, trying sized variants
            (the un-suffixed full image is often not downloaded, only _800x etc.)."""
            base = c.split('?')[0]
            if os.path.exists(f"{SB}/public{base}"):
                return base
            stem, ext = os.path.splitext(base)
            for sz in ("_1400x", "_1200x", "_1000x", "_800x", "_600x", "_400x", "_200x"):
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
        # drop lazy srcset/sizes machinery so the browser uses our resolved src
        tag = re.sub(r'\s(?:data-)?srcset="[^"]*"', '', tag)
        tag = re.sub(r'\s(?:data-)?sizes="[^"]*"', '', tag)
        def fix_style(sm):
            st = sm.group(1)
            st = re.sub(r'display:\s*none\s*!important;?', '', st, flags=re.I)
            st = re.sub(r'opacity:\s*0;?', 'opacity:1;', st, flags=re.I)
            return f'style="{st}"'
        tag = re.sub(r'style="([^"]*)"', fix_style, tag)
        # drop images that resolved to no real local asset (empty/placeholder src)
        # so they don't render a broken-image icon.
        final_src = re.search(r'\ssrc="([^"]*)"', tag)
        if not final_src or "/assets/" not in final_src.group(1):
            return ""
        return tag
    h = re.sub(r'<img\b[^>]*?/?>', fix_img, h)
    def reveal_grid(m):
        tag = m.group(0)
        if re.search(r'class="[^"]*(ProductItem|ArticleItem|Grid__Cell|ProductList|ArticleList)[^"]*"', tag):
            def fs(sm):
                st = re.sub(r'display:\s*none\s*!important;?', '', sm.group(1), flags=re.I).strip()
                return f'style="{st}"' if st else ''
            tag = re.sub(r'style="([^"]*)"', fs, tag)
        return tag
    h = re.sub(r'<(?:div|a|article|li)\b[^>]*>', reveal_grid, h)
    h = h.replace('Image--lazyLoad', 'Image--lazyLoad Image--lazyLoaded')
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
    css = s.get("css_rules","")
    if not css: continue
    for rule in split_rules(css):
        # drop malformed rules whose quotes are unbalanced (orphaned selector
        # tails from mis-splits) — they break the postcss tokenizer.
        if rule.count('"') % 2 or rule.count("'") % 2:
            continue
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen: continue
        seen.add(key); global_rules.append(rule)

gcss = "\n".join(global_rules)
gcss = gcss.replace('shopify-section', 'site-section')
gcss = re.sub(r'@media\s*\(--css[^{]*\)\s*\{(?:[^{}]|\{[^}]*\})*\}', '', gcss)
def fix_fontface(m):
    block = m.group(0)
    if 'Pano-Light' in block or 'panolight' in block:
        return ('@font-face{font-family:"Pano-Light";'
                'src:url(/assets/fonts/panolight.woff2) format("woff2"),'
                'url(/assets/fonts/panolight.woff) format("woff");'
                'font-weight:normal;font-style:normal;font-display:swap;}')
    if 'PagerieFont-Roman' in block:
        return ('@font-face{font-family:"PagerieFont-Roman";'
                'src:url(/assets/fonts/PagerieFont-Roman.woff2) format("woff2"),'
                'url(/assets/fonts/PagerieFont-Roman.woff) format("woff");'
                'font-weight:normal;font-style:normal;font-display:swap;}')
    def keep_local(sm):
        parts = [p.strip() for p in sm.group(1).split(",")]
        kept = [p for p in parts if '/assets/' in p]
        if not kept: return 'src:' + parts[0] + ';' if parts else ''
        return 'src:' + ", ".join(kept) + ';'
    block = re.sub(r'src:\s*([^;}]+);?', keep_local, block, count=1)
    return block
gcss = re.sub(r'@font-face\s*\{[^}]*\}', fix_fontface, gcss)
gcss = re.sub(r'url\((?:https?:)?//[^)]*\)\s*format\("[^"]*"\),?', '', gcss)
gcss = re.sub(r'url\(/cdn/[^)]*\)\s*format\("[^"]*"\),?', '', gcss)

header = (
    "/* === pagerie 'The Dorro' cleaned global theme CSS (deterministic union of section css_rules) === */\n"
    ":root{--header-height:71px;}\n"
)
ENHANCE = """
/* === pwc interaction-layer enhancements === */
.pwc-header{position:sticky;top:0;z-index:50;transition:box-shadow .3s ease;}
.ProductItem{position:relative;}
.ProductItem__ImageWrapper{position:relative;display:block;}
.AspectRatio--withFallback{padding-bottom:0!important;}
.AspectRatio--withFallback::before{content:""!important;display:block!important;padding-bottom:calc(100% / var(--aspect-ratio, 0.774))!important;}
.ProductItem__ImageWrapper .AspectRatio{position:relative;overflow:hidden;}
.ProductItem__ImageWrapper .AspectRatio>img,
.ProductItem .ProductItem__Image{position:absolute!important;top:0;left:0;width:100%!important;height:100%!important;object-fit:cover;}
.ProductItem__Image--alternate{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}
.ProductItem__ImageWrapper--withAlternateImage .ProductItem__Image--alternate{display:block!important;opacity:0;transition:opacity .45s ease;}
.ProductItem__ImageWrapper--withAlternateImage .ProductItem__Image{transition:opacity .45s ease;}
.ProductItem__ImageWrapper--withAlternateImage:hover .ProductItem__Image--alternate{opacity:1!important;}
.ProductItem__ImageWrapper--withAlternateImage:hover .ProductItem__Image:not(.ProductItem__Image--alternate){opacity:0!important;}
/* force every lazy/fade image visible — the live fade-in is JS-driven and never
   fires in the static clone, leaving the gallery blank. */
.Image--lazyLoad,.Image--lazyLoaded,.Image--fadeIn,.lazyautosizes,.Product__SlideItem img,.Product__Gallery img{opacity:1!important;visibility:visible!important;}

/* === PDP two-column layout ===
   the deterministic chunker split the product wrapper's two columns into
   sibling sections (gallery + product info); App.jsx wraps them back into a
   row so the gallery sits left and the sticky info column sits right. */
.pwc-pdp-row{display:flex;align-items:flex-start;gap:0;max-width:1500px;margin:0 auto;padding:0 24px;}
.pwc-pdp-row>.pwc-gallery{flex:0 0 58%;max-width:58%;min-width:0;}
.pwc-pdp-row>.pwc-product{flex:1 1 42%;max-width:42%;min-width:0;position:sticky;top:90px;padding-left:48px;}
.pwc-pdp-row .Product__SlideItem{margin-bottom:8px;}
@media (max-width:900px){
  .pwc-pdp-row{flex-direction:column;padding:0;}
  .pwc-pdp-row>.pwc-gallery,.pwc-pdp-row>.pwc-product{max-width:100%;flex-basis:auto;position:static;padding-left:0;}
}
"""
final_css = "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n" + header + gcss + "\n" + ENHANCE
with open(f"{SB}/src/index.css","w") as f:
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
    with open(f"{d}/{comp}.jsx","w") as f:
        f.write(code)
print(f"[components] wrote {len(data)} section components")

# ---------------------------------------------------------------- App.jsx (render order)
ordered = sorted(data, key=lambda s: s["order"])
imports = "\n".join(
    f"import {s['component_name']} from './components/sections/{s['namespace']}/{s['component_name']}.jsx'"
    for s in ordered
)
# wrap the consecutive gallery + product sections into a two-column PDP row
by_ns = {s["namespace"]: s["component_name"] for s in ordered}
render_lines = []
i = 0
while i < len(ordered):
    ns = ordered[i]["namespace"]
    if ns == "gallery" and i + 1 < len(ordered) and ordered[i + 1]["namespace"] == "product":
        render_lines.append(
            f'<div className="pwc-pdp-row">'
            f'<{by_ns["gallery"]} /><{by_ns["product"]} />'
            f'</div>'
        )
        i += 2
        continue
    render_lines.append(f"<{ordered[i]['component_name']} />")
    i += 1
renders = "\n      ".join(render_lines)
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
with open(f"{SB}/src/App.jsx","w") as f:
    f.write(app)
print(f"[app] wrote App.jsx with {len(ordered)} sections")
print("[done]")
