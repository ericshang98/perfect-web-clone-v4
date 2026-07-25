from core.structure_contract import build_structure_requirements


def _region(fingerprint, kind, y, height, critical=True):
    return {
        "fingerprint": fingerprint,
        "kind": kind,
        "critical": critical,
        "rect": {"x": 0, "y": y, "width": 1440, "height": height},
    }


def test_requirements_promote_standalone_hero_not_page_sized_wrappers():
    regions = [
        _region("root-wrapper", "hero", 0, 6450),
        _region("page-main", "hero", 122, 5976),
        _region("real-hero", "hero", 56, 484),
        _region("header", "header", 56, 66),
        _region("footer", "footer", 6098, 352),
    ]
    sections = [
        {
            "name": "header",
            "bounds": {"x": 0, "y": 56, "width": 1440, "height": 66},
        },
        {
            "name": "content",
            "bounds": {"x": 0, "y": 122, "width": 1440, "height": 5976},
        },
        {
            "name": "footer",
            "bounds": {"x": 0, "y": 6098, "width": 1440, "height": 352},
        },
    ]

    requirements = build_structure_requirements(
        regions,
        sections,
        viewport_height=900,
    )

    assert [item["anchor"] for item in requirements] == [
        "hero-1",
        "header-1",
        "footer-1",
    ]
    hero = requirements[0]
    assert hero["fingerprint"] == "real-hero"
    assert hero["owner_section"] == "content"
    assert hero["bounds"]["height"] == 484


def test_offscreen_carousel_region_maps_to_single_vertical_owner():
    regions = [
        {
            "fingerprint": "carousel-next-slide",
            "kind": "hero",
            "critical": True,
            "rect": {"x": 1428, "y": 553, "width": 416, "height": 202},
        }
    ]
    sections = [
        {
            "name": "page",
            "bounds": {"x": 0, "y": 0, "width": 1440, "height": 900},
        }
    ]

    requirements = build_structure_requirements(
        regions,
        sections,
        viewport_height=900,
    )

    assert requirements[0]["owner_section"] == "page"
