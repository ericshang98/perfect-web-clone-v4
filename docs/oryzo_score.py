#!/usr/bin/env python
"""Deterministic per-scene scorer for the oryzo clone (柱 5: no self-grading).

Outputs NUMBERS + evidence only. It does NOT decide pass/fail — the caller
(the workflow parent) holds the fixed thresholds. Metrics per scene i compare
clone frame i against the REAL oryzo.ai frame i (same scroll depth):

  ssim        grayscale structural similarity (directional; the ring≠coaster
              difference legitimately caps this, so it is reported, not gated hard)
  void_clone  fraction of the frame that is empty (dark + flat) — my actual failure
  void_real   same measure on the real frame
  void_delta  void_clone - void_real  (>0 ⇒ clone is EMPTIER than the original)
  bg_dE       CIE76 ΔE between clone & real background (frame-edge) colour
  gold_frac   fraction of gold-metal pixels in the clone (the ring must be present)

Usage: python oryzo_score.py <clone_frames_dir> <real_frames_dir>
"""
import sys, json, glob, os
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from skimage.color import rgb2lab


def load(p, size):
    im = Image.open(p).convert("RGB").resize(size)
    return np.asarray(im, dtype=np.uint8)


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def void_fraction(a, gy=9, gx=16, dark=46, flat=14):
    """Fraction of grid cells that are both dark and flat (empty background)."""
    h, w = a.shape[:2]
    L = lum(a)
    empty = 0
    tot = gy * gx
    for j in range(gy):
        for i in range(gx):
            cell = L[j * h // gy:(j + 1) * h // gy, i * w // gx:(i + 1) * w // gx]
            if cell.mean() < dark and cell.std() < flat:
                empty += 1
    return empty / tot


def edge_color(a, band=24):
    """Median colour of the frame border = background colour."""
    h, w = a.shape[:2]
    px = np.concatenate([
        a[:band].reshape(-1, 3), a[-band:].reshape(-1, 3),
        a[:, :band].reshape(-1, 3), a[:, -band:].reshape(-1, 3),
    ])
    return np.median(px, axis=0)


def deltaE(c1, c2):
    lab = rgb2lab(np.array([[c1 / 255.0, c2 / 255.0]]))
    return float(np.linalg.norm(lab[0, 0] - lab[0, 1]))


def gold_fraction(a):
    """Fraction of warm metallic-gold pixels (the ring)."""
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    gold = (r > 150) & (g > 95) & (b < 130) & (r >= g) & (g > b) & (sat > 0.28)
    return float(gold.mean())


def main():
    clone_dir, real_dir = sys.argv[1], sys.argv[2]
    clones = sorted(glob.glob(os.path.join(clone_dir, "frame_*.png")))
    reals = sorted(glob.glob(os.path.join(real_dir, "frame_*.png")))
    n = min(len(clones), len(reals))
    size = (720, 450)
    scenes = []
    for i in range(n):
        c = load(clones[i], size)
        r = load(reals[i], size)
        s = float(ssim(lum(c), lum(r), data_range=255))
        vc, vr = void_fraction(c), void_fraction(r)
        scenes.append({
            "i": i,
            "ssim": round(s, 3),
            "void_clone": round(vc, 3),
            "void_real": round(vr, 3),
            "void_delta": round(vc - vr, 3),
            "bg_dE": round(deltaE(edge_color(c), edge_color(r)), 1),
            "gold_frac": round(gold_fraction(c), 4),
        })
    # badness rank: emptier-than-original + palette drift + low ssim
    def bad(s):
        return max(0, s["void_delta"]) * 2.0 + s["bg_dE"] / 40.0 + (1 - s["ssim"]) * 0.5
    worst = sorted(scenes, key=bad, reverse=True)[:5]
    out = {
        "scenes": scenes,
        "summary": {
            "n": n,
            "mean_ssim": round(float(np.mean([s["ssim"] for s in scenes])), 3),
            "max_void_delta": round(max(s["void_delta"] for s in scenes), 3),
            "mean_void_delta": round(float(np.mean([s["void_delta"] for s in scenes])), 3),
            "max_bg_dE": round(max(s["bg_dE"] for s in scenes), 1),
            "any_ring_visible": any(s["gold_frac"] > 0.004 for s in scenes),
            "worst_scenes": [{"i": w["i"], "void_delta": w["void_delta"], "bg_dE": w["bg_dE"], "ssim": w["ssim"]} for w in worst],
        },
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
