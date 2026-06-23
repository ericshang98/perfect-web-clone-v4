"""Tests for the sticky-guard recognizer (Task 8).

sticky-guard rewrites overflow-clipping ancestors of position:sticky/fixed
nodes so the sticky element can actually pin: a clipping ancestor
(``overflow*`` in {hidden, auto, scroll}) establishes a scroll container that
breaks sticky/fixed positioning. We rewrite each such ancestor to
``overflow-x: clip`` / ``overflow-y: visible`` (never ``hidden``, which itself
forces a scroll container). The sticky node and the containing-block structure
are preserved (no reparenting).
"""

from __future__ import annotations

from core.ir.schema import DesignTokens, IRDocument, IRNode
from core.recognizers.sticky import sticky_guard


def _doc(root: IRNode) -> IRDocument:
    return IRDocument(
        root=root,
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )


def _walk(node: IRNode):
    yield node
    for child in node.children:
        yield from _walk(child)


def test_rewrites_overflow_hidden_ancestor_of_sticky():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"overflow": "hidden"},
        children=[sticky],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    # the clipping ancestor is rewritten so it is no longer a scroll container
    assert by_id["anc"].style.get("overflow-x") == "clip"
    assert by_id["anc"].style.get("overflow-y") == "visible"
    # the generic shorthand must not still say "hidden"
    assert by_id["anc"].style.get("overflow") != "hidden"

    # the sticky node keeps its positioning intact
    assert by_id["sticky"].style.get("position") == "sticky"
    assert by_id["sticky"].style.get("top") == "0px"


def test_rewrites_overflow_x_hidden_ancestor():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"overflow-x": "hidden", "overflow-y": "auto"},
        children=[sticky],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    assert by_id["anc"].style.get("overflow-x") == "clip"
    assert by_id["anc"].style.get("overflow-y") == "visible"


def test_fixed_node_ancestors_also_fixed():
    fixed = IRNode(
        id="fixed",
        role="nav",
        layout={"mode": "fixed"},
        style={"position": "fixed", "top": "0px"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"overflow": "scroll"},
        children=[fixed],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    assert by_id["anc"].style.get("overflow-x") == "clip"
    assert by_id["anc"].style.get("overflow-y") == "visible"


def test_all_clipping_ancestors_rewritten():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    inner = IRNode(
        id="inner",
        role="section",
        layout={"mode": "block"},
        style={"overflow": "hidden"},
        children=[sticky],
    )
    outer = IRNode(
        id="outer",
        role="section",
        layout={"mode": "block"},
        style={"overflow-y": "scroll"},
        children=[inner],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[outer])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    for anc_id in ("inner", "outer"):
        assert by_id[anc_id].style.get("overflow-x") == "clip", anc_id
        assert by_id[anc_id].style.get("overflow-y") == "visible", anc_id


def test_clean_ancestors_untouched():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"color": "token.color.ink"},
        children=[sticky],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    # no overflow keys invented on a clean ancestor
    assert "overflow" not in by_id["anc"].style
    assert "overflow-x" not in by_id["anc"].style
    assert "overflow-y" not in by_id["anc"].style
    assert by_id["anc"].style == {"color": "token.color.ink"}


def test_visible_overflow_ancestor_untouched():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"overflow": "visible"},
        children=[sticky],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    # a non-clipping ancestor is left exactly as-is
    assert by_id["anc"].style == {"overflow": "visible"}


def test_no_sticky_node_means_no_changes():
    child = IRNode(
        id="c",
        role="text",
        layout={"mode": "block"},
        style={"position": "relative"},
        children=[],
    )
    ancestor = IRNode(
        id="anc",
        role="section",
        layout={"mode": "block"},
        style={"overflow": "hidden"},
        children=[child],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[ancestor])

    out = sticky_guard(_doc(root))
    by_id = {n.id: n for n in _walk(out.root)}

    # without any sticky/fixed descendant, the clipping ancestor is left alone
    assert by_id["anc"].style == {"overflow": "hidden"}


def test_returns_document():
    sticky = IRNode(
        id="sticky",
        role="nav",
        layout={"mode": "sticky"},
        style={"position": "sticky", "top": "0px"},
        children=[],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={}, children=[sticky])

    out = sticky_guard(_doc(root))
    assert isinstance(out, IRDocument)
