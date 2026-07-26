from core.capture_integrity import assess_capture_integrity


def _region(
    fingerprint: str,
    *,
    y: float,
    height: float,
    width: float = 1440,
    kind: str = "section",
    critical: bool = True,
    selector: str | None = None,
):
    return {
        "fingerprint": fingerprint,
        "selector": selector,
        "kind": kind,
        "tag": "section",
        "rect": {"x": 0, "y": y, "width": width, "height": height},
        "critical": critical,
        "signals": {"heading": True, "media": True, "controls": 1},
    }


def test_reelshort_shape_fails_when_hero_disappears_from_normalized_capture():
    pre = [
        _region("header", y=0, height=128, kind="header"),
        _region("hero", y=128, height=484, kind="hero"),
        _region("new-releases", y=612, height=650),
        _region("footer", y=5950, height=500, kind="footer"),
    ]
    post = [
        _region("header", y=0, height=128, kind="header"),
        _region("new-releases", y=128, height=650),
        _region("footer", y=5488, height=500, kind="footer"),
    ]

    report = assess_capture_integrity(
        pre_regions=pre,
        post_regions=post,
        pre_page_height=6450,
        post_page_height=5988,
        raster_height=5988,
        viewport_width=1440,
        viewport_height=900,
    )

    assert report["status"] == "failed"
    assert report["ok"] is False
    assert "hero" in report["missing_critical"]
    assert any(issue["code"] == "critical_region_missing" for issue in report["issues"])


def test_material_raster_height_loss_fails_even_when_region_matching_is_ambiguous():
    regions = [
        _region("header", y=0, height=100, kind="header"),
        _region("content", y=100, height=1900),
    ]

    report = assess_capture_integrity(
        pre_regions=regions,
        post_regions=regions,
        pre_page_height=2000,
        post_page_height=2000,
        raster_height=1600,
        viewport_width=1440,
        viewport_height=900,
    )

    assert report["status"] == "failed"
    assert any(issue["code"] == "raster_height_loss" for issue in report["issues"])


def test_small_geometry_drift_passes():
    pre = [
        _region("header", y=0, height=100, kind="header"),
        _region("hero", y=100, height=500, kind="hero"),
        _region("content", y=600, height=1400),
    ]
    post = [
        _region("header", y=0, height=100, kind="header"),
        _region("hero", y=100, height=495, kind="hero"),
        _region("content", y=595, height=1405),
    ]

    report = assess_capture_integrity(
        pre_regions=pre,
        post_regions=post,
        pre_page_height=2000,
        post_page_height=2000,
        raster_height=2000,
        viewport_width=1440,
        viewport_height=900,
    )

    assert report["status"] == "passed"
    assert report["ok"] is True
    assert report["missing_critical"] == []


def test_noncritical_tiny_region_may_disappear_without_failing_capture():
    pre = [
        _region("content", y=0, height=1600),
        _region("decorative-chip", y=400, width=80, height=24, critical=False),
    ]
    post = [_region("content", y=0, height=1600)]

    report = assess_capture_integrity(
        pre_regions=pre,
        post_regions=post,
        pre_page_height=1600,
        post_page_height=1600,
        raster_height=1600,
        viewport_width=1440,
        viewport_height=900,
    )

    assert report["status"] == "passed"


def test_duplicate_fingerprints_match_the_same_selector_instead_of_last_region():
    pre = [
        _region(
            "heading:naro",
            y=0,
            height=1596,
            width=1410,
            kind="hero",
            selector="#root > div.page",
        ),
        _region(
            "heading:naro",
            y=0,
            height=868,
            width=1410,
            kind="hero",
            selector="#root > div.page > main",
        ),
        _region(
            "heading:naro",
            y=80,
            height=788,
            width=564,
            critical=False,
            selector="#root > div.page > main > div.details",
        ),
    ]
    post = [
        _region(
            "heading:naro",
            y=0,
            height=1550,
            width=1410,
            kind="hero",
            selector="#root > div.page",
        ),
        _region(
            "heading:naro",
            y=0,
            height=822,
            width=1410,
            kind="hero",
            selector="#root > div.page > main",
        ),
        _region(
            "heading:naro",
            y=80,
            height=742,
            width=706,
            critical=False,
            selector="#root > div.page > main > div.details",
        ),
    ]

    report = assess_capture_integrity(
        pre_regions=pre,
        post_regions=post,
        pre_page_height=1596,
        post_page_height=1550,
        raster_height=1518,
        viewport_width=1440,
        viewport_height=900,
    )

    assert report["status"] == "passed"
    assert report["collapsed_critical"] == []
