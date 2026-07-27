# Harness Enforcement Completion Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement each task with a
> failing regression test, focused verification, spec review, and code-quality
> review.

**Goal:** Turn the existing comparison tools and Agent instructions into a
durable, reusable Harness that cannot hand off a red clone while an actionable
repair remains, checks every required breakpoint, catches runtime/resource
failures, and is discoverable as one versioned Agent plugin.

**Architecture:** A pure run-state reducer owns `.pwc/run.json`. MCP gate tools
feed measured evidence into that reducer and receive one deterministic next
action. A failed gate creates a persisted repair obligation; only all-green
gates can transition to `ready_for_user_review`, while a residual handoff
requires a recorded hard stop. Source capture and replay operate at desktop and
mobile breakpoints. The repository is packaged as a Codex/Claude-compatible
plugin so the skill and MCP server resolve from the same checkout.

**Tech Stack:** Python 3.12, Playwright, FastMCP, Pydantic v2, Pillow, pytest,
Vite/React fixtures.

---

## Task 1: Enforced run-state loop

**Files:**
- Create: `core/run_controller.py`
- Modify: `mcp_server/tools/verify.py`
- Modify: `mcp_server/server.py`
- Modify: `core/iteration_ledger.py`
- Test: `tests/test_run_controller.py`
- Test: `tests/mcp/test_run_terminalization.py`
- Test: `tests/mcp/test_semantic_comparison_tools.py`

- [ ] Write failing tests for red-to-repair, pass-to-clear, resume, plateau,
  hard-token stop, and terminal-state rejection.
- [ ] Implement a pure reducer with explicit `execution_ok`, `gate_status`,
  `must_continue`, `next_action`, and `terminal_allowed` outputs.
- [ ] Persist the latest semantic report and digest; packet construction must
  reject stale/tampered reports and ineligible repair targets.
- [ ] Make invariant-only failures recordable without Agent-invented scores.
- [ ] Add deterministic terminalization and register its MCP surface.
- [ ] Run focused tests and commit.

## Task 2: Runtime and responsive gates

**Files:**
- Create: `core/runtime_audit.py`
- Create: `mcp_server/tools/runtime_audit.py`
- Modify: `mcp_server/server.py`
- Test: `tests/test_runtime_audit.py`
- Test: `tests/mcp/test_runtime_audit_tools.py`

- [ ] Write failing tests for horizontal overflow, broken images/fonts,
  external hotlinks, console/resource errors, and mobile-only regressions.
- [ ] Capture deterministic evidence at every declared breakpoint.
- [ ] Persist the result into the common run ledger and return the next action.
- [ ] Run focused tests and commit.

## Task 3: Desktop and mobile source evidence

**Files:**
- Modify: `core/extractor/models.py`
- Modify: `core/extractor/service.py`
- Modify: `core/extractor/api.py`
- Modify: `core/refs.py`
- Modify: `mcp_server/tools/verify.py`
- Test: `tests/test_extractor_multi_breakpoint.py`
- Test: `tests/test_refs.py`
- Test: `tests/mcp/test_manifest_tools.py`

- [ ] Write failing persistence and checklist tests for desktop plus mobile.
- [ ] Capture and persist full-page and scroll-state evidence for both.
- [ ] Seed and replay every breakpoint rather than only the primary viewport.
- [ ] Run focused tests and commit.

## Task 4: Hermetic preview verification

**Files:**
- Create or modify: `showcase/products/reelshort/tests/conftest.py`
- Modify: `showcase/products/reelshort/tests/test_desktop_contract.py`
- Test: `showcase/products/reelshort/tests/test_desktop_contract.py`

- [ ] Replace the hard-coded external dev-server dependency with a fixture that
  builds, starts a strict ephemeral preview, waits for readiness, and tears down.
- [ ] Verify the test exercises the fresh `dist`, not a stale Vite dev server.
- [ ] Run the focused test and commit.

## Task 5: Version-bound Agent plugin

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `skills/perfect-web-clone-v4/SKILL.md`
- Create: `skills/perfect-web-clone-v4/agents/openai.yaml`
- Create: `skills/perfect-web-clone-v4/references/harness-contract.md`
- Modify: `.mcp.json`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Test: `tests/test_plugin_package.py`
- Modify: `tests/test_agent_harness_skill.py`

- [ ] Write failing plugin-layout, path-resolution, and instruction tests.
- [ ] Make the plugin skill the canonical Agent contract and keep compatibility
  with existing repository references.
- [ ] Remove checkout-specific absolute paths from MCP configuration and expose
  the v4 console entry point.
- [ ] Validate with the plugin validator, run focused tests, and commit.

## Task 6: Full Harness and Jose reference-set validation

- [ ] Run the complete Python suite from a clean, self-owned preview lifecycle.
- [ ] Build every tracked Jose project from Git inputs only.
- [ ] Run structure, interaction, runtime, fingerprint, weight, and semantic
  gates at desktop and mobile breakpoints.
- [ ] Confirm red results persist a next repair action and cannot become ready.
- [ ] Commit final test/report updates and provide only original URLs plus live
  localhost URLs for user review.
