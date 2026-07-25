# Semantic Comparison Loop Design

**Date:** 2026-07-26
**Status:** Approved in conversation; pending written-spec review
**Scope:** Agent reasoning, comparison contracts, fidelity localization, and token-bounded repair

## Problem

The current Harness can apply one raw screenshot metric to every visible pixel.
That is useful only when the source and clone rasters describe the same
observable state. It becomes misleading for video frames, clocks, counters,
automatic carousels, advertisements, recommendations, canvas rendering, and
other content that can legitimately change between captures.

The ReelShort episode page exposed the failure:

- source and clone had the same 1440×900 page geometry;
- the source screenshot contained an arbitrary live video frame;
- the clone contained a different valid frame or poster;
- whole-page SSIM was 0.7232 and was incorrectly treated as a CSS verdict;
- replacing only the video pixels still left meaningful header and details
  differences that required normal CSS repair.

The Harness therefore needs more Agent judgment, not a looser global threshold.
It must decide which properties express the website and which observations are
legitimately volatile before selecting a measurement.

## Design Goals

1. The Agent understands the real page before fidelity scoring.
2. Static UI remains strictly measured; dynamic content is not used as a false
   CSS failure.
3. Dynamic regions retain measurable invariants such as bounds, aspect ratio,
   chrome, controls, state transitions, and relationships to surrounding UI.
4. Repairs are comparison-driven and monotonically improve the best candidate.
5. The Agent receives only the smallest evidence packet needed for the next
   repair.
6. No region is silently masked, waived, or averaged away.
7. The result remains `ready_for_user_review` or `failed_with_residuals`; only
   the user accepts it.

## Considered Approaches

### 1. Add hard-coded exclusions for video and canvas

This is inexpensive but too literal. It fixes the ReelShort example while
failing on timers, personalized data, animated carousels, third-party content,
and future dynamic surfaces.

### 2. Let raw whole-page SSIM remain the gate and ask the Agent to explain it

This preserves the current implementation but leaves the invalid measurement in
control. The Agent can describe the problem after the fact but cannot prevent a
false failure or focus repairs efficiently.

### 3. Agent-authored semantic comparison contract

The Agent inspects the source evidence once, classifies each important region by
what must remain invariant, and persists that decision. Deterministic tools then
measure only the declared invariants and localize the worst valid discrepancy.

This is the selected approach. It generalizes beyond individual HTML tags while
keeping measurement and iteration deterministic.

## Architecture

### 1. Source understanding pass

After capture integrity and section planning pass, the Agent reviews:

- one full-page source raster per required breakpoint;
- the ordered critical-region inventory and bounds;
- semantic DOM signals such as video, canvas, controls, ARIA relationships, and
  text roles;
- temporal evidence produced without model tokens: up to three source samples
  and the regions whose pixels or text changed;
- discovered interaction contracts.

The Agent does not receive the full raw DOM or every CSS rule. Tools summarize
the evidence into bounded region records.

### 2. Comparison contract

The Agent persists `.pwc/comparison-contract.json`. Every important region has:

```json
{
  "id": "episode-player",
  "owner": "section",
  "bounds": {"x": 246, "y": 66, "width": 468, "height": 834},
  "importance": "critical",
  "mode": "layout_behavior",
  "compare": [
    "bounds",
    "aspect_ratio",
    "container_style",
    "controls",
    "interaction"
  ],
  "ignore_observations": ["media_frame_pixels", "elapsed_time_text"],
  "reason": "live video content changes independently of page CSS",
  "confidence": 0.99
}
```

Supported comparison modes are:

- `static_pixels`: stable UI whose raster must meet the configured threshold;
- `layout_style`: geometry and computed presentation are invariant, while
  content may vary;
- `layout_behavior`: geometry, chrome, controls, and interactions are
  invariant, while runtime media pixels may vary;
- `stateful_pixels`: compare only after replaying a named deterministic state;
- `residual`: unmeasurable source behavior that remains visible in the report.

The contract is evidence, not a waiver. A non-static mode must include a reason,
the exact ignored observation, and the invariants that replace raw pixel
comparison. Critical regions cannot use `residual` without causing
`failed_with_residuals`.

### 3. Deterministic measurement

The fidelity layer consumes the contract:

- `static_pixels` regions use bounds-aligned two-dimensional crops and SSIM;
- `layout_style` regions compare bounds, aspect ratio, visibility, overflow,
  selected computed styles, and stable text/icon chrome;
- `layout_behavior` regions additionally replay their interaction contracts;
- `stateful_pixels` regions replay the named state before capture;
- ignored observations are excluded only inside their explicit 2D bounds;
- the report lists excluded pixel area and the replacement invariants.

Whole-page SSIM remains diagnostic. It is never a hard CSS gate when the
comparison contract contains volatile observations.

Hard gates remain per-region. An aggregate score cannot compensate for a failed
critical region.

### 4. Token-bounded evidence packet

The tools produce a repair packet for the single worst valid region:

- source crop;
- candidate crop;
- difference heatmap;
- region contract and measurements;
- owner component path;
- only the relevant JSX/CSS excerpts and shared tokens;
- previous attempts and score deltas.

The default limits are:

- one full-page Agent understanding pass per breakpoint;
- one repair target per iteration;
- at most three reported candidate regions, with only the worst expanded;
- 16 KiB maximum textual repair packet;
- five attempts per target and twelve attempts per run;
- stop after two consecutive non-improving attempts on the same target.

Images are cropped to the target region and capped for review resolution.
Unchanged DOM, source CSS, and prior evidence are referenced by artifact path
rather than repeated in the prompt.

### 5. Monotonic repair loop

For every repair:

1. select the earliest failed hard gate;
2. select its worst valid region;
3. build the bounded repair packet;
4. let the Agent change only the owner component or a proven shared token;
5. rebuild and remeasure the affected region;
6. rerun structural and interaction gates affected by the change;
7. keep the candidate only if the target improves and no hard gate regresses;
8. otherwise restore the best measured candidate and record the failed attempt.

A full-page sanity capture runs after all regions pass or after every fourth
accepted repair. This catches cross-region layout drift without repeatedly
spending Agent context on the full page.

## Agent Decision Principles

The Agent answers this question for every observed difference:

> If the real page refreshed naturally, could this observation change while the
> website's design and behavior remained correct?

If no, the observation is a strict fidelity target. If yes, the Agent identifies
the stable invariants around it. The Agent may not simply ignore a region
because it is difficult to reproduce.

Examples:

- video: ignore decoded frame pixels; compare player geometry, crop behavior,
  overlays, controls, and interactions;
- clock or counter: ignore the current value; compare formatting, layout, and
  update behavior;
- automatic carousel: compare one named stable state plus navigation behavior,
  not the chance slide visible at capture time;
- personalized card data: compare card system, density, hierarchy, and stable
  chrome; record content variability;
- static marketing image: compare pixels strictly.

## Failure Handling

- Unknown critical regions default to strict comparison until the Agent writes
  an evidence-backed contract.
- A low-confidence non-static classification is surfaced for Agent review once;
  it does not trigger repeated full-page analysis.
- Missing bounds, missing owner mapping, or missing replacement invariants are
  hard contract failures.
- A repair packet that exceeds its budget is reduced deterministically by
  dropping unrelated CSS and DOM, never by truncating the target evidence.
- Plateaus preserve the best candidate and produce a residual with attempts,
  measurements, and evidence.

## API and Artifact Changes

- Add a comparison-contract schema and validator.
- Extend capture evidence with bounded temporal volatility observations.
- Add two-dimensional region masking and contract-aware fidelity reports.
- Add a repair-packet builder that maps a failed region to its owning component.
- Extend `.pwc/run.json` with packet sizes, accepted/rejected attempts, best
  candidate, and per-region score history.
- Update the Harness skill so the current Agent authors and applies the
  comparison contract before visual scoring.

The deterministic `pwc4` tools still do not call a model. The current
Claude Code or Codex Agent remains the reasoning layer.

## Testing Strategy

### Unit and integration tests

- a changing video frame does not fail CSS fidelity when player invariants pass;
- changing player bounds or controls still fails;
- a stable marketing image remains strict;
- a timer value can vary while formatting and geometry remain enforced;
- an automatic carousel is compared in a named state and must still navigate;
- critical regions cannot disappear through exclusion;
- repair packets obey their text and crop budgets;
- accepted iterations improve the target and preserve all earlier hard gates;
- regressing candidates are rejected in favor of the best artifact.

### New-page A/B trial

Select a public, unauthenticated page not used during implementation. It must
contain both stable UI and at least one naturally changing or stateful region.

Run the same target twice:

1. checkpoint `88208f3` with the previous Harness;
2. the optimized semantic comparison loop.

Record:

- false visual failures caused by volatile observations;
- static-region fidelity before and after repair;
- number of Agent repair iterations;
- textual repair-packet bytes and estimated token cost;
- structural and interaction regressions;
- final residuals and user-review artifacts.

## Success Criteria

- ReelShort no longer treats arbitrary video-frame pixels as a CSS gate.
- Player geometry and behavior remain strictly verified.
- Static ReelShort regions still expose their real header/details discrepancies.
- A new page demonstrates at least one evidence-based volatile classification
  without hiding a static or behavioral defect.
- Every accepted repair improves its target with no hard-gate regression.
- Repair packets stay within the default budget.
- The optimized run provides more trustworthy evidence than checkpoint
  `88208f3`, even when raw whole-page SSIM is unchanged or lower.
