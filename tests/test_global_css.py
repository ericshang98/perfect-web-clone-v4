"""P0 — full ordered theme-CSS injection (fixes the cascade-blind per-section union).

build_global_css concatenates the captured stylesheets IN CAPTURE ORDER (so the
cascade is preserved — the root cause of pagerie's card-doubling / hover-blank /
footer-white bugs), localizes url(...) to local assets, strips source-site traces,
and de-fingerprints so the R1 gate stays green. defingerprint is shared with the
HTML side so class names stay consistent (.shopify-section ↔ class="shopify-section"
become the same scrubbed token in both)."""
from core.codegen.global_css import build_global_css
from core.output_sanitizer import defingerprint
from core.asset_localizer import localize_css


def _sheet(content, url="", inline=False):
    return {"url": url, "content": content, "is_inline": inline}


def test_concatenates_in_capture_order():
    sheets = [_sheet(".a{color:red}", "1.css"), _sheet(".a{color:blue}", "2.css")]
    out = build_global_css(sheets)
    # both present, and the later sheet appears after the earlier (cascade: blue wins)
    assert out.index("color:red") < out.index("color:blue")


def test_localizes_url_to_local_asset():
    amap = {"https://cdn/shop/f.woff2": "/assets/fonts/f.woff2"}
    out = build_global_css([_sheet("@font-face{src:url(https://cdn/shop/f.woff2)}")], asset_map=amap)
    assert "/assets/fonts/f.woff2" in out
    assert "cdn/shop/f.woff2" not in out


def test_strips_source_domain_and_myshopify():
    css = ".x{background:url(https://store.com/cdn/a.png)} /* store.myshopify.com */"
    out = build_global_css([_sheet(css)], source_url="https://store.com")
    assert "store.com" not in out
    assert "myshopify.com" not in out


def test_defingerprints_so_r1_gate_stays_clean():
    css = ".shopify-section{margin:0} #template--123__main{x:1} /*shopify*/"
    out = build_global_css([_sheet(css)])
    for bad in ("shopify", "shopify-section", "myshopify", "original.css"):
        assert bad not in out.lower()
    import re
    assert not re.search(r"template--[\w-]+__", out)


def test_empty_and_none_safe():
    assert build_global_css([]) == ""
    assert build_global_css(None) == ""
    assert build_global_css([_sheet("")]) == ""


def test_defingerprint_consistent_between_html_and_css():
    # the SAME scrub on a class in HTML and its selector in CSS must still match
    html_class = defingerprint('class="shopify-section ProductItem"')
    css_sel = defingerprint(".shopify-section{display:block}")
    token = "shopify"  # the fingerprint token both sides carried
    assert token not in html_class.lower() and token not in css_sel.lower()
    # the scrubbed wrapper token is identical on both sides → selector still matches
    assert "-section" in html_class and "-section{" in css_sel


def test_localize_css_passes_through_unmapped():
    out = localize_css("a{background:url(/keep/me.png)}", {})
    assert "/keep/me.png" in out
