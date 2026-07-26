import pytest

from core.token_accounting import (
    UsageSnapshot,
    aggregate_events,
    budget_decision,
    usage_delta,
)


def _actual_event(
    event_id="event-a",
    *,
    phase="repair",
    agent_id="owner",
    input_tokens=100,
    cached_input_tokens=60,
    output_tokens=10,
    estimated_tokens=4_000,
    quality=None,
):
    return {
        "event_id": event_id,
        "phase": phase,
        "agent_id": agent_id,
        "measurement": "actual",
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "non_cached_input_tokens": input_tokens - cached_input_tokens,
            "cache_write_input_tokens": 0,
            "output_tokens": output_tokens,
            "reasoning_output_tokens": 0,
            "total_tokens": input_tokens + output_tokens,
        },
        "context": {"estimated_tokens": estimated_tokens},
        "quality": quality or {},
    }


def test_delta_separates_cached_and_non_cached_input():
    before = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="thread",
        input_tokens=100,
        cached_input_tokens=60,
        output_tokens=10,
    )
    after = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="thread",
        input_tokens=160,
        cached_input_tokens=90,
        output_tokens=25,
    )

    delta = usage_delta(before, after)

    assert delta["input_tokens"] == 60
    assert delta["cached_input_tokens"] == 30
    assert delta["non_cached_input_tokens"] == 30
    assert delta["output_tokens"] == 15
    assert delta["total_tokens"] == 75
    assert delta["segment_reset"] is False


def test_counter_reset_starts_a_new_segment_without_negative_usage():
    before = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="old",
        input_tokens=100,
        cached_input_tokens=50,
        output_tokens=20,
    )
    after = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="new",
        input_tokens=12,
        cached_input_tokens=8,
        output_tokens=3,
    )

    delta = usage_delta(before, after)

    assert delta["segment_reset"] is True
    assert delta["input_tokens"] == 12
    assert delta["non_cached_input_tokens"] == 4
    assert delta["output_tokens"] == 3


def test_snapshot_rejects_negative_or_impossible_counters():
    with pytest.raises(ValueError, match="non-negative"):
        UsageSnapshot(provider="codex", input_tokens=-1)
    with pytest.raises(ValueError, match="cached input"):
        UsageSnapshot(
            provider="codex",
            input_tokens=3,
            cached_input_tokens=4,
        )


def test_actual_and_estimated_totals_never_merge():
    events = [
        _actual_event(
            quality={
                "target": "hero",
                "before": 0.90,
                "after": 0.95,
                "accepted": True,
            }
        ),
        {
            "event_id": "event-b",
            "phase": "understand",
            "agent_id": "owner",
            "measurement": "estimated",
            "usage": {},
            "context": {"estimated_tokens": 2_000},
            "quality": {},
        },
    ]

    report = aggregate_events(events)

    assert report["actual"]["total_tokens"] == 110
    assert report["estimated"]["observable_tokens"] == 6_000
    assert report["measurement_status"] == "mixed"
    assert report["efficiency"]["accepted_repairs"] == 1
    assert report["efficiency"]["tokens_per_accepted_repair"] == 50
    assert report["efficiency"]["tokens_per_quality_point"] == 10.0


def test_duplicate_event_ids_are_counted_once():
    event = _actual_event()
    assert aggregate_events([event, event])["actual"]["total_tokens"] == 110


def test_events_aggregate_by_phase_and_agent():
    report = aggregate_events(
        [
            _actual_event("one", phase="repair", agent_id="owner"),
            _actual_event(
                "two",
                phase="verify",
                agent_id="reviewer",
                input_tokens=30,
                cached_input_tokens=10,
                output_tokens=5,
            ),
        ]
    )

    assert report["by_phase"]["repair"]["total_tokens"] == 110
    assert report["by_phase"]["verify"]["total_tokens"] == 35
    assert report["by_agent"]["owner"]["total_tokens"] == 110
    assert report["by_agent"]["reviewer"]["total_tokens"] == 35


def test_invalid_measurement_or_phase_is_rejected():
    bad_phase = _actual_event()
    bad_phase["phase"] = "chat"
    with pytest.raises(ValueError, match="invalid phase"):
        aggregate_events([bad_phase])

    bad_measurement = _actual_event()
    bad_measurement["measurement"] = "guessed"
    with pytest.raises(ValueError, match="invalid measurement"):
        aggregate_events([bad_measurement])


def test_budget_uses_non_cached_input_plus_output():
    decision = budget_decision(
        {"non_cached_input_tokens": 240_000, "output_tokens": 20_000},
        soft_tokens=250_000,
        hard_tokens=500_000,
    )
    assert decision["status"] == "soft_warning"
    assert decision["can_start_repair"] is True
    assert decision["used_tokens"] == 260_000

    stopped = budget_decision(
        {"non_cached_input_tokens": 480_000, "output_tokens": 20_000},
        soft_tokens=250_000,
        hard_tokens=500_000,
    )
    assert stopped["status"] == "hard_stop"
    assert stopped["can_start_repair"] is False


def test_budget_configuration_must_be_ordered():
    with pytest.raises(ValueError, match="soft budget"):
        budget_decision(
            {},
            soft_tokens=500_000,
            hard_tokens=250_000,
        )
