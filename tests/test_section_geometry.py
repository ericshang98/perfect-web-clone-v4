"""Tests for core.section_geometry.attach_bounds — fills section bounds from the
persisted DOM geometry (dom.json rect) by matching each section's root element.

This closes the long-standing gap where chunked sections always carry bounds={},
which silently disables self-heal region localization AND per-section fidelity.
"""
from core.section_geometry import attach_bounds


def _dom(*nodes):
    return {"tag": "body", "rect": {"x": 0, "y": 0, "width": 1440, "height": 900},
            "children": list(nodes)}


def test_attach_bounds_matches_by_id():
    sections = [{"name": "hero", "full_html": '<section id="home-hero" class="section">x</section>', "bounds": {}}]
    dom = _dom({"tag": "section", "id": "home-hero", "classes": ["section"],
                "rect": {"x": 0, "y": 0, "width": 1440, "height": 906}, "children": []})
    attach_bounds(sections, dom)
    assert sections[0]["bounds"]["width"] == 1440
    assert sections[0]["bounds"]["height"] == 906


def test_attach_bounds_matches_by_tag_and_class_when_no_id():
    sections = [{"name": "footer", "full_html": '<footer class="site-footer">x</footer>', "bounds": {}}]
    dom = _dom({"tag": "footer", "id": None, "classes": ["site-footer"],
                "rect": {"x": 0, "y": 5000, "width": 1440, "height": 400}, "children": []})
    attach_bounds(sections, dom)
    assert sections[0]["bounds"]["y"] == 5000
    assert sections[0]["bounds"]["height"] == 400


def test_attach_bounds_leaves_empty_when_no_match():
    sections = [{"name": "x", "full_html": '<div class="nope">x</div>', "bounds": {}}]
    dom = _dom({"tag": "section", "id": None, "classes": ["yes"],
                "rect": {"x": 0, "y": 0, "width": 10, "height": 10}, "children": []})
    attach_bounds(sections, dom)
    assert sections[0]["bounds"] == {}


def test_attach_bounds_finds_nested_node():
    sections = [{"name": "feature", "full_html": '<section id="feat">x</section>', "bounds": {}}]
    dom = _dom({"tag": "div", "id": None, "classes": ["wrap"], "rect": {"x": 0, "y": 0, "width": 1440, "height": 900},
                "children": [{"tag": "section", "id": "feat", "classes": [],
                              "rect": {"x": 0, "y": 200, "width": 1200, "height": 600}, "children": []}]})
    attach_bounds(sections, dom)
    assert sections[0]["bounds"]["y"] == 200
    assert sections[0]["bounds"]["height"] == 600
