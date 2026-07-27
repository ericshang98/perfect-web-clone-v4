import json

from core.comparison_contract import (
    load_contract,
    region_map,
    save_contract,
    validate_contract,
)


def _region(**overrides):
    value = {
        "id": "hero",
        "owner": "hero",
        "importance": "critical",
        "mode": "static_pixels",
        "bounds": {"x": 0, "y": 80, "width": 1440, "height": 600},
        "compare": ["pixels"],
    }
    value.update(overrides)
    return value


def test_static_region_requires_bounds_and_owner():
    contract = {"schema": 1, "regions": [_region()]}

    assert validate_contract(contract) == []


def test_non_static_region_requires_reason_ignored_observation_and_replacement():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="video",
                owner="player",
                mode="layout_behavior",
                compare=["pixels"],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("reason" in error for error in errors)
    assert any("ignore_observations" in error for error in errors)
    assert any("replacement invariant" in error for error in errors)


def test_layout_style_requires_complete_geometry_and_container_style_policy():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="clock",
                mode="layout_style",
                compare=["bounds"],
                reason="clock digits change",
                ignore_observations=["live_text"],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("bounds, aspect_ratio, container_style" in error for error in errors)


def test_layout_behavior_requires_geometry_style_and_controls_or_behavior():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="video",
                mode="layout_behavior",
                compare=["bounds", "aspect_ratio", "container_style"],
                reason="video frames change",
                ignore_observations=["media_frame_pixels"],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("controls or behavior" in error for error in errors)


def test_stateful_pixels_requires_a_named_state_and_pixel_measurement():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="drawer-open",
                mode="stateful_pixels",
                compare=["bounds"],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("named state" in error for error in errors)
    assert any("pixels comparison" in error for error in errors)


def test_critical_residual_is_fail_closed():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="canvas",
                mode="residual",
                compare=[],
                reason="unmeasurable",
            )
        ],
    }

    assert any("critical residual" in error for error in validate_contract(contract))


def test_duplicate_region_ids_are_rejected():
    contract = {"schema": 1, "regions": [_region(), _region()]}

    assert any("duplicate region id" in error for error in validate_contract(contract))


def test_behavior_invariant_requires_bounded_replay_contract():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="settings",
                mode="layout_behavior",
                compare=["bounds", "behavior"],
                reason="the menu has an observable open state",
                ignore_observations=["clock_value"],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("behaviors" in error for error in errors)


def test_behavior_ids_must_be_unique():
    behavior = {
        "id": "settings-open",
        "trigger": '[data-pwc-interaction="settings"]',
        "assert": "visible",
    }
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="settings",
                mode="layout_behavior",
                compare=["bounds", "behavior"],
                reason="the menu has an observable open state",
                ignore_observations=["clock_value"],
                behaviors=[behavior, dict(behavior)],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("duplicate behavior id" in error for error in errors)


def test_contract_rejects_unbounded_agent_text_and_invariants():
    contract = {
        "schema": 1,
        "regions": [
            _region(
                id="video",
                mode="layout_behavior",
                compare=[
                    "bounds",
                    "aspect_ratio",
                    "container_style",
                    "controls",
                    "invented",
                ],
                reason="x" * 321,
                ignore_observations=["x" * 161],
            )
        ],
    }

    errors = validate_contract(contract)

    assert any("unknown comparison invariants" in error for error in errors)
    assert any("reason exceeds" in error for error in errors)
    assert any("ignore_observations" in error for error in errors)


def test_contract_rejects_global_behavior_and_serialized_size_explosion():
    behavior = {
        "id": "open",
        "trigger": "#trigger",
        "target": "#panel",
        "assert": "visible",
        "before": ["#prepare"] * 8,
    }
    regions = []
    for region_index in range(5):
        behaviors = [
            {**behavior, "id": f"open-{region_index}-{behavior_index}"}
            for behavior_index in range(16)
        ]
        regions.append(
            _region(
                id=f"menu-{region_index}",
                owner=f"menu-{region_index}",
                mode="layout_behavior",
                compare=[
                    "bounds",
                    "aspect_ratio",
                    "container_style",
                    "behavior",
                ],
                reason="menu state changes after a click",
                ignore_observations=["transition_frame"],
                behaviors=behaviors,
            )
        )
    contract = {"schema": 1, "regions": regions}

    behavior_errors = validate_contract(contract)
    oversized = json.loads(json.dumps(contract))
    oversized["padding"] = "x" * 140_000
    size_errors = validate_contract(oversized)

    assert any("total behaviors" in error for error in behavior_errors)
    assert any("total prerequisite selectors" in error for error in behavior_errors)
    assert any("serialized bytes" in error for error in size_errors)


def test_contract_round_trip_is_human_readable(tmp_path):
    path = tmp_path / "comparison-contract.json"
    contract = {"schema": 1, "regions": [_region()]}

    save_contract(contract, path)

    assert load_contract(path) == contract
    assert json.loads(path.read_text(encoding="utf-8")) == contract
    assert region_map(contract) == {"hero": contract["regions"][0]}
