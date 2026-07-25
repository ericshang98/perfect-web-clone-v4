"""Theme toggling must tolerate transient documents during site navigation."""

import os

import pytest

from core.extractor.theme import APPLY_THEME_JS


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE") != "1", reason="chromium theme script; set RUN_LIVE=1"
)


def test_apply_theme_is_safe_when_body_is_temporarily_absent():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<main>loading</main>")
        page.evaluate("document.body.remove()")

        applied = page.evaluate(APPLY_THEME_JS, "light")
        browser.close()

    assert applied is False
