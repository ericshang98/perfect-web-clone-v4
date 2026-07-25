"""Regressions for section-planning state normalization.

Deliberately hidden application UI must stay hidden on ordinary/Shopify pages.
Only a page positively classified as scroll choreography may have frozen reveal
styles neutralized.
"""

import json

from mcp_server.tools.extraction import get_section_plan
from mcp_server.tools.extraction import _normalize_section_animation_states


def _section(html):
    return {"name": "fixture", "full_html": html}


def test_shopify_cart_drawer_remains_hidden():
    sections = [
        _section(
            '<cart-drawer class="drawer" style="display: none !important;">'
            '<h2>Your cart is empty</h2></cart-drawer>'
        )
    ]
    raw_html = '<link href="https://cdn.shopify.com/theme.css">' + sections[0]["full_html"]

    changed = _normalize_section_animation_states(sections, raw_html)

    assert changed == 0
    assert "display: none !important" in sections[0]["full_html"]
    assert "hidden_revealed" not in sections[0]


def test_scroll_choreography_still_reveals_frozen_content():
    sections = [_section('<h1 style="display: none !important;">EverSwap</h1>')]
    raw_html = (
        "<script>gsap.registerPlugin(ScrollTrigger)</script>"
        + sections[0]["full_html"]
    )

    changed = _normalize_section_animation_states(sections, raw_html)

    assert changed == 1
    assert "display: none" not in sections[0]["full_html"]
    assert sections[0]["hidden_revealed"] == 1


def test_static_modal_remains_hidden():
    sections = [_section('<dialog style="visibility: hidden;">Subscribe</dialog>')]

    changed = _normalize_section_animation_states(sections, "<main>Static page</main>")

    assert changed == 0
    assert "visibility: hidden" in sections[0]["full_html"]


def _write_source(tmp_path, sid, integrity=None):
    source = tmp_path / sid
    source.mkdir()
    manifest = {"success": True}
    if integrity is not None:
        manifest["capture_integrity"] = integrity
    (source / "manifest.json").write_text(json.dumps(manifest))
    (source / "summary.json").write_text(
        json.dumps(
            {
                "source_id": sid,
                "url": "https://example.com",
                "title": "Example",
                "success": True,
            }
        )
    )
    (source / "raw.html").write_text("<main><h1>Example</h1></main>")


def test_section_planning_blocks_failed_capture_integrity(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    _write_source(
        tmp_path,
        "failed-source",
        {"status": "failed", "ok": False, "missing_critical": ["hero"]},
    )

    result = get_section_plan("failed-source")

    assert result["ok"] is False
    assert "capture integrity" in result["error"].lower()
    assert result["capture_integrity"]["status"] == "failed"


def test_section_planning_blocks_unknown_legacy_capture(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    _write_source(tmp_path, "unknown-source")

    result = get_section_plan("unknown-source")

    assert result["ok"] is False
    assert "unknown" in result["error"].lower()
