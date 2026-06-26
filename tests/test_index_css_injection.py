"""P0 wiring — _render_index_css must inject the ordered, cleaned theme CSS.

This is the seam that fixes the cascade-blind union: assemble_project's index.css
now carries the full captured theme stylesheet (ordered, localized, de-fingerprinted)
after the Tailwind layers, so injected real HTML renders with the real cascade."""
from mcp_server.tools.build_deploy import _render_index_css


def test_injects_ordered_cleaned_theme_css():
    source_data = {
        "css": {
            "stylesheets": [
                {"url": "1.css", "content": ".Footer{background:#000}", "is_inline": False},
                {"url": "2.css", "content": ".shopify-section{margin:0} a{background:url(https://store.com/cdn/shop/f.png)}", "is_inline": False},
            ],
            "css_variables": {"--brand": "#123"},
        }
    }
    amap = {"https://store.com/cdn/shop/f.png": "/assets/f.png"}
    out = _render_index_css(source_data, source_url="https://store.com", asset_map=amap)

    assert "@tailwind base" in out                 # tailwind layers kept
    assert "--brand: #123" in out                  # root vars still copied
    assert ".Footer{background:#000}" in out       # real theme rule injected
    assert "/assets/f.png" in out                  # url() localized
    assert "shopify" not in out.lower()            # de-fingerprinted (R1)
    assert "store.com" not in out                  # source domain stripped
    # theme CSS comes AFTER the tailwind base layer so it wins for injected HTML
    assert out.index("@tailwind base") < out.index(".Footer")


def test_no_css_falls_back_to_tailwind_only():
    out = _render_index_css({})
    assert out.strip().startswith("@tailwind base")
    assert "/* captured theme" not in out  # nothing injected when no stylesheets
