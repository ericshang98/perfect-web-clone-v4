"""MCP clone-side per-section fidelity tools (verify.capture_clone_sections /
verify.score_clone_sections).

These tools close the self-heal loop: capture the LIVE clone (full-page raster
+ data-pwc-section bounds), pair with the extraction plan's ref bounds, and
score per section — worst-first, so the agent repairs the worst section next.

The browser is faked here (capture_clone is monkeypatched); the real chromium
path is covered by tests/test_clone_capture.py.
"""
from __future__ import annotations

import asyncio
import json

from PIL import Image

from mcp_server.tools import verify


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def _mk_source(tmp_path, monkeypatch, sid="src-1", page_height=600.0,
               png_name="primary_full.png", with_summary=True):
    """Build a minimal on-disk SourceStore: plan + summary + reference raster."""
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    d = tmp_path / sid
    (d / "screenshots").mkdir(parents=True)
    ref_sections = [
        {"name": "hero", "bounds": {"x": 0, "y": 0, "width": 800, "height": 400}},
        {"name": "footer", "bounds": {"x": 0, "y": 400, "width": 800, "height": 200}},
    ]
    (d / "sections_full.json").write_text(json.dumps({"sections": ref_sections}))
    (d / "evidence").mkdir()
    (d / "evidence" / "raw_structure.json").write_text(
        json.dumps(
            {
                "page": {"width": 800, "height": page_height},
                "regions": [
                    {
                        "fingerprint": "hero",
                        "kind": "hero",
                        "critical": True,
                        "rect": {"x": 0, "y": 0, "width": 800, "height": 400},
                    },
                    {
                        "fingerprint": "footer",
                        "kind": "footer",
                        "critical": True,
                        "rect": {"x": 0, "y": 400, "width": 800, "height": 200},
                    },
                ],
            }
        )
    )
    (d / "manifest.json").write_text(
        json.dumps(
            {
                "success": True,
                "capture_integrity": {"ok": True, "status": "passed"},
            }
        )
    )
    if with_summary:
        (d / "summary.json").write_text(json.dumps(
            {"page_height": page_height, "page_width": 800}))
    img = Image.new("RGB", (800, int(page_height)), (200, 40, 40))
    img.paste(Image.new("RGB", (800, 200), (40, 40, 200)), (0, 400))
    img.save(d / "screenshots" / png_name)
    return sid, d


def _fake_capture(tmp_path, bounds, page_height=600.0, size=(800, 600)):
    """Return a stand-in for core.clone_capture.capture_clone."""
    cand = tmp_path / "cand.png"
    img = Image.new("RGB", size, (200, 40, 40))
    img.paste(Image.new("RGB", (size[0], 200), (40, 40, 200)), (0, 400))
    img.save(cand)

    calls = {}

    def fake(url, out_png, viewport=(1440, 900), settle_ms=800):
        calls["url"] = url
        calls["viewport"] = viewport
        return {"png": str(cand), "page_height": page_height, "bounds": bounds}

    return fake, calls


# --------------------------------------------------------------------------- #
# capture_clone_sections
# --------------------------------------------------------------------------- #
def test_capture_tool_passes_through_capture_result(tmp_path, monkeypatch):
    bounds = {"hero": {"x": 0, "y": 0, "width": 800, "height": 400}}
    fake, calls = _fake_capture(tmp_path, bounds)
    monkeypatch.setattr(verify.clone_capture, "capture_clone", fake)

    r = asyncio.run(verify.capture_clone_sections(url="http://localhost:5173"))
    assert r["ok"] is True
    assert r["bounds"] == bounds
    assert r["page_height"] == 600.0
    assert calls["url"] == "http://localhost:5173"


def test_capture_tool_requires_a_url_when_no_preview(monkeypatch):
    monkeypatch.setattr(verify, "get_sandbox", lambda: None)
    r = asyncio.run(verify.capture_clone_sections())
    assert r["ok"] is False
    assert "url" in r["error"].lower()


# --------------------------------------------------------------------------- #
# score_clone_sections
# --------------------------------------------------------------------------- #
def test_score_happy_path_grades_and_sorts_worst_first(tmp_path, monkeypatch):
    sid, _ = _mk_source(tmp_path, monkeypatch)
    cand_bounds = {
        "hero": {"x": 0, "y": 0, "width": 800, "height": 400},
        "footer": {"x": 0, "y": 400, "width": 800, "height": 200},
    }
    fake, _ = _fake_capture(tmp_path, cand_bounds)
    monkeypatch.setattr(verify.clone_capture, "capture_clone", fake)

    r = asyncio.run(verify.score_clone_sections(sid, url="http://x"))
    assert r["ok"] is True                      # identical rasters → perfect
    assert r["graded"] == 2 and r["ungraded"] == 0
    assert r["unmatched_ref"] == [] and r["unmatched_cand"] == []
    scores = [s["score"] for s in r["sections"] if s["graded"]]
    assert scores == sorted(scores)             # worst-first ordering
    assert r["png"] and r["ref_png"]


def test_score_reports_unmatched_and_still_grades_the_rest(tmp_path, monkeypatch):
    sid, _ = _mk_source(tmp_path, monkeypatch)
    cand_bounds = {  # footer never measured; rogue popup measured
        "hero": {"x": 0, "y": 0, "width": 800, "height": 400},
        "popup": {"x": 0, "y": 0, "width": 10, "height": 10},
    }
    fake, _ = _fake_capture(tmp_path, cand_bounds)
    monkeypatch.setattr(verify.clone_capture, "capture_clone", fake)

    r = asyncio.run(verify.score_clone_sections(sid, url="http://x"))
    assert r["graded"] == 1
    assert r["unmatched_ref"] == ["footer"]
    assert r["unmatched_cand"] == ["popup"]
    assert r["structure"]["ok"] is False


def test_score_without_plan_says_run_get_section_plan(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    r = asyncio.run(verify.score_clone_sections("nope", url="http://x"))
    assert r["ok"] is False
    assert "get_section_plan" in r["error"]


def test_score_falls_back_to_light_full_and_png_height(tmp_path, monkeypatch):
    # Older stores: light_full.png instead of primary_full.png, no summary.
    sid, _ = _mk_source(tmp_path, monkeypatch, png_name="light_full.png",
                        with_summary=False)
    cand_bounds = {
        "hero": {"x": 0, "y": 0, "width": 800, "height": 400},
        "footer": {"x": 0, "y": 400, "width": 800, "height": 200},
    }
    fake, _ = _fake_capture(tmp_path, cand_bounds)
    monkeypatch.setattr(verify.clone_capture, "capture_clone", fake)

    r = asyncio.run(verify.score_clone_sections(sid, url="http://x"))
    assert r["ok"] is True and r["graded"] == 2


def test_score_without_reference_raster_errors(tmp_path, monkeypatch):
    sid, d = _mk_source(tmp_path, monkeypatch)
    for p in (d / "screenshots").iterdir():
        p.unlink()
    r = asyncio.run(verify.score_clone_sections(sid, url="http://x"))
    assert r["ok"] is False
    assert "raster" in r["error"].lower() or "screenshot" in r["error"].lower()


def test_score_cannot_hide_hero_omitted_by_broken_reference_plan(tmp_path, monkeypatch):
    sid, d = _mk_source(tmp_path, monkeypatch, page_height=1000)
    # Recreate the historical failure: source evidence has Hero, but the broken
    # processed plan/raster starts at content and still matches the clone.
    broken_plan = [
        {"name": "content", "bounds": {"x": 0, "y": 400, "width": 800, "height": 400}},
        {"name": "footer", "bounds": {"x": 0, "y": 800, "width": 800, "height": 200}},
    ]
    (d / "sections_full.json").write_text(json.dumps({"sections": broken_plan}))
    candidate = {
        "content": {"x": 0, "y": 0, "width": 800, "height": 400},
        "footer": {"x": 0, "y": 400, "width": 800, "height": 200},
    }
    fake, _ = _fake_capture(tmp_path, candidate, page_height=600, size=(800, 600))
    monkeypatch.setattr(verify.clone_capture, "capture_clone", fake)

    result = asyncio.run(verify.score_clone_sections(sid, url="http://x"))

    assert result["ok"] is False
    assert result["structure"]["ok"] is False
    assert "hero" in result["structure"]["unplanned_critical"]


def test_new_tools_are_registered_on_the_server():
    from mcp_server.server import REGISTERED_TOOLS
    assert "capture_clone_sections" in REGISTERED_TOOLS
    assert "score_clone_sections" in REGISTERED_TOOLS
