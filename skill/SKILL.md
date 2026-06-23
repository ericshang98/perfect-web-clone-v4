---
name: perfect-web-clone-v4
description: >-
  Clone any live web page into a deployable Vite + React + Tailwind static
  project that is clean BY CONSTRUCTION and pixel-perfect AS A MEASURED GATE.
  Drives the deterministic `pwc4` MCP tools: extract the page, build a semantic
  IR (+ design tokens), run recognizers, generate clean code from the IR,
  assemble and build, then run the gate-driven self-heal loop
  (`check_fingerprints` ∧ `check_weight` ∧ `score_fidelity`) — on any failure,
  localize the worst region, repair that one IR component, regenerate, and
  re-gate until green or the budget is hit. Use whenever the user wants to clone,
  copy, replicate, or "rebuild this site" from a URL. Two non-negotiable, joint
  goals: cleanest-possible code AND pixel-perfect fidelity.
---

# Perfect Web Clone v4 — The Cloning Playbook

You are the brain. The `pwc4` MCP tools are pure, deterministic hands and eyes:
they extract, build the IR, run recognizers, generate code, assemble, build,
screenshot, scan, measure, and score. **No tool ever calls an LLM.** Every act
of *judgement* — deciding *how* to repair a flagged IR component against a
measured diff — is *yours*.

> **THE IRON RULE.** Layers 0–3 and every gate are deterministic Python: capture,
> build IR, run recognizers, generate code, render, scan, measure, score — they
> NEVER call a model. Claude Code is the brain in exactly one place: the Layer-4
> repair decision. Given a gate failure + the localized region + the offending IR
> node, *you* decide how to fix that one component — and you edit the IR / one
> component, never a wall of raw source.

> **TWO JOINT GOALS, TWO LAYERS.** "Clean" is born in the IR (Layer 1: our
> vocabulary, deduped design tokens, zero Shopify names). "Pixel-perfect" is
> enforced downstream (Layer 4: SSIM against the captured reference rasters). The
> two goals are decoupled into different layers, so they never fight over the same
> artifact. Both are *measured gates*, not matters of diligence.

All `pwc4` tools return `{"ok": bool, ...}` (build tools use `{"success": ...}`).
Always check that flag and read `error` / `errors` before proceeding. Never
fabricate a result you did not get back from a tool.

---

## Phase 0 — Frame the job

1. Confirm the target URL with the user. If they gave a vague request
   ("clone this"), get the exact URL.
2. Confirm scope: full-page clone is the default. Note explicit asks
   (e.g. "also give me a Dockerfile", "deploy it").
3. **Deployment is opt-in.** Do NOT deploy unless the user explicitly asks.
   Default delivery is the local `dist/` bundle (the standing no-deploy rule).

---

## Phase 1 — Extract (Layer 0: capture ground truth)

Call **`pwc4 extract_page(url, options)`**.

- Captures, per breakpoint (1440 / 768 / 375): DOM + computed styles + box
  geometry + assets + fonts, **and the REFERENCE RASTERS** per breakpoint × key
  state (initial, scrolled, hover/expanded). Triggers lazy-load, collects
  video/iframe sources, dismisses overlays.
- Returns `source_id` + a `summary`. **Record `source_id`** — it threads through
  every later phase. The captured rasters are the immutable ground truth every
  downstream artifact is judged against.
- If `ok` is false (bad URL, page won't load), report the error and stop. Do not
  guess at page content you never extracted.

---

## Phase 2 — Build IR (Layer 1: the keystone)

Call **`pwc4 build_ir(dom, css, breakpoints)`** with the captured DOM + computed
styles.

- Returns `{ok, document}`. `document` is the normalized semantic IR: a
  framework-agnostic component tree in OUR vocabulary plus a deduplicated
  **design-token table** (colors / spacing / type / radii / shadows).
- This is where "clean" is *born*: Shopify class/id fingerprints
  (`shopify-section`, `template--…__main`) are normalized away, repeated
  declarations collapse to shared tokens, and resolved style values become token
  refs. There is no Shopify source text left to leak.
- **Do not hand-edit the IR here.** Treat the returned `document` as the contract
  the rest of the pipeline reads and writes.

---

## Phase 3 — Run recognizers (Layer 2: pluggable registry)

Call **`pwc4 run_recognizers(document)`** with the IR from Phase 2.

- Returns `{ok, document, reports}`. Each recognizer pattern-matches IR subtrees
  and rewrites a dumb subtree into a smart component spec:
  - **sticky-guard** — ensure no ancestor clips overflow (rewrite clipping
    `overflow` to `clip`/`visible`) so a `position:sticky` element keeps
    following scroll; preserve the containing block.
  - **footer-rebuild** — capture explicit grid/flex container props (columns,
    gap) so the footer can't disassemble; reconstruct columns from child bboxes
    if they were dropped.
  - **reviews** — detect judge.me / loox / yotpo / okendo signatures, EXTRACT the
    review DATA, and emit a data-driven `Reviews` component (NOT a static PNG).
  - **video-collector** — map `<video>`/`<source>`/youtube/vimeo to a real
    `VideoPlayer`/`VideoEmbed`; promote lazy `data-src` → `src`.
- Read `reports` (`{name, changed, error}` each). A recognizer that errored is
  recorded, never fatal — but note it; a missing recognition may surface later as
  a fidelity-gate miss you'll repair in Phase 6.

---

## Phase 4 — Generate code (Layer 3: clean codegen)

Call **`pwc4 generate_code(document)`** with the recognized IR.

- Returns `{ok, jsx, tailwind_theme}`: Vite + React + Tailwind emitted FROM the
  IR (never from source HTML). Utility classes + a design-token Tailwind theme;
  **zero inline raw-CSS dumps; no `original.css`**; one readable component per
  section; recognizer components (Reviews / VideoPlayer / VideoEmbed) rendered as
  shared imports.
- Write the emitted component files and theme into the sandbox via
  **`pwc4 sandbox_write_file(path, content)`**. Clean is guaranteed by
  construction — there is no Shopify source text in the IR to leak.

---

## Phase 5 — Assemble + build (deterministic)

1. **`pwc4 assemble_project(source_id)`** — the ONLY thing that writes the shared
   files (`App.jsx`, `index.css`, routing), deterministically, in section order.
   Read `missing_section_files`; `ok` is true only when nothing is missing. If a
   component is missing, regenerate it (Phase 4) and re-assemble. Do not advance
   with missing components.
2. **`pwc4 build_project()`** — runs `npm run build`. **`success` MUST be true**
   (exit code 0 *and* a `dist/` produced). If false, read `errors`/`stderr_tail`,
   locate the cause, fix the offending component in the IR + regenerate, and
   rebuild. Optionally use **`pwc4 get_build_errors()` / `pwc4 diagnose()`** for
   the three-layer (terminal / browser / static) breakdown. **The build must pass
   before verify — this is a hard gate.**

---

## Phase 6 — Verify (Layer 4: the gate-driven self-heal loop)

This loop is the heart of v4. It replaces eyeball judgement with **measured
gates**. Because §1 of the architecture guarantees a clean, pixel-identical
equivalent *exists*, this is a closed search that converges: generate clean
candidate → measure raster distance → repair the worst region → re-measure.

### The three deterministic gates (run every iteration)

1. **`pwc4 check_fingerprints(dist_dir)`** (R1) — `ok` iff `total == 0` Shopify
   traces (`shopify`, `myshopify`, `template--…__`, `data-shopify*`,
   `original.css`, `shopify-section`) in `dist/`. Read `by_pattern` / `files` to
   see exactly what leaked.
2. **`pwc4 check_weight(dist_dir, budget_kb)`** (R3) — `ok` iff `total_kb ≤`
   budget (default 120 KB gz, target 50–80 KB). Read `by_type` to see which
   bucket (js/css/assets) is heavy.
3. **`pwc4 score_fidelity(ref_png, cand_png, threshold)`** (R4) — render the
   built output at each breakpoint × state, then score SSIM vs the captured
   reference raster. `ok` iff `score ≥ τ` (default 0.97). Carries
   **`worst_regions`** (per-band SSIM, worst-first, each with a `y0`/`y1`
   y-range).

> **R5 — beat the baseline.** Where a current-repo baseline render exists, also
> run **`pwc4 compare_to_baseline(ref_png, new_png, baseline_png)`**; `ok` iff
> the new output's fidelity is strictly better than the baseline's.

### The self-heal loop

Run the gates. **While any gate is red and budget remains:**

1. **Localize.** Take the failing gate's evidence — `score_fidelity`'s
   `worst_regions[0]` (lowest-SSIM band) for visual misses, `check_fingerprints`'
   `files`/`by_pattern` for leaks, `check_weight`'s `by_type` for bloat.
2. **Map region → IR node.** Use the worst band's `y0`/`y1` against each node's
   `sourceBBox` to find the offending IR component.
3. **CC repairs THAT component in the IR.** This is your one act of judgement:
   given (the diff/region, the IR node, its computed style, the gate evidence),
   decide how to fix that single component — adjust its layout/style/tokens, or
   correct a recognizer's output. Edit the IR, not a wall of source.
4. **Regenerate** just the affected component (Phase 4) and re-assemble/build
   only what changed (Phase 5).
5. **Re-gate** (re-run all three). Loop.

### Exit / stop criteria (no infinite loops)

- **Exit (success):** `check_fingerprints.ok` ∧ `check_weight.ok` ∧
  `score_fidelity.ok` (per breakpoint × state) — and, where applicable,
  `compare_to_baseline.ok`.
- **Iteration cap: at most 5 self-heal iterations per breakpoint × state.** On
  hitting the cap with a gate still red, STOP looping for that target.
- **No-progress guard:** if an iteration does not raise the failing gate's score
  (e.g. SSIM did not improve), stop early rather than burn budget.
- **Report residuals — never silent.** At the cap, list every remaining
  residual (which gate, which region/node, the measured score vs τ) explicitly to
  the user. Long-tail items (bespoke frame-by-frame animation, WebGL) are flagged
  fallbacks, never silently dropped.

---

## Phase 7 — Deliver

- **Default:** deliver the deployable static bundle `dist/` (exportable locally).
  If asked, also produce a `Dockerfile` (nginx). Tell the user where `dist/` is
  and summarize the gate results: fingerprints clean, weight within budget,
  fidelity score per breakpoint × state, plus any residuals accepted at the cap.
- **Deploy is opt-in and low-priority.** Only if the user explicitly asked,
  deploy (Cloudflare Pages / `wrangler` only — no Vercel) and return the live URL.
  **Never deploy by default.**

---

## Tool quick-reference (all `pwc4`, all deterministic, zero LLM)

| Phase | Tool |
|---|---|
| 1 Extract | `extract_page(url, options)` |
| 2 Build IR | `build_ir(dom, css, breakpoints)` |
| 3 Recognizers | `run_recognizers(document)` |
| 4 Generate | `generate_code(document)`, `sandbox_write_file(path, content)` |
| 5 Assemble/build | `assemble_project(source_id)`, `build_project()`, `get_build_errors()`, `diagnose()` |
| 6 Verify (gates) | `check_fingerprints(dist_dir)`, `check_weight(dist_dir, budget_kb)`, `score_fidelity(ref_png, cand_png, threshold)`, `compare_to_baseline(ref_png, new_png, baseline_png)`, `preview_screenshot(...)` |
| 7 Deliver | (default: `dist/`) — optional deploy |

## Invariants (do not violate)

- **The iron rule:** tools never call an LLM. CC's only judgement is the Layer-4
  repair decision; it edits the IR / one component, never raw source.
- **Clean is born in the IR; fidelity is a downstream gate.** Generate from the
  IR, never from source HTML. There is no Shopify source text to leak.
- **Gates, not vibes.** Acceptance = `check_fingerprints` ∧ `check_weight` ∧
  `score_fidelity` (∧ `compare_to_baseline` where a baseline exists), all green.
- The self-heal loop has a hard iteration cap (5 per breakpoint × state) and a
  no-progress guard — never loop forever. Residuals are reported, never silent.
- `npm run build` must pass before verify; the built artifact is what the gates
  measure.
- Never deploy unless explicitly asked.
- Both goals are joint and non-negotiable: cleanest-possible code AND
  pixel-perfect fidelity, each enforced as a measured gate.
