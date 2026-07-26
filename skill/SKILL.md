---
name: perfect-web-clone-v4
description: >-
  Reproduce a live website from its URL as a clean, deployable Vite + React
  project by running the complete agent-driven Perfect Web Clone harness:
  capture source evidence, plan the full page, author every section, implement
  common interactions, build, compare, repair, and hand the measured result to
  the user for review. Use whenever the user asks an agent to clone, copy,
  reproduce, replicate, rebuild, or 复刻 a website or web page, including a
  minimal request containing only an action and URL. The user gives one natural
  language instruction; the current Claude Code/Codex agent runs the internal
  multi-step loop through the deterministic pwc4 MCP tools.
---

# Perfect Web Clone v4

## Operating model

The current agent is the harness runtime.
Do not require a CLI, API, daemon, or separate orchestrator.
The `pwc4` tools are deterministic hands and eyes; they capture, persist, build,
render, replay, and measure. They never call another model. Use the current
agent to understand the evidence, author code, and choose targeted repairs.

A single natural-language request such as “复刻 https://example.com” authorizes
the entire local reproduction workflow. Treat it as one user operation even
though the harness performs many internal tool calls and repair iterations.

Do not ask for routine confirmation when the request contains a usable URL.
Infer that a full-page clone is the default.
Continue across phases without returning control merely to announce progress or
request ordinary implementation choices. Ask only when a missing fact would
materially change scope, when credentials or new authority are required, or when
the user must resolve an external blocker.

Deployment is never implicit. Produce a local build and review URL by default;
deploy only when the user explicitly asks.

Use one owning agent for the whole page so global visual context survives across
sections. Do not delegate unless the user explicitly asks.

## Non-negotiable execution contract

1. Run capture, planning, authoring, build, verification, repair, and handoff as
   one continuous task.
2. Inspect every `ok` or `success` flag and its error evidence. Never invent a
   tool result.
3. Preserve immutable raw evidence separately from normalized evidence. Refuse
   to plan from an incomplete capture.
4. Reproduce every planned top-level section and every independently required
   critical region. Do not stop after the viewport or after a visually dominant
   subset.
5. Implement and replay every required common interaction: carousel, menu, tabs,
   accordion/details, and other contracts discovered during capture.
   A visually similar but inert control fails.
6. Run gates in dependency order. A downstream score cannot override an
   upstream structural or behavioral failure.
7. Repair the smallest owning component identified by evidence, rebuild, and
   re-run all affected gates.
8. Never hide, waive silently, or average away a red gate.
   A missing critical region cannot be offset by aggregate visual similarity.
9. End only in `ready_for_user_review` or `failed_with_residuals`.
   Only the user can accept the result.
10. Account for Agent Token usage throughout the source-scoped run. Prefer
    provider-reported usage, label estimates, and never merge actual and estimated
    totals into a fake exact number.

Read [references/harness-contract.md](references/harness-contract.md) before
starting a new run or resuming one. It defines the progress ledger, terminal
states, evidence vocabulary, and exact stop rules.

## Continuous workflow

### 1. Resolve and resume

- Extract the target URL from the request. If none is present and it cannot be
  recovered from the current browser/task context, ask for it.
- Check the active sandbox for `.pwc/run.json`. Resume rather than restart when
  its URL matches and its status is non-terminal. Start a fresh run when the URL
  differs.
- Record the current phase and evidence after every successful phase and after
  every failure. The ledger is an audit trail, not a substitute for tool output.

### 2. Capture trustworthy source evidence

Call `pwc4 extract_page(url, options)`.

- Require `ok: true` and
  `summary.capture_integrity.status == "passed"`.
- Record `source_id`; use the same value for all later tools.
- Verify that `current_theme` and the primary raster preserve the source's
  authored default root state. A named theme such as `business`, `forest`, or a
  branded token is not interchangeable with a generic `light`/`dark` toggle.
- Surface `capture_residuals` and the `site_classification` ceiling. If the page
  relies on WebGL, runtime canvas drawing, or scroll choreography that cannot be
  captured faithfully, continue only within the measured ceiling and keep it as
  a residual.
- Stop with `failed_with_residuals` if source integrity remains red after the
  extractor's retry budget. Never generate from guessed or partial content.
- Immediately call `pwc4 generate_manifest(source_id)` so breakpoint, state, and
  interaction expectations exist before code generation.

### 3. Understand change and author the comparison contract

Call `pwc4 get_comparison_evidence(source_id)` once. Review its bounded section,
critical-region, interaction, and volatility records alongside the source
raster. A volatility mode is only a hint; the current Agent makes the decision.

For every important region ask: **could this observation change while the real
page's design and behavior remained correct after a natural refresh?**

- If no, use `static_pixels` (or a named `stateful_pixels` state) and keep pixel
  comparison strict.
- If yes, name only the observation that may vary, explain why, and supply
  replacement invariants such as bounds, aspect ratio, container style,
  controls, and interaction behavior.
- A dynamic region is never an excuse to ignore its container, chrome, controls,
  geometry, or behavior. Unknown critical regions remain strict.

Persist the Agent-authored result with
`pwc4 save_comparison_contract(source_id, contract)`. Fix every validation error
before continuing.

### 4. Plan the complete page

Call `pwc4 get_section_plan(source_id)`.

- Use the ordered real `#main` children as section and repair units.
- Treat every `required_structure` entry as a hard anchor, even when nested
  inside a large parent section.
- Review page geometry and source screenshots before authoring. Confirm that the
  plan spans the captured document height and contains the prominent regions
  visible in the raw evidence.
- Preserve the authored root theme attributes and computed color scheme in the
  clone. Do not infer the default theme from the Agent's own browser preference.
- Record all planned section ids in `.pwc/run.json`.

### 5. Create the shell and author every section

Call `pwc4 assemble_project(source_id)` once to create the sandbox shell.
Missing section files are expected on this first call. Assembly initializes
`.pwc/run.json`; read, update, and rewrite that ledger through the sandbox tools
as the agent advances.

Immediately call pwc4 `begin_token_accounting(source_id)` after the run ledger
exists. This establishes the provider baseline for the source-scoped run. The
capture, understanding, and planning work that occurred before this baseline
must be checkpointed as labeled estimates; do not describe the resulting
mixed report as complete actual usage.

The accounting tool sequence is `begin_token_accounting`,
`checkpoint_token_accounting`, `finalize_token_accounting`, and
`get_token_report`.

After every later phase call
pwc4 `checkpoint_token_accounting(source_id, phase, operation, context)`.
Use these phase names: `capture`, `understand`, `plan`, `generate`, `build`,
`verify`, `repair`, `debug`, and `handoff`. Unexpected Harness failures such as
a corrupted theme baseline belong to `debug`, never ordinary repair.

For each planned section, in order:

1. Call `pwc4 get_section_data(source_id, section_id)`.
2. Author clean semantic JSX and scoped local styles from the section evidence.
3. Write only its namespaced component files with
   `pwc4 sandbox_write_file(path, content, namespace)`.
4. Mark the section complete in `.pwc/run.json`.

Maintain whole-page layout tokens across sections. Reuse localized assets from
the capture. Never ship source-framework markup, source-specific class
fingerprints, hotlinked media, or an image snapshot in place of real content.
Use real text, images, links, video, and controls.

Apply these authoring requirements:

- Preserve sticky behavior and avoid clipping sticky ancestors.
- Reconstruct footer columns from source layout geometry.
- Render review widgets from captured review data.
- Emit functional localized video elements.
- Reveal recoverable lazy content instead of preserving an accidental empty
  capture state.
- Attach `data-pwc-critical="<anchor>"` to each required structural region.
- Attach `data-pwc-compare="<contract region id>"` to contract regions whose
  invariant facts must be measured; an explicit contract selector may be used
  when the wrapper is not the correct measurement target.
- Keep the assembly-owned `data-pwc-section` wrapper for every section.

For each interaction contract:

- Implement its state transition and visible controlled surface.
- Attach `data-pwc-interaction="<contract id>"` to the control.
- Attach `data-pwc-controlled="<contract id>"` to the controlled surface where
  applicable.
- Support repeated activation where the source does, such as next/previous
  carousel steps and open/close menu or accordion behavior.

An unresolved asset, region, or behavior becomes an explicit residual.

### 6. Build before judging fidelity

Call `pwc4 assemble_project(source_id)` again.

- Require no `missing_section_files`.
- Call `pwc4 build_project()` and require `success: true` plus a produced
  `dist/`.
- On failure, use `pwc4 get_build_errors()` or `pwc4 diagnose()`, repair the
  owning component, and rebuild.

Never run acceptance scoring against a broken or stale build.

### 7. Verify in gate order

Start the local preview with `pwc4 start_preview()` and retain its URL for user
review. Verify at the captured breakpoints and observable states.

Run:

1. Source integrity from extraction.
2. Critical structure through `pwc4 score_clone_sections(source_id, url)`.
3. Required interaction replay through
   `pwc4 verify_manifest(source_id, url)`.
4. Build cleanliness through `pwc4 check_fingerprints(dist_dir)`.
5. Code/asset weight through `pwc4 check_weight(dist_dir, budget_kb)`.
6. Contract-aware visual and invariant comparison through
   `pwc4 score_semantic_fidelity(source_id, url)`, plus per-state results from
   `verify_manifest`; use
   `pwc4 score_fidelity(...)` only for additional localization.
7. `pwc4 compare_to_baseline(...)` when a valid same-source baseline exists.

Whole-page SSIM is diagnostic, not a CSS verdict when legitimate live
observations differ. Do not treat one aggregate SSIM number as acceptance.
Structure, interaction, every contract region, and each required
breakpoint/state remain individually visible in the result.

### 8. Repair automatically

While a required gate is red and budget remains:

1. Select the earliest failed hard gate; within it select the worst measured
   section or state.
2. Call `pwc4 build_semantic_repair_packet(source_id, report)` for a visual or
   invariant failure. Its 16 KiB default budget supplies only the worst target,
   its contract, measurements, and owning component sources.
3. Read only additional source evidence proven necessary for that target.
4. Make one evidence-based repair to that component or shared token when the
   evidence proves the error is global.
5. Rebuild and replay every affected structural, behavioral, and visual gate.
6. Call `pwc4 record_semantic_attempt(...)` with the before/after measurement
   and any hard-gate regressions. Keep an improving candidate only when no hard
   gate regresses; otherwise restore the returned best candidate.
7. Update `.pwc/run.json` with packet bytes, the accepted/rejected attempt,
   measurement delta, and evidence paths.
8. Call pwc4 `checkpoint_token_accounting` with the repair packet byte/Token
   estimate and the same before/after/accepted quality evidence.

Use at most five repair attempts per breakpoint × state. Stop early after one
non-improving retry followed by a second attempt that also fails to improve the
same metric. Preserve the best measured candidate; do not leave a regression as
the final artifact.

Token budgets use **non-cached input plus output**, not gross processed input:

- soft budget: `250K`;
- hard budget: `500K`;
- a soft warning requires the next operation to use the smallest owner-scoped
  evidence path;
- at the hard stop, do not begin another repair;
- the hard Token budget cannot waive a failed gate. Preserve the best candidate
  and use `failed_with_residuals` when a required gate remains red.

Actual and estimated usage may both be present, but never merge them. Cached
input, non-cached input, output, usage by phase, and accepted/rejected repair
efficiency remain separately visible.

### 9. Hand off honestly

Set `ready_for_user_review` only when:

- capture integrity passed;
- all planned sections and critical anchors exist materially;
- all required common interactions replay successfully;
- the production build passed;
- fingerprints and required budgets passed;
- required visual breakpoint/state gates passed; and
- every claimed result has an evidence path or tool output.

Otherwise set `failed_with_residuals` and list every residual with its gate,
section/state, expected value, measured value, evidence, attempts, and reason for
stopping.

Return the local review URL, source project path, `dist/` path, evidence/report
paths, gate summary, and residuals. Say “ready for your review,” never “accepted”
or “pixel-perfect.” The user's visual and functional review is the final
decision.

Before returning, call pwc4 `finalize_token_accounting(source_id)` and then
`get_token_report(source_id)`. Include its compact totals, measurement
status, accounting completeness, budget status, highest-cost phases, and
Token-per-accepted-repair result. If provider telemetry was unavailable, say
that the total is estimated. A repair packet estimate is never the total run
usage.

## Tool map

| Purpose | `pwc4` tools |
|---|---|
| Capture and understand | `extract_page`, `generate_manifest`, `get_comparison_evidence`, `save_comparison_contract` |
| Plan | `get_section_plan`, `get_section_data` |
| Author and inspect | `assemble_project`, `sandbox_write_file`, `sandbox_read_file`, `sandbox_list_files` |
| Build and diagnose | `build_project`, `get_build_errors`, `diagnose` |
| Preview | `start_preview`, `preview_status`, `preview_screenshot` |
| Verify | `score_clone_sections`, `score_semantic_fidelity`, `verify_manifest`, `check_fingerprints`, `check_weight`, `compare_to_baseline` |
| Targeted repair | `build_semantic_repair_packet`, `record_semantic_attempt` |
| Optional delivery | `deploy` only after an explicit user request |

The IR tools (`build_ir`, `run_recognizers`, `generate_code`) remain
experimental and are not the default path for client work.
