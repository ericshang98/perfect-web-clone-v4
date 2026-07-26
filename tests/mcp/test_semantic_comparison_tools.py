"""Agent-facing semantic comparison tools.

These tests keep the reasoning/tool boundary explicit: the Agent classifies
regions, while deterministic MCP tools persist, measure, localize, and record.
"""
from __future__ import annotations

import asyncio
import json

from PIL import Image

from mcp_server.tools import verify


def _bounds(x=0, y=0, width=800, height=400):
    return {"x": x, "y": y, "width": width, "height": height}


def _source(tmp_path, monkeypatch, sid="semantic-source"):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    root = tmp_path / sid
    (root / "screenshots").mkdir(parents=True)
    (root / "evidence").mkdir()
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "success": True,
                "capture_integrity": {"ok": True, "status": "passed"},
            }
        ),
        encoding="utf-8",
    )
    (root / "summary.json").write_text(
        json.dumps(
            {
                "page_width": 800,
                "page_height": 600,
                "viewport": {"width": 800, "height": 600},
            }
        ),
        encoding="utf-8",
    )
    (root / "sections_full.json").write_text(
        json.dumps(
            {
                "sections": [
                    {
                        "name": "player",
                        "component_path": "src/components/sections/player/Player.jsx",
                        "bounds": _bounds(height=400),
                    },
                    {
                        "name": "details",
                        "component_path": "src/components/sections/details/Details.jsx",
                        "bounds": _bounds(y=400, height=200),
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (root / "sections.json").write_text(
        json.dumps({"source_url": "https://held-out.example/page"}),
        encoding="utf-8",
    )
    (root / "evidence" / "raw_structure.json").write_text(
        json.dumps(
            {
                "page": {"width": 800, "height": 600},
                "regions": [
                    {
                        "fingerprint": "player",
                        "kind": "video",
                        "critical": True,
                        "rect": _bounds(height=400),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "evidence" / "volatility_summary.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "sample_count": 3,
                "candidates": [
                    {
                        "id": "player",
                        "tag": "video",
                        "bounds": _bounds(height=400),
                        "hint": "runtime_media",
                        "suggested_mode": "layout_behavior",
                        "requires_agent_decision": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "interactions.json").write_text(
        json.dumps(
            {
                "interactions": [
                    {
                        "id": "player-toggle",
                        "kind": "button",
                        "owner": "player",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    Image.new("RGB", (800, 600), "white").save(
        root / "screenshots" / "primary_full.png"
    )
    return sid, root


def _contract():
    return {
        "schema": 1,
        "ref_page_size": [800, 600],
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "importance": "critical",
                "mode": "layout_behavior",
                "bounds": _bounds(height=400),
                "compare": ["bounds", "aspect_ratio", "controls", "interaction"],
                "ignore_observations": ["media_frame_pixels"],
                "reason": "decoded media frames change independently of page CSS",
                "reference_facts": {
                    "bounds": _bounds(height=400),
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
            },
            {
                "id": "details",
                "owner": "details",
                "importance": "important",
                "mode": "static_pixels",
                "bounds": _bounds(y=400, height=200),
                "compare": ["pixels"],
            },
        ],
    }


def test_get_comparison_evidence_is_bounded_and_keeps_agent_decision_explicit(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)

    result = asyncio.run(verify.get_comparison_evidence(sid))

    assert result["ok"] is True
    assert result["capture_integrity"]["status"] == "passed"
    assert result["volatility"]["candidates"][0]["requires_agent_decision"] is True
    assert result["critical_regions"][0]["id"] == "player"
    assert result["text_bytes"] <= 32_768
    assert "raw_html" not in result and "css" not in result


def test_save_contract_validates_and_persists_to_source_and_sandbox(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)

    class FakeSandbox:
        def __init__(self):
            self.writes = {}

        async def write_file(self, path, content):
            self.writes[path] = content
            return True

    sandbox = FakeSandbox()
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)

    result = asyncio.run(verify.save_comparison_contract(sid, _contract()))

    assert result["ok"] is True
    assert (root / "comparison-contract.json").is_file()
    assert ".pwc/comparison-contract.json" in sandbox.writes


def test_save_contract_fails_closed_on_unjustified_dynamic_region(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    contract = _contract()
    contract["regions"][0].pop("reason")

    result = asyncio.run(verify.save_comparison_contract(sid, contract))

    assert result["ok"] is False
    assert "reason" in result["error"]


def test_score_semantic_fidelity_ignores_media_pixels_but_enforces_facts(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (800, 600), "white").save(candidate)

    async def fake_capture(**_kwargs):
        return {
            "ok": True,
            "url": "http://clone",
            "png": str(candidate),
            "page_width": 800.0,
            "page_height": 600.0,
            "bounds": {
                "player": _bounds(height=400),
                "details": _bounds(y=400, height=200),
            },
            "critical_bounds": {"player": _bounds(height=400)},
            "comparison_facts": {
                "player": {
                    "bounds": _bounds(height=400),
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
                "details": {"bounds": _bounds(y=400, height=200)},
            },
        }

    monkeypatch.setattr(verify, "capture_clone_sections", fake_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(sid, url="http://clone")
    )

    assert result["ok"] is True
    assert result["static_score"] == 1.0
    player = next(row for row in result["regions"] if row["id"] == "player")
    assert player["status"] == "pass"
    assert player["excluded_observations"] == ["media_frame_pixels"]
    assert result["raw_whole_page_score"] == 1.0
    assert result["contract"] == str(root / "comparison-contract.json")


def test_score_semantic_fidelity_fails_changed_player_geometry(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (800, 600), "white").save(candidate)

    async def fake_capture(**_kwargs):
        return {
            "ok": True,
            "url": "http://clone",
            "png": str(candidate),
            "page_width": 800.0,
            "page_height": 600.0,
            "bounds": {},
            "critical_bounds": {},
            "comparison_facts": {
                "player": {
                    "bounds": _bounds(width=760, height=400),
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
                "details": {"bounds": _bounds(y=400, height=200)},
            },
        }

    monkeypatch.setattr(verify, "capture_clone_sections", fake_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(sid, url="http://clone")
    )

    assert result["ok"] is False
    player = next(row for row in result["regions"] if row["id"] == "player")
    assert "bounds" in player["failed_invariants"]


def test_repair_packet_uses_only_owner_component_and_records_attempt(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))

    class FakeSandbox:
        async def read_file(self, path):
            return f"// {path}\n" + "x" * 30_000

        async def write_file(self, path, content):
            return True

    monkeypatch.setattr(verify, "get_sandbox", lambda: FakeSandbox())
    report = {
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
                "measurements": {"delta": "typography"},
            },
            {
                "id": "player",
                "owner": "player",
                "status": "pass",
                "score": None,
                "failed_invariants": [],
            },
        ]
    }

    packet_result = asyncio.run(
        verify.build_semantic_repair_packet(
            sid, report, max_text_bytes=4_096
        )
    )
    assert packet_result["ok"] is True
    packet = packet_result["packet"]
    assert packet["target"]["id"] == "details"
    assert list(packet["sources"]) == [
        "src/components/sections/details/Details.jsx"
    ]
    assert packet["text_bytes"] <= 4_096

    first = asyncio.run(
        verify.record_semantic_attempt(
            sid,
            target="details",
            before=0.82,
            after=0.88,
            hard_gate_regressions=[],
            candidate_path="candidate-1",
            packet_bytes=packet["text_bytes"],
            estimated_tokens=packet["estimated_tokens"],
        )
    )
    second = asyncio.run(
        verify.record_semantic_attempt(
            sid,
            target="details",
            before=0.88,
            after=0.85,
            hard_gate_regressions=[],
            candidate_path="candidate-2",
        )
    )
    assert first["accepted"] is True
    assert second["accepted"] is False
    assert second["restore_candidate"] == "candidate-1"
    ledger_path = root / "iteration-ledger.json"
    assert ledger_path.is_file()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["packet_bytes"] == packet["text_bytes"]
    assert ledger["attempts"][0]["estimated_tokens"] == packet["estimated_tokens"]


def test_semantic_tools_are_registered():
    from mcp_server.server import REGISTERED_TOOLS

    for name in (
        "get_comparison_evidence",
        "save_comparison_contract",
        "score_semantic_fidelity",
        "build_semantic_repair_packet",
        "record_semantic_attempt",
    ):
        assert name in REGISTERED_TOOLS
