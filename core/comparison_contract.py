"""Semantic comparison contract for Agent-guided clone verification.

The current Agent authors this small JSON document after understanding the
source page. Deterministic gates consume it; they never infer that a difficult
region may be ignored.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
VALID_MODES = {
    "static_pixels",
    "layout_style",
    "layout_behavior",
    "stateful_pixels",
    "residual",
}
VALID_IMPORTANCE = {"critical", "important", "supporting"}
_NON_STATIC_MODES = {"layout_style", "layout_behavior"}


def _valid_bounds(bounds: Any) -> bool:
    if not isinstance(bounds, dict):
        return False
    try:
        return (
            float(bounds.get("width", 0)) > 0
            and float(bounds.get("height", 0)) > 0
            and all(
                isinstance(bounds.get(key, 0), (int, float))
                for key in ("x", "y", "width", "height")
            )
        )
    except (TypeError, ValueError):
        return False


def validate_contract(contract: dict) -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""

    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["contract must be an object"]
    if contract.get("schema") != SCHEMA_VERSION:
        errors.append(f"schema must equal {SCHEMA_VERSION}")
    regions = contract.get("regions")
    if not isinstance(regions, list) or not regions:
        errors.append("regions must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, region in enumerate(regions):
        prefix = f"regions[{index}]"
        if not isinstance(region, dict):
            errors.append(f"{prefix} must be an object")
            continue
        region_id = str(region.get("id") or "").strip()
        if not region_id:
            errors.append(f"{prefix} missing id")
        elif region_id in seen:
            errors.append(f"duplicate region id {region_id!r}")
        seen.add(region_id)

        owner = str(region.get("owner") or "").strip()
        if not owner:
            errors.append(f"{prefix} missing owner")
        if not _valid_bounds(region.get("bounds")):
            errors.append(f"{prefix} needs positive numeric bounds")

        importance = region.get("importance")
        if importance not in VALID_IMPORTANCE:
            errors.append(f"{prefix} importance {importance!r} is invalid")
        mode = region.get("mode")
        if mode not in VALID_MODES:
            errors.append(f"{prefix} mode {mode!r} is invalid")
            continue

        compare = region.get("compare")
        if mode != "residual" and (not isinstance(compare, list) or not compare):
            errors.append(f"{prefix} needs at least one replacement invariant")
        if mode == "static_pixels" and "pixels" not in (compare or []):
            errors.append(f"{prefix} static_pixels needs pixels comparison")
        if mode == "stateful_pixels" and not region.get("state"):
            errors.append(f"{prefix} stateful_pixels needs a named state")

        if mode in _NON_STATIC_MODES:
            if not str(region.get("reason") or "").strip():
                errors.append(f"{prefix} non-static comparison needs reason")
            ignored = region.get("ignore_observations")
            if not isinstance(ignored, list) or not ignored:
                errors.append(
                    f"{prefix} non-static comparison needs ignore_observations"
                )
            replacement = [item for item in (compare or []) if item != "pixels"]
            if not replacement:
                errors.append(f"{prefix} needs a replacement invariant")

        if mode == "residual":
            if not str(region.get("reason") or "").strip():
                errors.append(f"{prefix} residual needs reason")
            if importance == "critical":
                errors.append(f"{prefix} critical residual is a hard failure")

    return errors


def save_contract(contract: dict, path: str | Path) -> None:
    """Validate and persist a human-readable comparison contract."""

    errors = validate_contract(contract)
    if errors:
        raise ValueError("; ".join(errors))
    Path(path).write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_contract(path: str | Path) -> dict:
    """Load and validate a comparison contract."""

    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_contract(contract)
    if errors:
        raise ValueError("; ".join(errors))
    return contract


def region_map(contract: dict) -> dict[str, dict]:
    """Map region id to its contract entry after validation."""

    errors = validate_contract(contract)
    if errors:
        raise ValueError("; ".join(errors))
    return {region["id"]: region for region in contract["regions"]}


__all__ = [
    "SCHEMA_VERSION",
    "VALID_MODES",
    "VALID_IMPORTANCE",
    "validate_contract",
    "save_contract",
    "load_contract",
    "region_map",
]
