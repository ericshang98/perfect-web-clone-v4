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


def test_contract_round_trip_is_human_readable(tmp_path):
    path = tmp_path / "comparison-contract.json"
    contract = {"schema": 1, "regions": [_region()]}

    save_contract(contract, path)

    assert load_contract(path) == contract
    assert json.loads(path.read_text(encoding="utf-8")) == contract
    assert region_map(contract) == {"hero": contract["regions"][0]}
