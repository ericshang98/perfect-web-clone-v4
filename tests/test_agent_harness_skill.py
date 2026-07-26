"""Regression contract for the agent-facing Perfect Web Clone harness."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "SKILL.md"
HARNESS_CONTRACT = ROOT / "skill" / "references" / "harness-contract.md"
OPENAI_YAML = ROOT / "skill" / "agents" / "openai.yaml"
README = ROOT / "README.md"


def _skill() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_one_natural_language_request_authorizes_the_whole_local_workflow():
    text = _skill()
    assert "single natural-language request" in text
    assert "Do not ask for routine confirmation" in text
    assert "Continue across phases without returning control" in text
    assert "full-page clone is the default" in text


def test_the_current_agent_is_the_harness_runtime_not_a_cli_or_api():
    text = _skill()
    assert "The current agent is the harness runtime" in text
    assert "Do not require a CLI, API, daemon, or separate orchestrator" in text
    assert "The `pwc4` tools are deterministic hands and eyes" in text


def test_common_interactions_are_required_behavior_not_static_appearance():
    text = _skill()
    for interaction in ("carousel", "menu", "tabs", "accordion"):
        assert interaction in text
    assert "Implement and replay every required common interaction" in text
    assert "A visually similar but inert control fails" in text
    assert "full interactive behavior" not in text


def test_red_gates_cannot_be_hidden_or_reported_as_success():
    text = _skill()
    assert "Never hide, waive silently, or average away a red gate" in text
    assert "A missing critical region cannot be offset by aggregate visual similarity" in text
    assert "failed_with_residuals" in text
    assert "ready_for_user_review" in text
    assert "Only the user can accept the result" in text


def test_agent_authors_semantic_contract_before_visual_scoring():
    text = _skill()
    assert "`get_comparison_evidence`" in text
    assert "`save_comparison_contract`" in text
    assert "`score_semantic_fidelity`" in text
    assert "Whole-page SSIM is diagnostic" in text
    assert "could this observation change" in text
    assert "replacement invariants" in text


def test_repairs_are_token_bounded_and_monotonic():
    text = _skill()
    assert "`build_semantic_repair_packet`" in text
    assert "`record_semantic_attempt`" in text
    assert "16 KiB" in text
    assert "Preserve the best measured candidate" in text
    contract = HARNESS_CONTRACT.read_text(encoding="utf-8")
    assert '"comparison_contract"' in contract
    assert '"packet_bytes"' in contract
    assert '"accepted"' in contract


def test_harness_accounts_tokens_and_never_merges_estimates_with_actuals():
    text = _skill()
    for tool in (
        "begin_token_accounting",
        "checkpoint_token_accounting",
        "get_token_report",
        "finalize_token_accounting",
    ):
        assert f"`{tool}`" in text
    assert "actual and estimated" in text
    assert "never merge" in text
    assert "non-cached input plus output" in text
    contract = HARNESS_CONTRACT.read_text(encoding="utf-8")
    assert '".pwc/token-usage.jsonl"' in contract
    assert '"measurement_status"' in contract
    assert '"accounting_complete"' in contract


def test_hard_token_budget_stops_repairs_without_waiving_failures():
    text = _skill()
    assert "250K" in text
    assert "500K" in text
    assert "hard Token budget cannot waive" in text
    assert "failed_with_residuals" in text


def test_harness_persists_progress_and_resumes_the_same_run():
    text = _skill()
    assert "`.pwc/run.json`" in text
    assert "Resume rather than restart" in text
    assert HARNESS_CONTRACT.is_file()
    contract = HARNESS_CONTRACT.read_text(encoding="utf-8")
    for field in (
        '"url"',
        '"source_id"',
        '"phase"',
        '"status"',
        '"completed_sections"',
        '"gate_results"',
        '"residuals"',
    ):
        assert field in contract


def test_skill_metadata_supports_implicit_agent_invocation():
    assert OPENAI_YAML.is_file()
    metadata = OPENAI_YAML.read_text(encoding="utf-8")
    assert 'default_prompt: "Use $perfect-web-clone-v4' in metadata
    assert "allow_implicit_invocation: true" in metadata


def test_readme_describes_an_agent_harness_not_a_user_cli_or_api():
    readme = README.read_text(encoding="utf-8")
    assert "Agent-facing Harness" in readme
    assert "one natural-language request" in readme
    assert "There is no separate user-facing CLI or cloning API" in readme
    assert "one model call" in readme


def test_agent_facing_tool_descriptions_do_not_reintroduce_subagent_or_v3_architecture():
    files = [
        ROOT / "mcp_server" / "contracts.py",
        *sorted((ROOT / "mcp_server" / "tools").glob("*.py")),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        assert "subagent" not in text, path
        assert "sub-agent" not in text, path
        assert "perfect web clone v3" not in text, path
