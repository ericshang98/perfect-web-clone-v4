"""Wrapper test for the verify_links MCP gate.

The pure aggregation lives in core.link_verifier (separately tested). This guards
the thin async tool: load persisted sections, read each component from the
sandbox, return the orchestrator verdict.
"""

import asyncio
import json


def _make_sections(root, sid, sections, source_url):
    d = root / sid
    d.mkdir()
    (d / "sections_full.json").write_text(json.dumps({"sections": sections}), encoding="utf-8")
    (d / "sections.json").write_text(json.dumps({"source_url": source_url}), encoding="utf-8")


def test_verify_links_passes_when_components_keep_real_links(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "x.com-1-aaa"
    _make_sections(
        tmp_path,
        sid,
        [{"name": "nav", "component_path": "src/components/sections/nav/Nav.jsx",
          "links": [{"url": "https://x.com/shop"}]}],
        "https://x.com/p",
    )
    from mcp_server.tools import verify

    class FakeSB:
        async def read_file(self, path):
            return '<a href="/shop">Shop</a>'

    monkeypatch.setattr(verify, "get_sandbox", lambda: FakeSB())
    r = asyncio.run(verify.verify_links(sid))
    assert r["ok"], r
    assert r["passed"] == ["nav"]


def test_verify_links_fails_and_names_the_offending_section(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "x.com-2-bbb"
    _make_sections(
        tmp_path,
        sid,
        [{"name": "footer", "component_path": "src/components/sections/footer/Footer.jsx",
          "links": [{"url": "https://x.com/terms"}]}],
        "https://x.com/p",
    )
    from mcp_server.tools import verify

    class FakeSB:
        async def read_file(self, path):
            return '<a href="#">Terms</a>'  # fabricated placeholder

    monkeypatch.setattr(verify, "get_sandbox", lambda: FakeSB())
    r = asyncio.run(verify.verify_links(sid))
    assert not r["ok"]
    assert [f["name"] for f in r["failing"]] == ["footer"]


def test_verify_links_errors_when_no_section_data(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    from mcp_server.tools import verify

    r = asyncio.run(verify.verify_links("does-not-exist"))
    assert not r["ok"]
    assert "error" in r


def _make_asset_sections(root, sid, sections):
    d = root / sid
    d.mkdir()
    (d / "sections_full.json").write_text(json.dumps({"sections": sections}), encoding="utf-8")
    (d / "sections.json").write_text(json.dumps({"source_url": "https://x.com/p"}), encoding="utf-8")


def test_verify_assets_passes_when_local_paths_used(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "x.com-3-assets-ok"
    _make_asset_sections(
        tmp_path, sid,
        [{"name": "hero", "component_path": "src/components/sections/hero/Hero.jsx",
          "images": [{"url": "https://cdn/a.png", "local_url": "/assets/images/a.png", "localized": True}]}],
    )
    from mcp_server.tools import verify

    class FakeSB:
        async def read_file(self, path):
            return '<img src="/assets/images/a.png">'

    monkeypatch.setattr(verify, "get_sandbox", lambda: FakeSB())
    r = asyncio.run(verify.verify_assets(sid))
    assert r["ok"], r
    assert r["passed"] == ["hero"]


def test_verify_assets_flags_hotlinking_section(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "x.com-4-assets-bad"
    _make_asset_sections(
        tmp_path, sid,
        [{"name": "hero", "component_path": "src/components/sections/hero/Hero.jsx",
          "images": [{"url": "https://cdn/a.png", "local_url": "/assets/images/a.png", "localized": True}]}],
    )
    from mcp_server.tools import verify

    class FakeSB:
        async def read_file(self, path):
            return '<img src="https://cdn/a.png">'  # still hotlinking

    monkeypatch.setattr(verify, "get_sandbox", lambda: FakeSB())
    r = asyncio.run(verify.verify_assets(sid))
    assert not r["ok"]
    assert r["failing"][0]["name"] == "hero"
    assert "https://cdn/a.png" in r["failing"][0]["hotlinked"]
