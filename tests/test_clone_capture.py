"""core.clone_capture — capture the LIVE CLONE's full-page raster + per-section
bounds so score_fidelity_by_section can grade a real build (the last wire of the
self-heal loop).

match_sections is pure (always runs); capture_clone drives chromium against a
local file:// page and follows the repo's RUN_LIVE=1 convention.
"""
import os

import pytest

from core.clone_capture import match_sections


REF_SECTIONS = [
    {"name": "hero", "bounds": {"x": 0, "y": 0, "width": 1440, "height": 600}},
    {"name": "footer", "bounds": {"x": 0, "y": 600, "width": 1440, "height": 800}},
]


def test_match_sections_pairs_ref_and_cand_by_name():
    cand = {
        "hero": {"x": 0, "y": 0, "width": 1440, "height": 620},
        "footer": {"x": 0, "y": 620, "width": 1440, "height": 810},
    }
    out = match_sections(REF_SECTIONS, cand)
    assert [s["name"] for s in out["sections"]] == ["hero", "footer"]
    hero = out["sections"][0]
    assert hero["ref_bounds"] == {"x": 0, "y": 0, "width": 1440, "height": 600}
    assert hero["cand_bounds"] == {"x": 0, "y": 0, "width": 1440, "height": 620}
    assert out["unmatched_ref"] == []
    assert out["unmatched_cand"] == []


def test_ref_section_not_measured_on_clone_is_reported_not_dropped_silently():
    out = match_sections(REF_SECTIONS, {"hero": {"x": 0, "y": 0, "width": 1440, "height": 600}})
    assert [s["name"] for s in out["sections"]] == ["hero"]
    assert out["unmatched_ref"] == ["footer"]


def test_clone_anchor_unknown_to_plan_is_reported():
    cand = {
        "hero": {"x": 0, "y": 0, "width": 1440, "height": 600},
        "footer": {"x": 0, "y": 600, "width": 1440, "height": 800},
        "popup": {"x": 10, "y": 10, "width": 300, "height": 200},
    }
    out = match_sections(REF_SECTIONS, cand)
    assert out["unmatched_cand"] == ["popup"]


def test_ref_section_with_empty_bounds_is_ungradeable():
    ref = [{"name": "hero", "bounds": {}}]
    out = match_sections(ref, {"hero": {"x": 0, "y": 0, "width": 10, "height": 10}})
    assert out["sections"] == []
    assert out["unmatched_ref"] == ["hero"]


# --------------------------------------------------------------------------- #
# live-browser capture (chromium, file:// page — no network)
# --------------------------------------------------------------------------- #
live = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="chromium capture; set RUN_LIVE=1")

_PAGE = """<!doctype html><html><head><style>
  body{margin:0}
  [data-pwc-section="hero"]{height:600px;background:#ace}
  [data-pwc-section="footer"]{height:800px;background:#eca}
</style></head><body>
  <div data-pwc-section="hero">HERO</div>
  <div data-pwc-section="footer">FOOTER</div>
</body></html>"""


@live
def test_capture_clone_measures_bounds_and_full_page_raster(tmp_path):
    from PIL import Image

    from core.clone_capture import capture_clone

    page = tmp_path / "page.html"
    page.write_text(_PAGE, encoding="utf-8")
    out_png = str(tmp_path / "clone.png")

    res = capture_clone(f"file://{page}", out_png)

    assert res["png"] == out_png
    assert abs(res["page_height"] - 1400) <= 2

    b = res["bounds"]
    assert set(b) == {"hero", "footer"}
    assert abs(b["hero"]["height"] - 600) <= 2
    assert abs(b["footer"]["y"] - 600) <= 2
    assert abs(b["footer"]["height"] - 800) <= 2

    img = Image.open(out_png)
    assert abs(img.height - 1400) <= 4  # device_scale_factor=1 → raster px == CSS px
