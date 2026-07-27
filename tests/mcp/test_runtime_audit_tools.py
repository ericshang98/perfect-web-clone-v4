"""Runtime audit MCP persistence and composite candidate verification."""
from __future__ import annotations

import asyncio
import json

from mcp_server.tools import runtime_audit


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
HARD_GATES = (
    "critical_structure",
    "interactions",
    "build",
    "fingerprints",
    "weight",
    "runtime",
    "responsive",
)


class FakeSandbox:
    def __init__(self):
        ledger = {
            "schema": 3,
            "run_id": "run-epoch",
            "source_id": "source-1",
            "phase": "repair",
            "status": "running",
            "breakpoints": [1440, 390],
            "verification_epoch": 2,
            "gate_results": {
                gate: {"status": "pending", "epoch": 2, "evidence": []}
                for gate in GATES
            },
            "active_attempt": {
                "epoch": 2,
                "required_hard_gates": list(HARD_GATES),
            },
            "residuals": [],
        }
        self.files = {
            ".pwc/source-id": "source-1",
            ".pwc/run.json": json.dumps(ledger),
            ".pwc/preview.json": json.dumps(
                {"url": "http://127.0.0.1:4173/"}
            ),
        }

    async def read_file(self, path):
        return self.files.get(path)

    async def write_file(self, path, content):
        self.files[path] = content
        return True


def _clean(width):
    return {
        "breakpoint": width,
        "navigation": {"ok": True, "status": 200},
        "console": [],
        "page_errors": [],
        "request_failures": [],
        "http_errors": [],
        "resources": [],
        "fonts": [],
        "images": [],
        "media": [],
        "layout": {
            "viewport_width": width,
            "scroll_width": width,
            "reachable_scroll_x": 0,
            "offenders": [],
        },
    }


def test_runtime_audit_persists_both_gates_at_active_epoch(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(
        runtime_audit,
        "collect_runtime_observations",
        lambda _url, breakpoints, **_kwargs: [_clean(width) for width in breakpoints],
    )

    result = asyncio.run(
        runtime_audit.audit_runtime("source-1", "http://127.0.0.1:4173/")
    )

    assert result["ok"] is True
    ledger = json.loads(sandbox.files[".pwc/run.json"])
    assert ledger["gate_results"]["runtime"]["status"] == "pass"
    assert ledger["gate_results"]["runtime"]["epoch"] == 2
    assert ledger["gate_results"]["responsive"]["status"] == "pass"
    assert ledger["gate_results"]["responsive"]["epoch"] == 2


def test_runtime_audit_unions_override_with_every_ledger_breakpoint(monkeypatch):
    sandbox = FakeSandbox()
    ledger = json.loads(sandbox.files[".pwc/run.json"])
    ledger["breakpoints"] = [1440, 768, 390]
    sandbox.files[".pwc/run.json"] = json.dumps(ledger)
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)
    captured = []

    def fake_collect(_url, breakpoints, **_kwargs):
        captured.extend(breakpoints)
        return [_clean(width) for width in breakpoints]

    monkeypatch.setattr(
        runtime_audit,
        "collect_runtime_observations",
        fake_collect,
    )

    result = asyncio.run(
        runtime_audit.audit_runtime(
            "source-1",
            "http://127.0.0.1:4173/",
            breakpoints=[390],
        )
    )

    assert result["ok"] is True
    assert captured == [1440, 768, 390]


def test_runtime_audit_rejects_foreign_url_before_browser_collection(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)

    def should_not_collect(*_args, **_kwargs):
        raise AssertionError("foreign URL must not reach browser collection")

    monkeypatch.setattr(
        runtime_audit,
        "collect_runtime_observations",
        should_not_collect,
    )
    result = asyncio.run(
        runtime_audit.audit_runtime(
            "source-1",
            "https://unrelated.example/",
        )
    )

    assert result["ok"] is False
    assert "sandbox-owned preview URL" in result["error"]


def test_composite_verifier_stamps_all_post_edit_hard_gates(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)

    async def fake_build():
        return {
            "success": True,
            "exit_code": 0,
            "dist_dir": "/tmp/dist",
            "errors": [],
        }

    async def fake_manifest(_source_id, _url):
        return {
            "ok": False,
            "summary": {"ok": False, "states": 3},
            "report": "report.html",
            "interaction_states_expected": 1,
            "states": [
                {"id": "baseline", "channel": "baseline", "status": "fail"},
                {
                    "id": "carousel-next",
                    "channel": "interaction",
                    "status": "pass",
                },
            ],
        }

    async def fake_structure(_source_id, url=None):
        return {
            "ok": False,
            "url": url,
            "structure": {
                "ok": True,
                "failures": [],
                "required": 4,
            },
        }

    monkeypatch.setattr(runtime_audit.build_deploy, "build_project", fake_build)
    monkeypatch.setattr(
        runtime_audit.pipeline,
        "check_fingerprints",
        lambda _path: {"ok": True, "total": 0},
    )
    monkeypatch.setattr(
        runtime_audit.pipeline,
        "check_weight",
        lambda _path: {"ok": True, "total_kb": 12},
    )
    monkeypatch.setattr(
        runtime_audit.verify,
        "verify_manifest",
        fake_manifest,
    )
    monkeypatch.setattr(
        runtime_audit.verify,
        "score_clone_sections",
        fake_structure,
    )
    monkeypatch.setattr(
        runtime_audit,
        "collect_runtime_observations",
        lambda _url, breakpoints, **_kwargs: [_clean(width) for width in breakpoints],
    )

    result = asyncio.run(
        runtime_audit.verify_harness_candidate(
            "source-1",
            "http://127.0.0.1:4173/",
        )
    )

    assert result["ok"] is True
    ledger = json.loads(sandbox.files[".pwc/run.json"])
    for gate in HARD_GATES:
        assert ledger["gate_results"][gate]["status"] == "pass"
        assert ledger["gate_results"][gate]["epoch"] == 2
        assert ledger["gate_results"][gate]["evidence"]
    assert ledger["gate_results"]["critical_structure"]["details"]["required"] == 4
    assert ledger["gate_results"]["interactions"]["details"] == {
        "ok": True,
        "required_states": 1,
        "observed_states": 1,
        "failed_states": [],
        "missing_states": 0,
    }


def test_composite_rejects_dist_override_outside_just_built_dist(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)

    async def fake_build():
        return {
            "success": True,
            "exit_code": 0,
            "dist_dir": "/sandbox/dist",
            "errors": [],
        }

    monkeypatch.setattr(runtime_audit.build_deploy, "build_project", fake_build)
    result = asyncio.run(
        runtime_audit.verify_harness_candidate(
            "source-1",
            "http://127.0.0.1:4173/",
            dist_dir="/tmp/unrelated-clean-dist",
        )
    )

    assert result["ok"] is False
    assert "canonical just-built dist" in result["error"]


def test_composite_rejects_foreign_url_before_build(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(runtime_audit, "get_sandbox", lambda: sandbox)

    async def should_not_build():
        raise AssertionError("foreign URL must be rejected before build")

    monkeypatch.setattr(
        runtime_audit.build_deploy,
        "build_project",
        should_not_build,
    )
    result = asyncio.run(
        runtime_audit.verify_harness_candidate(
            "source-1",
            "https://unrelated.example/",
        )
    )

    assert result["ok"] is False
    assert "sandbox-owned preview URL" in result["error"]


def test_runtime_audit_tools_are_registered():
    from mcp_server.server import REGISTERED_TOOLS

    assert "audit_runtime" in REGISTERED_TOOLS
    assert "verify_harness_candidate" in REGISTERED_TOOLS


def test_interaction_gate_fails_closed_without_manifest_execution_evidence():
    execution_error = runtime_audit._interaction_gate_result(
        {"ok": False, "error": "checklist missing"}
    )
    missing_row = runtime_audit._interaction_gate_result(
        {
            "ok": False,
            "interaction_states_expected": 2,
            "states": [
                {
                    "id": "next",
                    "channel": "interaction",
                    "status": "pass",
                }
            ],
        }
    )
    baseline_only_failure = runtime_audit._interaction_gate_result(
        {
            "ok": False,
            "interaction_states_expected": 0,
            "states": [
                {"id": "baseline", "channel": "baseline", "status": "fail"}
            ],
        }
    )

    assert execution_error["ok"] is False
    assert execution_error["reason"] == "manifest execution produced no state evidence"
    assert missing_row["ok"] is False
    assert missing_row["missing_states"] == 1
    assert baseline_only_failure == {
        "ok": True,
        "required_states": 0,
        "observed_states": 0,
        "failed_states": [],
        "missing_states": 0,
    }
