"""Tests for core.anim_normalize.reveal_animation_states — neutralizes the
animation-transient inline styles that a scroll/reveal site has frozen at capture
time (opacity:0, display:none, visibility:hidden, blur, offscreen transforms),
so captured content is visible in a static clone instead of invisible.
"""
from core.anim_normalize import reveal_animation_states


def test_removes_opacity_zero_inline():
    out, n = reveal_animation_states('<div style="opacity: 0; color: red;">x</div>')
    assert "opacity" not in out
    assert "color: red" in out
    assert n >= 1


def test_removes_partial_opacity():
    out, _ = reveal_animation_states('<div style="opacity: 0.488;">x</div>')
    assert "opacity" not in out


def test_removes_display_none_important_reveals_heading():
    out, _ = reveal_animation_states('<h1 style="display: none !important;">EverSwap</h1>')
    assert "display: none" not in out
    assert "EverSwap" in out


def test_removes_blur_and_transform():
    out, _ = reveal_animation_states(
        '<div style="filter: blur(0.25em); transform: translate3d(-50%, -51%, 0);">x</div>')
    assert "blur" not in out
    assert "translate3d" not in out


def test_removes_visibility_hidden():
    out, _ = reveal_animation_states('<section style="visibility: hidden;">x</section>')
    assert "visibility: hidden" not in out


def test_keeps_benign_inline_styles_untouched():
    html = '<div style="display: flex; width: 1360px;">x</div>'
    out, n = reveal_animation_states(html)
    assert "display: flex" in out
    assert "width: 1360px" in out
    assert n == 0


def test_drops_empty_style_attribute_after_cleaning():
    out, _ = reveal_animation_states('<span style="opacity: 0;">hi</span>')
    assert "style=" not in out
    assert ">hi<" in out


def test_no_style_attribute_is_noop():
    html = "<div class='a'>plain</div>"
    out, n = reveal_animation_states(html)
    assert out == html
    assert n == 0
