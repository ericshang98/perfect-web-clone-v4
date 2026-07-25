# Structural Integrity and Common Interactions Implementation Plan

> Execute inline with test-driven development. Preserve unrelated dirty-worktree changes.

**Goal:** Prevent incomplete source captures from entering the clone pipeline, make critical-region omissions hard failures, and require common interactions to work.

**Architecture:** Add a pure integrity model around immutable pre-mutation and normalized post-mutation structure inventories. Gate extraction, planning, and verification on it. Extend manifests with conservative interaction contracts and replay them before visual scoring.

**Tech stack:** Python 3, pytest, Playwright async API, JSON manifests, existing MCP tool layer.

---

## Task 1: Pure capture-integrity gate

**Files:**
- Create: `core/capture_integrity.py`
- Create: `tests/test_capture_integrity.py`

1. Add failing tests for missing ReelShort Hero, material page-height loss, and valid stable capture.
2. Run the focused tests and confirm the missing API failure.
3. Implement immutable region/report models and the pre/post comparison.
4. Run focused tests.

## Task 2: Browser structure and interaction inventories

**Files:**
- Modify: `core/extractor/dom_scripts.py`
- Modify: `tests/test_dom_scripts.py`

1. Add failing script-contract tests for structure fields and common controls.
2. Add pre/post structure inventory JavaScript and conservative interaction discovery.
3. Harden rest-state stabilization so opacity-zero carousel children cannot collapse structural ancestors.
4. Run focused tests.

## Task 3: Extraction retries and persisted evidence

**Files:**
- Modify: `core/extractor/models.py`
- Modify: `core/extractor/service.py`
- Modify: `core/extractor/api.py`
- Modify: `core/extractor/storage.py`
- Modify: `tests/test_extractor_robustness.py`
- Modify: `tests/test_capture_completeness_acceptance.py`

1. Add failing tests for pass-on-third-attempt and hard-fail-after-three.
2. Extend extraction results with integrity evidence.
3. Save immutable raw evidence before stabilization and normalized evidence after it.
4. Compare evidence, retry up to three times, and preserve failed-attempt reports.
5. Run focused tests.

## Task 4: Fail-closed planning

**Files:**
- Modify: `mcp_server/tools/extraction.py`
- Modify: `tests/mcp/test_extraction_planning.py`

1. Add failing tests that failed/unknown integrity blocks section planning.
2. Add integrity precondition and explicit error payload.
3. Run focused tests.

## Task 5: Structure and interaction hard gates

**Files:**
- Create: `core/gates/structure.py`
- Create: `core/gates/interaction.py`
- Modify: `core/manifest.py`
- Modify: `core/gates/manifest_gate.py`
- Modify: `mcp_server/tools/verify.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/gates/test_manifest_gate.py`
- Modify: `tests/mcp/test_manifest_tools.py`
- Modify: `tests/mcp/test_score_clone_sections.py`

1. Add failing tests proving a missing Hero cannot pass through high SSIM.
2. Add failing tests for carousel/menu/tab/accordion contracts and required replay failure.
3. Extend manifest schema and verification output.
4. Enforce hard-gate ordering before visual score.
5. Run focused tests.

## Task 6: Documentation and contract wording

**Files:**
- Modify: `skill/SKILL.md`
- Modify: `README.md`
- Modify: `docs/delivery-strategy.md` if present

1. Replace “reference raster is ground truth” with validated dual-evidence rules.
2. Document common-interaction scope B.
3. Replace automatic acceptance language with `ready_for_user_review`.

## Task 7: Regression and live ReelShort proof

1. Run focused suites for extraction, planning, manifests, and gates.
2. Run the full test suite.
3. Recapture ReelShort and verify integrity report includes the Hero.
4. Rebuild missing Hero and common controls in the ReelShort clone.
5. Capture clone proof images and run hard gates.
6. Start or refresh localhost preview and hand it to the user for review.
