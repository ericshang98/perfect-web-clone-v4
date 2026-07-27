"""Pure run-state enforcement for comparison-driven repair."""
from __future__ import annotations

from copy import deepcopy

import pytest

from core.run_controller import (
    apply_semantic_report,
    authorize_stop,
    finalize_run_state,
    harness_decision,
    record_gate_evidence,
    semantic_objective,
    semantic_report_digest,
    start_repair_epoch,
)


GATES = (
    "capture_integrity",
    "critical_structure",
    "interactions",
    "build",
    "fingerprints",
    "weight",
    "visual",
    "runtime",
    "responsive",
)


def _ledger(*, visual: str = "pending") -> dict:
    return {
        "schema": 2,
        "run_id": "run-1",
        "source_id": "source-1",
        "phase": "verify",
        "status": "running",
        "gate_results": {
            gate: {
                "status": visual if gate == "visual" else "pass",
                "evidence": [],
            }
            for gate in GATES
        },
        "attempts": [],
        "residuals": [],
        "token_usage": {
            "budget_status": {
                "status": "ok",
                "can_start_repair": True,
            }
        },
    }


def _contract() -> dict:
    return {
        "schema": 1,
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "mode": "layout_behavior",
                "compare": ["bounds", "controls"],
            }
        ],
    }


def _report(*, passed: bool = False) -> dict:
    return {
        "ok": passed,
        "source_id": "source-1",
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "status": "pass" if passed else "fail",
                "score": None,
                "failed_invariants": [] if passed else ["bounds"],
            }
        ],
    }


def test_first_actionable_red_creates_durable_repair_obligation():
    ledger = _ledger()
    report = _report()
    digest = semantic_report_digest(report)

    updated, decision = apply_semantic_report(
        ledger,
        report,
        digest=digest,
        objective=semantic_objective(report, _contract()),
        report_path=".pwc/semantic-report.json",
    )

    assert updated["phase"] == "repair"
    assert updated["status"] == "running"
    assert updated["gate_results"]["visual"]["status"] == "fail"
    assert updated["pending_repair"] == {
        "gate": "visual",
        "target": "player",
        "owner": "player",
        "report_digest": digest,
        "objective": 0.5,
        "evidence": [f".pwc/semantic-report.json#{digest}"],
        "attempts_remaining": 5,
        "epoch": 0,
    }
    assert decision == {
        "execution_ok": True,
        "gate_status": "fail",
        "must_continue": True,
        "next_action": "repair:player",
        "terminal_allowed": [],
    }


def test_earlier_runtime_pending_blocks_visual_repair_packet_action():
    ledger = _ledger()
    ledger["gate_results"]["runtime"]["status"] = "pending"
    report = _report()

    updated, decision = apply_semantic_report(
        ledger,
        report,
        digest=semantic_report_digest(report),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )

    assert updated["gate_results"]["visual"]["status"] == "fail"
    assert decision["next_action"] == "run_gate:runtime"
    assert decision["gate_status"] == "pending"


def test_invariant_only_report_has_deterministic_numeric_objective():
    assert semantic_objective(_report(), _contract()) == 0.5
    assert semantic_objective(_report(passed=True), _contract()) == 1.0


def test_pending_target_uses_same_worst_score_order_as_repair_packet():
    report = {
        "ok": False,
        "source_id": "source-1",
        "regions": [
            {
                "id": "first",
                "owner": "first-owner",
                "status": "fail",
                "score": 0.9,
                "failed_invariants": ["pixels"],
            },
            {
                "id": "worst",
                "owner": "worst-owner",
                "status": "fail",
                "score": 0.2,
                "failed_invariants": ["pixels"],
            },
        ],
    }
    contract = {
        "regions": [
            {"id": "first", "compare": ["pixels"]},
            {"id": "worst", "compare": ["pixels"]},
        ]
    }

    updated, decision = apply_semantic_report(
        _ledger(),
        report,
        digest=semantic_report_digest(report),
        objective=semantic_objective(report, contract),
        report_path=".pwc/semantic-report.json",
    )

    assert updated["pending_repair"]["target"] == "worst"
    assert updated["pending_repair"]["owner"] == "worst-owner"
    assert decision["next_action"] == "repair:worst"


def test_fresh_pass_clears_repair_and_allows_ready_terminal():
    failed, _ = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )
    failed["residuals"] = [
        {
            "gate": "visual",
            "target": "player",
            "stop_reason": "plateau",
        }
    ]
    failed["authorized_stop"] = {
        "gate": "visual",
        "target": "player",
        "reason": "plateau",
    }
    passed_report = _report(passed=True)

    updated, decision = apply_semantic_report(
        failed,
        passed_report,
        digest=semantic_report_digest(passed_report),
        objective=1.0,
        report_path=".pwc/semantic-report.json",
    )

    assert "pending_repair" not in updated
    assert "authorized_stop" not in updated
    assert updated["residuals"] == []
    # The prior report migrated this legacy ledger to schema 4; a fresh pass
    # still needs exact view/state evidence before terminalization.
    assert updated["gate_results"]["visual"]["status"] == "pending"
    assert decision["must_continue"] is True
    assert decision["next_action"] == "run_gate:visual"
    assert decision["terminal_allowed"] == []


def test_resume_recomputes_same_pending_repair_action():
    failed, original = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )

    assert harness_decision(deepcopy(failed)) == original


def test_recorded_repair_obligation_can_require_fresh_reverification():
    failed, _ = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )
    failed["pending_repair"]["reverify_required"] = True

    decision = harness_decision(failed)

    assert decision["must_continue"] is True
    assert decision["next_action"] == "reverify:visual"
    assert decision["terminal_allowed"] == []


def test_repair_epoch_invalidates_every_affected_hard_gate():
    ledger = _ledger()
    updated = start_repair_epoch(
        ledger,
        target="player",
        owner="player",
        report_digest="sha256:before",
        objective=0.5,
        snapshot_path=".pwc/snapshot.json",
    )

    assert updated["verification_epoch"] == 1
    active = updated["active_attempt"]
    assert active["epoch"] == 1
    assert active["required_hard_gates"] == [
        "critical_structure",
        "interactions",
        "build",
        "fingerprints",
        "weight",
        "runtime",
        "responsive",
    ]
    for gate in active["required_hard_gates"]:
        assert updated["gate_results"][gate]["status"] == "pending"
        assert updated["gate_results"][gate]["epoch"] == 1
    with pytest.raises(ValueError, match="not all required gates pass"):
        finalize_run_state(updated, "ready_for_user_review")


def test_gate_evidence_is_stamped_with_active_epoch():
    ledger = start_repair_epoch(
        _ledger(),
        target="player",
        owner="player",
        report_digest="sha256:before",
        objective=0.5,
        snapshot_path=".pwc/snapshot.json",
    )

    updated = record_gate_evidence(
        ledger,
        gate="build",
        passed=True,
        evidence=["dist/index.html"],
        details={"exit_code": 0},
    )

    assert updated["gate_results"]["build"] == {
        "status": "pass",
        "epoch": 1,
        "evidence": ["dist/index.html"],
        "details": {"exit_code": 0},
    }


@pytest.mark.parametrize(
    "reason",
    [
        "plateau",
        "target_attempt_budget_exhausted",
        "total_attempt_budget_exhausted",
        "hard_token_stop",
    ],
)
def test_only_explicit_authorized_stop_can_end_actionable_repair(reason):
    failed, _ = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )

    stopped = authorize_stop(
        failed,
        reason=reason,
        gate="visual",
        target="player",
    )
    decision = harness_decision(stopped)

    assert decision["must_continue"] is False
    assert decision["next_action"] == "finalize:failed_with_residuals"
    assert decision["terminal_allowed"] == ["failed_with_residuals"]
    assert stopped["residuals"][-1]["stop_reason"] == reason


def test_unknown_stop_reason_is_rejected():
    with pytest.raises(ValueError, match="unauthorized stop reason"):
        authorize_stop(
            _ledger(visual="fail"),
            reason="agent_decided_it_was_close_enough",
            gate="visual",
            target="player",
        )


def test_proven_technical_ceiling_requires_explicit_evidence():
    failed, _ = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )
    with pytest.raises(ValueError, match="requires explicit evidence"):
        authorize_stop(
            failed,
            reason="proven_technical_ceiling",
            gate="visual",
            target="player",
        )

    stopped = authorize_stop(
        failed,
        reason="proven_technical_ceiling",
        gate="visual",
        target="player",
        evidence=["evidence/canvas-capture-limit.json"],
    )
    assert harness_decision(stopped)["terminal_allowed"] == [
        "failed_with_residuals"
    ]


def test_fresh_same_target_red_invalidates_old_authorized_stop_and_residual():
    report = _report()
    failed, _ = apply_semantic_report(
        _ledger(),
        report,
        digest=semantic_report_digest(report),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )
    stopped = authorize_stop(
        failed,
        reason="plateau",
        gate="visual",
        target="player",
    )
    fresh_report = _report()
    fresh_report["regions"][0]["failed_invariants"] = ["controls"]
    fresh_digest = semantic_report_digest(fresh_report)

    updated, decision = apply_semantic_report(
        stopped,
        fresh_report,
        digest=fresh_digest,
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )

    assert "authorized_stop" not in updated
    assert updated["residuals"] == []
    assert updated["pending_repair"]["report_digest"] == fresh_digest
    assert decision["terminal_allowed"] == []
    assert decision["must_continue"] is True


def test_declared_future_runtime_gate_blocks_ready_until_passed():
    ledger = _ledger(visual="pass")
    ledger["required_gates"] = [*GATES, "runtime", "responsive"]
    ledger["gate_results"]["runtime"] = {"status": "fail", "evidence": []}
    ledger["gate_results"]["responsive"] = {"status": "pending", "evidence": []}

    with pytest.raises(ValueError, match="runtime, responsive"):
        finalize_run_state(ledger, "ready_for_user_review")


def test_required_gate_extensions_cannot_drop_baseline_gates():
    ledger = _ledger(visual="pass")
    ledger["required_gates"] = []
    ledger["gate_results"]["build"]["status"] = "pending"
    with pytest.raises(ValueError, match="build"):
        finalize_run_state(ledger, "ready_for_user_review")

    ledger["required_gates"] = ["runtime"]
    ledger["gate_results"]["build"]["status"] = "pass"
    ledger["gate_results"]["runtime"] = {"status": "pass", "evidence": []}
    assert (
        finalize_run_state(ledger, "ready_for_user_review")["status"]
        == "ready_for_user_review"
    )


def test_ready_rejects_unresolved_residual_even_when_gates_pass():
    ledger = _ledger(visual="pass")
    ledger["residuals"] = [
        {
            "gate": "visual",
            "target": "hero",
            "stop_reason": "plateau",
        }
    ]

    with pytest.raises(ValueError, match="unresolved residuals"):
        finalize_run_state(ledger, "ready_for_user_review")


def test_new_harness_visual_pass_requires_exact_measured_view_coverage():
    ledger = _ledger(visual="pass")
    ledger["schema"] = 4
    ledger["comparison_contract"] = {"digest": "sha256:contract"}

    with pytest.raises(ValueError, match="visual state evidence"):
        finalize_run_state(ledger, "ready_for_user_review")

    ledger["gate_results"]["visual"]["details"] = {
        "policy_version": "visual-state-v1",
        "contract_digest": "sha256:contract",
        "required_view_ids": ["b1440:s-top", "b390:s-top"],
        "measured_view_ids": ["b1440:s-top", "b390:s-top"],
        "failures_by_view": {},
    }

    assert finalize_run_state(ledger, "ready_for_user_review")["status"] == "ready_for_user_review"


def test_legacy_run_upgrades_and_cannot_carry_generic_visual_green_forward():
    report = _report(passed=True)
    updated, decision = apply_semantic_report(
        _ledger(visual="pass"),
        report,
        digest=semantic_report_digest(report),
        objective=1.0,
        report_path=".pwc/semantic-report.json",
    )

    assert updated["schema"] == 4
    assert updated["gate_results"]["visual"]["status"] == "pending"
    assert decision["next_action"] == "run_gate:visual"


def test_ready_terminal_rejects_any_red_or_pending_gate():
    with pytest.raises(ValueError, match="not all required gates pass"):
        finalize_run_state(_ledger(visual="pending"), "ready_for_user_review")
    with pytest.raises(ValueError, match="not all required gates pass"):
        finalize_run_state(_ledger(visual="fail"), "ready_for_user_review")


def test_residual_terminal_rejects_actionable_repair_and_accepts_exact_stop():
    failed, _ = apply_semantic_report(
        _ledger(),
        _report(),
        digest=semantic_report_digest(_report()),
        objective=0.5,
        report_path=".pwc/semantic-report.json",
    )
    with pytest.raises(ValueError, match="repair remains actionable"):
        finalize_run_state(failed, "failed_with_residuals")

    stopped = authorize_stop(
        failed,
        reason="plateau",
        gate="visual",
        target="player",
    )
    terminal = finalize_run_state(stopped, "failed_with_residuals")
    assert terminal["status"] == "failed_with_residuals"
    assert terminal["phase"] == "handoff"
