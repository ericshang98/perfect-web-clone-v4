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
- The checklist is written to ``checklist.json`` (NOT ``manifest.json`` —
  that file is extraction metadata owned by SourceStore / the extractor and
  must not be overwritten by the checklist tool).
"""
import asyncio
import json

import pytest
from PIL import Image

from core.extractor.storage import SourceStore
from mcp_server.tools import verify as verify_tools


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Minimal on-disk SourceStore with sections.json + summary.json +
    a synthetic primary_full.png so refs materialization has something to work with."""
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
    # Synthetic full-page screenshot so refs materialization succeeds
    screenshots_dir = st.dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1440, 4000), (100, 150, 200))
    img.save(screenshots_dir / "primary_full.png")
    return st


# --------------------------------------------------------------------------- #
# generate_manifest — writes checklist.json, NOT manifest.json
# --------------------------------------------------------------------------- #
def test_generate_manifest_writes_baseline_checklist(store):
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    assert out["ok"] is True
    # Must write checklist.json
    checklist_path = store.dir / "checklist.json"
    assert checklist_path.is_file(), "checklist.json not written"
    m = json.loads(checklist_path.read_text(encoding="utf-8"))
    assert m["url"] == "https://example.com"
    assert out["states"] == len(m["states"])
    assert out["states"] > 0
    assert all(s["channel"] == "baseline" for s in m["states"])


def test_generate_manifest_does_not_overwrite_extraction_manifest(store):
    """generate_manifest must NOT write to manifest.json (extraction metadata)."""
    # Write a sentinel extraction manifest to confirm it is untouched
    sentinel = {"sentinel": True, "url": "original-extraction-data"}
    (store.dir / "manifest.json").write_text(
        json.dumps(sentinel), encoding="utf-8"
    )
    asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    # manifest.json must still contain the sentinel
    content = json.loads((store.dir / "manifest.json").read_text(encoding="utf-8"))
    assert content == sentinel, "manifest.json was overwritten by generate_manifest"


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


def test_generate_manifest_returns_checklist_path(store):
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    assert out["ok"] is True
    assert "checklist" in out
    assert str(store.dir / "checklist.json") == out["checklist"]


def test_generate_manifest_refs_materialized(store):
    """generate_manifest must call materialize_refs and return refs summary
    with at least one written ref, and the ref files must exist on disk."""
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))
    assert out["ok"] is True
    assert "refs" in out, "refs summary missing from return dict"
    refs = out["refs"]
    assert len(refs["written"]) > 0, "expected at least one ref to be written"
    # Verify at least one ref file actually exists
    from core.extractor.storage import SourceStore
    st = SourceStore("src_test")
    written_paths = refs["written"]
    for relpath in written_paths[:1]:  # check at least the first
        assert (st.dir / relpath).is_file(), f"ref file missing: {relpath}"


# --------------------------------------------------------------------------- #
# verify_manifest — reads checklist.json
# --------------------------------------------------------------------------- #
def test_verify_manifest_requires_checklist(store):
    """verify_manifest before generate_manifest (no checklist.json) → friendly error."""
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
