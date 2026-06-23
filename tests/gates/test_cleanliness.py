from core.gates.cleanliness import check


def test_clean_utility_components_pass(tmp_path):
    (tmp_path / "Hero.jsx").write_text(
        'export default function Hero(){return <div className="flex gap-4 bg-surface">hi</div>}'
    )
    r = check(str(tmp_path))
    assert r["ok"] is True
    assert r["violations"] == []


def test_style_tag_fails(tmp_path):
    (tmp_path / "Bad.jsx").write_text(
        "export default function Bad(){return <div><style>.x{color:red}</style></div>}"
    )
    r = check(str(tmp_path))
    assert r["ok"] is False
    assert len(r["violations"]) >= 1


def test_large_inline_style_fails(tmp_path):
    big_style = "{{" + ",".join(f'a{i}:"{i}px"' for i in range(200)) + "}}"
    (tmp_path / "Big.jsx").write_text(
        "export default function Big(){return <div style=" + big_style + " />}"
    )
    r = check(str(tmp_path), max_inline_css=400)
    assert r["ok"] is False
    assert len(r["violations"]) >= 1


def test_small_inline_style_passes(tmp_path):
    (tmp_path / "Small.jsx").write_text(
        'export default function Small(){return <div style={{top:"0px"}} />}'
    )
    r = check(str(tmp_path), max_inline_css=400)
    assert r["ok"] is True


def test_violation_records_file(tmp_path):
    (tmp_path / "Bad.jsx").write_text(
        "export default function Bad(){return <style>.x{}</style>}"
    )
    r = check(str(tmp_path))
    assert r["ok"] is False
    assert any("Bad.jsx" in v.get("file", "") for v in r["violations"])


def test_only_scans_jsx(tmp_path):
    # a .css file with a <style> string should be ignored (we only scan components)
    (tmp_path / "styles.css").write_text("<style> not a component </style>")
    (tmp_path / "Ok.jsx").write_text(
        'export default function Ok(){return <div className="flex" />}'
    )
    r = check(str(tmp_path))
    assert r["ok"] is True


def test_recurses(tmp_path):
    sub = tmp_path / "components"
    sub.mkdir()
    (sub / "Bad.jsx").write_text("export default ()=> <style>.x{}</style>")
    r = check(str(tmp_path))
    assert r["ok"] is False
