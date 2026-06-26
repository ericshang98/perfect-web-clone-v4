# Perfect Web Clone v4 — System Architecture

> **Status:** Design of record for the v4 rewrite. Forked from v3 on 2026-06-23.
> **Driver:** The Jose Gallardo engagement (see `docs/requirements.md`). Two non-negotiable,
> simultaneous requirements: **cleanest-possible code** AND **pixel-perfect visual fidelity**,
> produced by an **automated, paste-a-URL tool** across any product/landing page.

> **★ North star.** Every requirement must first become a **deterministic, evidence-backed
> gate**, then be satisfied — never by "looks close enough." The guiding philosophy (four
> pillars), the delivery contract, the decision log, and the live roadmap are consolidated in
> **`docs/delivery-strategy.md`** — read it first; this file is the deeper architecture behind it.

> **⚠ Default-route pivot (2026-06-26).** The **delivery path is the subagent-by-section route**
> (extract → plan sections by real `#main` children → assemble shell → per-section subagents author
> clean JSX → build → gates), per `skill/SKILL.md`. The **IR→codegen layers (1–3) below are
> demoted to experimental** R&D: on real pages the multi-MB DOM cannot transit MCP context and
> codegen currently emits empty shells. **Everything else in this document still holds** — the
> feasibility argument (§1), the requirement→gate mapping (§2), and the Layer-4 gate-driven
> self-heal loop are unchanged; only the *candidate-generation* mechanism changed from
> deterministic codegen to subagent authoring. See the decision log in `docs/delivery-strategy.md`.

---

## 0. Why v4 exists

v3 proved the **CC-as-brain / deterministic-MCP-as-hands** model and the
**chunk → reproduce-per-section → assemble → verify** loop. It works, and it is the right
skeleton. But the build delivered to the client still failed a technical code review:

- `shopify` appeared **70×**; **357** Shopify template refs (`template--20593513300135__main`);
- **64** blocks of raw inline CSS totalling **225 KB**, all on Shopify style variables;
- an `original.css` file was loaded; page weight **510 KB** (target: 50–80 KB);
- sticky element stopped following scroll; footer disassembled; reviews widget rendered as a
  static image; videos missing entirely.

The root cause is **not** that v3 is careless. It is **architectural**: v3's "intermediate
representation" is *real cleaned HTML + a critical-CSS string*, and the HTML→React conversion is
done **by hand inside a per-section subagent**. That design **couples fidelity to the source
representation** — the fastest way for a subagent to be faithful is to paste the original markup
and CSS, Shopify class names and all. Cleanliness then has to be *cleaned back out*, which never
fully happens.

**v4's thesis:** decouple the two goals into different layers, and make each goal a *measured
gate* rather than a matter of subagent diligence.

This document is the systematic architecture for doing that. It is grounded in the actual v3
code map (see `docs/v3-architecture-map.md`).

---

## 1. First-principles feasibility (can this even be done?)

Yes — with one honest boundary. The reasoning:

### 1.1 Rendering is many-to-one
A page is a function `render(DOM, CSS, assets, viewport, JS-state) → 2D pixel raster`. The map
from **source → raster is many-to-one**: infinitely many distinct HTML/CSS sources render to the
identical raster. Therefore **"same pixels" does not require "same source."** Shopify fingerprints
are an artifact of choosing the lazy inverse (copy the source), not a necessity. A clean source
that renders pixel-identically is **guaranteed to exist**. The problem reduces from *"is it
possible"* to *"can the tool find that clean source reliably"* — a search/inversion problem.

### 1.2 Split the page into two layers
- **Static visual layer** — determined entirely by **computed styles + geometry + content +
  assets**. Computed styles are *resolved* values (no Shopify variables, no cascade mystery).
  Inverting computed-style → clean CSS is a **solved-in-principle** problem. → *Static
  pixel-perfect + clean code is fully achievable.*
- **Behavioral layer** — arbitrary JS. Reproducing *all* interactive states means inverting an
  arbitrary program, which is **undecidable in general**. **But** real marketing/e-commerce pages
  draw on a **small, finite vocabulary** of behaviors (sticky, carousel, accordion,
  reveal-on-scroll, sticky-add-to-cart, video, reviews). The distribution has a **fat, coverable
  head and a thin tail.**

### 1.3 Feasibility is set by how "pixel-perfect" is *contracted*
- "Pixel-perfect" = *identical raster at N breakpoints × M observable states* → **finite,
  verifiable, achievable.**
- "Pixel-perfect" = *identical under every possible interaction and animation frame* → **open-ended,
  uncertifiable** by any tool (or human rewrite).
- → v4 pins the spec to **observable rendered states** (a finite set of breakpoint × interaction
  screenshots). This is exactly what the acceptance gate measures.

### 1.4 The loop converges because the target exists
Because §1.1 guarantees a clean equivalent exists, v4 does **not** need a perfect one-shot
inverter. It needs: `generate clean candidate → measure raster distance to reference → repair the
worst region → re-measure`. A known, reachable target turns open synthesis into a **closed search
that converges**.

### 1.5 Verdict
For Jose's sites (standard Shopify/landing pages) the work sits **squarely in the coverable head**:
static layer is fully invertible; his four flagged behaviors are all head-of-distribution
recognizers. **Clean + pixel-perfect together is an engineering problem, not a possibility
problem.** The residual long tail (bespoke frame-by-frame animation, WebGL) is handled by an
explicit, flagged fallback — never silently.

---

## 2. Requirements → measurable gates

Every requirement becomes a **deterministic gate** (a tool that returns pass/fail + evidence). No
gate is judged by vibes.

| # | Requirement (source) | Gate | Pass condition |
|---|---|---|---|
| R1 | No Shopify fingerprints (Jose 6/21, 6/23) | `fingerprint_gate` | 0 occurrences of `shopify`, `myshopify`, `template--…__`, `data-shopify*`, `original.css`, `shopify-section` in `dist/` |
| R2 | Clean, readable code | `cleanliness_gate` | No raw inline `<style>` dumps > N bytes; CSS expressed as tokens + utility classes; one component per section |
| R3 | Lightweight & fast | `weight_gate` | `dist/` total transfer ≤ budget (default 120 KB gz, target 50–80 KB); LCP image lazy below fold |
| R4 | Pixel-perfect | `fidelity_gate` | SSIM ≥ τ (default 0.97) per breakpoint × state vs reference raster |
| R5 | Clearly better than current repo (Jose's acceptance, 6/13) | `comparison_gate` | New output fidelity score strictly > current-repo output, side by side, per reference URL |
| R6 | sticky follows scroll | `sticky` recognizer + fidelity in scrolled state | sticky element pinned in scrolled-state screenshot |
| R7 | footer intact | `footer` recognizer | footer region SSIM ≥ τ |
| R8 | reviews = real widget | `reviews` recognizer | reviews rebuilt as data-driven component, not a static PNG |
| R9 | videos present | `video` collector | every source `<video>`/embed localized & playing |

These gates are the contract. "Done" = all gates green on the agreed reference URLs
(reelshort.com/es, livora.co, kojeva.com, trykojiva.com/brush).

---

## 3. The layered pipeline

> **Current delivery mapping (2026-06-26):** Layers 1–3 (IR → recognizers → codegen) are the
> *intended* design but are **demoted to experimental**. In the shipping pipeline their job —
> turning captured section data into clean components — is done by **per-section subagents**
> (one subagent per real `#main` child, authoring clean JSX + local CSS over a deduped global
> cleaned stylesheet). Layer 0 (capture) and Layer 4 (gate-driven self-heal) are unchanged and
> remain the backbone. See `skill/SKILL.md` for the operational route.

```
Layer 0  CAPTURE (ground truth)                          [evolves core/extractor]
   • Playwright renders at every breakpoint (1440 / 768 / 375)
   • Captures: DOM + computed styles + box geometry + assets + fonts
   • Captures REFERENCE RASTERS per breakpoint × key state (initial, scrolled, hover/expanded)
   • Triggers lazy-load; collects video/iframe sources; dismisses overlays
   • Output: immutable Source — every downstream artifact is judged against its rasters
        │
        ▼
Layer 1  SEMANTIC IR (the new core)                      [NEW: core/ir/]
   • Normalize DOM+computed-styles into a framework-agnostic component tree (our vocabulary)
   • Node = { role, layout(flex/grid params), resolved style, content, children, source-bbox }
   • Normalization passes:
        - design-token extraction (colors, spacing scale, typography, radii, shadows)
        - CSS de-duplication (repeated decls → shared token/utility)
        - class-name normalization (drop shopify-section / template--…__main → semantic names)
        - repeated-structure detection (cards, list items) → reusable component
   • THIS is where "clean" is born: the page is described in OUR words, not Shopify's
        │
        ▼
Layer 2  RECOGNIZERS (pluggable registry)                [NEW: core/recognizers/]
   • Pattern-match IR subtrees → replace dumb subtree with a smart component spec
        - sticky-guard    : ensure no ancestor clips overflow; keep containing block
        - footer-rebuild  : capture grid/flex container props so footer can't disassemble
        - reviews         : detect judge.me/loox/yotpo/okendo → EXTRACT review DATA →
                            data-driven Reviews component (NOT a static PNG)
        - video-collector : <video>/<source>/youtube/vimeo/bg-video → localize media, real player
        - carousel/accordion/reveal : map to a small headless-lib component
   • Each recognizer is a plugin; coverage compounds over time. Long-tail → flagged fallback.
        │
        ▼
Layer 3  CLEAN CODEGEN                                    [NEW: core/codegen/]
   • Emit Vite+React+Tailwind FROM the IR (not from source HTML)
   • Tailwind utilities + design tokens from Layer 1; zero inline raw-CSS dumps; no original.css
   • Tree-shake, dedupe, lazy-load below-fold; one readable component per section
   • Clean BY CONSTRUCTION — there is no Shopify source text to leak
        │
        ▼
Layer 4  VERIFY + SELF-HEAL (closes the fidelity gap)    [evolves core/visual_diff + SKILL loop]
   • Render generated output at each breakpoint × state → raster
   • SSIM / region-diff vs Layer-0 reference → fidelity_gate
   • Run fingerprint_gate + weight_gate + cleanliness_gate (deterministic, tool side)
   • Where a gate fails: localize the region → hand (region, IR node, computed style, diff) to
     Claude Code → CC repairs THAT component in the IR → regenerate → re-measure
   • Loop until all gates green or iteration budget hit (then report residuals — never silent)
```

### 3.1 Division of labour (the iron rule is preserved)
- **Layers 0–3 and all gates are deterministic MCP tools — they NEVER call an LLM.** Capture,
  build IR, run recognizers, generate code, render, diff, score: pure Python.
- **Claude Code is the brain only in the Layer-4 repair decision**: given a diff + the offending
  IR node, decide *how* to fix that one component. This is the high-value judgement work, and it
  edits the IR/one component — never a wall of source.

This is the same philosophy as v3 (tools LLM-free), but the LLM's surface area shrinks from "write
every section by hand from raw HTML" to "repair flagged components against a measured diff."

---

## 4. How v4 evolves v3 (module-level)

| v3 today | v4 change |
|---|---|
| `core/extractor/` captures DOM+computed styles, single primary viewport + full-page shot | **Keep & extend:** capture **per-breakpoint** rasters and **key-state** rasters (scrolled/hover) as the reference set; add **video/media collection** (download `<video>`/`<source>`, resolve lazy `data-src`) |
| Section "IR" = real cleaned HTML + critical-CSS string (`sections_full.json`) | **Replace with `core/ir/`:** a normalized semantic tree + design tokens. The HTML still informs it, but output is generated from the IR, not the HTML |
| HTML→React done **by hand** in per-section subagents | **Replace with `core/codegen/`:** deterministic IR→React/Tailwind. Subagents shrink to *repair* duty only |
| `output_sanitizer.py` strips domain URLs, `.myshopify.com`, `data-shopify*` | **Extend into `fingerprint_gate`:** also kill `shopify-section`, `template--…__`, the word `shopify`, `original.css`; make it a **hard gate**, not a best-effort pass |
| `embed_handler.py` snapshots cross-origin widgets as **static PNG** (incl. reviews) | **Replace for reviews with `reviews` recognizer:** scrape review data → data-driven component. Keep PNG only as last-resort fallback, flagged |
| Videos **not downloaded** (hotlinked / placeholder) | **`video-collector` recognizer:** download + localize media, emit a real `<video>`/player |
| sticky/footer "treated as structural content" | **`sticky-guard` + `footer-rebuild` recognizers** |
| `visual_diff.py` 64×64 mean-abs-diff, informational; SKILL judges by eye, 5-iter cap, "document residuals" | **Upgrade to SSIM + region localization driving `fidelity_gate`;** wire the closed self-heal loop with explicit gate, not vibe judgement |
| no weight measurement | **`weight_gate`** on `dist/` transfer size |
| MCP server `pwc3`, 17 tools | **`pwc4`**, add tools: `build_ir`, `run_recognizers`, `generate_code`, `check_fingerprints`, `check_weight`, `score_fidelity`, `compare_to_baseline` |

Everything not listed (boxlite sandbox, contracts/isolation, assemble/build/deploy, Vite template,
the seven-phase skill spine) is **inherited from v3 unchanged**.

---

## 5. The Semantic IR (Layer 1) — the keystone

> **Experimental (2026-06-26).** This IR is the long-term design but is **not on the shipping
> path** — the multi-MB real-page DOM cannot transit MCP context to `build_ir`, and
> `generate_code` currently emits empty shells. It is retained as R&D toward a fully
> deterministic codegen; today the per-section subagents play the role described here (produce
> clean components in our vocabulary). The section below is the target design, not current
> behavior.

The IR is the **single stable contract**; every other layer reads/writes it, so each is swappable.

```jsonc
// core/ir/schema — one node
{
  "id": "n_0421",
  "role": "hero | nav | grid | card | footer | media | reviews | text | …",
  "tag": "section",                  // original tag, advisory only
  "layout": {                        // resolved from computed style
    "mode": "flex | grid | block | sticky | absolute",
    "direction": "row | column",
    "gap": "token.space.4",
    "columns": "repeat(2, 1fr)",     // for grid (fixes footer disassembly)
    "align": "...", "justify": "..."
  },
  "style": {                         // RESOLVED values → token refs where possible
    "color": "token.color.ink",
    "bg": "token.color.surface",
    "font": "token.type.body",
    "radius": "token.radius.md",
    "shadow": "token.shadow.sm",
    "position": "sticky", "top": "0px", "z": 30   // sticky-guard reads this
  },
  "content": { "text": "…", "imageRef": "asset_017", "href": "/products/…" },
  "component": null,                 // set by a recognizer, e.g. "Reviews", "VideoPlayer"
  "componentProps": {},              // recognizer-extracted data (e.g. review items)
  "sourceBBox": { "x":0,"y":1280,"w":1440,"h":620,"breakpoint":1440 },
  "children": [ /* … */ ]
}
```

Plus a document-level **design-token table** (`tokens.json`): colors, spacing scale, type ramp,
radii, shadows — deduplicated from the whole page. Codegen maps these to a Tailwind theme so the
output is utility-class-driven, not inline-CSS-driven (kills R1/R2/R3 at the root).

**Why this is the keystone:** "clean" is produced *here* (our vocabulary, deduped tokens, no
Shopify names) and "fidelity" is enforced *downstream* (Layer 4 against rasters). The two goals
never fight over the same artifact.

---

## 6. Acceptance & delivery flow

1. Run the pipeline on each agreed reference URL.
2. Gates per URL: `fingerprint_gate` ∧ `cleanliness_gate` ∧ `weight_gate` ∧ `fidelity_gate`
   (per breakpoint × state) ∧ `comparison_gate` (strictly better than current-repo baseline).
3. Milestone mapping to the contract (40/30/30):
   - **M1 (already passed):** single-URL "clearly better" side-by-side.
   - **M2 (30%):** working end-to-end pipeline — all four reference URLs pass `fingerprint`,
     `weight`, `fidelity` ≥ τ.
   - **M3 (30%, acceptance):** Jose's side-by-side "clearly better" on every reference URL.
4. Deliver `dist/` only (per standing no-deploy rule). Residual long-tail items are listed
   explicitly, never silently dropped.

---

## 7. Non-goals (explicit boundary)
- Reproducing arbitrary bespoke JS / WebGL / canvas choreography 1:1 (long tail → flagged
  fallback or hand-built, scoped separately).
- Interactive behavior Jose handles himself (accordions, variant switching, timers) — the tool
  aims for visual fidelity of these in their captured states, not full behavioral equivalence.
- Live data sync (inventory, comment threads) — a once-off snapshot.

---

## 8. Build order
See `docs/superpowers/plans/2026-06-23-pwc-v4-pipeline.md` for the task-by-task TDD plan. Summary
of the dependency spine: **IR schema (contract) → token extractor → IR builder → codegen → gates
(fingerprint/weight/fidelity) → recognizers (sticky/footer/reviews/video) → self-heal loop → MCP
wiring → SKILL update.**
