# tests/test_manifest_report.py
"""core.manifest_report — the printed face of '100%': one row per checklist item."""
from core.manifest_report import render_report


ROWS = [
    {"id": "s_1440_scroll_0", "status": "pass", "ssim": 0.991,
     "sbs": "out/s_1440_scroll_0_sbs.png"},
    {"id": "s_carousel", "status": "fail", "ssim": 0.71, "sbs": "out/s_carousel_sbs.png"},
    {"id": "s_webgl", "status": "waived", "reason": "residual channel — reported, not verified"},
]
SUMMARY = {"total": 3, "pass": 1, "fail": 1, "waived": 1, "pending": 0, "ok": False}


def test_report_contains_every_item_and_summary(tmp_path):
    out = tmp_path / "report.html"
    render_report({"url": "https://x", "states": []}, ROWS, SUMMARY, out)
    html = out.read_text(encoding="utf-8")
    for r in ROWS:
        assert r["id"] in html
    assert "1 / 3" in html          # pass count over total
    assert "waived" in html and "residual" in html
    assert "0.991" in html and "0.71" in html
    assert 'src="out/s_carousel_sbs.png"' in html


def test_report_verdict_reflects_ok_flag(tmp_path):
    out = tmp_path / "r.html"
    render_report({"url": "u", "states": []}, ROWS,
                  {**SUMMARY, "fail": 0, "pending": 0, "ok": True}, out)
    assert "CHECKLIST GREEN" in out.read_text(encoding="utf-8")


def test_report_escapes_untrusted_row_fields(tmp_path):
    out = tmp_path / "esc.html"
    rows = [{"id": "s_<b>", "status": "<script>x</script>", "reason": "a & b"}]
    render_report({"url": "u"}, rows,
                  {"total": 1, "pass": 0, "fail": 0, "waived": 0, "pending": 1,
                   "ok": False}, out)
    html = out.read_text(encoding="utf-8")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html and "s_&lt;b&gt;" in html
