import json

import pytest

from core.usage_collectors import (
    CodexSessionCollector,
    explicit_snapshot,
    estimate_observable_tokens,
)


def _token_event(
    input_tokens,
    cached_input_tokens,
    output_tokens,
    *,
    reasoning_output_tokens=0,
):
    return {
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "total_token_usage": {
                    "input_tokens": input_tokens,
                    "cached_input_tokens": cached_input_tokens,
                    "output_tokens": output_tokens,
                    "reasoning_output_tokens": reasoning_output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                }
            },
        },
    }


def test_codex_collector_reads_only_latest_token_count(tmp_path):
    session = tmp_path / "rollout-thread.jsonl"
    session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": ["secret text must not be returned"],
                        },
                    }
                ),
                json.dumps(_token_event(100, 60, 10)),
                "{malformed",
                json.dumps(
                    _token_event(
                        180,
                        120,
                        25,
                        reasoning_output_tokens=4,
                    )
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot = CodexSessionCollector(
        thread_id="thread",
        roots=[tmp_path],
        model="gpt-test",
    ).snapshot()

    assert snapshot.input_tokens == 180
    assert snapshot.cached_input_tokens == 120
    assert snapshot.output_tokens == 25
    assert snapshot.reasoning_output_tokens == 4
    assert snapshot.session_id == "thread"
    assert snapshot.model == "gpt-test"
    assert "secret" not in json.dumps(snapshot.to_dict())


def test_codex_collector_ignores_other_thread_files(tmp_path):
    (tmp_path / "rollout-other.jsonl").write_text(
        json.dumps(_token_event(999, 0, 100)) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "rollout-thread.jsonl").write_text(
        json.dumps(_token_event(10, 5, 2)) + "\n",
        encoding="utf-8",
    )

    snapshot = CodexSessionCollector(
        thread_id="thread",
        roots=[tmp_path],
    ).snapshot()

    assert snapshot.input_tokens == 10
    assert snapshot.output_tokens == 2


def test_unavailable_codex_session_returns_none(tmp_path):
    assert (
        CodexSessionCollector(
            thread_id="missing",
            roots=[tmp_path],
        ).snapshot()
        is None
    )


def test_explicit_usage_is_validated():
    snapshot = explicit_snapshot(
        "claude",
        {
            "model": "sonnet",
            "session_id": "run",
            "input_tokens": 20,
            "cached_input_tokens": 5,
            "cache_write_input_tokens": 2,
            "output_tokens": 4,
            "reasoning_output_tokens": 1,
        },
    )

    assert snapshot.provider == "claude"
    assert snapshot.input_tokens == 20
    assert snapshot.cached_input_tokens == 5
    assert snapshot.output_tokens == 4

    with pytest.raises(ValueError, match="cached input"):
        explicit_snapshot(
            "claude",
            {"input_tokens": 2, "cached_input_tokens": 3},
        )


def test_bytes_use_ceiling_estimate():
    assert estimate_observable_tokens(0) == 0
    assert estimate_observable_tokens(16_061) == 4_016
    with pytest.raises(ValueError, match="non-negative"):
        estimate_observable_tokens(-1)
