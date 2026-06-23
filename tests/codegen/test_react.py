"""Tests for the clean IR -> React + Tailwind emitter (Task 12).

The emitter must:
  * map layout/style to Tailwind utility classes,
  * never dump raw inline CSS via ``style={{...}}``,
  * never leak the words ``shopify`` / ``template--``,
  * render recognizer components (Reviews / VideoPlayer / VideoEmbed) as imports,
  * build a ``tailwind.config.js`` theme from the DesignTokens table.
"""

from core.codegen.react import emit_component
from core.codegen.tailwind_theme import emit_tailwind_theme
from core.ir.schema import DesignTokens, IRDocument, IRNode


# --- emit_component ---------------------------------------------------------


def test_clean_jsx():
    n = IRNode(
        id="h",
        role="hero",
        layout={"mode": "flex", "direction": "row"},
        style={"bg": "token.color.surface"},
        children=[],
    )
    jsx = emit_component(n)
    assert "flex" in jsx
    assert "shopify" not in jsx.lower()
    assert "template--" not in jsx
    assert "<style" not in jsx
    # No raw inline CSS dump.
    assert "style={{" not in jsx


def test_flex_direction_and_gap_to_utilities():
    n = IRNode(
        id="row",
        role="block",
        layout={"mode": "flex", "direction": "column", "gap": "token.space.s2"},
        style={},
        children=[],
    )
    jsx = emit_component(n)
    assert "flex" in jsx
    assert "flex-col" in jsx
    # gap token maps to a gap utility, not a raw value.
    assert "gap-" in jsx


def test_grid_columns_to_utility():
    n = IRNode(
        id="g",
        role="grid",
        layout={"mode": "grid", "columns": "repeat(3, 1fr)"},
        style={},
        children=[],
    )
    jsx = emit_component(n)
    assert "grid" in jsx
    assert "grid-cols-3" in jsx


def test_token_style_maps_to_theme_class_not_inline():
    n = IRNode(
        id="t",
        role="text",
        layout={"mode": "block"},
        style={"color": "token.color.ink", "bg": "token.color.surface"},
        children=[],
    )
    jsx = emit_component(n)
    assert "style={{" not in jsx
    # token refs become theme-driven utility classes.
    assert "text-ink" in jsx
    assert "bg-surface" in jsx


def test_children_are_rendered():
    child = IRNode(id="c", role="text", layout={"mode": "block"},
                   style={}, content={"text": "Hello"}, children=[])
    parent = IRNode(id="p", role="block", layout={"mode": "flex"},
                    style={}, children=[child])
    jsx = emit_component(parent)
    assert "Hello" in jsx


def test_recognizer_component_rendered_as_import():
    n = IRNode(
        id="r",
        role="reviews",
        layout={"mode": "block"},
        style={},
        component="Reviews",
        componentProps={"items": [{"author": "A", "rating": 5, "text": "Great", "date": "2024"}]},
        children=[],
    )
    jsx = emit_component(n)
    # Rendered as a component element, not a raw subtree.
    assert "<Reviews" in jsx
    assert "shopify" not in jsx.lower()


def test_video_embed_component():
    n = IRNode(
        id="v",
        role="media",
        layout={"mode": "block"},
        style={},
        component="VideoEmbed",
        componentProps={"src": "https://www.youtube.com/embed/abc"},
        children=[],
    )
    jsx = emit_component(n)
    assert "<VideoEmbed" in jsx


# --- emit_tailwind_theme ----------------------------------------------------


def test_theme_extends_colors_and_space():
    tokens = DesignTokens(
        colors={"ink": "#111111", "surface": "#ffffff"},
        space={"s2": "16px"},
        type={},
        radius={"md": "8px"},
        shadow={"sm": "0 1px 2px rgba(0,0,0,.1)"},
    )
    cfg = emit_tailwind_theme(tokens)
    assert "module.exports" in cfg or "export default" in cfg
    assert "extend" in cfg
    assert "#111111" in cfg
    assert "ink" in cfg
    assert "16px" in cfg
    assert "shopify" not in cfg.lower()


def test_theme_is_valid_js_object_shape():
    tokens = DesignTokens(
        colors={"ink": "#111111"},
        space={},
        type={},
        radius={},
        shadow={},
    )
    cfg = emit_tailwind_theme(tokens)
    assert "colors" in cfg
    # balanced braces sanity check
    assert cfg.count("{") == cfg.count("}")
