"""Route-(c) phase 2 — deterministic HTML → readable JSX.

Turns a section's cleaned+localized real HTML (currently shipped as a
``dangerouslySetInnerHTML`` blob — fails R2 "clean, readable, editable code")
into real JSX elements a developer can open and edit, WITHOUT changing what
renders (the theme CSS still styles the real class names → fidelity preserved)."""
import re

from core.codegen.html_to_jsx import html_to_jsx, render_section_component


def test_class_and_for_become_classname_htmlfor():
    out = html_to_jsx('<label class="lbl" for="x">Hi</label>')
    assert 'className="lbl"' in out
    assert 'htmlFor="x"' in out
    assert "class=" not in out


def test_void_elements_self_close():
    out = html_to_jsx('<img src="/a.png" alt="x">')
    assert "<img" in out and out.rstrip().endswith("/>")
    assert "</img>" not in out


def test_inline_style_becomes_object_with_camelcase():
    out = html_to_jsx('<div style="background-color: red; font-size: 12px">x</div>')
    assert "style={{" in out
    assert "backgroundColor" in out and "fontSize" in out
    assert "'red'" in out or '"red"' in out


def test_hyphenated_svg_attrs_camelcased_but_data_aria_preserved():
    out = html_to_jsx('<svg><path stroke-width="2" fill-rule="evenodd" data-x="1" aria-hidden="true"/></svg>')
    assert "strokeWidth" in out and "fillRule" in out
    assert 'data-x="1"' in out          # data-* kept verbatim
    assert 'aria-hidden="true"' in out  # aria-* kept verbatim


def test_comments_and_script_style_dropped():
    out = html_to_jsx('<div><!-- c --><script>bad()</script><style>.a{}</style><p>ok</p></div>')
    assert "bad()" not in out and ".a{}" not in out and "<!--" not in out
    assert "<p>" in out and "ok" in out


def test_text_braces_escaped():
    out = html_to_jsx("<p>use {curly} braces</p>")
    assert "{curly}" not in out          # raw braces would be a JSX expression
    assert "curly" in out


def test_nested_structure_preserved_and_not_a_blob():
    html = '<section class="S"><div class="a"><span>hi</span></div></section>'
    out = html_to_jsx(html)
    assert "dangerouslySetInnerHTML" not in out
    assert out.index("<section") < out.index("<div") < out.index("<span")


def test_render_section_component_is_clean_jsx_no_blob():
    comp = render_section_component("HeroSection", '<section class="Hero"><h1>Hi</h1></section>')
    assert "export default function HeroSection()" in comp
    assert "dangerouslySetInnerHTML" not in comp
    assert "__html" not in comp
    assert 'className="Hero"' in comp
    # multiple-safe: wraps children so a multi-root section still compiles
    multi = render_section_component("X", "<div>a</div><div>b</div>")
    assert "<>" in multi or "<React.Fragment" in multi or "<div" in multi
