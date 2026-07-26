"""Theme handling must preserve the source's authored default state."""

import asyncio
import base64
import io
import os

import pytest
from bs4 import BeautifulSoup
from PIL import Image

from core.extractor.models import ExtractOptions, ThemeMode
from core.extractor.service import ExtractorService
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


def test_named_dark_theme_remains_the_primary_capture(tmp_path):
    page_file = tmp_path / "business-theme.html"
    page_file.write_text(
        """<!doctype html>
        <html data-theme="business">
          <head>
            <style>
              html, body { margin: 0; min-height: 900px; }
              header { height: 80px; }
              main { height: 740px; }
              section { height: 700px; padding: 20px; }
              footer { height: 80px; }
              html[data-theme="business"], html[data-theme="business"] body {
                color-scheme: dark;
                background: rgb(20, 20, 20);
                color: rgb(240, 240, 240);
              }
              html[data-theme="light"], html[data-theme="light"] body {
                color-scheme: light;
                background: rgb(255, 255, 255);
                color: rgb(20, 20, 20);
              }
              html[data-theme="dark"], html[data-theme="dark"] body {
                color-scheme: dark;
                background: rgb(20, 20, 20);
                color: rgb(240, 240, 240);
              }
            </style>
          </head>
          <body>
            <header><nav><a href="/">Business</a></nav></header>
            <main>
              <section>
                <h1>Business theme</h1>
                <button type="button">Start clock</button>
              </section>
            </main>
            <footer>Business footer</footer>
          </body>
        </html>""",
        encoding="utf-8",
    )

    async def capture():
        service = ExtractorService()
        try:
            return await service.extract(
                page_file.as_uri(),
                ExtractOptions(
                    settle_ms=0,
                    extract_css=False,
                    extract_blocks=False,
                    download_resources=False,
                    capture_embeds=False,
                ),
            )
        finally:
            await service.close()

    result = asyncio.run(capture())
    root = BeautifulSoup(result.raw_html, "html.parser").html
    primary = Image.open(
        io.BytesIO(base64.b64decode(result.full_b64))
    ).convert("RGB")

    assert result.success, result.capture_integrity
    assert result.current_theme == ThemeMode.DARK
    assert root["data-theme"] == "business"
    assert root.get("data-color-scheme") is None
    assert root.get("style") is None
    assert primary.getpixel((5, 5)) == (20, 20, 20)
