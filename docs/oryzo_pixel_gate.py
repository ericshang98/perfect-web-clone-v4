#!/usr/bin/env python
"""Pixel-level gate: compare a rendered candidate against the reference screenshot.

Reports NUMBERS only (柱 5 — the threshold lives with the caller):
  ssim        structural similarity (0..1)
  mae         mean absolute pixel error (0..255)
  pct_exact   % of pixels whose max channel diff <= tol (near-exact match)
  worst_tiles the lowest-matching regions (for the convergence loop to target)

Usage: python oryzo_pixel_gate.py <reference.png> <candidate.png> [tol]
"""
import sys, json
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def main():
    ref = Image.open(sys.argv[1]).convert("RGB")
    cand = Image.open(sys.argv[2]).convert("RGB")
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    if cand.size != ref.size:
        cand = cand.resize(ref.size)
    R = np.asarray(ref, dtype=np.int16)
    C = np.asarray(cand, dtype=np.int16)
    diff = np.abs(R - C)
    maxc = diff.max(axis=2)
    mae = float(diff.mean())
    pct_exact = float((maxc <= tol).mean() * 100.0)
    g_ref = np.asarray(ref.convert("L"))
    g_cand = np.asarray(cand.convert("L"))
    s = float(ssim(g_ref, g_cand, data_range=255))

    # worst tiles (grid) by mean error — where to fix next
    gy, gx = 12, 8
    h, w = maxc.shape
    tiles = []
    for j in range(gy):
        for i in range(gx):
            cell = maxc[j * h // gy:(j + 1) * h // gy, i * w // gx:(i + 1) * w // gx]
            tiles.append({"row": j, "col": i,
                          "y0": j * h // gy, "y1": (j + 1) * h // gy,
                          "x0": i * w // gx, "x1": (i + 1) * w // gx,
                          "err": round(float(cell.mean()), 1)})
    worst = sorted(tiles, key=lambda t: t["err"], reverse=True)[:8]

    print(json.dumps({
        "size": list(ref.size),
        "ssim": round(s, 4),
        "mae": round(mae, 2),
        "pct_exact": round(pct_exact, 2),
        "tol": tol,
        "worst_tiles": worst,
    }, indent=2))


if __name__ == "__main__":
    main()
