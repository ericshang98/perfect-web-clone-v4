"""Tests for core.embed_handler — neutralize un-cloneable third-party embeds.

Live third-party widgets embedded via cross-origin ``<iframe>`` (Loox reviews,
chat bubbles, maps) can never work in a clone: the provider only serves the
authorized shop origin, so the frame renders "refused to connect". A faithful
clone must degrade these gracefully — replace them with a clean, sized
placeholder rather than leaving an ugly error block. Pure, deterministic, no LLM.
"""

from core import embed_handler


def test_neutralizes_cross_origin_iframe():
    html = (
        '<iframe title="Reviews widget" src="https://loox.io/widget/x/reviews" '
        'height="1612px" width="100%"></iframe>'
    )
    out, n = embed_handler.neutralize_embeds(html, page_url="https://livora.co/products/foo")
    assert n == 1
    assert "loox.io" not in out
    assert "Reviews widget" in out  # title preserved as label
    assert "pwc-embed-placeholder" in out


def test_keeps_same_origin_iframe():
    html = '<iframe src="https://livora.co/embed/x"></iframe>'
    out, n = embed_handler.neutralize_embeds(html, page_url="https://livora.co/products/foo")
    assert n == 0
    assert out == html


def test_handles_self_closing_iframe():
    html = '<iframe src="https://loox.io/w" width="100%" height="800px"/>'
    out, n = embed_handler.neutralize_embeds(html, page_url="https://livora.co")
    assert n == 1
    assert "loox.io" not in out


def test_preserves_dimensions_for_layout_stability():
    html = '<iframe src="https://loox.io/w" height="1612px" width="100%"></iframe>'
    out, _ = embed_handler.neutralize_embeds(html, page_url="https://livora.co")
    assert "1612px" in out


def test_protocol_relative_external_iframe_is_neutralized():
    html = '<iframe src="//www.youtube.com/embed/abc"></iframe>'
    out, n = embed_handler.neutralize_embeds(html, page_url="https://livora.co")
    assert n == 1
    assert "youtube.com" not in out


def test_no_iframes_is_noop():
    out, n = embed_handler.neutralize_embeds("<div>hi</div>", "https://x.com")
    assert n == 0
    assert out == "<div>hi</div>"


def test_replaces_with_snapshot_image_when_available():
    # During extraction we were on the authorized origin, so the widget rendered
    # and we screenshotted it. The clone should show that static snapshot.
    html = (
        '<iframe title="Reviews" src="https://loox.io/widget/x/reviews?h=1" '
        'height="1612px" width="100%"></iframe>'
    )
    snap = {"https://loox.io/widget/x/reviews?h=1": "/assets/embeds/loox-reviews.png"}
    out, n = embed_handler.neutralize_embeds(html, "https://livora.co", snapshot_map=snap)
    assert n == 1
    assert "/assets/embeds/loox-reviews.png" in out
    assert "<img" in out
    assert "loox.io" not in out
    assert "1612px" in out  # keep the original dimensions


def test_snapshot_matches_by_path_ignoring_volatile_query():
    # The iframe src carries a volatile h=<timestamp>; match by path, not query.
    html = '<iframe src="https://loox.io/widget/x/reviews?h=999&limit=5" height="800"></iframe>'
    snap = {"https://loox.io/widget/x/reviews?h=111": "/assets/embeds/r.png"}
    out, n = embed_handler.neutralize_embeds(html, "https://livora.co", snapshot_map=snap)
    assert n == 1
    assert "/assets/embeds/r.png" in out


def test_falls_back_to_placeholder_when_no_snapshot():
    html = '<iframe src="https://loox.io/w"></iframe>'
    out, n = embed_handler.neutralize_embeds(html, "https://livora.co", snapshot_map={})
    assert n == 1
    assert "pwc-embed-placeholder" in out


def test_neutralize_section_in_place():
    sec = {
        "name": "reviews",
        "full_html": '<iframe title="Reviews" src="https://loox.io/w" height="900px"></iframe>',
    }
    n = embed_handler.neutralize_section_embeds(sec, "https://livora.co/products/foo")
    assert n == 1
    assert "loox.io" not in sec["full_html"]
    assert "900px" in sec["full_html"]
