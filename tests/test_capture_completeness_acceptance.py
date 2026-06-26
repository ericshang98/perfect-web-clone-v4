"""Live acceptance: the widened capture must grab the bulk of pagerie's images
+ the brand fonts. Skipped unless RUN_LIVE=1 (needs network + chromium)."""
import os, asyncio, pytest
from core.extractor.service import ExtractorService
from core.extractor.models import ExtractOptions

pytestmark = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="live capture; set RUN_LIVE=1")


def test_pagerie_capture_grabs_images_and_brand_fonts():
    svc = ExtractorService()
    res = asyncio.run(svc.extract("https://www.pagerie.com",
                                  ExtractOptions(settle_ms=9000, max_images=150, max_fonts=24)))
    dl = res.downloaded_resources
    assert dl is not None, "no downloaded_resources on result"
    assert len(dl.images) >= 80, f"only {len(dl.images)} images captured (want >=80)"
    font_names = " ".join((f.filename or f.url).lower() for f in dl.fonts)
    assert "pano" in font_names or "pagerie" in font_names, "brand fonts not captured"
