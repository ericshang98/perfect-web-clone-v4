"""The serialized DOM and reference raster must observe the same settled state."""

import asyncio
import os

import pytest

from core.extractor.models import ExtractOptions
from core.extractor.service import ExtractorService


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE") != "1", reason="chromium extraction; set RUN_LIVE=1"
)


def test_delayed_hydration_settles_before_rest_state_bake(tmp_path):
    page_file = tmp_path / "delayed.html"
    page_file.write_text(
        """<!doctype html><html><body style="margin:0">
        <div style="height:2200px">tall</div>
        <aside id="product-info" style="display:none">Product offer</aside>
        <script>
          window.addEventListener('scroll', () => {
            if (window.scrollY === 0) {
              setTimeout(() => {
                document.querySelector('#product-info')
                  .style.setProperty('display', 'flex', 'important')
              }, 1500)
            }
          })
        </script>
        </body></html>""",
        encoding="utf-8",
    )
    async def run_capture():
        service = ExtractorService()
        try:
            return await service.extract(
                page_file.as_uri(),
                ExtractOptions(
                    settle_ms=0,
                    detect_theme=False,
                    extract_css=False,
                    extract_blocks=False,
                    download_resources=False,
                    capture_embeds=False,
                    include_screenshot=False,
                    full_page_screenshot=False,
                ),
            )
        finally:
            await service.close()

    result = asyncio.run(run_capture())

    assert result.success
    assert 'id="product-info" style="display: flex' in result.raw_html
