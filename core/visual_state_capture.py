"""Browser-owned candidate screenshots/facts for every checklist view."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.clone_capture import _MEASURE_COMPARISON_FACTS, comparison_fact_request
from core.trigger_replay import replay_triggers


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:120] or "view"


def _local_bounds(facts: Mapping[str, Any], scroll_y: float) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for region_id, fact in facts.items():
        if not isinstance(fact, Mapping):
            continue
        normalized = dict(fact)
        bounds = fact.get("bounds")
        if isinstance(bounds, Mapping):
            local = dict(bounds)
            try:
                local["y"] = float(local.get("y", 0)) - scroll_y
            except (TypeError, ValueError):
                pass
            normalized["bounds"] = local
        result[str(region_id)] = normalized
    return result


def _behavior_facts_for_view(browser, url: str, state: Mapping[str, Any], request, width: int, height: int, settle_ms: int):
    """Replay each bounded semantic behavior from the same checklist state."""

    results: dict[str, list[dict[str, Any]]] = {}
    for region in request:
        rows: list[dict[str, Any]] = []
        for behavior in region.get("behaviors") or []:
            page = None
            assertion = str(behavior.get("assert") or "visible")
            row: dict[str, Any] = {"id": str(behavior["id"]), "assert": assertion, "passed": False}
            try:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.goto(url, wait_until="networkidle", timeout=60_000)
                # A semantic behavior has its own bounded prerequisite
                # sequence. Replaying the surrounding checklist trigger here
                # would double-toggle menus/accordions in their named view and
                # turn a working control into a false failure.
                for selector in behavior.get("before") or []:
                    page.dispatch_event(str(selector), "click", timeout=5_000)
                page.dispatch_event(str(behavior["trigger"]), "click", timeout=5_000)
                page.wait_for_timeout(max(0, min(int(settle_ms), 2_000)))
                target = page.locator(str(behavior.get("target") or behavior["trigger"])).first
                if assertion == "visible":
                    row["passed"] = target.count() > 0 and target.is_visible()
                elif assertion == "hidden":
                    row["passed"] = target.count() == 0 or not target.is_visible()
                elif assertion == "attribute_equals":
                    row["passed"] = target.get_attribute(str(behavior.get("attribute") or "")) == behavior.get("value")
                elif assertion == "text_contains":
                    row["passed"] = str(behavior.get("value") or "") in (target.inner_text() if target.count() else "")
                else:
                    row["error"] = "unsupported assertion"
            except Exception as exc:  # noqa: BLE001 -- evidence stays fail-closed
                row["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
            finally:
                if page is not None:
                    page.close()
            rows.append(row)
        if rows:
            results[str(region["id"])] = rows
    return results


def capture_visual_state_views(
    url: str,
    source_views: Sequence[Mapping[str, Any]],
    regions: Sequence[Mapping[str, Any]],
    out_dir: str | Path,
    *,
    settle_ms: int = 400,
) -> dict[str, dict[str, Any]]:
    """Replay each source checklist state and save one candidate viewport PNG.

    This is intentionally browser-owned.  The Agent supplies no measurement
    result: it only authored the compact region contract used by the browser
    fact probe.  A failed replay is returned as that view's evidence rather
    than aborting sibling breakpoints.
    """

    from playwright.sync_api import sync_playwright

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    request = comparison_fact_request(regions)
    captured: dict[str, dict[str, Any]] = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for view in source_views:
                view_id = str(view.get("id") or "")
                state = view.get("state") or {}
                bounds = (state.get("expect") or {}).get("bounds") or {}
                try:
                    width = int(bounds.get("width") or view.get("breakpoint"))
                    height = int(bounds.get("height") or 900)
                except (TypeError, ValueError):
                    captured[view_id] = {"error": "invalid_viewport"}
                    continue
                page = None
                try:
                    page = browser.new_page(
                        viewport={"width": width, "height": height},
                        device_scale_factor=1,
                    )
                    page.goto(url, wait_until="networkidle", timeout=60_000)
                    replay_triggers(page, list(state.get("trigger") or []))
                    page.wait_for_timeout(max(0, min(int(settle_ms), 2_000)))
                    png_bytes = page.screenshot()
                    png_hex = hashlib.sha256(png_bytes).hexdigest()
                    shot = output / f"{_safe_name(view_id)}.{png_hex}.png"
                    # Content-addressed evidence is immutable: the same bytes
                    # reuse the same file, while a changed render can never
                    # overwrite evidence from a prior score.
                    if not shot.exists():
                        shot.write_bytes(png_bytes)
                    scroll_y = float(page.evaluate("window.scrollY"))
                    facts = page.evaluate(_MEASURE_COMPARISON_FACTS, request)
                    behaviors = _behavior_facts_for_view(
                        browser, url, state, request, width, height, settle_ms
                    )
                    for region_id, rows in behaviors.items():
                        facts.setdefault(region_id, {})["behavior"] = rows
                    captured[view_id] = {
                        "png": str(shot),
                        "png_digest": f"sha256:{png_hex}",
                        "facts": _local_bounds(facts if isinstance(facts, dict) else {}, scroll_y),
                        "scroll_y": scroll_y,
                    }
                except Exception as exc:  # noqa: BLE001 -- per view is fail-closed evidence
                    captured[view_id] = {
                        "error": f"{type(exc).__name__}: {str(exc)[:240]}"
                    }
                finally:
                    if page is not None:
                        page.close()
        finally:
            browser.close()
    return captured


__all__ = ["capture_visual_state_views"]
