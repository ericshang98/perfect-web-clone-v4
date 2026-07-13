"""MCP manifest tools — generate the checklist from a captured source and
verify it against the live clone. Deterministic; no LLM.

Convention note: this codebase uses ``asyncio.run(...)`` for async tool tests
(not ``@pytest.mark.anyio``); see test_score_clone_sections.py and
test_verify_tool.py for the established pattern.

Reality adaptations (vs plan draft):
- ``sections.json`` carries ``source_url`` but NOT ``viewport`` or
  ``page_height`` — those live in ``summary.json`` (keys: ``viewport``
  dict ``{width, height}`` and ``page_height`` float).
- ``generate_manifest`` therefore reads ``summary.json`` for these fields.
- The fixture creates both ``sections.json`` + ``summary.json``.
"""
import asyncio
import json

import pytest

from core.extractor.storage import SourceStore
from mcp_server.tools import verify as verify_tools


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Minimal on-disk SourceStore with sections.json + summary.json."""
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    st = SourceStore("src_test")
    st.dir.mkdir(parents=True, exist_ok=True)
    # sections.json has source_url but no viewport/page_height
    (st.dir / "sections.json").write_text(
        json.dumps({"source_url": "https://example.com"}),
        encoding="utf-8",
    )
    # summary.json carries viewport + page_height
    (st.dir / "summary.json").write_text(
        json.dumps({"viewport": {"width": 1440, "height": 900},
                    "page_height": 4000}),
        encoding="utf-8",
    )
    return st


# --------------------------------------------------------------------------- #
# generate_manifest
# --------------------------------------------------------------------------- #
def test_generate_manifest_writes_baseline_manifest(store):
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    assert out["ok"] is True
    m = json.loads((store.dir / "manifest.json").read_text(encoding="utf-8"))
    assert m["url"] == "https://example.com"
    assert out["states"] == len(m["states"])
    assert out["states"] > 0
    assert all(s["channel"] == "baseline" for s in m["states"])


def test_generate_manifest_missing_sections_errors(tmp_path, monkeypatch):
    """No sections.json at all → friendly error."""
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    out = asyncio.run(verify_tools.generate_manifest(source_id="nope"))
    assert out["ok"] is False
    assert "nope" in out["error"]


def test_generate_manifest_missing_summary_errors(tmp_path, monkeypatch):
    """sections.json present but summary.json absent → page_height=0 error."""
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    d = tmp_path / "no_summary"
    d.mkdir()
    (d / "sections.json").write_text(
        json.dumps({"source_url": "https://example.com"}), encoding="utf-8"
    )
    out = asyncio.run(verify_tools.generate_manifest(source_id="no_summary"))
    assert out["ok"] is False
    assert "page_height" in out["error"]


def test_generate_manifest_returns_manifest_path(store):
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    assert out["ok"] is True
    assert "manifest" in out
    assert str(store.dir / "manifest.json") == out["manifest"]


# --------------------------------------------------------------------------- #
# verify_manifest
# --------------------------------------------------------------------------- #
def test_verify_manifest_requires_manifest(store):
    """verify_manifest before generate_manifest → friendly error."""
    out = asyncio.run(verify_tools.verify_manifest(source_id="src_test", url="http://x"))
    assert out["ok"] is False
    assert "generate_manifest" in out["error"]


def test_verify_manifest_missing_source_errors(tmp_path, monkeypatch):
    """No source at all → still a friendly error."""
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    out = asyncio.run(verify_tools.verify_manifest(source_id="nope", url="http://x"))
    assert out["ok"] is False
    assert "generate_manifest" in out["error"]


# --------------------------------------------------------------------------- #
# server registration
# --------------------------------------------------------------------------- #
def test_manifest_tools_are_registered_on_the_server():
    pytest.importorskip("mcp")
    from mcp_server.server import REGISTERED_TOOLS
    assert "generate_manifest" in REGISTERED_TOOLS
    assert "verify_manifest" in REGISTERED_TOOLS
