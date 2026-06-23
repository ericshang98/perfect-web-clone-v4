"""Tests for core.link_verifier — the deterministic real-link gate.

A section sub-agent must reproduce the section's REAL hrefs (from the extracted
``links``), not fabricate ``#`` / ``javascript:`` placeholders. This verifier
reads a generated component and reports whether every real link survived, so the
orchestrator can re-dispatch any section that dropped them. Pure, no LLM.
"""

from core import link_verifier


# --------------------------------------------------------------------------- #
# extract_hrefs — pull link targets out of generated JSX
# --------------------------------------------------------------------------- #

def test_extract_hrefs_double_quoted():
    assert "/shop" in link_verifier.extract_hrefs('<a href="/shop">Shop</a>')


def test_extract_hrefs_brace_string():
    assert "/cart" in link_verifier.extract_hrefs('<a href={"/cart"}>Cart</a>')


def test_extract_to_attribute_for_react_router_link():
    assert "/about" in link_verifier.extract_hrefs('<Link to="/about">About</Link>')


def test_extract_hrefs_full_url():
    hrefs = link_verifier.extract_hrefs('<a href="https://x.com/p">P</a>')
    assert "https://x.com/p" in hrefs


# --------------------------------------------------------------------------- #
# verify_section — did the real links survive?
# --------------------------------------------------------------------------- #

def test_passes_when_all_real_links_present():
    expected = [{"url": "https://x.com/shop"}, {"url": "https://x.com/cart"}]
    src = '<a href="/shop">Shop</a><a href="https://x.com/cart">Cart</a>'
    r = link_verifier.verify_section(expected, src)
    assert r["ok"]
    assert r["missing"] == []
    assert r["preserved_count"] == 2


def test_fails_when_a_real_link_is_missing():
    expected = [{"url": "https://x.com/shop"}, {"url": "https://x.com/cart"}]
    src = '<a href="/shop">Shop</a><a href="#">Cart</a>'
    r = link_verifier.verify_section(expected, src)
    assert not r["ok"]
    assert any("cart" in m for m in r["missing"])


def test_matches_real_link_by_path_when_component_uses_relative():
    expected = [{"url": "https://livora.co/policies/refund-policy"}]
    src = '<a href="/policies/refund-policy">Refund</a>'
    assert link_verifier.verify_section(expected, src)["ok"]


def test_matches_ignoring_trailing_slash():
    expected = [{"url": "https://x.com/contact/"}]
    src = '<a href="/contact">Contact</a>'
    assert link_verifier.verify_section(expected, src)["ok"]


def test_reports_placeholder_hrefs():
    expected = [{"url": "https://x.com/cart"}]
    src = '<a href="#">x</a><a href="javascript:void(0)">y</a>'
    r = link_verifier.verify_section(expected, src)
    assert r["placeholder_count"] >= 2


def test_trivially_ok_with_no_expected_links():
    r = link_verifier.verify_section([], "<div>nothing</div>")
    assert r["ok"]
    assert r["missing"] == []


def test_skips_same_page_self_and_anchor_links():
    # A link to the current page (incl. #MainContent in-page jumps) is not real
    # navigation; its absence must not fail the gate. The homepage "/" link from
    # a product page IS real and must still be required.
    expected = [
        {"url": "https://x.com/p#MainContent"},  # self/in-page → skip
        {"url": "https://x.com/p"},               # self → skip
        {"url": "https://x.com/real"},            # required
    ]
    src = '<a href="/real">Real</a>'
    r = link_verifier.verify_section(expected, src, page_url="https://x.com/p")
    assert r["ok"]


def test_homepage_link_from_a_subpage_is_still_required():
    expected = [{"url": "https://x.com/"}]
    src = "<div>no links</div>"
    r = link_verifier.verify_section(expected, src, page_url="https://x.com/products/foo")
    assert not r["ok"]


# --------------------------------------------------------------------------- #
# verify_sections — aggregate across a whole clone for the orchestrator gate
# --------------------------------------------------------------------------- #

def test_verify_sections_aggregates_pass_and_fail():
    sections = [
        {"name": "nav", "component_path": "a.jsx", "links": [{"url": "https://x.com/shop"}]},
        {"name": "foot", "component_path": "b.jsx", "links": [{"url": "https://x.com/terms"}]},
    ]
    sources = {"nav": '<a href="/shop">S</a>', "foot": '<a href="#">T</a>'}
    r = link_verifier.verify_sections(sections, sources, page_url="https://x.com/p")
    assert not r["ok"]
    assert "nav" in r["passed"]
    assert [f["name"] for f in r["failing"]] == ["foot"]


def test_verify_sections_ok_when_all_pass():
    sections = [{"name": "nav", "component_path": "a.jsx", "links": [{"url": "https://x.com/shop"}]}]
    sources = {"nav": '<a href="/shop">S</a>'}
    r = link_verifier.verify_sections(sections, sources)
    assert r["ok"]
    assert r["passed"] == ["nav"]
    assert r["failing"] == []


def test_verify_sections_flags_unreadable_component_with_links():
    sections = [{"name": "nav", "component_path": "a.jsx", "links": [{"url": "https://x.com/shop"}]}]
    r = link_verifier.verify_sections(sections, {"nav": None})
    assert not r["ok"]
    assert r["unreadable"][0]["name"] == "nav"


def test_verify_sections_ignores_unreadable_component_without_links():
    sections = [{"name": "deco", "component_path": "a.jsx", "links": []}]
    r = link_verifier.verify_sections(sections, {"deco": None})
    assert r["ok"]
    assert r["unreadable"] == []
