"""Agent-facing semantic comparison tools.

These tests keep the reasoning/tool boundary explicit: the Agent classifies
regions, while deterministic MCP tools persist, measure, localize, and record.
"""
from __future__ import annotations

import asyncio
import hashlib
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
                "compare": [
                    "bounds",
                    "aspect_ratio",
                    "container_style",
                    "controls",
                    "interaction",
                ],
                "ignore_observations": ["media_frame_pixels"],
                "reason": "decoded media frames change independently of page CSS",
                "reference_facts": {
                    "bounds": _bounds(height=400),
                    "style": {"display": "block"},
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


def _active_run(source_id):
    gates = (
        "capture_integrity",
        "critical_structure",
        "interactions",
        "build",
        "fingerprints",
        "weight",
        "runtime",
        "responsive",
        "visual",
    )
    return {
        "schema": 2,
        "run_id": "semantic-run",
        "source_id": source_id,
        "phase": "verify",
        "status": "running",
        "gate_results": {
            name: {
                "status": "pending" if name == "visual" else "pass",
                "evidence": [],
            }
            for name in gates
        },
        "attempts": [],
        "residuals": [],
        "token_usage": {
            "budget_status": {"status": "ok", "can_start_repair": True}
        },
    }


class _RunSandbox:
    def __init__(self, source_id):
        self.files = {
            ".pwc/source-id": source_id,
            ".pwc/run.json": json.dumps(_active_run(source_id)),
            ".pwc/preview.json": json.dumps(
                {"url": "http://127.0.0.1:4173/"}
            ),
            "src/components/sections/player/Player.jsx": (
                "export default function Player(){return 'player'}"
            ),
            "src/components/sections/details/Details.jsx": (
                "export default function Details(){return 'details'}"
            ),
        }

    async def read_file(self, path):
        if path in self.files:
            return self.files[path]
        return f"// {path}\n" + "x" * 30_000

    async def write_file(self, path, content):
        self.files[path] = content
        return True

    async def delete_file(self, path):
        self.files.pop(path, None)
        return True


def _stamp_active_hard_gates(sandbox):
    from core.run_controller import record_gate_evidence

    run = json.loads(sandbox.files[".pwc/run.json"])
    for gate in run["active_attempt"]["required_hard_gates"]:
        run = record_gate_evidence(
            run,
            gate=gate,
            passed=True,
            evidence=[f"measured:{gate}"],
        )
    sandbox.files[".pwc/run.json"] = json.dumps(run)


def test_get_comparison_evidence_is_bounded_and_keeps_agent_decision_explicit(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    (root / "checklist.json").write_text(
        json.dumps(
            {
                "source_region_universe": [
                    {
                        "id": "player",
                        "owner": "player",
                        "kind": "video",
                        "position": "static",
                        "critical": True,
                        "breakpoints": [800],
                        "bounds": _bounds(height=400),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = asyncio.run(verify.get_comparison_evidence(sid))

    assert result["ok"] is True, result
    assert result["capture_integrity"]["status"] == "passed"
    assert result["volatility"]["candidates"][0]["requires_agent_decision"] is True
    assert result["critical_regions"][0]["id"] == "player"
    assert result["source_regions"][0]["id"] == "player"
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
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
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
                    "style": {"display": "block"},
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
                "details": {"bounds": _bounds(y=400, height=200)},
            },
        }

    monkeypatch.setattr(verify, "capture_clone_sections", fake_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(
            sid,
            url="http://127.0.0.1:4173/",
        )
    )

    assert result["ok"] is True
    assert result["static_score"] == 1.0
    player = next(row for row in result["regions"] if row["id"] == "player")
    assert player["status"] == "pass"
    assert player["excluded_observations"] == ["media_frame_pixels"]
    assert result["raw_whole_page_score"] == 1.0
    assert result["contract"] == str(root / "comparison-contract.json")


def test_strict_score_replays_every_checklist_view_and_persists_visual_coverage(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    sandbox.files[".pwc/run.json"] = json.dumps({**_active_run(sid), "schema": 4})
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    for width in (800, 390):
        ref = root / "refs" / str(width)
        ref.mkdir(parents=True)
        Image.new("RGB", (width, 600), "white").save(ref / "top.png")
    (root / "checklist.json").write_text(
        json.dumps(
            {
                "states": [
                    {
                        "id": "top-desktop", "breakpoint": 800,
                        "trigger": [{"kind": "scroll", "y": 0}],
                        "expect": {"ref": "refs/800/top.png", "bounds": _bounds(width=800, height=600)},
                        "channel": "baseline",
                    },
                    {
                        "id": "top-mobile", "breakpoint": 390,
                        "trigger": [{"kind": "scroll", "y": 0}],
                        "expect": {"ref": "refs/390/top.png", "bounds": _bounds(width=390, height=600)},
                        "channel": "baseline",
                    },
                ],
                "source_region_universe": [
                    {
                        "id": "player",
                        "owner": "player",
                        "critical": True,
                        "bounds": _bounds(width=800, height=400),
                    }
                ],
                "structure_by_breakpoint": {
                    "800": {
                        "regions": [{"fingerprint": "player", "critical": True, "rect": _bounds(width=800, height=400)}],
                        "critical_regions": [{"fingerprint": "player", "critical": True, "rect": _bounds(width=800, height=400)}],
                        "region_facts": {"player": {"style": {"display": "block"}, "controls": ["play"], "interaction": ["player-toggle"]}},
                    },
                    "390": {
                        "regions": [{"fingerprint": "player", "critical": True, "rect": _bounds(width=390, height=400)}],
                        "critical_regions": [{"fingerprint": "player", "critical": True, "rect": _bounds(width=390, height=400)}],
                        "region_facts": {"player": {"style": {"display": "block"}, "controls": ["play"], "interaction": ["player-toggle"]}},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    desktop = tmp_path / "desktop.png"
    mobile = tmp_path / "mobile.png"
    Image.new("RGB", (800, 600), "white").save(desktop)
    Image.new("RGB", (390, 600), "white").save(mobile)

    def fake_capture(_url, views, _regions, out):
        out.mkdir(parents=True, exist_ok=True)
        desktop_owned = out / "desktop.png"
        mobile_owned = out / "mobile.png"
        desktop_owned.write_bytes(desktop.read_bytes())
        mobile_owned.write_bytes(mobile.read_bytes())
        desktop_digest = (
            "sha256:" + hashlib.sha256(desktop_owned.read_bytes()).hexdigest()
        )
        mobile_digest = (
            "sha256:" + hashlib.sha256(mobile_owned.read_bytes()).hexdigest()
        )
        return {
            "b800:top-desktop": {
                "png": str(desktop_owned),
                "png_digest": desktop_digest,
                "facts": {"player": {"bounds": _bounds(width=800, height=400), "style": {"display": "block"}, "controls": ["play"], "interaction": ["player-toggle"]}},
                "scroll_y": 0,
            },
            "b390:top-mobile": {
                "png": str(mobile_owned),
                "png_digest": mobile_digest,
                "facts": {"player": {"bounds": _bounds(width=390, height=400), "style": {"display": "block"}, "controls": ["play"], "interaction": ["player-toggle"]}},
                "scroll_y": 0,
            },
        }

    import core.visual_state_capture as state_capture
    monkeypatch.setattr(state_capture, "capture_visual_state_views", fake_capture)
    result = asyncio.run(verify.score_semantic_fidelity(sid, url="http://127.0.0.1:4173/"))

    assert result["ok"] is True, result
    details = result["visual_details"]
    assert details["required_view_ids"] == ["b800:top-desktop", "b390:top-mobile"]
    assert details["measured_view_ids"] == details["required_view_ids"]
    assert details["failures_by_view"] == {}
    persisted = json.loads(sandbox.files[".pwc/run.json"])
    assert persisted["gate_results"]["visual"]["details"]["policy_version"] == "visual-state-v1"


def test_source_coverage_uses_only_regions_visible_in_each_scroll_view():
    contract = {
        "schema": 1,
        "regions": [
            {"id": "top", "owner": "top", "mode": "static_pixels", "bounds": _bounds(y=0, height=100), "compare": ["pixels"]},
            {"id": "bottom", "owner": "bottom", "mode": "static_pixels", "bounds": _bounds(y=900, height=100), "compare": ["pixels"]},
        ],
    }
    views = [
        {"id": "b800:top", "state_id": "top", "state": {"expect": {"bounds": _bounds(y=0, height=300)}}, "regions": [{"id": "top", "owner": "top"}], "critical_regions": [{"id": "top", "owner": "top"}]},
        {"id": "b800:bottom", "state_id": "bottom", "state": {"expect": {"bounds": _bounds(y=800, height=300)}}, "regions": [{"id": "bottom", "owner": "bottom"}], "critical_regions": [{"id": "bottom", "owner": "bottom"}]},
    ]

    materialized = verify._materialize_source_coverage(contract, views)

    assert materialized["coverage"]["views"]["b800:top"]["region_ids"] == ["top"]
    assert materialized["coverage"]["views"]["b800:bottom"]["region_ids"] == ["bottom"]


def test_scrolled_views_keep_fixed_and_sticky_source_regions_visible():
    regions = [
        {
            "fingerprint": "fixed-header",
            "position": "fixed",
            "rect": _bounds(y=0, width=800, height=60),
            "critical": True,
        },
        {
            "fingerprint": "sticky-nav",
            "position": "sticky",
            "rect": _bounds(y=120, width=800, height=50),
            "critical": False,
        },
        {
            "fingerprint": "ordinary-top",
            "position": "static",
            "rect": _bounds(y=0, width=800, height=100),
            "critical": False,
        },
    ]

    visible = verify._view_visible_regions(
        regions,
        viewport_y=1000,
        viewport_height=600,
    )
    by_id = {region["id"]: region for region in visible}

    assert set(by_id) == {"fixed-header", "sticky-nav"}
    assert by_id["fixed-header"]["bounds"]["y"] == 0
    assert by_id["sticky-nav"]["bounds"]["y"] == 0


def test_bounded_region_universe_round_robins_mobile_and_state_only_regions():
    desktop = [
        {
            "fingerprint": f"desktop-{index}",
            "kind": "section",
            "critical": False,
            "rect": _bounds(y=index * 100, width=800, height=80),
        }
        for index in range(64)
    ]
    mobile = [
        {
            "fingerprint": "mobile-only",
            "kind": "navigation",
            "critical": True,
            "rect": _bounds(width=390, height=200),
        }
    ]
    interaction = [
        {
            "fingerprint": "drawer-open-only",
            "kind": "section",
            "critical": False,
            "rect": _bounds(width=390, height=300),
        }
    ]

    universe = verify._bounded_source_region_universe(
        [
            ("b1440:rest", 1440, desktop),
            ("b390:rest", 390, mobile),
            ("b390:drawer-open", 390, interaction),
        ]
    )
    ids = {region["id"] for region in universe}

    assert len(universe) == 64
    assert {"mobile-only", "drawer-open-only"} <= ids


def test_bounded_region_universe_keeps_prompt_size_stable_across_many_states():
    regions = [
        {
            "fingerprint": f"region-{index:02d}-with-a-stable-name",
            "owner": f"owner-{index:02d}-with-a-stable-name",
            "kind": "section",
            "critical": False,
            "signals": {
                "interactive": True,
                "media": False,
                "dynamic": True,
            },
            "rect": _bounds(
                x=index,
                y=index * 100,
                width=390,
                height=80,
            ),
        }
        for index in range(64)
    ]
    universe = verify._bounded_source_region_universe(
        [
            (f"b390:interaction-state-{state}", 390, regions)
            for state in range(32)
        ]
    )

    payload_bytes = len(
        json.dumps(universe, separators=(",", ":")).encode("utf-8")
    )

    assert len(universe) == 64
    assert max(len(region["states"]) for region in universe) == 2
    assert payload_bytes < 32_768


def test_mobile_noncritical_reflow_uses_mobile_source_bounds_and_facts():
    contract = {
        "schema": 1,
        "regions": [
            {
                "id": "card-grid",
                "owner": "catalog",
                "importance": "important",
                "mode": "static_pixels",
                "bounds": _bounds(x=80, y=200, width=640, height=300),
                "compare": ["pixels"],
            }
        ],
    }
    mobile_bounds = _bounds(x=12, y=120, width=366, height=560)
    view = {
        "id": "b390:mobile",
        "state_id": "mobile",
        "state": {"expect": {"bounds": _bounds(width=390, height=844)}},
        "regions": [
            {
                "id": "card-grid",
                "owner": "catalog",
                "critical": False,
                "bounds": mobile_bounds,
            }
        ],
        "critical_regions": [],
        "reference_facts": {
            "card-grid": {
                "bounds": mobile_bounds,
                "style": {"display": "grid"},
                "controls": [],
            }
        },
    }

    materialized = verify._materialize_source_coverage(contract, [view])
    effective, facts = verify._view_contract_and_facts(materialized, view)

    assert materialized["coverage"]["views"][view["id"]]["region_ids"] == [
        "card-grid"
    ]
    assert effective["regions"][0]["bounds"] == mobile_bounds
    assert facts["card-grid"]["bounds"] == mobile_bounds


def test_strict_source_contract_discards_agent_forged_reference_facts(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    ref = root / "refs" / "800"
    ref.mkdir(parents=True)
    Image.new("RGB", (800, 600), "white").save(ref / "top.png")
    source_bounds = _bounds(width=800, height=400)
    (root / "checklist.json").write_text(
        json.dumps(
            {
                "states": [
                    {
                        "id": "top",
                        "breakpoint": 800,
                        "trigger": [{"kind": "scroll", "y": 0}],
                        "expect": {
                            "ref": "refs/800/top.png",
                            "bounds": _bounds(width=800, height=600),
                        },
                        "channel": "baseline",
                    }
                ],
                "source_region_universe": [
                    {
                        "id": "player",
                        "owner": "player",
                        "critical": True,
                        "bounds": source_bounds,
                    }
                ],
                "structure_by_breakpoint": {
                    "800": {
                        "regions": [
                            {
                                "fingerprint": "player",
                                "critical": True,
                                "rect": source_bounds,
                            }
                        ],
                        "critical_regions": [
                            {
                                "fingerprint": "player",
                                "critical": True,
                                "rect": source_bounds,
                            }
                        ],
                        "region_facts": {
                            "player": {
                                "bounds": source_bounds,
                                "style": {"display": "block"},
                                "controls": ["source-play"],
                            }
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    forged = _contract()
    forged["regions"][0]["reference_facts"] = {
        "bounds": _bounds(width=1, height=1),
        "style": {"display": "none"},
        "controls": ["forged"],
    }

    result = asyncio.run(verify.save_comparison_contract(sid, forged))

    assert result["ok"] is True, result
    persisted = json.loads(
        (root / "comparison-contract.json").read_text(encoding="utf-8")
    )
    assert "reference_facts" not in persisted["regions"][0]
    views, error = verify._source_visual_views(verify.SourceStore(sid))
    assert error is None
    effective, source_facts = verify._view_contract_and_facts(persisted, views[0])
    assert effective["regions"][0]["bounds"] == source_bounds
    assert source_facts["player"]["controls"] == ["source-play"]


def test_comparison_evidence_includes_mobile_only_critical_fingerprint(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    summary["breakpoints"] = [
        {
            "breakpoint": 390,
            "interaction_evidence": "evidence/breakpoints/390.json",
        }
    ]
    (root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    breakpoint = root / "evidence" / "breakpoints" / "390.json"
    breakpoint.parent.mkdir(parents=True, exist_ok=True)
    breakpoint.write_text(
        json.dumps(
            {
                "regions": [
                    {
                        "fingerprint": "mobile-drawer",
                        "critical": True,
                        "kind": "navigation",
                        "rect": _bounds(width=390, height=240),
                    },
                    {
                        "fingerprint": "mobile-footer",
                        "critical": False,
                        "kind": "footer",
                        "position": "static",
                        "signals": {"heading": False, "media": False, "controls": 0},
                        "rect": _bounds(y=1000, width=390, height=300),
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (root / "checklist.json").write_text(
        json.dumps(
            {
                "source_region_universe": [
                    {
                        "id": "mobile-drawer",
                        "owner": "mobile-drawer",
                        "kind": "navigation",
                        "critical": True,
                        "breakpoints": [390],
                        "bounds": _bounds(width=390, height=240),
                    },
                    {
                        "id": "mobile-footer",
                        "owner": "mobile-footer",
                        "kind": "footer",
                        "critical": False,
                        "breakpoints": [390],
                        "bounds": _bounds(y=1000, width=390, height=300),
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = asyncio.run(verify.get_comparison_evidence(sid))

    mobile = next(
        row
        for row in result["critical_regions"]
        if row["id"] == "mobile-drawer"
    )
    assert mobile["breakpoints"] == [390]
    source_ids = {row["id"] for row in result["source_regions"]}
    assert {"mobile-drawer", "mobile-footer"} <= source_ids


def test_visual_measurement_rejects_candidate_that_did_not_reach_source_scroll(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    ref = root / "refs" / "800"
    ref.mkdir(parents=True)
    Image.new("RGB", (800, 600), "white").save(ref / "scroll.png")
    bounds = _bounds(y=0, width=800, height=200)
    source_view = {
        "id": "b800:scroll-500",
        "breakpoint": 800,
        "state_id": "scroll-500",
        "state": {
            "channel": "baseline",
            "trigger": [{"kind": "scroll", "y": 500}],
            "expect": {
                "ref": "refs/800/scroll.png",
                "bounds": _bounds(y=500, width=800, height=600),
            },
        },
        "regions": [
            {"id": "hero", "owner": "hero", "bounds": bounds, "critical": True}
        ],
        "critical_regions": [
            {"id": "hero", "owner": "hero", "bounds": bounds, "critical": True}
        ],
        "reference_facts": {"hero": {"bounds": bounds}},
    }
    contract = verify._materialize_source_coverage(
        {
            "schema": 1,
            "regions": [
                {
                    "id": "hero",
                    "owner": "hero",
                    "importance": "critical",
                    "mode": "static_pixels",
                    "bounds": bounds,
                    "compare": ["pixels"],
                }
            ],
        },
        [source_view],
    )
    candidate = tmp_path / "candidate-scroll.png"
    Image.new("RGB", (800, 600), "white").save(candidate)

    def fake_capture(*_args, **_kwargs):
        return {
            source_view["id"]: {
                "png": str(candidate),
                "facts": {"hero": {"bounds": bounds}},
                "scroll_y": 0,
            }
        }

    import core.visual_state_capture as state_capture

    monkeypatch.setattr(state_capture, "capture_visual_state_views", fake_capture)
    report = asyncio.run(
        verify._measure_visual_state_reports(
            verify.SourceStore(sid),
            "http://127.0.0.1:4173/",
            contract,
            [source_view],
            threshold=0.97,
        )
    )

    assert report["ok"] is False
    assert report["measured_view_ids"] == []
    assert report["failures_by_view"][source_view["id"]][0]["code"] == (
        "unmeasured_view"
    )


def test_score_semantic_fidelity_fails_changed_player_geometry(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
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
                    "style": {"display": "block"},
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
                "details": {"bounds": _bounds(y=400, height=200)},
            },
        }

    monkeypatch.setattr(verify, "capture_clone_sections", fake_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(
            sid,
            url="http://127.0.0.1:4173/",
        )
    )

    assert result["ok"] is False
    player = next(row for row in result["regions"] if row["id"] == "player")
    assert "bounds" in player["failed_invariants"]


def test_semantic_scoring_rejects_non_sandbox_preview_url(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))

    async def should_not_capture(**_kwargs):
        raise AssertionError("foreign URL must be rejected before capture")

    monkeypatch.setattr(verify, "capture_clone_sections", should_not_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(
            sid,
            url="https://unrelated.example/",
        )
    )

    assert result["ok"] is False
    assert "sandbox-owned preview URL" in result["error"]


def test_semantic_failure_persists_report_digest_and_repair_obligation(
    tmp_path, monkeypatch
):
    sid, root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
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
                    "style": {"display": "block"},
                    "controls": ["play"],
                    "interaction": ["player-toggle"],
                },
                "details": {"bounds": _bounds(y=400, height=200)},
            },
        }

    monkeypatch.setattr(verify, "capture_clone_sections", fake_capture)
    result = asyncio.run(
        verify.score_semantic_fidelity(
            sid,
            url="http://127.0.0.1:4173/",
        )
    )

    assert result["execution_ok"] is True
    assert result["gate_status"] == "fail"
    assert result["must_continue"] is True
    assert result["next_action"] == "repair:player"
    assert result["terminal_allowed"] == []
    persisted = json.loads(sandbox.files[".pwc/run.json"])
    assert persisted["phase"] == "repair"
    assert persisted["pending_repair"]["target"] == "player"
    assert persisted["latest_semantic_report"]["digest"].startswith("sha256:")
    assert json.loads(sandbox.files[".pwc/semantic-report.json"])["ok"] is False
    assert (root / "latest-semantic-report.json").is_file()
    packet = asyncio.run(
        verify.build_semantic_repair_packet(sid, result, max_text_bytes=4_096)
    )
    assert packet["ok"] is True
    assert packet["packet"]["target"]["id"] == "player"


def test_repair_packet_rejects_stale_or_tampered_semantic_report(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
            }
        ],
    }
    persisted = asyncio.run(
        verify.persist_semantic_report(sid, report, _contract())
    )
    assert persisted["ok"] is True

    valid = asyncio.run(
        verify.build_semantic_repair_packet(
            sid, report, max_text_bytes=4_096
        )
    )
    tampered = json.loads(json.dumps(report))
    tampered["regions"][0]["score"] = 0.99
    rejected = asyncio.run(
        verify.build_semantic_repair_packet(
            sid, tampered, max_text_bytes=4_096
        )
    )

    assert valid["ok"] is True
    assert rejected["ok"] is False
    assert "stale or tampered" in rejected["error"]


def test_repair_packet_rejects_plateaued_target(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
            }
        ],
    }
    asyncio.run(verify.persist_semantic_report(sid, report, _contract()))
    for index in range(2):
        packet = asyncio.run(
            verify.build_semantic_repair_packet(sid, report)
        )
        assert packet["ok"] is True
        candidate_report = json.loads(json.dumps(report))
        candidate_report["regions"][0]["score"] = 0.81 - index * 0.01
        asyncio.run(
            verify.persist_semantic_report(
                sid,
                candidate_report,
                _contract(),
            )
        )
        _stamp_active_hard_gates(sandbox)
        result = asyncio.run(
            verify.record_semantic_attempt(
                sid,
                target="details",
                before=0.82,
                after=0.99,
                hard_gate_regressions=[],
            )
        )
    assert result["stop_code"] == "plateau"
    run = json.loads(sandbox.files[".pwc/run.json"])
    assert run["pending_repair"]["attempts_remaining"] == 3

    packet = asyncio.run(
        verify.build_semantic_repair_packet(sid, report)
    )

    assert packet["ok"] is False
    assert "no longer eligible" in packet["error"]


def test_standalone_packet_also_rejects_iteration_ledger_plateau(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))

    class StandaloneSandbox:
        async def read_file(self, path):
            if path == ".pwc/source-id":
                return "another-source"
            return f"// {path}\n" + "x" * 30_000

        async def write_file(self, path, content):
            return True

    monkeypatch.setattr(verify, "get_sandbox", lambda: StandaloneSandbox())
    report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
            }
        ],
    }
    asyncio.run(verify.persist_semantic_report(sid, report, _contract()))
    asyncio.run(
        verify.record_semantic_attempt(sid, "details", 0.82, 0.81, [])
    )
    asyncio.run(
        verify.record_semantic_attempt(sid, "details", 0.82, 0.80, [])
    )

    packet = asyncio.run(verify.build_semantic_repair_packet(sid, report))

    assert packet["ok"] is False
    assert "iteration limit" in packet["error"]


def test_active_persist_chooses_deterministic_worst_region(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "status": "fail",
                "score": 0.9,
                "failed_invariants": ["bounds"],
            },
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.2,
                "failed_invariants": ["pixels"],
            },
        ],
    }

    result = asyncio.run(
        verify.persist_semantic_report(sid, report, _contract())
    )

    assert result["next_action"] == "repair:details"


def test_semantic_persist_without_active_run_fails_closed(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    asyncio.run(verify.save_comparison_contract(sid, _contract()))
    monkeypatch.setattr(verify, "get_sandbox", lambda: None)
    report = {
        "ok": True,
        "source_id": sid,
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "status": "pass",
                "score": None,
                "failed_invariants": [],
            }
        ],
    }

    result = asyncio.run(
        verify.persist_semantic_report(sid, report, _contract())
    )

    assert result["execution_ok"] is False
    assert result["must_continue"] is True
    assert result["next_action"] == "assemble_or_resume_run"
    assert result["terminal_allowed"] == []


def test_contract_change_invalidates_prior_semantic_obligation(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    first_contract = _contract()
    asyncio.run(verify.save_comparison_contract(sid, first_contract))
    report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
            }
        ],
    }
    asyncio.run(verify.persist_semantic_report(sid, report, first_contract))
    old_digest = json.loads(sandbox.files[".pwc/run.json"])[
        "latest_semantic_report"
    ]["digest"]
    changed_contract = json.loads(json.dumps(first_contract))
    changed_contract["regions"][1]["importance"] = "critical"

    saved = asyncio.run(
        verify.save_comparison_contract(sid, changed_contract)
    )

    assert saved["ok"] is True
    run = json.loads(sandbox.files[".pwc/run.json"])
    assert run["gate_results"]["visual"]["status"] == "pending"
    assert "latest_semantic_report" not in run
    assert "pending_repair" not in run
    stale = asyncio.run(
        verify.build_semantic_repair_packet(sid, report)
    )
    assert stale["ok"] is False
    assert old_digest not in json.dumps(run)


def test_rejected_candidate_uses_fresh_measured_report_and_restores_snapshot(
    tmp_path, monkeypatch
):
    sid, _root = _source(tmp_path, monkeypatch)
    sandbox = _RunSandbox(sid)
    details_path = "src/components/sections/details/Details.jsx"
    sandbox.files[details_path] = "export default function Details(){return 'original'}"
    sandbox.files["src/index.css"] = "/* baseline css */"
    monkeypatch.setattr(verify, "get_sandbox", lambda: sandbox)
    contract = _contract()
    asyncio.run(verify.save_comparison_contract(sid, contract))
    before_report = {
        "ok": False,
        "source_id": sid,
        "regions": [
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.82,
                "failed_invariants": ["pixels"],
            }
        ],
    }
    asyncio.run(verify.persist_semantic_report(sid, before_report, contract))
    baseline_run = json.loads(sandbox.files[".pwc/run.json"])
    baseline_run["gate_results"]["runtime"] = {
        "status": "pass",
        "epoch": 0,
        "evidence": ["baseline-runtime.json"],
        "details": {"code_version": "restored"},
    }
    sandbox.files[".pwc/run.json"] = json.dumps(baseline_run)
    packet = asyncio.run(
        verify.build_semantic_repair_packet(sid, before_report)
    )
    assert packet["ok"] is True
    sandbox.files[details_path] = "export default function Details(){return 'bad'}"
    shared_path = "src/index.css"
    sandbox.files[shared_path] = "candidate css"
    added_path = "src/candidate-only.js"
    sandbox.files[added_path] = "candidate only"

    stale_attempt = asyncio.run(
        verify.record_semantic_attempt(
            sid,
            target="details",
            before=0.82,
            after=0.99,
            hard_gate_regressions=[],
        )
    )
    assert stale_attempt["ok"] is False
    assert "fresh semantic re-score" in stale_attempt["error"]

    after_report = json.loads(json.dumps(before_report))
    after_report["regions"][0]["score"] = 0.70
    asyncio.run(verify.persist_semantic_report(sid, after_report, contract))
    stale_hard_gates = asyncio.run(
        verify.record_semantic_attempt(
            sid,
            target="details",
            before=0.01,
            after=1.0,
            hard_gate_regressions=[],
            candidate_path="/caller/untrusted",
        )
    )
    assert stale_hard_gates["ok"] is False
    assert "fresh hard-gate evidence" in stale_hard_gates["error"]

    _stamp_active_hard_gates(sandbox)
    candidate_run = json.loads(sandbox.files[".pwc/run.json"])
    candidate_run["gate_results"]["runtime"] = {
        "status": "fail",
        "epoch": candidate_run["active_attempt"]["epoch"],
        "evidence": ["candidate-runtime.json"],
        "details": {"code_version": "candidate"},
    }
    sandbox.files[".pwc/run.json"] = json.dumps(candidate_run)
    result = asyncio.run(
        verify.record_semantic_attempt(
            sid,
            target="details",
            before=0.01,
            after=1.0,
            hard_gate_regressions=[],
            candidate_path="/caller/untrusted",
        )
    )

    assert result["ok"] is True
    assert result["accepted"] is False
    assert result["before"] == 0.82
    assert result["after"] == 0.70
    assert result["restored"] is True
    assert sandbox.files[details_path] == (
        "export default function Details(){return 'original'}"
    )
    assert sandbox.files[shared_path] == "/* baseline css */"
    assert added_path not in sandbox.files
    restored_run = json.loads(sandbox.files[".pwc/run.json"])
    assert restored_run["gate_results"]["runtime"] == {
        "status": "pass",
        "epoch": 0,
        "evidence": ["baseline-runtime.json"],
        "details": {"code_version": "restored"},
    }


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
        "ok": False,
        "source_id": sid,
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
    persisted = asyncio.run(
        verify.persist_semantic_report(sid, report, _contract())
    )
    assert persisted["ok"] is True

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
        "get_harness_run_state",
        "finalize_run",
    ):
        assert name in REGISTERED_TOOLS
