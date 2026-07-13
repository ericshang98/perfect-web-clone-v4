"""Fidelity-gate MCP tools for Perfect Web Clone v3.

Deterministic verification that the generated clone kept what the extractor
captured. The first gate here is **real links**: a section sub-agent must
reproduce the section's real ``href``s, not fabricate ``#`` / ``javascript:``
placeholders. ``verify_links`` reads each generated component from the sandbox
and reports, per section, whether every real navigational link survived — so the
orchestrator can re-dispatch any section that dropped them.

THE IRON RULE: no LLM here. This is filesystem reads + string checks (the
matching/aggregation logic lives in ``core.link_verifier``). All judgement
belongs to Claude Code.
"""

from __future__ import annotations

import functools
import json
import os
import tempfile
from typing import Any, Dict, Optional

import anyio

from core import asset_verifier, clone_capture, link_verifier
from core.boxlite import get_sandbox
from core.extractor.storage import SourceStore
from core.gates import fidelity


def _err(message: str, **extra: Any) -> Dict[str, Any]:
    return {"ok": False, "error": message, **extra}


def _load_page_url(store: SourceStore) -> str:
    """Best-effort page URL (for skipping same-page self/anchor links)."""
    sj = store.dir / "sections.json"
    if sj.is_file():
        try:
            return json.loads(sj.read_text(encoding="utf-8")).get("source_url", "") or ""
        except Exception:  # noqa: BLE001
            return ""
    return ""


async def _load_sections_and_sources(source_id: str):
    """Shared loader for the fidelity gates.

    Returns ``(sections, sources, page_url, None)`` on success, or
    ``(None, None, None, error_dict)`` on a setup failure. ``sources`` maps each
    section name to its generated component text (or ``None`` if unreadable).
    """
    store = SourceStore(source_id)
    full_path = store.dir / "sections_full.json"
    if not full_path.is_file():
        return None, None, None, _err(
            f"no section data for {source_id!r}; run get_section_plan first.",
            source_id=source_id,
        )
    try:
        sections = json.loads(full_path.read_text(encoding="utf-8")).get("sections", [])
    except Exception as exc:  # noqa: BLE001
        return None, None, None, _err(f"could not read section data: {exc}", source_id=source_id)

    sb = get_sandbox()
    if sb is None:
        return None, None, None, _err(
            "No sandbox exists yet; create the sandbox and assemble the project "
            "before verifying.",
            source_id=source_id,
        )

    sources: Dict[str, Any] = {}
    for sec in sections:
        name = sec.get("name")
        cp = sec.get("component_path")
        if not cp:
            sources[name] = None
            continue
        try:
            sources[name] = await sb.read_file(cp)
        except Exception:  # noqa: BLE001
            sources[name] = None
    return sections, sources, _load_page_url(store), None


async def verify_assets(source_id: str) -> Dict[str, Any]:
    """Verify each section uses the DOWNLOADED local assets, not hotlinks.

    After localization, an image with a local copy must be referenced by its
    ``/assets/...`` path. This reads each generated component and reports sections
    that still hotlink the CDN (when a local copy exists) or dropped the image.

    Returns ``{"ok", "source_id", "section_count", "passed", "failing",
    "unreadable", "summary"}``. ``failing`` entries carry ``hotlinked`` (remote
    URLs still used) and ``missing`` (local paths not referenced) — re-dispatch
    those sections. On setup errors: ``{"ok": False, "error"}``.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    sections, sources, _page_url, err = await _load_sections_and_sources(source_id)
    if err:
        return err

    result = asset_verifier.verify_sections_assets(sections, sources)
    result["source_id"] = source_id
    result["summary"] = (
        f"{len(result['passed'])}/{result['section_count']} sections use local assets"
        + (
            f"; {len(result['failing'])} hotlinking/missing, "
            f"{len(result['unreadable'])} unreadable"
            if not result["ok"]
            else ""
        )
    )
    return result


async def verify_links(source_id: str) -> Dict[str, Any]:
    """Verify every section kept its real links in the generated component.

    Loads the persisted section data for ``source_id``, reads each section's
    component from the sandbox, and checks the real ``href``s survived.

    Args:
        source_id: The id from ``extract_page`` (after ``get_section_plan`` and
            the section sub-agents have written their components).

    Returns:
        ``{"ok", "source_id", "section_count", "passed", "failing",
        "unreadable", "summary"}``. ``ok`` is true only when nothing is failing
        or unreadable. ``failing`` / ``unreadable`` list the sections to
        re-dispatch (each with ``name`` and ``component_path``); ``failing``
        entries also carry ``missing`` (the real link URLs that were dropped)
        and ``placeholder_count``. On setup errors: ``{"ok": False, "error"}``.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    sections, sources, page_url, err = await _load_sections_and_sources(source_id)
    if err:
        return err

    result = link_verifier.verify_sections(sections, sources, page_url=page_url or None)
    result["source_id"] = source_id
    ok_n = len(result["passed"])
    total = result["section_count"]
    result["summary"] = (
        f"{ok_n}/{total} sections preserved all real links"
        + (
            f"; {len(result['failing'])} failing, {len(result['unreadable'])} unreadable"
            if not result["ok"]
            else ""
        )
    )
    return result


async def capture_clone_sections(
    url: Optional[str] = None,
    out_png: Optional[str] = None,
    viewport_width: int = 1440,
    viewport_height: int = 900,
    settle_ms: int = 800,
) -> Dict[str, Any]:
    """Capture the LIVE clone: full-page raster + per-section anchor bounds.

    Rasters the running clone (default: the sandbox preview URL) full-page and
    measures every ``data-pwc-section`` anchor that ``assemble_project`` wraps
    around section components. This is the candidate half of the per-section
    fidelity gate; feed the result to ``score_clone_sections`` (or pair bounds
    yourself and call ``score_fidelity_by_section``).

    Playwright here is sync (validated capture path), so it runs on a worker
    thread — never on this server's event loop.

    Returns ``{"ok", "url", "png", "page_height", "bounds": {name: {x, y,
    width, height}}}`` (CSS px, DPR=1), or ``{"ok": False, "error"}``.
    """
    if not url:
        sb = get_sandbox()
        state = getattr(sb, "state", None) if sb is not None else None
        url = getattr(state, "preview_url", None) if state is not None else None
    if not url:
        return _err(
            "no url to capture: pass url explicitly or run start_preview first."
        )
    if not out_png:
        fd, out_png = tempfile.mkstemp(prefix="pwc4-clone-", suffix=".png")
        os.close(fd)
    try:
        result = await anyio.to_thread.run_sync(
            functools.partial(
                clone_capture.capture_clone,
                url,
                out_png,
                viewport=(int(viewport_width), int(viewport_height)),
                settle_ms=int(settle_ms),
            )
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"capture_clone failed: {exc}", url=url)
    return {"ok": True, "url": url, **result}


async def score_clone_sections(
    source_id: str,
    url: Optional[str] = None,
    threshold: float = fidelity.DEFAULT_THRESHOLD,
    out_png: Optional[str] = None,
) -> Dict[str, Any]:
    """One-shot per-section fidelity: capture the live clone and score it (R4).

    Loads the extraction plan's per-section ``bounds`` + full-page reference
    raster for ``source_id``, captures the running clone via
    ``capture_clone_sections``, pairs ref/cand bounds by section name, and
    scores each section on its own crop (height-independent SSIM).

    ``sections`` in the result is sorted **worst-first** — repair the first
    entry, rebuild, and call this again; loop until ``ok``. ``unmatched_ref``
    lists plan sections the clone never measured (a dropped section fails the
    gate); ``unmatched_cand`` lists clone anchors unknown to the plan
    (informational).

    Returns ``{"ok", "score", "threshold", "graded", "ungraded", "sections",
    "unmatched_ref", "unmatched_cand", "png", "ref_png", "url", "source_id"}``,
    or ``{"ok": False, "error"}`` on a setup/capture failure.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    store = SourceStore(source_id)
    full_path = store.dir / "sections_full.json"
    if not full_path.is_file():
        return _err(
            f"no section data for {source_id!r}; run get_section_plan first.",
            source_id=source_id,
        )
    try:
        ref_sections = json.loads(full_path.read_text(encoding="utf-8")).get(
            "sections", []
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read section data: {exc}", source_id=source_id)

    ref_png: Optional[Any] = None
    for name in ("primary_full.png", "light_full.png", "dark_full.png"):
        p = store.dir / "screenshots" / name
        if p.is_file():
            ref_png = p
            break
    if ref_png is None:
        return _err(
            "no full-page reference raster in screenshots/ "
            "(primary_full.png); re-run extract_page.",
            source_id=source_id,
        )

    # Reference CSS page height: summary.json when present; otherwise the
    # raster's own pixel height (extraction rasters are DPR=1).
    ref_page_height: Optional[float] = None
    summary_path = store.dir / "summary.json"
    if summary_path.is_file():
        try:
            ref_page_height = json.loads(
                summary_path.read_text(encoding="utf-8")
            ).get("page_height")
        except Exception:  # noqa: BLE001
            ref_page_height = None
    if not ref_page_height:
        from PIL import Image

        with Image.open(ref_png) as im:
            ref_page_height = float(im.height)

    cap = await capture_clone_sections(url=url, out_png=out_png)
    if not cap.get("ok"):
        return cap

    match = clone_capture.match_sections(ref_sections, cap["bounds"])
    try:
        result = fidelity.score_by_section(
            str(ref_png),
            cap["png"],
            match["sections"],
            float(ref_page_height),
            float(cap["page_height"]),
            threshold=threshold,
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"score_by_section failed: {exc}", source_id=source_id)

    # Worst-first so the agent always repairs sections in priority order.
    result["sections"] = sorted(
        result["sections"],
        key=lambda r: (
            0 if r.get("graded") else 1,
            r["score"] if r.get("score") is not None else 1.0,
        ),
    )
    # A plan section the clone never measured is a dropped/renamed section —
    # that must fail the gate, not silently vanish from the aggregate.
    result["ok"] = bool(result["ok"]) and not match["unmatched_ref"]
    result["unmatched_ref"] = match["unmatched_ref"]
    result["unmatched_cand"] = match["unmatched_cand"]
    result["png"] = cap["png"]
    result["ref_png"] = str(ref_png)
    result["url"] = cap["url"]
    result["source_id"] = source_id
    return result


async def generate_manifest(source_id: str) -> Dict[str, Any]:
    """Generate the per-site state checklist (manifest.json) — M1: baseline states.

    Reads the captured source's url / viewport / page_height from
    ``sections.json`` (url) and ``summary.json`` (viewport + page_height), seeds
    one state per scroll offset (aligned with the multi-state reference rasters),
    and writes ``manifest.json`` into the source dir.

    THE IRON RULE: no LLM here — pure filesystem reads + deterministic seeding.

    Returns ``{"ok", "source_id", "states", "manifest"}`` on success, or
    ``{"ok": False, "error"}`` on a setup failure.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    from core import manifest as mf

    store = SourceStore(source_id)
    sj = store.dir / "sections.json"
    if not sj.is_file():
        return _err(
            f"no captured source {source_id!r}; run extract_page first.",
            source_id=source_id,
        )
    try:
        meta = json.loads(sj.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read sections.json: {exc}", source_id=source_id)

    # viewport + page_height live in summary.json, not sections.json
    vw, vh = 1440, 900
    page_h: float = 0.0
    summary_path = store.dir / "summary.json"
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            vp = summary.get("viewport") or {}
            vw = int(vp.get("width", 1440))
            vh = int(vp.get("height", 900))
            page_h = float(summary.get("page_height") or 0)
        except Exception:  # noqa: BLE001
            pass

    if page_h <= 0:
        return _err(
            "source has no page_height in summary.json; "
            "re-extract with current harness.",
            source_id=source_id,
        )

    m = mf.new_manifest(meta.get("source_url", ""), [vw])
    for st in mf.baseline_states(page_h, (vw, vh), vw):
        mf.add_state(m, st)
    mf.save_manifest(m, store.dir / "manifest.json")
    return {
        "ok": True,
        "source_id": source_id,
        "states": len(m["states"]),
        "manifest": str(store.dir / "manifest.json"),
    }


async def verify_manifest(source_id: str, url: str) -> Dict[str, Any]:
    """Replay the checklist on the live clone and reconcile it (spec §6).

    Requires ``generate_manifest`` to have run first (manifest.json must exist).
    Drives the Playwright trigger-replay loop in a worker thread (sync Playwright
    path — same pattern as ``capture_clone_sections``), then writes statuses back
    into manifest.json and renders report.html beside it.

    Returns ``{"ok", "source_id", "states", "summary", "report"}`` on success,
    or ``{"ok": False, "error"}`` on a setup failure.

    THE IRON RULE: no LLM here — replay + raster + SSIM + bookkeeping only.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    if not url:
        return _err(
            "no url to verify: pass url explicitly or run start_preview first."
        )

    from core.gates import manifest_gate
    from core import manifest as mf
    from core.manifest_report import render_report

    store = SourceStore(source_id)
    mpath = store.dir / "manifest.json"
    if not mpath.is_file():
        return _err(
            f"no manifest for {source_id!r}; run generate_manifest first.",
            source_id=source_id,
        )
    try:
        m = mf.load_manifest(mpath)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read manifest.json: {exc}", source_id=source_id)

    out_dir = store.dir / "manifest_out"

    def _run():
        return manifest_gate.verify_manifest(m, url, store.dir, out_dir)

    try:
        result = await anyio.to_thread.run_sync(_run)
    except Exception as exc:  # noqa: BLE001
        return _err(f"verify_manifest failed: {exc}", source_id=source_id)

    mf.save_manifest(m, mpath)
    report_path = store.dir / "report.html"
    render_report(m, result["states"], result["summary"], report_path)
    return {
        "ok": True,
        "source_id": source_id,
        **result,
        "report": str(report_path),
    }


__all__ = [
    "verify_links",
    "verify_assets",
    "capture_clone_sections",
    "score_clone_sections",
    "generate_manifest",
    "verify_manifest",
]
