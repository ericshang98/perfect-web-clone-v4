"""Emit-fidelity: chunk full_html must keep REAL svg/style/srcset (not the
token-budget placeholders), while token *estimation* may still collapse them."""

from core import section_chunker as sc


def test_token_estimator_still_collapses_svg():
    # The estimator stays lossy on purpose (keeps split budgets stable).
    html = '<svg viewBox="0 0 10 10"><path d="M0 0L10 10"/></svg>'
    assert "[SVG]" in sc.clean_html_for_tokens(html)


def test_emitted_full_html_keeps_real_svg():
    page = (
        '<section class="hero"><h2>Hi</h2>'
        '<svg viewBox="0 0 24 24"><path d="M1 2 L3 4" stroke-width="2"/></svg>'
        "</section>"
        '<section class="cta"><h2>Buy</h2><p>x</p></section>'
    )
    secs = sc.chunk_page(page, "https://e.com")
    blob = "".join(s["full_html"] for s in secs)
    assert "[SVG]" not in blob, "real svg must survive into full_html"
    assert "<path" in blob and 'd="M1 2 L3 4"' in blob
    assert "stroke-width" in blob


def test_emitted_full_html_keeps_long_inline_style():
    long_style = "background:" + "#abcdef;" * 40  # >200 chars
    page = (
        f'<section class="a"><div style="{long_style}">x</div><h2>A</h2></section>'
        '<section class="b"><h2>B</h2><p>y</p></section>'
    )
    secs = sc.chunk_page(page, "https://e.com")
    blob = "".join(s["full_html"] for s in secs)
    assert "[LONG_STYLES]" not in blob
    assert "#abcdef" in blob


def test_large_real_section_is_not_truncated_below_real_length():
    # A single dense section bigger than the old 48k cap must not be cut.
    big = '<section class="x">' + ("<p>lorem ipsum dolor sit amet </p>" * 2500) + "</section>"
    assert len(big) > 60000
    secs = sc.chunk_page(big, "https://e.com")
    joined = "".join(s["full_html"] for s in secs)
    # nothing dropped: the closing marker survives somewhere
    assert joined.count("<p>lorem") > 2000
