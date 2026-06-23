"""TDD tests for core.visual_diff — pure, deterministic image comparison."""
import os

from PIL import Image

from core.visual_diff import diff_score, region_scores


def _save(img: Image.Image, path: str) -> str:
    img.save(path)
    return path


def test_identical_images_score_near_zero(tmp_path):
    a = _save(Image.new("RGB", (200, 300), (50, 120, 200)), str(tmp_path / "a.png"))
    b = _save(Image.new("RGB", (200, 300), (50, 120, 200)), str(tmp_path / "b.png"))
    assert diff_score(a, b) < 0.02


def test_black_vs_white_score_near_one(tmp_path):
    a = _save(Image.new("RGB", (100, 100), (0, 0, 0)), str(tmp_path / "black.png"))
    b = _save(Image.new("RGB", (100, 100), (255, 255, 255)), str(tmp_path / "white.png"))
    assert diff_score(a, b) > 0.9


def test_diff_score_in_unit_range(tmp_path):
    a = _save(Image.new("RGB", (64, 64), (10, 20, 30)), str(tmp_path / "a.png"))
    b = _save(Image.new("RGB", (64, 64), (200, 100, 60)), str(tmp_path / "b.png"))
    s = diff_score(a, b)
    assert 0.0 <= s <= 1.0


def test_diff_score_handles_different_sizes(tmp_path):
    # Identical color but different dimensions -> still ~0 after resize.
    a = _save(Image.new("RGB", (300, 900), (128, 128, 128)), str(tmp_path / "a.png"))
    b = _save(Image.new("RGB", (120, 200), (128, 128, 128)), str(tmp_path / "b.png"))
    assert diff_score(a, b) < 0.02


def test_region_scores_returns_rows_floats(tmp_path):
    a = _save(Image.new("RGB", (100, 480), (0, 0, 0)), str(tmp_path / "a.png"))
    b = _save(Image.new("RGB", (100, 480), (0, 0, 0)), str(tmp_path / "b.png"))
    scores = region_scores(a, b, rows=12)
    assert isinstance(scores, list)
    assert len(scores) == 12
    assert all(isinstance(s, float) for s in scores)


def test_region_scores_localizes_top_half_difference(tmp_path):
    # Image A: all black. Image B: top half white, bottom half black.
    black = Image.new("RGB", (120, 480), (0, 0, 0))
    a = _save(black.copy(), str(tmp_path / "a.png"))

    b_img = Image.new("RGB", (120, 480), (0, 0, 0))
    for y in range(0, 240):
        for x in range(0, 120):
            b_img.putpixel((x, y), (255, 255, 255))
    b = _save(b_img, str(tmp_path / "b.png"))

    scores = region_scores(a, b, rows=12)
    top = scores[:6]
    bottom = scores[6:]
    assert sum(top) / len(top) > sum(bottom) / len(bottom)
    assert max(top) > max(bottom)


def test_region_scores_custom_row_count(tmp_path):
    a = _save(Image.new("RGB", (100, 100), (5, 5, 5)), str(tmp_path / "a.png"))
    b = _save(Image.new("RGB", (100, 100), (5, 5, 5)), str(tmp_path / "b.png"))
    assert len(region_scores(a, b, rows=4)) == 4
    assert len(region_scores(a, b, rows=1)) == 1
