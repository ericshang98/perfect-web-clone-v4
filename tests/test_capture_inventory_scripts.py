import pytest

from core.extractor.dom_scripts import CAPTURE_INVENTORY_JS, REST_STATE_BAKE_JS


def _browser_page(html: str):
    playwright = pytest.importorskip("playwright.sync_api")
    manager = playwright.sync_playwright()
    runtime = manager.start()
    browser = runtime.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.set_content(html)
    return manager, runtime, browser, page


def test_inventory_marks_large_media_heading_control_region_as_critical_hero():
    manager, runtime, browser, page = _browser_page(
        """
        <body style="margin:0">
          <header style="height:80px">Brand</header>
          <main>
            <section id="featured-carousel" style="height:484px;width:1440px">
              <img src="hero.jpg" width="1440" height="484">
              <h1>Waterboy: Segunda oportunidad</h1>
              <button aria-label="Next slide">Next</button>
            </section>
            <section style="height:1200px"><h2>New releases</h2></section>
          </main>
        </body>
        """
    )
    try:
        inventory = page.evaluate(CAPTURE_INVENTORY_JS)
    finally:
        browser.close()
        runtime.stop()

    hero = next(
        region
        for region in inventory["regions"]
        if region["fingerprint"].startswith("id:featured-carousel")
    )
    assert hero["kind"] == "hero"
    assert hero["critical"] is True
    assert hero["signals"]["media"] is True
    assert hero["signals"]["controls"] >= 1


def test_inventory_discovers_carousel_menu_tabs_and_accordion_contracts():
    manager, runtime, browser, page = _browser_page(
        """
        <body>
          <section class="carousel">
            <button aria-label="Previous slide">Prev</button>
            <button aria-label="Next slide">Next</button>
          </section>
          <button id="menu-button" aria-controls="site-menu"
                  aria-expanded="false">Menu</button>
          <nav id="site-menu" hidden>Navigation</nav>
          <div role="tablist">
            <button role="tab" aria-controls="panel-one"
                    aria-selected="true">One</button>
            <button role="tab" aria-controls="panel-two"
                    aria-selected="false">Two</button>
          </div>
          <div id="panel-one" role="tabpanel">First</div>
          <div id="panel-two" role="tabpanel" hidden>Second</div>
          <details><summary>Shipping</summary><p>Tomorrow</p></details>
        </body>
        """
    )
    try:
        inventory = page.evaluate(CAPTURE_INVENTORY_JS)
    finally:
        browser.close()
        runtime.stop()

    kinds = {item["kind"] for item in inventory["interactions"]}
    assert {"carousel", "menu", "tab", "accordion"} <= kinds
    assert all(item["target"] for item in inventory["interactions"])
    assert all(item["expect"]["observable"] for item in inventory["interactions"])
    assert all(
        item["clone_target"]
        == f'[data-pwc-interaction="{item["id"]}"]'
        for item in inventory["interactions"]
    )


def test_inventory_discovers_clickable_div_carousel_pagination_dots():
    manager, runtime, browser, page = _browser_page(
        """
        <div id="root"><div><div><div><div><div><div>
          <section style="height:484px">
            <div class="pagination" style="display:flex;gap:8px">
              <div class="relative cursor-pointer" style="width:6px;height:6px"></div>
              <div class="relative cursor-pointer" style="width:6px;height:6px"></div>
              <div class="relative cursor-pointer" style="width:32px;height:6px"></div>
            </div>
            <img src="hero.jpg" width="1440" height="484">
          </section>
        </div></div></div></div></div></div></div>
        """
    )
    try:
        inventory = page.evaluate(CAPTURE_INVENTORY_JS)
        resolvable = [
            page.locator(item["target"]).count()
            for item in inventory["interactions"]
            if item["kind"] == "carousel"
        ]
    finally:
        browser.close()
        runtime.stop()

    dots = [
        item
        for item in inventory["interactions"]
        if item["kind"] == "carousel"
    ]
    # One non-active representative proves that the carousel can switch.
    # Requiring every pagination dot creates a guaranteed no-op contract for
    # whichever dot is selected at capture time.
    assert len(dots) == 1
    assert resolvable == [1]
    assert all(
        item["expect"]["observable"]
        == "selected_slide_or_visible_content_changes"
        for item in dots
    )


def test_inventory_promotes_unsemantic_carousel_band_from_pagination_group():
    manager, runtime, browser, page = _browser_page(
        """
        <body style="margin:0">
          <div id="__next">
            <div style="height:72px">Header</div>
            <div id="page-shell">
              <div id="featured-band"
                   style="position:relative;width:1440px;height:484px">
                <img src="hero.jpg" width="1440" height="484">
                <div style="position:absolute;bottom:20px;display:flex;gap:8px">
                  <div class="cursor-pointer" style="width:6px;height:6px"></div>
                  <div class="cursor-pointer" style="width:28px;height:6px"></div>
                  <div class="cursor-pointer" style="width:6px;height:6px"></div>
                </div>
              </div>
              <div style="height:1400px">Shelves</div>
            </div>
          </div>
        </body>
        """
    )
    try:
        inventory = page.evaluate(CAPTURE_INVENTORY_JS)
    finally:
        browser.close()
        runtime.stop()

    hero = next(
        region
        for region in inventory["regions"]
        if region["fingerprint"] == "id:featured-band"
    )
    assert hero["kind"] == "hero"
    assert hero["critical"] is True
    assert 480 <= hero["rect"]["height"] <= 488


def test_inventory_discovers_anonymous_nav_download_popover_control():
    manager, runtime, browser, page = _browser_page(
        """
        <body>
          <header>
            <nav>
              <div class="DownloadBtn_nav_item__hashed"
                   style="width:78px;height:46px">Descargar</div>
            </nav>
          </header>
        </body>
        """
    )
    try:
        inventory = page.evaluate(CAPTURE_INVENTORY_JS)
    finally:
        browser.close()
        runtime.stop()

    contract = next(
        item
        for item in inventory["interactions"]
        if item["kind"] == "menu"
    )
    assert contract["expect"]["observable"] == (
        "menu_or_overlay_visibility_toggle"
    )


def test_rest_state_bake_does_not_collapse_large_opacity_zero_carousel_region():
    manager, runtime, browser, page = _browser_page(
        """
        <body style="margin:0">
          <section id="hero" style="height:484px;opacity:0;position:relative">
            <img src="hero.jpg" width="1440" height="484">
          </section>
          <main style="height:1200px">Content</main>
        </body>
        """
    )
    try:
        before = page.evaluate("document.body.scrollHeight")
        page.evaluate(REST_STATE_BAKE_JS)
        after = page.evaluate("document.body.scrollHeight")
        display = page.locator("#hero").evaluate(
            "element => getComputedStyle(element).display"
        )
    finally:
        browser.close()
        runtime.stop()

    assert display != "none"
    assert after == before


def test_rest_state_bake_preserves_hidden_in_flow_carousel_height_spacer():
    manager, runtime, browser, page = _browser_page(
        """
        <body style="margin:0">
          <div id="carousel" style="position:relative">
            <div id="active" style="position:absolute;inset:0;height:484px">
              Active slide
            </div>
            <div id="height-spacer"
                 style="height:484px;visibility:hidden;opacity:0;position:static">
              <img src="hero.jpg" width="1440" height="484">
            </div>
          </div>
          <main style="height:1200px">Content</main>
        </body>
        """
    )
    try:
        before = page.evaluate("document.body.scrollHeight")
        page.evaluate(REST_STATE_BAKE_JS)
        after = page.evaluate("document.body.scrollHeight")
        display = page.locator("#height-spacer").evaluate(
            "element => getComputedStyle(element).display"
        )
    finally:
        browser.close()
        runtime.stop()

    assert display != "none"
    assert after == before
