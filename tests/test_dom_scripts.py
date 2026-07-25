"""Browser-side DOM extraction regressions."""

import os

import pytest

from core.extractor.dom_scripts import (
    DISMISS_OVERLAYS_JS,
    DOM_TREE_JS,
    REST_STATE_BAKE_JS,
)


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE") != "1", reason="chromium DOM extraction; set RUN_LIVE=1"
)


def test_zero_size_wrapper_keeps_visible_descendants():
    """A display:contents/custom wrapper must not erase its visible header."""
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 600})
        page.set_content(
            """
            <style>
              sticky-group-manager { display: contents; }
              header { display:block; width:800px; height:96px; background:red; }
            </style>
            <sticky-group-manager>
              <header id="site-header"><h1>Visible brand</h1></header>
            </sticky-group-manager>
            <main style="height:900px">Body</main>
            """
        )

        tree = page.evaluate(DOM_TREE_JS, {"maxDepth": 20, "includeHidden": False})
        browser.close()

    def ids(node):
        found = [node.get("id")]
        for child in node.get("children") or []:
            found.extend(ids(child))
        return found

    assert "site-header" in ids(tree)


def test_rest_state_bake_keeps_tall_sticky_content_column():
    """A tall sticky product column is page content, not a viewport overlay."""
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_content(
            """
            <main style="display:grid;grid-template-columns:1fr 1fr;gap:40px">
              <div style="height:2200px">Product gallery</div>
              <aside id="product-info"
                     style="display:flex;flex-direction:column;position:sticky;
                            top:96px;height:1700px;z-index:auto">
                Product title, price, options and details
              </aside>
            </main>
            """
        )

        page.evaluate(REST_STATE_BAKE_JS)
        display = page.locator("#product-info").evaluate(
            "element => getComputedStyle(element).display"
        )
        browser.close()

    assert display == "flex"


def test_overlay_dismissal_never_submits_a_search_form():
    """A close-looking submit button must not navigate to the search page."""
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 600})
        page.set_content(
            """
            <form id="search" action="/search">
              <button aria-label="Close search" style="width:32px;height:32px">
                ×
              </button>
            </form>
            <script>
              window.submitCount = 0;
              document.querySelector('#search').addEventListener('submit', event => {
                window.submitCount += 1;
                event.preventDefault();
              });
            </script>
            """
        )

        page.evaluate(DISMISS_OVERLAYS_JS)
        submit_count = page.evaluate("window.submitCount")
        browser.close()

    assert submit_count == 0
