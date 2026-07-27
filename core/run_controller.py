"""Pure state reduction for the Agent Harness run ledger.

This module owns no filesystem, browser, or model integration.  Gate tools feed
measured evidence into these reducers and persist the returned ledger.  Keeping
the transition rules here makes a red gate an enforceable repair obligation
instead of a prose suggestion an Agent can accidentally skip.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from core.repair_packet import select_worst_region
from core.visual_state_gate import POLICY_VERSION


REQUIRED_GATES = (
    "capture_integrity",
    "critical_structure",
    "interactions",
    "build",
    "fingerprints",
    "weight",
    "runtime",
    "responsive",
    "visual",
)
AFFECTED_HARD_GATES = (
    "critical_structure",
    "interactions",
    "build",
    "fingerprints",
    "weight",
    "runtime",
    "responsive",
)
AUTHORIZED_STOP_REASONS = frozenset(
    {
        "plateau",
        "target_attempt_budget_exhausted",
        "total_attempt_budget_exhausted",
        "hard_token_stop",
        "proven_technical_ceiling",
    }
)
TERMINAL_STATUSES = frozenset(
    {"ready_for_user_review", "failed_with_residuals"}
)
_ORCHESTRATION_FIELDS = frozenset(
    {
        "execution_ok",
        "gate_status",
        "must_continue",
        "next_action",
        "terminal_allowed",
        "semantic_report_digest",
        "semantic_report_path",
        "objective",
        "run_state_recorded",
        "persistence_error",
    }
)


def semantic_report_payload(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return the measured report without transient controller output fields."""

    return {
        key: deepcopy(value)
        for key, value in report.items()
        if key not in _ORCHESTRATION_FIELDS
    }


def semantic_report_digest(report: Mapping[str, Any]) -> str:
    """Return a stable digest for stale/tampered report detection."""

    canonical = json.dumps(
        semantic_report_payload(report),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def semantic_objective(
    report: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> float:
    """Convert mixed pixel/invariant evidence into one deterministic objective.

    Every declared comparison contributes exactly one value. Pixel comparisons
    use their measured region score; invariant comparisons contribute 1 when
    satisfied and 0 when named in ``failed_invariants``. Consequently a
    layout/behavior-only failure still has a numeric, reproducible objective
    without asking an Agent to invent a score.
    """

    contracts = {
        str(region.get("id")): region
        for region in (contract.get("regions") or [])
        if region.get("id") is not None
    }
    values: list[float] = []
    for row in report.get("regions") or []:
        region_id = str(row.get("id") or "")
        declaration = contracts.get(region_id) or {}
        comparisons = list(declaration.get("compare") or [])
        failed = {str(item) for item in (row.get("failed_invariants") or [])}
        if not comparisons:
            values.append(1.0 if row.get("status") == "pass" else 0.0)
            continue
        for comparison in comparisons:
            name = str(comparison)
            if name == "pixels":
                score = row.get("score")
                values.append(
                    min(1.0, max(0.0, float(score)))
                    if isinstance(score, (int, float))
                    and not isinstance(score, bool)
                    else (1.0 if row.get("status") == "pass" else 0.0)
                )
            else:
                values.append(0.0 if name in failed else 1.0)
    if not values:
        return 1.0 if report.get("ok") else 0.0
    return round(sum(values) / len(values), 12)


def _gate_status(ledger: Mapping[str, Any], gate: str) -> str:
    result = (ledger.get("gate_results") or {}).get(gate) or {}
    if (
        gate == "visual"
        and str(result.get("status") or "pending") == "pass"
        and not visual_state_evidence_complete(ledger)
    ):
        # A generic green bit cannot be carried forward into a strict run.
        # Treat it as pending rather than allowing terminalization to infer
        # responsive/state coverage that was never measured.
        return "pending"
    return str(result.get("status") or "pending")


def visual_state_evidence_complete(ledger: Mapping[str, Any]) -> bool:
    """Return whether a v4 Harness visual pass proves every required view.

    Schema <= 3 ledgers predate visual-state contracts and are intentionally
    readable for migration.  Fresh assembly writes schema 4 and must carry the
    exact coverage report emitted by :mod:`core.visual_state_gate`.
    """

    try:
        strict = int(ledger.get("schema") or 0) >= 4
    except (TypeError, ValueError):
        strict = False
    if not strict:
        return True
    result = (ledger.get("gate_results") or {}).get("visual") or {}
    details = result.get("details")
    if not isinstance(details, Mapping):
        return False
    if details.get("policy_version") != POLICY_VERSION:
        return False
    expected_digest = ((ledger.get("comparison_contract") or {}).get("digest"))
    if expected_digest and details.get("contract_digest") != expected_digest:
        return False
    required = details.get("required_view_ids")
    measured = details.get("measured_view_ids")
    if (
        not isinstance(required, list)
        or not required
        or not isinstance(measured, list)
        or len(required) != len(set(required))
        or len(measured) != len(set(measured))
        or set(required) != set(measured)
    ):
        return False
    failures = details.get("failures_by_view")
    return isinstance(failures, Mapping) and not failures


def _required_gates(ledger: Mapping[str, Any]) -> tuple[str, ...]:
    """Allow later gate modules to extend terminalization without reducer edits."""

    declared = ledger.get("required_gates")
    if isinstance(declared, list) and all(
        isinstance(gate, str) and gate for gate in declared
    ):
        return tuple(dict.fromkeys((*REQUIRED_GATES, *declared)))
    return REQUIRED_GATES


def _matching_authorized_stop(ledger: Mapping[str, Any]) -> dict[str, Any] | None:
    stop = ledger.get("authorized_stop")
    pending = ledger.get("pending_repair")
    if not isinstance(stop, dict) or not isinstance(pending, dict):
        return None
    if stop.get("reason") not in AUTHORIZED_STOP_REASONS:
        return None
    if stop.get("gate") != pending.get("gate"):
        return None
    if stop.get("target") != pending.get("target"):
        return None
    if stop.get("report_digest") != pending.get("report_digest"):
        return None
    if int(stop.get("epoch") or -1) != int(pending.get("epoch") or -1):
        return None
    residuals = ledger.get("residuals") or []
    if not any(
        residual.get("gate") == stop.get("gate")
        and residual.get("target") == stop.get("target")
        and residual.get("stop_reason") == stop.get("reason")
        for residual in residuals
        if isinstance(residual, dict)
    ):
        return None
    return dict(stop)


def harness_decision(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Return the one next action allowed by the durable run state."""

    status = str(ledger.get("status") or "running")
    if status in TERMINAL_STATUSES:
        return {
            "execution_ok": True,
            "gate_status": "pass" if status == "ready_for_user_review" else "fail",
            "must_continue": False,
            "next_action": None,
            "terminal_allowed": [status],
        }

    active_attempt = ledger.get("active_attempt")
    if isinstance(active_attempt, dict):
        latest = ledger.get("latest_semantic_report") or {}
        if latest.get("digest") == active_attempt.get("before_report_digest"):
            return {
                "execution_ok": True,
                "gate_status": _gate_status(ledger, "visual"),
                "must_continue": True,
                "next_action": "reverify:visual",
                "terminal_allowed": [],
            }
        stale = stale_attempt_gates(ledger)
        if stale:
            return {
                "execution_ok": True,
                "gate_status": "pending",
                "must_continue": True,
                "next_action": "verify_hard_gates:" + ",".join(stale),
                "terminal_allowed": [],
            }
        return {
            "execution_ok": True,
            "gate_status": _gate_status(ledger, "visual"),
            "must_continue": True,
            "next_action": "record_semantic_attempt",
            "terminal_allowed": [],
        }

    gates = ledger.get("gate_results") or {}
    first_pending: str | None = None
    first_failed: str | None = None
    for gate in _required_gates(ledger):
        gate_status = str((gates.get(gate) or {}).get("status") or "pending")
        if gate_status == "fail":
            first_failed = gate
            break
        if gate_status != "pass":
            first_pending = gate
            break

    if first_failed is not None:
        pending = ledger.get("pending_repair") or {}
        target = str(pending.get("target") or first_failed)
        authorized_stop = _matching_authorized_stop(ledger)
        if (
            authorized_stop is not None
            and authorized_stop.get("gate") == first_failed
        ):
            return {
                "execution_ok": True,
                "gate_status": "fail",
                "must_continue": False,
                "next_action": "finalize:failed_with_residuals",
                "terminal_allowed": ["failed_with_residuals"],
            }
        if pending.get("reverify_required"):
            return {
                "execution_ok": True,
                "gate_status": "fail",
                "must_continue": True,
                "next_action": f"reverify:{pending.get('gate') or first_failed}",
                "terminal_allowed": [],
            }
        return {
            "execution_ok": True,
            "gate_status": "fail",
            "must_continue": True,
            "next_action": f"repair:{target}",
            "terminal_allowed": [],
        }

    if first_pending is not None:
        return {
            "execution_ok": True,
            "gate_status": _gate_status(ledger, first_pending),
            "must_continue": True,
            "next_action": f"run_gate:{first_pending}",
            "terminal_allowed": [],
        }

    return {
        "execution_ok": True,
        "gate_status": "pass",
        "must_continue": False,
        "next_action": "finalize:ready_for_user_review",
        "terminal_allowed": ["ready_for_user_review"],
    }


def apply_semantic_report(
    ledger: Mapping[str, Any],
    report: Mapping[str, Any],
    *,
    digest: str,
    objective: float,
    report_path: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Record fresh semantic evidence and create/clear its repair obligation."""

    updated = deepcopy(dict(ledger))
    # Schema 4 makes view/state coverage part of visual evidence.  A resumed
    # legacy run may continue, but its old single-desktop green bit is never
    # accepted as evidence for the new contract.
    try:
        is_legacy = int(updated.get("schema") or 0) < 4
    except (TypeError, ValueError):
        is_legacy = True
    if is_legacy:
        updated["schema"] = 4
    gates = updated.setdefault("gate_results", {})
    visual_details = report.get("visual_details")
    gate_status = "pass" if bool(report.get("ok")) else "fail"
    try:
        target_row = select_worst_region(dict(report))
    except ValueError:
        target_row = None
    target = str((target_row or {}).get("id") or "visual")
    owner = str((target_row or {}).get("owner") or target)
    repair_limits = (
        updated.get("repair_limits")
        or updated.get("limits")
        or {"max_target_attempts": 5, "max_total_attempts": 12}
    )
    target_attempts = sum(
        1
        for attempt in (updated.get("attempts") or [])
        if attempt.get("target") == target
    )
    total_attempts = len(updated.get("attempts") or [])
    attempts_remaining = max(
        0,
        min(
            int(repair_limits.get("max_target_attempts", 5)) - target_attempts,
            int(repair_limits.get("max_total_attempts", 12)) - total_attempts,
        ),
    )
    visual_gate = {
        "status": gate_status,
        "epoch": int(updated.get("verification_epoch") or 0),
        "evidence": [f"{report_path}#{digest}"],
        "objective": float(objective),
    }
    if isinstance(visual_details, Mapping):
        visual_gate["details"] = deepcopy(dict(visual_details))
    gates["visual"] = visual_gate
    if gate_status == "pass" and not visual_state_evidence_complete(updated):
        gates["visual"]["status"] = "pending"
        gate_status = "pending"
    updated["latest_semantic_report"] = {
        "path": report_path,
        "digest": digest,
        "objective": float(objective),
        "status": gate_status,
        "target": None if gate_status == "pass" else target,
    }
    updated["status"] = "running"
    if gate_status == "fail":
        updated["phase"] = "repair"
        updated["pending_repair"] = {
            "gate": "visual",
            "target": target,
            "owner": owner,
            "report_digest": digest,
            "objective": float(objective),
            "epoch": int(updated.get("verification_epoch") or 0),
            "evidence": [f"{report_path}#{digest}"],
            "attempts_remaining": attempts_remaining,
        }
        stop = updated.get("authorized_stop")
        stop_is_stale = isinstance(stop, dict) and (
            stop.get("gate") != "visual"
            or stop.get("target") != target
            or stop.get("report_digest") != digest
            or int(stop.get("epoch") or -1)
            != int(updated["pending_repair"]["epoch"])
        )
        if stop_is_stale:
            updated.pop("authorized_stop", None)
            updated["residuals"] = [
                residual
                for residual in (updated.get("residuals") or [])
                if not (
                    isinstance(residual, dict)
                    and residual.get("gate") == "visual"
                    and residual.get("target") == target
                )
            ]
    else:
        updated["phase"] = "verify"
        updated.pop("pending_repair", None)
        updated.pop("authorized_stop", None)
        updated["residuals"] = [
            residual
            for residual in (updated.get("residuals") or [])
            if not (
                isinstance(residual, dict)
                and residual.get("gate") == "visual"
            )
        ]
    return updated, harness_decision(updated)


def start_repair_epoch(
    ledger: Mapping[str, Any],
    *,
    target: str,
    owner: str,
    report_digest: str,
    objective: float,
    snapshot_path: str,
) -> dict[str, Any]:
    """Start one candidate epoch and invalidate every code-affected hard gate."""

    updated = deepcopy(dict(ledger))
    epoch = int(updated.get("verification_epoch") or 0) + 1
    baseline = {
        gate: _gate_status(updated, gate) for gate in AFFECTED_HARD_GATES
    }
    baseline_results = {
        gate: deepcopy(
            (updated.get("gate_results") or {}).get(gate)
            or {"status": "pending", "evidence": []}
        )
        for gate in AFFECTED_HARD_GATES
    }
    updated["verification_epoch"] = epoch
    for gate in AFFECTED_HARD_GATES:
        updated.setdefault("gate_results", {})[gate] = {
            "status": "pending",
            "epoch": epoch,
            "evidence": [],
        }
    updated["active_attempt"] = {
        "epoch": epoch,
        "gate": "visual",
        "target": target,
        "owner": owner,
        "before_report_digest": report_digest,
        "before_objective": float(objective),
        "snapshot_path": snapshot_path,
        "required_hard_gates": list(AFFECTED_HARD_GATES),
        "baseline_gate_statuses": baseline,
        "baseline_gate_results": baseline_results,
    }
    return updated


def record_gate_evidence(
    ledger: Mapping[str, Any],
    *,
    gate: str,
    passed: bool,
    evidence: list[str],
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Stamp measured gate output with the active verification epoch."""

    updated = deepcopy(dict(ledger))
    if gate not in _required_gates(updated):
        raise ValueError(f"unknown required gate: {gate}")
    active = updated.get("active_attempt")
    epoch = (
        int(active.get("epoch"))
        if isinstance(active, dict) and active.get("epoch") is not None
        else int(updated.get("verification_epoch") or 0)
    )
    result: dict[str, Any] = {
        "status": "pass" if passed else "fail",
        "epoch": epoch,
        "evidence": list(evidence or []),
    }
    if details is not None:
        result["details"] = deepcopy(dict(details))
    updated.setdefault("gate_results", {})[gate] = result
    return updated


def stale_attempt_gates(ledger: Mapping[str, Any]) -> list[str]:
    """Return hard gates without measured evidence from the active epoch."""

    active = ledger.get("active_attempt")
    if not isinstance(active, dict):
        return []
    epoch = int(active.get("epoch") or -1)
    stale: list[str] = []
    for gate in active.get("required_hard_gates") or AFFECTED_HARD_GATES:
        result = (ledger.get("gate_results") or {}).get(gate) or {}
        if (
            result.get("status") not in {"pass", "fail"}
            or int(result.get("epoch") or -1) != epoch
            or not result.get("evidence")
        ):
            stale.append(str(gate))
    return stale


def authorize_stop(
    ledger: Mapping[str, Any],
    *,
    reason: str,
    gate: str,
    target: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    """Record an exact, auditable reason why a red repair may stop."""

    if reason not in AUTHORIZED_STOP_REASONS:
        raise ValueError(f"unauthorized stop reason: {reason}")
    if reason == "proven_technical_ceiling" and not evidence:
        raise ValueError("proven_technical_ceiling requires explicit evidence")
    updated = deepcopy(dict(ledger))
    pending = updated.get("pending_repair") or {}
    if pending.get("gate") != gate or pending.get("target") != target:
        raise ValueError("authorized stop does not match pending repair")
    stop = {
        "reason": reason,
        "gate": gate,
        "target": target,
        "report_digest": pending.get("report_digest"),
        "epoch": int(pending.get("epoch") or 0),
    }
    updated["authorized_stop"] = stop
    residual = {
        "gate": gate,
        "target": target,
        "expected": 1.0,
        "measured": pending.get("objective"),
        "attempts": sum(
            1
            for attempt in (updated.get("attempts") or [])
            if attempt.get("target") == target
        ),
        "evidence": list(evidence or []),
        "reason": reason.replace("_", " "),
        "stop_reason": reason,
    }
    residuals = updated.setdefault("residuals", [])
    residuals[:] = [
        item
        for item in residuals
        if not (
            isinstance(item, dict)
            and item.get("gate") == gate
            and item.get("target") == target
        )
    ]
    residuals.append(residual)
    return updated


def synchronize_stop_conditions(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Apply external hard-stop evidence (currently the Token budget)."""

    updated = deepcopy(dict(ledger))
    pending = updated.get("pending_repair")
    if not isinstance(pending, dict):
        return updated
    budget = (updated.get("token_usage") or {}).get("budget_status") or {}
    if (
        budget.get("status") == "hard_stop"
        or budget.get("can_start_repair") is False
    ):
        return authorize_stop(
            updated,
            reason="hard_token_stop",
            gate=str(pending.get("gate")),
            target=str(pending.get("target")),
            evidence=[".pwc/run.json#token_usage.budget_status"],
        )
    return updated


def finalize_run_state(
    ledger: Mapping[str, Any],
    requested_status: str,
) -> dict[str, Any]:
    """Validate and apply a terminal transition without mutating the input."""

    if requested_status not in TERMINAL_STATUSES:
        raise ValueError(f"invalid terminal status: {requested_status!r}")
    current = str(ledger.get("status") or "running")
    if current in TERMINAL_STATUSES and current != requested_status:
        raise ValueError(f"run is already terminal as {current}")
    updated = synchronize_stop_conditions(ledger)
    if requested_status == "ready_for_user_review":
        raw_visual = (updated.get("gate_results") or {}).get("visual") or {}
        if raw_visual.get("status") == "pass" and not visual_state_evidence_complete(updated):
            raise ValueError(
                "visual state evidence is incomplete, stale, or missing required views"
            )
        incomplete = [
            gate
            for gate in _required_gates(updated)
            if _gate_status(updated, gate) != "pass"
        ]
        if incomplete:
            raise ValueError(
                "not all required gates pass: " + ", ".join(incomplete)
            )
        if updated.get("residuals"):
            raise ValueError("unresolved residuals block ready_for_user_review")
    else:
        decision = harness_decision(updated)
        if "failed_with_residuals" not in decision["terminal_allowed"]:
            raise ValueError(
                "repair remains actionable; failed_with_residuals requires "
                "an exact authorized stop"
            )
    updated["status"] = requested_status
    updated["phase"] = "handoff"
    return updated


__all__ = [
    "AUTHORIZED_STOP_REASONS",
    "AFFECTED_HARD_GATES",
    "REQUIRED_GATES",
    "apply_semantic_report",
    "authorize_stop",
    "finalize_run_state",
    "harness_decision",
    "record_gate_evidence",
    "semantic_objective",
    "semantic_report_digest",
    "semantic_report_payload",
    "stale_attempt_gates",
    "start_repair_epoch",
    "synchronize_stop_conditions",
    "visual_state_evidence_complete",
]
