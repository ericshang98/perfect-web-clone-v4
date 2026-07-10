"""Tests for core.scroll_capture.scroll_capture_positions — evenly-spaced scroll
offsets for multi-state raster capture of scroll-choreographed sites (whose
content reveals across scroll, so one full-page raster is mostly blank).
"""
from core.scroll_capture import scroll_capture_positions


def test_five_positions_span_full_scroll():
    pos = scroll_capture_positions(13275, 900, n=5)
    assert len(pos) == 5
    assert pos[0] == 0
    assert pos[-1] == 13275 - 900           # last position bottoms out the page
    assert pos == sorted(pos)               # monotonic
    assert len(set(pos)) == 5               # distinct


def test_short_page_yields_single_top_position():
    assert scroll_capture_positions(800, 900, n=5) == [0]


def test_n_one_is_top_only():
    assert scroll_capture_positions(13275, 900, n=1) == [0]


def test_positions_are_ints_and_in_range():
    pos = scroll_capture_positions(5000, 1000, n=4)
    assert all(isinstance(p, int) for p in pos)
    assert all(0 <= p <= 4000 for p in pos)
