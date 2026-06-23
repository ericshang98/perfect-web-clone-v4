"""Tests for core.asset_localizer — point the clone at downloaded local assets.

The extractor downloads images/fonts to ``assets/`` (with a ``saved_path``); the
section data, however, still references the original CDN URLs, so the clone
hotlinks — and breaks the moment a host refuses (Loox, hotlink protection) or the
asset disappears. This module rewrites section HTML + image lists to the local
copies, keeping the remote URL only as a fallback. Pure, deterministic, no LLM.
"""

from core import asset_localizer


# --------------------------------------------------------------------------- #
# build_asset_map — original URL -> public local path
# --------------------------------------------------------------------------- #

def test_build_asset_map_maps_url_to_public_path():
    downloaded = {
        "images": [
            {"url": "https://cdn.shopify.com/x/foo.png?v=1", "saved_path": "assets/images/foo.png"},
        ]
    }
    m = asset_localizer.build_asset_map(downloaded)
    assert m["https://cdn.shopify.com/x/foo.png?v=1"] == "/assets/images/foo.png"


def test_build_asset_map_skips_entries_without_saved_path():
    downloaded = {"images": [{"url": "https://x/y.png", "saved_path": None}]}
    assert asset_localizer.build_asset_map(downloaded) == {}


def test_build_asset_map_covers_fonts_and_scripts():
    downloaded = {
        "images": [],
        "fonts": [{"url": "https://x/f.woff2", "saved_path": "assets/fonts/f.woff2"}],
        "scripts": [{"url": "https://x/s.js", "saved_path": "assets/scripts/s.js"}],
    }
    m = asset_localizer.build_asset_map(downloaded)
    assert m["https://x/f.woff2"] == "/assets/fonts/f.woff2"
    assert m["https://x/s.js"] == "/assets/scripts/s.js"


def test_build_asset_map_handles_none():
    assert asset_localizer.build_asset_map(None) == {}


# --------------------------------------------------------------------------- #
# localize_html — rewrite references to local paths
# --------------------------------------------------------------------------- #

def test_localize_html_rewrites_img_src():
    m = {"https://cdn.shopify.com/x/foo.png?v=1": "/assets/images/foo.png"}
    html = '<img src="https://cdn.shopify.com/x/foo.png?v=1" alt="a">'
    out = asset_localizer.localize_html(html, m)
    assert 'src="/assets/images/foo.png"' in out


def test_localize_html_rewrites_inside_srcset():
    m = {"https://cdn/x/foo.png": "/assets/images/foo.png"}
    html = '<img srcset="https://cdn/x/foo.png 1x, https://cdn/x/foo.png 2x">'
    out = asset_localizer.localize_html(html, m)
    assert out.count("/assets/images/foo.png") == 2
    assert "https://cdn/x/foo.png" not in out


def test_localize_html_leaves_unmapped_urls_alone():
    m = {"https://cdn/x/foo.png": "/assets/images/foo.png"}
    html = '<img src="https://loox.io/blocked.png">'
    out = asset_localizer.localize_html(html, m)
    assert out == html  # no local copy → untouched (onerror fallback handles it)


def test_localize_html_matches_by_basename_ignoring_query_variants():
    # Downloaded with one set of query params; the HTML uses a different width/v.
    m = {"https://livora.co/cdn/shop/files/foo.png?v=1&width=500": "/assets/images/foo.png"}
    html = '<img src="https://livora.co/cdn/shop/files/foo.png?v=9&width=823">'
    out = asset_localizer.localize_html(html, m)
    assert 'src="/assets/images/foo.png"' in out


def test_localize_html_matches_cdn_domain_variant_by_basename():
    # Shopify serves the same file from both the shop domain and cdn.shopify.com.
    m = {"https://livora.co/cdn/shop/files/foo.png?width=500": "/assets/images/foo.png"}
    html = '<img src="https://cdn.shopify.com/s/files/1/0614/foo.png?width=1200">'
    out = asset_localizer.localize_html(html, m)
    assert "/assets/images/foo.png" in out


def test_localize_html_basename_match_in_srcset():
    m = {"https://livora.co/cdn/shop/files/foo.png?width=500": "/assets/images/foo.png"}
    html = '<img srcset="https://cdn.shopify.com/s/files/1/foo.png?width=400 400w, https://cdn.shopify.com/s/files/1/foo.png?width=800 800w">'
    out = asset_localizer.localize_html(html, m)
    assert out.count("/assets/images/foo.png") == 2
    assert "cdn.shopify.com" not in out


# --------------------------------------------------------------------------- #
# localize_sections — wire it onto chunker sections
# --------------------------------------------------------------------------- #

def test_localize_sections_rewrites_html_and_marks_images():
    m = {"https://cdn/x/foo.png": "/assets/images/foo.png"}
    sections = [
        {
            "name": "hero",
            "full_html": '<img src="https://cdn/x/foo.png">',
            "images": [{"url": "https://cdn/x/foo.png", "alt": "a"}],
        }
    ]
    asset_localizer.localize_sections(sections, m)
    assert 'src="/assets/images/foo.png"' in sections[0]["full_html"]
    img = sections[0]["images"][0]
    assert img["local_url"] == "/assets/images/foo.png"
    assert img["url"] == "https://cdn/x/foo.png"  # remote kept as fallback


def test_localize_sections_flags_image_with_no_local_copy():
    sections = [{"name": "r", "full_html": "", "images": [{"url": "https://loox.io/b.png"}]}]
    asset_localizer.localize_sections(sections, {})
    img = sections[0]["images"][0]
    assert img.get("local_url") is None
    assert img["localized"] is False


def test_localize_sections_safe_with_empty_map():
    sections = [{"name": "r", "full_html": "<div>x</div>", "images": []}]
    asset_localizer.localize_sections(sections, {})  # must not raise
    assert sections[0]["full_html"] == "<div>x</div>"
