# pwc4 Interaction Layer + State-Checklist Contract — Design

> **Status:** Approved by Eric 2026-07-13 (verbal, after brainstorming).
> **Decisions locked:** ① "100% 复刻" = 状态清单合同制 (finite breakpoint × state × behavior
> checklist, item-by-item gated). ② Interaction layer is a **general harness capability**,
> validated first on Jose's 4 reference URLs (over-delivery vs contract, which lists
> interactions as Jose-handles-himself). ③ Production route = **Route C hybrid**:
> deterministic recognizers for head patterns, evidence-driven subagents for mid-tail,
> explicit flagged residuals for long tail; recurring B-channel patterns graduate into
> A-channel recognizers.

Companion docs: `docs/architecture.md` (v4 architecture, unchanged philosophy),
`docs/harness-audit-pagerie.md` (the audit that identified the missing interaction layer),
`docs/requirements.md` (Jose contract).

---

## 1. Product promise (upgraded)

> Paste a URL → the harness auto-generates that site's **state checklist**
> (breakpoints × interaction states × behaviors) → delivers a clean, **alive** React
> project that passes the checklist item-by-item, plus a reconciliation report.

"100%" means checklist pass-rate, never universe coverage. The checklist is born at
capture time, verified at gate time, and shipped with the deliverable.

Core iron rules preserved from v4:
- Tools are deterministic and **LLM-free**; Claude Code is the only brain.
- Every requirement is a gate with evidence, never "looks close enough".
- Long-tail items are **explicitly flagged, never silently dropped**.
- Extraction stays **strictly serial** (single MCP server; parallel extract deadlocks).
- Never deploy clones; deliver local `dist/` only.

## 2. Upgraded pipeline (7-step journey, widened at 3 points)

```
输入 URL
  ↓
① 采集真相＋交互探测      deterministic probes on original (scroll/hover/click)
   ├─ 参考截图（断点 × 状态）
   └─ ★ manifest.json（状态清单 = 本站验收合同）
  ↓
② 规划切分                sections from real #main children; each state attached to a section
  ↓
③ 生产（三通道分流）
   ├─ A 通道: recognizer hit → emit standard clean interaction component
   ├─ B 通道: no hit but evidence pack exists → subagent authors from evidence
   └─ 残差:   no evidence capturable (WebGL/bespoke) → flagged residual
  ↓
④ 组装构建                assemble shell + theme.css + Vite build (+ interaction runtime boot)
  ↓
⑤ 核销自愈闭环            replay every manifest state on the clone → per-state score
                          → repair worst failing item → rebuild → re-measure → green or budget
  ↓
交付 dist/ ＋ 核销报告     per-item pass/fail/waived + side-by-side evidence images
```

## 3. Interaction Manifest (`manifest.json`) — the contract artifact

One per site. Central contract read/written by capture, planner, producers, gate,
self-heal, and report.

```jsonc
{
  "url": "https://…",
  "breakpoints": [1440, 375],
  "generated_at": "…",
  "states": [
    {
      "id": "s_carousel_slide2",
      "section": "product-gallery",            // section id from the plan
      "breakpoint": 1440,
      "trigger": [                               // replayable on BOTH original and clone
        { "kind": "scroll", "y": 1200 },
        { "kind": "click", "target": ".dot:nth-child(2)" }
      ],
      "expect": { "ref": "refs/1440/s_carousel_slide2.png", "ssim": 0.97,
                   "bounds": {"x":0,"y":1100,"w":1440,"h":800} },
      "channel": "A:carousel",                  // "A:<recognizer>" | "B:evidence" | "residual"
      "evidence": "evidence/s_carousel_slide2/",
      "stability": "stable | unstable",         // unstable → masked regions in compare
      "status": "pending | pass | fail | waived"
    }
  ]
}
```

**Trigger vocabulary is deliberately tiny** — `scroll(y)`, `hover(target)`,
`click(target)`, `wait(ms)`, `viewport(w,h)`, and sequences thereof — because triggers
must replay deterministically on both original and clone. Anything not expressible in
this vocabulary is a residual by definition.

`waived` = explicitly agreed exemption (recorded, shown in report), the honest
alternative to silent dropping.

## 4. Capture probes (how the checklist is auto-generated)

Deterministic, LLM-free, run on the original site in three layers:

1. **Baseline states** — initial + scroll 25/50/75/100% per breakpoint (extension of
   existing multi-state rasters; zero new risk).
2. **Heuristic probes** — hover product cards, click accordion heads, flick carousel
   dots, open drawer icons. Candidates found via selector heuristics + recognizer
   pre-pass signatures. Each probe records before/after raster + DOM mutation diff;
   **pixel delta above threshold ⇒ auto-promoted to a manifest state**.
3. **Evidence packs** — per promoted state: DOM mutation records, animation params
   (Web Animations API), event-listener signatures (CDP), config blobs
   (e.g. `data-flickity-config`). A-channel recognizers consume signatures directly;
   unconsumed packs flow verbatim to B-channel subagents.

**Probe safety boundary (exhaustive):**

| Case | Handling |
|---|---|
| Click would navigate / submit form / add-to-cart | same-URL guard + dangerous-action blacklist; prefer under-capture over pollution |
| Popup/overlay blocks probe point | reuse existing overlay dismissal, clear-then-probe |
| State not stably replayable (random/time-driven animation) | reuse anim-normalize; else mark `unstable` + region-mask in compare |
| Hover on mobile breakpoints | hover states generated desktop-only |
| Whole site is WebGL/canvas (vshslv-class) | site classifier (existing) routes entire interaction layer to residual/manual; probes skipped |
| Probe time blowup | capture stays serial; state count cap; overflow truncated by visual-impact area, truncation listed in report |

## 5. Production channels (Route C spec)

**A channel — recognizer registry** (`core/recognizers/` grows an interaction wing):
- Initial vocabulary (covers Jose R6–R9 head): `sticky-header`, `carousel`
  (flickity/swiper/slick config extraction), `accordion`, `drawer` (menu/cart/search),
  `hover-swap`, `reveal-on-scroll`, `video-player`, `popup`.
- Each recognizer: matches evidence signatures → emits a **standard clean component +
  props** (data-driven, tokenized, zero source fingerprints). Born clean.
- Reference implementation to generalize: the hand-written 194-line
  `showcase/products/pagerie/src/interactions.js`.

**B channel — evidence-driven subagent authoring:**
- Input: the evidence pack + the section's clean JSX + the target manifest states.
- Subagent writes minimal interaction code (per-section module booted after mount,
  same pattern as pagerie's `interactions.js` boot-after-React-mount).
- Quality is enforced by the gate (per-state replay), cleanliness by existing
  fingerprint/weight/cleanliness gates.

**Residual channel:** anything with no capturable evidence or outside the trigger
vocabulary → manifest entry with `channel: residual`, surfaced in the report.

**Graduation mechanism:** when a B-channel pattern recurs across ≥2 sites, its evidence
signature + authored solution become a candidate new A-channel recognizer (logged in a
`recognizer-backlog.md`). B is A's incubator; capability migrates toward born-clean.

## 6. Verification gate + self-heal wiring

- New MCP tool `verify_manifest` (deterministic): boots the clone preview, replays each
  manifest state's trigger script via Playwright, rasters the state, scores
  **bounds-aligned per-state SSIM** (reuses `score_by_section` machinery), writes
  `status` back into the manifest, emits side-by-side crops per item.
- Static fidelity gate (existing per-section SSIM) remains for the `initial` states;
  manifest states extend, not replace, it.
- **Self-heal loop (finally wired end-to-end):** worst failing manifest item → hand
  (state, evidence pack, diff crop, owning section) to CC → CC repairs that one
  component/interaction module → rebuild → re-verify. Iteration budget; on exhaustion,
  remaining fails are reported, never hidden.
- Pre-requisite debt to clear FIRST (any route needs it):
  1. Wire live clone capture into the self-heal loop (gate was rewritten 6/30 with 296
     tests but never connected).
  2. Land/merge `feat/capture-completeness` so the shipping harness runs the fixed code.
  3. Asset-optimization stage (WebP/AVIF resize + `manualChunks`) to un-break R3.

## 7. Deliverables & report

- `dist/` (unchanged rule: local only).
- `manifest.json` with final statuses.
- **Reconciliation report** (HTML): one row per checklist item — trigger description,
  original vs clone crop side-by-side, SSIM, pass/fail/waived; residual section;
  truncation notes. This is what "100%" looks like when printed.

## 8. Milestones

- **M0 (debt):** self-heal wiring + branch landing + asset-optimization stage.
- **M1:** manifest generator over existing static states only (baseline states,
  no probes yet) + `verify_manifest` gate + report. Pipeline speaks checklist.
- **M2:** heuristic probes + evidence packs + A-channel big-four recognizers
  (sticky/carousel/accordion-drawer/video) → validated on pagerie + 1 Jose URL.
- **M3:** B channel (evidence → subagent authoring) + graduation backlog → validated
  across Jose's 4 reference URLs; side-by-side "clearly better" refreshed.

## 9. Testing strategy

- TDD throughout (project convention; 296+ existing tests stay green).
- Probe suite: unit tests on recorded fixture pages (no network); safety blacklist
  tests (navigation/submit never fired).
- Manifest: schema round-trip + status lifecycle tests.
- `verify_manifest`: fixture clone with known-good/known-broken interactions must
  rank correctly (the anti-Goodhart test — the metric must rank clones correctly,
  learned from the pagerie SSIM failure).
- Recognizers: per-recognizer fixture evidence → expected component props.

## 10. Non-goals (unchanged)

- 1:1 reproduction of bespoke WebGL/canvas choreography (residual/manual route).
- Live data sync (inventory, comments) — once-off snapshot.
- Interactions outside the trigger vocabulary (declared residual, not attempted).
