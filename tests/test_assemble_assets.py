"""The assembler must ship downloaded assets into the clone's public/ dir.

Localized section HTML points images at ``/assets/images/...``; that only
resolves if the files are actually copied into the Vite ``public/`` dir. Without
this, localization would turn working hotlinks into broken local 404s.
"""


def test_copy_downloaded_assets_into_public(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "shop.com-1-cp"
    img_dir = tmp_path / sid / "assets" / "images"
    img_dir.mkdir(parents=True)
    (img_dir / "foo.png").write_bytes(b"\x89PNG-bytes")
    font_dir = tmp_path / sid / "assets" / "fonts"
    font_dir.mkdir(parents=True)
    (font_dir / "f.woff2").write_bytes(b"woff2")

    work = tmp_path / "work"
    work.mkdir()

    class FakeSB:
        work_dir = work

    from mcp_server.tools import build_deploy

    count, dest = build_deploy._copy_downloaded_assets(sid, FakeSB())
    assert count == 2
    assert dest == "public/assets"
    assert (work / "public" / "assets" / "images" / "foo.png").read_bytes() == b"\x89PNG-bytes"
    assert (work / "public" / "assets" / "fonts" / "f.woff2").read_bytes() == b"woff2"


def test_copy_downloaded_assets_no_assets_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    sid = "shop.com-2-empty"
    (tmp_path / sid).mkdir()
    work = tmp_path / "work2"
    work.mkdir()

    class FakeSB:
        work_dir = work

    from mcp_server.tools import build_deploy

    count, dest = build_deploy._copy_downloaded_assets(sid, FakeSB())
    assert count == 0
    assert dest is None
