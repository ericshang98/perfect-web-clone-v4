"""Build the smallest useful Agent context for one measured clone repair."""
from __future__ import annotations

import json
import math
from typing import Any

from core.comparison_contract import region_map


def _score_key(row: dict) -> tuple[int, float, str]:
    failed = row.get("status") == "fail"
    score = row.get("score")
    numeric = float(score) if score is not None else 1.0
    return (0 if failed else 1, numeric, str(row.get("id") or ""))


def select_worst_region(report: dict) -> dict:
    """Return the earliest actionable failure, lowest score first."""

    rows = list(report.get("regions") or [])
    if not rows:
        raise ValueError("report has no regions")
    rows.sort(key=_score_key)
    target = rows[0]
    if target.get("status") != "fail":
        raise ValueError("report has no failed region")
    return target


def _size(value: dict) -> int:
    return len(
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )


def _slice_utf8(value: str, length: int) -> str:
    if length <= 0:
        return ""
    return value.encode("utf-8")[:length].decode("utf-8", errors="ignore")


def _source_matches_owner(path: str, owner: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    owner = owner.lower()
    basename = normalized.rsplit("/", 1)[-1]
    return f"/{owner}/" in normalized or basename.startswith(owner)


def _compact_attempts(attempts: list[dict], target_id: str) -> list[dict]:
    compact = [
        {
            key: attempt.get(key)
            for key in ("target", "before", "after")
            if key in attempt
        }
        for attempt in attempts
        if attempt.get("target") == target_id
    ]
    return compact[-3:]


def _set_metrics(packet: dict) -> int:
    for _index in range(4):
        size = _size(packet)
        packet["text_bytes"] = size
        packet["estimated_tokens"] = math.ceil(size / 4)
    return _size(packet)


def build_repair_packet(
    report: dict,
    contract: dict,
    sources: dict[str, str],
    attempts: list[dict] | None = None,
    max_text_bytes: int = 16_384,
) -> dict[str, Any]:
    """Build a deterministic, owner-scoped repair packet under a byte budget."""

    budget = max(512, int(max_text_bytes))
    target = dict(select_worst_region(report))
    contract_regions = region_map(contract)
    target_id = target["id"]
    target_contract = contract_regions[target_id]
    owner = str(target_contract["owner"])

    candidate_regions = [
        {
            "id": row.get("id"),
            "owner": row.get("owner"),
            "status": row.get("status"),
            "score": row.get("score"),
            "failed_invariants": row.get("failed_invariants") or [],
        }
        for row in sorted(list(report.get("regions") or []), key=_score_key)[:3]
    ]
    packet: dict[str, Any] = {
        "schema": 1,
        "target": target,
        "contract": target_contract,
        "candidate_regions": candidate_regions,
        "attempts": _compact_attempts(list(attempts or []), target_id),
        "sources": {
            path: content
            for path, content in sorted(sources.items())
            if _source_matches_owner(path, owner)
        },
        "max_text_bytes": budget,
        "truncated_fields": [],
        "text_bytes": 0,
        "estimated_tokens": 0,
    }

    # Keep all required target evidence and spend the remaining budget only on
    # owner source text. Longest sources are reduced first.
    for _iteration in range(16):
        current = _set_metrics(packet)
        if current <= budget:
            break
        if not packet["sources"]:
            packet["budget_exceeded_by_required_evidence"] = current - budget
            break
        path = max(packet["sources"], key=lambda key: len(packet["sources"][key]))
        content = packet["sources"][path]
        overflow = current - budget
        keep = max(0, len(content.encode("utf-8")) - overflow - 96)
        trimmed = _slice_utf8(content, keep)
        if trimmed:
            packet["sources"][path] = trimmed
        else:
            del packet["sources"][path]
        if path not in packet["truncated_fields"]:
            packet["truncated_fields"].append(path)

    _set_metrics(packet)
    return packet


__all__ = ["select_worst_region", "build_repair_packet"]
