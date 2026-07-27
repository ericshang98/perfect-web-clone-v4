"""Deterministic runtime/responsive evidence evaluation."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from core.runtime_audit import (
    collect_runtime_observations,
    evaluate_runtime_observations,
)


def _clean(width: int) -> dict:
    return {
        "breakpoint": width,
        "navigation": {"ok": True, "status": 200},
        "console": [],
        "page_errors": [],
        "request_failures": [],
        "http_errors": [],
        "resources": [
            {
                "url": "http://127.0.0.1:4173/assets/app.js",
                "resource_type": "script",
                "content_type": "application/javascript",
            }
        ],
        "fonts": [{"family": "Inter", "status": "loaded", "check": True}],
        "images": [{"src": "/hero.webp", "complete": True, "naturalWidth": 800}],
        "media": [{"src": "/hero.mp4", "readyState": 4, "error": None}],
        "layout": {
            "viewport_width": width,
            "scroll_width": width,
            "reachable_scroll_x": 0,
            "offenders": [],
        },
    }


def test_clean_desktop_mobile_and_contained_carousel_pass():
    desktop = _clean(1440)
    mobile = _clean(390)
    mobile["layout"]["contained_overflows"] = [
        {
            "selector": ".carousel-track",
            "client_width": 360,
            "scroll_width": 1080,
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [desktop, mobile],
        required_breakpoints=[1440, 390],
    )

    assert result["runtime"]["ok"] is True
    assert result["responsive"]["ok"] is True
    assert result["ok"] is True


def test_runtime_fails_closed_on_navigation_console_and_network_errors():
    observation = _clean(390)
    observation["navigation"] = {"ok": False, "status": 503, "error": "timeout"}
    observation["console"] = [
        {"type": "warning", "text": "bad font"},
        {"type": "error", "text": "boom"},
    ]
    observation["page_errors"] = ["ReferenceError"]
    observation["request_failures"] = [
        {"url": "/missing.js", "error": "net::ERR_FAILED"}
    ]
    observation["http_errors"] = [{"url": "/api", "status": 500}]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )
    codes = {row["code"] for row in result["runtime"]["failures"]}

    assert {
        "navigation_failed",
        "console_warning",
        "console_error",
        "page_error",
        "request_failed",
        "http_error",
    } <= codes


def test_runtime_ignores_aborted_media_range_when_media_is_usable():
    observation = _clean(390)
    observation["request_failures"] = [
        {
            "url": "/hero.mp4",
            "resource_type": "media",
            "error": "net::ERR_ABORTED",
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )

    assert result["runtime"]["ok"] is True


def test_runtime_rejects_aborted_media_when_media_is_not_usable():
    observation = _clean(390)
    observation["request_failures"] = [
        {
            "url": "/hero.mp4",
            "resource_type": "media",
            "error": "net::ERR_ABORTED",
        }
    ]
    observation["media"] = [
        {
            "src": "/hero.mp4",
            "readyState": 0,
            "error": None,
            "visible": True,
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )
    codes = [row["code"] for row in result["runtime"]["failures"]]

    assert "request_failed" in codes
    assert "broken_media" in codes


def test_runtime_rejects_external_origins_and_content_type_mismatch():
    observation = _clean(390)
    observation["resources"] = [
        {
            "url": "https://cdn.shopify.com/theme.js",
            "resource_type": "script",
            "content_type": "text/html",
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )
    codes = {row["code"] for row in result["runtime"]["failures"]}

    assert "external_http_origin" in codes
    assert "resource_content_type_mismatch" in codes


def test_runtime_rejects_fonts_images_and_media_that_did_not_load():
    observation = _clean(390)
    observation["fonts"] = [
        {"family": "Poppins", "status": "error", "check": False}
    ]
    observation["images"] = [
        {"src": "/broken.webp", "complete": True, "naturalWidth": 0}
    ]
    observation["media"] = [
        {"src": "/broken.mp4", "readyState": 0, "error": "MEDIA_ERR_SRC_NOT_SUPPORTED"}
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )
    codes = {row["code"] for row in result["runtime"]["failures"]}

    assert {"font_not_loaded", "broken_image", "broken_media"} <= codes


def test_runtime_accepts_unused_font_and_offscreen_lazy_resources():
    observation = _clean(390)
    observation["fonts"] = [
        {"family": "Unused Face", "status": "unloaded", "check": True}
    ]
    observation["images"] = [
        {
            "src": "/below-fold.webp",
            "complete": False,
            "naturalWidth": 0,
            "loading": "lazy",
            "visible": False,
        }
    ]
    observation["media"] = [
        {
            "src": "/below-fold.mp4",
            "readyState": 0,
            "error": None,
            "visible": False,
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )

    assert result["runtime"]["ok"] is True


def test_runtime_rejects_visible_resource_that_is_not_ready():
    observation = _clean(390)
    observation["images"] = [
        {
            "src": "/hero.webp",
            "complete": False,
            "naturalWidth": 0,
            "visible": True,
        }
    ]
    observation["media"] = [
        {
            "src": "/hero.mp4",
            "readyState": 0,
            "error": None,
            "visible": True,
        }
    ]

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )
    codes = [row["code"] for row in result["runtime"]["failures"]]

    assert "broken_image" in codes
    assert "broken_media" in codes


def test_document_horizontal_overflow_fails_with_reachable_scroll_and_offenders():
    observation = _clean(390)
    observation["layout"] = {
        "viewport_width": 390,
        "scroll_width": 674,
        "reachable_scroll_x": 284,
        "offenders": [
            {
                "selector": "nav.desktop-menu",
                "left": 0,
                "right": 674,
                "width": 674,
            }
        ],
    }

    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [observation],
        required_breakpoints=[390],
    )

    assert result["responsive"]["ok"] is False
    failure = result["responsive"]["failures"][0]
    assert failure["code"] == "document_horizontal_overflow"
    assert failure["reachable_scroll_x"] == 284
    assert failure["offenders"][0]["selector"] == "nav.desktop-menu"


def test_missing_required_breakpoint_fails_responsive_gate():
    result = evaluate_runtime_observations(
        "http://127.0.0.1:4173/",
        [_clean(1440)],
        required_breakpoints=[1440, 390],
    )

    assert result["responsive"]["ok"] is False
    assert result["responsive"]["failures"][0] == {
        "code": "missing_breakpoint",
        "breakpoint": 390,
    }


def test_playwright_collector_accepts_real_local_clipped_carousel(tmp_path):
    (tmp_path / "index.html").write_text(
        """<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;overflow-x:clip}
.carousel{width:300px;overflow:hidden}
.track{display:flex;width:900px}
.slide{flex:0 0 300px;height:80px}
</style></head><body>
<div class="carousel"><div class="track">
  <div class="slide">One</div><div class="slide">Two</div>
  <div class="slide">Three</div>
</div></div>
</body></html>""",
        encoding="utf-8",
    )

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, _format, *_args):
            return

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(QuietHandler, directory=str(tmp_path)),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        observations = collect_runtime_observations(
            url,
            [390],
            viewport_height=300,
            settle_ms=20,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    result = evaluate_runtime_observations(
        url,
        observations,
        required_breakpoints=[390],
    )
    assert observations[0]["navigation"]["status"] == 200
    assert observations[0]["layout"]["contained_overflows"]
    assert result["runtime"]["ok"] is True
    assert result["responsive"]["ok"] is True


def test_playwright_collector_handles_variable_font_weight_ranges(tmp_path):
    (tmp_path / "index.html").write_text(
        """<!doctype html>
<html><head><meta charset="utf-8"><style>
@font-face {
  font-family: "Harness Variable";
  src: local("Arial");
  font-weight: 400 800;
}
body { font-family: "Harness Variable", sans-serif; font-weight: 600; }
</style></head><body>Variable font probe</body></html>""",
        encoding="utf-8",
    )

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, _format, *_args):
            return

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(QuietHandler, directory=str(tmp_path)),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        observations = collect_runtime_observations(
            url,
            [390],
            viewport_height=300,
            settle_ms=20,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert observations[0]["navigation"]["status"] == 200
    assert observations[0]["fonts"]
    assert observations[0]["fonts"][0]["check_error"] is None
