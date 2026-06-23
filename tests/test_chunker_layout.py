"""Tests that chunk_page keeps grid/flex layout containers atomic when hinted."""

from core.section_chunker import chunk_page, MAX_SECTION_TOKENS


def _big_text(tokens):
    # ~4 chars per token in the token estimator
    return "x " * (tokens * 2)


def _build_page():
    """A page whose single top-level grid container is too big for one section,
    with two large children that would otherwise be split apart."""
    half = MAX_SECTION_TOKENS  # each column on its own exceeds half the budget
    media = f'<div class="media">{_big_text(half)}</div>'
    info = f'<div class="info">{_big_text(half)}</div>'
    grid = f'<div class="product grid two-col">{media}{info}</div>'
    return f"<html><body>{grid}</body></html>"


def test_grid_container_kept_as_one_section_with_hint():
    html = _build_page()
    sections = chunk_page(html, layout_containers={".product.grid.two-col"})

    # The grid container must survive as a single section containing BOTH columns.
    grid_sections = [s for s in sections if "media" in s["full_html"] and "info" in s["full_html"]]
    assert len(grid_sections) == 1, (
        f"expected the grid to stay as ONE section, got sections="
        f"{[(s['name'], 'media' in s['full_html'], 'info' in s['full_html']) for s in sections]}"
    )
    # And no section should contain only one of the two columns (i.e. it wasn't split).
    for s in sections:
        has_media = "media" in s["full_html"]
        has_info = "info" in s["full_html"]
        assert not (has_media ^ has_info), "grid children were split across sections"


def test_grid_container_split_without_hint_preserves_old_behavior():
    html = _build_page()
    sections = chunk_page(html)  # no hint -> unchanged behavior

    # Old behavior: the oversized grid is descended into and the two big
    # children land in separate sections.
    media_only = [s for s in sections if "media" in s["full_html"] and "info" not in s["full_html"]]
    info_only = [s for s in sections if "info" in s["full_html"] and "media" not in s["full_html"]]
    assert media_only and info_only, (
        "without a hint the big grid should still be split into separate sections"
    )


def test_layout_containers_none_is_default():
    # Passing None explicitly behaves identically to omitting it.
    html = _build_page()
    assert chunk_page(html, layout_containers=None) == chunk_page(html)
