"""fidelity_gate (R4) — SSIM scoring + region localization.

Pure, deterministic. Wraps the SSIM primitives in ``core.visual_diff`` to give
the self-heal loop two operations:

* ``score(ref, cand)`` — a single 0..1 structural-similarity score (1.0 =
  identical) used as the pass/fail signal against a threshold τ.
* ``worst_regions(ref, cand, rows)`` — per-band local SSIM, sorted worst-first,
  each entry carrying the band's y-range so the offending region can be mapped
  back to an IR node via ``sourceBBox``.

No I/O beyond reading the two image files; no network, no randomness.
"""
from __future__ import annotations

from core.visual_diff import _SSIM_SIZE, ssim_region_scores, ssim_score

# Default acceptance threshold for the fidelity gate (per architecture §2, R4).
DEFAULT_THRESHOLD = 0.97


def score(ref_png: str, cand_png: str) -> float:
    """Structural-similarity score between the reference and candidate rasters.

    Returns 1.0 for identical images, lower for divergent ones (clamped 0..1).
    """
    return ssim_score(ref_png, cand_png)


def passes(ref_png: str, cand_png: str, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """True iff ``score(ref, cand) >= threshold``."""
    return score(ref_png, cand_png) >= threshold


def worst_regions(
    ref_png: str, cand_png: str, rows: int = 12
) -> list[dict]:
    """Localize the worst-matching horizontal bands.

    Splits both rasters into ``rows`` equal horizontal bands, computes each
    band's local SSIM, and returns one dict per band sorted **worst-first**
    (lowest SSIM). Each dict carries:

    * ``index`` — the band's position (0 = topmost) on the shared canvas.
    * ``ssim``  — the band's local structural similarity (1.0 = identical).
    * ``y0`` / ``y1`` — the band's y-range on the SSIM canvas (height
      ``_SSIM_SIZE[1]``); callers map this back to source geometry / IR nodes.

    ``rows`` must be >= 1.
    """
    band_scores = ssim_region_scores(ref_png, cand_png, rows=rows)

    canvas_h = _SSIM_SIZE[1]
    band_h = max(1, canvas_h // rows)

    regions: list[dict] = []
    for i, s in enumerate(band_scores):
        y0 = i * band_h
        y1 = y0 + band_h
        regions.append({"index": i, "ssim": s, "y0": y0, "y1": y1})

    # Worst (lowest SSIM) first; tie-break by band index for determinism.
    regions.sort(key=lambda r: (r["ssim"], r["index"]))
    return regions
