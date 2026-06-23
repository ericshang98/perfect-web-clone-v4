"""Wiring test: section data must point at downloaded local assets, not hotlinks.

Regression guard for "the clone hotlinks images and breaks when a host refuses".
``get_section_data`` must rewrite downloaded image URLs to their local paths and
leave un-downloadable ones (e.g. Loox) untouched for an onerror fallback.
"""

import json


def _make_source(root, sid):
    d = root / sid
    d.mkdir()
    (d / "manifest.json").write_text(
        json.dumps(
            {
                "downloaded_resources": {
                    "images": [
                        {"url": "https://cdn.shopify.com/x/foo.png", "saved_path": "assets/images/foo.png"}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (d / "raw.html").write_text(
        "<html><body>"
        '<header class="h"><img src="https://cdn.shopify.com/x/foo.png"></header>'
        '<section class="s"><img src="https://loox.io/blocked.png"></section>'
        "</body></html>",
        encoding="utf-8",
    )


def test_section_data_localizes_downloaded_images(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "shop.com-1-loc"
    _make_source(tmp_path, sid)

    from mcp_server.tools import extraction

    plan = extraction.get_section_plan(sid)
    assert plan["ok"], plan
    names = [s["name"] for s in plan["sections"]]
    all_html = " ".join(extraction.get_section_data(sid, n).get("raw_html", "") for n in names)

    # Downloaded image now points at the local copy, not the CDN.
    assert "/assets/images/foo.png" in all_html
    assert "https://cdn.shopify.com/x/foo.png" not in all_html
    # Un-downloadable third-party image is left alone (onerror fallback covers it).
    assert "https://loox.io/blocked.png" in all_html


def test_section_data_uses_embed_snapshot_for_cross_origin_iframe(tmp_path, monkeypatch):
    import json
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "shop.com-2-embed"
    d = tmp_path / sid
    d.mkdir()
    (d / "manifest.json").write_text("{}", encoding="utf-8")
    (d / "raw.html").write_text(
        "<html><body>"
        '<header class="h"><a href="/x">x</a></header>'
        '<section class="reviews"><iframe title="Reviews" '
        'src="https://loox.io/widget/x/reviews?h=1" height="1612px" width="100%"></iframe></section>'
        "</body></html>",
        encoding="utf-8",
    )
    (d / "embeds.json").write_text(
        json.dumps({"embeds": [
            {"src": "https://loox.io/widget/x/reviews?h=1", "saved_path": "assets/embeds/looxReviewsFrame.png",
             "title": "Reviews", "width": "1080", "height": "1612"}
        ]}),
        encoding="utf-8",
    )
    from mcp_server.tools import extraction
    plan = extraction.get_section_plan(sid)
    assert plan["ok"], plan
    names = [s["name"] for s in plan["sections"]]
    all_html = " ".join(extraction.get_section_data(sid, n).get("raw_html", "") for n in names)
    assert "loox.io" not in all_html              # live iframe gone
    assert "/assets/embeds/looxReviewsFrame.png" in all_html  # static snapshot used
