"""_render_app_jsx must emit a deterministic per-section anchor.

The self-heal loop needs to measure each section's bounds on the LIVE CLONE
(getBoundingClientRect) to feed score_fidelity_by_section. Bare `<Component />`
renders give the clone DOM no addressable handle, so assemble wraps every
section in `<div data-pwc-section="{namespace}">` — assembly-owned, layout-
neutral for top-level page bands, and stable across re-assembly.
"""
from mcp_server.tools.build_deploy import _render_app_jsx

TEMPLATE = {
    "page_title": "T",
    "source_url": "https://example.com",
    "component_order": [
        {
            "namespace": "hero",
            "import_name": "HeroSection",
            "import_path": "./components/sections/hero/HeroSection",
            "order": 0,
        },
        {
            "namespace": "footer",
            "import_name": "FooterSection",
            "import_path": "./components/sections/footer/FooterSection",
            "order": 1,
        },
    ],
}


def test_each_section_wrapped_in_data_pwc_section_anchor():
    jsx = _render_app_jsx(TEMPLATE)
    assert '<div data-pwc-section="hero">' in jsx
    assert '<div data-pwc-section="footer">' in jsx
    assert "<HeroSection />" in jsx
    assert "<FooterSection />" in jsx


def test_anchor_wraps_its_own_component():
    jsx = _render_app_jsx(TEMPLATE)
    hero_open = jsx.index('<div data-pwc-section="hero">')
    hero_comp = jsx.index("<HeroSection />")
    footer_open = jsx.index('<div data-pwc-section="footer">')
    assert hero_open < hero_comp < footer_open


def test_empty_plan_still_builds_placeholder():
    jsx = _render_app_jsx({"component_order": []})
    assert "No sections to assemble yet" in jsx
    assert "data-pwc-section" not in jsx
