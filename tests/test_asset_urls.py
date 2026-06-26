from core.extractor import asset_urls


def test_plain_src_passes_through():
    assert asset_urls.expand_image_urls({"src": "https://x/a.png"}) == ["https://x/a.png"]


def test_lazy_data_src_with_width_template_substituted():
    out = asset_urls.expand_image_urls(
        {"src": "data:image/gif;base64,AAAA", "dataSrc": "https://cdn/shop/p_{width}x.jpg"}
    )
    assert out == ["https://cdn/shop/p_1200x.jpg"]  # placeholder src skipped, {width}->1200


def test_srcset_expanded_to_all_candidates():
    out = asset_urls.expand_image_urls({"srcset": "https://x/a_300.jpg 300w, https://x/a_900.jpg 900w"})
    assert out == ["https://x/a_300.jpg", "https://x/a_900.jpg"]


def test_data_image_url_and_bg_collected():
    out = asset_urls.expand_image_urls({"dataImageUrl": "https://x/hover.png", "bg": "https://x/bg.jpg"})
    assert set(out) == {"https://x/hover.png", "https://x/bg.jpg"}


def test_relative_url_joined_and_protocol_relative_https():
    assert asset_urls.expand_image_urls({"src": "/cdn/a.png"}, base_url="https://site.com/x") == ["https://site.com/cdn/a.png"]
    assert asset_urls.expand_image_urls({"src": "//cdn/a.png"}) == ["https://cdn/a.png"]


def test_dedupes_and_skips_data_blob_and_unsubstituted_templates():
    out = asset_urls.expand_image_urls(
        {"src": "https://x/a.png", "dataSrc": "https://x/a.png", "srcset": "blob:xyz 1x, {bad} 2x"}
    )
    assert out == ["https://x/a.png"]


def test_font_absolute_url_unchanged():
    assert asset_urls.absolutize_font_url("https://x/f.woff2", None) == "https://x/f.woff2"


def test_font_relative_resolved_against_sheet_href():
    out = asset_urls.absolutize_font_url("panolight.woff2", "https://site.com/cdn/t/3/assets/theme.css")
    assert out == "https://site.com/cdn/t/3/assets/panolight.woff2"


def test_font_relative_falls_back_to_page_url():
    out = asset_urls.absolutize_font_url("f.woff2", None, page_url="https://site.com/")
    assert out == "https://site.com/f.woff2"


def test_font_data_uri_and_empty_return_none():
    assert asset_urls.absolutize_font_url("data:font/woff2;base64,AA", "https://x/t.css") is None
    assert asset_urls.absolutize_font_url("", "https://x/t.css") is None


def test_normalize_assets_expands_images_and_fonts():
    raw = {
        "images": [
            {"src": "data:image/gif;base64,A", "dataSrc": "https://cdn/p_{width}x.jpg"},
            {"src": "https://cdn/logo.svg"},
        ],
        "fonts": [{"url": "panolight.woff2", "sheetHref": "https://site.com/t/assets/x.css"}],
    }
    norm = asset_urls.normalize_assets(raw, base_url="https://site.com/")
    assert [i["url"] for i in norm["images"]] == ["https://cdn/p_1200x.jpg", "https://cdn/logo.svg"]
    assert [f["url"] for f in norm["fonts"]] == ["https://site.com/t/assets/panolight.woff2"]
    assert all(i["type"] == "image" for i in norm["images"])


def test_harvest_html_image_urls_finds_noscript_relative_template_and_json():
    html = (
        '<img src="data:image/gif;base64,AAA">'
        '<noscript><img src="https://cdn/shop/files/a_600x.jpg"></noscript>'
        '<div data-src="//cdn/shop/files/b_{width}x.png?v=1"></div>'
        '<a href="/cdn/shop/files/c.webp">x</a>'
        '<script>{"image":"https:\\/\\/cdn\\/shop\\/files\\/d_1024x.jpg"}</script>'
    )
    out = asset_urls.harvest_html_image_urls(html, base_url="https://site.com/")
    assert "https://cdn/shop/files/a_600x.jpg" in out
    assert "https://cdn/shop/files/b_1200x.png?v=1" in out   # protocol-relative + {width}
    assert "https://site.com/cdn/shop/files/c.webp" in out   # root-relative joined to base
    assert "https://cdn/shop/files/d_1024x.jpg" in out       # JSON-escaped \/
    assert not any(u.startswith("data:") for u in out)       # blobs/data skipped
    assert len(out) == len(set(out))                         # deduped
