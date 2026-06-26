# pwc4 Capture Completeness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Layer-0 capture grab **all** referenced images (incl. lazy `data-src`/`srcset`/`data-image-url` + Shopify `{width}` templates) and **theme-relative fonts**, and strengthen popup dismissal — so the default route produces a complete, standalone clone instead of hotlinking/missing 80%+ of assets.

**Architecture:** The image/font URL logic is extracted into a new **pure Python module** `core/extractor/asset_urls.py` (browser-free, unit-testable). The in-page `ASSETS_JS` snippet is widened to emit each image's full set of source attributes + each font's stylesheet href; `_extract_assets` then runs the pure normalizer over that raw payload. Download caps are raised. Overlay dismissal gains newsletter/dialog handling.

**Tech Stack:** Python 3.12, pydantic models, Playwright (capture), pytest (`.venv/bin/python -m pytest`).

**Scope note:** This is **plan 1 of 4** for "make the winning route the default" (see [[pwc4-default-route]] memory). Follow-on plans, to be written next: (2) `assemble_project` injects a deduped global cleaned stylesheet by default; (3) componentize by `#main` real children instead of the chunker; (4) fix `check_weight` MCP crash + split code/asset weight budgets. Each is an independent subsystem producing working software.

---

### Task 1: `expand_image_urls` — recover all image URLs from one element

**Files:**
- Create: `core/extractor/asset_urls.py`
- Test: `tests/test_asset_urls.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_asset_urls.py
from core.extractor import asset_urls


def test_plain_src_passes_through():
    assert asset_urls.expand_image_urls({"src": "https://x/a.png"}) == ["https://x/a.png"]


def test_lazy_data_src_with_width_template_substituted():
    out = asset_urls.expand_image_urls(
        {"src": "data:image/gif;base64,AAAA", "dataSrc": "https://cdn/shop/p_{width}x.jpg"}
    )
    assert out == ["https://cdn/shop/p_1200x.jpg"]  # placeholder src skipped, {width}->1200


def test_srcset_expanded_to_all_candidates():
    out = asset_urls.expand_image_urls({"srcset": "https://x/a_300.jpg 300w, https://x/a_900.jpg 900w"})
    assert out == ["https://x/a_300.jpg", "https://x/a_900.jpg"]


def test_data_image_url_and_bg_collected():
    out = asset_urls.expand_image_urls({"dataImageUrl": "https://x/hover.png", "bg": "https://x/bg.jpg"})
    assert set(out) == {"https://x/hover.png", "https://x/bg.jpg"}


def test_relative_url_joined_and_protocol_relative_https():
    assert asset_urls.expand_image_urls({"src": "/cdn/a.png"}, base_url="https://site.com/x") == ["https://site.com/cdn/a.png"]
    assert asset_urls.expand_image_urls({"src": "//cdn/a.png"}) == ["https://cdn/a.png"]


def test_dedupes_and_skips_data_blob_and_unsubstituted_templates():
    out = asset_urls.expand_image_urls(
        {"src": "https://x/a.png", "dataSrc": "https://x/a.png", "srcset": "blob:xyz 1x, {bad} 2x"}
    )
    assert out == ["https://x/a.png"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -q`
Expected: FAIL — `ModuleNotFoundError: core.extractor.asset_urls`

- [ ] **Step 3: Write minimal implementation**

```python
# core/extractor/asset_urls.py
"""Pure helpers to recover every image URL an element can carry, and to
absolutize theme-relative @font-face URLs. No network, no browser, no LLM.

Why: lazy-loaded images (Shopify/Webflow) keep the real URL in
``data-src``/``srcset``/``data-image-url`` — often with a ``{width}`` template —
while the rendered ``src`` is a 1px placeholder. The old ASSETS_JS only read
``img.src``, so those were never collected (pagerie: 21 of 107 captured).
"""
from __future__ import annotations

from urllib.parse import urljoin

_TEMPLATE_WIDTH = "1200"  # concrete width substituted for {width} URL templates


def _subst_width(url: str) -> str:
    return url.replace("{width}", _TEMPLATE_WIDTH)


def _parse_srcset(srcset: str) -> list[str]:
    out = []
    for part in srcset.split(","):
        token = part.strip().split(" ")[0].strip()
        if token:
            out.append(token)
    return out


def expand_image_urls(img: dict, base_url: str = "") -> list[str]:
    """Return de-duped concrete image URLs from one element's attributes.

    Recognized keys (any may be absent): ``src``, ``srcset``, ``dataSrc``,
    ``dataSrcset``, ``dataImageUrl``, ``bg``. ``{width}`` is substituted; srcset
    is expanded to all candidates; relative/protocol-relative URLs are resolved.
    """
    raw: list[str] = []
    for key in ("src", "dataSrc", "dataImageUrl", "bg"):
        v = img.get(key)
        if v:
            raw.append(v)
    for key in ("srcset", "dataSrcset"):
        v = img.get(key)
        if v:
            raw.extend(_parse_srcset(v))

    out: list[str] = []
    seen: set[str] = set()
    for u in raw:
        u = _subst_width(u.strip())
        if not u or u.startswith(("data:", "blob:")) or "{" in u:
            continue
        if u.startswith("//"):
            u = "https:" + u
        elif base_url and not u.startswith(("http://", "https://")):
            u = urljoin(base_url, u)
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -q`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add core/extractor/asset_urls.py tests/test_asset_urls.py
git commit -m "feat(extractor): expand_image_urls recovers lazy/srcset/template image URLs"
```

---

### Task 2: `absolutize_font_url` — resolve theme-relative @font-face URLs

**Files:**
- Modify: `core/extractor/asset_urls.py`
- Test: `tests/test_asset_urls.py`

- [ ] **Step 1: Write the failing test (append to tests/test_asset_urls.py)**

```python
def test_font_absolute_url_unchanged():
    assert asset_urls.absolutize_font_url("https://x/f.woff2", None) == "https://x/f.woff2"


def test_font_relative_resolved_against_sheet_href():
    out = asset_urls.absolutize_font_url("panolight.woff2", "https://site.com/cdn/t/3/assets/theme.css")
    assert out == "https://site.com/cdn/t/3/assets/panolight.woff2"


def test_font_relative_falls_back_to_page_url():
    out = asset_urls.absolutize_font_url("f.woff2", None, page_url="https://site.com/")
    assert out == "https://site.com/f.woff2"


def test_font_data_uri_and_empty_return_none():
    assert asset_urls.absolutize_font_url("data:font/woff2;base64,AA", "https://x/t.css") is None
    assert asset_urls.absolutize_font_url("", "https://x/t.css") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -k font -q`
Expected: FAIL — `AttributeError: module ... has no attribute 'absolutize_font_url'`

- [ ] **Step 3: Write minimal implementation (append to core/extractor/asset_urls.py)**

```python
def absolutize_font_url(raw: str, sheet_href: str | None, page_url: str = "") -> str | None:
    """Resolve a @font-face url() that may be relative to its stylesheet.

    Theme fonts are declared ``url("panolight.woff2")`` relative to the theme
    CSS file; resolving against ``sheet_href`` (preferred) or ``page_url`` gives
    a downloadable absolute URL. Returns None for data: URIs / empty input.
    """
    if not raw:
        return None
    u = raw.strip().strip('"\'')
    if not u or u.startswith("data:"):
        return None
    if u.startswith(("http://", "https://")):
        return u
    if u.startswith("//"):
        return "https:" + u
    base = sheet_href or page_url
    if not base:
        return None
    return urljoin(base, u)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -q`
Expected: PASS (10 passed)

- [ ] **Step 5: Commit**

```bash
git add core/extractor/asset_urls.py tests/test_asset_urls.py
git commit -m "feat(extractor): absolutize_font_url resolves theme-relative font URLs"
```

---

### Task 3: `normalize_assets` — turn raw ASSETS_JS payload into AssetInfo URL lists

**Files:**
- Modify: `core/extractor/asset_urls.py`
- Test: `tests/test_asset_urls.py`

This is the seam `_extract_assets` will call, so the integration stays unit-testable without a browser.

- [ ] **Step 1: Write the failing test (append)**

```python
def test_normalize_assets_expands_images_and_fonts():
    raw = {
        "images": [
            {"src": "data:image/gif;base64,A", "dataSrc": "https://cdn/p_{width}x.jpg"},
            {"src": "https://cdn/logo.svg"},
        ],
        "fonts": [{"url": "panolight.woff2", "sheetHref": "https://site.com/t/assets/x.css"}],
    }
    norm = asset_urls.normalize_assets(raw, base_url="https://site.com/")
    assert [i["url"] for i in norm["images"]] == ["https://cdn/p_1200x.jpg", "https://cdn/logo.svg"]
    assert [f["url"] for f in norm["fonts"]] == ["https://site.com/t/assets/panolight.woff2"]
    assert all(i["type"] == "image" for i in norm["images"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -k normalize -q`
Expected: FAIL — `AttributeError: ... 'normalize_assets'`

- [ ] **Step 3: Write minimal implementation (append)**

```python
def normalize_assets(raw: dict, base_url: str = "") -> dict:
    """Expand a raw ASSETS_JS payload into deduped {url,type} lists.

    Input ``raw`` keys: images (list of attr dicts), fonts (list of
    {url, sheetHref}), plus scripts/stylesheets/videos passed through. Output
    mirrors the structure with concrete, absolute, deduped URLs.
    """
    img_seen: set[str] = set()
    images = []
    for it in raw.get("images") or []:
        for u in expand_image_urls(it, base_url):
            if u not in img_seen:
                img_seen.add(u)
                images.append({"url": u, "type": it.get("type") or "image"})

    font_seen: set[str] = set()
    fonts = []
    for it in raw.get("fonts") or []:
        u = absolutize_font_url(it.get("url", ""), it.get("sheetHref"), base_url)
        if u and u not in font_seen:
            font_seen.add(u)
            fonts.append({"url": u, "type": "font"})

    return {
        "images": images,
        "fonts": fonts,
        "scripts": raw.get("scripts") or [],
        "stylesheets": raw.get("stylesheets") or [],
        "videos": raw.get("videos") or [],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py -q`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add core/extractor/asset_urls.py tests/test_asset_urls.py
git commit -m "feat(extractor): normalize_assets seam for browser-free asset URL expansion"
```

---

### Task 4: Widen `ASSETS_JS` to emit all image attrs + font sheet href

**Files:**
- Modify: `core/extractor/dom_scripts.py` (the `ASSETS_JS` constant, starts line 148)

No new unit test (it is an in-browser JS string; covered by the Task 6 acceptance run). Keep the change mechanical and minimal.

- [ ] **Step 1: Replace the `<img>` collection + font loop in `ASSETS_JS`**

Replace the image collection block:

```js
    document.querySelectorAll('img').forEach(img => {
        if (img.src) result.images.push({ url: img.src, type: 'image' });
    });
```

with (emit every source attribute the normalizer understands):

```js
    const imgAttr = (el, name) => el.getAttribute(name) || '';
    document.querySelectorAll('img, source[srcset], source[data-srcset]').forEach(el => {
        result.images.push({
            type: 'image',
            src: el.currentSrc || el.getAttribute('src') || '',
            srcset: imgAttr(el, 'srcset'),
            dataSrc: imgAttr(el, 'data-src') || imgAttr(el, 'data-lazy-src') || imgAttr(el, 'data-original'),
            dataSrcset: imgAttr(el, 'data-srcset') || imgAttr(el, 'data-lazy-srcset'),
            dataImageUrl: imgAttr(el, 'data-image-url') || imgAttr(el, 'data-bg') || imgAttr(el, 'data-background')
        });
    });
```

- [ ] **Step 2: Replace the background-image push to carry the `bg` key**

Change:

```js
            if (m && m[1]) result.images.push({ url: m[1], type: 'background-image' });
```

to:

```js
            if (m && m[1]) result.images.push({ type: 'background-image', bg: m[1] });
```

- [ ] **Step 3: Make the @font-face loop carry the stylesheet href**

Change:

```js
                if (m && m[1]) result.fonts.push({ url: m[1], type: 'font' });
```

to (split multiple url() and remember the owning sheet so relative theme fonts resolve):

```js
                if (m && m[1]) result.fonts.push({ url: m[1], type: 'font', sheetHref: sheet.href || '' });
```

- [ ] **Step 4: Verify the file still parses (import smoke test)**

Run: `.venv/bin/python -c "from core.extractor import dom_scripts; assert 'dataImageUrl' in dom_scripts.ASSETS_JS and 'sheetHref' in dom_scripts.ASSETS_JS; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add core/extractor/dom_scripts.py
git commit -m "feat(extractor): ASSETS_JS emits all image source attrs + font sheet href"
```

---

### Task 5: Wire `_extract_assets` to the normalizer + raise download caps

**Files:**
- Modify: `core/extractor/service.py` (`_extract_assets`, ~line 324)
- Modify: `core/extractor/models.py` (`ExtractOptions`, line 363: `max_images`, `max_fonts`)
- Test: `tests/test_extract_assets_normalize.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extract_assets_normalize.py
"""_extract_assets must expand a raw ASSETS_JS payload via asset_urls.normalize_assets."""
import asyncio
from core.extractor.service import ExtractorService


class _FakePage:
    def __init__(self, payload): self._p = payload
    async def evaluate(self, *a, **k): return self._p


def test_extract_assets_uses_normalizer(monkeypatch):
    payload = {
        "images": [{"src": "data:image/gif;base64,A", "dataSrc": "https://cdn/p_{width}x.jpg"}],
        "fonts": [{"url": "f.woff2", "sheetHref": "https://site.com/t/x.css"}],
        "scripts": [], "stylesheets": [], "videos": [],
    }
    svc = ExtractorService()
    svc._asset_base_url = "https://site.com/"   # set by extract(); see Step 3
    out = asyncio.run(svc._extract_assets(_FakePage(payload)))
    assert [i.url for i in out.images] == ["https://cdn/p_1200x.jpg"]
    assert [f.url for f in out.fonts] == ["https://site.com/t/f.woff2"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_extract_assets_normalize.py -q`
Expected: FAIL (images empty / no `_asset_base_url` handling / placeholder src kept).

- [ ] **Step 3: Rewrite `_extract_assets` body to call the normalizer**

In `core/extractor/service.py`, replace the dedupe + list-building block inside `_extract_assets` (the part after `if not data: return PageAssets()`) with:

```python
        from core.extractor import asset_urls
        base = getattr(self, "_asset_base_url", "") or ""
        norm = asset_urls.normalize_assets(data, base_url=base)

        def to_assets(items):
            return [AssetInfo(url=i["url"], type=i.get("type", "image")) for i in items]

        images = to_assets(norm["images"])
        fonts = to_assets(norm["fonts"])
        scripts = [AssetInfo(**i) for i in norm["scripts"]]
        stylesheets = [AssetInfo(**i) for i in norm["stylesheets"]]
        videos = [AssetInfo(**i) for i in (norm["videos"] or [])]
        return PageAssets(
            images=images, scripts=scripts, stylesheets=stylesheets,
            fonts=fonts, videos=videos,
            total_images=len(images), total_scripts=len(scripts),
            total_stylesheets=len(stylesheets), total_fonts=len(fonts),
            total_videos=len(videos),
        )
```

Then in `extract()` (around line 145, right after resolving the navigated URL), set the base used for resolution:

```python
                self._asset_base_url = response.url if response else url
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_extract_assets_normalize.py -q`
Expected: PASS

- [ ] **Step 5: Raise download caps in `ExtractOptions`**

In `core/extractor/models.py` change:

```python
    max_images: int = 40
    max_fonts: int = 12
```

to:

```python
    max_images: int = 150   # image-heavy stores (e.g. Shopify) reference 100+ originals
    max_fonts: int = 24
```

- [ ] **Step 6: Run full extractor-related tests + commit**

Run: `.venv/bin/python -m pytest tests/test_asset_urls.py tests/test_extract_assets_normalize.py tests/test_asset_localizer.py -q`
Expected: PASS

```bash
git add core/extractor/service.py core/extractor/models.py tests/test_extract_assets_normalize.py
git commit -m "feat(extractor): wire _extract_assets to normalizer; raise image/font caps"
```

---

### Task 6: Strengthen overlay dismissal for newsletter/dialog popups

**Files:**
- Modify: `core/extractor/dom_scripts.py` (`DISMISS_OVERLAYS_JS`)

The pagerie `$900 GIFT` newsletter popup survived dismissal (its close control didn't match). Add dialog-role + newsletter close selectors, staying navigation-safe (never click `<a href>`).

- [ ] **Step 1: Extend the `CLOSE_SEL` list**

In `DISMISS_OVERLAYS_JS`, add these entries to the `CLOSE_SEL` array:

```js
    '[class*="newsletter" i] [class*="close" i]','[class*="Popup" i] [class*="close" i]',
    '[data-action*="close" i]','[class*="needsclick" i][class*="close" i]','.klaviyo-close-form',
    'div[role="dialog"] button','[aria-modal="true"] button[class*="close" i]'
```

- [ ] **Step 2: After the close-click loop, hard-hide any leftover modal/dialog**

Append before `return closed;`:

```js
  // Last resort: visually remove still-open newsletter/promo dialogs so they
  // don't bake into the reference raster. Never removes <a>-navigating content.
  document.querySelectorAll('[role="dialog"],[aria-modal="true"],[class*="newsletter" i],[class*="popup" i],[id*="popup" i]').forEach(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const onTop = (cs.position === 'fixed' || cs.position === 'absolute') && parseInt(cs.zIndex || '0', 10) >= 100;
    if (onTop && r.width > 200 && r.height > 120 && !el.querySelector('header,nav')) {
      el.style.setProperty('display', 'none', 'important'); closed++;
    }
  });
```

- [ ] **Step 3: Verify the file parses**

Run: `.venv/bin/python -c "from core.extractor import dom_scripts; assert 'klaviyo-close-form' in dom_scripts.DISMISS_OVERLAYS_JS; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add core/extractor/dom_scripts.py
git commit -m "feat(extractor): dismiss newsletter/dialog popups before capture"
```

---

### Task 7: Acceptance — re-extract pagerie and assert completeness

**Files:**
- Test: `tests/test_capture_completeness_acceptance.py` (network/browser; mark slow)

- [ ] **Step 1: Write the acceptance test**

```python
# tests/test_capture_completeness_acceptance.py
"""Live acceptance: the widened capture must grab the bulk of pagerie's images
+ the brand fonts. Skipped unless RUN_LIVE=1 (needs network + chromium)."""
import os, asyncio, pytest
from core.extractor.service import ExtractorService
from core.extractor.models import ExtractOptions

pytestmark = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="live capture; set RUN_LIVE=1")


def test_pagerie_capture_grabs_images_and_brand_fonts():
    svc = ExtractorService()
    res = asyncio.run(svc.extract("https://www.pagerie.com",
                                  ExtractOptions(settle_ms=9000, max_images=150, max_fonts=24)))
    dl = res.downloaded
    assert len(dl.images) >= 80, f"only {len(dl.images)} images captured (want >=80)"
    font_names = " ".join((f.filename or f.url).lower() for f in dl.fonts)
    assert "pano" in font_names or "pagerie" in font_names, "brand fonts not captured"
```

- [ ] **Step 2: Run it live**

Run: `RUN_LIVE=1 .venv/bin/python -m pytest tests/test_capture_completeness_acceptance.py -q -s`
Expected: PASS — `dl.images >= 80` and brand fonts present (was 21 images / 0 brand fonts before this plan).

- [ ] **Step 3: Commit**

```bash
git add tests/test_capture_completeness_acceptance.py
git commit -m "test(extractor): live acceptance for pagerie capture completeness"
```

---

## Self-Review

- **Spec coverage:** capture all images (Tasks 1,3,4,5) ✓; lazy `data-src`/`srcset`/`data-image-url` + `{width}` (Task 1) ✓; theme fonts (Tasks 2,4,5) ✓; raise caps (Task 5) ✓; popup dismissal (Task 6) ✓; proof on pagerie (Task 7) ✓. Global-CSS default, `#main` componentization, and weight-gate fixes are **out of scope here** — explicitly deferred to follow-on plans 2–4.
- **Placeholder scan:** none — every code step has full code.
- **Type consistency:** `expand_image_urls` (Task 1) → used by `normalize_assets` (Task 3) → used by `_extract_assets` (Task 5); `absolutize_font_url` (Task 2) → `normalize_assets` (Task 3). `normalize_assets` output keys (`images`/`fonts`/`scripts`/`stylesheets`/`videos`) match `_extract_assets` consumption. `AssetInfo(url, type)` matches the model (url, type, size optional).
