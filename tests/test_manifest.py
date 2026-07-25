"""core.manifest — the per-site state-checklist contract (spec §3).

Pure dict schema; the manifest is born at capture, verified at gate time,
shipped with the deliverable. Statuses: pending|pass|fail|waived.
"""
import json

import pytest

from core.manifest import (
    VALID_STATUSES,
    add_state,
    load_manifest,
    new_manifest,
    save_manifest,
    update_status,
    validate_state,
    interaction_states,
)


def _state(sid="s_scroll_0", **over):
    st = {
        "id": sid,
        "section": None,
        "breakpoint": 1440,
        "trigger": [{"kind": "scroll", "y": 0}],
        "expect": {"ref": f"refs/1440/{sid}.png", "ssim": 0.97,
                   "bounds": {"x": 0, "y": 0, "width": 1440, "height": 900}},
        "channel": "baseline",
        "evidence": None,
        "stability": "stable",
        "status": "pending",
    }
    st.update(over)
    return st


def test_new_manifest_shape():
    m = new_manifest("https://example.com", [1440, 375])
    assert m["url"] == "https://example.com"
    assert m["breakpoints"] == [1440, 375]
    assert m["states"] == []
    assert m["schema"] == 2


def test_validate_state_ok():
    assert validate_state(_state()) == []


def test_validate_state_rejects_bad_trigger_kind_and_status():
    errs = validate_state(_state(trigger=[{"kind": "teleport"}], status="maybe"))
    assert any("trigger" in e for e in errs)
    assert any("status" in e for e in errs)


def test_add_state_rejects_duplicate_id():
    m = new_manifest("u", [1440])
    add_state(m, _state())
    with pytest.raises(ValueError):
        add_state(m, _state())


def test_add_state_rejects_invalid_state():
    m = new_manifest("u", [1440])
    with pytest.raises(ValueError):
        add_state(m, _state(trigger=[{"kind": "teleport"}]))


def test_update_status_lifecycle():
    m = new_manifest("u", [1440])
    add_state(m, _state())
    update_status(m, "s_scroll_0", "pass")
    assert m["states"][0]["status"] == "pass"
    with pytest.raises(ValueError):
        update_status(m, "s_scroll_0", "nope")
    with pytest.raises(KeyError):
        update_status(m, "missing", "pass")
    assert VALID_STATUSES == {"pending", "pass", "fail", "waived"}


def test_save_load_roundtrip(tmp_path):
    m = new_manifest("u", [1440])
    add_state(m, _state())
    p = tmp_path / "manifest.json"
    save_manifest(m, p)
    assert load_manifest(p) == m
    # file is stable, human-diffable json
    assert json.loads(p.read_text(encoding="utf-8"))["states"][0]["id"] == "s_scroll_0"


from core.manifest import baseline_states
from core.scroll_capture import scroll_capture_positions


def test_baseline_states_follow_scroll_positions():
    states = baseline_states(page_height=8000, viewport=(1440, 900), breakpoint=1440)
    ys = scroll_capture_positions(8000, 900, n=5)
    assert [s["trigger"][0]["y"] for s in states] == ys
    for s, y in zip(states, ys):
        assert s["id"] == f"s_1440_scroll_{y}"
        assert s["channel"] == "baseline"
        assert s["status"] == "pending"
        assert s["expect"]["ref"] == f"refs/1440/s_1440_scroll_{y}.png"
        assert s["expect"]["bounds"] == {"x": 0, "y": y, "width": 1440, "height": 900}
        assert validate_state(s) == []


def test_baseline_states_short_page_yields_at_least_initial():
    states = baseline_states(page_height=500, viewport=(1440, 900), breakpoint=1440)
    assert states and states[0]["trigger"] == [{"kind": "scroll", "y": 0}]


def test_interaction_contracts_become_required_verifiable_states_without_raster_ref():
    contracts = [
        {
            "id": "next",
            "kind": "carousel",
            "target": "#next",
            "action": "click",
            "controlled": None,
            "required": True,
            "expect": {
                "observable": "selected_slide_or_visible_content_changes"
            },
        },
        {
            "id": "menu",
            "kind": "menu",
            "target": "#menu",
            "action": "click",
            "controlled": "#nav",
            "required": True,
            "expect": {
                "observable": "aria_expanded_and_menu_visibility_toggle"
            },
        },
    ]

    states = interaction_states(contracts, breakpoint=1440)

    assert {state["interaction_kind"] for state in states} == {"carousel", "menu"}
    assert all(state["channel"] == "interaction" for state in states)
    assert all(state["required"] is True for state in states)
    assert all(validate_state(state) == [] for state in states)
    assert all("ref" not in state["expect"] for state in states)
    assert states[0]["trigger"] == [
        {"kind": "click", "target": '[data-pwc-interaction="next"]'}
    ]
    assert states[0]["source_target"] == "#next"
    assert states[1]["expect"]["controlled"] == (
        '[data-pwc-controlled="menu"]'
    )
