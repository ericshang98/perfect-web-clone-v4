import asyncio
import json

from core.token_accounting import UsageSnapshot
from mcp_server.tools import token_accounting as token_tools


class _FakeSandbox:
    def __init__(self, files=None):
        self.files = dict(files or {})

    async def read_file(self, path):
        return self.files.get(path)

    async def write_file(self, path, content):
        self.files[path] = content
        return True


def _ledger(source_id="source-a"):
    return {
        "schema": 2,
        "run_id": "run-a",
        "source_id": source_id,
        "status": "running",
        "token_usage": {
            "measurement_status": "estimated",
            "accounting_complete": False,
            "budget": {
                "soft_tokens": 250_000,
                "hard_tokens": 500_000,
                "basis": "non_cached_input_plus_output",
            },
        },
    }


def _sandbox(source_id="source-a"):
    return _FakeSandbox(
        {
            ".pwc/source-id": source_id,
            ".pwc/run.json": json.dumps(_ledger(source_id)),
        }
    )


def _snapshot(
    input_tokens,
    cached_input_tokens,
    output_tokens,
    *,
    session_id="thread",
):
    return UsageSnapshot(
        provider="codex",
        model="gpt-test",
        session_id=session_id,
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens,
    )


def test_begin_checkpoint_report_and_finalize_are_run_scoped(monkeypatch):
    sandbox = _sandbox()
    snapshots = iter(
        [
            _snapshot(100, 60, 10),
            _snapshot(160, 90, 25),
            _snapshot(180, 100, 30),
        ]
    )
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: next(snapshots),
    )

    begin = asyncio.run(token_tools.begin_token_accounting("source-a"))
    checkpoint = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "repair",
            "repair:hero:1",
            context={
                "text_bytes": 16_061,
                "artifact_paths": ["hero-diff.png"],
            },
            quality={
                "target": "hero",
                "before": 0.90,
                "after": 0.95,
                "accepted": True,
                "hard_gate_regressions": [],
            },
        )
    )
    report = asyncio.run(token_tools.get_token_report("source-a"))
    final = asyncio.run(token_tools.finalize_token_accounting("source-a"))

    assert begin["ok"] is True
    assert checkpoint["ok"] is True
    assert checkpoint["usage"]["non_cached_input_tokens"] == 30
    assert report["report"]["actual"]["total_tokens"] == 75
    assert report["report"]["estimated"]["observable_tokens"] == 4_016
    assert final["finalized"] is True
    assert final["report"]["accounting_complete"] is True
    assert final["report"]["actual"]["total_tokens"] == 100
    assert final["report"]["budget_status"]["status"] == "ok"
    run = json.loads(sandbox.files[".pwc/run.json"])
    assert run["token_usage"]["actual"]["total_tokens"] == 100
    assert run["token_usage"]["accounting_complete"] is True
    assert "secret" not in sandbox.files[".pwc/token-usage.jsonl"]


def test_duplicate_operation_is_idempotent(monkeypatch):
    sandbox = _sandbox()
    snapshots = iter([_snapshot(100, 60, 10), _snapshot(120, 70, 12)])
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: next(snapshots),
    )

    asyncio.run(token_tools.begin_token_accounting("source-a"))
    first = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a", "verify", "visual:desktop"
        )
    )
    duplicate = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a", "verify", "visual:desktop"
        )
    )
    report = asyncio.run(token_tools.get_token_report("source-a"))

    assert first["duplicate"] is False
    assert duplicate["duplicate"] is True
    assert report["report"]["actual"]["total_tokens"] == 22
    assert len(sandbox.files[".pwc/token-usage.jsonl"].splitlines()) == 1


def test_unavailable_provider_uses_labeled_estimate(monkeypatch):
    sandbox = _sandbox()
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: None,
    )

    begin = asyncio.run(token_tools.begin_token_accounting("source-a"))
    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "understand",
            "comparison-evidence",
            context={"text_bytes": 1_000},
        )
    )

    assert begin["measurement"] == "estimated"
    assert result["measurement"] == "estimated"
    assert result["context"]["estimated_tokens"] == 250
    assert result["report"]["measurement_status"] == "estimated"
    assert result["report"]["accounting_complete"] is False


def test_source_mismatch_fails_without_writing(monkeypatch):
    sandbox = _sandbox("source-a")
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)

    result = asyncio.run(token_tools.begin_token_accounting("source-b"))

    assert result["ok"] is False
    assert "active sandbox belongs to" in result["error"]
    assert ".pwc/token-usage.jsonl" not in sandbox.files


def test_context_is_compacted_to_metrics_digest_and_paths(monkeypatch):
    sandbox = _sandbox()
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: None,
    )
    asyncio.run(token_tools.begin_token_accounting("source-a"))

    payload = "sensitive-content-" * 1_000
    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "debug",
            "large-tool-output",
            context={
                "text_bytes": len(payload.encode("utf-8")),
                "artifact_paths": ["debug/full-output.txt"],
                "payload": payload,
            },
        )
    )

    persisted = sandbox.files[".pwc/token-usage.jsonl"]
    assert payload not in persisted
    assert result["context"]["content_digest"].startswith("sha256:")
    assert result["context"]["artifact_paths"] == ["debug/full-output.txt"]


def test_hard_budget_prevents_starting_another_repair(monkeypatch):
    sandbox = _sandbox()
    snapshots = iter(
        [
            _snapshot(0, 0, 0),
            _snapshot(500_000, 0, 1),
        ]
    )
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: next(snapshots),
    )
    asyncio.run(token_tools.begin_token_accounting("source-a"))

    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "repair",
            "repair:footer:1",
        )
    )

    assert result["report"]["budget_status"]["status"] == "hard_stop"
    assert result["report"]["budget_status"]["can_start_repair"] is False


def test_estimated_usage_also_enforces_the_hard_budget(monkeypatch):
    sandbox = _sandbox()
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: None,
    )
    asyncio.run(token_tools.begin_token_accounting("source-a"))

    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "repair",
            "repair:hero:estimated",
            context={"text_bytes": 2_000_000},
        )
    )

    budget = result["report"]["budget_status"]
    assert budget["measurement"] == "estimated"
    assert budget["used_tokens"] == 500_000
    assert budget["status"] == "hard_stop"
    assert budget["can_start_repair"] is False


def test_counter_reset_is_reported_as_an_incomplete_segment(monkeypatch):
    sandbox = _sandbox()
    snapshots = iter(
        [
            _snapshot(100, 60, 10, session_id="old"),
            _snapshot(12, 8, 3, session_id="new"),
        ]
    )
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: next(snapshots),
    )
    asyncio.run(token_tools.begin_token_accounting("source-a"))

    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "verify",
            "visual:desktop",
        )
    )

    assert result["usage"]["segment_reset"] is True
    assert result["report"]["accounting_complete"] is False
    assert any(
        "counter reset" in marker
        for marker in result["report"]["missing_segments"]
    )


def test_expected_child_agent_missing_is_visible_in_report(monkeypatch):
    sandbox = _sandbox()
    ledger = json.loads(sandbox.files[".pwc/run.json"])
    ledger["token_usage"]["expected_agents"] = ["owner", "reviewer"]
    sandbox.files[".pwc/run.json"] = json.dumps(ledger)
    snapshots = iter(
        [
            _snapshot(100, 60, 10),
            _snapshot(120, 70, 12),
        ]
    )
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        token_tools,
        "_collect_snapshot",
        lambda *_args, **_kwargs: next(snapshots),
    )
    asyncio.run(token_tools.begin_token_accounting("source-a"))

    result = asyncio.run(
        token_tools.checkpoint_token_accounting(
            "source-a",
            "verify",
            "visual:desktop",
            agent_id="owner",
        )
    )

    assert "agent:reviewer usage missing" in result["report"]["missing_segments"]


def test_tools_are_registered():
    from mcp_server.server import REGISTERED_TOOLS

    for name in (
        "begin_token_accounting",
        "checkpoint_token_accounting",
        "get_token_report",
        "finalize_token_accounting",
    ):
        assert name in REGISTERED_TOOLS
