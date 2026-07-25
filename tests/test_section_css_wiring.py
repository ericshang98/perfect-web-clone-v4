"""Wiring test: the section pipeline must hand each sub-agent its real CSS.

This is the regression guard for the "interactions come out approximate" bug:
the page-wide CSS (hover/animation/responsive) was extracted but never reached
the per-section sub-agent. ``get_section_data`` must now carry a ``css_rules``
field populated from ``css.json``.
"""

import json

import pytest


def _make_source(root, sid):
    d = root / sid
    d.mkdir()
    (d / "manifest.json").write_text(
        json.dumps(
            {
                "success": True,
                "capture_integrity": {"ok": True, "status": "passed"},
            }
        ),
        encoding="utf-8",
    )
    (d / "raw.html").write_text(
        "<html><body>"
        '<header class="site-head"><a href="/shop">Shop</a></header>'
        '<section class="hero"><h1>Welcome</h1></section>'
        "</body></html>",
        encoding="utf-8",
    )
    (d / "css.json").write_text(
        json.dumps(
            {
                "stylesheets": [
                    {
                        "url": "inline-0",
                        "content": ".hero { color: red } .hero:hover { color: blue } "
                        ".site-head { background: black }",
                    }
                ],
                "variables": [],
            }
        ),
        encoding="utf-8",
    )
    return d


def test_get_section_data_carries_real_css_rules(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "example.com-1-abc123"
    _make_source(tmp_path, sid)

    from mcp_server.tools import extraction

    plan = extraction.get_section_plan(sid)
    assert plan["ok"], plan
    names = [s["name"] for s in plan["sections"]]
    assert names

    # Every section's data exposes a css_rules field.
    for name in names:
        data = extraction.get_section_data(sid, name)
        assert data["ok"], data
        assert "css_rules" in data

    # The hero section's real :hover CSS must reach the sub-agent.
    all_css = " ".join(extraction.get_section_data(sid, n).get("css_rules", "") for n in names)
    assert ".hero" in all_css
    assert ":hover" in all_css
    assert "background: black" in all_css  # header's real CSS too
