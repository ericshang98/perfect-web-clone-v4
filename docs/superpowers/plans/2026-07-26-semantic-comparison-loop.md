# Semantic Comparison Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Agent-authored, token-bounded semantic comparison loop that measures stable website invariants strictly without treating naturally changing runtime content as a CSS failure.

**Architecture:** Persist an explicit comparison contract between capture/planning and visual verification. Deterministic Python gates evaluate each region according to its declared mode, emit a bounded worst-region repair packet, and keep a monotonic best-candidate ledger. The current Codex/Claude Agent remains the only reasoning layer and writes the contract from compact source evidence.

**Tech Stack:** Python 3.12, Pydantic v2, Pillow, NumPy, scikit-image SSIM, Playwright, FastMCP, pytest.

---

## File Map

- Create `core/comparison_contract.py`: schema, validation, persistence, and fail-closed rules.
- Create `core/volatility.py`: bounded semantic/temporal source evidence and volatile-candidate hints.
- Create `core/gates/semantic_fidelity.py`: contract-aware region scoring, 2D exclusion, and invariant checks.
- Create `core/repair_packet.py`: worst-region packet construction and text-budget enforcement.
- Create `core/iteration_ledger.py`: monotonic best-candidate and plateau bookkeeping.
- Modify `core/clone_capture.py`: collect critical/contract region geometry and stable presentation facts.
- Modify `mcp_server/tools/verify.py`: expose evidence, semantic scoring, and repair-packet tools.
- Modify `mcp_server/server.py`: register the new deterministic tools.
- Modify `skill/SKILL.md`: require semantic comparison before strict visual conclusions.
- Modify `skill/references/harness-contract.md`: record contract, token, and monotonic-iteration evidence.
- Create focused tests under `tests/` and `tests/mcp/`.

### Task 1: Comparison contract

**Files:**
- Create: `core/comparison_contract.py`
- Test: `tests/test_comparison_contract.py`

- [ ] **Step 1: Write failing schema and validation tests**

```python
from core.comparison_contract import validate_contract


def test_static_region_requires_bounds_and_owner():
    contract = {
        "schema": 1,
        "regions": [{
            "id": "hero",
            "owner": "hero",
            "importance": "critical",
            "mode": "static_pixels",
            "bounds": {"x": 0, "y": 80, "width": 1440, "height": 600},
            "compare": ["pixels"],
        }],
    }
    assert validate_contract(contract) == []


def test_non_static_region_requires_reason_ignored_observation_and_replacement():
    contract = {
        "schema": 1,
        "regions": [{
            "id": "video",
            "owner": "player",
            "importance": "critical",
            "mode": "layout_behavior",
            "bounds": {"x": 20, "y": 20, "width": 400, "height": 700},
            "compare": ["bounds"],
        }],
    }
    errors = validate_contract(contract)
    assert any("reason" in error for error in errors)
    assert any("ignore_observations" in error for error in errors)
    assert any("replacement invariant" in error for error in errors)


def test_critical_residual_is_fail_closed():
    contract = {
        "schema": 1,
        "regions": [{
            "id": "canvas",
            "owner": "hero",
            "importance": "critical",
            "mode": "residual",
            "bounds": {"x": 0, "y": 0, "width": 800, "height": 500},
            "reason": "unmeasurable",
        }],
    }
    assert any("critical residual" in error for error in validate_contract(contract))
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/test_comparison_contract.py`

Expected: collection fails because `core.comparison_contract` does not exist.

- [ ] **Step 3: Implement the schema and persistence helpers**

Implement:

```python
SCHEMA_VERSION = 1
VALID_MODES = {
    "static_pixels",
    "layout_style",
    "layout_behavior",
    "stateful_pixels",
    "residual",
}
VALID_IMPORTANCE = {"critical", "important", "supporting"}


def validate_contract(contract: dict) -> list[str]: ...
def save_contract(contract: dict, path: str | Path) -> None: ...
def load_contract(path: str | Path) -> dict: ...
def region_map(contract: dict) -> dict[str, dict]: ...
```

Validation must reject duplicate ids, invalid/empty bounds, missing owners,
unknown modes, critical residuals, and non-static regions without an explicit
reason, ignored observation, and replacement invariant.

- [ ] **Step 4: Run focused tests**

Run: `./.venv/bin/pytest -q tests/test_comparison_contract.py`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add core/comparison_contract.py tests/test_comparison_contract.py
git commit -m "feat: add semantic comparison contract"
```

### Task 2: Bounded volatility evidence

**Files:**
- Create: `core/volatility.py`
- Modify: `core/extractor/dom_scripts.py`
- Modify: `core/extractor/service.py`
- Test: `tests/test_volatility.py`
- Test: `tests/test_capture_inventory_scripts.py`

- [ ] **Step 1: Write failing evidence tests**

```python
from core.volatility import build_volatility_summary


def test_video_is_hint_not_automatic_waiver():
    summary = build_volatility_summary([{
        "id": "player",
        "tag": "video",
        "rect": {"x": 10, "y": 20, "width": 400, "height": 700},
        "changed_samples": 2,
        "total_samples": 3,
    }])
    assert summary["candidates"][0]["hint"] == "runtime_media"
    assert summary["candidates"][0]["suggested_mode"] == "layout_behavior"
    assert summary["candidates"][0]["requires_agent_decision"] is True


def test_static_image_remains_strict_hint():
    summary = build_volatility_summary([{
        "id": "hero-image",
        "tag": "img",
        "rect": {"x": 0, "y": 0, "width": 900, "height": 600},
        "changed_samples": 0,
        "total_samples": 3,
    }])
    assert summary["candidates"][0]["suggested_mode"] == "static_pixels"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/test_volatility.py`

Expected: import failure.

- [ ] **Step 3: Implement compact evidence normalization**

`build_volatility_summary(records, max_candidates=64)` must emit only:

```python
{
    "schema": 1,
    "sample_count": 3,
    "candidates": [{
        "id": "...",
        "tag": "video",
        "bounds": {...},
        "hint": "runtime_media",
        "changed_samples": 2,
        "suggested_mode": "layout_behavior",
        "requires_agent_decision": True,
    }],
}
```

The function may suggest but never finalize comparison modes.

- [ ] **Step 4: Add browser-side semantic inventory**

Extend the existing extraction inventory script to record bounded candidates for
`video`, `canvas`, time-like elements, aria-live regions, carousels, and elements
whose visible text/presentation changed across the extractor's stabilization
samples. Persist the compact summary as
`evidence/volatility_summary.json`.

- [ ] **Step 5: Run focused extraction tests**

Run:

```bash
./.venv/bin/pytest -q \
  tests/test_volatility.py \
  tests/test_capture_inventory_scripts.py \
  tests/test_dom_scripts.py
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add core/volatility.py core/extractor/dom_scripts.py core/extractor/service.py \
  tests/test_volatility.py tests/test_capture_inventory_scripts.py
git commit -m "feat: capture bounded volatility evidence"
```

### Task 3: Contract-aware fidelity gate

**Files:**
- Create: `core/gates/semantic_fidelity.py`
- Modify: `core/gates/fidelity.py`
- Test: `tests/gates/test_semantic_fidelity.py`

- [ ] **Step 1: Write failing video/static-region tests**

```python
def test_changing_video_pixels_do_not_fail_when_invariants_match(tmp_path):
    report = evaluate_contract(
        ref_png=ref_with_red_video,
        cand_png=cand_with_blue_video,
        contract=video_layout_behavior_contract,
        ref_facts={"player": matching_facts},
        cand_facts={"player": matching_facts},
    )
    assert report["regions"][0]["status"] == "pass"
    assert report["regions"][0]["excluded_observations"] == ["media_frame_pixels"]


def test_video_geometry_change_still_fails(tmp_path):
    report = evaluate_contract(
        ref_png=ref,
        cand_png=cand,
        contract=video_layout_behavior_contract,
        ref_facts={"player": {"bounds": {"width": 400, "height": 700}}},
        cand_facts={"player": {"bounds": {"width": 360, "height": 700}}},
    )
    assert report["regions"][0]["status"] == "fail"
    assert "bounds" in report["regions"][0]["failed_invariants"]


def test_static_image_pixels_remain_strict(tmp_path):
    report = evaluate_contract(ref, different_candidate, static_contract, {}, {})
    assert report["regions"][0]["status"] == "fail"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/gates/test_semantic_fidelity.py`

Expected: import failure.

- [ ] **Step 3: Implement 2D region helpers**

Add deterministic helpers:

```python
def crop_box(image: Image.Image, bounds: dict, page_size: tuple[int, int]) -> Image.Image: ...
def normalize_excluded_rects(bounds: dict, exclusions: list[dict]) -> list[dict]: ...
def masked_ssim_2d(ref: Image.Image, cand: Image.Image, exclusions: list[dict]) -> dict: ...
```

`masked_ssim_2d` must return score, excluded pixel fraction, and visible 2D
bounds; it cannot silently exclude a whole critical region.

- [ ] **Step 4: Implement invariant evaluation**

Implement:

```python
def evaluate_contract(
    ref_png: str,
    cand_png: str,
    contract: dict,
    ref_facts: dict[str, dict],
    cand_facts: dict[str, dict],
    threshold: float = 0.97,
) -> dict: ...
```

Geometry tolerance defaults to 2 CSS px and aspect-ratio tolerance to 0.005.
Static regions require threshold SSIM. Layout modes require every declared
invariant. Aggregate score remains informational and only includes valid static
pixel observations.

- [ ] **Step 5: Run focused gates**

Run:

```bash
./.venv/bin/pytest -q \
  tests/gates/test_semantic_fidelity.py \
  tests/test_visual_diff.py \
  tests/test_fidelity_mask.py
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add core/gates/semantic_fidelity.py core/gates/fidelity.py \
  tests/gates/test_semantic_fidelity.py
git commit -m "feat: score semantic region invariants"
```

### Task 4: Token-bounded repair packet

**Files:**
- Create: `core/repair_packet.py`
- Test: `tests/test_repair_packet.py`

- [ ] **Step 1: Write failing packet-budget tests**

```python
from core.repair_packet import build_repair_packet


def test_packet_contains_only_worst_region_and_relevant_sources():
    packet = build_repair_packet(report, contract, sources, max_text_bytes=16_384)
    assert packet["target"]["id"] == "details"
    assert set(packet["sources"]) == {"Details.jsx", "Details.css"}
    assert packet["text_bytes"] <= 16_384


def test_packet_preserves_target_evidence_when_trimming():
    packet = build_repair_packet(large_report, contract, large_sources, max_text_bytes=2048)
    assert packet["target"]["measurements"]
    assert packet["target"]["source_crop"]
    assert packet["target"]["candidate_crop"]
    assert packet["truncated_fields"]
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/test_repair_packet.py`

Expected: import failure.

- [ ] **Step 3: Implement deterministic packet selection**

Implement:

```python
def select_worst_region(report: dict) -> dict: ...
def build_repair_packet(
    report: dict,
    contract: dict,
    sources: dict[str, str],
    attempts: list[dict] | None = None,
    max_text_bytes: int = 16_384,
) -> dict: ...
```

Trim in this order: unrelated regions, comments, unrelated selectors, old
attempt details. Never remove target measurements, contract, evidence paths, or
owner identity.

- [ ] **Step 4: Run tests**

Run: `./.venv/bin/pytest -q tests/test_repair_packet.py`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add core/repair_packet.py tests/test_repair_packet.py
git commit -m "feat: build token-bounded repair packets"
```

### Task 5: Monotonic candidate ledger

**Files:**
- Create: `core/iteration_ledger.py`
- Test: `tests/test_iteration_ledger.py`

- [ ] **Step 1: Write failing monotonicity tests**

```python
from core.iteration_ledger import record_attempt


def test_improving_candidate_is_accepted():
    result = record_attempt(ledger, target="details", before=0.81, after=0.88,
                            hard_gate_regressions=[])
    assert result["accepted"] is True
    assert result["ledger"]["best"]["details"] == 0.88


def test_regression_is_rejected_and_best_is_preserved():
    result = record_attempt(ledger_with_best, target="details", before=0.88,
                            after=0.84, hard_gate_regressions=[])
    assert result["accepted"] is False
    assert result["restore_candidate"]


def test_two_non_improving_attempts_plateau_target():
    result = record_attempt(ledger_with_one_rejection, target="details",
                            before=0.88, after=0.88, hard_gate_regressions=[])
    assert result["plateaued"] is True
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/test_iteration_ledger.py`

Expected: import failure.

- [ ] **Step 3: Implement ledger rules**

Implement JSON-serializable functions:

```python
def new_ledger(max_target_attempts: int = 5, max_total_attempts: int = 12) -> dict: ...
def record_attempt(
    ledger: dict,
    target: str,
    before: float,
    after: float,
    hard_gate_regressions: list[str],
    candidate_path: str | None = None,
) -> dict: ...
```

An accepted attempt must strictly improve the target and have zero hard-gate
regressions. Preserve the best candidate path and stop at the configured target
or total budgets.

- [ ] **Step 4: Run tests**

Run: `./.venv/bin/pytest -q tests/test_iteration_ledger.py`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add core/iteration_ledger.py tests/test_iteration_ledger.py
git commit -m "feat: preserve monotonic clone improvements"
```

### Task 6: MCP and Harness integration

**Files:**
- Modify: `mcp_server/tools/verify.py`
- Modify: `mcp_server/server.py`
- Modify: `skill/SKILL.md`
- Modify: `skill/references/harness-contract.md`
- Test: `tests/mcp/test_semantic_comparison_tools.py`
- Test: `tests/test_agent_harness_skill.py`

- [ ] **Step 1: Write failing MCP contract tests**

Test these async functions directly:

```python
async def test_get_comparison_evidence_is_bounded_and_requires_capture(...): ...
async def test_save_comparison_contract_rejects_invalid_contract(...): ...
async def test_score_semantic_fidelity_returns_region_report(...): ...
async def test_build_semantic_repair_packet_respects_budget(...): ...
```

- [ ] **Step 2: Run tests and verify failure**

Run: `./.venv/bin/pytest -q tests/mcp/test_semantic_comparison_tools.py`

Expected: missing tool functions.

- [ ] **Step 3: Implement deterministic tools**

Add:

```python
async def get_comparison_evidence(source_id: str) -> dict: ...
async def save_comparison_contract(source_id: str, contract: dict) -> dict: ...
async def score_semantic_fidelity(
    source_id: str,
    url: str | None = None,
    threshold: float = 0.97,
) -> dict: ...
async def build_semantic_repair_packet(
    source_id: str,
    report: dict,
    max_text_bytes: int = 16_384,
) -> dict: ...
```

Register them in `mcp_server/server.py`. Persist contracts beside source
evidence and copy the active contract into sandbox `.pwc/`.

- [ ] **Step 4: Update Agent instructions**

The skill must state:

1. inspect the real page and compact evidence before scoring;
2. author a comparison contract;
3. never use raw whole-page SSIM as a CSS verdict when volatile observations
   exist;
4. repair only the worst valid region from the bounded packet;
5. keep only monotonic improvements;
6. report dynamic-region invariants and exclusions explicitly.

- [ ] **Step 5: Run integration tests**

Run:

```bash
./.venv/bin/pytest -q \
  tests/mcp/test_semantic_comparison_tools.py \
  tests/test_agent_harness_skill.py \
  tests/mcp/test_score_clone_sections.py
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add mcp_server/tools/verify.py mcp_server/server.py skill/SKILL.md \
  skill/references/harness-contract.md tests/mcp/test_semantic_comparison_tools.py \
  tests/test_agent_harness_skill.py
git commit -m "feat: integrate semantic comparison loop"
```

### Task 7: Full verification and live A/B trial

**Files:**
- Create: `docs/experiments/2026-07-26-semantic-comparison-ab.md`
- Create: `delivery/semantic-comparison-ab.json`

- [ ] **Step 1: Run the complete test suite**

Run: `./.venv/bin/pytest -q`

Expected: zero failures.

- [ ] **Step 2: Select a held-out page**

Choose one public unauthenticated page not used in implementation, containing
stable UI and at least one naturally changing or stateful region. Record the
exact URL before extraction so it cannot be changed after seeing results.

- [ ] **Step 3: Run checkpoint baseline**

Using checkpoint `88208f3`, capture, reproduce, and record:

- raw visual result;
- false failures caused by volatile observations;
- static-region scores;
- Agent repair iterations;
- evidence payload bytes;
- structural and interaction results.

- [ ] **Step 4: Run optimized workflow**

Using the same source capture when valid, run the semantic contract flow and
record the same metrics. The Agent may repair only from bounded packets.

- [ ] **Step 5: Write A/B artifacts**

`delivery/semantic-comparison-ab.json` must contain machine-readable source URL,
commit ids, contracts, scores, iteration counts, packet bytes, residuals, and
evidence paths. The Markdown report must explain whether the new evidence is
more trustworthy and whether the final static UI improved.

- [ ] **Step 6: Run final regression tests**

Run:

```bash
./.venv/bin/pytest -q
git diff --check
```

Expected: all tests pass and no whitespace errors.

- [ ] **Step 7: Commit and push**

```bash
git add docs/experiments/2026-07-26-semantic-comparison-ab.md \
  delivery/semantic-comparison-ab.json
git commit -m "test: validate semantic comparison on held-out page"
git push -u origin codex/semantic-comparison-loop
```
