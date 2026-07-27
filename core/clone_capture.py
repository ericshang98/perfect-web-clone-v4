"""Capture the LIVE CLONE's state for the per-section fidelity gate.

The gate (:func:`core.gates.fidelity.score_by_section`) needs, per section, a
crop from BOTH rasters by that section's own bounds. The reference side comes
from extraction (full-page raster + plan bounds). This module supplies the
candidate side: a full-page raster of the running clone plus each section's
bounds, measured off the ``data-pwc-section`` anchors that assemble_project
emits around every section component.

``match_sections`` is pure; ``capture_clone`` drives headless chromium
(sync Playwright) against the preview URL.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

_BOUNDS_KEYS = ("x", "y", "width", "height")

_MEASURE = """() => {
  const bounds = {};
  const critical_bounds = {};
  document.querySelectorAll('[data-pwc-section]').forEach(el => {
    const r = el.getBoundingClientRect();
    bounds[el.getAttribute('data-pwc-section')] = {
      x: r.x + window.scrollX,
      y: r.y + window.scrollY,
      width: r.width,
      height: r.height,
    };
  });
  document.querySelectorAll('[data-pwc-critical]').forEach(el => {
    const r = el.getBoundingClientRect();
    critical_bounds[el.getAttribute('data-pwc-critical')] = {
      x: r.x + window.scrollX,
      y: r.y + window.scrollY,
      width: r.width,
      height: r.height,
    };
  });
  return {
    bounds,
    critical_bounds,
    page_width: document.documentElement.scrollWidth,
    page_height: document.documentElement.scrollHeight
  };
}"""

_MEASURE_COMPARISON_FACTS = """(regions) => {
  const facts = {};
  const esc = value => {
    if (window.CSS && CSS.escape) return CSS.escape(String(value));
    return String(value).replace(/["\\\\]/g, '\\\\$&');
  };
  const rect = el => {
    const r = el.getBoundingClientRect();
    return {
      x: r.x + window.scrollX,
      y: r.y + window.scrollY,
      width: r.width,
      height: r.height,
    };
  };
  const unique = values => [...new Set(values.filter(Boolean))].sort();
  for (const region of regions || []) {
    let el = null;
    if (region.selector) {
      try { el = document.querySelector(region.selector); } catch (_) {}
    }
    if (!el) {
      el = document.querySelector(
        `[data-pwc-compare="${esc(region.id)}"]`
      );
    }
    if (!el) {
      el = document.querySelector(
        `[data-pwc-critical="${esc(region.id)}"]`
      );
    }
    if (!el && region.owner) {
      el = document.querySelector(
        `[data-pwc-section="${esc(region.owner)}"]`
      );
    }
    if (!el) continue;
    const style = getComputedStyle(el);
    const controls = [];
    if (el.matches('video[controls]')) controls.push('video');
    el.querySelectorAll(
      'button,[role="button"],input,select,textarea,video[controls]'
    ).forEach(control => {
      const label = (
        control.getAttribute('aria-label') ||
        control.getAttribute('data-pwc-control') ||
        control.getAttribute('name') ||
        control.getAttribute('type') ||
        control.getAttribute('role') ||
        control.tagName
      ).trim().toLowerCase();
      if (label) controls.push(label);
    });
    const interactions = [];
    if (el.hasAttribute('data-pwc-interaction')) {
      interactions.push(el.getAttribute('data-pwc-interaction'));
    }
    el.querySelectorAll('[data-pwc-interaction]').forEach(control => {
      interactions.push(control.getAttribute('data-pwc-interaction'));
    });
    facts[region.id] = {
      bounds: rect(el),
      style: {
        display: style.display,
        position: style.position,
        overflow: style.overflow,
        borderRadius: style.borderRadius,
        backgroundColor: style.backgroundColor,
        color: style.color,
      },
      controls: unique(controls),
      interaction: unique(interactions),
    };
  }
  return facts;
}"""


def comparison_fact_request(
    regions: Sequence[Dict[str, Any]] | None,
) -> List[Dict[str, Any]]:
    """Return the bounded selector metadata needed by the browser fact probe."""

    request: List[Dict[str, Any]] = []
    for region in regions or []:
        region_id = str(region.get("id") or "").strip()
        owner = str(region.get("owner") or "").strip()
        if not region_id:
            continue
        selector = region.get("selector")
        behaviors = []
        for behavior in list(region.get("behaviors") or [])[:16]:
            if not isinstance(behavior, dict):
                continue
            if not behavior.get("id") or not behavior.get("trigger"):
                continue
            behaviors.append(
                {
                    key: behavior.get(key)
                    for key in (
                        "id",
                        "before",
                        "trigger",
                        "target",
                        "assert",
                        "attribute",
                        "value",
                    )
                    if behavior.get(key) is not None
                }
            )
            if "before" in behaviors[-1]:
                behaviors[-1]["before"] = [
                    str(selector)
                    for selector in list(behaviors[-1]["before"] or [])[:8]
                    if str(selector).strip()
                ]
        record = {
            "id": region_id,
            "owner": owner,
            "selector": str(selector) if selector else None,
        }
        if behaviors:
            record["behaviors"] = behaviors
        request.append(record)
    return request


def _capture_behavior_facts(
    page,
    url: str,
    request: Sequence[Dict[str, Any]],
    settle_ms: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """Replay bounded click/assert contracts in a fresh page state."""

    results: Dict[str, List[Dict[str, Any]]] = {}
    for region in request:
        rows: List[Dict[str, Any]] = []
        for behavior in region.get("behaviors") or []:
            assertion = str(behavior.get("assert") or "visible")
            row: Dict[str, Any] = {
                "id": str(behavior["id"]),
                "assert": assertion,
                "passed": False,
                "observed": "not-run",
            }
            try:
                page.goto(url, wait_until="networkidle", timeout=60_000)
                page.wait_for_timeout(min(max(int(settle_ms), 0), 2_000))
                for selector in behavior.get("before") or []:
                    page.locator(str(selector)).first.click(timeout=3_000)
                    page.wait_for_timeout(50)
                trigger = page.locator(str(behavior["trigger"])).first
                trigger.click(timeout=3_000)
                page.wait_for_timeout(100)
                target_selector = str(
                    behavior.get("target") or behavior["trigger"]
                )
                target = page.locator(target_selector).first
                if assertion == "visible":
                    visible = target.count() > 0 and target.is_visible()
                    row.update(passed=visible, observed="visible" if visible else "hidden")
                elif assertion == "hidden":
                    hidden = target.count() == 0 or not target.is_visible()
                    row.update(passed=hidden, observed="hidden" if hidden else "visible")
                elif assertion == "attribute_equals":
                    attribute = str(behavior.get("attribute") or "")
                    observed = target.get_attribute(attribute) if target.count() else None
                    expected = behavior.get("value")
                    row.update(passed=observed == expected, observed=observed)
                elif assertion == "text_contains":
                    observed = target.inner_text() if target.count() else ""
                    expected = str(behavior.get("value") or "")
                    row.update(passed=expected in observed, observed=observed[:256])
                else:
                    row["observed"] = f"unsupported assertion: {assertion}"
            except Exception as exc:  # noqa: BLE001
                row["observed"] = f"replay error: {type(exc).__name__}"
            rows.append(row)
        if rows:
            results[str(region["id"])] = rows
    return results


def match_sections(
    ref_sections: Sequence[Dict[str, Any]],
    cand_bounds: Dict[str, Dict[str, float]],
) -> Dict[str, Any]:
    """Pair plan sections with clone measurements into the gate's payload.

    ``ref_sections`` is the extraction plan's ``[{name, bounds}, ...]``;
    ``cand_bounds`` maps ``data-pwc-section`` anchor names to measured bounds.

    Returns ``{sections, unmatched_ref, unmatched_cand}`` where ``sections``
    is ready for ``score_by_section`` ([{name, ref_bounds, cand_bounds}]).
    A ref section with incomplete bounds or no clone measurement is reported
    in ``unmatched_ref`` (never silently dropped); clone anchors unknown to
    the plan land in ``unmatched_cand``.
    """
    ref_names = {rec.get("name") for rec in ref_sections}
    sections: List[Dict[str, Any]] = []
    unmatched_ref: List[str] = []
    for rec in ref_sections:
        name = rec.get("name")
        ref_b = rec.get("bounds") or {}
        cand_b = cand_bounds.get(name)
        if not all(k in ref_b for k in _BOUNDS_KEYS) or not cand_b:
            unmatched_ref.append(name)
            continue
        sections.append({"name": name, "ref_bounds": ref_b, "cand_bounds": cand_b})
    unmatched_cand = [n for n in cand_bounds if n not in ref_names]
    return {
        "sections": sections,
        "unmatched_ref": unmatched_ref,
        "unmatched_cand": unmatched_cand,
    }


def capture_clone(
    url: str,
    out_png: str,
    viewport: Tuple[int, int] = (1440, 900),
    settle_ms: int = 800,
    comparison_regions: Sequence[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Raster the running clone full-page and measure every section anchor.

    ``device_scale_factor=1`` so raster pixels equal CSS pixels — bounds and
    page_height feed ``score_fidelity_by_section`` without DPR conversion.

    Returns ``{png, page_height, bounds: {name: {x, y, width, height}}}``.
    """
    from io import BytesIO

    from PIL import Image
    from playwright.sync_api import sync_playwright
    from core.extractor.dom_scripts import FORCE_LOAD_IMAGES_JS

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": viewport[0], "height": viewport[1]},
            device_scale_factor=1,
        )
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(settle_ms)
        # Full-page screenshots do not automatically scroll through lazy image
        # bands. Force the clone's already-local image URLs to decode so a valid
        # lower-page section is not scored as a black placeholder.
        page.evaluate(FORCE_LOAD_IMAGES_JS)
        # Measure and raster the clone's authored positioning. Converting fixed
        # or sticky elements to static pushes following sections through the
        # document and creates a candidate layout that never existed in either
        # the source or the running clone.
        measured = page.evaluate(_MEASURE)
        request = comparison_fact_request(comparison_regions)
        comparison_facts = page.evaluate(
            _MEASURE_COMPARISON_FACTS,
            request,
        )
        # A full-page screenshot otherwise expands to the document's
        # horizontal scroll width. That silently changes the requested
        # breakpoint when a child overflows on the x-axis and makes the
        # fidelity gate compare a horizontally rescaled candidate against the
        # reference viewport. Keep the raster at the requested CSS width while
        # still capturing the complete document height.
        screenshot = page.screenshot(full_page=True)
        with Image.open(BytesIO(screenshot)) as raster:
            raster.crop(
                (0, 0, min(viewport[0], raster.width), raster.height)
            ).save(out_png)
        behavior_facts = _capture_behavior_facts(page, url, request, settle_ms)
        for region_id, rows in behavior_facts.items():
            comparison_facts.setdefault(region_id, {})["behavior"] = rows
        browser.close()

    return {
        "png": out_png,
        "page_width": float(viewport[0]),
        "document_width": float(measured["page_width"]),
        "page_height": float(measured["page_height"]),
        "bounds": measured["bounds"],
        "critical_bounds": measured["critical_bounds"],
        "comparison_facts": comparison_facts,
    }


__all__ = ["match_sections", "comparison_fact_request", "capture_clone"]
