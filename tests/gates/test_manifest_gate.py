"""core.gates.manifest_gate — replay the checklist on the clone and reconcile it.

The anti-Goodhart requirement (learned from the pagerie full-page-SSIM failure):
the metric must RANK candidates correctly — identical beats shifted, shifted
beats blank.
"""
from PIL import Image

from core.gates.fidelity import ssim_images


def _png(tmp_path, name, color, size=(200, 120)):
    p = tmp_path / name
    Image.new("RGB", size, color).save(p)
    return str(p)


def test_ssim_images_ranks_identical_above_different(tmp_path):
    a = _png(tmp_path, "a.png", (200, 30, 30))
    same = _png(tmp_path, "same.png", (200, 30, 30))
    diff = _png(tmp_path, "diff.png", (30, 30, 200))
    assert ssim_images(a, same) > ssim_images(a, diff)
    assert ssim_images(a, same) > 0.95
