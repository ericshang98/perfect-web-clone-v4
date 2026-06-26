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


# Masked area above this fraction of the page is flagged loudly — you must never
# be able to mask away a real fidelity miss and silently "pass".
MASK_AREA_CAP = 0.15

# Band resolution for masked scoring (fine enough to follow a mask y-range).
_MASK_ROWS = 32


def _band_masked(b0: float, b1: float, mask_regions: list[dict]) -> bool:
    """True if band ``[b0,b1)`` (normalized) overlaps any mask region."""
    for m in mask_regions:
        if not (b1 <= m.get("y0", 0.0) or b0 >= m.get("y1", 0.0)):
            return True
    return False


def masked_fraction(mask_regions: list[dict] | None, rows: int = _MASK_ROWS) -> float:
    """Fraction of the page height covered by ``mask_regions`` (band-quantized)."""
    if not mask_regions:
        return 0.0
    band_h = 1.0 / rows
    n = sum(1 for i in range(rows) if _band_masked(i * band_h, (i + 1) * band_h, mask_regions))
    return n / rows


def score(ref_png: str, cand_png: str, mask_regions: list[dict] | None = None) -> float:
    """Structural-similarity score between the reference and candidate rasters.

    Returns 1.0 for identical images, lower for divergent ones (clamped 0..1).
    ``mask_regions`` is an optional list of ``{"y0","y1"}`` normalized [0,1]
    y-ranges to EXCLUDE — e.g. a known third-party overlay (Klaviyo popup) baked
    into the reference only. When given, the score is the mean SSIM over the
    UNMASKED horizontal bands. With no mask, returns the exact global SSIM.
    """
    if not mask_regions:
        return ssim_score(ref_png, cand_png)
    bands = ssim_region_scores(ref_png, cand_png, rows=_MASK_ROWS)
    band_h = 1.0 / _MASK_ROWS
    kept = [s for i, s in enumerate(bands) if not _band_masked(i * band_h, (i + 1) * band_h, mask_regions)]
    if not kept:
        return 0.0
    return sum(kept) / len(kept)


def score_report(
    ref_png: str,
    cand_png: str,
    threshold: float = DEFAULT_THRESHOLD,
    mask_regions: list[dict] | None = None,
) -> dict:
    """Score + provenance: the masked regions and area fraction are always logged.

    ``mask_oversized`` is True when the masked area exceeds ``MASK_AREA_CAP`` — a
    loud flag so masking can never silently hide a real miss.
    """
    s = score(ref_png, cand_png, mask_regions)
    frac = masked_fraction(mask_regions)
    return {
        "score": s,
        "threshold": threshold,
        "ok": s >= threshold,
        "masked_regions": mask_regions or [],
        "masked_fraction": frac,
        "mask_oversized": frac > MASK_AREA_CAP,
    }


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
