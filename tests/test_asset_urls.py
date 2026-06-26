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
