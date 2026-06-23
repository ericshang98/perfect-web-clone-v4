"""Tests for the footer-rebuild recognizer (Task 9 / R7).

A ``role=="footer"`` node whose layout is a grid must carry explicit
``grid-template-columns``/``columns`` (and ``gap``) so the footer cannot
disassemble downstream. If those were dropped, the recognizer reconstructs the
column count by clustering the children's ``sourceBBox.x`` positions and sets
``layout.columns = "repeat(n, 1fr)"``.
"""

from __future__ import annotations

from core.ir.schema import DesignTokens, IRDocument, IRNode
from core.recognizers.footer import footer_rebuild


def _doc(root: IRNode) -> IRDocument:
    return IRDocument(
        root=root,
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )


def _col_child(node_id: str, x: int) -> IRNode:
    return IRNode(
        id=node_id,
        role="block",
        layout={"mode": "block"},
        style={},
        sourceBBox={"x": x, "y": 1280, "w": 200, "h": 300, "breakpoint": 1440},
        children=[],
    )


def test_explicit_columns_preserved():
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "grid", "columns": "repeat(4, 1fr)", "gap": "24px"},
        style={},
        children=[_col_child("c1", 0), _col_child("c2", 360)],
    )
    out = footer_rebuild(_doc(footer))
    f = out.root
    assert f.layout["columns"] == "repeat(4, 1fr)"
    assert f.layout["gap"] == "24px"


def test_infers_columns_from_child_bboxes():
    # Four distinct x columns: 0, 360, 720, 1080.
    children = [
        _col_child("c1", 0),
        _col_child("c2", 360),
        _col_child("c3", 720),
        _col_child("c4", 1080),
    ]
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "grid"},  # columns dropped
        style={},
        children=children,
    )
    out = footer_rebuild(_doc(footer))
    f = out.root
    assert f.layout["columns"] == "repeat(4, 1fr)"


def test_infers_columns_with_multiple_rows():
    # 3 columns across 2 rows -> 6 children, only 3 distinct x positions.
    xs = [0, 480, 960, 0, 480, 960]
    ys = [1280, 1280, 1280, 1600, 1600, 1600]
    children = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        children.append(
            IRNode(
                id=f"c{i}",
                role="block",
                layout={"mode": "block"},
                style={},
                sourceBBox={"x": x, "y": y, "w": 200, "h": 200, "breakpoint": 1440},
                children=[],
            )
        )
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "grid"},
        style={},
        children=children,
    )
    out = footer_rebuild(_doc(footer))
    assert out.root.layout["columns"] == "repeat(3, 1fr)"


def test_clusters_near_x_positions():
    # x positions jittered by a few px should cluster to 2 columns, not 4.
    children = [
        _col_child("c1", 0),
        _col_child("c2", 3),
        _col_child("c3", 700),
        _col_child("c4", 703),
    ]
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "grid"},
        style={},
        children=children,
    )
    out = footer_rebuild(_doc(footer))
    assert out.root.layout["columns"] == "repeat(2, 1fr)"


def test_non_footer_untouched():
    other = IRNode(
        id="g",
        role="grid",
        layout={"mode": "grid"},  # no columns, but not a footer
        style={},
        children=[_col_child("c1", 0), _col_child("c2", 360)],
    )
    out = footer_rebuild(_doc(other))
    assert "columns" not in out.root.layout


def test_nested_footer_found():
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "grid"},
        style={},
        children=[_col_child("c1", 0), _col_child("c2", 360), _col_child("c3", 720)],
    )
    root = IRNode(
        id="r",
        role="page",
        layout={"mode": "block"},
        style={},
        children=[footer],
    )
    out = footer_rebuild(_doc(root))
    f = out.root.children[0]
    assert f.layout["columns"] == "repeat(3, 1fr)"


def test_non_grid_footer_untouched():
    # A footer laid out as flex/block should not get grid columns invented.
    footer = IRNode(
        id="f",
        role="footer",
        layout={"mode": "flex"},
        style={},
        children=[_col_child("c1", 0), _col_child("c2", 360)],
    )
    out = footer_rebuild(_doc(footer))
    assert "columns" not in out.root.layout
