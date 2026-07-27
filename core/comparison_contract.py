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
_BEHAVIOR_ASSERTIONS = {
    "visible",
    "hidden",
    "attribute_equals",
    "text_contains",
}
_VALID_INVARIANTS = {
    "pixels",
    "bounds",
    "aspect_ratio",
    "container_style",
    "controls",
    "interaction",
    "behavior",
}
_MAX_CONTRACT_BYTES = 131_072
_MAX_TOTAL_BEHAVIORS = 64
_MAX_TOTAL_PREREQUISITES = 256


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
    try:
        serialized_bytes = len(
            json.dumps(
                contract,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    except (TypeError, ValueError):
        return ["contract must be JSON serializable"]
    if serialized_bytes > _MAX_CONTRACT_BYTES:
        errors.append(
            f"contract exceeds {_MAX_CONTRACT_BYTES} serialized bytes"
        )
    if contract.get("schema") != SCHEMA_VERSION:
        errors.append(f"schema must equal {SCHEMA_VERSION}")
    regions = contract.get("regions")
    if not isinstance(regions, list) or not regions:
        errors.append("regions must be a non-empty list")
        return errors
    if len(regions) > 64:
        errors.append("regions supports at most 64 entries")

    seen: set[str] = set()
    total_behaviors = 0
    total_prerequisites = 0
    for index, region in enumerate(regions):
        prefix = f"regions[{index}]"
        if not isinstance(region, dict):
            errors.append(f"{prefix} must be an object")
            continue
        region_id = str(region.get("id") or "").strip()
        if not region_id:
            errors.append(f"{prefix} missing id")
        elif len(region_id) > 120:
            errors.append(f"{prefix} id exceeds 120 characters")
        elif region_id in seen:
            errors.append(f"duplicate region id {region_id!r}")
        seen.add(region_id)

        owner = str(region.get("owner") or "").strip()
        if not owner:
            errors.append(f"{prefix} missing owner")
        elif len(owner) > 120:
            errors.append(f"{prefix} owner exceeds 120 characters")
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
        if isinstance(compare, list):
            if len(compare) > 8:
                errors.append(f"{prefix} supports at most 8 comparison invariants")
            unknown = [
                item
                for item in compare
                if not isinstance(item, str) or item not in _VALID_INVARIANTS
            ]
            if unknown:
                errors.append(f"{prefix} contains unknown comparison invariants")
        if mode in {"static_pixels", "stateful_pixels"} and "pixels" not in (
            compare or []
        ):
            errors.append(f"{prefix} {mode} needs pixels comparison")
        if mode == "stateful_pixels" and not region.get("state"):
            errors.append(f"{prefix} stateful_pixels needs a named state")

        if mode in _NON_STATIC_MODES:
            if not str(region.get("reason") or "").strip():
                errors.append(f"{prefix} non-static comparison needs reason")
            elif len(str(region.get("reason"))) > 320:
                errors.append(f"{prefix} reason exceeds 320 characters")
            ignored = region.get("ignore_observations")
            if not isinstance(ignored, list) or not ignored:
                errors.append(
                    f"{prefix} non-static comparison needs ignore_observations"
                )
            elif (
                len(ignored) > 16
                or any(
                    not isinstance(item, str) or not item.strip() or len(item) > 160
                    for item in ignored
                )
            ):
                errors.append(
                    f"{prefix} ignore_observations must contain at most "
                    "16 strings of 160 characters"
                )
            replacement = [item for item in (compare or []) if item != "pixels"]
            if not replacement:
                errors.append(f"{prefix} needs a replacement invariant")
            required_layout = {"bounds", "aspect_ratio", "container_style"}
            if not required_layout.issubset(set(compare or [])):
                errors.append(
                    f"{prefix} {mode} needs bounds, aspect_ratio, container_style"
                )
            if mode == "layout_behavior" and not (
                {"controls", "behavior"} & set(compare or [])
            ):
                errors.append(f"{prefix} layout_behavior needs controls or behavior")

        if "behavior" in (compare or []):
            behaviors = region.get("behaviors")
            if not isinstance(behaviors, list) or not behaviors:
                errors.append(f"{prefix} behavior comparison needs behaviors")
            else:
                if len(behaviors) > 16:
                    errors.append(f"{prefix} supports at most 16 behaviors")
                total_behaviors += len(behaviors)
                seen_behaviors: set[str] = set()
                for behavior_index, behavior in enumerate(behaviors):
                    behavior_prefix = (
                        f"{prefix}.behaviors[{behavior_index}]"
                    )
                    if not isinstance(behavior, dict):
                        errors.append(f"{behavior_prefix} must be an object")
                        continue
                    behavior_id = str(behavior.get("id") or "").strip()
                    if not behavior_id:
                        errors.append(f"{behavior_prefix} missing id")
                    elif len(behavior_id) > 120:
                        errors.append(f"{behavior_prefix} id exceeds 120 characters")
                    elif behavior_id in seen_behaviors:
                        errors.append(
                            f"{prefix} duplicate behavior id {behavior_id!r}"
                        )
                    seen_behaviors.add(behavior_id)
                    if not str(behavior.get("trigger") or "").strip():
                        errors.append(f"{behavior_prefix} missing trigger")
                    elif len(str(behavior.get("trigger"))) > 512:
                        errors.append(f"{behavior_prefix} trigger exceeds 512 characters")
                    target = behavior.get("target")
                    if target is not None and len(str(target)) > 512:
                        errors.append(f"{behavior_prefix} target exceeds 512 characters")
                    before = behavior.get("before")
                    if isinstance(before, list):
                        total_prerequisites += len(before)
                    if before is not None and (
                        not isinstance(before, list)
                        or len(before) > 8
                        or any(
                            not isinstance(selector, str)
                            or not selector.strip()
                            or len(selector) > 512
                            for selector in before
                        )
                    ):
                        errors.append(
                            f"{behavior_prefix} before must contain at most "
                            "8 selector strings"
                        )
                    assertion = behavior.get("assert", "visible")
                    if assertion not in _BEHAVIOR_ASSERTIONS:
                        errors.append(
                            f"{behavior_prefix} assertion {assertion!r} is invalid"
                        )
                    if assertion in {"attribute_equals", "text_contains"} and (
                        "value" not in behavior
                    ):
                        errors.append(
                            f"{behavior_prefix} {assertion} needs value"
                        )
                    if "value" in behavior and len(str(behavior.get("value"))) > 320:
                        errors.append(f"{behavior_prefix} value exceeds 320 characters")
                    if assertion == "attribute_equals" and not str(
                        behavior.get("attribute") or ""
                    ).strip():
                        errors.append(
                            f"{behavior_prefix} attribute_equals needs attribute"
                        )

        if mode == "residual":
            if not str(region.get("reason") or "").strip():
                errors.append(f"{prefix} residual needs reason")
            elif len(str(region.get("reason"))) > 320:
                errors.append(f"{prefix} reason exceeds 320 characters")
            if importance == "critical":
                errors.append(f"{prefix} critical residual is a hard failure")

    if total_behaviors > _MAX_TOTAL_BEHAVIORS:
        errors.append(
            f"contract supports at most {_MAX_TOTAL_BEHAVIORS} total behaviors"
        )
    if total_prerequisites > _MAX_TOTAL_PREREQUISITES:
        errors.append(
            "contract supports at most "
            f"{_MAX_TOTAL_PREREQUISITES} total prerequisite selectors"
        )
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
