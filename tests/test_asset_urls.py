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
