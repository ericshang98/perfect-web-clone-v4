"""Tests for the video-collector recognizer (Task 11, R9).

The recognizer maps media nodes to data-driven video components:

- a ``<video>`` media node with a resolved local ``assetRef`` becomes
  ``component="VideoPlayer"`` with ``componentProps.src`` pointing at the local
  asset;
- a youtube/vimeo ``<iframe>`` node becomes ``component="VideoEmbed"`` with the
  embed URL in ``componentProps.src``;
- a node carrying only a lazy ``data-src`` has it promoted to ``src``;
- non-media nodes are left untouched.
"""

from __future__ import annotations

from core.ir.schema import DesignTokens, IRDocument, IRNode
from core.recognizers.video import video_collector


def _doc(root: IRNode) -> IRDocument:
    return IRDocument(
        root=root,
        tokens=DesignTokens(colors={}, space={}, type={}, radius={}, shadow={}),
        breakpoints=[1440],
    )


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def test_video_node_becomes_videoplayer_with_local_src():
    video = IRNode(
        id="v1",
        role="media",
        tag="video",
        content={"assetRef": "assets/media/hero.mp4", "poster": "assets/img/p.jpg"},
        children=[],
    )
    root = IRNode(id="r", role="page", children=[video])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["v1"]
    assert node.component == "VideoPlayer"
    assert node.componentProps["src"] == "assets/media/hero.mp4"
    assert node.componentProps.get("poster") == "assets/img/p.jpg"


def test_source_child_provides_video_src():
    """A <video> whose URL lives on a <source> child is still resolved."""
    source = IRNode(
        id="s1",
        role="media",
        tag="source",
        content={"src": "assets/media/clip.webm"},
        children=[],
    )
    video = IRNode(id="v2", role="media", tag="video", content={}, children=[source])
    root = IRNode(id="r", role="page", children=[video])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["v2"]
    assert node.component == "VideoPlayer"
    assert node.componentProps["src"] == "assets/media/clip.webm"


def test_youtube_iframe_becomes_videoembed():
    iframe = IRNode(
        id="e1",
        role="media",
        tag="iframe",
        content={"src": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
        children=[],
    )
    root = IRNode(id="r", role="page", children=[iframe])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["e1"]
    assert node.component == "VideoEmbed"
    assert node.componentProps["src"] == "https://www.youtube.com/embed/dQw4w9WgXcQ"


def test_vimeo_iframe_becomes_videoembed():
    iframe = IRNode(
        id="e2",
        role="media",
        tag="iframe",
        content={"src": "https://player.vimeo.com/video/76979871"},
        children=[],
    )
    root = IRNode(id="r", role="page", children=[iframe])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["e2"]
    assert node.component == "VideoEmbed"


def test_data_src_is_promoted_to_src():
    video = IRNode(
        id="v3",
        role="media",
        tag="video",
        content={"data-src": "assets/media/lazy.mp4"},
        children=[],
    )
    root = IRNode(id="r", role="page", children=[video])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["v3"]
    # data-src promoted onto content.src and used as the player source
    assert node.content.get("src") == "assets/media/lazy.mp4"
    assert node.component == "VideoPlayer"
    assert node.componentProps["src"] == "assets/media/lazy.mp4"


def test_non_video_iframe_is_not_videoembed():
    iframe = IRNode(
        id="e3",
        role="media",
        tag="iframe",
        content={"src": "https://maps.google.com/embed?pb=xyz"},
        children=[],
    )
    root = IRNode(id="r", role="page", children=[iframe])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["e3"]
    assert node.component is None


def test_non_media_node_untouched():
    text = IRNode(id="t1", role="text", tag="p", content={"text": "hi"}, children=[])
    root = IRNode(id="r", role="page", children=[text])
    out = video_collector(_doc(root))

    node = {n.id: n for n in _walk(out.root)}["t1"]
    assert node.component is None
    assert node.componentProps == {}


def test_returns_irdocument():
    root = IRNode(id="r", role="page", children=[])
    out = video_collector(_doc(root))
    assert isinstance(out, IRDocument)
