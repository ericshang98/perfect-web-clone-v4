"""MCP terminalization must obey the durable Harness run state."""
from __future__ import annotations

import asyncio
import json

from mcp_server.tools import verify


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


class FakeSandbox:
    def __init__(self, ledger: dict):
        self.files = {
            ".pwc/source-id": "source-1",
            ".pwc/run.json": json.dumps(ledger),
        }

    async def read_file(self, path):
        return self.files.get(path)

    async def write_file(self, path, content):
        self.files[path] = content
        return True


def _ledger(*, visual="pending"):
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
            "budget_status": {"status": "ok", "can_start_repair": True}
        },
    }


def test_finalize_run_rejects_ready_with_pending_gate(monkeypatch):
    sandbox = FakeSandbox(_ledger())
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)

    result = asyncio.run(
        verify.finalize_run("source-1", "ready_for_user_review")
    )

    assert result["ok"] is False
    assert "not all required gates pass" in result["error"]
    persisted = json.loads(sandbox.files[".pwc/run.json"])
    assert persisted["status"] == "running"


def test_finalize_run_allows_ready_only_after_every_gate_passes(monkeypatch):
    sandbox = FakeSandbox(_ledger(visual="pass"))
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)

    result = asyncio.run(
        verify.finalize_run("source-1", "ready_for_user_review")
    )

    assert result["ok"] is True
    assert result["status"] == "ready_for_user_review"
    assert result["terminal_allowed"] == ["ready_for_user_review"]
    persisted = json.loads(sandbox.files[".pwc/run.json"])
    assert persisted["phase"] == "handoff"


def test_finalize_run_rejects_residual_while_repair_is_actionable(monkeypatch):
    ledger = _ledger(visual="fail")
    ledger["phase"] = "repair"
    ledger["pending_repair"] = {
        "gate": "visual",
        "target": "hero",
        "report_digest": "sha256:test",
        "objective": 0.7,
    }
    sandbox = FakeSandbox(ledger)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)

    result = asyncio.run(
        verify.finalize_run("source-1", "failed_with_residuals")
    )

    assert result["ok"] is False
    assert "repair remains actionable" in result["error"]


def test_harness_run_state_resumes_exact_next_action(monkeypatch):
    ledger = _ledger(visual="fail")
    ledger["phase"] = "repair"
    ledger["pending_repair"] = {
        "gate": "visual",
        "target": "hero",
        "report_digest": "sha256:test",
        "objective": 0.7,
    }
    sandbox = FakeSandbox(ledger)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)

    result = asyncio.run(verify.get_harness_run_state("source-1"))

    assert result["ok"] is True
    assert result["must_continue"] is True
    assert result["next_action"] == "repair:hero"
    assert result["terminal_allowed"] == []


def test_run_controller_tools_are_registered():
    from mcp_server.server import REGISTERED_TOOLS

    assert "get_harness_run_state" in REGISTERED_TOOLS
    assert "finalize_run" in REGISTERED_TOOLS
