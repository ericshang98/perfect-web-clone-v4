"""Tests for core.css_matcher — per-section critical-CSS extraction.

The matcher turns the page-wide ``css.json`` (every stylesheet, animation,
variable) into the *subset* of CSS that actually applies to one section's HTML,
so the section's sub-agent can faithfully reproduce hover/animation/responsive
behavior instead of guessing. Pure, deterministic, no LLM.
"""

from core import css_matcher


# --------------------------------------------------------------------------- #
# build_index — parse stylesheets into addressable rules
# --------------------------------------------------------------------------- #

def test_build_index_parses_a_simple_rule():
    css_json = {"stylesheets": [{"url": "inline-0", "content": ".btn { color: red; }"}]}
    idx = css_matcher.build_index(css_json)
    assert len(idx.rules) == 1
    assert idx.rules[0].selectors == [".btn"]
    assert "color: red" in idx.rules[0].body
    assert idx.rules[0].media is None


def test_build_index_splits_a_selector_list():
    css_json = {"stylesheets": [{"url": "i", "content": ".a, .b ,.c { margin: 0 }"}]}
    idx = css_matcher.build_index(css_json)
    assert idx.rules[0].selectors == [".a", ".b", ".c"]


def test_build_index_strips_comments():
    css_json = {"stylesheets": [{"url": "i", "content": "/* hi */ .a { color: red } /* bye */"}]}
    idx = css_matcher.build_index(css_json)
    assert len(idx.rules) == 1
    assert idx.rules[0].selectors == [".a"]


def test_build_index_captures_media_block_rules_with_their_condition():
    content = "@media (max-width: 600px) { .a { color: green } }"
    idx = css_matcher.build_index({"stylesheets": [{"url": "i", "content": content}]})
    media_rules = [r for r in idx.rules if r.media]
    assert len(media_rules) == 1
    assert ".a" in media_rules[0].selectors
    assert "max-width" in media_rules[0].media


def test_build_index_captures_keyframes_by_name():
    content = "@keyframes spin { from { transform: rotate(0) } to { transform: rotate(360deg) } }"
    idx = css_matcher.build_index({"stylesheets": [{"url": "i", "content": content}]})
    assert "spin" in idx.keyframes
    assert "rotate(360deg)" in idx.keyframes["spin"]


def test_build_index_keeps_source_order():
    content = ".a { color: red } .b { color: blue }"
    idx = css_matcher.build_index({"stylesheets": [{"url": "i", "content": content}]})
    assert idx.rules[0].order < idx.rules[1].order


# --------------------------------------------------------------------------- #
# match_section_css — the subset that applies to one section
# --------------------------------------------------------------------------- #

def _idx(content, **extra):
    return css_matcher.build_index({"stylesheets": [{"url": "i", "content": content}], **extra})


def test_match_includes_rule_whose_class_is_in_the_section():
    idx = _idx(".btn { color: red } .other { color: blue }")
    css = css_matcher.match_section_css('<div class="btn">x</div>', idx)
    assert ".btn" in css
    assert ".other" not in css


def test_match_includes_hover_variant_of_a_present_element():
    idx = _idx(".btn:hover { text-decoration: underline }")
    css = css_matcher.match_section_css('<a class="btn">x</a>', idx)
    assert ":hover" in css
    assert "underline" in css


def test_match_includes_keyframes_referenced_by_a_matched_rule():
    idx = _idx(".spin { animation: rot 2s linear infinite } @keyframes rot { to { transform: rotate(360deg) } }")
    css = css_matcher.match_section_css('<div class="spin">x</div>', idx)
    assert "@keyframes rot" in css
    assert "rotate(360deg)" in css


def test_match_omits_keyframes_not_referenced():
    idx = _idx(".x { color: red } @keyframes unused { to { opacity: 0 } }")
    css = css_matcher.match_section_css('<div class="x">y</div>', idx)
    assert "unused" not in css


def test_match_includes_media_rule_for_a_present_element():
    idx = _idx("@media (max-width: 600px) { .card { padding: 4px } }")
    css = css_matcher.match_section_css('<div class="card">y</div>', idx)
    assert "@media" in css
    assert "max-width: 600px" in css
    assert "padding: 4px" in css


def test_match_includes_css_variables_used_by_matched_rules():
    idx = _idx(
        ".btn { color: var(--brand) }",
        variables=[{"name": "--brand", "value": "#ff0066", "scope": ":root"}],
    )
    css = css_matcher.match_section_css('<button class="btn">x</button>', idx)
    assert "--brand" in css
    assert "#ff0066" in css
    assert ":root" in css


def test_match_resolves_transitive_variables():
    idx = _idx(
        ".btn { color: var(--text) }",
        variables=[
            {"name": "--text", "value": "var(--brand)", "scope": ":root"},
            {"name": "--brand", "value": "#abc", "scope": ":root"},
        ],
    )
    css = css_matcher.match_section_css('<button class="btn">x</button>', idx)
    assert "--text" in css
    assert "--brand" in css


def test_match_matches_by_tag_and_id_too():
    idx = _idx("h1 { font-size: 40px } #hero { background: black }")
    css = css_matcher.match_section_css('<section id="hero"><h1>Hi</h1></section>', idx)
    assert "font-size: 40px" in css
    assert "#hero" in css


def test_match_returns_empty_for_no_matches():
    idx = _idx(".nope { color: red }")
    css = css_matcher.match_section_css('<div class="totally-different">x</div>', idx)
    assert css.strip() == ""


def test_match_respects_a_char_budget():
    big = " ".join(f".c{i} {{ color: red }}" for i in range(500))
    html = "".join(f'<div class="c{i}"></div>' for i in range(500))
    idx = _idx(big)
    css = css_matcher.match_section_css(html, idx, max_chars=200)
    assert len(css) <= 200


def test_match_is_deterministic():
    idx = _idx(".a { color: red } .b:hover { color: blue }")
    html = '<div class="a"><span class="b">x</span></div>'
    assert css_matcher.match_section_css(html, idx) == css_matcher.match_section_css(html, idx)


# --------------------------------------------------------------------------- #
# attach_css_rules — wire the matcher onto a list of chunker sections
# --------------------------------------------------------------------------- #

def test_attach_sets_css_rules_per_section_from_its_own_html():
    css_json = {"stylesheets": [{"url": "i", "content": ".hero { color: red } .foot { color: blue }"}]}
    sections = [
        {"name": "hero", "full_html": '<div class="hero">x</div>'},
        {"name": "footer", "full_html": '<div class="foot">y</div>'},
    ]
    css_matcher.attach_css_rules(sections, css_json)
    assert ".hero" in sections[0]["css_rules"]
    assert ".foot" not in sections[0]["css_rules"]
    assert ".foot" in sections[1]["css_rules"]
    assert ".hero" not in sections[1]["css_rules"]


def test_attach_builds_the_index_once_and_is_safe_with_no_css():
    sections = [{"name": "a", "full_html": '<div class="a">x</div>'}]
    css_matcher.attach_css_rules(sections, {})
    assert sections[0]["css_rules"] == ""
