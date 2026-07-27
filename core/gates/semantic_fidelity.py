"""Contract-aware visual fidelity for stable and naturally changing regions."""
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as _ssim

from core.comparison_contract import validate_contract
from core.gates.fidelity import DEFAULT_THRESHOLD, _ssim_images

_CANVAS = (256, 256)
_GEOMETRY_TOLERANCE = 2.0
_ASPECT_TOLERANCE = 0.005
_MAX_FACT_ITEMS = 16
_MAX_FACT_STRING = 160
_MAX_FACT_DEPTH = 4


def _compact_fact(value: Any, *, depth: int = 0) -> Any:
    """Bound browser facts before they enter reports, ledgers, or Agent context."""

    if depth >= _MAX_FACT_DEPTH:
        return "<truncated>"
    if isinstance(value, dict):
        return {
            str(key)[:80]: _compact_fact(item, depth=depth + 1)
            for key, item in list(value.items())[:_MAX_FACT_ITEMS]
        }
    if isinstance(value, (list, tuple)):
        return [
            _compact_fact(item, depth=depth + 1)
            for item in list(value)[:_MAX_FACT_ITEMS]
        ]
    if isinstance(value, str):
        return value[:_MAX_FACT_STRING]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:_MAX_FACT_STRING]


def _gray(image: Image.Image) -> np.ndarray:
    return np.asarray(image.convert("L").resize(_CANVAS), dtype=np.float64)


def _box(bounds: dict) -> tuple[float, float, float, float]:
    return (
        float(bounds.get("x", 0)),
        float(bounds.get("y", 0)),
        float(bounds.get("width", 0)),
        float(bounds.get("height", 0)),
    )


def crop_box(
    image: Image.Image,
    bounds: dict,
    page_size: tuple[float, float],
) -> Image.Image:
    """Crop CSS-pixel bounds from an arbitrary raster size."""

    page_width, page_height = page_size
    sx = image.width / page_width if page_width else 1.0
    sy = image.height / page_height if page_height else 1.0
    x, y, width, height = _box(bounds)
    left = max(0, int(round(x * sx)))
    top = max(0, int(round(y * sy)))
    right = min(image.width, int(round((x + width) * sx)))
    bottom = min(image.height, int(round((y + height) * sy)))
    if right <= left or bottom <= top:
        return Image.new("RGB", (1, 1), "black")
    return image.crop((left, top, right, bottom))


def masked_ssim_2d(
    ref: Image.Image,
    cand: Image.Image,
    exclusions: list[dict],
) -> dict[str, Any]:
    """SSIM over all pixels outside explicit two-dimensional rectangles."""

    a = _gray(ref)
    b = _gray(cand)
    score, similarity = _ssim(a, b, data_range=255.0, full=True)
    if not exclusions:
        return {
            "score": min(1.0, max(0.0, float(score))),
            "excluded_fraction": 0.0,
            "excluded_bounds": [],
        }

    mask = np.zeros(_CANVAS[::-1], dtype=bool)
    sx = _CANVAS[0] / max(1, ref.width)
    sy = _CANVAS[1] / max(1, ref.height)
    normalized: list[dict[str, float]] = []
    for exclusion in exclusions:
        x, y, width, height = _box(exclusion)
        x0 = max(0, min(_CANVAS[0], int(round(x * sx))))
        y0 = max(0, min(_CANVAS[1], int(round(y * sy))))
        x1 = max(x0, min(_CANVAS[0], int(round((x + width) * sx))))
        y1 = max(y0, min(_CANVAS[1], int(round((y + height) * sy))))
        mask[y0:y1, x0:x1] = True
        normalized.append(
            {"x": x, "y": y, "width": width, "height": height}
        )
    kept = similarity[~mask]
    masked_score = float(kept.mean()) if kept.size else 0.0
    return {
        "score": min(1.0, max(0.0, masked_score)),
        "excluded_fraction": float(mask.mean()),
        "excluded_bounds": normalized,
    }


def _bounds_match(ref: dict, cand: dict) -> bool:
    if not all(key in ref and key in cand for key in ("x", "y", "width", "height")):
        return False
    try:
        if float(ref["width"]) <= 0 or float(ref["height"]) <= 0:
            return False
        if float(cand["width"]) <= 0 or float(cand["height"]) <= 0:
            return False
    except (TypeError, ValueError):
        return False
    return all(
        abs(float(ref.get(key, 0)) - float(cand.get(key, 0)))
        <= _GEOMETRY_TOLERANCE
        for key in ("x", "y", "width", "height")
    )


def _aspect_ratio(bounds: dict) -> float:
    height = float(bounds.get("height", 0))
    return float(bounds.get("width", 0)) / height if height else 0.0


def _style_match(ref: dict, cand: dict) -> bool:
    ref_style = ref.get("style") or {}
    cand_style = cand.get("style") or {}
    if not isinstance(ref_style, dict) or not ref_style:
        return False
    if not isinstance(cand_style, dict) or not cand_style:
        return False
    return all(cand_style.get(key) == value for key, value in ref_style.items())


def _invariant_failures(
    compare: list[str],
    ref: dict,
    cand: dict,
    behavior_ids: list[str] | None = None,
) -> list[str]:
    failed: list[str] = []
    ref_bounds = ref.get("bounds") or {}
    cand_bounds = cand.get("bounds") or {}
    for invariant in compare:
        if invariant == "bounds" and not _bounds_match(ref_bounds, cand_bounds):
            failed.append(invariant)
        elif invariant == "aspect_ratio" and abs(
            _aspect_ratio(ref_bounds) - _aspect_ratio(cand_bounds)
        ) > _ASPECT_TOLERANCE:
            failed.append(invariant)
        elif invariant == "container_style" and not _style_match(ref, cand):
            failed.append(invariant)
        elif invariant == "controls" and ref.get("controls") != cand.get("controls"):
            failed.append(invariant)
        elif invariant == "interaction" and ref.get("interaction") != cand.get(
            "interaction"
        ):
            failed.append(invariant)
        elif invariant == "behavior":
            source_replay = {
                str(item.get("id")): bool(item.get("passed", True))
                for item in (ref.get("behavior") or [])
            }
            observed = {
                str(item.get("id")): bool(item.get("passed"))
                for item in (cand.get("behavior") or [])
            }
            declared = behavior_ids or list(source_replay)
            if not declared or any(
                not source_replay.get(behavior_id, False)
                or not observed.get(behavior_id, False)
                for behavior_id in declared
            ):
                failed.append(invariant)
    return failed


def evaluate_contract(
    ref_png: str,
    cand_png: str,
    contract: dict,
    ref_facts: dict[str, dict],
    cand_facts: dict[str, dict],
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    """Evaluate every declared region without conflating volatile observations."""

    errors = validate_contract(contract)
    if errors:
        raise ValueError("; ".join(errors))
    ref_image = Image.open(ref_png).convert("RGB")
    cand_image = Image.open(cand_png).convert("RGB")
    ref_page_size = tuple(contract.get("ref_page_size") or ref_image.size)
    cand_page_size = tuple(contract.get("cand_page_size") or cand_image.size)

    rows: list[dict[str, Any]] = []
    static_weighted: list[tuple[float, float]] = []
    for region in contract["regions"]:
        region_id = region["id"]
        mode = region["mode"]
        row: dict[str, Any] = {
            "id": region_id,
            "owner": region["owner"],
            "importance": region["importance"],
            "mode": mode,
            "score": None,
            "failed_invariants": [],
            "excluded_observations": list(
                region.get("ignore_observations") or []
            ),
        }
        if mode == "residual":
            row.update(status="residual", reason=region["reason"])
            rows.append(row)
            continue

        if mode in {"layout_style", "layout_behavior"}:
            ref_region_facts = ref_facts.get(region_id)
            cand_region_facts = cand_facts.get(region_id)
            if not ref_region_facts:
                row.update(status="fail", reason="missing reference facts")
            elif not cand_region_facts:
                row.update(status="fail", reason="missing candidate facts")
            else:
                failed = _invariant_failures(
                    list(region.get("compare") or []),
                    ref_region_facts,
                    cand_region_facts,
                    [
                        str(behavior["id"])
                        for behavior in region.get("behaviors") or []
                    ],
                )
                row["failed_invariants"] = failed
                row["status"] = "fail" if failed else "pass"
                row["measurements"] = {
                    "reference": _compact_fact(ref_region_facts),
                    "candidate": _compact_fact(cand_region_facts),
                }
            rows.append(row)
            continue

        ref_bounds = region["bounds"]
        cand_region_facts = cand_facts.get(region_id)
        cand_bounds = (cand_region_facts or {}).get("bounds") or {}
        ref_crop = crop_box(ref_image, ref_bounds, ref_page_size)
        # The source rectangle is authoritative for pixel comparison.  A
        # displaced clone must not crop its own displaced box and pass merely
        # because the pixels inside that box are identical.
        cand_crop = crop_box(cand_image, ref_bounds, cand_page_size)
        exclusions = list(region.get("excluded_bounds") or [])
        pixel_report = (
            masked_ssim_2d(ref_crop, cand_crop, exclusions)
            if exclusions
            else {
                "score": _ssim_images(ref_crop, cand_crop),
                "excluded_fraction": 0.0,
                "excluded_bounds": [],
            }
        )
        score = float(pixel_report["score"])
        failed = [] if score >= threshold else ["pixels"]
        if not cand_region_facts or not _bounds_match(ref_bounds, cand_bounds):
            failed.append("bounds")
        replacement_invariants = [
            invariant
            for invariant in list(region.get("compare") or [])
            if invariant != "pixels"
        ]
        ref_region_facts = ref_facts.get(region_id) or {
            "bounds": ref_bounds
        }
        if replacement_invariants:
            if not cand_region_facts:
                failed.extend(replacement_invariants)
            else:
                failed.extend(
                    _invariant_failures(
                        replacement_invariants,
                        ref_region_facts,
                        cand_region_facts,
                        [
                            str(behavior["id"])
                            for behavior in region.get("behaviors") or []
                        ],
                    )
                )
        failed = list(dict.fromkeys(failed))
        row.update(
            status="pass" if not failed else "fail",
            score=score,
            failed_invariants=failed,
            pixel_report=pixel_report,
        )
        if replacement_invariants:
            row["measurements"] = {
                "reference": _compact_fact(ref_region_facts),
                "candidate": _compact_fact(cand_region_facts),
            }
        weight = float(ref_bounds["width"]) * float(ref_bounds["height"])
        static_weighted.append((score, weight))
        rows.append(row)

    static_weight = sum(weight for _score, weight in static_weighted)
    static_score = (
        sum(score * weight for score, weight in static_weighted) / static_weight
        if static_weight
        else None
    )
    rows.sort(
        key=lambda row: (
            0 if row["status"] == "fail" else 1,
            row["score"] if row["score"] is not None else 1.0,
        )
    )
    return {
        "ok": bool(rows) and all(row["status"] == "pass" for row in rows),
        "threshold": float(threshold),
        "static_score": static_score,
        "regions": rows,
        "raw_whole_page_score": _ssim_images(ref_image, cand_image),
    }


__all__ = [
    "crop_box",
    "masked_ssim_2d",
    "evaluate_contract",
]
