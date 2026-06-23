"""Task 3 — IR builder (DOM + computed styles -> normalized tree)."""

from core.ir.builder import build_ir
from core.ir.schema import IRDocument


def test_normalizes_shopify_names_and_layout():
    dom = {
        "tag": "div",
        "id": "template--123__main",
        "classes": ["shopify-section"],
        "rect": {"x": 0, "y": 0, "width": 1440, "height": 100},
        "styles": {"display": "flex", "color": "#111111"},
        "children": [],
    }
    doc = build_ir(dom, css={})
    node = doc.root
    assert node.layout["mode"] == "flex"
    blob = doc.model_dump_json()
    assert "shopify-section" not in blob and "template--" not in blob


def test_returns_document():
    dom = {"tag": "div", "styles": {}, "children": []}
    doc = build_ir(dom, css={})
    assert isinstance(doc, IRDocument)
    assert doc.breakpoints  # non-empty default breakpoints


def test_source_bbox_from_rect():
    dom = {
        "tag": "section",
        "rect": {"x": 0, "y": 1280, "width": 1440, "height": 620},
        "styles": {},
        "children": [],
    }
    doc = build_ir(dom, css={})
    bb = doc.root.sourceBBox
    assert bb is not None
    assert bb["x"] == 0 and bb["y"] == 1280
    assert bb["w"] == 1440 and bb["h"] == 620


def test_style_values_tokenized():
    dom = {"tag": "div", "styles": {"display": "block", "color": "#111111"}, "children": []}
    doc = build_ir(dom, css={})
    assert doc.root.style.get("color", "").startswith("token.color.")
    # the value resolves back to a real color in the token table
    assert "#111111" in doc.tokens.colors.values()


def test_layout_modes_mapped():
    for display, expected in [("flex", "flex"), ("grid", "grid"), ("block", "block")]:
        dom = {"tag": "div", "styles": {"display": display}, "children": []}
        doc = build_ir(dom, css={})
        assert doc.root.layout["mode"] == expected


def test_flex_params_copied():
    dom = {
        "tag": "div",
        "styles": {
            "display": "flex",
            "flex-direction": "column",
            "gap": "16px",
            "justify-content": "center",
            "align-items": "stretch",
        },
        "children": [],
    }
    doc = build_ir(dom, css={})
    layout = doc.root.layout
    assert layout["mode"] == "flex"
    assert layout["direction"] == "column"
    assert "gap" in layout
    assert layout["justify"] == "center"
    assert layout["align"] == "stretch"


def test_grid_columns_copied():
    dom = {
        "tag": "div",
        "styles": {"display": "grid", "grid-template-columns": "repeat(4, 1fr)", "gap": "24px"},
        "children": [],
    }
    doc = build_ir(dom, css={})
    assert doc.root.layout["mode"] == "grid"
    assert doc.root.layout["columns"] == "repeat(4, 1fr)"


def test_position_copied_for_sticky_guard():
    dom = {
        "tag": "div",
        "styles": {"display": "block", "position": "sticky", "top": "0px", "z-index": "30"},
        "children": [],
    }
    doc = build_ir(dom, css={})
    style = doc.root.style
    assert style["position"] == "sticky"
    assert style["top"] == "0px"
    assert str(style.get("z")) == "30" or str(style.get("z-index")) == "30"


def test_roles_derived():
    cases = [
        ("header", "header"),
        ("footer", "footer"),
        ("nav", "nav"),
        ("section", "section"),
        ("figure", "media"),
    ]
    for tag, expected_role in cases:
        dom = {"tag": tag, "styles": {}, "children": []}
        doc = build_ir(dom, css={})
        assert doc.root.role == expected_role


def test_recursive_children_normalized():
    dom = {
        "tag": "div",
        "id": "template--9__main",
        "classes": ["shopify-section"],
        "styles": {},
        "children": [
            {
                "tag": "div",
                "classes": ["shopify-section", "my-card"],
                "styles": {"display": "flex"},
                "children": [],
            }
        ],
    }
    doc = build_ir(dom, css={})
    blob = doc.model_dump_json()
    assert "shopify-section" not in blob and "template--" not in blob
    # the legit class survives
    assert "my-card" in blob
    assert doc.root.children[0].layout["mode"] == "flex"
