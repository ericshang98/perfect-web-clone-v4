#!/usr/bin/env python3
"""Deterministic builder: sections_full.json -> sandbox (global CSS + section components + localized images)."""
import json, re, os, sys, hashlib, urllib.request, urllib.parse, concurrent.futures

SRC = "/Users/eric/AI_development/perfect-web-clone-v4/core/extractor/_sources/www.pagerie.com-1782464152-9b6f51"
# durable target (the ephemeral /tmp sandbox is lost on MCP/CC restart; the
# showcase copy persists and already has the scaffold + assets). Rebuild there.
SB  = "/Users/eric/AI_development/perfect-web-clone-v4/showcase/products/pagerie"
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
    # cap Shopify CDN images to 1000px wide to keep the bundle lean (display sizes are smaller)
    if "/cdn/shop/" in u and not u.lower().endswith(".svg"):
        sep = "&" if "?" in u else "?"
        u = f"{u}{sep}width=1000"
    return u
def localname(u):
    p = urllib.parse.urlparse(u.split("?")[0])
    base = os.path.basename(p.path) or "img"
    base = base.replace("{width}", "1200")
    if not re.search(r"\.(png|jpg|jpeg|webp|svg|gif|avif)$", base, re.I):
        base += ".png"
    # de-dupe collisions with short hash of full url
    h = hashlib.md5(u.encode()).hexdigest()[:6]
    name, ext = os.path.splitext(base)
    return f"{name}.{h}{ext}"

# collect every url-ish attribute value across sections
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
# also from images[] list
for s in data:
    for im in s.get("images", []):
        u = im.get("url","")
        if "/cdn/shop/" in u:
            urls.add(u.replace("https://www.pagerie.com",""))

urlmap = {}   # original-attr-string -> /assets/images/local
def fetch(u):
    full = absurl(u)
    fname = localname(full)
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
    except Exception as e:
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
    # rewrite srcset/data-srcset first (multi-url)
    def repl_srcset(m):
        attr = m.group(0)
        out_parts = []
        for part in m.group(1).split(","):
            seg = part.strip()
            if not seg: continue
            bits = seg.split(" ")
            u = bits[0]
            key = u
            if key not in urlmap:
                key = u.replace("https://www.pagerie.com","")
            local = urlmap.get(key) or urlmap.get(u)
            bits[0] = local if local else u
            out_parts.append(" ".join(bits))
        name = "srcset" if m.group(0).startswith("srcset") else "data-srcset"
        return f'{name}="{", ".join(out_parts)}"'
    h = re.sub(r'(?:data-srcset|srcset)="([^"]+)"', repl_srcset, h)
    # rewrite single-url attrs
    def repl_attr(m):
        name, val = m.group(1), m.group(2)
        key = val
        if key not in urlmap:
            key = val.replace("https://www.pagerie.com","")
        local = urlmap.get(key) or urlmap.get(val)
        return f'{name}="{local}"' if local else m.group(0)
    h = re.sub(r'(data-src|src|data-original)="([^"]+)"', repl_attr, h)
    return h

VOID = "img|br|hr|input|meta|link|source|area|base|col|embed|param|track|wbr"
def clean_section(s):
    h = s["full_html"]
    # strip script/style/noscript/meta/comments
    h = re.sub(r'<script\b[^>]*>.*?</script>', '', h, flags=re.S|re.I)
    h = re.sub(r'<style\b[^>]*>.*?</style>', '', h, flags=re.S|re.I)
    h = re.sub(r'<noscript\b[^>]*>.*?</noscript>', '', h, flags=re.S|re.I)
    h = re.sub(r'<meta\b[^>]*?/?>', '', h, flags=re.I)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    # de-shopify identifiers
    h = h.replace('shopify-section', 'site-section').replace('myshopify', 'site')
    h = re.sub(r'\sdata-(section-id|section-type|section-settings|shopify[\w-]*)="[^"]*"', '', h)
    h = re.sub(r'\sdata-(section-id|section-type)=""', '', h)
    h = re.sub(r'shopify', 'shop', h, flags=re.I)  # kill residual fingerprints (e.g. pi-shopify_pay)
    # localize images
    h = localize_html(h)
    # for <img>: move data-src -> src, strip inline display:none/opacity so lazy imgs render
    def fix_img(m):
        tag = m.group(0)
        dsrc = re.search(r'data-src="([^"]+)"', tag)
        hassrc = re.search(r'\ssrc="([^"]+)"', tag)
        if dsrc and (not hassrc or '/assets/' not in (hassrc.group(1) if hassrc else '')):
            if hassrc:
                tag = re.sub(r'\ssrc="[^"]*"', f' src="{dsrc.group(1)}"', tag)
            else:
                tag = tag[:4] + f' src="{dsrc.group(1)}"' + tag[4:]
        # strip display:none / opacity:0 from inline style on images so they show
        def fix_style(sm):
            st = sm.group(1)
            st = re.sub(r'display:\s*none\s*!important;?', '', st, flags=re.I)
            st = re.sub(r'opacity:\s*0;?', 'opacity:1;', st, flags=re.I)
            return f'style="{st}"'
        tag = re.sub(r'style="([^"]*)"', fix_style, tag)
        return tag
    h = re.sub(r'<img\b[^>]*?/?>', fix_img, h)
    # reveal filter-hidden product cards: ProductItem / Grid__Cell carry inline
    # display:none (Shopify tab/filter default state shown by JS). Strip it ONLY
    # on those grid wrappers so the captured products render (not on search/drawers).
    def reveal_grid(m):
        tag = m.group(0)
        if re.search(r'class="[^"]*(ProductItem|ArticleItem|Grid__Cell|ProductList|ArticleList)[^"]*"', tag):
            def fs(sm):
                st = re.sub(r'display:\s*none\s*!important;?', '', sm.group(1), flags=re.I).strip()
                return f'style="{st}"' if st else ''
            tag = re.sub(r'style="([^"]*)"', fs, tag)
        return tag
    h = re.sub(r'<(?:div|a|article|li)\b[^>]*>', reveal_grid, h)
    # add 'is-loaded' to lazyload images so fadeIn CSS reveals them
    h = h.replace('Image--lazyLoad', 'Image--lazyLoad Image--lazyLoaded')
    return h.strip()

# ---------------------------------------------------------------- global CSS
def split_rules(css):
    """split top-level CSS into (selector_or_at, full_block) units honoring nesting."""
    rules = []
    i, n = 0, len(css)
    depth = 0; start = 0; buf = ""
    while i < n:
        c = css[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                rules.append(css[start:i+1].strip())
                start = i+1
        i += 1
    tail = css[start:].strip()
    if tail: rules.append(tail)
    return [r for r in rules if r]

seen = set(); global_rules = []
for s in data:
    css = s.get("css_rules","")
    if not css: continue
    for rule in split_rules(css):
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen: continue
        seen.add(key)
        global_rules.append(rule)

gcss = "\n".join(global_rules)
# de-shopify in CSS
gcss = gcss.replace('shopify-section', 'site-section')
# drop invalid @media (--css ...) blocks
gcss = re.sub(r'@media\s*\(--css[^{]*\)\s*\{(?:[^{}]|\{[^}]*\})*\}', '', gcss)
# fix brand @font-face: relative panolight/PagerieFont -> /assets/fonts (woff2+woff only)
def fix_fontface(m):
    block = m.group(0)
    fam = re.search(r'font-family:\s*["\']?([^;"\']+)', block)
    famname = fam.group(1).strip() if fam else ''
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
    # other @font-face: drop remote (http/ //cdn) srcs, keep /assets ones
    def keep_local(sm):
        srcval = sm.group(1)
        parts = [p.strip() for p in srcval.split(",")]
        kept = [p for p in parts if '/assets/' in p]
        if not kept: return 'src:' + parts[0] + ';' if parts else ''
        return 'src:' + ", ".join(kept) + ';'
    block = re.sub(r'src:\s*([^;}]+);?', keep_local, block, count=1)
    return block
gcss = re.sub(r'@font-face\s*\{[^}]*\}', fix_fontface, gcss)
# clean stray remote font urls in any remaining src
gcss = re.sub(r'url\((?:https?:)?//[^)]*\)\s*format\("[^"]*"\),?', '', gcss)
gcss = re.sub(r'url\(/cdn/[^)]*\)\s*format\("[^"]*"\),?', '', gcss)

# footer section has EMPTY css_rules → its styling (black bg, layout, newsletter)
# never made it into the union. Pull footer/newsletter rules straight from the
# full theme css.json so the footer renders correctly (black, not unstyled white).
themecss = json.load(open(f"{SRC}/css.json"))
_allcss = "\n".join((s.get("content","") if isinstance(s, dict) else str(s)) for s in themecss["stylesheets"])
_fpat = re.compile(r'\.(Footer|footer_|footer-|Newsletter|newsletter|top-newslatter)', re.I)
_footer_rules, _seenf = [], set()
for rule in split_rules(_allcss):
    sel = rule.split("{", 1)[0]
    if _fpat.search(sel) and "NewsletterPopup" not in sel:
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen or key in _seenf:
            continue
        _seenf.add(key)
        _footer_rules.append(rule)
footer_css = "\n".join(_footer_rules)
footer_css = footer_css.replace('shopify-section', 'site-section').replace('shopify', 'shop')
print(f"[css] footer theme rules added={len(_footer_rules)}")

header = (
    "/* === pagerie cleaned global theme CSS (deterministic union of section css_rules) === */\n"
    ":root{--header-height:71px;}\n"
)
ENHANCE = """
/* === pwc interaction-layer enhancements === */
.pwc-header{position:sticky;top:0;z-index:50;transition:box-shadow .3s ease;}
.pwc-header.is-scrolled .Header{box-shadow:0 1px 0 rgba(255,255,255,.12) inset,0 6px 24px rgba(0,0,0,.18);}
.ProductItem{position:relative;}
/* product-card image sizing: the captured AspectRatio uses padding-bottom to set
   the box height and expects BOTH imgs absolutely filling it (object-fit:cover).
   Without this the in-flow img stacks on top of the padding spacer → 2x-tall cards. */
.ProductItem__ImageWrapper{position:relative;display:block;}
/* AspectRatio height must come from ONE source. Some cards get a ::before height
   (then the inline padding-bottom doubles the box → 2x tall); others have no
   ::before and rely on the inline padding (zeroing it collapses them to 0 — the
   granite regression). Fix: make ::before the single height source from
   --aspect-ratio for ALL withFallback boxes, and zero the element's own padding. */
.AspectRatio--withFallback{padding-bottom:0!important;}
.AspectRatio--withFallback::before{content:""!important;display:block!important;padding-bottom:calc(100% / var(--aspect-ratio, 0.774))!important;}
.ProductItem__ImageWrapper .AspectRatio{position:relative;overflow:hidden;}
.ProductItem__ImageWrapper .AspectRatio>img,
.ProductItem .ProductItem__Image{position:absolute!important;top:0;left:0;width:100%!important;height:100%!important;object-fit:cover;}
.ProductItem__Image--alternate{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}
/* hover image-swap: the theme default `.ProductItem__Image--alternate{display:none}`
   survived the union but its `--withAlternateImage{display:block}` override did not,
   so the alt image stayed display:none and hover went blank. Restore the swap. */
.ProductItem__ImageWrapper--withAlternateImage .ProductItem__Image--alternate{display:block!important;opacity:0;transition:opacity .45s ease;}
.ProductItem__ImageWrapper--withAlternateImage .ProductItem__Image{transition:opacity .45s ease;}
.ProductItem__ImageWrapper--withAlternateImage:hover .ProductItem__Image--alternate{opacity:1!important;}
.ProductItem__ImageWrapper--withAlternateImage:hover .ProductItem__Image:not(.ProductItem__Image--alternate){opacity:0!important;}
/* Signature Collar (FeaturedProduct): the real site shows only the info text +
   the custom lifestyle image (.product_img greyhound); the product gallery
   thumbnail is NOT shown (left panel is empty black). Hide the stray gallery. */
.pwc-section-7 .FeaturedProduct__Gallery{display:none!important;}
.Image--lazyLoad{opacity:0;transition:opacity .7s ease;}
.Image--lazyLoad.is-loaded,.Image--lazyLoaded{opacity:1;}
/* carousel page dots */
.flickity-enabled{position:relative;}
.pwc-dots{position:absolute;bottom:18px;left:0;right:0;display:flex;justify-content:center;gap:9px;list-style:none;margin:0;padding:0;z-index:10;}
.pwc-dots li{width:8px;height:8px;border-radius:50%;background:rgba(0,0,0,.25);cursor:pointer;transition:background .25s ease;}
.pwc-dots li.is-on{background:#1a1a1a;}
/* drawers / search overlay reveal */
.pwc-scrim{position:fixed;inset:0;background:rgba(0,0,0,.45);opacity:0;visibility:hidden;transition:opacity .3s ease,visibility .3s ease;z-index:60;}
.pwc-scrim.is-open{opacity:1;visibility:visible;}
.Drawer{transition:transform .35s ease;z-index:70;}
.Drawer.is-open{transform:translateX(0)!important;visibility:visible!important;}
.Search.is-visible{pointer-events:auto!important;visibility:visible!important;opacity:1!important;transform:translateY(0)!important;z-index:65!important;}
body.pwc-locked{overflow:hidden;}
/* $100-off signup popup */
.pwc-popup-overlay{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
  background:rgba(20,18,16,.55);opacity:0;visibility:hidden;transition:opacity .32s ease,visibility .32s ease;z-index:120;padding:20px;}
.pwc-popup-overlay.is-open{opacity:1;visibility:visible;}
.pwc-popup{display:flex;width:760px;max-width:100%;background:#ece7df;color:#1a1a1a;position:relative;
  transform:translateY(14px) scale(.98);transition:transform .32s ease;box-shadow:0 30px 80px rgba(0,0,0,.4);overflow:hidden;}
.pwc-popup-overlay.is-open .pwc-popup{transform:none;}
.pwc-popup__media{flex:1 1 50%;background:#e7e1d7;}
.pwc-popup__media img{display:block;width:100%;height:100%;object-fit:cover;}
.pwc-popup__body{flex:1 1 50%;background:#000;color:#fff;padding:42px 34px;text-align:center;display:flex;flex-direction:column;justify-content:center;}
.pwc-popup__brand{font-family:"PagerieFont-Roman",serif;letter-spacing:3px;font-size:18px;margin-bottom:18px;}
.pwc-popup__kicker{font-family:"Pano-Light",sans-serif;letter-spacing:3px;font-size:11px;}
.pwc-popup__deal{font-family:"PagerieFont-Roman",serif;font-size:46px;line-height:1.1;margin:6px 0;}
.pwc-popup__sub{font-family:"Pano-Light",sans-serif;letter-spacing:2px;font-size:11px;margin-bottom:18px;}
.pwc-popup__legal{font-size:9px;line-height:1.5;color:#b9b9b9;letter-spacing:.3px;margin:0 0 16px;}
.pwc-popup__form input{width:100%;padding:13px 14px;border:1px solid #555;background:transparent;color:#fff;
  font-family:"Pano-Light",sans-serif;letter-spacing:1px;font-size:12px;margin-bottom:10px;}
.pwc-popup__form input::placeholder{color:#9a9a9a;}
.pwc-popup__form button{width:100%;padding:14px;background:#fff;color:#000;border:none;cursor:pointer;
  font-family:"Pano-Light",sans-serif;letter-spacing:2px;font-size:11px;text-transform:uppercase;}
.pwc-popup__foot{font-family:"Pano-Light",sans-serif;letter-spacing:1px;font-size:10px;color:#9a9a9a;margin-top:10px;}
.pwc-popup__close{position:absolute;top:10px;right:14px;background:none;border:none;color:#000;font-size:26px;line-height:1;cursor:pointer;z-index:2;}
@media (max-width:640px){.pwc-popup{flex-direction:column;width:360px;}.pwc-popup__media{max-height:170px;}}
"""
FOOTER_FIX = """
/* === footer layout/newsletter cleanup (Klaviyo form has no JS here) === */
.footer_top{display:flex;align-items:center;gap:40px;flex-wrap:wrap;padding-bottom:40px;}
.footer_logo{flex:0 0 auto;}
.footer_logo img{width:54px;height:auto;display:block;}
.top-newslatter{display:flex;gap:40px;align-items:center;flex:1 1 auto;flex-wrap:wrap;}
.newsletter-head{flex:1 1 300px;}
.newsletter-head p{color:#939393;margin:6px 0 0;}
.newsletter_block{flex:1 1 320px;}
.newsletter_block .klaviyo-form,.newsletter_block form{display:flex!important;gap:0;align-items:stretch;width:100%;padding:0!important;background:transparent!important;}
.newsletter_block input[type=email],.newsletter_block input:not([type=submit]):not([type=hidden]){flex:1 1 auto;background:transparent;border:1px solid #4a4a4a;border-right:none;color:#fff;padding:13px 14px;font-family:"Pano-Light",sans-serif;letter-spacing:1px;font-size:11px;text-transform:uppercase;min-width:0;}
.newsletter_block input::placeholder{color:#8a8a8a;}
.newsletter_block button,.newsletter_block input[type=submit]{flex:0 0 auto;background:#fff;color:#000;border:none;padding:13px 22px;cursor:pointer;font-family:"Pano-Light",sans-serif;letter-spacing:2px;font-size:11px;text-transform:uppercase;}
.newsletter_block .kl-private-reset-css-Xuajs1{width:100%!important;transform:none!important;}
"""
final_css = "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n" + header + gcss + "\n" + footer_css + "\n" + ENHANCE + FOOTER_FIX
with open(f"{SB}/src/index.css","w") as f:
    f.write(final_css)
print(f"[css] global rules={len(global_rules)} bytes={len(final_css)}")

# ---------------------------------------------------------------- components
# 'features' (order 6) is a bogus 1161px capture of the $100 popup snapshot — neutralize.
NEUTRALIZE = {"features"}
for s in data:
    ns = s["namespace"]; comp = s["component_name"]
    if ns in NEUTRALIZE:
        code = (f"// {comp} — neutralized: extractor mis-captured the $100 popup snapshot here.\n"
                f"export default function {comp}() {{ return null; }}\n")
        d = f"{SB}/src/components/sections/{ns}"
        os.makedirs(d, exist_ok=True)
        open(f"{d}/{comp}.jsx","w").write(code)
        continue
    inner = clean_section(s)
    js = json.dumps(inner)  # safe JS string
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
print("[done]")
