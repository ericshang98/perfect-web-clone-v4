from core.gates.structure import verify_structure


def _region(name, y, height, kind="section"):
    return {
        "fingerprint": name,
        "kind": kind,
        "critical": True,
        "rect": {"x": 0, "y": y, "width": 800, "height": height},
    }


def _section(name, y, height):
    return {"name": name, "bounds": {"x": 0, "y": y, "width": 800, "height": height}}


def test_missing_hero_fails_even_when_every_planned_section_exists():
    raw_regions = [
        _region("hero", 0, 400, "hero"),
        _region("content", 400, 400),
        _region("footer", 800, 200, "footer"),
    ]
    # A broken planner omitted Hero, and the clone perfectly matched that broken plan.
    planned = [_section("content", 400, 400), _section("footer", 800, 200)]
    candidate = {
        "content": {"x": 0, "y": 0, "width": 800, "height": 400},
        "footer": {"x": 0, "y": 400, "width": 800, "height": 200},
    }

    result = verify_structure(
        source_regions=raw_regions,
        planned_sections=planned,
        candidate_bounds=candidate,
        source_page_height=1000,
        candidate_page_height=600,
    )

    assert result["ok"] is False
    assert "hero" in result["unplanned_critical"]
    assert any(issue["code"] == "critical_region_unplanned" for issue in result["issues"])


def test_planned_critical_section_missing_from_clone_fails():
    raw_regions = [_region("hero", 0, 400, "hero"), _region("content", 400, 600)]
    planned = [_section("hero-section", 0, 400), _section("content", 400, 600)]
    candidate = {"content": {"x": 0, "y": 0, "width": 800, "height": 600}}

    result = verify_structure(
        source_regions=raw_regions,
        planned_sections=planned,
        candidate_bounds=candidate,
        source_page_height=1000,
        candidate_page_height=600,
    )

    assert result["ok"] is False
    assert result["missing_critical"] == ["hero-section"]


def test_complete_structure_passes_with_small_geometry_drift():
    raw_regions = [_region("hero", 0, 400, "hero"), _region("content", 400, 600)]
    planned = [_section("hero-section", 0, 400), _section("content", 400, 600)]
    candidate = {
        "hero-section": {"x": 0, "y": 0, "width": 800, "height": 390},
        "content": {"x": 0, "y": 390, "width": 800, "height": 600},
    }

    result = verify_structure(
        source_regions=raw_regions,
        planned_sections=planned,
        candidate_bounds=candidate,
        source_page_height=1000,
        candidate_page_height=990,
    )

    assert result["ok"] is True
    assert result["unplanned_critical"] == []
    assert result["missing_critical"] == []


def test_required_nested_hero_anchor_cannot_hide_inside_large_content_section():
    raw_regions = [
        _region("hero", 0, 400, "hero"),
        _region("content", 0, 1000),
    ]
    planned = [_section("content", 0, 1000)]
    candidate = {
        "content": {"x": 0, "y": 0, "width": 800, "height": 1000},
    }
    requirements = [
        {
            "anchor": "hero-1",
            "fingerprint": "hero",
            "kind": "hero",
            "owner_section": "content",
            "bounds": {"x": 0, "y": 0, "width": 800, "height": 400},
        }
    ]

    result = verify_structure(
        source_regions=raw_regions,
        planned_sections=planned,
        candidate_bounds=candidate,
        source_page_height=1000,
        candidate_page_height=1000,
        requirements=requirements,
        candidate_critical_bounds={},
    )

    assert result["ok"] is False
    assert result["missing_critical_anchors"] == ["hero-1"]
    assert any(
        issue["code"] == "critical_anchor_missing"
        for issue in result["issues"]
    )


def test_offscreen_required_region_uses_explicit_plan_owner():
    raw_regions = [
        {
            "fingerprint": "carousel-next",
            "kind": "hero",
            "critical": True,
            "rect": {"x": 790, "y": 400, "width": 300, "height": 200},
        }
    ]
    planned = [_section("content", 0, 900)]
    candidate = {"content": {"x": 0, "y": 0, "width": 800, "height": 900}}
    requirements = [
        {
            "anchor": "hero-1",
            "fingerprint": "carousel-next",
            "kind": "hero",
            "owner_section": "content",
            "bounds": {"x": 790, "y": 400, "width": 300, "height": 200},
        }
    ]

    result = verify_structure(
        source_regions=raw_regions,
        planned_sections=planned,
        candidate_bounds=candidate,
        source_page_height=900,
        candidate_page_height=900,
        requirements=requirements,
        candidate_critical_bounds={
            "hero-1": {"x": 790, "y": 400, "width": 300, "height": 200}
        },
    )

    assert result["ok"] is True
    assert result["mapped"]["carousel-next"] == "content"
