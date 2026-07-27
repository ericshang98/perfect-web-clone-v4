"""A reusable agent harness must never leak one site's files into the next."""

import asyncio
import json

from mcp_server.tools import build_deploy


class _FakeSandbox:
    def __init__(self, files=None):
        self.files = dict(files or {})

    async def read_file(self, path):
        return self.files.get(path)

    async def write_file(self, path, content):
        self.files[path] = content
        return True


def test_same_source_reuses_the_active_sandbox(monkeypatch):
    sandbox = _FakeSandbox(
        {
            ".pwc/source-id": "source-a",
            "src/components/sections/hero/Hero.jsx": "keep me",
        }
    )
    resets = []

    monkeypatch.setattr(build_deploy, "get_sandbox", lambda: sandbox)

    async def create_sandbox(*, reset):
        resets.append(reset)
        return sandbox

    monkeypatch.setattr(build_deploy, "create_sandbox", create_sandbox)

    result = asyncio.run(build_deploy._require_sandbox("source-a"))

    assert result is sandbox
    assert resets == []
    assert sandbox.files["src/components/sections/hero/Hero.jsx"] == "keep me"


def test_different_source_resets_before_assembly(monkeypatch):
    sandbox = _FakeSandbox(
        {
            ".pwc/source-id": "source-a",
            "src/components/sections/hero/Hero.jsx": "site A",
        }
    )
    resets = []
    monkeypatch.setattr(build_deploy, "get_sandbox", lambda: sandbox)

    async def create_sandbox(*, reset):
        resets.append(reset)
        if reset:
            sandbox.files.clear()
        return sandbox

    monkeypatch.setattr(build_deploy, "create_sandbox", create_sandbox)

    result = asyncio.run(build_deploy._require_sandbox("source-b"))

    assert result is sandbox
    assert resets == [True]
    assert "src/components/sections/hero/Hero.jsx" not in sandbox.files
    assert sandbox.files[".pwc/source-id"] == "source-b"


def test_assembly_ledger_has_the_agent_harness_contract_fields():
    ledger = build_deploy._new_run_ledger(
        source_id="source-a",
        source_url="https://example.com/",
        plan={
            "sections": [
                {"namespace": "header"},
                {"namespace": "hero"},
                {"namespace": "footer"},
            ]
        },
    )

    assert json.loads(json.dumps(ledger)) == ledger
    assert ledger["schema"] == 4
    assert ledger["run_id"]
    assert ledger["source_id"] == "source-a"
    assert ledger["url"] == "https://example.com/"
    assert ledger["phase"] == "assemble"
    assert ledger["status"] == "running"
    assert ledger["planned_sections"] == ["header", "hero", "footer"]
    assert ledger["completed_sections"] == []
    assert set(ledger["gate_results"]) == {
        "capture_integrity",
        "critical_structure",
        "interactions",
        "build",
        "fingerprints",
        "weight",
        "visual",
        "runtime",
        "responsive",
    }
    assert ledger["verification_epoch"] == 0
    assert {"runtime", "responsive"} <= set(ledger["required_gates"])
    assert ledger["residuals"] == []
    usage = ledger["token_usage"]
    assert usage["measurement_status"] == "estimated"
    assert usage["accounting_complete"] is False
    assert usage["budget"] == {
        "soft_tokens": 250_000,
        "hard_tokens": 500_000,
        "basis": "non_cached_input_plus_output",
    }


def test_each_new_assembly_ledger_has_a_distinct_run_id():
    first = build_deploy._new_run_ledger(
        "source-a", "https://example.com/a", {"sections": []}
    )
    second = build_deploy._new_run_ledger(
        "source-b", "https://example.com/b", {"sections": []}
    )

    assert first["run_id"] != second["run_id"]
