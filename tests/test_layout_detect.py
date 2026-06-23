"""Tests for core.layout_detect.layout_container_keys (pure DOM walk)."""

from core.layout_detect import layout_container_keys


def _node(tag="div", id=None, classes=None, display=None, children=None):
    return {
        "tag": tag,
        "id": id,
        "classes": classes or [],
        "styles": {"display": display} if display else {},
        "children": children or [],
    }


def test_detects_grid_by_id_and_flex_by_classes_excludes_block():
    tree = _node(
        tag="body",
        children=[
            _node(tag="div", id="hero", display="grid"),
            _node(tag="section", classes=["row", "cols-2"], display="flex"),
            _node(tag="div", classes=["plain"], display="block"),
        ],
    )
    keys = layout_container_keys(tree)
    assert keys == {"#hero", ".row.cols-2"}


def test_id_takes_precedence_over_classes():
    tree = _node(id="grid-root", classes=["c1", "c2"], display="grid")
    assert layout_container_keys(tree) == {"#grid-root"}


def test_node_with_no_id_and_no_classes_is_skipped():
    tree = _node(tag="div", display="flex")
    assert layout_container_keys(tree) == set()


def test_all_layout_display_variants_detected():
    tree = _node(
        tag="body",
        children=[
            _node(classes=["a"], display="grid"),
            _node(classes=["b"], display="flex"),
            _node(classes=["c"], display="inline-grid"),
            _node(classes=["d"], display="inline-flex"),
        ],
    )
    assert layout_container_keys(tree) == {".a", ".b", ".c", ".d"}


def test_nested_layout_containers_all_collected():
    tree = _node(
        id="outer",
        display="grid",
        children=[_node(classes=["inner"], display="flex")],
    )
    assert layout_container_keys(tree) == {"#outer", ".inner"}


def test_empty_or_missing_input():
    assert layout_container_keys({}) == set()
    assert layout_container_keys(None) == set()
