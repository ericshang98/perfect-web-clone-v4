from core.iteration_ledger import new_ledger, record_attempt


def test_improving_candidate_is_accepted():
    ledger = new_ledger()

    result = record_attempt(
        ledger,
        target="details",
        before=0.81,
        after=0.88,
        hard_gate_regressions=[],
        candidate_path="/tmp/candidate-2",
    )

    assert result["accepted"] is True
    assert result["ledger"]["best"]["details"] == 0.88
    assert result["ledger"]["best_candidates"]["details"] == "/tmp/candidate-2"


def test_regression_is_rejected_and_best_is_preserved():
    ledger = new_ledger()
    first = record_attempt(
        ledger,
        target="details",
        before=0.81,
        after=0.88,
        hard_gate_regressions=[],
        candidate_path="/tmp/best",
    )["ledger"]

    result = record_attempt(
        first,
        target="details",
        before=0.88,
        after=0.84,
        hard_gate_regressions=[],
        candidate_path="/tmp/regression",
    )

    assert result["accepted"] is False
    assert result["restore_candidate"] == "/tmp/best"
    assert result["ledger"]["best"]["details"] == 0.88


def test_hard_gate_regression_rejects_visual_improvement():
    ledger = new_ledger()

    result = record_attempt(
        ledger,
        target="hero",
        before=0.70,
        after=0.90,
        hard_gate_regressions=["interaction:carousel"],
        candidate_path="/tmp/visually-better",
    )

    assert result["accepted"] is False
    assert result["ledger"]["attempts"][0]["hard_gate_regressions"] == [
        "interaction:carousel"
    ]


def test_two_non_improving_attempts_plateau_target():
    ledger = new_ledger()
    first = record_attempt(
        ledger,
        target="details",
        before=0.88,
        after=0.87,
        hard_gate_regressions=[],
    )["ledger"]

    result = record_attempt(
        first,
        target="details",
        before=0.88,
        after=0.88,
        hard_gate_regressions=[],
    )

    assert result["plateaued"] is True
    assert result["ledger"]["non_improving"]["details"] == 2


def test_target_and_total_budgets_stop_further_repairs():
    ledger = new_ledger(max_target_attempts=2, max_total_attempts=3)
    first = record_attempt(
        ledger, "hero", 0.50, 0.60, [], "/tmp/one"
    )["ledger"]
    second = record_attempt(
        first, "hero", 0.60, 0.70, [], "/tmp/two"
    )["ledger"]

    result = record_attempt(second, "hero", 0.70, 0.80, [], "/tmp/three")

    assert result["recorded"] is False
    assert result["stop_reason"] == "target attempt budget exhausted"
