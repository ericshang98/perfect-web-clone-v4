"""Compact evidence for observations that may change between source captures.

These functions provide hints to the Agent. They never waive a fidelity check or
finalize a comparison mode.
"""
from __future__ import annotations

import asyncio
from typing import Any

_MODE_HINTS = {
    "runtime_media": "layout_behavior",
    "canvas_runtime": "layout_behavior",
    "live_text": "layout_style",
    "stateful_content": "stateful_pixels",
    "static_media": "static_pixels",
}


def _area(record: dict) -> float:
    bounds = record.get("bounds") or {}
    try:
        return max(0.0, float(bounds.get("width", 0))) * max(
            0.0, float(bounds.get("height", 0))
        )
    except (TypeError, ValueError):
        return 0.0


def merge_volatility_samples(samples: list[list[dict]]) -> list[dict]:
    """Merge temporal browser samples and count observable transitions."""

    if not samples:
        return []
    ordered_ids: list[str] = []
    observations: dict[str, list[dict]] = {}
    for sample in samples:
        for record in sample or []:
            record_id = str(record.get("id") or "").strip()
            if not record_id:
                continue
            if record_id not in observations:
                ordered_ids.append(record_id)
                observations[record_id] = []
            observations[record_id].append(record)

    merged: list[dict] = []
    total_samples = len(samples)
    for record_id in ordered_ids:
        records = observations[record_id]
        base = {
            key: value
            for key, value in records[0].items()
            if key != "signature"
        }
        signatures = [record.get("signature") for record in records]
        changed = sum(
            1
            for before, after in zip(signatures, signatures[1:])
            if before != after
        )
        base["changed_samples"] = changed
        base["total_samples"] = total_samples
        merged.append(base)
    return merged


def build_volatility_summary(
    records: list[dict], max_candidates: int = 64
) -> dict[str, Any]:
    """Return a size-bounded Agent evidence summary."""

    maximum = max(1, int(max_candidates))
    normalized: list[dict] = []
    for record in records or []:
        record_id = str(record.get("id") or "").strip()
        if not record_id:
            continue
        hint = str(record.get("hint") or "stateful_content")
        normalized.append(
            {
                "id": record_id,
                "tag": str(record.get("tag") or "").lower(),
                "bounds": dict(record.get("bounds") or {}),
                "hint": hint,
                "changed_samples": int(record.get("changed_samples") or 0),
                "total_samples": int(record.get("total_samples") or 1),
                "suggested_mode": _MODE_HINTS.get(hint, "static_pixels"),
                "requires_agent_decision": True,
            }
        )

    normalized.sort(key=lambda item: (-_area(item), item["id"]))
    kept = normalized[:maximum]
    return {
        "schema": 1,
        "sample_count": max(
            (item["total_samples"] for item in normalized),
            default=0,
        ),
        "candidates": kept,
        "truncated": max(0, len(normalized) - len(kept)),
    }


async def capture_volatility_samples(
    page: Any,
    inventory_script: str,
    sample_count: int = 3,
    interval_ms: int = 150,
    initial_sample: list[dict] | None = None,
) -> dict[str, Any]:
    """Collect a few cheap browser inventories and return one compact summary."""

    count = max(1, min(3, int(sample_count)))
    interval = max(0, int(interval_ms)) / 1000
    samples: list[list[dict]] = [list(initial_sample)] if initial_sample is not None else []
    remaining = max(0, count - len(samples))
    for _index in range(remaining):
        if samples and interval:
            await asyncio.sleep(interval)
        inventory = await page.evaluate(inventory_script)
        samples.append(list((inventory or {}).get("volatile_candidates") or []))
    return build_volatility_summary(merge_volatility_samples(samples))


__all__ = [
    "merge_volatility_samples",
    "build_volatility_summary",
    "capture_volatility_samples",
]
