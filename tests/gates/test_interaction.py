from core.gates.interaction import observable_changed


def test_carousel_requires_visible_content_or_selection_change():
    before = {
        "target": {"ariaSelected": None},
        "scope": {"text": "Slide one", "media": "one.jpg", "selected": "1"},
    }
    after = {
        "target": {"ariaSelected": None},
        "scope": {"text": "Slide two", "media": "two.jpg", "selected": "2"},
    }
    same = {
        "target": {"ariaSelected": None},
        "scope": {"text": "Slide one", "media": "one.jpg", "selected": "1"},
    }

    assert (
        observable_changed(
            "selected_slide_or_visible_content_changes", before, after
        )
        is True
    )
    assert (
        observable_changed(
            "selected_slide_or_visible_content_changes", before, same
        )
        is False
    )


def test_menu_and_accordion_require_expansion_and_panel_visibility_change():
    before = {
        "target": {"ariaExpanded": "false"},
        "controlled": {"visible": False},
    }
    after = {
        "target": {"ariaExpanded": "true"},
        "controlled": {"visible": True},
    }

    assert observable_changed(
        "aria_expanded_and_menu_visibility_toggle", before, after
    )
    assert observable_changed(
        "aria_expanded_and_panel_visibility_toggle", before, after
    )
    assert not observable_changed(
        "aria_expanded_and_panel_visibility_toggle", before, before
    )


def test_details_and_tab_observables_are_fail_closed():
    assert observable_changed(
        "details_open_toggles",
        {"detailsOpen": False},
        {"detailsOpen": True},
    )
    assert observable_changed(
        "aria_selected_and_panel_change",
        {
            "target": {"ariaSelected": "false"},
            "controlled": {"visible": False},
        },
        {
            "target": {"ariaSelected": "true"},
            "controlled": {"visible": True},
        },
    )
    assert not observable_changed("unknown_observable", {}, {})


def test_anonymous_menu_requires_visible_surface_set_to_change():
    before = {"globalSurfaces": []}
    after = {
        "globalSurfaces": [
            "aside:Descargar Desbloquea episodios gratis solo en la app"
        ]
    }

    assert observable_changed(
        "menu_or_overlay_visibility_toggle", before, after
    )
    assert not observable_changed(
        "menu_or_overlay_visibility_toggle", before, before
    )
