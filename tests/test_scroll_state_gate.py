"""Unit tests for the multi-state scroll-raster capture gate.

These rasters (``screenshots/scroll_{i:02d}.png``) are the preferred source for
the state-checklist reference images (``core.refs.materialize_refs``), so
extraction must capture them for EVERY site — not only runtime-visual ones.
This guards the decision (``ExtractorService._should_capture_scroll_states``)
without driving a browser.
"""
import os
from pathlib import Path

import pytest

from core.extractor.service import ExtractorService


def test_static_tall_site_still_captures_scroll_states():
    """A static/clone-well page must still get multi-state rasters (checklist refs).

    Old gate gated on ``not cls['can_clone_well']`` — a static site was skipped.
    The refs pipeline now needs these rasters for every site.
    """
    svc = ExtractorService()
    # full_page_screenshot on, page ~15x the viewport (clearly tall).
    assert svc._should_capture_scroll_states(
        full_page_screenshot=True, page_height=13275, viewport_height=900
    ) is True


def test_short_page_is_not_captured():
    # A page barely taller than one viewport has nothing to reveal across scroll.
    assert ExtractorService()._should_capture_scroll_states(
        full_page_screenshot=True, page_height=1000, viewport_height=900
    ) is False


def test_no_full_page_screenshot_means_no_scroll_states():
    # Scroll states are viewport crops of the full-page scroll; without the
    # full-page pass we don't have the reconciled height to scroll against.
    assert ExtractorService()._should_capture_scroll_states(
        full_page_screenshot=False, page_height=13275, viewport_height=900
    ) is False


# --------------------------------------------------------------------------- #
# live-browser extraction (chromium, file:// fixture — no network)
# --------------------------------------------------------------------------- #
live = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="chromium extraction; set RUN_LIVE=1")

# A plainly-static page (no canvas / WebGL / scroll libs → classify_site → "static"),
# tall enough (5 x 1200px = 6000px >> 2 x viewport) for several scroll positions.
_STATIC_TALL = """<!doctype html><html><head><meta charset="utf-8">
<title>Static Tall Fixture</title><style>
  body{margin:0;font-family:sans-serif}
  section{height:1200px;display:flex;align-items:center;justify-content:center;font-size:64px}
  .a{background:#fee}.b{background:#efe}.c{background:#eef}.d{background:#ffe}.e{background:#fef}
</style></head><body>
  <section class="a">ONE</section>
  <section class="b">TWO</section>
  <section class="c">THREE</section>
  <section class="d">FOUR</section>
  <section class="e">FIVE</section>
</body></html>"""


@live
def test_static_fixture_extraction_writes_scroll_rasters(tmp_path):
    from core.extractor.api import extract_page

    page = tmp_path / "tall.html"
    page.write_text(_STATIC_TALL, encoding="utf-8")

    out = extract_page(f"file://{page}", storage_root=tmp_path / "store")
    storage_dir = Path(out["summary"]["storage_dir"])

    scroll0 = storage_dir / "screenshots" / "scroll_00.png"
    assert scroll0.exists(), f"expected multi-state raster at {scroll0} for a static site"
