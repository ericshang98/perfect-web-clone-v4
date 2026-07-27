"""Fail-closed visual verification across responsive views and UI states.

The source checklist is the finite universe of observable views.  A semantic
contract may classify a region as dynamic, but it may never make an entire
mobile breakpoint, scroll state, or menu state disappear from verification.
This module deliberately consumes compact *measured* per-view reports; it
doesn't copy DOM/CSS facts into every view and therefore keeps Agent context and
ledger payloads bounded.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping


POLICY_VERSION = "visual-state-v1"
_STATIC = "static_pixels"
# A named state is stable after replay and therefore still has a pixel raster.
# Only naturally-changing layout/behavior regions (video, clocks, canvases) are
# exempt from raw frame comparison.
_DYNAMIC = {"layout_style", "layout_behavior"}


def _strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if isinstance(value, str) and value]


def _source_view_map(source_views: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in source_views:
        view_id = str(item.get("id") or "")
        if view_id and view_id not in result:
            result[view_id] = dict(item)
    return result


def _contract_regions(contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(region.get("id")): dict(region)
        for region in (contract.get("regions") or [])
        if isinstance(region, Mapping) and str(region.get("id") or "")
    }


def validate_contract_coverage(
    contract: Mapping[str, Any],
    source_views: Iterable[Mapping[str, Any]],
) -> list[str]:
    """Ensure exact checklist-view and critical-owner coverage before scoring.

    ``source_views`` is source-derived evidence (not Agent text).  Each row has
    a canonical ``id`` and a small list of critical ``{id, owner}`` entries.
    The contract's coverage table maps every view to declared region/owner ids.
    No inferred default or desktop fallback is accepted.
    """

    errors: list[str] = []
    source_map = _source_view_map(source_views)
    expected_ids = list(source_map)
    coverage = contract.get("coverage") if isinstance(contract, Mapping) else None
    if not isinstance(coverage, Mapping):
        return ["contract needs deterministic coverage for every required source view"]
    declared_ids = _strings(coverage.get("required_view_ids"))
    if len(declared_ids) != len(set(declared_ids)):
        errors.append("coverage.required_view_ids contains duplicate view ids")
    if set(declared_ids) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(declared_ids))
        extra = sorted(set(declared_ids) - set(expected_ids))
        if missing:
            errors.append("coverage missing required source views: " + ", ".join(missing))
        if extra:
            errors.append("coverage declares unknown views: " + ", ".join(extra))

    views = coverage.get("views")
    if not isinstance(views, Mapping):
        return [*errors, "coverage.views must map every required view id"]
    regions = _contract_regions(contract)
    for view_id in expected_ids:
        view_coverage = views.get(view_id)
        if not isinstance(view_coverage, Mapping):
            errors.append(f"coverage missing view mapping for {view_id}")
            continue
        region_ids = _strings(view_coverage.get("region_ids"))
        owner_ids = _strings(view_coverage.get("owner_ids"))
        unknown_regions = sorted(set(region_ids) - set(regions))
        if unknown_regions:
            errors.append(
                f"coverage {view_id} names unknown region ids: "
                + ", ".join(unknown_regions)
            )
        # Every visible source region is part of the finite page contract, not
        # only the handful labelled critical.  Otherwise an Agent could author
        # a hero-only contract and silently omit the product grid or footer.
        source_regions = (
            source_map[view_id].get("regions")
            or source_map[view_id].get("critical_regions")
            or []
        )
        for source_region in source_regions:
            if not isinstance(source_region, Mapping):
                errors.append(f"source region evidence for {view_id} is invalid")
                continue
            region_id = str(source_region.get("id") or "")
            owner = str(source_region.get("owner") or "")
            if not region_id or not owner:
                errors.append(f"source region evidence for {view_id} lacks id/owner")
                continue
            if region_id not in region_ids:
                errors.append(
                    f"coverage {view_id} omits source region {region_id}"
                )
            if owner not in owner_ids:
                errors.append(f"coverage {view_id} omits source owner {owner}")
            declared = regions.get(region_id) or {}
            if declared.get("owner") != owner:
                errors.append(
                    f"contract region {region_id} does not own source owner {owner}"
                )
    return errors


def _failure(code: str, **fields: Any) -> dict[str, Any]:
    return {"code": code, **fields}


def _valid_static_measurement(row: Mapping[str, Any]) -> bool:
    pixel = row.get("pixel_report")
    score = pixel.get("score") if isinstance(pixel, Mapping) else None
    return isinstance(score, (int, float)) and not isinstance(score, bool)


def _valid_dynamic_measurement(row: Mapping[str, Any]) -> bool:
    measurements = row.get("measurements")
    return (
        isinstance(measurements, Mapping)
        and isinstance(measurements.get("reference"), Mapping)
        and isinstance(measurements.get("candidate"), Mapping)
    )


def _evaluate_view(
    view_id: str,
    expected_region_ids: list[str],
    regions: Mapping[str, Mapping[str, Any]],
    measurement: Mapping[str, Any] | None,
    *,
    contract_digest: str,
) -> list[dict[str, Any]]:
    if not expected_region_ids:
        return [_failure("zero_region_view")]
    if measurement is None:
        return [_failure("missing_measurement")]
    if measurement.get("measured") is not True:
        return [_failure("unmeasured_view")]
    if measurement.get("policy_version") != POLICY_VERSION:
        return [_failure("stale_policy")]
    if measurement.get("contract_digest") != contract_digest:
        return [_failure("stale_contract")]
    rows = measurement.get("regions")
    if not isinstance(rows, list):
        return [_failure("missing_region_measurements")]
    rows_by_id: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        region_id = str(row.get("id") or "")
        if region_id and region_id not in rows_by_id:
            rows_by_id[region_id] = row
    failures: list[dict[str, Any]] = []
    for region_id in expected_region_ids:
        declared = regions.get(region_id)
        row = rows_by_id.get(region_id)
        if declared is None:
            failures.append(_failure("unknown_contract_region", id=region_id))
            continue
        if row is None:
            failures.append(_failure("missing_region_measurement", id=region_id))
            continue
        if row.get("owner") != declared.get("owner"):
            failures.append(_failure("owner_mismatch", id=region_id))
            continue
        mode = declared.get("mode")
        if row.get("mode") not in {None, mode}:
            failures.append(_failure("mode_mismatch", id=region_id))
            continue
        if mode in {_STATIC, "stateful_pixels"} and not _valid_static_measurement(row):
            failures.append(_failure("unmeasured_static_pixels", id=region_id))
            continue
        if mode in _DYNAMIC and not _valid_dynamic_measurement(row):
            failures.append(_failure("unmeasured_dynamic_invariants", id=region_id))
            continue
        if row.get("status") != "pass":
            failures.append(
                {
                    "id": region_id,
                    "failed_invariants": list(row.get("failed_invariants") or []),
                    "score": row.get("score"),
                }
            )
    return failures


def evaluate_visual_state_reports(
    contract: Mapping[str, Any],
    source_views: Iterable[Mapping[str, Any]],
    measured_views: Iterable[Mapping[str, Any]],
    *,
    contract_digest: str,
) -> dict[str, Any]:
    """Aggregate measured per-view reports under one bounded policy.

    Dynamic/frame content does not use raw frame/whole-page similarity as a
    gate.  It is retained in each view purely as a diagnostic.  Static pixels
    must include a measured pixel report; dynamic regions must include source
    and candidate invariant facts.
    """

    source_map = _source_view_map(source_views)
    required_ids = list(source_map)
    coverage_errors = validate_contract_coverage(contract, source_map.values())
    measurements: dict[str, Mapping[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for view in measured_views:
        if not isinstance(view, Mapping):
            continue
        view_id = str(view.get("view_id") or "")
        if not view_id:
            continue
        if view_id in measurements:
            duplicate_ids.add(view_id)
        else:
            measurements[view_id] = view
    coverage = contract.get("coverage") or {}
    view_coverage = coverage.get("views") if isinstance(coverage, Mapping) else {}
    regions = _contract_regions(contract)
    failures_by_view: dict[str, list[dict[str, Any]]] = {}
    view_reports: dict[str, dict[str, Any]] = {}
    for view_id in required_ids:
        declared = view_coverage.get(view_id) if isinstance(view_coverage, Mapping) else None
        region_ids = _strings(declared.get("region_ids")) if isinstance(declared, Mapping) else []
        failures = _evaluate_view(
            view_id,
            region_ids,
            regions,
            measurements.get(view_id),
            contract_digest=contract_digest,
        )
        if view_id in duplicate_ids:
            failures.append(_failure("duplicate_measurement"))
        if failures:
            failures_by_view[view_id] = failures
        measurement = measurements.get(view_id) or {}
        view_reports[view_id] = {
            "ok": not failures,
            "raw_whole_page_score": measurement.get("raw_whole_page_score"),
            "raw_frame_score": measurement.get("raw_frame_score"),
            "candidate_png_digest": measurement.get("candidate_png_digest"),
        }
    if coverage_errors:
        failures_by_view.setdefault("__coverage__", []).extend(
            _failure("incomplete_contract_coverage", detail=error)
            for error in coverage_errors
        )
    measured_ids = [
        view_id
        for view_id in required_ids
        if (measurements.get(view_id) or {}).get("measured") is True
    ]
    unexpected = sorted(set(measurements) - set(required_ids))
    if unexpected:
        failures_by_view.setdefault("__coverage__", []).append(
            _failure("unexpected_measured_view", view_ids=unexpected)
        )
    return {
        "ok": not failures_by_view,
        "policy_version": POLICY_VERSION,
        "contract_digest": contract_digest,
        "required_view_ids": required_ids,
        "measured_view_ids": measured_ids,
        "failures_by_view": failures_by_view,
        "views": view_reports,
    }


__all__ = [
    "POLICY_VERSION",
    "validate_contract_coverage",
    "evaluate_visual_state_reports",
]
