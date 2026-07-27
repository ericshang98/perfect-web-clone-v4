"""Strict visual-state coverage: every required viewport/state is evidence."""
from __future__ import annotations

from core.visual_state_gate import (
    POLICY_VERSION,
    evaluate_visual_state_reports,
    validate_contract_coverage,
)


def _contract(*, mobile_region_ids=None):
    return {
        "schema": 1,
        "regions": [
            {
                "id": "hero",
                "owner": "hero",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": {"x": 0, "y": 0, "width": 100, "height": 60},
                "compare": ["pixels"],
            },
            {
                "id": "video",
                "owner": "player",
                "importance": "critical",
                "mode": "layout_behavior",
                "bounds": {"x": 0, "y": 60, "width": 100, "height": 40},
                "compare": ["bounds", "controls"],
                "reason": "the decoded video frame is volatile",
                "ignore_observations": ["media_frame_pixels"],
            },
        ],
        "coverage": {
            "required_view_ids": ["b1440:s-top", "b390:s-top"],
            "views": {
                "b1440:s-top": {"region_ids": ["hero", "video"], "owner_ids": ["hero", "player"]},
                "b390:s-top": {
                    "region_ids": mobile_region_ids if mobile_region_ids is not None else ["hero", "video"],
                    "owner_ids": ["hero", "player"],
                },
            },
        },
    }


def _source_views():
    return [
        {
            "id": "b1440:s-top",
            "breakpoint": 1440,
            "state_id": "s-top",
            "critical_regions": [
                {"id": "hero", "owner": "hero"},
                {"id": "video", "owner": "player"},
            ],
        },
        {
            "id": "b390:s-top",
            "breakpoint": 390,
            "state_id": "s-top",
            "critical_regions": [
                {"id": "hero", "owner": "hero"},
                {"id": "video", "owner": "player"},
            ],
        },
    ]


def _region(region_id, *, mode="static_pixels", passed=True, raw=0.2):
    row = {
        "id": region_id,
        "owner": "hero" if region_id == "hero" else "player",
        "mode": mode,
        "status": "pass" if passed else "fail",
        "failed_invariants": [] if passed else (["pixels"] if mode == "static_pixels" else ["bounds"]),
        "score": 0.99 if passed else 0.2,
    }
    if mode == "static_pixels":
        row["pixel_report"] = {"score": row["score"]}
    else:
        row["measurements"] = {
            "reference": {"bounds": {"x": 0, "y": 60, "width": 100, "height": 40}, "controls": ["play"]},
            "candidate": {"bounds": {"x": 0, "y": 60, "width": 100, "height": 40}, "controls": ["play"]},
        }
        row["raw_frame_score"] = raw
    return row


def _view(view_id, *, mobile_static_pass=True, video_pass=True, raw=0.1):
    is_mobile = view_id.startswith("b390")
    return {
        "view_id": view_id,
        "policy_version": POLICY_VERSION,
        "contract_digest": "sha256:contract",
        "measured": True,
        "regions": [
            _region("hero", passed=(mobile_static_pass or not is_mobile)),
            _region("video", mode="layout_behavior", passed=video_pass, raw=raw),
        ],
        "raw_whole_page_score": raw,
    }


def test_desktop_pass_and_mobile_static_failure_blocks_visual_gate():
    result = evaluate_visual_state_reports(
        _contract(),
        _source_views(),
        [_view("b1440:s-top"), _view("b390:s-top", mobile_static_pass=False)],
        contract_digest="sha256:contract",
    )

    assert result["ok"] is False
    assert result["failures_by_view"]["b390:s-top"][0]["id"] == "hero"


def test_different_video_frame_passes_when_dynamic_geometry_and_controls_match():
    result = evaluate_visual_state_reports(
        _contract(), _source_views(),
        [_view("b1440:s-top", raw=0.02), _view("b390:s-top", raw=0.98)],
        contract_digest="sha256:contract",
    )

    assert result["ok"] is True
    assert result["views"]["b1440:s-top"]["raw_whole_page_score"] == 0.02


def test_mobile_dynamic_geometry_or_control_mismatch_fails_even_when_frame_is_similar():
    mobile = _view("b390:s-top", raw=0.99)
    mobile["regions"][1]["status"] = "fail"
    mobile["regions"][1]["failed_invariants"] = ["controls"]
    result = evaluate_visual_state_reports(
        _contract(), _source_views(), [_view("b1440:s-top"), mobile],
        contract_digest="sha256:contract",
    )

    assert result["ok"] is False
    assert result["failures_by_view"]["b390:s-top"][0]["failed_invariants"] == ["controls"]


def test_missing_required_state_evidence_fails_closed():
    result = evaluate_visual_state_reports(
        _contract(), _source_views(), [_view("b1440:s-top")],
        contract_digest="sha256:contract",
    )

    assert result["ok"] is False
    assert result["measured_view_ids"] == ["b1440:s-top"]
    assert result["failures_by_view"]["b390:s-top"] == [{"code": "missing_measurement"}]


def test_incomplete_contract_coverage_of_mobile_critical_region_fails():
    errors = validate_contract_coverage(
        _contract(mobile_region_ids=["hero"]), _source_views()
    )

    assert any("b390:s-top" in error and "video" in error for error in errors)


def test_contract_cannot_omit_visible_noncritical_source_region():
    contract = _contract()
    source = _source_views()
    source[0]["regions"] = [
        *source[0]["critical_regions"],
        {"id": "footer", "owner": "footer", "critical": False},
    ]

    errors = validate_contract_coverage(contract, source)
    result = evaluate_visual_state_reports(
        contract,
        source,
        [_view("b1440:s-top"), _view("b390:s-top")],
        contract_digest="sha256:contract",
    )

    assert any(
        "b1440:s-top" in error and "footer" in error
        for error in errors
    )
    assert result["ok"] is False
    assert result["failures_by_view"]["__coverage__"]


def test_named_stateful_pixel_view_still_requires_measured_pixels():
    contract = _contract()
    contract["regions"][0]["mode"] = "stateful_pixels"
    contract["regions"][0]["state"] = "menu-open"
    desktop = _view("b1440:s-top")
    desktop["regions"][0]["mode"] = "stateful_pixels"
    desktop["regions"][0].pop("pixel_report")
    mobile = _view("b390:s-top")
    mobile["regions"][0]["mode"] = "stateful_pixels"
    mobile["regions"][0].pop("pixel_report")

    result = evaluate_visual_state_reports(
        contract, _source_views(), [desktop, mobile], contract_digest="sha256:contract"
    )

    assert result["ok"] is False
    assert result["failures_by_view"]["b1440:s-top"][0]["code"] == "unmeasured_static_pixels"


def test_required_view_with_zero_regions_is_not_counted_as_measured():
    contract = _contract()
    contract["coverage"]["views"]["b390:s-top"] = {"region_ids": [], "owner_ids": []}
    source = _source_views()
    source[1]["critical_regions"] = []
    mobile = _view("b390:s-top")
    mobile["regions"] = []

    result = evaluate_visual_state_reports(
        contract, source, [_view("b1440:s-top"), mobile],
        contract_digest="sha256:contract",
    )

    assert result["ok"] is False
    assert result["failures_by_view"]["b390:s-top"] == [{"code": "zero_region_view"}]
