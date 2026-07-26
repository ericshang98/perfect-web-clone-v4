"""Fidelity-gate MCP tools for Perfect Web Clone v4.

Deterministic verification that the generated clone kept what the extractor
captured. The first gate here is **real links**: the owning agent must
reproduce the section's real ``href``s, not fabricate ``#`` / ``javascript:``
placeholders. ``verify_links`` reads each generated component from the sandbox
and reports, per section, whether every real navigational link survived — so the
owning agent can repair any section that dropped them.

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
from core.comparison_contract import (
    load_contract,
    save_contract,
    validate_contract,
)
from core.extractor.storage import SourceStore
from core.gates import fidelity, structure as structure_gate
from core.gates.semantic_fidelity import evaluate_contract
from core.iteration_ledger import new_ledger, record_attempt
from core.repair_packet import build_repair_packet


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


def _read_json(path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def _capture_integrity(store: SourceStore) -> Dict[str, Any]:
    try:
        manifest = store.read_manifest()
    except Exception:  # noqa: BLE001
        manifest = None
    return ((manifest.capture_integrity if manifest else {}) or {})


def _reference_raster(store: SourceStore):
    for name in ("primary_full.png", "light_full.png", "dark_full.png"):
        candidate = store.dir / "screenshots" / name
        if candidate.is_file():
            return candidate
    return None


def _contract_path(store: SourceStore):
    return store.dir / "comparison-contract.json"


async def get_comparison_evidence(
    source_id: str,
    max_text_bytes: int = 32_768,
) -> Dict[str, Any]:
    """Return compact source evidence for the Agent's comparison decision.

    This tool suggests likely volatile regions but never classifies them on the
    Agent's behalf. It intentionally omits raw HTML and full CSS payloads.
    """

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    store = SourceStore(source_id)
    if not store.dir.is_dir():
        return _err(
            f"no captured source {source_id!r}; run extract_page first.",
            source_id=source_id,
        )
    integrity = _capture_integrity(store)
    if integrity.get("status") != "passed":
        return _err(
            "source capture integrity is not passed; recapture before classifying.",
            source_id=source_id,
            capture_integrity=integrity or {"status": "unknown"},
        )

    full = _read_json(store.dir / "sections_full.json", {})
    raw = _read_json(store.dir / "evidence" / "raw_structure.json", {})
    volatility = _read_json(
        store.dir / "evidence" / "volatility_summary.json",
        {"schema": 1, "sample_count": 0, "candidates": []},
    )
    interactions = _read_json(store.dir / "interactions.json", {})
    summary = _read_json(store.dir / "summary.json", {})
    sections = [
        {
            "id": section.get("name"),
            "owner": section.get("name"),
            "bounds": section.get("bounds") or {},
            "component_path": section.get("component_path"),
        }
        for section in (full.get("sections") or [])[:64]
    ]
    critical_regions = [
        {
            "id": region.get("fingerprint") or region.get("id"),
            "kind": region.get("kind"),
            "critical": bool(region.get("critical")),
            "bounds": region.get("rect") or region.get("bounds") or {},
        }
        for region in (raw.get("regions") or [])[:64]
        if region.get("critical")
    ]
    result: Dict[str, Any] = {
        "ok": True,
        "source_id": source_id,
        "capture_integrity": integrity,
        "page": raw.get("page")
        or {
            "width": summary.get("page_width"),
            "height": summary.get("page_height"),
        },
        "sections": sections,
        "critical_regions": critical_regions,
        "volatility": {
            "schema": volatility.get("schema", 1),
            "sample_count": volatility.get("sample_count", 0),
            "candidates": list(volatility.get("candidates") or [])[:64],
        },
        "interactions": list(interactions.get("interactions") or [])[:64],
        "reference_raster": (
            str(_reference_raster(store)) if _reference_raster(store) else None
        ),
        "decision_required": (
            "The Agent must classify every important region. Volatility hints "
            "never waive pixels without replacement invariants."
        ),
    }
    budget = max(2_048, int(max_text_bytes))
    for key in ("interactions", "sections", "critical_regions"):
        while len(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        ) > budget and result[key]:
            result[key].pop()
    while (
        len(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )
        > budget
        and result["volatility"]["candidates"]
    ):
        result["volatility"]["candidates"].pop()
    result["text_bytes"] = len(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    return result


async def save_comparison_contract(
    source_id: str,
    contract: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate and persist the Agent-authored semantic comparison contract."""

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    store = SourceStore(source_id)
    if not store.dir.is_dir():
        return _err(
            f"no captured source {source_id!r}; run extract_page first.",
            source_id=source_id,
        )
    errors = validate_contract(contract)
    if errors:
        return _err(
            "invalid comparison contract: " + "; ".join(errors),
            source_id=source_id,
            validation_errors=errors,
        )
    path = _contract_path(store)
    try:
        save_contract(contract, path)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not save comparison contract: {exc}", source_id=source_id)

    sandbox_saved = False
    sb = get_sandbox()
    if sb is not None:
        try:
            sandbox_saved = bool(
                await sb.write_file(
                    ".pwc/comparison-contract.json",
                    path.read_text(encoding="utf-8"),
                )
            )
        except Exception:  # noqa: BLE001
            sandbox_saved = False
    return {
        "ok": True,
        "source_id": source_id,
        "regions": len(contract["regions"]),
        "contract": str(path),
        "sandbox_saved": sandbox_saved,
    }


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
            the owning agent has written the section components).

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
    comparison_regions: Optional[list[Dict[str, Any]]] = None,
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
    capture_kwargs: Dict[str, Any] = {
        "viewport": (int(viewport_width), int(viewport_height)),
        "settle_ms": int(settle_ms),
    }
    if comparison_regions:
        capture_kwargs["comparison_regions"] = comparison_regions
    try:
        result = await anyio.to_thread.run_sync(
            functools.partial(
                clone_capture.capture_clone,
                url,
                out_png,
                **capture_kwargs,
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
    extraction_manifest = store.read_manifest()
    source_integrity = (
        extraction_manifest.capture_integrity if extraction_manifest else {}
    ) or {}
    if source_integrity.get("status") != "passed":
        return _err(
            "source capture integrity is not passed; recapture before scoring.",
            source_id=source_id,
            capture_integrity=source_integrity or {"status": "unknown"},
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
    required_structure = []
    light_plan_path = store.dir / "sections.json"
    if light_plan_path.is_file():
        try:
            required_structure = json.loads(
                light_plan_path.read_text(encoding="utf-8")
            ).get("required_structure", [])
        except Exception:  # noqa: BLE001 — empty falls through to legacy gate.
            required_structure = []

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

    raw_structure_path = store.dir / "evidence" / "raw_structure.json"
    if not raw_structure_path.is_file():
        return _err(
            "immutable raw structure evidence is missing; recapture before scoring.",
            source_id=source_id,
        )
    try:
        raw_structure = json.loads(raw_structure_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return _err(
            f"could not read immutable raw structure evidence: {exc}",
            source_id=source_id,
        )

    cap = await capture_clone_sections(url=url, out_png=out_png)
    if not cap.get("ok"):
        return cap

    match = clone_capture.match_sections(ref_sections, cap["bounds"])
    structure = structure_gate.verify_structure(
        source_regions=raw_structure.get("regions") or [],
        planned_sections=ref_sections,
        candidate_bounds=cap["bounds"],
        source_page_height=(raw_structure.get("page") or {}).get("height")
        or ref_page_height,
        candidate_page_height=cap["page_height"],
        requirements=required_structure,
        candidate_critical_bounds=cap.get("critical_bounds") or {},
    )
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
    result["ok"] = (
        bool(result["ok"])
        and not match["unmatched_ref"]
        and bool(structure.get("ok"))
    )
    result["unmatched_ref"] = match["unmatched_ref"]
    result["unmatched_cand"] = match["unmatched_cand"]
    result["png"] = cap["png"]
    result["ref_png"] = str(ref_png)
    result["url"] = cap["url"]
    result["source_id"] = source_id
    result["capture_integrity"] = source_integrity
    result["structure"] = structure
    return result


async def score_semantic_fidelity(
    source_id: str,
    url: Optional[str] = None,
    threshold: float = fidelity.DEFAULT_THRESHOLD,
    out_png: Optional[str] = None,
) -> Dict[str, Any]:
    """Measure the live clone according to its Agent-authored region contract.

    Raw whole-page SSIM remains diagnostic. Only explicit static pixels or
    replacement invariants decide each region's status.
    """

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    store = SourceStore(source_id)
    contract_path = _contract_path(store)
    if not contract_path.is_file():
        return _err(
            "no comparison contract; call get_comparison_evidence and "
            "save_comparison_contract before scoring.",
            source_id=source_id,
        )
    integrity = _capture_integrity(store)
    if integrity.get("status") != "passed":
        return _err(
            "source capture integrity is not passed; recapture before scoring.",
            source_id=source_id,
            capture_integrity=integrity or {"status": "unknown"},
        )
    ref_png = _reference_raster(store)
    if ref_png is None:
        return _err(
            "no full-page reference raster; re-run extract_page.",
            source_id=source_id,
        )
    try:
        contract = load_contract(contract_path)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read comparison contract: {exc}", source_id=source_id)

    summary = _read_json(store.dir / "summary.json", {})
    viewport = summary.get("viewport") or {}
    width = int(viewport.get("width") or summary.get("page_width") or 1440)
    height = int(viewport.get("height") or 900)
    cap = await capture_clone_sections(
        url=url,
        out_png=out_png,
        viewport_width=width,
        viewport_height=height,
        comparison_regions=contract["regions"],
    )
    if not cap.get("ok"):
        return cap

    effective_contract = json.loads(json.dumps(contract))
    effective_contract.setdefault(
        "ref_page_size",
        [
            float(summary.get("page_width") or width),
            float(summary.get("page_height") or 0),
        ],
    )
    if not effective_contract["ref_page_size"][1]:
        from PIL import Image

        with Image.open(ref_png) as ref_image:
            effective_contract["ref_page_size"] = list(ref_image.size)
    effective_contract["cand_page_size"] = [
        float(cap.get("page_width") or width),
        float(cap.get("page_height") or height),
    ]
    ref_facts = {
        region["id"]: (
            region.get("reference_facts")
            or {"bounds": region.get("bounds") or {}}
        )
        for region in contract["regions"]
    }
    cand_facts = dict(cap.get("comparison_facts") or {})
    for region in contract["regions"]:
        region_id = region["id"]
        if region_id not in cand_facts:
            owner = region["owner"]
            bounds = (
                (cap.get("critical_bounds") or {}).get(region_id)
                or (cap.get("bounds") or {}).get(owner)
            )
            if bounds:
                cand_facts[region_id] = {"bounds": bounds}
    try:
        report = evaluate_contract(
            str(ref_png),
            cap["png"],
            effective_contract,
            ref_facts,
            cand_facts,
            threshold=float(threshold),
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"semantic fidelity scoring failed: {exc}", source_id=source_id)
    report.update(
        {
            "source_id": source_id,
            "url": cap["url"],
            "png": cap["png"],
            "ref_png": str(ref_png),
            "contract": str(contract_path),
            "capture_integrity": integrity,
            "measurement_policy": (
                "whole-page SSIM is diagnostic; region contracts are gating"
            ),
        }
    )
    return report


async def build_semantic_repair_packet(
    source_id: str,
    report: Dict[str, Any],
    max_text_bytes: int = 16_384,
) -> Dict[str, Any]:
    """Build one owner-scoped, token-bounded repair packet for the worst region."""

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    store = SourceStore(source_id)
    path = _contract_path(store)
    if not path.is_file():
        return _err(
            "no comparison contract; save it before building a repair packet.",
            source_id=source_id,
        )
    try:
        contract = load_contract(path)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read comparison contract: {exc}", source_id=source_id)
    sections, section_sources, _page_url, err = await _load_sections_and_sources(
        source_id
    )
    if err:
        return err
    sources: Dict[str, str] = {}
    for section in sections:
        name = section.get("name")
        component_path = section.get("component_path")
        content = section_sources.get(name)
        if component_path and isinstance(content, str):
            sources[component_path] = content
    ledger = _read_json(store.dir / "iteration-ledger.json", {})
    try:
        packet = build_repair_packet(
            report,
            contract,
            sources,
            attempts=list(ledger.get("attempts") or []),
            max_text_bytes=int(max_text_bytes),
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not build semantic repair packet: {exc}", source_id=source_id)
    return {"ok": True, "source_id": source_id, "packet": packet}


async def record_semantic_attempt(
    source_id: str,
    target: str,
    before: float,
    after: float,
    hard_gate_regressions: list[str],
    candidate_path: Optional[str] = None,
    packet_bytes: Optional[int] = None,
    estimated_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """Persist one measured repair attempt and reject non-monotonic candidates."""

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    store = SourceStore(source_id)
    if not store.dir.is_dir():
        return _err(
            f"no captured source {source_id!r}; run extract_page first.",
            source_id=source_id,
        )
    ledger_path = store.dir / "iteration-ledger.json"
    ledger = _read_json(ledger_path, None)
    if not isinstance(ledger, dict):
        ledger = new_ledger()
    for value, name in (
        (packet_bytes, "packet_bytes"),
        (estimated_tokens, "estimated_tokens"),
    ):
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value < 0
        ):
            return _err(
                f"{name} must be a non-negative integer.",
                source_id=source_id,
            )
    previous_attempts = len(ledger.get("attempts") or [])
    result = record_attempt(
        ledger,
        target=target,
        before=before,
        after=after,
        hard_gate_regressions=hard_gate_regressions,
        candidate_path=candidate_path,
    )
    updated_ledger = result["ledger"]
    if len(updated_ledger.get("attempts") or []) > previous_attempts:
        attempt = updated_ledger["attempts"][-1]
        if packet_bytes is not None:
            attempt["packet_bytes"] = packet_bytes
        if estimated_tokens is not None:
            attempt["estimated_tokens"] = estimated_tokens
    ledger_path.write_text(
        json.dumps(updated_ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    sb = get_sandbox()
    if sb is not None:
        try:
            await sb.write_file(
                ".pwc/iteration-ledger.json",
                ledger_path.read_text(encoding="utf-8"),
            )
        except Exception:  # noqa: BLE001
            pass
    return {
        "ok": True,
        "source_id": source_id,
        **{key: value for key, value in result.items() if key != "ledger"},
        "ledger": str(ledger_path),
    }


async def generate_manifest(source_id: str) -> Dict[str, Any]:
    """Generate the per-site state checklist (checklist.json) — M1: baseline states.

    Reads the captured source's url / viewport / page_height from
    ``sections.json`` (url) and ``summary.json`` (viewport + page_height), seeds
    one state per scroll offset (aligned with the multi-state reference rasters),
    and writes ``checklist.json`` into the source dir.

    NOTE: the checklist is written to ``checklist.json``, NOT ``manifest.json``.
    ``manifest.json`` is the extraction metadata file owned by the extractor
    (SourceStore) and must never be overwritten by this tool.

    After building states, calls :func:`core.refs.materialize_refs` to write
    any missing reference rasters so that ``verify_manifest`` can compare
    against them.

    THE IRON RULE: no LLM here — pure filesystem reads + deterministic seeding.

    Returns ``{"ok", "source_id", "states", "checklist", "refs"}`` on success, or
    ``{"ok": False, "error"}`` on a setup failure.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    from core import manifest as mf
    from core.refs import materialize_refs

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

    extraction_manifest = store.read_manifest()
    integrity = (
        extraction_manifest.capture_integrity if extraction_manifest else {}
    ) or {}
    if integrity.get("status") != "passed":
        return _err(
            "source capture integrity is not passed; recapture before generating a checklist.",
            source_id=source_id,
            capture_integrity=integrity or {"status": "unknown"},
        )

    m = mf.new_manifest(meta.get("source_url", ""), [vw])
    for st in mf.baseline_states(page_h, (vw, vh), vw):
        mf.add_state(m, st)
    interactions_path = store.dir / "interactions.json"
    interactions = []
    if interactions_path.is_file():
        try:
            interactions = json.loads(
                interactions_path.read_text(encoding="utf-8")
            ).get("interactions", [])
        except Exception as exc:  # noqa: BLE001
            return _err(
                f"could not read interactions.json: {exc}",
                source_id=source_id,
            )
    for st in mf.interaction_states(interactions, vw):
        mf.add_state(m, st)

    raw_structure_path = store.dir / "evidence" / "raw_structure.json"
    if raw_structure_path.is_file():
        try:
            raw_structure = json.loads(raw_structure_path.read_text(encoding="utf-8"))
            m["structure"] = {
                "critical_regions": [
                    region
                    for region in raw_structure.get("regions", [])
                    if region.get("critical")
                ],
                "page": raw_structure.get("page") or {},
            }
        except Exception as exc:  # noqa: BLE001
            return _err(
                f"could not read raw structure evidence: {exc}",
                source_id=source_id,
            )
    checklist_path = store.dir / "checklist.json"
    mf.save_manifest(m, checklist_path)

    # Materialize reference rasters from captured screenshots (idempotent)
    try:
        refs_summary = materialize_refs(store.dir, page_h, (vw, vh), vw)
    except Exception as exc:  # noqa: BLE001
        refs_summary = {"written": [], "skipped": [], "missing": [], "source": "none",
                        "error": str(exc)}

    return {
        "ok": True,
        "source_id": source_id,
        "states": len(m["states"]),
        "interactions": sum(
            1 for state in m["states"] if state.get("channel") == "interaction"
        ),
        "checklist": str(checklist_path),
        "refs": refs_summary,
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
    mpath = store.dir / "checklist.json"
    if not mpath.is_file():
        return _err(
            f"no checklist for {source_id!r}; run generate_manifest first.",
            source_id=source_id,
        )
    try:
        m = mf.load_manifest(mpath)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not read checklist.json: {exc}", source_id=source_id)

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
        "ok": bool(result["summary"].get("ok")),
        "source_id": source_id,
        **result,
        "report": str(report_path),
    }


__all__ = [
    "verify_links",
    "verify_assets",
    "capture_clone_sections",
    "score_clone_sections",
    "get_comparison_evidence",
    "save_comparison_contract",
    "score_semantic_fidelity",
    "build_semantic_repair_packet",
    "record_semantic_attempt",
    "generate_manifest",
    "verify_manifest",
]
