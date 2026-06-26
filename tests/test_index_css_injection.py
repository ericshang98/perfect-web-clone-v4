"""P0 wiring — the theme CSS is emitted as a SEPARATE static stylesheet.

index.css stays Tailwind+tokens (PostCSS-processed). The full ordered theme CSS
goes to public/theme.css (served verbatim, NOT through PostCSS — real themes carry
typos like `!importnat` that browsers ignore but PostCSS rejects), plus rest-state
overrides so a faithful-CSS clone isn't left blank by JS-gated visibility."""
from mcp_server.tools.build_deploy import _render_index_css, _render_theme_css


def _source():
    return {
        "css": {
            "stylesheets": [
                {"url": "1.css", "content": ".Footer{background:#000}", "is_inline": False},
                {"url": "2.css", "content": ".shopify-section{margin:0} a{background:url(https://store.com/cdn/shop/f.png)}", "is_inline": False},
            ],
            "css_variables": {"--brand": "#123"},
        }
    }


def test_index_css_is_tailwind_plus_tokens_only_no_theme():
    out = _render_index_css(_source())
    assert "@tailwind base" in out
    assert "--brand: #123" in out          # root tokens still copied
    assert ".Footer" not in out            # theme CSS is NOT in index.css anymore


def test_theme_css_has_ordered_cleaned_rules_and_rest_state_override():
    amap = {"https://store.com/cdn/shop/f.png": "/assets/f.png"}
    out = _render_theme_css(_source(), source_url="https://store.com", asset_map=amap)
    assert ".Footer{background:#000}" in out   # real theme rule, ordered
    assert "/assets/f.png" in out              # url() localized
    assert "shopify" not in out.lower()        # de-fingerprinted (R1)
    assert "store.com" not in out              # source domain stripped
    # rest-state override appended LAST so it wins (page not left blank by JS gates)
    assert "opacity:1!important" in out
    assert out.index(".Footer") < out.index("opacity:1!important")


def test_theme_css_empty_when_no_stylesheets():
    assert _render_theme_css({}) == ""
    assert _render_theme_css({"css": {"stylesheets": []}}) == ""
