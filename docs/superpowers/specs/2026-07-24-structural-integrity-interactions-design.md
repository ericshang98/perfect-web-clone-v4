# Structural Integrity and Common Interaction Design

**Date:** 2026-07-24
**Status:** Approved for implementation
**Scope:** Capture, planning, generation, and verification for one-agent page cloning

## Problem

The ReelShort run exposed a circular validation failure:

1. The browser DOM and geometry inventory contained a 1440×484 Hero carousel.
2. The stabilization pass mutated the live page.
3. The final full-page reference raster was roughly 462px shorter and omitted the Hero.
4. Planning and verification treated that damaged raster as immutable truth.
5. A clone that repeated the omission received a high similarity score.

The pipeline therefore proved only that the clone matched its own incomplete evidence. It did not prove that it copied the source page.

The same architecture also treats interaction behavior as optional. The required scope is now **common page interactions**: carousel controls, menus, tabs, and accordions/details. Authentication, checkout, media playback backends, and other business workflows remain outside this milestone.

## Success Criteria

- Capture preserves immutable pre-mutation evidence.
- Any stabilization or normalization step is checked against the pre-mutation structure.
- Capture retries automatically up to three attempts.
- A source that is still structurally inconsistent after three attempts is a hard failure and cannot enter planning or generation.
- Missing critical source regions are hard verification failures regardless of aggregate image similarity.
- Required common interactions are discovered, captured as contracts, replayed against the clone, and must pass.
- Automated output is reported as `ready_for_user_review`; only the user accepts the result.

## Considered Approaches

### 1. Patch carousel opacity handling

Change the current rest-state script so it does not hide carousel ancestors.

This is small, but it fixes one symptom. Other source mutations, lazy-loading races, virtualized regions, or animation frameworks could still remove content without being noticed.

### 2. Dual evidence plus hard structural and interaction contracts

Capture immutable raw evidence first, inventory source structure and controls independently, then allow stabilization only if its output remains structurally consistent. Gate every downstream stage on that integrity result. Verify clone structure and interactions before visual similarity.

This is the selected design because it closes the evidence boundary, catches whole-region omissions, and supports the requested common interactions without attempting arbitrary business workflows.

### 3. Full browser state-graph mirroring

Explore every reachable UI and business-flow state.

This is broader than the requested scope, expensive, and unsafe around destructive or authenticated actions. It is deferred.

## Architecture

### 1. Immutable raw evidence

Before any DOM mutation, the extractor records:

- initial viewport raster;
- full-page raster;
- serialized DOM;
- page dimensions;
- a high-level structure inventory;
- a common-interaction inventory.

These artifacts are immutable for the capture attempt. Normalized HTML and rasters are separate derivatives and never replace raw evidence.

### 2. Structural inventory

The browser inventory emits ordered, visible page regions with:

- stable fingerprint;
- semantic kind and tag;
- bounds and document order;
- text, image, video, and control signals;
- criticality.

A region is critical when it is semantic chrome (`header`, `main`, `footer`, navigation), or is a large, content-bearing region such as a Hero. Large regions containing both media and heading/control signals are always critical.

### 3. Capture integrity comparison

The integrity checker compares the immutable pre-mutation inventory with the normalized post-mutation inventory and raster geometry.

Hard failures include:

- a critical pre-mutation region is absent after normalization;
- a critical region collapses or moves outside the document;
- normalized document or raster height loses a material band;
- source inventory and saved raster disagree materially.

The ReelShort failure—6450px source geometry, 5988px raster, and a missing 484px Hero—must fail this gate.

Each capture attempt writes its integrity report. Failed attempts are retained for diagnosis. The extractor retries at most three times. Three failed attempts return `capture_integrity_failed`; no source is promoted to planning.

### 4. Safe stabilization

Stabilization is a derivative operation:

- wait for stable region geometry rather than arbitrary sleep;
- identify the active carousel item without hiding a structural ancestor;
- stop animations and transitions without deleting content;
- compare the result with raw structure before accepting it.

If safe stabilization cannot be proven, the attempt fails visibly.

### 5. Planning contract

The section plan is derived from the validated raw structure and DOM. Planning refuses sources whose integrity is `failed` or `unknown`.

The plan explicitly includes every critical region and the common-interaction contracts associated with it. A generator cannot mark a section done while a required interaction is missing.

One owning agent keeps the full-page context and authors all section
components. Sections remain isolation and repair units, but are not compulsory
subagent boundaries.

Nested critical regions receive explicit clone anchors such as
`data-pwc-critical="hero-1"`. This prevents a large parent content section from
masking a missing Hero merely by retaining similar total height.

### 6. Common-interaction contracts

The extractor discovers conservative, semantic controls:

- carousel previous/next buttons and pagination dots;
- menu buttons using `aria-controls`, `aria-expanded`, or recognizable navigation relationships;
- tabs using ARIA tab roles;
- native `details/summary` and common accordion buttons.

Each contract records a stable target, action, and expected observable state change, such as:

- selected carousel item or visible media/text changes;
- `aria-expanded` toggles and controlled panel visibility changes;
- selected tab and tab panel change;
- `details.open` toggles.

The source selector is retained as evidence. The clean clone exposes
`data-pwc-interaction="<contract id>"` on its corresponding control and, when
needed, `data-pwc-controlled="<contract id>"` on the controlled surface.
Verification replays those stable clone hooks rather than requiring copied
framework class names.

Reference interaction states are captured separately. Verification replays the same contracts against the clone and checks the observable state, with regional visual comparison where a stable reference raster exists.

### 7. Verification ordering

Verification is fail-closed:

1. source capture integrity;
2. clone structural completeness;
3. required interaction replay;
4. section and full-page visual fidelity;
5. asset, cleanliness, and weight checks.

Any missing critical region or failed required interaction is a hard failure. No average score, residual score, or later visual metric can override it.

### 8. Result ownership

Machine states are `failed`, `needs_attention`, and `ready_for_user_review`. The system does not call the clone “accepted” or “complete.” Final acceptance belongs to the user.

## Data and API Changes

- `ExtractOptions.max_capture_attempts` defaults to `3`.
- Capture results include integrity status, attempt count, issues, and evidence paths.
- Source directories contain raw and normalized evidence plus `capture_integrity.json`.
- Manifests gain `structure` and `interactions` requirements.
- Planning tools reject failed/unknown capture integrity.
- Verification exposes structural and interaction gate results separately and computes overall pass with hard-gate semantics.

## Testing Strategy

Tests are written before implementation:

- a synthetic ReelShort-shaped case where a 484px Hero disappears must fail;
- two failed capture attempts followed by a valid third attempt must succeed with attempt count three;
- three inconsistent attempts must hard fail and block planning;
- removing a Hero from an otherwise pixel-identical clone must fail structural verification;
- carousel, menu, tab, and accordion contracts must be discovered and replayed;
- a failed required interaction must fail the overall result;
- legacy static pages without discovered interactions must continue through the pipeline.

## Rollout

After unit and integration tests pass:

1. recapture ReelShort using the new integrity gate;
2. confirm the Hero exists in immutable and normalized evidence;
3. rebuild the clone from the validated plan;
4. implement and replay the Hero carousel and applicable menus;
5. expose the localhost preview as `ready_for_user_review`.
