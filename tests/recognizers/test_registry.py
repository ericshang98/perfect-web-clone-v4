"""Tests for the pluggable recognizer registry (Task 7)."""

from __future__ import annotations

import pytest

from core.ir.schema import DesignTokens, IRDocument, IRNode
import core.recognizers as recognizers
from core.recognizers import register, run_all


@pytest.fixture(autouse=True)
def _clean_registry():
    """Each test starts with an empty registry and restores it after."""
    saved = list(recognizers._RECOGNIZERS)
    recognizers._RECOGNIZERS.clear()
    try:
        yield
    finally:
        recognizers._RECOGNIZERS.clear()
        recognizers._RECOGNIZERS.extend(saved)


def _doc():
    root = IRNode(
        id="r",
        role="page",
        layout={"mode": "block"},
        style={},
        children=[
            IRNode(id="a", role="reviews", layout={}, style={}, children=[]),
            IRNode(id="b", role="text", layout={}, style={}, children=[]),
        ],
    )
    return IRDocument(
        root=root,
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def test_register_returns_callable():
    @register
    def my_recognizer(doc):
        return doc

    assert my_recognizer in recognizers._RECOGNIZERS
    # decorator returns the original function unchanged
    assert callable(my_recognizer)


def test_run_all_applies_recognizer():
    @register
    def set_reviews(doc):
        for node in _walk(doc.root):
            if node.role == "reviews":
                node.component = "X"
        return doc

    doc = _doc()
    out = run_all(doc)
    result = out["doc"]
    by_id = {n.id: n for n in _walk(result.root)}
    assert by_id["a"].component == "X"
    assert by_id["b"].component is None


def test_runs_in_registration_order():
    order = []

    @register
    def first(doc):
        order.append("first")
        return doc

    @register
    def second(doc):
        order.append("second")
        return doc

    run_all(_doc())
    assert order == ["first", "second"]


def test_exception_is_caught_and_recorded():
    @register
    def boom(doc):
        raise ValueError("kaboom")

    @register
    def ok(doc):
        for node in _walk(doc.root):
            if node.role == "reviews":
                node.component = "Y"
        return doc

    out = run_all(_doc())
    reports = out["reports"]
    by_name = {r["name"]: r for r in reports}

    # the failing recognizer is recorded, not fatal
    assert by_name["boom"]["error"] is not None
    assert "kaboom" in by_name["boom"]["error"]

    # the later recognizer still ran and changed the doc
    assert by_name["ok"]["error"] is None
    result = out["doc"]
    by_id = {n.id: n for n in _walk(result.root)}
    assert by_id["a"].component == "Y"


def test_changed_flag_reported():
    @register
    def mutator(doc):
        for node in _walk(doc.root):
            if node.role == "reviews":
                node.component = "Z"
        return doc

    @register
    def noop(doc):
        return doc

    out = run_all(_doc())
    by_name = {r["name"]: r for r in out["reports"]}
    assert by_name["mutator"]["changed"] is True
    assert by_name["noop"]["changed"] is False
