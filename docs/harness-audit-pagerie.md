# pwc4 Harness Audit — pagerie.com (2026-06-26)

Durable record of the multi-agent harness audit + the fidelity-measurement and
interaction-layer findings. Companion to `docs/delivery-strategy.html` (the living
strategy doc) and the `pwc4-architecture-pivot` memory.

---

## How this was produced
A **Workflow** (16 agents) cloned pagerie.com section-by-section via the pwc4 MCP
tools and each agent logged harness friction → a synthesis agent produced a
prioritized optimization list. **Caveat:** the MCP server ran the *pre-branch*
(stale) code, so the audit reflects the **old harness on `main`** — which is why it
independently rediscovered the very gaps the `feat/capture-completeness` branch
already fixes (validation), and surfaces the ones still open.

Build/gates of the workflow's clone (old harness): build OK, 13/13 sections, but
**R1 FAILS (80 shopify fingerprints)** and **R3 FAILS hard (4.75 MB; images 4.6 MB
unoptimized + JS 121 KB)**.

---

## ⚠ Biggest finding: the fidelity metric itself is broken
Ran real SSIM of three clones vs the live site (top popup band masked):

| clone | visual quality | full-page SSIM |
|---|---|---|
| workflow (old harness, 37505px, broken) | worst | **0.84 ← highest** |
| my v4 (new-code branch, 8776px, clean) | good | 0.38 |
| user's `showcase/products/pagerie` (best) | best | **0.33 ← lowest** |

**The visually-broken clone scores highest; the best clone scores lowest.** So
**full-page SSIM cannot rank clones.** Two root causes (same Goodhart trap logged
for oryzo): (1) it resizes pages of very different heights to 256² → vertical
content positions no longer align → it compares colour blocks, not "looks like";
(2) the **reference raster is defective** (popup + un-loaded hero leave large blank
areas), so it rewards clones whose blanks match.

**Consequence:** the fidelity gate is untrustworthy until there is (a) a CLEAN
reference raster (popup dismissed + hero loaded) and (b) **per-section,
bounds-aligned** comparison instead of full-page squish — which is blocked on the
missing `bounds` (below). Until then every "pixel-level" number is self-deception.

---

## Biggest missing capability: an interaction layer
The user's good clone (`showcase/products/pagerie`) is *alive* only because of a
hand-written `src/interactions.js` (~194 lines) that reimplements the live site's
behaviours from captured signatures: **Flickity carousels (translateX slide +
autoplay + dots + drag from `data-flickity-config`), lazy fade-in, product
hover-swap, sticky header, search/cart/menu drawers, the $100 popup** — booted
*after* React mounts (polls `.pwc-footer`). The pwc4 harness ships a **dead static
snapshot** (audit: 0/79 scripts captured, 73 animations dropped). **The harness has
no interaction stage.** `interactions.js` is the reference for what a
`recognizers → runtime interaction layer` stage should generate.

---

## Prioritized harness optimizations (from the 16-agent synthesis)
🟢 = already fixed on `feat/capture-completeness`; 🔴 = still open.

1. **🔴 P1 — always emit numeric `bounds {x,y,w,h}` per section** (12/13 were `{}`).
   Silently disables self-heal AND all per-section fidelity scoring. **Unblocks the
   trustworthy metric above. Do first.**
2. 🟢 P1 — follow lazy-load `data-src`/`srcset`/`{width}`/`noscript` + download real
   images (Plan 1 + Task A; v4 hero image still partially missing → finish).
3. 🟢 P1 — scrub shopify fingerprints (defingerprint; the 80 are stale-code).
4. 🟢 P2 — de-dup `css_rules` + hoist global theme CSS once (P0 theme.css).
5. 🟡 P2 — normalize JS-gated hidden states + add a `hidden_reason` flag (partial:
   page-level rest-state override done; per-container reveal + flag open).
6. **🔴 P2 — asset-optimization stage** (resize/re-encode images to WebP/AVIF) +
   split JS (`manualChunks`) → fixes the 4.6 MB R3 weight fail.
7. 🟢 P3 — capture + localize fonts with a manifest (Plan 1).
8. **🔴 P3 — planner: drop empty/junk containers** (empty `shopify-section-popup`
   became a component) **+ classify overlay/chrome sections** (drawers as sections).
9. **🔴 P3 — keep id-scoped CSS selectors in sync** when codegen renames namespaces.
10. **🔴 P4 — make `images[]` self-sufficient** (resolved `src` + stable DOM key).
11. 🟢 P4 — auto HTML→JSX in codegen (phase 2 `html_to_jsx`).
12. **🔴 P4 — semantic recognizers** for carousels / form widgets → the interaction
    layer above.
13. **🔴 P5 — sanitize malformed CSS** (empty decls, trailing-comma selectors).
14. **🔴 P5 — `sandbox_write_file` staged-path** for large sections (footer 52 KB had
    to bypass the gate via `sandbox_exec`).

---

## Proof the branch fixes work end-to-end
Rebuilt pagerie with the **new branch code** (P0 theme.css + html_to_jsx + localize
+ defingerprint) → `showcase/products/pagerie-v4`, served at a local port:
page height **8776px** (original 8168) vs the old harness's **37505px** (4.6×
bloat). Nav, hero, fonts, layout correct, **no popup baked in**. Remaining visible
gap: hero/some product images not downloaded (open item #2/#6).

---

## Recommended next order (each unlocks the next)
1. **`bounds`** → unlocks per-section aligned SSIM.
2. **clean reference raster** (popup dismissed + hero forced-loaded) → metric becomes meaningful.
3. **interaction-layer recognizers** (model on `interactions.js`) → clone stops being dead.
4. **asset-optimization stage** + finish lazy-image capture → pass R3, fix hero image.
