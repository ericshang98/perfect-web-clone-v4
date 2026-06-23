"""Pure, deterministic image comparison for visual proofreading ("校对").

Compares two images (original vs. clone) and produces normalized difference
scores, including per-vertical-band scores to localize *where* a cloned page
diverges from the original. No I/O beyond reading the two image files; no
network, no randomness — fully deterministic.
"""
from __future__ import annotations

from PIL import Image

# Common canvas the two images are resized onto before comparison. Small enough
# to be fast and to smooth over sub-pixel anti-aliasing noise, large enough to
# preserve coarse layout structure.
_COMPARE_SIZE = (64, 64)


def _mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    """Mean absolute per-channel pixel difference of two equal-size RGB images,
    normalized to 0.0..1.0 (0 = identical, 1 = maximally opposite)."""
    # Raw RGB bytes: one unsigned byte per channel, row-major. Comparing bytes
    # avoids deprecated per-pixel accessors and is fully deterministic.
    ba = a.tobytes()
    bb = b.tobytes()
    if not ba:
        return 0.0
    total = sum(abs(x - y) for x, y in zip(ba, bb))
    return (total / len(ba)) / 255.0


def diff_score(img_a_path: str, img_b_path: str) -> float:
    """Normalized 0.0..1.0 difference between two images.

    Both images are opened, converted to RGB and resized to a common small
    canvas, then compared by mean absolute pixel difference. Identical images
    score ~0.0; solid-black vs. solid-white scores ~1.0.
    """
    with Image.open(img_a_path) as ia, Image.open(img_b_path) as ib:
        a = ia.convert("RGB").resize(_COMPARE_SIZE)
        b = ib.convert("RGB").resize(_COMPARE_SIZE)
        return _mean_abs_diff(a, b)


def region_scores(img_a_path: str, img_b_path: str, rows: int = 12) -> list[float]:
    """Per-band normalized difference scores.

    Both images are resized to the SAME width and height, then split into
    ``rows`` equal horizontal bands. Returns one ``diff_score``-style value per
    band (top to bottom), localizing which vertical region differs most.
    """
    if rows < 1:
        raise ValueError("rows must be >= 1")

    # Use a height divisible by rows so bands are exactly equal.
    width = _COMPARE_SIZE[0]
    band_h = max(1, _COMPARE_SIZE[1] // rows)
    height = band_h * rows

    with Image.open(img_a_path) as ia, Image.open(img_b_path) as ib:
        a = ia.convert("RGB").resize((width, height))
        b = ib.convert("RGB").resize((width, height))

        scores: list[float] = []
        for i in range(rows):
            top = i * band_h
            bottom = top + band_h
            band_a = a.crop((0, top, width, bottom))
            band_b = b.crop((0, top, width, bottom))
            scores.append(_mean_abs_diff(band_a, band_b))
        return scores
