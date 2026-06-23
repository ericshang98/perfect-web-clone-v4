"""Tests for core.output_sanitizer — guarantee a clean, standalone deliverable.

The clone must carry NO trace of the source site: no absolute source-domain
URLs, no CMS/Shopify artifacts (data-shopify*, checkout tokens, *.myshopify.com),
no dependency on the origin. This turns section HTML into clean, self-contained
markup before the React rebuild, and provides a gate to verify nothing leaked.
Pure, deterministic, no LLM.
"""

from core import output_sanitizer as san


SRC = "https://livora.co/products/silkglide-pro-2-0"


# --- sanitize_html ---

def test_relativizes_absolute_source_domain_links():
    html = '<a href="https://livora.co/cart">Cart</a>'
    out = san.sanitize_html(html, SRC)
    assert 'href="/cart"' in out
    assert "livora.co" not in out


def test_relativizes_protocol_relative_source_links():
    html = '<a href="//livora.co/collections/all">All</a>'
    out = san.sanitize_html(html, SRC)
    assert 'href="/collections/all"' in out
    assert "livora.co" not in out


def test_strips_data_shopify_attributes():
    html = '<div data-shopify="abc" data-shopify-editor-block="x" class="k">hi</div>'
    out = san.sanitize_html(html, SRC)
    assert "data-shopify" not in out
    assert 'class="k"' in out  # unrelated attrs preserved
    assert ">hi<" in out


def test_removes_internal_myshopify_domain_references():
    html = '<link href="https://37fa13-2.myshopify.com/x"><span>37fa13-2.myshopify.com</span>'
    out = san.sanitize_html(html, SRC)
    assert "myshopify.com" not in out


def test_keeps_already_relative_links_and_local_assets():
    html = '<a href="/policies/refund-policy">R</a><img src="/assets/images/foo.png">'
    out = san.sanitize_html(html, SRC)
    assert 'href="/policies/refund-policy"' in out
    assert 'src="/assets/images/foo.png"' in out


def test_leaves_unrelated_external_domains_alone():
    # A genuine third-party link that isn't the source is not a "trace" to strip.
    html = '<a href="https://example.com/page">x</a>'
    out = san.sanitize_html(html, SRC)
    assert "https://example.com/page" in out


# --- find_source_traces / verify_clean ---

def test_find_source_traces_reports_remaining_references():
    text = 'foo https://livora.co/x bar data-shopify="y" baz 37fa13-2.myshopify.com'
    traces = san.find_source_traces(text, SRC)
    assert any("livora.co" in t for t in traces)
    assert any("myshopify" in t for t in traces)
    assert any("data-shopify" in t for t in traces)


def test_verify_clean_passes_on_sanitized_output():
    html = '<a href="https://livora.co/cart" data-shopify="z">C</a>'
    clean = san.sanitize_html(html, SRC)
    assert san.verify_clean(clean, SRC)["ok"] is True


def test_verify_clean_flags_dirty_output():
    r = san.verify_clean('<a href="https://livora.co/cart">C</a>', SRC)
    assert r["ok"] is False
    assert r["traces"]
