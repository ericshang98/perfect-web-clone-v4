# tests/test_trigger_replay.py
"""core.trigger_replay — the tiny replayable trigger vocabulary (spec §3).

Triggers must replay deterministically on BOTH original and clone; anything
outside the vocabulary is a residual by definition. Pure validation always
runs; the Playwright executor follows the repo's RUN_LIVE=1 convention.
"""
import os

import pytest

from core.trigger_replay import replay_triggers, validate_triggers


def test_validate_ok_for_full_vocabulary():
    assert validate_triggers([
        {"kind": "scroll", "y": 100},
        {"kind": "hover", "target": ".card"},
        {"kind": "click", "target": ".dot"},
        {"kind": "wait", "ms": 50},
        {"kind": "viewport", "width": 375, "height": 667},
    ]) == []


def test_validate_reports_unknown_kind_and_missing_field():
    errs = validate_triggers([{"kind": "swipe"}, {"kind": "scroll"}])
    assert len(errs) == 2


@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="RUN_LIVE=1 only")
def test_replay_scroll_click_on_local_fixture(tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    fixture = tmp_path / "page.html"
    fixture.write_text(
        "<body style='margin:0'><div style='height:3000px'></div>"
        "<button id='b' onclick=\"this.textContent='clicked'\">go</button></body>",
        encoding="utf-8")
    with playwright.sync_playwright() as p:
        page = p.chromium.launch().new_page(viewport={"width": 800, "height": 600})
        page.goto(fixture.as_uri())
        replay_triggers(page, [
            {"kind": "scroll", "y": 1200},
            {"kind": "click", "target": "#b"},
            {"kind": "wait", "ms": 20},
        ])
        assert page.evaluate("window.scrollY") == 1200
        assert page.text_content("#b") == "clicked"
