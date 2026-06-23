"""Tests for the reviews recognizer (Task 10 / R8).

The recognizer detects a review-widget subtree by its platform class/id
signatures (judge.me, loox, yotpo, okendo, stamped, shopify-product-reviews),
sets ``node.component = "Reviews"``, fills ``componentProps.items`` with the
extracted ``{author, rating, text, date}`` records, and drops the raw subtree
children (they are replaced by the data-driven component).
"""

from __future__ import annotations

from core.ir.schema import DesignTokens, IRDocument, IRNode
from core.recognizers.reviews import reviews


def _doc(root: IRNode) -> IRDocument:
    return IRDocument(
        root=root,
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )


def _review_item(author, stars, text, date, *, item_class="jdgm-rev", role="block"):
    """Build a single review item subtree the way the IR builder shapes it."""
    return IRNode(
        id=f"rev_{author}",
        role=role,
        layout={},
        style={},
        content={"classes": [item_class]},
        children=[
            IRNode(
                id=f"author_{author}",
                role="text",
                layout={},
                style={},
                content={"classes": ["jdgm-rev__author"], "text": author},
                children=[],
            ),
            IRNode(
                id=f"rating_{author}",
                role="block",
                layout={},
                style={},
                # rating encoded as N starred children (star count = rating)
                content={"classes": ["jdgm-rev__rating"]},
                children=[
                    IRNode(
                        id=f"star_{author}_{i}",
                        role="block",
                        layout={},
                        style={},
                        content={"classes": ["jdgm-star", "jdgm-star--on"]},
                        children=[],
                    )
                    for i in range(stars)
                ],
            ),
            IRNode(
                id=f"body_{author}",
                role="text",
                layout={},
                style={},
                content={"classes": ["jdgm-rev__body"], "text": text},
                children=[],
            ),
            IRNode(
                id=f"date_{author}",
                role="text",
                layout={},
                style={},
                content={"classes": ["jdgm-rev__timestamp"], "text": date},
                children=[],
            ),
        ],
    )


def _judgeme_widget():
    """A judge.me reviews widget node with two review items."""
    return IRNode(
        id="widget",
        role="section",
        layout={},
        style={},
        content={"classes": ["jdgm-rev-widg"]},
        children=[
            _review_item("Alice", 5, "Great product!", "2024-01-02"),
            _review_item("Bob", 4, "Pretty good.", "2024-02-15"),
        ],
    )


def test_detects_judgeme_and_sets_component():
    root = IRNode(
        id="r", role="page", layout={"mode": "block"}, style={},
        children=[_judgeme_widget()],
    )
    out = reviews(_doc(root))
    widget = out.root.children[0]
    assert widget.component == "Reviews"


def test_extracts_review_items():
    root = IRNode(
        id="r", role="page", layout={"mode": "block"}, style={},
        children=[_judgeme_widget()],
    )
    out = reviews(_doc(root))
    items = out.root.children[0].componentProps["items"]
    assert len(items) == 2

    first = items[0]
    assert set(first.keys()) >= {"author", "rating", "text", "date"}
    assert first["author"] == "Alice"
    assert first["rating"] == 5
    assert first["text"] == "Great product!"
    assert first["date"] == "2024-01-02"

    assert items[1]["author"] == "Bob"
    assert items[1]["rating"] == 4


def test_drops_raw_subtree_children():
    root = IRNode(
        id="r", role="page", layout={"mode": "block"}, style={},
        children=[_judgeme_widget()],
    )
    out = reviews(_doc(root))
    widget = out.root.children[0]
    # raw item markup replaced by the data-driven component
    assert widget.children == []


def test_non_reviews_node_untouched():
    inner = IRNode(
        id="card", role="block", layout={}, style={},
        content={"classes": ["product-card"]},
        children=[
            IRNode(id="t", role="text", layout={}, style={},
                   content={"text": "hello"}, children=[]),
        ],
    )
    root = IRNode(
        id="r", role="page", layout={"mode": "block"}, style={},
        children=[inner],
    )
    out = reviews(_doc(root))
    node = out.root.children[0]
    assert node.component is None
    assert node.componentProps == {}
    assert len(node.children) == 1


def test_detects_loox_yotpo_okendo_stamped_spr():
    for sig, cls in [
        ("loox", "loox-reviews"),
        ("yotpo", "yotpo-main-widget"),
        ("okendo", "okeReviews-widget"),
        ("okendo2", "oke-reviews"),
        ("stamped", "stamped-reviews"),
        ("spr", "spr-reviews"),
    ]:
        widget = IRNode(
            id=f"w_{sig}", role="section", layout={}, style={},
            content={"classes": [cls]},
            children=[_review_item("Carol", 3, "ok", "2024-03-01",
                                   item_class=f"{cls}-item")],
        )
        root = IRNode(id="r", role="page", layout={"mode": "block"}, style={},
                      children=[widget])
        out = reviews(_doc(root))
        assert out.root.children[0].component == "Reviews", f"signature {sig} not detected"


def test_signature_on_id_attribute():
    widget = IRNode(
        id="judgeme_product_reviews", role="section", layout={}, style={},
        content={},
        children=[_review_item("Dave", 5, "love it", "2024-04-04")],
    )
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={},
                  children=[widget])
    out = reviews(_doc(root))
    assert out.root.children[0].component == "Reviews"


def test_returns_irdocument():
    root = IRNode(id="r", role="page", layout={"mode": "block"}, style={},
                  children=[_judgeme_widget()])
    out = reviews(_doc(root))
    assert isinstance(out, IRDocument)
