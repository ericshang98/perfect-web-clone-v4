"""Tests for core.section_geometry.attach_bounds — fills section bounds from the
persisted DOM geometry (dom.json rect) by matching each section's root element.

This closes the long-standing gap where chunked sections always carry bounds={},
which silently disables self-heal region localization AND per-section fidelity.
"""
from core.section_geometry import attach_bounds, filter_hidden_identified_sections


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


def test_filter_drops_anonymous_closed_modal_without_geometry():
    sections = [
        {
            "name": "modal",
            "full_html": (
                '<div><div class="ant-modal-wrap ant-modal-centered" '
                'style="display: none;"><div role="dialog">Paywall</div></div></div>'
            ),
            "bounds": {},
        }
    ]
    dom = {
        "tag": "body",
        "rect": {"x": 0, "y": 0, "width": 1440, "height": 900},
        "children": [],
    }

    assert filter_hidden_identified_sections(sections, dom) == []


def test_filter_drops_analytics_only_tail_without_geometry():
    sections = [
        {
            "name": "analytics",
            "full_html": '<noscript><img style="display:none"></noscript><script></script>',
            "bounds": {},
        }
    ]
    dom = {
        "tag": "body",
        "rect": {"x": 0, "y": 0, "width": 1440, "height": 900},
        "children": [],
    }

    assert filter_hidden_identified_sections(sections, dom) == []


def test_explicit_id_does_not_fall_back_to_generic_class_match():
    """A hidden drawer id must not borrow another .shopify-section's bounds."""
    sections = [{
        "name": "drawer",
        "full_html": '<div id="cart-drawer" class="shopify-section">x</div>',
        "bounds": {},
    }]
    dom = _dom({
        "tag": "div",
        "id": "visible-product",
        "classes": ["shopify-section"],
        "rect": {"x": 0, "y": 300, "width": 1440, "height": 900},
        "children": [],
    })

    attach_bounds(sections, dom)

    assert sections[0]["bounds"] == {}


def test_filter_hidden_identified_sections_drops_only_missing_ids():
    sections = [
        {
            "name": "header",
            "full_html": '<header id="site-header" class="section">Header</header>',
            "bounds": {},
        },
        {
            "name": "drawer",
            "full_html": '<div id="cart-drawer" class="section">Drawer</div>',
            "bounds": {},
        },
        {
            "name": "anonymous",
            "full_html": '<section class="unknown">Keep when identity is ambiguous</section>',
            "bounds": {},
        },
    ]
    dom = _dom({
        "tag": "header",
        "id": "site-header",
        "classes": ["section"],
        "rect": {"x": 0, "y": 0, "width": 1440, "height": 100},
        "children": [],
    })

    visible = filter_hidden_identified_sections(sections, dom)

    assert [section["name"] for section in visible] == ["header", "anonymous"]


def test_filter_drops_anonymous_root_explicitly_hidden_at_capture():
    sections = [
        {
            "name": "content",
            "full_html": '<main class="content">Visible</main>',
            "bounds": {},
        },
        {
            "name": "cookie-popup",
            "full_html": (
                '<div class="fixed CookiesModal" '
                'style="display: none !important;">Hidden</div>'
            ),
            "bounds": {},
        },
    ]
    dom = _dom(
        {
            "tag": "main",
            "id": None,
            "classes": ["content"],
            "rect": {"x": 0, "y": 0, "width": 1440, "height": 900},
            "children": [],
        }
    )

    visible = filter_hidden_identified_sections(sections, dom)

    assert [section["name"] for section in visible] == ["content"]
