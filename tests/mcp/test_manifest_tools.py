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
import hashlib
import json

import pytest
from PIL import Image

from core import scroll_capture
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
        json.dumps({
            "viewport": {"width": 1440, "height": 900},
            "page_height": 4000,
            "breakpoints": [
                {
                    "breakpoint": 1440,
                    "viewport": {"width": 1440, "height": 900},
                    "page_width": 1440,
                    "page_height": 4000,
                    "screenshot": "screenshots/breakpoints/1440/viewport.png",
                    "full_page_screenshot": "screenshots/breakpoints/1440/full.png",
                    "scroll_states": [
                        f"screenshots/breakpoints/1440/scroll_{index:02d}.png"
                        for index in range(5)
                    ],
                    "interaction_evidence": "evidence/breakpoints/1440.json",
                    "device_scale_factor": 1,
                },
                {
                    "breakpoint": 390,
                    "viewport": {"width": 390, "height": 844},
                    "page_width": 390,
                    "page_height": 2800,
                    "screenshot": "screenshots/breakpoints/390/viewport.png",
                    "full_page_screenshot": "screenshots/breakpoints/390/full.png",
                    "scroll_states": [
                        f"screenshots/breakpoints/390/scroll_{index:02d}.png"
                        for index in range(5)
                    ],
                    "interaction_evidence": "evidence/breakpoints/390.json",
                    "device_scale_factor": 1,
                },
            ],
        }),
        encoding="utf-8",
    )
    (st.dir / "manifest.json").write_text(
        json.dumps(
            {
                "success": True,
                "capture_integrity": {"ok": True, "status": "passed"},
            }
        ),
        encoding="utf-8",
    )
    (st.dir / "interactions.json").write_text(
        json.dumps(
            {
                "interactions": [
                    {
                        "id": "menu",
                        "kind": "menu",
                        "target": "#menu-button",
                        "action": "click",
                        "controlled": "#site-menu",
                        "required": True,
                        "expect": {
                            "observable": "aria_expanded_and_menu_visibility_toggle"
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    for width, interaction_id in ((1440, "desktop-menu"), (390, "mobile-menu")):
        viewport_height = 900 if width == 1440 else 844
        page_height = 4000 if width == 1440 else 2800
        region_id = "desktop" if width == 1440 else "mobile"
        state_id = f"i_{width}_{interaction_id}"
        ref = st.dir / "refs" / str(width) / f"{state_id}-fixture.png"
        ref.parent.mkdir(parents=True, exist_ok=True)
        Image.new(
            "RGB",
            (width, 900 if width == 1440 else 844),
            (100, 150, 200),
        ).save(ref)
        facts_payload = {
            "schema": 1,
            "breakpoint": width,
            "state_id": state_id,
            "interaction_id": interaction_id,
            "scroll_y": 0.0,
            "regions": [
                {
                    "id": "desktop-region" if width == 1440 else "mobile-region",
                    "fingerprint": region_id,
                    "kind": "main",
                    "critical": True,
                    "selector": "main",
                    "rect": {"x": 0, "y": 0, "width": width, "height": 400},
                }
            ],
            "facts": {
                region_id: {
                    "bounds": {"x": 0, "y": 0, "width": width, "height": 400},
                    "style": {"display": "block"},
                    "controls": [],
                    "behavior": [{"id": interaction_id, "passed": True}],
                }
            },
        }
        facts_canonical = json.dumps(
            facts_payload, sort_keys=True, separators=(",", ":")
        ).encode()
        facts = (
            st.dir
            / "evidence"
            / "breakpoints"
            / str(width)
            / "interactions"
            / f"{state_id}-fixture.json"
        )
        facts.parent.mkdir(parents=True, exist_ok=True)
        facts.write_text(json.dumps(facts_payload), encoding="utf-8")
        scroll_states = []
        for scroll_y in scroll_capture.scroll_capture_positions(
            page_height, viewport_height, 5
        ):
            scroll_state_id = f"s_{width}_scroll_{scroll_y}"
            scroll_ref = (
                st.dir / "refs" / str(width) / f"{scroll_state_id}-fixture.png"
            )
            Image.new(
                "RGB",
                (width, viewport_height),
                (100, 150, 200),
            ).save(scroll_ref)
            scroll_region = {
                "id": region_id,
                "fingerprint": region_id,
                "kind": "main",
                "position": "fixed",
                "critical": True,
                "selector": "main",
                "rect": {
                    "x": 0,
                    "y": scroll_y,
                    "width": width,
                    "height": 400,
                },
            }
            scroll_payload = {
                "schema": 1,
                "breakpoint": width,
                "state_id": scroll_state_id,
                "scroll_y": float(scroll_y),
                "regions": [scroll_region],
                "facts": {
                    region_id: {
                        "bounds": scroll_region["rect"],
                        "style": {
                            "display": "block",
                            "position": "fixed",
                        },
                        "controls": [],
                    }
                },
            }
            scroll_canonical = json.dumps(
                scroll_payload, sort_keys=True, separators=(",", ":")
            ).encode()
            scroll_facts = (
                st.dir
                / "evidence"
                / "breakpoints"
                / str(width)
                / "scroll"
                / f"{scroll_state_id}-fixture.json"
            )
            scroll_facts.parent.mkdir(parents=True, exist_ok=True)
            scroll_facts.write_text(json.dumps(scroll_payload), encoding="utf-8")
            scroll_states.append(
                {
                    "id": scroll_state_id,
                    "ref": str(scroll_ref.relative_to(st.dir)),
                    "ref_digest": "sha256:"
                    + hashlib.sha256(scroll_ref.read_bytes()).hexdigest(),
                    "facts_path": str(scroll_facts.relative_to(st.dir)),
                    "facts_digest": "sha256:"
                    + hashlib.sha256(scroll_canonical).hexdigest(),
                    "scroll_y": float(scroll_y),
                    "region_ids": [region_id],
                }
            )
        evidence = st.dir / "evidence" / "breakpoints" / f"{width}.json"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(
            json.dumps(
                {
                    "breakpoint": width,
                    "interactions": [
                        {
                            "id": interaction_id,
                            "kind": "menu",
                            "target": f"#{interaction_id}",
                            "action": "click",
                            "required": True,
                            "expect": {
                                "observable": "menu_or_overlay_visibility_toggle"
                            },
                        }
                    ],
                    "page": {"width": width, "height": 4000 if width == 1440 else 2800},
                    "regions": [
                        {
                            "id": "desktop-region" if width == 1440 else "mobile-region",
                            "fingerprint": "desktop" if width == 1440 else "mobile",
                            "kind": "main",
                            "critical": True,
                            "rect": {"x": 0, "y": 0, "width": width, "height": 400},
                        }
                    ],
                    "region_facts": facts_payload["facts"],
                    "scroll_states": scroll_states,
                    "interaction_states": [
                        {
                            "id": state_id,
                            "interaction_id": interaction_id,
                            "ref": str(ref.relative_to(st.dir)),
                            "ref_digest": "sha256:"
                            + hashlib.sha256(ref.read_bytes()).hexdigest(),
                            "facts_path": str(facts.relative_to(st.dir)),
                            "facts_digest": "sha256:"
                            + hashlib.sha256(facts_canonical).hexdigest(),
                            "scroll_y": 0.0,
                            "region_ids": [region_id],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
    # Synthetic full-page screenshot so refs materialization succeeds
    screenshots_dir = st.dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1440, 4000), (100, 150, 200))
    img.save(screenshots_dir / "primary_full.png")
    for width, height, page_height in ((1440, 900, 4000), (390, 844, 2800)):
        breakpoint_dir = screenshots_dir / "breakpoints" / str(width)
        breakpoint_dir.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (width, height), (100, 150, 200)).save(
            breakpoint_dir / "viewport.png"
        )
        Image.new("RGB", (width, page_height), (100, 150, 200)).save(
            breakpoint_dir / "full.png"
        )
        for index in range(5):
            Image.new("RGB", (width, height), (100, 150, 200)).save(
                breakpoint_dir / f"scroll_{index:02d}.png"
            )
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
    assert any(s["channel"] == "baseline" for s in m["states"])
    assert any(s["channel"] == "interaction" for s in m["states"])
    assert out["interactions"] == 2


def test_generate_manifest_seeds_and_materializes_every_captured_breakpoint(store):
    """Mobile is a required replay contract, never a desktop-only afterthought."""
    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is True
    checklist = json.loads((store.dir / "checklist.json").read_text(encoding="utf-8"))
    assert checklist["breakpoints"] == [1440, 390]
    for breakpoint in (1440, 390):
        states = [state for state in checklist["states"] if state["breakpoint"] == breakpoint]
        assert any(state["channel"] == "baseline" for state in states)
        interactions = [state for state in states if state["channel"] == "interaction"]
        assert interactions
        expected_id = "desktop-menu" if breakpoint == 1440 else "mobile-menu"
        assert [state["id"] for state in interactions] == [
            f"i_{breakpoint}_{expected_id}"
        ]
        expected_height = 900 if breakpoint == 1440 else 844
        assert all(
            state["expect"]["bounds"] == {
                "x": 0,
                "y": 0,
                "width": breakpoint,
                "height": expected_height,
            }
            for state in interactions
        )
        assert (store.dir / "refs" / str(breakpoint)).is_dir()
    assert set(out["refs_by_breakpoint"]) == {"1440", "390"}
    assert checklist["structure_by_breakpoint"]["390"]["critical_regions"][0]["id"] == "mobile-region"


def test_generate_manifest_does_not_overwrite_extraction_manifest(store):
    """generate_manifest must NOT write to manifest.json (extraction metadata)."""
    # Write a sentinel extraction manifest to confirm it is untouched
    sentinel = {
        "sentinel": True,
        "url": "original-extraction-data",
        "success": True,
        "capture_integrity": {"ok": True, "status": "passed"},
    }
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


def test_generate_manifest_blocks_unvalidated_source(store):
    (store.dir / "manifest.json").write_text(
        json.dumps({"success": True, "capture_integrity": {"status": "unknown"}})
    )

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert "integrity" in out["error"].lower()


def test_generate_manifest_requires_both_desktop_and_mobile_evidence(store):
    """A legacy one-breakpoint capture may be read, but cannot become green."""
    summary_path = store.dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["breakpoints"] = [summary["breakpoints"][0]]
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert "1440" in out["error"] and "390" in out["error"]


def test_generate_manifest_rejects_unsupported_non_dpr1_evidence(store):
    """The harness deliberately captures at DPR1; it must not infer another DPR."""
    summary_path = store.dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["breakpoints"][1]["device_scale_factor"] = 2
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert "DPR 1" in out["error"]


def test_generate_manifest_rejects_inventory_evidence_without_regions_or_page(store):
    """An interaction list alone is not enough to cover mobile-only static regions."""
    evidence = store.dir / "evidence" / "breakpoints" / "390.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload.pop("regions", None)
    evidence.write_text(json.dumps(payload), encoding="utf-8")

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert "inventory" in out["error"]


@pytest.mark.parametrize("artifact", ["post-trigger-raster", "post-trigger-facts"])
def test_generate_manifest_rejects_tampered_post_trigger_source_evidence(
    store, artifact
):
    evidence = store.dir / "evidence" / "breakpoints" / "390.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    state = payload["interaction_states"][0]
    path = store.dir / (
        state["ref"] if artifact == "post-trigger-raster" else state["facts_path"]
    )
    if artifact == "post-trigger-raster":
        Image.new("RGB", (390, 844), (9, 8, 7)).save(path)
    else:
        facts = json.loads(path.read_text(encoding="utf-8"))
        facts["scroll_y"] = 99
        path.write_text(json.dumps(facts), encoding="utf-8")

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert "inventory" in out["error"]


@pytest.mark.parametrize(
    "fault",
    ["missing_viewport", "corrupt_full", "missing_scroll", "wrong_full_width", "wrong_full_height"],
)
def test_generate_manifest_rejects_incomplete_or_corrupt_breakpoint_evidence(store, fault):
    """Refs must originate in intact, declared source files for every viewport."""
    summary = json.loads((store.dir / "summary.json").read_text(encoding="utf-8"))
    mobile = next(item for item in summary["breakpoints"] if item["breakpoint"] == 390)
    mobile_dir = store.dir / "screenshots" / "breakpoints" / "390"
    if fault == "missing_viewport":
        (mobile_dir / "viewport.png").unlink()
    elif fault == "corrupt_full":
        (mobile_dir / "full.png").write_bytes(b"not a png")
    elif fault == "wrong_full_width":
        Image.new("RGB", (1440, 2800), (1, 2, 3)).save(mobile_dir / "full.png")
    elif fault == "wrong_full_height":
        Image.new("RGB", (390, 2799), (1, 2, 3)).save(mobile_dir / "full.png")
    else:
        scroll = mobile_dir / "scroll_00.png"
        Image.new("RGB", (390, 844), (1, 2, 3)).save(scroll)
        mobile["scroll_states"] = ["screenshots/breakpoints/390/scroll_00.png"]
        scroll.unlink()
    (store.dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    out = asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    assert out["ok"] is False
    assert out["breakpoint"] == 390
    assert "evidence" in out["error"]


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


def test_verify_manifest_rejects_non_sandbox_preview_url(store, monkeypatch):
    asyncio.run(verify_tools.generate_manifest(source_id="src_test"))

    class OwnedPreviewSandbox:
        async def read_file(self, path):
            values = {
                ".pwc/source-id": "src_test",
                ".pwc/run.json": json.dumps(
                    {"run_id": "manifest-run", "source_id": "src_test"}
                ),
                ".pwc/preview.json": json.dumps(
                    {"url": "http://127.0.0.1:4173/"}
                ),
            }
            return values.get(path)

    monkeypatch.setattr(
        verify_tools,
        "get_sandbox",
        lambda: OwnedPreviewSandbox(),
    )
    out = asyncio.run(
        verify_tools.verify_manifest(
            source_id="src_test",
            url="https://unrelated.example/",
        )
    )

    assert out["ok"] is False
    assert "sandbox-owned preview URL" in out["error"]


# --------------------------------------------------------------------------- #
# server registration
# --------------------------------------------------------------------------- #
def test_manifest_tools_are_registered_on_the_server():
    pytest.importorskip("mcp")
    from mcp_server.server import REGISTERED_TOOLS
    assert "generate_manifest" in REGISTERED_TOOLS
    assert "verify_manifest" in REGISTERED_TOOLS
