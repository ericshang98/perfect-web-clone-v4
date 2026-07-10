"""Wrapper tests for the v4 pipeline MCP tools (mcp_server.tools.pipeline).

The heavy lifting lives in the deterministic ``core`` modules (separately
tested). These guard the thin proxies: every tool returns a JSON-serializable
dict with an ``ok`` key, and each proxies the matching core module.

THE IRON RULE: no LLM here. Pure Python proxies over deterministic core.
"""

import json
import os

import pytest
from PIL import Image

from mcp_server.tools import pipeline


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_json(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


_DOM = {
    "tag": "div",
    "id": "template--123__main",
    "classes": ["shopify-section"],
    "rect": {"x": 0, "y": 0, "width": 1440, "height": 100},
    "styles": {"display": "flex", "color": "#111111"},
    "children": [],
}


# --------------------------------------------------------------------------- #
# build_ir
# --------------------------------------------------------------------------- #
def test_build_ir_returns_ok_dict_and_normalizes():
    r = pipeline.build_ir(_DOM)
    assert isinstance(r, dict) and r["ok"] is True
    assert _is_json(r)
    blob = json.dumps(r["document"])
    assert "shopify-section" not in blob and "template--" not in blob
    assert r["document"]["root"]["layout"]["mode"] == "flex"


def test_build_ir_bad_input_returns_not_ok():
    r = pipeline.build_ir("not-a-dom")
    assert r["ok"] is False and "error" in r


# --------------------------------------------------------------------------- #
# run_recognizers
# --------------------------------------------------------------------------- #
def test_run_recognizers_returns_ok_and_reports():
    doc = pipeline.build_ir(_DOM)["document"]
    r = pipeline.run_recognizers(doc)
    assert r["ok"] is True
    assert _is_json(r)
    assert isinstance(r["reports"], list)
    assert "document" in r


def test_run_recognizers_bad_input_returns_not_ok():
    r = pipeline.run_recognizers({"not": "a-doc"})
    assert r["ok"] is False and "error" in r


# --------------------------------------------------------------------------- #
# generate_code
# --------------------------------------------------------------------------- #
def test_generate_code_emits_clean_jsx_and_theme():
    doc = pipeline.build_ir(_DOM)["document"]
    r = pipeline.generate_code(doc)
    assert r["ok"] is True
    assert _is_json(r)
    assert "shopify" not in r["jsx"].lower()
    assert "<style" not in r["jsx"]
    assert "module.exports" in r["tailwind_theme"] or "theme" in r["tailwind_theme"]


def test_generate_code_bad_input_returns_not_ok():
    r = pipeline.generate_code({"not": "a-doc"})
    assert r["ok"] is False and "error" in r


# --------------------------------------------------------------------------- #
# check_fingerprints  (proxies core.gates.fingerprint.scan_tree)
# --------------------------------------------------------------------------- #
def test_check_fingerprints_detects(tmp_path):
    (tmp_path / "a.css").write_text(".shopify-section{} /* template--9__main */")
    (tmp_path / "i.html").write_text('<link href="original.css"> data-shopify-x')
    r = pipeline.check_fingerprints(str(tmp_path))
    assert r["ok"] is False and r["total"] >= 3
    assert _is_json(r)


def test_check_fingerprints_clean(tmp_path):
    (tmp_path / "a.css").write_text(".hero{color:#111}")
    assert pipeline.check_fingerprints(str(tmp_path))["ok"] is True


# --------------------------------------------------------------------------- #
# check_weight  (proxies core.gates.weight.measure_dist)
# --------------------------------------------------------------------------- #
def test_check_weight_tiny_passes(tmp_path):
    (tmp_path / "index.html").write_text("<h1>hi</h1>")
    r = pipeline.check_weight(str(tmp_path))
    assert r["ok"] is True
    assert _is_json(r)
    assert "total_kb" in r and "budget_kb" in r


def test_check_weight_over_budget_fails(tmp_path):
    # Incompressible payload so gzip can't shrink it below the budget.
    (tmp_path / "big.js").write_bytes(os.urandom(300 * 1024))
    r = pipeline.check_weight(str(tmp_path), budget_kb=120)
    assert r["ok"] is False


# --------------------------------------------------------------------------- #
# score_fidelity  (proxies the fidelity gate)
# --------------------------------------------------------------------------- #
def _write_png(path, color, size=(64, 64)):
    Image.new("RGB", size, color).save(path)


def test_score_fidelity_identical(tmp_path):
    ref = tmp_path / "ref.png"
    cand = tmp_path / "cand.png"
    _write_png(ref, (255, 255, 255))
    _write_png(cand, (255, 255, 255))
    r = pipeline.score_fidelity(str(ref), str(cand))
    assert r["ok"] is True
    assert _is_json(r)
    assert r["score"] >= 0.97
    assert isinstance(r["worst_regions"], list)


def test_score_fidelity_divergent(tmp_path):
    ref = tmp_path / "ref.png"
    cand = tmp_path / "cand.png"
    img = Image.new("RGB", (64, 64), (255, 255, 255))
    for y in range(20, 44):
        for x in range(64):
            img.putpixel((x, y), (0, 0, 0))
    img.save(ref)
    _write_png(cand, (255, 255, 255))
    r = pipeline.score_fidelity(str(ref), str(cand), threshold=0.97)
    assert r["ok"] is False
    assert r["score"] < 0.97
    # worst band localized
    assert r["worst_regions"][0]["ssim"] <= r["worst_regions"][-1]["ssim"]


# --------------------------------------------------------------------------- #
# score_fidelity_by_section  (height-independent, per-section R4)
# --------------------------------------------------------------------------- #
def _striped_page(path, w, sec_h, n):
    """A textured n-section page so SSIM is meaningful; each section distinct."""
    from PIL import ImageDraw
    page = Image.new("RGB", (w, sec_h * n), (255, 255, 255))
    d = ImageDraw.Draw(page)
    for i in range(n):
        y0 = i * sec_h
        for x in range(0, w, 8):
            d.line([(x, y0), (x, y0 + sec_h)], fill=(40, 80 + i * 50, 160), width=3)
    page.save(path)
    return page.height


def _secs(ref_h, cand_h, n=3):
    return [
        {"name": f"s{i}",
         "ref_bounds": {"x": 0, "y": i * ref_h, "width": 400, "height": ref_h},
         "cand_bounds": {"x": 0, "y": i * cand_h, "width": 400, "height": cand_h}}
        for i in range(n)
    ]


def test_score_fidelity_by_section_height_independent(tmp_path):
    ref = tmp_path / "ref.png"
    cand = tmp_path / "cand.png"
    rh = _striped_page(ref, 400, 300, 3)
    ch = _striped_page(cand, 400, 600, 3)  # clone is 2x taller, same content
    r = pipeline.score_fidelity_by_section(str(ref), str(cand), _secs(300, 600), rh, ch)
    assert r["ok"] is True
    assert _is_json(r)
    assert r["score"] >= 0.95
    assert r["graded"] == 3


def test_score_fidelity_by_section_bad_input(tmp_path):
    r = pipeline.score_fidelity_by_section(123, "x", [], 0, 0)
    assert r["ok"] is False
    assert "error" in r


# --------------------------------------------------------------------------- #
# compare_to_baseline  (R5 — new output strictly better than the baseline)
# --------------------------------------------------------------------------- #
def test_compare_to_baseline_new_better(tmp_path):
    ref = tmp_path / "ref.png"
    new = tmp_path / "new.png"
    base = tmp_path / "base.png"
    _write_png(ref, (255, 255, 255))
    _write_png(new, (255, 255, 255))  # identical to ref -> high score
    _write_png(base, (0, 0, 0))  # opposite -> low score
    r = pipeline.compare_to_baseline(str(ref), str(new), str(base))
    assert r["ok"] is True
    assert _is_json(r)
    assert r["new_score"] > r["baseline_score"]


def test_compare_to_baseline_new_not_better(tmp_path):
    ref = tmp_path / "ref.png"
    new = tmp_path / "new.png"
    base = tmp_path / "base.png"
    _write_png(ref, (255, 255, 255))
    _write_png(new, (0, 0, 0))  # opposite -> low score
    _write_png(base, (255, 255, 255))  # identical to ref -> high score
    r = pipeline.compare_to_baseline(str(ref), str(new), str(base))
    assert r["ok"] is False


# --------------------------------------------------------------------------- #
# server registration + naming
# --------------------------------------------------------------------------- #
def test_server_registers_pipeline_tools_and_is_pwc4():
    # The server module needs the third-party ``mcp`` (FastMCP) package; skip
    # cleanly where it is not installed so the suite stays green there.
    pytest.importorskip("mcp")
    from mcp_server import server

    assert server.mcp.name == "pwc4"
    for name in (
        "build_ir",
        "run_recognizers",
        "generate_code",
        "check_fingerprints",
        "check_weight",
        "score_fidelity",
        "score_fidelity_by_section",
        "compare_to_baseline",
    ):
        assert name in server.REGISTERED_TOOLS, name
