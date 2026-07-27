"""Monotonic bookkeeping for comparison-driven clone repairs."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def new_ledger(
    max_target_attempts: int = 5,
    max_total_attempts: int = 12,
) -> dict[str, Any]:
    return {
        "schema": 1,
        "limits": {
            "max_target_attempts": max(1, int(max_target_attempts)),
            "max_total_attempts": max(1, int(max_total_attempts)),
        },
        "attempts": [],
        "best": {},
        "best_candidates": {},
        "non_improving": {},
    }


def _target_attempts(ledger: dict, target: str) -> int:
    return sum(
        1 for attempt in ledger.get("attempts", []) if attempt.get("target") == target
    )


def record_attempt(
    ledger: dict,
    target: str,
    before: float,
    after: float,
    hard_gate_regressions: list[str],
    candidate_path: str | None = None,
) -> dict[str, Any]:
    """Record one candidate and accept it only when improvement is monotonic."""

    updated = deepcopy(ledger)
    limits = updated.get("limits") or {}
    if _target_attempts(updated, target) >= int(
        limits.get("max_target_attempts", 5)
    ):
        return {
            "recorded": False,
            "accepted": False,
            "plateaued": True,
            "stop_reason": "target attempt budget exhausted",
            "stop_code": "target_attempt_budget_exhausted",
            "restore_candidate": (updated.get("best_candidates") or {}).get(target),
            "ledger": updated,
        }
    if len(updated.get("attempts") or []) >= int(
        limits.get("max_total_attempts", 12)
    ):
        return {
            "recorded": False,
            "accepted": False,
            "plateaued": True,
            "stop_reason": "total attempt budget exhausted",
            "stop_code": "total_attempt_budget_exhausted",
            "restore_candidate": (updated.get("best_candidates") or {}).get(target),
            "ledger": updated,
        }

    before_value = float(before)
    after_value = float(after)
    previous_best = (updated.get("best") or {}).get(target)
    required_baseline = max(
        before_value,
        float(previous_best) if previous_best is not None else before_value,
    )
    regressions = list(hard_gate_regressions or [])
    accepted = after_value > required_baseline + 1e-12 and not regressions
    attempt = {
        "target": target,
        "before": before_value,
        "after": after_value,
        "delta": after_value - before_value,
        "accepted": accepted,
        "hard_gate_regressions": regressions,
        "candidate_path": candidate_path,
    }
    updated.setdefault("attempts", []).append(attempt)

    non_improving = updated.setdefault("non_improving", {})
    if accepted:
        updated.setdefault("best", {})[target] = after_value
        if candidate_path:
            updated.setdefault("best_candidates", {})[target] = candidate_path
        non_improving[target] = 0
    else:
        non_improving[target] = int(non_improving.get(target, 0)) + 1

    plateaued = non_improving.get(target, 0) >= 2
    return {
        "recorded": True,
        "accepted": accepted,
        "plateaued": plateaued,
        "stop_reason": "two non-improving attempts" if plateaued else None,
        "stop_code": "plateau" if plateaued else None,
        "restore_candidate": (
            None
            if accepted
            else (updated.get("best_candidates") or {}).get(target)
        ),
        "ledger": updated,
    }


__all__ = ["new_ledger", "record_attempt"]
