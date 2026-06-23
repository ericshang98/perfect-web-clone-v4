"""Task 1 — IR schema (the stable contract).

Covers docs/architecture.md §5: IRNode / DesignTokens / IRDocument.
"""

import pytest

from core.ir.schema import IRNode, IRDocument, DesignTokens


def test_irnode_roundtrip():
    n = IRNode(
        id="n1",
        role="hero",
        layout={"mode": "flex"},
        style={"color": "token.color.ink"},
        children=[],
    )
    assert IRNode.model_validate(n.model_dump()).id == "n1"


def test_irnode_required_fields_exist():
    n = IRNode(id="n1", role="hero", layout={}, style={}, children=[])
    dumped = n.model_dump()
    for field in ("id", "role", "layout", "style", "children"):
        assert field in dumped


def test_irnode_optional_fields_default():
    n = IRNode(id="n1", role="text", layout={}, style={}, children=[])
    # §5 advisory / recognizer fields
    assert n.tag is None or isinstance(n.tag, str)
    assert n.content == {}
    assert n.component is None
    assert n.componentProps == {}
    assert n.sourceBBox is None


def test_irnode_recursive_children():
    child = IRNode(id="c", role="text", layout={}, style={}, children=[])
    parent = IRNode(id="p", role="grid", layout={"mode": "grid"}, style={}, children=[child])
    rebuilt = IRNode.model_validate(parent.model_dump())
    assert rebuilt.children[0].id == "c"


def test_design_tokens_holds_all_maps():
    t = DesignTokens(
        colors={"ink": "#111"},
        space={"4": "16px"},
        type={"body": "16px/1.5 sans"},
        radius={"md": "8px"},
        shadow={"sm": "0 1px 2px rgba(0,0,0,.1)"},
    )
    assert t.colors["ink"] == "#111"
    assert t.space["4"] == "16px"
    assert "body" in t.type
    assert t.radius["md"] == "8px"
    assert t.shadow["sm"].startswith("0 1px")


def test_document():
    doc = IRDocument(
        root=IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[]),
        tokens=DesignTokens(colors={"ink": "#111"}, space={"4": "16px"}, type={}, radius={}, shadow={}),
        breakpoints=[1440, 768, 375],
    )
    assert 1440 in doc.breakpoints and doc.tokens.colors["ink"] == "#111"


def test_document_roundtrip():
    doc = IRDocument(
        root=IRNode(id="r", role="page", layout={}, style={}, children=[]),
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )
    rebuilt = IRDocument.model_validate(doc.model_dump())
    assert rebuilt.root.id == "r"
    assert rebuilt.breakpoints == [1440]
