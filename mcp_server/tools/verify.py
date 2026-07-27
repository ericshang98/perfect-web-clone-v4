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

import base64
import functools
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import anyio
from PIL import Image

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
from core.repair_packet import build_repair_packet, select_worst_region
from core.run_controller import (
    apply_semantic_report,
    authorize_stop,
    finalize_run_state,
    harness_decision,
    semantic_objective,
    semantic_report_digest,
    semantic_report_payload,
    stale_attempt_gates,
    start_repair_epoch,
    synchronize_stop_conditions,
)
from core.visual_state_gate import (
    POLICY_VERSION as VISUAL_POLICY_VERSION,
    evaluate_visual_state_reports,
    validate_contract_coverage,
)
from mcp_server.run_ledger import require_owned_preview_url


_SOURCE_MARKER = ".pwc/source-id"
_RUN_LEDGER = ".pwc/run.json"
_SEMANTIC_REPORT = ".pwc/semantic-report.json"
_SOURCE_SEMANTIC_REPORT = "latest-semantic-report.json"
_PROJECT_SNAPSHOT_EXCLUDED_ROOTS = {
    ".git",
    ".next",
    ".pwc",
    "build",
    "coverage",
    "dist",
    "manifest_out",
    "node_modules",
}
_REQUIRED_SOURCE_BREAKPOINTS = (1440, 390)


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


def _view_id(breakpoint: int, state_id: str) -> str:
    return f"b{int(breakpoint)}:{state_id}"


def _rect(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None
    try:
        rect = {
            key: float(value.get(key, 0))
            for key in ("x", "y", "width", "height")
        }
    except (TypeError, ValueError):
        return None
    return rect if rect["width"] > 0 and rect["height"] > 0 else None


def _view_visible_regions(
    regions: Any,
    *,
    viewport_y: float,
    viewport_height: float,
    state_scoped: bool = False,
) -> list[dict[str, Any]]:
    """Return source-critical owners intersecting this checklist view.

    Per-breakpoint evidence is the authority.  A critical region outside a
    scroll state is not silently graded from that state's raster; it is covered
    by the state where it is actually observable.
    """

    visible: list[dict[str, Any]] = []
    for raw in regions or []:
        if not isinstance(raw, dict):
            continue
        region_id = str(raw.get("fingerprint") or raw.get("id") or "").strip()
        owner = str(raw.get("owner") or raw.get("section") or region_id).strip()
        bounds = _rect(raw.get("rect") or raw.get("bounds"))
        if not region_id or not owner or bounds is None:
            continue
        position = str(raw.get("position") or "").strip().lower()
        if state_scoped:
            # State-local inventory stores the element's actual document-space
            # rectangle at this scroll stop.  Subtracting the measured scroll
            # yields the real viewport coordinate for fixed/sticky insets and
            # container-bound sticky release points.
            local_y = bounds["y"] - viewport_y
            if local_y + bounds["height"] <= 0 or local_y >= viewport_height:
                continue
        elif position == "fixed":
            local_y = bounds["y"]
            if local_y + bounds["height"] <= 0 or local_y >= viewport_height:
                continue
        elif position == "sticky":
            natural_y = bounds["y"] - viewport_y
            if natural_y >= viewport_height:
                continue
            # The inventory stores the element's initial document rectangle.
            # Once scrolled past it, a common top-sticky element remains at the
            # viewport edge instead of disappearing from required coverage.
            local_y = max(0.0, natural_y)
        else:
            if (
                bounds["y"] + bounds["height"] <= viewport_y
                or bounds["y"] >= viewport_y + viewport_height
            ):
                continue
            local_y = bounds["y"] - viewport_y
        local_bounds = dict(bounds)
        local_bounds["y"] = local_y
        visible.append(
            {
                "id": region_id,
                "owner": owner,
                "bounds": local_bounds,
                "critical": bool(raw.get("critical")),
                "position": position or None,
            }
        )
    return visible


def _bounded_source_region_universe(
    groups: list[tuple[str, int, list[dict[str, Any]]]],
    *,
    limit: int = 64,
) -> list[dict[str, Any]]:
    """Select one deterministic, cross-state region universe.

    Critical regions are never silently truncated. Remaining slots are filled
    round-robin across breakpoint/state groups so a large desktop rest-state
    inventory cannot crowd out mobile-only or interaction-only content.
    """

    merged: dict[str, dict[str, Any]] = {}
    ids_by_group: list[list[str]] = []
    for group_id, breakpoint, regions in groups:
        group_ids: list[str] = []
        for raw in regions[:64]:
            if not isinstance(raw, dict):
                continue
            region_id = str(raw.get("fingerprint") or raw.get("id") or "").strip()
            if not region_id:
                continue
            owner = str(
                raw.get("owner") or raw.get("section") or region_id
            ).strip()
            bounds = _rect(raw.get("rect") or raw.get("bounds"))
            if not owner or bounds is None:
                continue
            entry = merged.setdefault(
                region_id,
                {
                    "id": region_id,
                    "owner": owner,
                    "kind": str(raw.get("kind") or "section")[:40],
                    "position": str(raw.get("position") or "static")[:24],
                    "critical": False,
                    "signals": dict(raw.get("signals") or {}),
                    "breakpoints": [],
                    "states": [],
                    "bounds_by_breakpoint": {},
                    "bounds": bounds,
                },
            )
            entry["critical"] = bool(entry["critical"] or raw.get("critical"))
            if breakpoint not in entry["breakpoints"]:
                entry["breakpoints"].append(breakpoint)
            # State membership is diagnostic context, not the acceptance
            # contract. Keep only two representative state IDs so a page with
            # many interaction states cannot inflate the Agent prompt.
            if group_id not in entry["states"] and len(entry["states"]) < 2:
                entry["states"].append(group_id)
            entry["bounds_by_breakpoint"].setdefault(str(breakpoint), bounds)
            if region_id not in group_ids:
                group_ids.append(region_id)
        ids_by_group.append(group_ids)

    critical_ids = sorted(
        region_id
        for region_id, entry in merged.items()
        if entry.get("critical")
    )
    if len(critical_ids) > limit:
        raise ValueError(
            f"source exposes {len(critical_ids)} critical regions; bounded "
            f"contract limit is {limit}"
        )
    selected = list(critical_ids)
    selected_set = set(selected)
    offsets = [0] * len(ids_by_group)
    while len(selected) < limit:
        progressed = False
        for group_index, group_ids in enumerate(ids_by_group):
            while offsets[group_index] < len(group_ids):
                region_id = group_ids[offsets[group_index]]
                offsets[group_index] += 1
                if region_id in selected_set:
                    continue
                selected.append(region_id)
                selected_set.add(region_id)
                progressed = True
                break
            if len(selected) >= limit:
                break
        if not progressed:
            break
    return [merged[region_id] for region_id in selected]


def _source_visual_views(store: SourceStore) -> tuple[list[dict[str, Any]], str | None]:
    """Read canonical required views from the source-owned checklist evidence."""

    checklist = _read_json(store.dir / "checklist.json", None)
    if not isinstance(checklist, dict) or not isinstance(checklist.get("states"), list):
        return [], "no generated checklist; run generate_manifest before visual scoring"
    structures = checklist.get("structure_by_breakpoint")
    if not isinstance(structures, dict):
        return [], "checklist lacks breakpoint-scoped source structure evidence; re-extract and generate_manifest"
    universe = checklist.get("source_region_universe")
    if not isinstance(universe, list) or not universe:
        return [], "checklist lacks the bounded source-region universe; regenerate it"
    universe_ids = {
        str(region.get("id"))
        for region in universe
        if isinstance(region, dict) and region.get("id")
    }
    views: list[dict[str, Any]] = []
    seen: set[str] = set()
    for state in checklist.get("states") or []:
        if not isinstance(state, dict):
            return [], "checklist contains invalid state evidence"
        if state.get("channel") == "residual" or state.get("required") is False:
            continue
        state_id = str(state.get("id") or "").strip()
        try:
            breakpoint = int(state.get("breakpoint"))
        except (TypeError, ValueError):
            return [], "checklist state lacks a valid breakpoint"
        source = structures.get(str(breakpoint))
        if not isinstance(source, dict) or not isinstance(source.get("regions"), list):
            return [], f"checklist lacks critical source evidence for breakpoint {breakpoint}"
        bounds = (state.get("expect") or {}).get("bounds") or {}
        try:
            viewport_y = float(bounds.get("y") or 0)
            viewport_height = float(bounds.get("height") or 0)
        except (TypeError, ValueError):
            return [], f"checklist state {state_id} lacks viewport bounds"
        if not state_id or viewport_height <= 0:
            return [], "checklist has an incomplete required state"
        view_id = _view_id(breakpoint, state_id)
        if view_id in seen:
            return [], f"checklist contains duplicate required view {view_id}"
        seen.add(view_id)
        source_regions = source.get("regions") or []
        source_facts = source.get("region_facts") or {}
        state_scoped = False
        expect = state.get("expect") or {}
        facts_rel = expect.get("source_facts_path")
        if facts_rel:
            digest = expect.get("source_facts_digest")
            facts_path = _owned_evidence_path(store, facts_rel)
            facts_payload = _read_json(facts_path, None) if facts_path is not None else None
            if not isinstance(facts_payload, dict):
                return [], f"state {state_id} lacks source-browser facts"
            canonical = json.dumps(
                facts_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            if digest != "sha256:" + hashlib.sha256(canonical).hexdigest():
                return [], f"state {state_id} source facts are stale"
            ref_digest = expect.get("source_ref_digest")
            ref_rel = expect.get("ref")
            ref_path = _owned_evidence_path(store, ref_rel)
            if (
                ref_path is None
                or not ref_path.is_file()
                or ref_digest
                != "sha256:" + hashlib.sha256(ref_path.read_bytes()).hexdigest()
            ):
                return [], f"state {state_id} source raster is stale"
            source_regions = facts_payload.get("regions") or []
            source_facts = facts_payload.get("facts") or {}
            try:
                viewport_y = float(facts_payload.get("scroll_y") or 0)
            except (TypeError, ValueError):
                return [], f"state {state_id} has invalid source scroll"
            state_scoped = True
        elif state.get("channel") == "interaction":
            return [], f"interaction state {state_id} lacks source-browser facts"
        visible_regions = _view_visible_regions(
            source_regions,
            viewport_y=viewport_y,
            viewport_height=viewport_height,
            state_scoped=state_scoped,
        )
        visible_regions = [
            region for region in visible_regions if region.get("id") in universe_ids
        ]
        views.append(
            {
                "id": view_id,
                "breakpoint": breakpoint,
                "state_id": state_id,
                "state": state,
                "regions": visible_regions,
                "critical_regions": [region for region in visible_regions if region.get("critical")],
                "reference_facts": dict(source_facts) if isinstance(source_facts, dict) else {},
            }
        )
    if not views:
        return [], "checklist has no required visual states"
    return views, None


def _materialize_source_coverage(
    contract: Dict[str, Any], source_views: list[dict[str, Any]]
) -> Dict[str, Any]:
    """Attach compact source-derived coverage without duplicating source facts."""

    normalized = json.loads(json.dumps(contract))
    normalized.pop("reference_facts_by_view", None)
    regions = normalized.get("regions") or []
    for region in regions:
        if isinstance(region, dict):
            region.pop("reference_facts", None)
    coverage = normalized.get("coverage")
    if not isinstance(coverage, dict):
        coverage = {}
        normalized["coverage"] = coverage
    coverage.setdefault("required_view_ids", [view["id"] for view in source_views])
    views = coverage.setdefault("views", {})
    if isinstance(views, dict):
        for view in source_views:
            state_bounds = ((view.get("state") or {}).get("expect") or {}).get("bounds") or {}
            try:
                viewport_y = float(state_bounds.get("y") or 0)
                viewport_height = float(state_bounds.get("height") or 0)
            except (TypeError, ValueError):
                viewport_y, viewport_height = 0.0, 0.0
            state_id = str(view.get("state_id") or "")
            source_region_ids = {
                str(region.get("id"))
                for region in view.get("regions") or []
                if isinstance(region, dict) and region.get("id")
            }
            selected: list[dict[str, Any]] = []
            for region in regions:
                region_id = str(region.get("id") or "")
                named_state = str(region.get("state") or "")
                state_matches = not (
                    region.get("mode") == "stateful_pixels"
                    and named_state
                    and named_state != state_id
                )
                if region_id in source_region_ids and state_matches:
                    selected.append(region)
            views.setdefault(
                view["id"],
                {
                    "region_ids": [str(region.get("id")) for region in selected if region.get("id")],
                    "owner_ids": [str(region.get("owner")) for region in selected if region.get("owner")],
                },
            )
    return normalized


def _view_contract_and_facts(
    contract: Dict[str, Any],
    view: Mapping[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """Project one compact contract onto one source checkpoint viewport."""

    coverage = contract.get("coverage") or {}
    mappings = coverage.get("views") or {}
    declared = mappings.get(view["id"]) or {}
    requested = set(declared.get("region_ids") or [])
    source_bounds = {
        str(region.get("id")): region.get("bounds")
        for region in view.get("regions") or []
        if isinstance(region, dict)
    }
    projected: list[dict[str, Any]] = []
    ref_facts: Dict[str, Dict[str, Any]] = {}
    source_reference_facts = view.get("reference_facts") or {}
    for region in contract.get("regions") or []:
        region_id = str(region.get("id") or "")
        if region_id not in requested:
            continue
        projected_region = json.loads(json.dumps(region))
        if isinstance(source_bounds.get(region_id), dict):
            projected_region["bounds"] = source_bounds[region_id]
        projected.append(projected_region)
        facts = (
            source_reference_facts.get(region_id)
            if isinstance(source_reference_facts, dict)
            else None
        )
        fact = json.loads(json.dumps(facts or {}))
        # Bounds are viewport/state-specific source evidence; global desktop
        # reference facts may still contribute controls/style but must never
        # overwrite a mobile or scrolled source rectangle.
        fact["bounds"] = projected_region.get("bounds") or {}
        ref_facts[region_id] = fact
    bounds = ((view.get("state") or {}).get("expect") or {}).get("bounds") or {}
    try:
        page_size = [float(bounds.get("width")), float(bounds.get("height"))]
    except (TypeError, ValueError):
        page_size = [0.0, 0.0]
    return {
        "schema": contract.get("schema"),
        "regions": projected,
        "ref_page_size": page_size,
        "cand_page_size": page_size,
    }, ref_facts


async def _measure_visual_state_reports(
    store: SourceStore,
    url: str,
    contract: Dict[str, Any],
    source_views: list[dict[str, Any]],
    *,
    threshold: float,
) -> dict[str, Any]:
    """Replay every checklist view and evaluate its relevant semantic regions."""

    from core.visual_state_capture import capture_visual_state_views

    candidate_dir = store.dir / "evidence" / "visual-state-candidates"
    captures = await anyio.to_thread.run_sync(
        functools.partial(
            capture_visual_state_views,
            url,
            source_views,
            contract.get("regions") or [],
            candidate_dir,
        )
    )
    digest = _contract_digest(contract)
    measured: list[dict[str, Any]] = []
    for view in source_views:
        view_id = view["id"]
        capture = captures.get(view_id) or {}
        row: dict[str, Any] = {
            "view_id": view_id,
            "policy_version": VISUAL_POLICY_VERSION,
            "contract_digest": digest,
            "measured": False,
            "regions": [],
        }
        if capture.get("error"):
            row["capture_error"] = capture["error"]
            measured.append(row)
            continue
        state = view.get("state") or {}
        expected_scroll = (
            (state.get("expect") or {}).get("source_scroll_y")
            if state.get("channel") == "interaction"
            else ((state.get("expect") or {}).get("bounds") or {}).get("y")
        )
        try:
            actual_scroll = float(capture.get("scroll_y"))
            expected_scroll = float(expected_scroll or 0)
        except (TypeError, ValueError):
            row["capture_error"] = "missing scroll-position measurement"
            measured.append(row)
            continue
        if abs(actual_scroll - expected_scroll) > 2.0:
            row["capture_error"] = (
                f"scroll-position mismatch: expected {expected_scroll:.1f}, "
                f"observed {actual_scroll:.1f}"
            )
            measured.append(row)
            continue
        candidate_png = capture.get("png")
        candidate_digest = capture.get("png_digest")
        try:
            candidate_path = Path(str(candidate_png)).resolve()
            candidate_root = candidate_dir.resolve()
            digest_matches = (
                candidate_path.is_file()
                and candidate_path.is_relative_to(candidate_root)
                and isinstance(candidate_digest, str)
                and candidate_digest
                == "sha256:" + hashlib.sha256(candidate_path.read_bytes()).hexdigest()
            )
        except (OSError, ValueError):
            digest_matches = False
        if not digest_matches:
            row["capture_error"] = "candidate visual evidence is missing, mutable, or stale"
            measured.append(row)
            continue
        row["candidate_png_digest"] = candidate_digest
        ref_rel = ((state.get("expect") or {}).get("ref"))
        ref_png = store.dir / str(ref_rel) if isinstance(ref_rel, str) else None
        effective, ref_facts = _view_contract_and_facts(contract, view)
        static_present = any(
            region.get("mode") in {"static_pixels", "stateful_pixels"}
            for region in effective.get("regions") or []
        )
        if not effective["regions"]:
            row["capture_error"] = "required view has zero effective regions"
            measured.append(row)
            continue
        if not candidate_png or (static_present and (ref_png is None or not ref_png.is_file())):
            row["capture_error"] = "missing candidate or source state raster"
            measured.append(row)
            continue
        try:
            # Dynamic-only views do not need a source raster; evaluate_contract
            # opens images for a diagnostic raw score, so use the candidate as
            # a harmless diagnostic carrier while invariants remain the gate.
            reference = str(ref_png) if ref_png is not None and ref_png.is_file() else str(candidate_png)
            evaluated = evaluate_contract(
                reference,
                str(candidate_png),
                effective,
                ref_facts,
                dict(capture.get("facts") or {}),
                threshold=float(threshold),
            )
            row.update(
                measured=True,
                regions=evaluated.get("regions") or [],
                raw_whole_page_score=evaluated.get("raw_whole_page_score"),
            )
        except Exception as exc:  # noqa: BLE001 -- one missing view must fail closed
            row["capture_error"] = f"semantic evaluation failed: {exc}"
        measured.append(row)
    return evaluate_visual_state_reports(
        contract,
        source_views,
        measured,
        contract_digest=digest,
    )


def _contract_digest(contract: Dict[str, Any]) -> str:
    canonical = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _owner_source_paths(sources: Dict[str, str], owner: str) -> Dict[str, str]:
    normalized_owner = owner.lower()
    selected: Dict[str, str] = {}
    for path, content in sources.items():
        normalized = path.replace("\\", "/").lower()
        basename = normalized.rsplit("/", 1)[-1]
        if (
            f"/{normalized_owner}/" in normalized
            or basename.startswith(normalized_owner)
        ):
            selected[path] = content
    return selected


def _safe_snapshot_name(value: str) -> str:
    cleaned = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in value
    ).strip("-")
    return cleaned[:80] or "visual"


def _allowed_project_path(path: str) -> bool:
    normalized = str(path or "").replace("\\", "/")
    if normalized.startswith("/"):
        return False
    parts = tuple(part for part in normalized.split("/") if part)
    return bool(parts) and ".." not in parts and parts[0] not in (
        _PROJECT_SNAPSHOT_EXCLUDED_ROOTS
    )


async def _snapshot_project_files(sandbox: Any) -> dict[str, dict[str, str]]:
    """Capture every mutable project file outside generated/runtime roots."""

    captured: dict[str, dict[str, str]] = {}
    work_dir = getattr(sandbox, "work_dir", None)
    if work_dir is not None and Path(work_dir).is_dir():
        root = Path(work_dir).resolve()
        for candidate in sorted(root.rglob("*")):
            if candidate.is_symlink() or not candidate.is_file():
                continue
            relative = candidate.relative_to(root).as_posix()
            if not _allowed_project_path(relative):
                continue
            payload = candidate.read_bytes()
            captured[relative] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "base64": base64.b64encode(payload).decode("ascii"),
            }
        return captured

    files = getattr(sandbox, "files", None)
    if isinstance(files, dict):
        for path, content in sorted(files.items()):
            if not isinstance(path, str) or not _allowed_project_path(path):
                continue
            if not isinstance(content, str):
                continue
            payload = content.encode("utf-8")
            captured[path] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "base64": base64.b64encode(payload).decode("ascii"),
            }
    return captured


async def _restore_repair_snapshot(
    sandbox: Any,
    snapshot_path: str,
) -> tuple[bool, list[str], dict[str, Any] | None]:
    raw = await sandbox.read_file(snapshot_path)
    snapshot = _read_json_text(raw, None)
    if not isinstance(snapshot, dict):
        return False, [], None
    project_files = snapshot.get("project_files")
    if not isinstance(project_files, dict) or not project_files:
        return False, [], snapshot
    desired_paths = set(project_files)
    current = await _snapshot_project_files(sandbox)
    current_paths = set(current)
    restored: list[str] = []
    for path in sorted(current_paths - desired_paths):
        if not _allowed_project_path(path) or not hasattr(sandbox, "delete_file"):
            return False, restored, snapshot
        await sandbox.delete_file(path)
        restored.append(path)
    work_dir = getattr(sandbox, "work_dir", None)
    root = Path(work_dir).resolve() if work_dir is not None else None
    for path, record in sorted(project_files.items()):
        if (
            not isinstance(path, str)
            or not _allowed_project_path(path)
            or not isinstance(record, dict)
            or not isinstance(record.get("base64"), str)
            or not isinstance(record.get("sha256"), str)
        ):
            return False, restored, snapshot
        try:
            payload = base64.b64decode(record["base64"], validate=True)
        except (ValueError, TypeError):
            return False, restored, snapshot
        if hashlib.sha256(payload).hexdigest() != record["sha256"]:
            return False, restored, snapshot
        try:
            content = payload.decode("utf-8")
        except UnicodeDecodeError:
            content = None
        if content is not None:
            await sandbox.write_file(path, content)
        elif root is not None and root.is_dir():
            destination = (root / path).resolve()
            if root not in destination.parents:
                return False, restored, snapshot
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        else:
            return False, restored, snapshot
        restored.append(path)
    verified = await _snapshot_project_files(sandbox)
    verified_hashes = {
        path: record.get("sha256") for path, record in verified.items()
    }
    expected_hashes = {
        path: record.get("sha256") for path, record in project_files.items()
    }
    return verified_hashes == expected_hashes, restored, snapshot


async def _load_active_run(
    source_id: str,
    *,
    required: bool,
) -> tuple[Any | None, dict[str, Any] | None, Dict[str, Any] | None]:
    """Load the source-scoped sandbox ledger without silently crossing runs."""

    sandbox = get_sandbox()
    if sandbox is None:
        return (
            None,
            None,
            _err("no active clone sandbox.", source_id=source_id)
            if required
            else None,
        )
    if not hasattr(sandbox, "read_file"):
        return (
            sandbox,
            None,
            _err("active sandbox cannot read the run ledger.", source_id=source_id)
            if required
            else None,
        )
    active_source = await sandbox.read_file(_SOURCE_MARKER)
    if active_source != source_id:
        return (
            sandbox,
            None,
            _err(
                f"active sandbox belongs to {active_source!r}, not {source_id!r}.",
                source_id=source_id,
            )
            if required
            else None,
        )
    ledger = _read_json_text(await sandbox.read_file(_RUN_LEDGER), None)
    if not isinstance(ledger, dict) or not ledger.get("run_id"):
        return (
            sandbox,
            None,
            _err(
                "run ledger is missing run_id; assemble the project first.",
                source_id=source_id,
            ),
        )
    if ledger.get("source_id") != source_id:
        return (
            sandbox,
            None,
            _err("run ledger source_id does not match the active source.", source_id=source_id),
        )
    return sandbox, ledger, None


def _read_json_text(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


async def _persist_run(sandbox: Any, ledger: dict[str, Any]) -> None:
    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    await sandbox.write_file(_RUN_LEDGER, _json_text(ledger))


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
    seen_critical = {str(region.get("id")) for region in critical_regions}
    checklist = _read_json(store.dir / "checklist.json", {})
    source_regions = [
        dict(region)
        for region in (checklist.get("source_region_universe") or [])[:64]
        if isinstance(region, dict)
    ]
    if not source_regions:
        return _err(
            "no bounded source-region universe; run generate_manifest with the "
            "current Harness before requesting comparison evidence.",
            source_id=source_id,
        )
    for breakpoint_entry in summary.get("breakpoints") or []:
        if not isinstance(breakpoint_entry, dict):
            continue
        evidence_path = _owned_evidence_path(
            store, breakpoint_entry.get("interaction_evidence")
        )
        evidence = _read_json(evidence_path, {}) if evidence_path is not None else {}
        breakpoint = breakpoint_entry.get("breakpoint")
        for region in evidence.get("regions") or []:
            if not isinstance(region, dict) or not region.get("critical"):
                continue
            region_id = str(region.get("fingerprint") or region.get("id") or "")
            if not region_id or region_id in seen_critical:
                continue
            seen_critical.add(region_id)
            critical_regions.append(
                {
                    "id": region_id,
                    "kind": region.get("kind"),
                    "critical": True,
                    "bounds": region.get("rect") or region.get("bounds") or {},
                    "breakpoints": [breakpoint],
                }
            )
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
        "critical_regions": critical_regions[:64],
        "source_regions": source_regions,
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
    if result["text_bytes"] > budget:
        return _err(
            "max_text_bytes is too small for the required bounded source-region "
            "contract; retry with a larger budget.",
            source_id=source_id,
            required_bytes=result["text_bytes"],
            source_region_count=len(source_regions),
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
    # Coverage is source-derived and compact: view IDs plus declared region and
    # owner IDs.  It avoids making the Agent repeat a large DOM/style contract
    # for every breakpoint while still making omissions deterministic.
    source_views, source_views_error = _source_visual_views(store)
    normalized_contract = json.loads(json.dumps(contract))
    if source_views_error is None:
        normalized_contract.pop("reference_facts_by_view", None)
        for region in normalized_contract.get("regions") or []:
            if isinstance(region, dict):
                region.pop("reference_facts", None)
        normalized_contract = _materialize_source_coverage(normalized_contract, source_views)
        coverage_errors = validate_contract_coverage(normalized_contract, source_views)
        if coverage_errors:
            return _err(
                "incomplete comparison-contract coverage: " + "; ".join(coverage_errors),
                source_id=source_id,
                validation_errors=coverage_errors,
            )
    errors = validate_contract(normalized_contract)
    if errors:
        return _err(
            "invalid comparison contract: " + "; ".join(errors),
            source_id=source_id,
            validation_errors=errors,
        )
    path = _contract_path(store)
    try:
        save_contract(normalized_contract, path)
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not save comparison contract: {exc}", source_id=source_id)

    contract = normalized_contract
    digest = _contract_digest(contract)
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
    run_sandbox, ledger, load_error = await _load_active_run(
        source_id,
        required=False,
    )
    if load_error:
        return load_error
    if run_sandbox is not None and ledger is not None:
        previous = (ledger.get("comparison_contract") or {}).get("digest")
        latest_contract = (ledger.get("latest_semantic_report") or {}).get(
            "contract_digest"
        )
        changed = (
            (previous is not None and previous != digest)
            or (latest_contract is not None and latest_contract != digest)
        )
        ledger["comparison_contract"] = {
            "path": ".pwc/comparison-contract.json",
            "regions": len(contract["regions"]),
            "status": "valid",
            "digest": digest,
        }
        if changed:
            ledger.pop("latest_semantic_report", None)
            ledger.pop("pending_repair", None)
            ledger.pop("active_attempt", None)
            ledger.pop("authorized_stop", None)
            ledger["gate_results"]["visual"] = {
                "status": "pending",
                "evidence": [],
            }
            ledger["residuals"] = [
                residual
                for residual in (ledger.get("residuals") or [])
                if not (
                    isinstance(residual, dict)
                    and residual.get("gate") == "visual"
                )
            ]
            source_report = store.dir / _SOURCE_SEMANTIC_REPORT
            if source_report.is_file():
                source_report.unlink()
        await _persist_run(run_sandbox, ledger)
    return {
        "ok": True,
        "source_id": source_id,
        "regions": len(contract["regions"]),
        "required_views": len(source_views),
        "contract": str(path),
        "contract_digest": digest,
        "sandbox_saved": sandbox_saved,
    }


async def persist_semantic_report(
    source_id: str,
    report: Dict[str, Any],
    contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Persist fresh measured semantic evidence and advance the run reducer.

    This is a module helper used by :func:`score_semantic_fidelity`; it is kept
    separately testable so digest and resume behavior never depends on a live
    browser.
    """

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    if not isinstance(report, dict):
        return _err("report must be an object.", source_id=source_id)
    measured_source = report.get("source_id")
    if measured_source is not None and measured_source != source_id:
        return _err("report source_id does not match source_id.", source_id=source_id)
    store = SourceStore(source_id)
    if not store.dir.is_dir():
        return _err(
            f"no captured source {source_id!r}; run extract_page first.",
            source_id=source_id,
        )
    if contract is None:
        try:
            contract = load_contract(_contract_path(store))
        except Exception as exc:  # noqa: BLE001
            return _err(
                f"could not read comparison contract: {exc}",
                source_id=source_id,
            )
    saved_contract = load_contract(_contract_path(store))
    contract_digest = _contract_digest(contract)
    if contract_digest != _contract_digest(saved_contract):
        return _err(
            "semantic report contract is stale; save and use the current contract.",
            source_id=source_id,
        )
    payload = semantic_report_payload(report)
    payload["source_id"] = source_id
    payload["comparison_contract_digest"] = contract_digest
    digest = semantic_report_digest(payload)
    objective = semantic_objective(payload, contract)
    source_report_path = store.dir / _SOURCE_SEMANTIC_REPORT
    source_report_path.write_text(_json_text(payload), encoding="utf-8")

    sandbox, ledger, load_error = await _load_active_run(
        source_id,
        required=False,
    )
    if load_error:
        return load_error
    decision = {
        "execution_ok": False,
        "gate_status": "pass" if payload.get("ok") else "fail",
        "must_continue": True,
        "next_action": "assemble_or_resume_run",
        "terminal_allowed": [],
    }
    run_state_recorded = False
    if sandbox is not None and ledger is not None:
        await sandbox.write_file(_SEMANTIC_REPORT, _json_text(payload))
        ledger, decision = apply_semantic_report(
            ledger,
            payload,
            digest=digest,
            objective=objective,
            report_path=_SEMANTIC_REPORT,
        )
        ledger["latest_semantic_report"]["contract_digest"] = contract_digest
        ledger = synchronize_stop_conditions(ledger)
        decision = harness_decision(ledger)
        await _persist_run(sandbox, ledger)
        run_state_recorded = True
    return {
        "ok": True,
        "source_id": source_id,
        "semantic_report_digest": digest,
        "semantic_report_path": str(source_report_path),
        "comparison_contract_digest": contract_digest,
        "objective": objective,
        "run_state_recorded": run_state_recorded,
        **decision,
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
    sandbox, _ledger, load_error = await _load_active_run(
        source_id,
        required=True,
    )
    if load_error:
        return load_error
    assert sandbox is not None
    owned_url, ownership_error = await require_owned_preview_url(sandbox, url)
    if ownership_error:
        return _err(ownership_error, source_id=source_id)
    assert owned_url is not None

    # New source captures own a finite responsive/state checklist.  Measure
    # every one before letting the legacy full-page path run; a desktop-only
    # capture is retained solely for schema<=3 migration tests and cannot green
    # a schema4 run.
    source_views, source_views_error = _source_visual_views(store)
    if source_views_error is None:
        coverage_errors = validate_contract_coverage(contract, source_views)
        if coverage_errors:
            return _err(
                "comparison contract lacks required view/critical-region coverage: "
                + "; ".join(coverage_errors),
                source_id=source_id,
                validation_errors=coverage_errors,
            )
        visual_details = await _measure_visual_state_reports(
            store,
            owned_url,
            contract,
            source_views,
            threshold=float(threshold),
        )
        flattened_regions: list[dict[str, Any]] = []
        for view_id, summary in (visual_details.get("views") or {}).items():
            # The measured report itself is in the source artifact; keep the
            # durable repair reducer payload compact but localizable.
            failures = (visual_details.get("failures_by_view") or {}).get(view_id) or []
            for failure in failures:
                if isinstance(failure, dict) and failure.get("id"):
                    flattened_regions.append(
                        {
                            "id": failure["id"],
                            "owner": next(
                                (
                                    region.get("owner")
                                    for region in contract.get("regions") or []
                                    if region.get("id") == failure["id"]
                                ),
                                failure["id"],
                            ),
                            "view_id": view_id,
                            "status": "fail",
                            "score": failure.get("score"),
                            "failed_invariants": list(failure.get("failed_invariants") or [failure.get("code")]),
                        }
                    )
        report = {
            "ok": bool(visual_details.get("ok")),
            "source_id": source_id,
            "url": owned_url,
            "regions": flattened_regions,
            "visual_details": visual_details,
            "measurement_policy": (
                "static pixels are measured per checklist view; dynamic layout/behavior "
                "uses geometry/style/controls invariants and raw frames are diagnostic"
            ),
            "capture_integrity": integrity,
        }
        persisted = await persist_semantic_report(source_id, report, contract)
        report.update(
            {
                key: persisted[key]
                for key in (
                    "execution_ok",
                    "gate_status",
                    "must_continue",
                    "next_action",
                    "terminal_allowed",
                    "semantic_report_digest",
                    "semantic_report_path",
                    "comparison_contract_digest",
                    "objective",
                    "run_state_recorded",
                )
                if key in persisted
            }
        )
        if not persisted.get("ok"):
            report["persistence_error"] = persisted.get("error")
        return report
    try:
        strict_run = int((_ledger or {}).get("schema") or 0) >= 4
    except (TypeError, ValueError):
        strict_run = True
    if strict_run:
        return _err(source_views_error or "missing required visual state evidence", source_id=source_id)

    summary = _read_json(store.dir / "summary.json", {})
    viewport = summary.get("viewport") or {}
    width = int(viewport.get("width") or summary.get("page_width") or 1440)
    height = int(viewport.get("height") or 900)
    cap = await capture_clone_sections(
        url=owned_url,
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
    persisted = await persist_semantic_report(source_id, report, contract)
    if not persisted.get("ok"):
        report.update(
            {
                "execution_ok": False,
                "gate_status": "pass" if report.get("ok") else "fail",
                "must_continue": True,
                "next_action": "repair:harness-run-state",
                "terminal_allowed": [],
                "persistence_error": persisted.get("error"),
            }
        )
        return report
    report.update(
        {
            key: persisted[key]
            for key in (
                "execution_ok",
                "gate_status",
                "must_continue",
                "next_action",
                "terminal_allowed",
                "semantic_report_digest",
                "semantic_report_path",
                "comparison_contract_digest",
                "objective",
                "run_state_recorded",
            )
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
    latest_path = store.dir / _SOURCE_SEMANTIC_REPORT
    latest_report = _read_json(latest_path, None)
    if not isinstance(latest_report, dict):
        return _err(
            "no persisted semantic report; score semantic fidelity first.",
            source_id=source_id,
        )
    current_contract_digest = _contract_digest(contract)
    if (
        latest_report.get("comparison_contract_digest")
        != current_contract_digest
    ):
        return _err(
            "persisted semantic report belongs to a stale comparison contract.",
            source_id=source_id,
        )
    supplied_payload = semantic_report_payload(report)
    supplied_payload.setdefault(
        "comparison_contract_digest",
        current_contract_digest,
    )
    supplied_digest = semantic_report_digest(supplied_payload)
    latest_digest = semantic_report_digest(latest_report)
    if supplied_digest != latest_digest:
        return _err(
            "semantic report is stale or tampered; re-score before repairing.",
            source_id=source_id,
        )
    sandbox, run_ledger, load_error = await _load_active_run(
        source_id,
        required=False,
    )
    if load_error:
        return load_error
    if sandbox is not None and run_ledger is not None:
        latest_meta = run_ledger.get("latest_semantic_report") or {}
        pending = run_ledger.get("pending_repair") or {}
        decision = harness_decision(synchronize_stop_conditions(run_ledger))
        if (
            latest_meta.get("digest") != latest_digest
            or pending.get("report_digest") != latest_digest
            or latest_meta.get("contract_digest") != current_contract_digest
            or (run_ledger.get("comparison_contract") or {}).get("digest")
            != current_contract_digest
        ):
            return _err(
                "semantic report is stale or tampered relative to run state.",
                source_id=source_id,
            )
        if (
            decision.get("must_continue") is not True
            or not str(decision.get("next_action") or "").startswith("repair:")
        ):
            return _err(
                "semantic repair target is no longer eligible.",
                source_id=source_id,
                next_action=decision.get("next_action"),
            )
        if run_ledger.get("active_attempt"):
            return _err(
                "a repair candidate is already awaiting fresh semantic re-score.",
                source_id=source_id,
            )
    iteration_ledger = _read_json(store.dir / "iteration-ledger.json", {})
    try:
        deterministic_target = str(
            select_worst_region(latest_report).get("id") or "visual"
        )
    except ValueError as exc:
        return _err(str(exc), source_id=source_id)
    limits = iteration_ledger.get("limits") or {}
    target_attempts = sum(
        1
        for attempt in (iteration_ledger.get("attempts") or [])
        if attempt.get("target") == deterministic_target
    )
    total_attempts = len(iteration_ledger.get("attempts") or [])
    non_improving = int(
        (iteration_ledger.get("non_improving") or {}).get(
            deterministic_target,
            0,
        )
    )
    if (
        non_improving >= 2
        or target_attempts >= int(limits.get("max_target_attempts", 5))
        or total_attempts >= int(limits.get("max_total_attempts", 12))
    ):
        return _err(
            "semantic repair target is ineligible under the iteration limit.",
            source_id=source_id,
            target=deterministic_target,
        )
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
    try:
        packet = build_repair_packet(
            latest_report,
            contract,
            sources,
            attempts=list(iteration_ledger.get("attempts") or []),
            max_text_bytes=int(max_text_bytes),
        )
    except Exception as exc:  # noqa: BLE001
        return _err(f"could not build semantic repair packet: {exc}", source_id=source_id)
    if run_ledger is not None:
        pending_target = (run_ledger.get("pending_repair") or {}).get("target")
        packet_target = (packet.get("target") or {}).get("id")
        if packet_target != pending_target:
            return _err(
                "persisted repair target does not match the deterministic packet target.",
                source_id=source_id,
            )
        owner = str((packet.get("contract") or {}).get("owner") or packet_target)
        snapshot_sources = _owner_source_paths(sources, owner)
        if not snapshot_sources:
            return _err(
                "could not snapshot any owner source before repair.",
                source_id=source_id,
                target=packet_target,
            )
        snapshot_path = (
            ".pwc/repair-snapshots/"
            f"{_safe_snapshot_name(str(packet_target))}-"
            f"{latest_digest.removeprefix('sha256:')[:16]}.json"
        )
        project_files = await _snapshot_project_files(sandbox)
        if not project_files:
            return _err(
                "could not snapshot the complete editable project before repair.",
                source_id=source_id,
                target=packet_target,
            )
        snapshot = {
            "schema": 2,
            "source_id": source_id,
            "target": packet_target,
            "owner": owner,
            "before_report_digest": latest_digest,
            "before_objective": (run_ledger.get("pending_repair") or {}).get(
                "objective"
            ),
            "sources": snapshot_sources,
            "project_files": project_files,
            "semantic_report": latest_report,
        }
        assert sandbox is not None
        await sandbox.write_file(snapshot_path, _json_text(snapshot))
        run_ledger = start_repair_epoch(
            run_ledger,
            target=str(packet_target),
            owner=owner,
            report_digest=latest_digest,
            objective=float(snapshot["before_objective"]),
            snapshot_path=snapshot_path,
        )
        run_ledger["active_attempt"]["packet_bytes"] = packet.get("text_bytes")
        run_ledger["active_attempt"]["estimated_tokens"] = packet.get(
            "estimated_tokens"
        )
        await _persist_run(sandbox, run_ledger)
        packet["snapshot_path"] = snapshot_path
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
    run_sandbox, run_ledger, load_error = await _load_active_run(
        source_id,
        required=False,
    )
    if load_error:
        return load_error
    active_attempt: Dict[str, Any] | None = None
    if run_ledger is not None:
        active_attempt = run_ledger.get("active_attempt")
        if not isinstance(active_attempt, dict):
            return _err(
                "no active repair snapshot; build a repair packet first.",
                source_id=source_id,
            )
        latest_meta = run_ledger.get("latest_semantic_report") or {}
        if (
            latest_meta.get("digest")
            == active_attempt.get("before_report_digest")
        ):
            return _err(
                "fresh semantic re-score required after editing the candidate.",
                source_id=source_id,
            )
        stale_gates = stale_attempt_gates(run_ledger)
        if stale_gates:
            return _err(
                "fresh hard-gate evidence required after the repair edit.",
                source_id=source_id,
                stale_gates=stale_gates,
                verification_epoch=active_attempt.get("epoch"),
            )
        target = str(active_attempt.get("target") or "visual")
        before = float(active_attempt.get("before_objective"))
        after = float(latest_meta.get("objective"))
        baseline = active_attempt.get("baseline_gate_statuses") or {}
        current_gates = run_ledger.get("gate_results") or {}
        hard_gate_regressions = [
            gate
            for gate, baseline_status in baseline.items()
            if gate != "visual"
            and baseline_status == "pass"
            and (current_gates.get(gate) or {}).get("status") != "pass"
        ]
        candidate_path = None
        packet_bytes = active_attempt.get("packet_bytes")
        estimated_tokens = active_attempt.get("estimated_tokens")
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
    decision: Dict[str, Any] = {}
    restored = False
    restored_paths: list[str] = []
    if run_sandbox is not None and run_ledger is not None:
        assert active_attempt is not None
        if not result.get("accepted"):
            restored, restored_paths, snapshot = await _restore_repair_snapshot(
                run_sandbox,
                str(active_attempt.get("snapshot_path") or ""),
            )
            if not restored or not isinstance(snapshot, dict):
                return _err(
                    "rejected candidate could not restore its deterministic snapshot.",
                    source_id=source_id,
                )
            prior_report = snapshot.get("semantic_report")
            if not isinstance(prior_report, dict):
                return _err(
                    "repair snapshot is missing its semantic report.",
                    source_id=source_id,
                )
            prior_digest = semantic_report_digest(prior_report)
            run_ledger, _ = apply_semantic_report(
                run_ledger,
                prior_report,
                digest=prior_digest,
                objective=float(active_attempt.get("before_objective")),
                report_path=_SEMANTIC_REPORT,
            )
            contract_digest = prior_report.get(
                "comparison_contract_digest"
            )
            run_ledger["latest_semantic_report"][
                "contract_digest"
            ] = contract_digest
            for gate, gate_result in (
                active_attempt.get("baseline_gate_results") or {}
            ).items():
                run_ledger.setdefault("gate_results", {})[gate] = json.loads(
                    json.dumps(gate_result)
                )
            await run_sandbox.write_file(
                _SEMANTIC_REPORT,
                _json_text(prior_report),
            )
            (store.dir / _SOURCE_SEMANTIC_REPORT).write_text(
                _json_text(prior_report),
                encoding="utf-8",
            )
        compact_attempt = {
            "gate": "visual",
            "target": target,
            "before": before,
            "after": after,
            "accepted": bool(result.get("accepted")),
            "hard_gate_regressions": list(hard_gate_regressions or []),
            "candidate_path": candidate_path,
        }
        if packet_bytes is not None:
            compact_attempt["packet_bytes"] = packet_bytes
        if estimated_tokens is not None:
            compact_attempt["estimated_tokens"] = estimated_tokens
        run_ledger.setdefault("attempts", []).append(compact_attempt)
        pending = run_ledger.get("pending_repair") or {}
        if result.get("recorded"):
            pending["attempts_remaining"] = max(
                0,
                int(pending.get("attempts_remaining", 1)) - 1,
            )
        if pending:
            run_ledger["pending_repair"] = pending
        run_ledger.pop("active_attempt", None)
        stop_code = result.get("stop_code")
        if stop_code:
            run_ledger = authorize_stop(
                run_ledger,
                reason=str(stop_code),
                gate="visual",
                target=target,
                evidence=[str(candidate_path)] if candidate_path else [],
            )
        run_ledger = synchronize_stop_conditions(run_ledger)
        decision = harness_decision(run_ledger)
        await _persist_run(run_sandbox, run_ledger)
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
        "before": float(before),
        "after": float(after),
        "hard_gate_regressions": list(hard_gate_regressions or []),
        "ledger": str(ledger_path),
        "restored": restored,
        "restored_paths": restored_paths,
        **decision,
    }


async def get_harness_run_state(source_id: str) -> Dict[str, Any]:
    """Return the durable next action for the active source-scoped run."""

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    sandbox, ledger, error = await _load_active_run(source_id, required=True)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    ledger = synchronize_stop_conditions(ledger)
    await _persist_run(sandbox, ledger)
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": ledger["run_id"],
        "phase": ledger.get("phase"),
        "status": ledger.get("status"),
        "pending_repair": ledger.get("pending_repair"),
        **harness_decision(ledger),
    }


async def finalize_run(
    source_id: str,
    status: str,
) -> Dict[str, Any]:
    """Apply a fail-closed Harness terminal transition and persist it."""

    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()
    sandbox, ledger, error = await _load_active_run(source_id, required=True)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    try:
        terminal = finalize_run_state(ledger, str(status or "").strip())
    except ValueError as exc:
        return _err(str(exc), source_id=source_id, run_id=ledger["run_id"])
    terminal["completed_at"] = datetime.now(timezone.utc).isoformat()
    await _persist_run(sandbox, terminal)
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": terminal["run_id"],
        "phase": terminal["phase"],
        "status": terminal["status"],
        "residuals": list(terminal.get("residuals") or []),
        **harness_decision(terminal),
    }


def _owned_evidence_path(store: SourceStore, rel: Any) -> Path | None:
    """Resolve only a real, source-owned relative evidence path."""
    if not isinstance(rel, str) or not rel.strip():
        return None
    try:
        root = store.dir.resolve()
        path = (store.dir / rel).resolve()
        if not path.is_relative_to(root):
            return None
        return path if path.is_file() else None
    except (OSError, ValueError):
        return None


def _valid_png(path: Path, expected_size: tuple[int, int] | None) -> bool:
    """Verify evidence is decodable and has the exact viewport geometry."""
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG":
                return False
            if expected_size is not None and image.size != expected_size:
                return False
        return True
    except (OSError, ValueError):
        return False


def _valid_full_png(
    path: Path,
    *,
    page_width: int,
    page_height: float,
) -> bool:
    """Validate full-page CSS-pixel geometry under the explicit DPR1 policy."""
    if not _valid_png(path, None):
        return False
    try:
        with Image.open(path) as full:
            return full.size == (page_width, round(page_height))
    except (OSError, ValueError):
        return False


def _breakpoint_inventory(
    path: Path | None, breakpoint: int
) -> dict[str, Any] | None:
    """Load successful, bounded source inventory for one breakpoint."""
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or int(payload.get("breakpoint") or 0) != breakpoint:
        return None
    interactions = payload.get("interactions")
    regions = payload.get("regions")
    region_facts = payload.get("region_facts")
    scroll_states = payload.get("scroll_states")
    interaction_states = payload.get("interaction_states")
    page = payload.get("page")
    if (
        not isinstance(interactions, list)
        or not all(isinstance(item, dict) for item in interactions)
        or not isinstance(regions, list)
        or not all(isinstance(item, dict) for item in regions)
        or not isinstance(region_facts, dict)
        or not isinstance(scroll_states, list)
        or not isinstance(interaction_states, list)
        or not isinstance(page, dict)
    ):
        return None
    source_root = path.parents[2]
    verified_scroll_states: list[dict[str, Any]] = []
    seen_scroll_ids: set[str] = set()
    for state in scroll_states:
        if not isinstance(state, dict) or not state.get("id"):
            return None
        state_id = str(state["id"])
        if state_id in seen_scroll_ids:
            return None
        seen_scroll_ids.add(state_id)
        ref = state.get("ref")
        facts_path = state.get("facts_path")
        ref_path = source_root / str(ref) if isinstance(ref, str) else None
        fact_file = (
            source_root / str(facts_path)
            if isinstance(facts_path, str)
            else None
        )
        if (
            ref_path is None
            or not _valid_png(ref_path, None)
            or fact_file is None
            or not fact_file.is_file()
        ):
            return None
        if state.get("ref_digest") != (
            "sha256:" + hashlib.sha256(ref_path.read_bytes()).hexdigest()
        ):
            return None
        facts_payload = _read_json(fact_file, None)
        if (
            not isinstance(facts_payload, dict)
            or facts_payload.get("state_id") != state_id
            or int(facts_payload.get("breakpoint") or 0) != breakpoint
            or not isinstance(facts_payload.get("regions"), list)
            or not isinstance(facts_payload.get("facts"), dict)
        ):
            return None
        canonical = json.dumps(
            facts_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if state.get("facts_digest") != (
            "sha256:" + hashlib.sha256(canonical).hexdigest()
        ):
            return None
        verified_state = dict(state)
        verified_state["_regions"] = list(facts_payload.get("regions") or [])[:64]
        verified_scroll_states.append(verified_state)
    states_by_interaction: dict[str, dict[str, Any]] = {}
    for state in interaction_states:
        if not isinstance(state, dict) or not state.get("interaction_id"):
            return None
        ref = state.get("ref")
        facts_path = state.get("facts_path")
        facts_digest = state.get("facts_digest")
        ref_digest = state.get("ref_digest")
        ref_path = source_root / str(ref) if isinstance(ref, str) else None
        fact_file = source_root / str(facts_path) if isinstance(facts_path, str) else None
        if ref_path is None or not _valid_png(ref_path, None) or fact_file is None or not fact_file.is_file():
            return None
        if ref_digest != "sha256:" + hashlib.sha256(ref_path.read_bytes()).hexdigest():
            return None
        facts_payload = _read_json(fact_file, None)
        if not isinstance(facts_payload, dict):
            return None
        canonical = json.dumps(
            facts_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if facts_digest != "sha256:" + hashlib.sha256(canonical).hexdigest():
            return None
        verified_state = dict(state)
        verified_state["_regions"] = list(facts_payload.get("regions") or [])[:64]
        states_by_interaction[str(state["interaction_id"])] = verified_state
    enriched_interactions: list[dict[str, Any]] = []
    for interaction in interactions:
        record = dict(interaction)
        if interaction.get("required", True):
            source_state = states_by_interaction.get(str(interaction.get("id") or ""))
            if source_state is None:
                return None
            record["source_state"] = source_state
        enriched_interactions.append(record)
    return {
        "interactions": enriched_interactions,
        "scroll_states": verified_scroll_states,
        "critical_regions": [region for region in regions[:64] if region.get("critical")],
        "regions": regions[:64],
        "region_facts": {
            str(key): dict(value)
            for key, value in list(region_facts.items())[:64]
            if isinstance(value, dict)
        },
        "page": page,
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

    # Responsive viewport + page height evidence lives in summary.json.  Older
    # captures have just the primary fields; retain that read path so their
    # desktop checklist can still be replayed, while modern captures seed every
    # namespaced breakpoint bundle.
    vw, vh = 1440, 900
    page_h: float = 0.0
    breakpoint_evidence: list[dict[str, Any]] = []
    summary_path = store.dir / "summary.json"
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            vp = summary.get("viewport") or {}
            vw = int(vp.get("width", 1440))
            vh = int(vp.get("height", 900))
            page_h = float(summary.get("page_height") or 0)
            raw_breakpoints = summary.get("breakpoints") or []
            if isinstance(raw_breakpoints, list):
                breakpoint_evidence = [
                    item for item in raw_breakpoints if isinstance(item, dict)
                ]
        except Exception:  # noqa: BLE001
            pass

    if page_h <= 0:
        return _err(
            "source has no page_height in summary.json; "
            "re-extract with current harness.",
            source_id=source_id,
        )

    if not breakpoint_evidence:
        return _err(
            "legacy desktop-only capture is readable but cannot pass the strict "
            "Harness; re-extract to capture required 1440 and 390 evidence.",
            source_id=source_id,
            required_breakpoints=list(_REQUIRED_SOURCE_BREAKPOINTS),
        )

    normalized_breakpoints: list[dict[str, Any]] = []
    seen_breakpoints: set[int] = set()
    for item in breakpoint_evidence:
        viewport = item.get("viewport") or {}
        try:
            breakpoint = int(item.get("breakpoint") or viewport.get("width"))
            width = int(viewport.get("width") or breakpoint)
            height = int(viewport.get("height"))
            item_page_width = int(item.get("page_width") or width)
            item_page_height = float(item.get("page_height") or 0)
            dpr = int(item.get("device_scale_factor", 1))
        except (TypeError, ValueError):
            return _err("summary.json contains an invalid breakpoint evidence record.", source_id=source_id)
        if breakpoint <= 0 or width != breakpoint or height <= 0 or item_page_height <= 0:
            return _err(
                "summary.json contains incomplete breakpoint viewport/page-height evidence.",
                source_id=source_id,
                breakpoint=item.get("breakpoint"),
            )
        if dpr != 1:
            return _err(
                "breakpoint evidence must use explicit DPR 1; recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        if breakpoint in seen_breakpoints:
            return _err(
                "summary.json contains duplicate breakpoint evidence.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        viewport_rel = item.get("screenshot")
        full_rel = item.get("full_page_screenshot")
        scroll_rels = item.get("scroll_states")
        if not isinstance(scroll_rels, list) or not all(isinstance(path, str) for path in scroll_rels):
            return _err(
                "source has invalid breakpoint scroll-state evidence; recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        expected_scroll_count = 5 if item_page_height > 2 * height else 0
        if len(scroll_rels) != expected_scroll_count:
            return _err(
                "source has incomplete breakpoint scroll-state evidence; recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        viewport_path = _owned_evidence_path(store, viewport_rel)
        if viewport_path is None or not _valid_png(viewport_path, (width, height)):
            return _err(
                "source is missing or corrupt breakpoint viewport evidence; "
                "recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        full_path = _owned_evidence_path(store, full_rel)
        if full_path is None or not _valid_full_png(
            full_path,
            page_width=item_page_width,
            page_height=item_page_height,
        ):
            return _err(
                "source is missing, corrupt, or geometrically invalid breakpoint "
                "full-page evidence; recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        evidence_paths = [("scroll-state", path, (width, height)) for path in scroll_rels]
        resolved_paths: dict[str, Path] = {}
        for label, rel, expected_size in evidence_paths:
            path = _owned_evidence_path(store, rel)
            if path is None or not _valid_png(path, expected_size):
                return _err(
                    f"source is missing or corrupt breakpoint {label} evidence; "
                    "recapture before generating a checklist.",
                    source_id=source_id,
                    breakpoint=breakpoint,
                )
        resolved_paths["full"] = full_path
        interaction_path = _owned_evidence_path(store, item.get("interaction_evidence"))
        inventory = _breakpoint_inventory(interaction_path, breakpoint)
        if inventory is None:
            return _err(
                "source is missing, corrupt, or incomplete breakpoint inventory evidence; "
                "recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        if len(inventory.get("scroll_states") or []) != expected_scroll_count:
            return _err(
                "source is missing state-local scroll inventory/facts; "
                "recapture before generating a checklist.",
                source_id=source_id,
                breakpoint=breakpoint,
            )
        seen_breakpoints.add(breakpoint)
        normalized_breakpoints.append({
            "breakpoint": breakpoint,
            "viewport": (width, height),
            "page_height": item_page_height,
            "screenshots_dir": resolved_paths["full"].parent,
            **inventory,
        })

    missing_breakpoints = sorted(set(_REQUIRED_SOURCE_BREAKPOINTS) - seen_breakpoints)
    if missing_breakpoints:
        return _err(
            "source is missing required strict breakpoint evidence; re-extract before "
            "generating a checklist (required 1440 and 390).",
            source_id=source_id,
            required_breakpoints=list(_REQUIRED_SOURCE_BREAKPOINTS),
            missing_breakpoints=missing_breakpoints,
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

    m = mf.new_manifest(
        meta.get("source_url", ""),
        [item["breakpoint"] for item in normalized_breakpoints],
    )
    for item in normalized_breakpoints:
        source_scroll_states = item.get("scroll_states") or []
        if source_scroll_states:
            width, height = item["viewport"]
            for source_state in source_scroll_states:
                scroll_y = float(source_state.get("scroll_y") or 0)
                state_id = str(source_state.get("id") or "")
                mf.add_state(
                    m,
                    {
                        "id": state_id,
                        "section": None,
                        "breakpoint": item["breakpoint"],
                        "trigger": [{"kind": "scroll", "y": scroll_y}],
                        "expect": {
                            "ref": source_state.get("ref"),
                            "source_ref_digest": source_state.get("ref_digest"),
                            "source_facts_path": source_state.get("facts_path"),
                            "source_facts_digest": source_state.get("facts_digest"),
                            "source_scroll_y": scroll_y,
                            "ssim": 0.97,
                            "bounds": {
                                "x": 0,
                                "y": scroll_y,
                                "width": width,
                                "height": height,
                            },
                        },
                        "channel": "baseline",
                        "evidence": None,
                        "stability": "stable",
                        "status": "pending",
                    },
                )
        else:
            for st in mf.baseline_states(
                item["page_height"], item["viewport"], item["breakpoint"]
            ):
                mf.add_state(m, st)

    m["structure_by_breakpoint"] = {
        str(item["breakpoint"]): {
            "page": item["page"],
            "critical_regions": item["critical_regions"],
            "regions": item["regions"],
            "region_facts": item["region_facts"],
        }
        for item in normalized_breakpoints
    }
    region_groups: list[tuple[str, int, list[dict[str, Any]]]] = []
    for item in normalized_breakpoints:
        breakpoint = int(item["breakpoint"])
        region_groups.append(
            (f"b{breakpoint}:rest", breakpoint, list(item.get("regions") or []))
        )
        for state in item.get("scroll_states") or []:
            region_groups.append(
                (
                    f"b{breakpoint}:{state.get('id')}",
                    breakpoint,
                    list(state.get("_regions") or []),
                )
            )
        for interaction in item.get("interactions") or []:
            source_state = interaction.get("source_state") or {}
            region_groups.append(
                (
                    f"b{breakpoint}:{source_state.get('id')}",
                    breakpoint,
                    list(source_state.get("_regions") or []),
                )
            )
    try:
        m["source_region_universe"] = _bounded_source_region_universe(
            region_groups
        )
    except ValueError as exc:
        return _err(
            f"source region universe cannot be bounded safely: {exc}",
            source_id=source_id,
        )
    if not m["source_region_universe"]:
        return _err(
            "source has no measurable bounded regions; recapture before "
            "generating a checklist.",
            source_id=source_id,
        )
    for item in normalized_breakpoints:
        for st in mf.interaction_states(
            item["interactions"], item["breakpoint"], viewport=item["viewport"]
        ):
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
    refs_by_breakpoint: dict[str, dict[str, Any]] = {}
    for item in normalized_breakpoints:
        try:
            refs_by_breakpoint[str(item["breakpoint"])] = materialize_refs(
                store.dir,
                item["page_height"],
                item["viewport"],
                item["breakpoint"],
                screenshots_dir=item["screenshots_dir"],
            )
        except Exception as exc:  # noqa: BLE001
            refs_by_breakpoint[str(item["breakpoint"])] = {
                "written": [], "skipped": [], "missing": [], "source": "none",
                "error": str(exc),
            }
    # Keep the original ``refs`` payload for callers that consumed the
    # desktop-only API; explicit callers can inspect the full map.
    refs_summary = refs_by_breakpoint[str(normalized_breakpoints[0]["breakpoint"])]

    return {
        "ok": True,
        "source_id": source_id,
        "states": len(m["states"]),
        "interactions": sum(
            1 for state in m["states"] if state.get("channel") == "interaction"
        ),
        "checklist": str(checklist_path),
        "refs": refs_summary,
        "refs_by_breakpoint": refs_by_breakpoint,
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
    sandbox, _ledger, load_error = await _load_active_run(
        source_id,
        required=True,
    )
    if load_error:
        return load_error
    assert sandbox is not None
    owned_url, ownership_error = await require_owned_preview_url(sandbox, url)
    if ownership_error:
        return _err(ownership_error, source_id=source_id)
    assert owned_url is not None

    out_dir = store.dir / "manifest_out"

    def _run():
        return manifest_gate.verify_manifest(m, owned_url, store.dir, out_dir)

    try:
        result = await anyio.to_thread.run_sync(_run)
    except Exception as exc:  # noqa: BLE001
        return _err(f"verify_manifest failed: {exc}", source_id=source_id)

    mf.save_manifest(m, mpath)
    report_path = store.dir / "report.html"
    render_report(m, result["states"], result["summary"], report_path)
    channel_by_id = {
        state.get("id"): state.get("channel")
        for state in m.get("states") or []
    }
    for row in result.get("states") or []:
        row["channel"] = channel_by_id.get(row.get("id"))
    interaction_states_expected = sum(
        1
        for state in m.get("states") or []
        if state.get("channel") == "interaction"
    )
    return {
        "ok": bool(result["summary"].get("ok")),
        "source_id": source_id,
        **result,
        "interaction_states_expected": interaction_states_expected,
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
    "persist_semantic_report",
    "build_semantic_repair_packet",
    "record_semantic_attempt",
    "get_harness_run_state",
    "finalize_run",
    "generate_manifest",
    "verify_manifest",
]
