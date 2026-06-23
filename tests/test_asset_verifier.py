"""Tests for core.asset_verifier — the deterministic local-asset gate.

After localization, an image with a downloaded copy MUST be referenced by its
local ``/assets/...`` path, not hotlinked. This verifier reads a generated
component and flags any image that still hotlinks (when a local copy exists) or
went missing, so the orchestrator can re-dispatch it. Images with no local copy
(a host refused download too) are out of scope here — an onerror fallback covers
those. Pure, no LLM.
"""

from core import asset_verifier


def test_extract_img_srcs_handles_src_and_srcset():
    src = '<img src="/assets/images/a.png" srcset="/assets/images/a.png 1x, /assets/images/b.png 2x">'
    got = asset_verifier.extract_img_srcs(src)
    assert "/assets/images/a.png" in got
    assert "/assets/images/b.png" in got


def test_passes_when_local_path_is_used():
    images = [{"url": "https://cdn/foo.png", "local_url": "/assets/images/foo.png", "localized": True}]
    r = asset_verifier.verify_section_assets(images, '<img src="/assets/images/foo.png">')
    assert r["ok"]
    assert r["hotlinked"] == []
    assert r["missing"] == []


def test_flags_hotlink_when_local_copy_exists():
    images = [{"url": "https://cdn/foo.png", "local_url": "/assets/images/foo.png", "localized": True}]
    r = asset_verifier.verify_section_assets(images, '<img src="https://cdn/foo.png">')
    assert not r["ok"]
    assert "https://cdn/foo.png" in r["hotlinked"]


def test_flags_missing_local_image():
    images = [{"url": "https://cdn/foo.png", "local_url": "/assets/images/foo.png", "localized": True}]
    r = asset_verifier.verify_section_assets(images, "<div>no image here</div>")
    assert not r["ok"]
    assert "/assets/images/foo.png" in r["missing"]


def test_ignores_images_with_no_local_copy():
    images = [{"url": "https://loox.io/b.png", "local_url": None, "localized": False}]
    r = asset_verifier.verify_section_assets(images, '<img src="https://loox.io/b.png" onError="...">')
    assert r["ok"]


def test_trivially_ok_with_no_images():
    assert asset_verifier.verify_section_assets([], "<div/>")["ok"]


# --- aggregate ---

def test_verify_sections_assets_aggregates():
    sections = [
        {"name": "hero", "component_path": "h.jsx",
         "images": [{"url": "https://cdn/a.png", "local_url": "/assets/images/a.png", "localized": True}]},
        {"name": "foot", "component_path": "f.jsx",
         "images": [{"url": "https://cdn/b.png", "local_url": "/assets/images/b.png", "localized": True}]},
    ]
    sources = {"hero": '<img src="/assets/images/a.png">', "foot": '<img src="https://cdn/b.png">'}
    r = asset_verifier.verify_sections_assets(sections, sources)
    assert not r["ok"]
    assert "hero" in r["passed"]
    assert [f["name"] for f in r["failing"]] == ["foot"]
