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
