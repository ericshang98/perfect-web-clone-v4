from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILL_ROOT = ROOT / "skills" / "perfect-web-clone-v4"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_plugin_manifests_and_runtime_share_one_versioned_root():
    codex = _json(CODEX_MANIFEST)
    claude = _json(CLAUDE_MANIFEST)
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert codex["name"] == claude["name"] == project["project"]["name"]
    assert codex["version"] == claude["version"] == project["project"]["version"]
    assert codex["skills"] == "./skills/"
    assert codex["mcpServers"] == "./.mcp.json"
    assert (SKILL_ROOT / "SKILL.md").is_file()
    assert (SKILL_ROOT / "agents" / "openai.yaml").is_file()
    assert (SKILL_ROOT / "references" / "harness-contract.md").is_file()


def test_mcp_launch_is_checkout_relative_and_uses_v4_entrypoint():
    config = _json(MCP_CONFIG)
    server = config["mcpServers"]["pwc4"]
    assert server == {
        "command": "uv",
        "args": ["run", "--project", ".", "pwc4-mcp"],
        "cwd": ".",
    }
    serialized = MCP_CONFIG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "pwc3" not in serialized
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["scripts"]["pwc4-mcp"] == "mcp_server.server:main"
    assert "pwc3-mcp" not in project["project"]["scripts"]


def test_codex_plugin_contract_validator_passes():
    validator = (
        Path.home()
        / ".codex"
        / "skills"
        / ".system"
        / "plugin-creator"
        / "scripts"
        / "validate_plugin.py"
    )
    if not validator.is_file():
        pytest.skip("Codex plugin-creator validator is not installed")
    result = subprocess.run(
        [sys.executable, str(validator), str(ROOT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_canonical_skill_is_not_duplicated_in_legacy_location():
    assert not (ROOT / "skill" / "SKILL.md").exists()
