---
name: perfect-web-clone-v3
description: >-
  Clone any live web page into a deployable Vite + React + Tailwind static
  project at the highest achievable visual fidelity. Drives the deterministic
  `pwc3` MCP tools through a seven-phase pipeline: extract the page, split it
  into sections, fan out one Task sub-agent per section to reproduce it in
  isolation, deterministically assemble the project, then run a screenshot-vs-
  original verify-loop in dev and again against the production build before
  delivering `dist/`. Use whenever the user wants to clone, copy, replicate,
  or "rebuild this site" from a URL. The North Star is replication fidelity:
  every decision is judged by "does it look more like the original?"
---

# Perfect Web Clone v3 — The Cloning Playbook

You are the brain. The `pwc3` MCP tools are pure, deterministic hands and eyes:
they extract, plan, write the sandbox, execute, screenshot, build, and diagnose.
**No tool ever calls an LLM.** Every act of thinking — writing components,
judging "does this look like the original?", deciding what to fix — is *yours*.

> **NORTH STAR: replication fidelity.** Deployment is not a goal; a deployable
> `dist/` is merely the byproduct of having cloned the page well enough. When two
> options conflict, always pick the one that makes the clone look more like the
> original.

All `pwc3` tools return `{"ok": bool, ...}` (build tools use `{"success": ...}`).
Always check that flag and read the `error` / `errors` before proceeding. Never
fabricate a result you did not get back from a tool.

---

## Phase 0 — Frame the job

1. Confirm the target URL with the user. If they gave a vague request
   ("clone this"), get the exact URL.
2. Confirm scope: full-page clone is the default. Note any explicit asks
   (e.g. "also give me a Dockerfile", "deploy it").
3. **Deployment is opt-in.** Do NOT call `deploy` unless the user explicitly
   asks to put it online. Default delivery is the local `dist/` bundle.

---

## Phase 1 — Extract

Call **`pwc3 extract_page(url, options)`**.

- Returns `source_id` + a `summary`. **Record `source_id`** — it threads through
  every later phase.
- If `ok` is false (bad URL, page won't load), report the error to the user and
  stop. Do not guess at page content you never extracted.
- Read the summary so you understand what you're about to clone (title, themes,
  rough size).

---

## Phase 2 — Section plan (the v2 ace, preserved as a tool)

Call **`pwc3 get_section_plan(source_id)`**.

- Returns `section_count` and a `sections[]` list. Each section carries the
  fields you will hand to its sub-agent: `name`, `namespace`, `component_name`,
  `section_type`, `base_path` (= `src/components/sections/{namespace}/`),
  `component_path`, `bounds`, `order`, `counts`, and a `task_description`.
- **Do not re-plan, merge, or split sections yourself.** The plan is
  deterministic and is the contract the assembler expects. Treat it as ground
  truth for "how many sub-agents" and "what each one owns."

---

## Phase 3 — Parallel reproduction (one Task sub-agent per section)

This is where the fan-out happens. **Spawn exactly one native `Task` sub-agent
per section** in the plan (`section_count` sub-agents total). Dispatch them in
parallel.

### Hard constraints for every section sub-agent (state these in its prompt)

1. **Data first, always.** The sub-agent MUST call
   **`pwc3 get_section_data(source_id, name)`** for its own `name` *before*
   writing any code. It builds the component from the returned section data
   (DOM/CSS/assets/bounds), not from imagination.
2. **Stay in your lane.** The sub-agent may ONLY write under its own
   `src/components/sections/{namespace}/` via
   **`pwc3 sandbox_write_file(path, content)`**. The tool enforces this: an
   out-of-namespace write is *rejected* and returns `{"ok": False, "error": ...}`.
   If a sub-agent gets rejected, that is a bug in the sub-agent — it must correct
   the path, never try to write shared files.
3. **Never touch shared files.** `App.jsx`, `main.jsx`, `index.css`,
   `package.json`, routing — all of these belong to the deterministic assembler
   in Phase 4. Sub-agents do not create or edit them.
4. **Tech stack:** React function component + Tailwind utility classes,
   reproducing the extracted CSS as faithfully as possible. The component file
   name and path come from the plan (`component_name`, `component_path`).
5. **Fidelity over cleverness.** The sub-agent's job is to look like the
   original section, not to write elegant abstractions. Match layout, spacing,
   typography, colors, and responsive behavior from the extracted data.
6. **Real links only — never fabricate.** Every anchor MUST use its real `href`
   from the section data's `links` array (and the real hrefs in `raw_html`).
   `#`, `javascript:void(0)`, empty, and invented URLs are FORBIDDEN. If the
   original linked to `/policies/refund-policy`, the clone links there too. The
   deterministic `verify_links` gate (Phase 4) rejects any section that dropped a
   real link, and that section gets re-dispatched — so get it right the first time.
7. **Real interaction & animation from `css_rules`.** `get_section_data` returns
   a `css_rules` string carrying the section's REAL `:hover`/`:focus` states,
   `@keyframes` animations, `transition`s, and `@media` breakpoints. Reproduce
   them faithfully (Tailwind `hover:`/`md:`/`animate-[…]` or a small scoped
   stylesheet) — do NOT approximate or omit interaction, animation, and
   responsive behavior when the real CSS for it was handed to you.
8. **Local assets, never hotlink.** Each entry in the section's `images` carries
   a `local_url` (e.g. `/assets/images/foo.png`) when the asset was downloaded.
   Use `local_url` for the `src`/`srcset` — do NOT reference the remote `url`
   when a `local_url` exists (hotlinking breaks on hosts that refuse, like Loox).
   For an image with `local_url: null` (download was refused), use the remote
   `url` BUT add an `onError` fallback that hides the broken image or swaps in a
   neutral placeholder — never leave a broken-image icon. `verify_assets`
   (Phase 4) rejects sections that hotlink an asset that had a local copy.
9. **No live third-party embeds — use the crawl-time snapshot.** Cross-origin
   widget `<iframe>`s (Loox reviews, chat, maps, YouTube) cannot work in a clone
   (the provider serves only the authorized origin → "refused to connect"). The
   extractor screenshots each such widget *while on the live page* (where it
   renders); the section data then replaces the iframe with an `<img
   class="pwc-embed-snapshot">` of that snapshot — a faithful static stand-in for
   what the visitor saw. When no snapshot exists it falls back to a sized
   `pwc-embed-placeholder`. Keep whichever the data gives you; NEVER reintroduce
   the live cross-origin iframe.

### What you (the orchestrator) do here

- Hand each sub-agent: its `source_id`, its section `name`/`namespace`, the
  `component_path` it must write, and the constraints above.
- Wait for all sub-agents to finish. Collect which ones reported success.
- If a sub-agent fails or refuses to write its file, re-dispatch that one
  section only.

---

## Phase 4 — Assemble (deterministic)

Call **`pwc3 assemble_project(source_id)`**.

- This is the ONLY thing that writes the shared files (`App.jsx`, `index.css`,
  routing) — deterministically, in section `order`.
- Read the return: `written_files`, `expected_section_files`, and crucially
  **`missing_section_files`**. `ok` is true only when nothing is missing.
- **Structural gate:** if `missing_section_files` is non-empty, a sub-agent
  failed to produce its component. Re-dispatch a Task sub-agent for each missing
  section (Phase 3 rules), then call `assemble_project` again. Do not advance to
  preview with missing components.

### Link-fidelity gate — `verify_links(source_id)`

After assembly succeeds, call **`pwc3 verify_links(source_id)`**. This is a
deterministic check (no LLM) that every section kept its REAL links instead of
fabricating `#`/`javascript:` placeholders.

- Read `ok`. When true, every section preserved its real navigational links —
  proceed to Phase 5.
- When false, **re-dispatch a Task sub-agent for each section in `failing` and
  `unreadable`** (Phase 3 rules — emphasize constraint 6, real links only). Each
  `failing` entry tells you exactly what was dropped (`missing` = the real link
  URLs, `placeholder_count` = how many fake hrefs it wrote). Re-run
  `verify_links` until `ok` is true. Fabricated links are a fidelity failure, not
  a cosmetic one — do not advance with `failing` sections.

### Local-asset gate — `verify_assets(source_id)`

`assemble_project` copies the downloaded assets into `public/assets/`. Call
**`pwc3 verify_assets(source_id)`** to confirm every section actually references
those local copies instead of hotlinking.

- `ok` true → assets are self-contained; proceed to Phase 5.
- `ok` false → re-dispatch each `failing`/`unreadable` section (Phase 3,
  constraint 8). Each `failing` entry lists `hotlinked` (remote URLs it should
  have localized) and `missing` (local paths it dropped). Re-run until `ok`.

---

## Phase 5 — Dev preview verify-loop (the fidelity engine)

This loop is the heart of v3 and where you spend the most effort. The engine is
not the framework — it is **screenshot → compare to original → locate the
section → fix → screenshot again.**

### Enter the loop

1. **`pwc3 start_preview()`** → starts the Vite dev server, returns a `url`.
   If it fails, read `stderr`, fix the cause (often a missing import surfaced by
   a section component), and retry.
2. **`pwc3 preview_status()`** → confirm `has_error` is false before judging
   visuals. If `has_error` is true, read `error_message`, fix it (locate the
   offending section), and re-check. A runtime error means you are not allowed
   to judge "close enough" yet.

### Each iteration

3. **`pwc3 preview_screenshot(...)`** for **each viewport** the loop must cover:
   capture **desktop and mobile** separately. The original was extracted at both;
   compare like-for-like.
4. Visually diff each viewport's screenshot against the corresponding original.
   **You** are the judge of fidelity. For every deviation, **localize it to a
   specific section** (use the section `bounds`/`order` to map a pixel region to
   a `namespace`).
5. Fix by re-dispatching a Task sub-agent for *only the offending section*
   (same Phase 3 constraints — data first, own namespace only), or make a
   targeted correction. Then loop back to step 3.

### "Close enough" — the fidelity standard

A clone is close enough when, per viewport:

- **Layout & structure** match: section order, presence, and overall page
  composition are correct; nothing is missing or duplicated.
- **Spacing & sizing** are visually indistinguishable at a normal glance —
  no obviously wrong margins, paddings, or element widths.
- **Typography** matches: font family/feel, weight, size hierarchy, line
  height read the same.
- **Color & theming** match: backgrounds, text, accents, borders; the right
  theme (light/dark) renders.
- **Imagery & key assets** are present and correctly placed.
- **Responsive behavior** is correct: the mobile screenshot reflows like the
  original's mobile, not a squeezed desktop.

Cosmetic sub-pixel differences and non-reproducible dynamic content (live feeds,
randomized data) do NOT block acceptance. **Structural/layout/typography/color
mismatches DO block** — keep iterating on those.

### Exit / stop criteria (no infinite loops)

- **Exit (success):** every covered viewport meets the "close enough" standard
  AND `preview_status().has_error` is false.
- **Iteration cap: at most 5 verify-loop iterations per viewport.** If you hit
  the cap with deviations remaining, STOP looping. Record the residual
  differences, report them honestly to the user, and proceed to Phase 6 with the
  best result — do not loop forever chasing diminishing returns.
- **No-progress guard:** if an iteration produces no visible improvement over the
  previous one, stop early rather than spending the remaining budget; re-examine
  whether the deviation is reproducible at all.

---

## Phase 6 — Production self-check (build, then re-verify)

A page that looks right in dev but breaks in the production build is a failed
clone. Guard against "dev looks good, build is broken."

1. **`pwc3 build_project()`** → runs `npm run build`. **`success` MUST be true**
   (exit code 0 *and* a `dist/` produced). If false, read `errors` /
   `stderr_tail`, locate the cause (often a section component), fix it
   (re-dispatch that section's sub-agent if needed), and rebuild. Optionally use
   **`pwc3 get_build_errors()`** / **`pwc3 diagnose()`** for the three-layer
   (terminal / browser / static) error breakdown. **The build must pass before
   delivery — this is a hard gate.**
2. **Re-screenshot the build output.** Serve/preview the produced `dist/` and
   take desktop + mobile screenshots, then confirm they match the dev
   screenshots (and the original). If the build artifact diverges from dev,
   that divergence is a real defect — fix and rebuild.
   - Apply the same iteration cap here: do not loop indefinitely on the
     build-vs-dev comparison.

**Production gate (all three layers must be green before delivery):**

1. **Structural:** sub-agent count == section count; every section produced its
   file; `assemble_project().missing_section_files` is empty; `verify_links`
   reports `ok` (no fabricated/dropped links); `verify_assets` reports `ok`
   (local assets, no hotlinks); `build` has no errors.
2. **Visual:** dev screenshots meet the "close enough" standard per viewport
   (or residual deltas are documented and accepted).
3. **Production:** `npm run build` exit code 0 AND the build-artifact
   screenshots match the dev screenshots.

---

## Phase 7 — Deliver

- **Default:** deliver the deployable static bundle `dist/` (in the sandbox /
  exportable locally). If the user asked for it, also produce a `Dockerfile`
  (nginx). Tell the user where `dist/` is and summarize the fidelity result,
  including any residual deviations you accepted at the iteration cap.
- **Deploy is opt-in and low-priority.** Only if the user explicitly asked to
  put it online, call **`pwc3 deploy(target)`** (Cloudflare Pages / `wrangler`
  only — no Vercel) and return the live URL. **Never deploy by default.**

---

## Tool quick-reference (all `pwc3`, all deterministic, zero LLM)

| Phase | Tool |
|---|---|
| 1 Extract | `extract_page(url, options)` |
| 2 Plan | `get_section_plan(source_id)` |
| 3 Reproduce | `get_section_data(source_id, name)`, `sandbox_write_file(path, content)`, `sandbox_read_file`, `sandbox_list_files`, `sandbox_exec` |
| 4 Assemble | `assemble_project(source_id)`, `verify_links(source_id)`, `verify_assets(source_id)` |
| 5 Dev verify | `start_preview()`, `preview_status()`, `preview_screenshot(...)` |
| 6 Build verify | `build_project()`, `get_build_errors()`, `diagnose()` |
| 7 Deliver | (default: `dist/`) — optional `deploy(target)` |

## Invariants (do not violate)

- One Task sub-agent per section; sub-agents call `get_section_data` before
  generating and write only their own `sections/{namespace}/`.
- **Real links, real interaction, and local assets are not optional.** Anchors
  use the real hrefs from `links`; `:hover`/animation/`@media` come from the
  section's `css_rules`; images use `local_url` (downloaded copies), never
  hotlinks. `verify_links` AND `verify_assets` must report `ok` before Phase 5.
- Shared files are written exclusively by `assemble_project`.
- The verify-loop has a hard iteration cap (5 per viewport) and explicit
  exit criteria — never loop forever.
- `npm run build` must pass and the build artifact must be re-verified before
  delivery.
- Never deploy unless explicitly asked.
- Fidelity is the North Star: when in doubt, do whatever makes the clone look
  more like the original.
