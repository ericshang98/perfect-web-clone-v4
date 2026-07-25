# Four Reference Sites Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task-by-task,
> with spec review followed by code-quality review for each code-changing task.

**Goal:** Reach the client’s second milestone with reproducible evidence: all
four contracted reference URLs produce standalone clones that build and pass
the project’s cleanliness, weight, link, and visual-fidelity gates.

**Architecture:** Fix shared capture/planning defects once in the deterministic
Python pipeline, then run the same extract → plan → assemble → section conversion
→ gate loop for each site. Preserve every reference raster and gate result under
the corresponding product directory so the result can be reviewed without
trusting a prose status update.

**Tech Stack:** Python 3.12, pytest, Playwright, BeautifulSoup, Vite, React,
Tailwind CSS, PIL/scikit-image SSIM, pwc4 MCP tools.

**Contracted references:**

1. `https://www.reelshort.com/es`
2. `https://livora.co/products/painless-hair-removal-epilator-usb-rechargeable-trimmer-women-body-razor-face-leg-armpit-bikini-hand-pubic-shaver-hair-remover`
3. `https://kojeva.com/products/kojeva-lymphatic-face-brush`
4. `https://trykojiva.com/brush`

**Milestone gate:** For each site, the fresh clone must build; contain zero
source-platform fingerprints; stay within the configured code budget; contain
no fabricated or broken links; and meet the project’s recorded visual threshold
at the captured viewport. Any exception must be an explicit residual, never a
silent pass.

---

## Task 1: Make visible-state capture and section planning trustworthy

**Files:**
- Modify: `core/extractor/dom_scripts.py`
- Modify: `core/extractor/service.py`
- Modify: `core/extractor/theme.py`
- Modify: `core/section_chunker.py`
- Modify: `core/section_geometry.py`
- Modify: `mcp_server/tools/extraction.py`
- Test: `tests/test_dom_scripts.py`
- Test: `tests/test_rest_state_alignment.py`
- Test: `tests/test_theme.py`
- Test: `tests/test_chunker_layout.py`
- Test: `tests/test_section_geometry.py`
- Test: `tests/mcp/test_extraction_planning.py`

- [x] Add a failing regression showing that a zero-size/custom wrapper must not
  cause visible descendants (for example a sticky header) to disappear from
  `dom.json`.
- [x] Add a failing regression showing that a Shopify cart drawer baked with
  `display:none !important` remains hidden during section planning.
- [x] Add a failing regression showing that an actual scroll-choreography page
  still has frozen reveal styles normalized.
- [x] Implement the smallest changes that make those regressions pass. Apply
  reveal normalization only when the deterministic site classification calls
  for it; preserve deliberate hidden UI states.
- [x] Add a real-shape regression proving that nonvisual drawer/style/script
  fragments are not emitted as visible page sections and that render order
  follows page geometry/source order.
- [x] Run:
  `.venv/bin/python -m pytest tests/test_dom_scripts.py tests/test_anim_normalize.py tests/mcp/test_extraction_planning.py -v`
- [x] Run:
  `.venv/bin/python -m pytest -q`

## Task 2: Establish one validated capture per contracted URL

**Files:**
- Create/update: `delivery/four-reference-sites.json`
- Create/update: `delivery/four-reference-sites.md`
- Generated evidence: `core/extractor/_sources/<source-id>/`

- [x] Extract each URL at the standard desktop viewport with full-page and
  scroll-state screenshots enabled.
- [x] Validate URL, title, page height, visible heading/product text, asset
  counts, screenshot dimensions, and section bounds before accepting a capture.
- [x] Reject search pages, access-denied pages, consent overlays, blank SPA
  shells, or captures whose product identity does not match the requested URL.
- [x] Record the accepted `source_id`, capture timestamp, classification,
  dimensions, asset counts, and residuals in the JSON ledger.
- [x] Generate and persist a section plan for every accepted source.

## Task 3: Build the ReelShort clone

**Files:**
- Create/update: `showcase/products/reelshort/`
- Generated evidence: `showcase/products/reelshort/shots/`

- [x] Assemble the deterministic Vite/React shell from the accepted source.
- [x] Convert each planned section using only its own extracted HTML, CSS,
  assets, text, and links. Keep source order and captured geometry.
- [x] Build and capture the clone at the reference viewport and scroll states.
- [x] Run all gates from Task 7 and repair the worst failing section until the
  recorded threshold passes or an explicit platform residual is documented.

## Task 4: Build the Livora clone

**Files:**
- Create/update: `showcase/products/livora/`
- Generated evidence: `showcase/products/livora/shots/`

- [x] Repeat Task 3 using the accepted Livora product capture.
- [x] Specifically verify the two-column product area, carousel rest state,
  long review/widget area, FAQ, and footer; a closed cart drawer must not appear.

## Task 5: Build the Kojeva clone

**Files:**
- Create/update: `showcase/products/kojeva/`
- Generated evidence: `showcase/products/kojeva/shots/`

- [x] Repeat Task 3 using a capture whose title and primary heading identify the
  lymphatic face brush product, not the site search page.
- [x] Preserve product imagery, offer blocks, social proof, FAQ, and footer.

## Task 6: Finish the TryKojiva clone

**Files:**
- Modify: `showcase/products/trykojiva/`
- Generated evidence: `showcase/products/trykojiva/shots/`

- [x] Replace generated raw HTML with a maintainable, data-driven React/CSS
  implementation while preserving the accepted content and links.
- [x] Prioritize cumulative vertical geometry, review grid, FAQ, and footer,
  and record the below-threshold logical-section aggregate as a residual.
- [x] Rebuild and rerun all gates from Task 7.

## Task 7: Produce machine-checkable acceptance evidence

**Files:**
- Create/update: `delivery/four-reference-sites.json`
- Create/update: `delivery/four-reference-sites.md`
- Create/update: `showcase/products/<site>/shots/sidebyside.png`

- [x] For each site run `build_project`.
- [x] For each site run `check_fingerprints`; expected result: zero findings.
- [x] For each site run `check_weight` with the project’s configured code budget.
- [x] For each site run `verify_links`; expected result: no fabricated/broken
  section links.
- [x] For each site run full-page and per-section fidelity scoring against the
  accepted capture; record scores, thresholds, and worst sections.
- [x] Save a labeled side-by-side image made from the exact images used by the
  gate, not from unrelated manual screenshots.
- [x] Update the delivery ledger only from fresh tool output.

## Task 8: Final regression, packaging, and handoff

**Files:**
- Modify: `README.md`
- Modify: `skill/SKILL.md` only if the verified workflow differs
- Create/update: `delivery/four-reference-sites.md`

- [x] Run `.venv/bin/python -m pytest -q` from the repository root.
- [x] Run a fresh production build in every product directory.
- [x] Confirm the delivery ledger points to existing source IDs, product paths,
  screenshots, and gate artifacts.
- [x] Review `git diff` and `git status`; preserve unrelated user files and keep
  generated bulk artifacts out of the commit unless they are required evidence.
- [x] Document exact install/run commands, known residuals, and the evidence
  paths the client can inspect.
- [x] Use `superpowers:verification-before-completion` before claiming the
  milestone complete.
