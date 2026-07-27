"""Real-browser integration for stateful semantic visual evidence."""

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from core.gates.semantic_fidelity import evaluate_contract
from core.visual_state_capture import capture_visual_state_views


HTML = b"""<!doctype html><html><head><style>
html,body{margin:0;font:16px sans-serif}
.region{box-sizing:border-box;width:300px;height:100px;padding:8px;border:1px solid #333}
#menu-panel[hidden]{display:none}
.spacer{height:1000px}
</style></head><body>
<section class="region" data-pwc-compare="menu-region">
  <button data-pwc-interaction="menu">Menu</button>
  <nav id="menu-panel" data-pwc-controlled="menu" hidden>Navigation</nav>
</section>
<section class="region" data-pwc-compare="faq-region">
  <details><summary data-pwc-interaction="faq">FAQ</summary>
    <p data-pwc-controlled="faq">Answer</p>
  </details>
</section>
<div class="spacer"></div>
<footer>Bottom</footer>
<script>
if (location.pathname !== '/broken') {
  const button = document.querySelector('[data-pwc-interaction="menu"]');
  const panel = document.querySelector('#menu-panel');
  button.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    button.setAttribute('aria-expanded', String(!panel.hidden));
  });
}
</script></body></html>"""


def _regions():
    return [
        {
            "id": "menu-region",
            "owner": "menu",
            "importance": "critical",
            "mode": "layout_behavior",
            "selector": '[data-pwc-compare="menu-region"]',
            "bounds": {"x": 0, "y": 0, "width": 300, "height": 100},
            "compare": [
                "bounds",
                "aspect_ratio",
                "container_style",
                "behavior",
            ],
            "reason": "menu state is validated after deterministic replay",
            "ignore_observations": ["transition_frame"],
            "behaviors": [
                {
                    "id": "menu-opens",
                    "trigger": '[data-pwc-interaction="menu"]',
                    "target": "#menu-panel",
                    "assert": "visible",
                }
            ],
        },
        {
            "id": "faq-region",
            "owner": "faq",
            "importance": "important",
            "mode": "layout_behavior",
            "selector": '[data-pwc-compare="faq-region"]',
            "bounds": {"x": 0, "y": 100, "width": 300, "height": 100},
            "compare": [
                "bounds",
                "aspect_ratio",
                "container_style",
                "behavior",
            ],
            "reason": "accordion state is validated after deterministic replay",
            "ignore_observations": ["transition_frame"],
            "behaviors": [
                {
                    "id": "faq-opens",
                    "trigger": '[data-pwc-interaction="faq"]',
                    "target": '[data-pwc-controlled="faq"]',
                    "assert": "visible",
                }
            ],
        },
    ]


def _views():
    bounds = {"x": 0, "y": 0, "width": 480, "height": 360}
    return [
        {
            "id": "b480:menu",
            "breakpoint": 480,
            "state": {
                "channel": "interaction",
                "trigger": [
                    {"kind": "click", "target": '[data-pwc-interaction="menu"]'}
                ],
                "expect": {"bounds": bounds},
            },
        },
        {
            "id": "b480:faq",
            "breakpoint": 480,
            "state": {
                "channel": "interaction",
                "trigger": [
                    {"kind": "click", "target": '[data-pwc-interaction="faq"]'}
                ],
                "expect": {"bounds": bounds},
            },
        },
        {
            "id": "b480:scroll-700",
            "breakpoint": 480,
            "state": {
                "channel": "baseline",
                "trigger": [{"kind": "scroll", "y": 700}],
                "expect": {
                    "bounds": {**bounds, "y": 700},
                },
            },
        },
    ]


def test_real_menu_accordion_and_scroll_states_are_measured_and_fail_closed(
    tmp_path,
):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(HTML)))
            self.end_headers()
            self.wfile.write(HTML)

        def log_message(self, *_args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        views = _views()
        regions = _regions()
        good = capture_visual_state_views(
            base + "/", views[:2], regions, tmp_path / "good"
        )
        good.update(
            capture_visual_state_views(
                base + "/", views[2:], [], tmp_path / "scroll"
            )
        )
        broken = capture_visual_state_views(
            base + "/broken", views[:1], regions, tmp_path / "broken"
        )

        assert set(good) == {view["id"] for view in views}
        assert all("error" not in row for row in good.values())
        for row in good.values():
            png = Path(row["png"])
            expected = "sha256:" + hashlib.sha256(png.read_bytes()).hexdigest()
            assert row["png_digest"] == expected
            assert expected.removeprefix("sha256:") in png.name
        assert good["b480:scroll-700"]["scroll_y"] == 700
        assert good["b480:menu"]["facts"]["menu-region"]["behavior"] == [
            {
                "id": "menu-opens",
                "assert": "visible",
                "passed": True,
            }
        ]
        assert good["b480:faq"]["facts"]["faq-region"]["behavior"] == [
            {
                "id": "faq-opens",
                "assert": "visible",
                "passed": True,
            }
        ]

        contract = {"schema": 1, "regions": regions}
        passing = evaluate_contract(
            good["b480:menu"]["png"],
            good["b480:menu"]["png"],
            contract,
            good["b480:menu"]["facts"],
            good["b480:menu"]["facts"],
        )
        failing = evaluate_contract(
            good["b480:menu"]["png"],
            broken["b480:menu"]["png"],
            contract,
            good["b480:menu"]["facts"],
            broken["b480:menu"]["facts"],
        )

        assert passing["ok"] is True, [
            (row["id"], row["failed_invariants"], row.get("measurements"))
            for row in passing["regions"]
        ]
        assert failing["ok"] is False
        menu = next(row for row in failing["regions"] if row["id"] == "menu-region")
        assert "behavior" in menu["failed_invariants"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
