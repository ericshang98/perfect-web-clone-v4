"""Tests for core.site_classifier.classify_site — deterministic, pre-clone site
typing so the brain can warn the user about a known fidelity ceiling BEFORE
promising a pixel-perfect clone (scroll-choreography / WebGL sites cannot be
faithfully reproduced statically; Shopify stores and static pages can).
"""
from core.site_classifier import classify_site


def test_canvas_site_flags_webgl_ceiling():
    html = '<canvas width="1440" height="900"></canvas><script src="/three.min.js"></script>'
    r = classify_site(html, {"animation_count": 2})
    assert r["site_type"] == "webgl_canvas"
    assert r["ceiling"]               # non-empty advisory
    assert r["can_clone_well"] is False


def test_gsap_scrolltrigger_is_scroll_choreography():
    html = '<div data-scroll></div><script>gsap.registerPlugin(ScrollTrigger)</script>'
    r = classify_site(html, {})
    assert r["site_type"] == "scroll_choreography"
    assert r["can_clone_well"] is False


def test_lenis_is_scroll_choreography():
    r = classify_site('<script src="https://unpkg.com/lenis"></script>', {})
    assert r["site_type"] == "scroll_choreography"


def test_shopify_store_clones_well():
    html = '<link href="https://cdn.shopify.com/s/files/x.css"><body class="shopify">'
    r = classify_site(html, {})
    assert r["site_type"] == "shopify_store"
    assert r["can_clone_well"] is True
    assert r["ceiling"] == ""


def test_plain_static_clones_well():
    html = "<header>Hi</header><main><p>content</p></main><footer>x</footer>"
    r = classify_site(html, {"total_elements": 400})
    assert r["site_type"] == "static"
    assert r["can_clone_well"] is True


def test_canvas_beats_scroll_when_both_present():
    html = '<canvas width="800" height="600"></canvas><script>gsap.to(".x")</script>'
    r = classify_site(html, {})
    assert r["site_type"] == "webgl_canvas"
