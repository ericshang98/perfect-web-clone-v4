---
name: perfect-web-clone-v4
description: >-
  Clone any live web page into a deployable Vite + React + Tailwind static
  project that is clean BY CONSTRUCTION and pixel-perfect AS A MEASURED GATE.
  Default route: extract the page, plan sections by the real `#main` children,
  assemble a sandbox shell (with a deduped global cleaned stylesheet), then
  dispatch one subagent per section to author clean JSX + local styles from the
  captured data, build, and run the gate-driven self-heal loop
  (`check_fingerprints` ∧ `check_weight` ∧ `score_fidelity`) — on any failure,
  localize the worst region, repair that one section component, rebuild, and
  re-gate until green or the budget is hit. Use whenever the user wants to clone,
  copy, replicate, or "rebuild this site" from a URL. Two non-negotiable, joint
  goals: cleanest-possible code AND pixel-perfect fidelity.
---

# Perfect Web Clone v4 — The Cloning Playbook

> **★ North star (the guiding thesis).** Every requirement must first become a
> **deterministic, evidence-backed gate**, and only then be satisfied — never by
> "I think it looks close enough." The full guiding philosophy, the delivery
> contract, decision log, and roadmap live in **`docs/delivery-strategy.md`** (the
> canonical strategy doc). This SKILL is the operational playbook for it.

You are the brain. The `pwc4` MCP tools are pure, deterministic hands and eyes:
they extract, plan sections, assemble, build, screenshot, scan, measure, and
score. **No `pwc4` tool ever calls an LLM.** The *judgement* — authoring each
section's clean component, and deciding *how* to repair a flagged component
against a measured diff — is *yours* (you and the subagents you dispatch).

> **THE IRON RULE.** Every `pwc4` tool and every gate is deterministic Python:
> capture, plan, assemble, build, render, scan, measure, score — they NEVER call a
> model. The brain (you + per-section subagents) appears in exactly two places:
> **(1)** authoring each section into clean JSX from the captured section data,
> and **(2)** the Layer-4 repair decision. Everywhere else is deterministic.

> **TWO JOINT GOALS, TWO LAYERS.** "Clean" is born **upstream**, by construction:
> each section subagent authors *our own* clean JSX + utility/local CSS from the
> captured data — it NEVER pastes raw Shopify markup — over a deduped global
> cleaned stylesheet, and the **fingerprint gate** enforces zero source
> fingerprints. "Pixel-perfect" is enforced **downstream**: SSIM against the
> captured reference rasters (Layer 4). The two goals live in different layers, so
> they never fight over the same artifact. Both are *measured gates*, not matters
> of diligence.

All `pwc4` tools return `{"ok": bool, ...}` (build tools use `{"success": ...}`).
Always check that flag and read `error` / `errors` before proceeding. Never
fabricate a result you did not get back from a tool.

> **Default route vs. the experimental IR route.** The route below
> (extract → plan sections → assemble shell → per-section subagents → build →
> gates) is the **default and only supported delivery path** — it is what produces
> high fidelity on real pages. The IR→codegen tools (`build_ir`,
> `run_recognizers`, `generate_code`) are **experimental and OFF the default
> path**: on real pages the multi-MB DOM cannot transit MCP context and codegen
> currently emits empty shells. Do not route delivery through them unless you are
> deliberately doing IR R&D. See the decision log in `docs/delivery-strategy.md`.

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
- The `summary` now carries **`site_classification`** (`site_type` +
  `can_clone_well` + a human `ceiling` advisory). **If `can_clone_well` is false**
  (a `webgl_canvas` or `scroll_choreography` site whose visuals live in a runtime
  layer), **tell the user the ceiling up front** — you can faithfully recover the
  content but NOT the runtime-drawn/animated *look*. Do not promise pixel-perfect
  fidelity on these. It also carries **`capture_residuals`** (e.g. significant
  `<canvas>` main visuals) — surface them; never silently drop them.
- **Capture completeness is upstream of everything.** Lazy images
  (`data-src`/`srcset`/`{width}` templates), theme-relative fonts, and overlay
  dismissal must be complete here — a fidelity gap you can't fix downstream starts
  as a capture gap here. (Hardening tracked as Plan 1 in the strategy doc.)
- If `ok` is false (bad URL, page won't load), report the error and stop. Do not
  guess at page content you never extracted.

---

## Phase 2 — Plan sections (by the real `#main` children)

Call **`pwc4 get_section_plan(source_id)`**.

- Returns the ordered section list — split by the page's **real `#main`
  children**, not an arbitrary chunker. Each entry has a section id/name and its
  source bbox/`bounds` (used later to map a failing raster band back to the
  section that owns it).
- This list is the unit of work: one section → one component → one subagent.
- Record the order; `assemble_project` writes the shell in exactly this order.

---

## Phase 3 — Assemble the shell FIRST (deterministic)

Call **`pwc4 assemble_project(source_id)`** **before** filling sections.

- This is the ONLY thing that writes the shared files (`App.jsx`, `index.css`,
  routing) and **creates the sandbox** — section files are written *into* the
  shell it creates, so it must run first. (This order is the reverse of older
  drafts; follow this one.)
- It seeds `index.css` with the Tailwind layers and emits the **deduped global
  cleaned stylesheet** for the whole page as a static **`public/theme.css`**
  linked from `index.html` (`<link rel="stylesheet" href="/theme.css">`), so
  sections render styled rather than blank. (This is the P0 wiring; older drafts
  injected it into `index.css` directly — the `public/theme.css` + `<link>` form
  is current. Per-section local CSS from Phase 4 remains the fallback.)
- It will report `missing_section_files` for every planned section — expected at
  this point, because the subagents fill them in Phase 4.

---

## Phase 4 — Per-section subagents author clean components

For **each** section in the plan, dispatch a subagent. Each subagent owns exactly
one section, writes only its own namespaced file, and works like this:

1. **`pwc4 get_section_data(source_id, section_id)`** — pull that section's DOM
   subtree, computed styles / `css_rules`, geometry, content, and asset refs.
2. **Author clean JSX + local styles from that data.** Write *our own* component
   — semantic element + Tailwind utilities + a small local stylesheet derived from
   `css_rules`. **Never paste raw Shopify markup, class names, or `original.css`.**
   This is where "clean" is born by construction.
3. **`pwc4 sandbox_write_file(path, content)`** — write the component into its
   namespaced path in the shell.

**Section authoring rules (these encode R6–R9 — get them right at authoring
time, not as an afterthought):**
- **sticky** — if the source element is `position:sticky`, keep it sticky and
  ensure no ancestor clips overflow (no `overflow:hidden` on a containing block),
  so it keeps following scroll.
- **footer** — capture the explicit grid/flex container props (columns, gap) so
  the footer can't disassemble; reconstruct columns from child bboxes if needed.
- **reviews** — rebuild reviews as a **data-driven component from the extracted
  review data** (judge.me / loox / yotpo / okendo). NEVER ship a static PNG of the
  widget.
- **video** — localize the media and emit a real `<video>`/player; promote lazy
  `data-src` → `src`. Never leave a hotlink or a popup snapshot in place.
- **captured `display:none` state** — prefer **revealing** lazy/hidden content
  (e.g. product grids the theme hid at capture time) over faithfully shipping an
  empty band; that is closer to the real site. Be consistent across sections.

Dispatch sections **concurrently** when independent. A subagent that can't resolve
an asset records it (a residual to surface), never invents one.

---

## Phase 5 — Build (deterministic, hard gate)

1. Re-run **`pwc4 assemble_project(source_id)`** to confirm nothing is missing —
   `ok` is true only when `missing_section_files` is empty. If a component is
   missing, finish that section (Phase 4) and re-assemble. Do not advance with
   missing components.
2. **`pwc4 build_project()`** — runs `npm run build`. **`success` MUST be true**
   (exit code 0 *and* a `dist/` produced). If false, read `errors`/`stderr_tail`,
   locate the cause, fix the offending **section component**, and rebuild.
   Optionally use **`pwc4 get_build_errors()` / `pwc4 diagnose()`** for the
   three-layer (terminal / browser / static) breakdown. **The build must pass
   before verify — this is a hard gate.**

---

## Phase 6 — Verify (Layer 4: the gate-driven self-heal loop)

This loop is the heart of v4. It replaces eyeball judgement with **measured
gates**. Because the architecture guarantees a clean, pixel-identical equivalent
*exists*, this is a closed search that converges: build clean candidate → measure
raster distance → repair the worst region → re-measure.

### The three deterministic gates (run every iteration)

1. **`pwc4 check_fingerprints(dist_dir)`** (R1) — `ok` iff `total == 0` Shopify
   traces (`shopify`, `myshopify`, `template--…__`, `data-shopify*`,
   `original.css`, `shopify-section`) in `dist/`. Read `by_pattern` / `files` to
   see exactly what leaked.
2. **`pwc4 check_weight(dist_dir, budget_kb)`** (R3) — now reports **separate
   code and asset budgets**: `code_kb`/`code_ok` (html+css+js+svg gzipped, target
   50–80 KB) and `asset_kb`/`asset_ok` (images/fonts/video raw; only fails when
   you pass `asset_budget_kb`). `ok` = `code_ok` ∧ `asset_ok`, so an image-heavy
   store no longer false-fails on content weight when its code is clean. Read
   `code_ok` for the real "is the code lightweight" judgment.
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
2. **Map region → section component.** Use the worst band's `y0`/`y1` against the
   section `bounds` from the Phase-2 plan to find the section that owns it.
   `bounds` are now filled from the captured DOM geometry (`section_geometry`),
   so this mapping works directly. (If a section still has empty `bounds` — no
   geometric match was found — fall back to matching the band against the rendered
   section order manually.)
3. **Repair THAT section component.** This is your act of judgement: given (the
   diff/region, the section's component + captured data + computed style, the gate
   evidence), decide how to fix that single component — adjust its layout / style /
   tokens / asset wiring, or correct a sticky/footer/reviews/video mistake. Edit
   that one section component, never a wall of raw source.
4. **Rebuild** (Phase 5) just what changed.
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
  residual (which gate, which region/section, the measured score vs τ) explicitly
  to the user. Long-tail items (bespoke frame-by-frame animation, WebGL) are
  flagged fallbacks, never silently dropped.

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
| 2 Plan | `get_section_plan(source_id)` |
| 3 Assemble shell | `assemble_project(source_id)` |
| 4 Per-section | `get_section_data(source_id, section_id)`, `sandbox_write_file(path, content)` |
| 5 Build | `assemble_project(source_id)`, `build_project()`, `get_build_errors()`, `diagnose()` |
| 6 Verify (gates) | `check_fingerprints(dist_dir)`, `check_weight(dist_dir, budget_kb)`, `score_fidelity(ref_png, cand_png, threshold)`, `compare_to_baseline(ref_png, new_png, baseline_png)`, `preview_screenshot(...)` |
| 7 Deliver | (default: `dist/`) — optional deploy |
| — Experimental (OFF default path) | `build_ir`, `run_recognizers`, `generate_code` |

## Invariants (do not violate)

- **The iron rule:** `pwc4` tools never call an LLM. The brain's judgement is in
  two places only — per-section authoring (Phase 4) and the Layer-4 repair
  decision (Phase 6); repair edits one section component, never raw source.
- **Clean is born upstream, by construction.** Each section subagent authors our
  own clean JSX from the captured data over a global cleaned stylesheet — it never
  pastes Shopify markup, class names, or `original.css`. The fingerprint gate
  enforces zero source fingerprints.
- **Gates, not vibes.** Acceptance = `check_fingerprints` ∧ `check_weight` ∧
  `score_fidelity` (∧ `compare_to_baseline` where a baseline exists), all green.
- **Scope boundary:** the tool targets *visual* fidelity of interactive elements
  in their captured states; full interactive behavior (accordions, variant
  switching, timers) is the user's own to wire up.
- The self-heal loop has a hard iteration cap (5 per breakpoint × state) and a
  no-progress guard — never loop forever. Residuals are reported, never silent.
- `npm run build` must pass before verify; the built artifact is what the gates
  measure.
- Never deploy unless explicitly asked.
- Both goals are joint and non-negotiable: cleanest-possible code AND
  pixel-perfect fidelity, each enforced as a measured gate.
- The IR→codegen tools are experimental and OFF the default delivery path.
