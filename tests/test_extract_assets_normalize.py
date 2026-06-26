"""_extract_assets must expand a raw ASSETS_JS payload via asset_urls.normalize_assets."""
import asyncio
from core.extractor.service import ExtractorService


class _FakePage:
    def __init__(self, payload): self._p = payload
    async def evaluate(self, *a, **k): return self._p


def test_extract_assets_uses_normalizer(monkeypatch):
    payload = {
        "images": [{"src": "data:image/gif;base64,A", "dataSrc": "https://cdn/p_{width}x.jpg"}],
        "fonts": [{"url": "f.woff2", "sheetHref": "https://site.com/t/x.css"}],
        "scripts": [], "stylesheets": [], "videos": [],
    }
    svc = ExtractorService()
    svc._asset_base_url = "https://site.com/"   # set by extract(); see Step 3
    out = asyncio.run(svc._extract_assets(_FakePage(payload)))
    assert [i.url for i in out.images] == ["https://cdn/p_1200x.jpg"]
    assert [f.url for f in out.fonts] == ["https://site.com/t/f.woff2"]
