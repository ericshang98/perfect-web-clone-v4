"""Regression coverage for first-class desktop + mobile source evidence."""

import asyncio
import base64
import json
from io import BytesIO
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from PIL import Image
import pytest

from core.extractor import api
from core.extractor.models import (
    BreakpointCapture,
    ExtractionResult,
    InteractionStateCapture,
    PageMetadata,
    ScrollStateCapture,
)
from core.extractor.storage import SourceStore
from core.extractor.service import ExtractorService
from core.extractor.models import ExtractOptions


def _png_b64(width: int, height: int, color: tuple[int, int, int]) -> str:
    image = Image.new("RGB", (width, height), color)
    out = BytesIO()
    image.save(out, format="PNG")
    return base64.b64encode(out.getvalue()).decode("ascii")


def _metadata() -> PageMetadata:
    return PageMetadata(
        url="https://example.com",
        title="Example",
        viewport_width=1440,
        viewport_height=900,
        page_width=1440,
        page_height=2400,
        total_elements=4,
        max_depth=2,
        load_time_ms=10,
    )


def _capture(
    width: int, height: int, page_height: int, *, interaction_id: str | None = None
) -> BreakpointCapture:
    interactions = []
    if interaction_id:
        interactions = [{
            "id": interaction_id,
            "kind": "menu",
            "target": f"#{interaction_id}",
            "clone_target": f'[data-pwc-interaction="{interaction_id}"]',
            "action": "click",
            "required": True,
            "expect": {"observable": "menu_or_overlay_visibility_toggle"},
        }]
    return BreakpointCapture(
        breakpoint=width,
        viewport={"width": width, "height": height},
        page_width=width,
        page_height=page_height,
        screenshot_b64=_png_b64(width, height, (20, 30, 40)),
        full_b64=_png_b64(width, page_height, (40, 50, 60)),
        scroll_state_b64s=[
            _png_b64(width, height, (i * 20, 10, 10)) for i in range(5)
        ],
        interactions=interactions,
    )


def _result() -> ExtractionResult:
    return ExtractionResult(
        success=True,
        metadata=_metadata(),
        capture_integrity={"ok": True, "status": "passed"},
        breakpoint_captures=[
            _capture(1440, 900, 2400, interaction_id="desktop-menu"),
            _capture(390, 844, 3100, interaction_id="mobile-menu"),
        ],
    )


def test_persist_keeps_breakpoint_scoped_viewport_full_and_scroll_evidence(tmp_path):
    """Both required breakpoints retain their own viewport/full/scroll rasters."""
    store = SourceStore("source", tmp_path)
    store.ensure_dirs()
    result = _result()

    api._persist(store, result)

    for width, height in ((1440, 900), (390, 844)):
        root = store.dir / "screenshots" / "breakpoints" / str(width)
        assert (root / "viewport.png").is_file()
        assert (root / "full.png").is_file()
        assert len(list(root.glob("scroll_*.png"))) == 5
        interaction_evidence = store.dir / "evidence" / "breakpoints" / f"{width}.json"
        assert interaction_evidence.is_file()
        evidence = json.loads(interaction_evidence.read_text(encoding="utf-8"))
        expected_interaction = "desktop-menu" if width == 1440 else "mobile-menu"
        assert [item["id"] for item in evidence["interactions"]] == [expected_interaction]
        assert evidence["regions"] == []
        assert evidence["page"] == {}
        capture = next(item for item in result.breakpoint_captures if item.breakpoint == width)
        assert capture.viewport == {"width": width, "height": height}
        assert capture.full_page_screenshot_path == f"screenshots/breakpoints/{width}/full.png"


def test_persist_keeps_all_region_facts_and_post_trigger_interaction_refs(tmp_path):
    store = SourceStore("interaction-source", tmp_path)
    store.ensure_dirs()
    capture = _capture(390, 844, 3100, interaction_id="mobile-menu")
    capture.regions = [
        {"fingerprint": "id:mobile-menu", "selector": "#mobile-menu", "critical": False,
         "rect": {"x": 10, "y": 10, "width": 40, "height": 30}}
    ]
    capture.region_facts = {
        "id:mobile-menu": {"bounds": {"x": 10, "y": 10, "width": 40, "height": 30},
                           "style": {"display": "block"}, "controls": ["mobile menu"]}
    }
    capture.interaction_states = [
        InteractionStateCapture(
            id="i_390_mobile-menu",
            interaction_id="mobile-menu",
            screenshot_b64=_png_b64(390, 844, (80, 90, 100)),
            regions=capture.regions,
            facts=capture.region_facts,
        )
    ]
    capture.scroll_states = [
        ScrollStateCapture(
            id="s_390_scroll_500",
            scroll_y=500,
            screenshot_b64=_png_b64(390, 844, (60, 70, 80)),
            regions=[
                {
                    **capture.regions[0],
                    "position": "sticky",
                    "rect": {"x": 10, "y": 564, "width": 40, "height": 30},
                }
            ],
            facts={
                "id:mobile-menu": {
                    "bounds": {"x": 10, "y": 564, "width": 40, "height": 30},
                    "style": {"display": "block", "position": "sticky"},
                    "controls": ["mobile menu"],
                }
            },
        )
    ]

    api._persist(store, ExtractionResult(
        success=True, metadata=_metadata(),
        capture_integrity={"ok": True, "status": "passed"},
        breakpoint_captures=[capture],
    ))

    payload = json.loads(
        (store.dir / "evidence" / "breakpoints" / "390.json").read_text(encoding="utf-8")
    )
    assert payload["regions"][0]["fingerprint"] == "id:mobile-menu"
    assert payload["region_facts"]["id:mobile-menu"]["style"]["display"] == "block"
    scroll = payload["scroll_states"][0]
    assert (store.dir / scroll["ref"]).is_file()
    assert (store.dir / scroll["facts_path"]).is_file()
    assert scroll["ref_digest"].startswith("sha256:")
    assert scroll["facts_digest"].startswith("sha256:")
    assert scroll["scroll_y"] == 500
    state = payload["interaction_states"][0]
    assert (store.dir / state["ref"]).is_file()
    assert (store.dir / state["facts_path"]).is_file()
    assert state["ref_digest"].startswith("sha256:")
    assert state["facts_digest"].startswith("sha256:")
    assert state["ref"].startswith("refs/390/i_390_mobile-menu-")
    assert state["facts_path"].startswith(
        "evidence/breakpoints/390/interactions/i_390_mobile-menu-"
    )


class _FakeService:
    async def extract(self, _url, _options):
        return _result()


def test_summary_exposes_all_captured_breakpoints_to_manifest_generation(tmp_path, monkeypatch):
    """The compact extraction hand-off names desktop and mobile evidence."""
    monkeypatch.setattr(api, "_get_service", lambda: _FakeService())

    response = asyncio.run(
        api.aextract_page("https://example.com", storage_root=tmp_path)
    )

    expected_breakpoints = [
        {
            "breakpoint": 1440,
            "device_scale_factor": 1,
            "viewport": {"width": 1440, "height": 900},
            "page_width": 1440,
            "page_height": 2400,
            "screenshot": "screenshots/breakpoints/1440/viewport.png",
            "full_page_screenshot": "screenshots/breakpoints/1440/full.png",
            "scroll_states": [
                f"screenshots/breakpoints/1440/scroll_{i:02d}.png" for i in range(5)
            ],
            "interaction_evidence": "evidence/breakpoints/1440.json",
        },
        {
            "breakpoint": 390,
            "device_scale_factor": 1,
            "viewport": {"width": 390, "height": 844},
            "page_width": 390,
            "page_height": 3100,
            "screenshot": "screenshots/breakpoints/390/viewport.png",
            "full_page_screenshot": "screenshots/breakpoints/390/full.png",
            "scroll_states": [
                f"screenshots/breakpoints/390/scroll_{i:02d}.png" for i in range(5)
            ],
            "interaction_evidence": "evidence/breakpoints/390.json",
        },
    ]
    assert response["summary"]["breakpoints"] == expected_breakpoints
    persisted = json.loads(
        (tmp_path / response["source_id"] / "summary.json").read_text(encoding="utf-8")
    )
    assert persisted["breakpoints"] == expected_breakpoints


class _BreakpointPage:
    def __init__(self):
        self.viewports = []
        self.reloads = 0

    async def set_viewport_size(self, viewport):
        self.viewports.append(viewport)

    async def reload(self, **_kwargs):
        self.reloads += 1

    async def evaluate(self, _script):
        return {"interactions": [], "regions": [], "page": {}}


class _Response:
    def __init__(self, status):
        self.status = status


class _ErrorReloadPage(_BreakpointPage):
    async def reload(self, **_kwargs):
        self.reloads += 1
        return _Response(429)


class _InventoryFailurePage(_BreakpointPage):
    async def reload(self, **_kwargs):
        self.reloads += 1
        return _Response(200)

    async def evaluate(self, _script):
        raise RuntimeError("inventory execution failed")


def test_mobile_options_drive_a_real_second_browser_viewport_capture(monkeypatch):
    """The configured mobile dimensions reach Playwright, rather than being ignored."""
    service = ExtractorService()
    page = _BreakpointPage()
    options = ExtractOptions(
        settle_ms=0,
        mobile_viewport_width=412,
        mobile_viewport_height=915,
    )

    async def no_scroll(*_args, **_kwargs):
        return None

    async def metadata(*_args, **_kwargs):
        return PageMetadata(
            url="https://example.com",
            title="Example",
            viewport_width=412,
            viewport_height=915,
            page_width=412,
            page_height=2200,
            total_elements=1,
            max_depth=1,
            load_time_ms=1,
        )

    async def shot(_page, *, full_page=True):
        return _png_b64(412, 2200 if full_page else 915, (1, 2, 3))

    async def scroll_states(*_args, **_kwargs):
        return [
            ScrollStateCapture(
                id="s_412_scroll_0",
                scroll_y=0,
                screenshot_b64=_png_b64(412, 915, (4, 5, 6)),
            )
        ]

    monkeypatch.setattr(service, "_scroll_to_load_lazy", no_scroll)
    monkeypatch.setattr(service, "_extract_metadata", metadata)
    monkeypatch.setattr(service, "_screenshot", shot)
    monkeypatch.setattr(service, "_capture_scroll_state_evidence", scroll_states)

    capture = asyncio.run(
        service._capture_breakpoint(
            page,
            "https://example.com",
            options,
            width=options.mobile_viewport_width,
            height=options.mobile_viewport_height,
            load_ms=1,
            reload_source=True,
        )
    )

    assert page.viewports == [{"width": 412, "height": 915}]
    assert page.reloads == 1
    assert capture.breakpoint == 412
    assert capture.viewport == {"width": 412, "height": 915}
    assert capture.scroll_states


def test_breakpoint_reload_refuses_http_error_evidence(monkeypatch):
    """A 429 mobile reload must not be persisted as source evidence."""
    service = ExtractorService()
    page = _ErrorReloadPage()
    options = ExtractOptions(settle_ms=0, include_screenshot=False, full_page_screenshot=False)

    async def no_scroll(*_args, **_kwargs):
        return None

    monkeypatch.setattr(service, "_scroll_to_load_lazy", no_scroll)

    with pytest.raises(RuntimeError, match="HTTP 429"):
        asyncio.run(
            service._capture_breakpoint(
                page,
                "https://example.com",
                options,
                width=390,
                height=844,
                load_ms=1,
                reload_source=True,
            )
        )


def test_breakpoint_inventory_failure_never_becomes_an_empty_interaction_list(monkeypatch):
    """Only a successful inventory may certify that a viewport has no controls."""
    service = ExtractorService()
    page = _InventoryFailurePage()

    async def no_scroll(*_args, **_kwargs):
        return None

    async def metadata(*_args, **_kwargs):
        return PageMetadata(
            url="https://example.com", title="Example", viewport_width=390,
            viewport_height=844, page_width=390, page_height=844,
            total_elements=1, max_depth=1, load_time_ms=1,
        )

    monkeypatch.setattr(service, "_scroll_to_load_lazy", no_scroll)
    monkeypatch.setattr(service, "_extract_metadata", metadata)
    with pytest.raises(RuntimeError, match="inventory"):
        asyncio.run(
            service._capture_breakpoint(
                page,
                "https://example.com",
                ExtractOptions(settle_ms=0, include_screenshot=False, full_page_screenshot=False),
                width=390,
                height=844,
                load_ms=1,
                reload_source=True,
            )
        )


def test_breakpoint_region_inventory_includes_noncritical_volatile_regions():
    inventory = {
        "regions": [
            {
                "fingerprint": "main",
                "selector": "main",
                "critical": True,
                "rect": {"x": 0, "y": 0, "width": 390, "height": 800},
            }
        ],
        "volatile_candidates": [
            {
                "id": "live-clock",
                "selector": "#clock",
                "hint": "live_text",
                "bounds": {"x": 10, "y": 20, "width": 100, "height": 40},
            }
        ],
    }

    regions = ExtractorService._regions(inventory)

    assert [region["fingerprint"] for region in regions] == [
        "main",
        "live-clock",
    ]
    assert regions[1]["rect"] == inventory["volatile_candidates"][0]["bounds"]


def test_real_browser_mobile_reload_discards_desktop_bake_and_discovers_mobile_only_menu():
    """A real local source proves mobile evidence is fresh, not desktop residue."""
    html = b"""<!doctype html><html><head><style>
      html,body{margin:0} #responsive{height:100vh;background:rgb(0,0,255)}
      #mobile-menu{display:none}
      @media (max-width:600px){#responsive{background:rgb(255,128,0)}
      #desktop-menu{display:none}#mobile-menu{display:block}}
    </style></head><body><main id="responsive">
      <button id="desktop-menu" aria-controls="desktop-nav" aria-expanded="false">Desktop menu</button>
      <nav id="desktop-nav" hidden>Desktop navigation</nav>
      <button id="mobile-menu" aria-controls="mobile-nav" aria-expanded="false">Mobile menu</button>
      <nav id="mobile-nav" hidden>Mobile navigation</nav>
      <details id="faq"><summary>Frequently asked question</summary>
        <p>Browser-native accordion answer.</p>
      </details>
      <div id="slides"><article class="slide active">First slide</article>
        <article class="slide">Second slide</article></div>
      <button id="next-slide">Next slide</button>
    </main><script>
      for (const id of ['desktop', 'mobile']) {
        const button = document.querySelector(`#${id}-menu`);
        const nav = document.querySelector(`#${id}-nav`);
        button.addEventListener('click', () => {
          const expanded = button.getAttribute('aria-expanded') === 'true';
          button.setAttribute('aria-expanded', String(!expanded));
          nav.hidden = expanded;
        });
      }
      document.querySelector('#next-slide').addEventListener('click', () => {
        const slides = Array.from(document.querySelectorAll('.slide'));
        slides[0].classList.remove('active');
        slides[1].classList.add('active');
      });
    </script></body></html>"""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - stdlib handler API
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *_args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    service = ExtractorService()
    try:
        async def capture_after_desktop_bake():
            from playwright.async_api import async_playwright
            from core.extractor import dom_scripts as js

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                page = await browser.new_page(viewport={"width": 1440, "height": 900})
                try:
                    await page.goto(
                        f"http://127.0.0.1:{server.server_port}/",
                        wait_until="load",
                        timeout=10_000,
                    )
                    # This is the exact desktop mutation performed by the full
                    # extractor; the mobile capture must not inherit it.
                    await page.evaluate(js.REST_STATE_BAKE_JS)
                    return await service._capture_breakpoint(
                        page,
                        f"http://127.0.0.1:{server.server_port}/",
                        ExtractOptions(settle_ms=0, nav_timeout_ms=10_000, eval_timeout_ms=5_000),
                        width=390,
                        height=844,
                        load_ms=1,
                        reload_source=True,
                    )
                finally:
                    await page.close()
                    await browser.close()

        mobile = asyncio.run(asyncio.wait_for(capture_after_desktop_bake(), timeout=20))
        assert any(item["target"] == "#mobile-menu" for item in mobile.interactions)
        assert not any(item["target"] == "#desktop-menu" for item in mobile.interactions)
        assert len(mobile.interaction_states) >= 3
        assert all(state.screenshot_b64 for state in mobile.interaction_states)
        assert all(
            any(
                behavior.get("passed") is True
                for fact in state.facts.values()
                for behavior in fact.get("behavior") or []
            )
            for state in mobile.interaction_states
        )
        # The desktop bake inlines ``display:none`` onto #mobile-menu.  Its
        # presence above therefore proves this evidence came after reload, not
        # from merely resizing the mutated desktop DOM.
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_real_scroll_evidence_measures_sticky_top_inset_per_state():
    html = b"""<!doctype html><html><head><style>
      html,body{margin:0}
      .before{height:200px}
      header{position:sticky;top:64px;height:50px;background:#123;color:white}
      main{height:1350px}
    </style></head><body>
      <div class="before"></div>
      <header id="sticky">Sticky navigation</header>
      <main><h1>Long content</h1></main>
    </body></html>"""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *_args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    service = ExtractorService()
    try:
        async def capture():
            from playwright.async_api import async_playwright

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                page = await browser.new_page(viewport={"width": 800, "height": 400})
                try:
                    await page.goto(
                        f"http://127.0.0.1:{server.server_port}/",
                        wait_until="load",
                    )
                    page_height = float(
                        await page.evaluate("document.documentElement.scrollHeight")
                    )
                    return await service._capture_scroll_state_evidence(
                        page,
                        page_height,
                        400,
                        timeout_s=5,
                        breakpoint=800,
                        n=3,
                    )
                finally:
                    await page.close()
                    await browser.close()

        states = asyncio.run(asyncio.wait_for(capture(), timeout=20))
        scrolled = next(state for state in states if state.scroll_y > 200)
        sticky = next(
            region
            for region in scrolled.regions
            if region.get("position") == "sticky"
        )
        local_y = float(sticky["rect"]["y"]) - scrolled.scroll_y

        assert local_y == pytest.approx(64, abs=1)
        assert scrolled.facts[sticky["fingerprint"]]["bounds"]["y"] == pytest.approx(
            scrolled.scroll_y + 64,
            abs=1,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
