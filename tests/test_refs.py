"""Tests for core.refs — materialize reference rasters.

TDD: these tests are written BEFORE the implementation. Run them first to
confirm they all fail with ImportError / NotImplementedError, then implement.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from core.manifest import baseline_states, state_ref_relpath
from core.refs import materialize_refs
from core.scroll_capture import scroll_capture_positions


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

PAGE_HEIGHT = 4000
VW, VH = 1440, 900
BP = 1440


def _solid(w: int, h: int, color: tuple) -> Image.Image:
    img = Image.new("RGB", (w, h), color)
    return img


def _banded_full(w: int, h: int, positions: list[int]) -> Image.Image:
    """Full-page raster with a distinct colour for every scroll band."""
    img = Image.new("RGB", (w, h), (128, 128, 128))
    for i, y in enumerate(positions):
        band_color = (i * 40 + 10, i * 20 + 50, 255 - i * 30)
        # Fill a strip from y to y+VH (or to h)
        for row in range(y, min(y + VH, h)):
            for col in range(w):
                img.putpixel((col, row), band_color)
    return img


def _make_store(tmp_path: Path) -> Path:
    """Return a source dir with screenshots/ sub-dir."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "screenshots").mkdir()
    return src


# ---------------------------------------------------------------------------
# 1. Naming authority
# ---------------------------------------------------------------------------

def test_state_ref_relpath_format():
    assert state_ref_relpath(1440, 0) == "refs/1440/s_1440_scroll_0.png"
    assert state_ref_relpath(375, 1234) == "refs/375/s_375_scroll_1234.png"


def test_state_ref_relpath_matches_baseline_states():
    """state_ref_relpath must produce the same path that baseline_states puts in
    expect.ref — the two naming authorities must never drift."""
    states = baseline_states(page_height=PAGE_HEIGHT, viewport=(VW, VH), breakpoint=BP)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)
    for state, y in zip(states, positions):
        expect_ref = state["expect"]["ref"]
        assert state_ref_relpath(BP, y) == expect_ref, (
            f"drift: state_ref_relpath({BP!r}, {y!r}) = {state_ref_relpath(BP, y)!r} "
            f"but baseline_states produced {expect_ref!r}"
        )


# ---------------------------------------------------------------------------
# 2. full-page crop path
# ---------------------------------------------------------------------------

def test_fullpage_crop_writes_refs(tmp_path):
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    # Build a banded full-page raster (1440 wide, same DPR as CSS px)
    img = _banded_full(VW, PAGE_HEIGHT, positions)
    img.save(src / "screenshots" / "primary_full.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)

    # All positions should be written (none existed yet)
    assert set(result["written"]) == {state_ref_relpath(BP, y) for y in positions}
    assert result["skipped"] == []
    assert result["missing"] == []
    assert result["source"] in ("fullpage_crop", "mixed")

    # Verify each ref matches the expected band colour and exact size
    for i, y in enumerate(positions):
        ref_path = src / state_ref_relpath(BP, y)
        assert ref_path.is_file(), f"missing ref for y={y}"
        with Image.open(ref_path) as ref:
            assert ref.size == (VW, VH), f"wrong size at y={y}: {ref.size}"
            # The band colour should dominate — sample a few pixels
            band_color = (i * 40 + 10, i * 20 + 50, 255 - i * 30)
            px = ref.getpixel((VW // 2, VH // 2))
            assert px == band_color, f"wrong colour at y={y}: {px!r} != {band_color!r}"


def test_breakpoint_scoped_source_bundle_is_used_instead_of_primary_desktop_raster(tmp_path):
    """Mobile refs must crop mobile evidence, never scale desktop primary_full."""
    src = _make_store(tmp_path)
    mobile_width, mobile_height, mobile_page_height = 390, 844, 2800
    desktop = _solid(VW, PAGE_HEIGHT, (255, 0, 0))
    desktop.save(src / "screenshots" / "primary_full.png")
    mobile_dir = src / "screenshots" / "breakpoints" / str(mobile_width)
    mobile_dir.mkdir(parents=True)
    _solid(mobile_width, mobile_page_height, (0, 0, 255)).save(mobile_dir / "full.png")

    result = materialize_refs(
        src,
        mobile_page_height,
        (mobile_width, mobile_height),
        mobile_width,
        screenshots_dir=mobile_dir,
    )

    assert result["missing"] == []
    with Image.open(src / state_ref_relpath(mobile_width, 0)) as ref:
        assert ref.size == (mobile_width, mobile_height)
        assert ref.getpixel((10, 10)) == (0, 0, 255)


# ---------------------------------------------------------------------------
# 3. Bottom clamp (last scroll position crop stays (VW, VH), no overflow)
# ---------------------------------------------------------------------------

def test_bottom_clamp(tmp_path):
    """The last scroll position must still produce a (VW, VH) ref even when
    y + VH > page_height (browser clamps scroll, so the window may shift up)."""
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)
    last_y = positions[-1]

    # Sanity: for this page last_y + VH > PAGE_HEIGHT would trigger clamping
    # (PAGE_HEIGHT=4000, VH=900, last_y=max_scroll=3100; 3100+900=4000 == PAGE_HEIGHT,
    # so in this case it's exactly at the bottom — still valid).
    img = _solid(VW, PAGE_HEIGHT, (200, 100, 50))
    img.save(src / "screenshots" / "primary_full.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert result["missing"] == []

    ref_path = src / state_ref_relpath(BP, last_y)
    with Image.open(ref_path) as ref:
        assert ref.size == (VW, VH)


def test_bottom_clamp_overflow(tmp_path):
    """Explicitly test with a page where last_y + VH > page_height."""
    # Make a short page so max_scroll < VH
    page_h = 1200  # max_scroll = 300
    src = _make_store(tmp_path)
    img = _solid(VW, page_h, (10, 20, 30))
    img.save(src / "screenshots" / "primary_full.png")

    positions = scroll_capture_positions(page_h, VH, n=5)
    result = materialize_refs(src, page_h, (VW, VH), BP)

    assert result["missing"] == []
    for y in positions:
        ref_path = src / state_ref_relpath(BP, y)
        with Image.open(ref_path) as ref:
            assert ref.size == (VW, VH)


# ---------------------------------------------------------------------------
# 4. Scroll-raster preference
# ---------------------------------------------------------------------------

def test_scroll_raster_preferred_over_fullpage(tmp_path):
    """When screenshots/scroll_{i:02d}.png exists for every position, scroll
    rasters must be used verbatim (no crop); source should include 'scroll_rasters'.

    Note: the count-guard requires the number of scroll_*.png files to equal
    len(positions) — a partial set triggers the guard and falls back to fullpage
    crop.  This test therefore writes a complete, matching set of scroll rasters.
    """
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    # Write a full-page fallback that is distinctly different
    fallback = _solid(VW, PAGE_HEIGHT, (0, 0, 0))
    fallback.save(src / "screenshots" / "primary_full.png")

    # Write a complete matching set of scroll rasters (count == len(positions))
    # scroll_00.png has a unique colour so we can confirm it was used.
    unique_color = (255, 0, 128)
    _solid(VW, VH, unique_color).save(src / "screenshots" / "scroll_00.png")
    filler_color = (200, 200, 200)
    for idx in range(1, len(positions)):
        _solid(VW, VH, filler_color).save(src / "screenshots" / f"scroll_{idx:02d}.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    # Source may be "scroll_rasters" (all from scroll shots) or "mixed" (some
    # scroll shots, rest from fullpage crop) — either signals scroll rasters were used.
    assert result["source"] in ("scroll_rasters", "mixed")
    assert "warning" not in result

    # The ref for positions[0] should use the scroll raster
    ref_path = src / state_ref_relpath(BP, positions[0])
    with Image.open(ref_path) as ref:
        px = ref.getpixel((0, 0))
        assert px == unique_color, f"expected scroll raster colour {unique_color}, got {px}"


def test_scroll_raster_resizes_if_wrong_size(tmp_path):
    """If a scroll raster has wrong size, it is resized to (VW, VH).

    A complete matching set of scroll rasters is written so the count-guard
    does not trigger.  scroll_00.png is deliberately the wrong size.
    """
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    # write scroll_00.png at wrong size, plus a full set so the count matches
    _solid(800, 600, (10, 20, 30)).save(src / "screenshots" / "scroll_00.png")
    for idx in range(1, len(positions)):
        _solid(VW, VH, (50, 50, 50)).save(src / "screenshots" / f"scroll_{idx:02d}.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert "warning" not in result
    ref_path = src / state_ref_relpath(BP, positions[0])
    with Image.open(ref_path) as ref:
        assert ref.size == (VW, VH)


# ---------------------------------------------------------------------------
# 5. Idempotency
# ---------------------------------------------------------------------------

def test_idempotent_second_call(tmp_path):
    """Second call with refs already on disk → all skipped, none written."""
    src = _make_store(tmp_path)
    img = _solid(VW, PAGE_HEIGHT, (100, 100, 100))
    img.save(src / "screenshots" / "primary_full.png")

    r1 = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert r1["written"]  # first call wrote something

    r2 = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert r2["written"] == []
    assert set(r2["skipped"]) == set(r1["written"])
    assert r2["missing"] == []


# ---------------------------------------------------------------------------
# 6. Missing everything → all missing, source "none"
# ---------------------------------------------------------------------------

def test_missing_everything(tmp_path):
    """No screenshots at all → all positions missing, source='none'."""
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert result["written"] == []
    assert result["skipped"] == []
    assert set(result["missing"]) == {state_ref_relpath(BP, y) for y in positions}
    assert result["source"] == "none"


# ---------------------------------------------------------------------------
# 7. Device-scale / HiDPI: primary_full at 2× width → crop resized back to VW×VH
# ---------------------------------------------------------------------------

def test_device_scale_2x(tmp_path):
    """primary_full.png at 2880px wide (2× DPR) is correctly cropped and
    down-scaled to (1440, 900)."""
    src = _make_store(tmp_path)
    scale = 2
    w2, h2 = VW * scale, PAGE_HEIGHT * scale

    img = _solid(w2, h2, (50, 100, 150))
    img.save(src / "screenshots" / "primary_full.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)
    assert result["missing"] == []

    for y in scroll_capture_positions(PAGE_HEIGHT, VH, n=5):
        ref_path = src / state_ref_relpath(BP, y)
        with Image.open(ref_path) as ref:
            assert ref.size == (VW, VH), f"expected ({VW},{VH}) got {ref.size} at y={y}"


# ---------------------------------------------------------------------------
# 8. Scroll-raster count guard
# ---------------------------------------------------------------------------

def test_count_mismatch_falls_back_to_fullpage_crop_with_warning(tmp_path):
    """When scroll rasters are present but their count != len(positions), the
    index mapping is unsafe.  materialize_refs must skip all scroll rasters,
    fall through to fullpage_crop for every position, and include a 'warning'
    key explaining the count mismatch."""
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    # Write a recognisable full-page fallback
    fallback_color = (77, 88, 99)
    fallback = _solid(VW, PAGE_HEIGHT, fallback_color)
    fallback.save(src / "screenshots" / "primary_full.png")

    # Write fewer scroll rasters than len(positions) — creates a count mismatch.
    # Use a uniquely different colour so we can detect if it was (wrongly) used.
    wrong_color = (255, 0, 0)
    wrong_shot = _solid(VW, VH, wrong_color)
    # Write only 3 scroll rasters when 5 positions are expected
    for idx in range(3):
        wrong_shot.save(src / "screenshots" / f"scroll_{idx:02d}.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)

    # Must contain a warning mentioning the count mismatch
    assert "warning" in result, "expected a 'warning' key when counts mismatch"
    warning = result["warning"]
    assert "3" in warning, f"warning should mention count 3: {warning!r}"
    assert str(len(positions)) in warning, (
        f"warning should mention expected count {len(positions)}: {warning!r}"
    )

    # All positions must be written (from fullpage crop, not scroll rasters)
    assert set(result["written"]) == {state_ref_relpath(BP, y) for y in positions}
    assert result["missing"] == []

    # Verify none of the refs used the (wrong) scroll-raster colour
    for y in positions:
        ref_path = src / state_ref_relpath(BP, y)
        with Image.open(ref_path) as ref:
            px = ref.getpixel((VW // 2, VH // 2))
            assert px == fallback_color, (
                f"ref at y={y} used wrong colour {px!r}; expected fullpage crop colour"
            )


def test_count_match_uses_scroll_rasters_no_warning(tmp_path):
    """When scroll raster count matches len(positions), the index mapping is
    safe: scroll rasters are used and no 'warning' key is present."""
    src = _make_store(tmp_path)
    positions = scroll_capture_positions(PAGE_HEIGHT, VH, n=5)

    # Full-page fallback with a distinct colour (should NOT be used)
    fallback = _solid(VW, PAGE_HEIGHT, (0, 0, 0))
    fallback.save(src / "screenshots" / "primary_full.png")

    # Write exactly len(positions) scroll rasters, each with a unique colour
    scroll_colors = [(i * 40 + 10, i * 20 + 50, 255 - i * 30) for i in range(len(positions))]
    for idx, color in enumerate(scroll_colors):
        shot = _solid(VW, VH, color)
        shot.save(src / "screenshots" / f"scroll_{idx:02d}.png")

    result = materialize_refs(src, PAGE_HEIGHT, (VW, VH), BP)

    # No warning should be present
    assert "warning" not in result, f"unexpected warning: {result.get('warning')!r}"

    # Source must indicate scroll rasters were used
    assert result["source"] in ("scroll_rasters", "mixed")

    # Each ref should carry the colour from the matching scroll raster
    for i, y in enumerate(positions):
        ref_path = src / state_ref_relpath(BP, y)
        assert ref_path.is_file(), f"ref missing for y={y}"
        with Image.open(ref_path) as ref:
            px = ref.getpixel((VW // 2, VH // 2))
            assert px == scroll_colors[i], (
                f"ref at position {i} (y={y}) has colour {px!r}; "
                f"expected scroll raster colour {scroll_colors[i]!r}"
            )
