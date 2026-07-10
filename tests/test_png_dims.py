"""Tests for core.png_dims — read PNG pixel dimensions from a base64 string and
normalize the height to CSS pixels by the known CSS width (to undo devicePixelRatio
upscaling). Used to reconcile page_height with the ground-truth full-page raster.
"""
import base64
import io

from PIL import Image

from core.png_dims import png_css_height_b64, png_dims_b64


def _png_b64(w, h):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (1, 2, 3)).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def test_reads_dimensions():
    assert png_dims_b64(_png_b64(1440, 13275)) == (1440, 13275)


def test_css_height_when_dpr_is_1():
    assert png_css_height_b64(_png_b64(1440, 13275), 1440) == 13275


def test_css_height_normalizes_2x_dpr():
    # a 2x (retina) screenshot is 2880px wide for a 1440 CSS-px page
    assert png_css_height_b64(_png_b64(2880, 1800), 1440) == 900


def test_with_data_uri_prefix():
    uri = "data:image/png;base64," + _png_b64(800, 600)
    assert png_dims_b64(uri) == (800, 600)


def test_invalid_returns_none():
    assert png_dims_b64("not-a-png") is None
    assert png_css_height_b64("not-a-png", 1440) == 0
