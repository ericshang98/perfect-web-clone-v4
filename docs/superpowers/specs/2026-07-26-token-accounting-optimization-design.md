# Per-run Token Accounting and Optimization Design

**Date:** 2026-07-26  
**Status:** Approved in conversation; pending written-spec review  
**Scope:** Agent-run attribution, actual/estimated usage collection, budgets,
quality-normalized efficiency, and low-context clone execution

## Problem

The Harness currently limits a single semantic repair packet to 16 KiB and
records its estimated Token count, but it does not measure a complete clone
run. As a result, the `4,016` estimated Tokens reported for FlipClocker
described one repair packet rather than the Agent's full cost.

Session telemetry reconstructed after the run showed the actual problem:
the corrected FlipClocker trial processed `41.12M` Tokens, of which `39.64M`
were cached input. Even after excluding cache hits, non-cached input plus output
was `1.48M`. The owner-scoped repair packet was small, but repeated long-thread
context, broad tool output, debugging, and theme-baseline rework dominated the
run.

The Harness needs an honest per-run Token ledger and deterministic controls that
reduce usage without allowing a cheaper but worse clone to appear successful.

## Goals

1. Attribute usage to one clone `run_id`, including child Agent work.
2. Prefer provider-reported usage and fall back to a labeled estimate.
3. Never combine actual and estimated values into a fake exact total.
4. Show where Tokens were spent by phase, operation, target, and attempt.
5. Relate Token usage to accepted quality improvement and hard-gate outcomes.
6. Enforce soft and hard budgets without hiding failures.
7. Reduce repeated context, tool output, and unproductive repair attempts.
8. Compare an optimized run with a valid same-page baseline.

## Non-goals

- The Harness will not calculate currency cost without an explicitly supplied
  provider pricing table.
- Token accounting will not replace structural, interaction, build, or visual
  gates.
- A budget will not automatically turn a red quality gate green.
- Provider-specific telemetry will not become a required dependency. A run may
  continue with explicitly labeled estimates.
- The Harness will not require a new user-facing CLI, API, daemon, or
  orchestrator.

## Considered Approaches

### 1. Repair-packet estimates only

Continue estimating Tokens from textual evidence bytes. This is portable and
deterministic, but it excludes the Agent's conversation context, output,
reasoning, tool results, retries, and child work. It cannot answer the user's
question about total run cost.

### 2. Provider log scraping only

Read Codex or Claude Code session telemetry and derive run deltas. This is the
most accurate source when available, but log paths and event schemas are
provider-specific and may change. It also fails in environments that do not
expose usage.

### 3. Hybrid collectors with a deterministic fallback

Use provider-reported usage when an adapter can obtain it. Otherwise estimate
the bounded Agent evidence and output through a shared estimator. Persist the
measurement source on every event and aggregate actual and estimated data
separately.

This is the selected approach. It preserves portability while making exact
usage available where the host exposes it.

## Architecture

### 1. Run-scoped accounting

The first `assemble_project` call creates a stable `run_id` in `.pwc/run.json`.
All Token events include that id. A matching source resumes the same active run;
a different source creates a new run and resets its baseline.

Accounting begins with a provider snapshot and ends with a final snapshot. A
snapshot is cumulative provider state; the Harness stores only the non-negative
delta attributable to the active run. Counter resets, model changes, or
provider-session changes create a new segment rather than a negative delta.

Child Agents receive the parent `run_id`. Their events include a unique
`agent_id` and are merged into the same aggregate. An unreported child is
surfaced as incomplete accounting, not silently treated as zero.

### 2. Measurement adapters

All collectors implement one logical interface:

```python
class UsageCollector(Protocol):
    def snapshot(self) -> UsageSnapshot | None: ...
```

`UsageSnapshot` contains:

- provider and model;
- provider session id, when available;
- input Tokens;
- cached input Tokens;
- cache-write input Tokens, when available;
- output Tokens;
- reasoning output Tokens, when separately reported;
- cumulative/interval semantics;
- measurement source and confidence.

Initial adapters:

- `CodexSessionCollector`: reads the active Codex session Token events when the
  host exposes a thread id and readable session log.
- `ExplicitUsageCollector`: accepts usage returned directly by a model host or
  supplied by the owning Agent.
- `EstimatedUsageCollector`: estimates only the material the Harness can
  observe, such as comparison evidence, section payloads, repair packets, and
  Agent-authored output.

The adapter boundary allows Claude Code or another host to add a collector
without changing the ledger schema or optimization rules.

Collectors read usage metadata only. The Codex adapter reads `token_count`
events and never copies conversation text, tool payloads, credentials, or model
responses into the Harness ledger.

Image-input usage remains unknown when the provider does not report it. The
fallback collector records the image count, dimensions, and provider-specific
estimate only when a supported estimator exists; otherwise it marks that
segment incomplete instead of pretending the image cost is zero.

### 3. Agent-facing accounting tools

The deterministic MCP surface adds four operations:

- `begin_token_accounting(source_id, provider_hint=None)` — creates or resumes
  the run scope and records its starting snapshot;
- `checkpoint_token_accounting(source_id, phase, operation, context=None,
  quality=None, explicit_usage=None)` — records one idempotent interval;
- `get_token_report(source_id)` — returns a compact aggregate and paths to the
  detailed ledger;
- `finalize_token_accounting(source_id)` — records the closing snapshot,
  validates completeness, and persists the final report.

The current Agent calls a checkpoint after every phase and repair attempt.
Provider adapters may fill usage automatically; `explicit_usage` exists for a
host that returns usage directly. Tools validate the active sandbox/source and
do not accept an arbitrary path to another session log.

### 4. Append-only event ledger

Detailed events are appended to `.pwc/token-usage.jsonl`. Each event has:

```json
{
  "schema": 1,
  "run_id": "uuid",
  "agent_id": "owner",
  "timestamp": "ISO-8601",
  "phase": "repair",
  "operation": "repair:feature-grid:2",
  "provider": "codex",
  "model": "model-id",
  "measurement": "actual",
  "usage": {
    "input_tokens": 12000,
    "cached_input_tokens": 9000,
    "cache_write_input_tokens": 0,
    "output_tokens": 900,
    "reasoning_output_tokens": 200,
    "total_tokens": 12900
  },
  "context": {
    "text_bytes": 16061,
    "estimated_tokens": 4016
  },
  "quality": {
    "target": "feature-grid",
    "before": 0.91,
    "after": 0.98,
    "accepted": true,
    "hard_gate_regressions": []
  }
}
```

Actual and estimated observations may coexist on an event, but only actual
usage enters actual totals. Estimated totals remain separate and are used only
when actual telemetry is unavailable.

### 5. Aggregate run ledger

`.pwc/run.json` gains a `token_usage` object:

```json
{
  "measurement_status": "actual",
  "accounting_complete": true,
  "budget": {
    "soft_tokens": 250000,
    "hard_tokens": 500000,
    "basis": "non_cached_input_plus_output"
  },
  "actual": {
    "input_tokens": 180000,
    "cached_input_tokens": 120000,
    "non_cached_input_tokens": 60000,
    "output_tokens": 12000,
    "total_tokens": 192000
  },
  "estimated": {
    "observable_tokens": 71000
  },
  "by_phase": {},
  "by_agent": {},
  "efficiency": {
    "accepted_repairs": 3,
    "rejected_repairs": 1,
    "tokens_per_accepted_repair": 21000,
    "tokens_per_quality_point": 4800
  }
}
```

`measurement_status` is `actual`, `estimated`, or `mixed`. `mixed` does not
merge the two numeric domains; it means some operations have actual usage and
others have estimates. `accounting_complete=false` lists missing agents or
segments.

The default budget basis is:

```text
non_cached_input_tokens + output_tokens
```

Gross processed Tokens and cached input remain visible because they affect
latency and provider usage, but cache hits do not masquerade as newly supplied
context.

## Phase Boundaries

The owning Agent records usage at these boundaries:

1. `capture` — extraction calls and compact integrity review;
2. `understand` — one comparison-evidence pass and contract authorship;
3. `plan` — complete-page section and critical-region planning;
4. `generate` — shell plus initial section implementation;
5. `build` — build diagnosis and corrections;
6. `verify` — structural, interaction, visual, and baseline gates;
7. `repair` — one event per owner-scoped attempt;
8. `debug` — unexpected Harness or source failures;
9. `handoff` — final aggregation and report generation.

Unexpected work belongs to `debug`; it must not be blended into normal repair
cost. This makes theme-capture failures like FlipClocker's visible as avoidable
overhead.

## Budget Policy

Defaults are configurable per run:

- `250K` soft budget;
- `500K` hard budget;
- `16 KiB` maximum textual repair packet;
- five attempts per target and twelve attempts per run;
- stop a target after two consecutive non-improving attempts.

Budget behavior:

- At 80% of the soft budget, the next operation must use the smallest available
  evidence path.
- At the soft budget, the Agent may continue only on a failed required gate and
  must record the projected next-operation cost.
- At the hard budget, no further quality repair is started. The best candidate
  is preserved and the run becomes `failed_with_residuals` unless all required
  gates already pass.
- Capture integrity or build debugging may exceed the hard budget only to
  produce a safe, explicit terminal record; it cannot continue open-ended.

A budget stop is never a waiver. The unresolved gate, best score, attempts,
Token use, and evidence remain visible.

## Token Optimization Controls

### 1. Bounded understanding pass

`get_comparison_evidence` remains the only default whole-page Agent evidence
pass per breakpoint. It returns compact region records and paths to large
artifacts instead of raw DOM/CSS.

### 2. Digest-first tool responses

Agent-facing tools return a bounded summary by default:

- status and hard-gate failures;
- ids, bounds, scores, and artifact paths;
- a capped list of actionable errors.

Large DOM, CSS, logs, and complete histories require an explicit targeted read.
Repeated identical payloads are represented by content digest and artifact
path.

### 3. Owner-scoped generation and repair

Initial generation reads each section once. Repairs load only:

- the worst failing target;
- its contract and measurements;
- its owning component and scoped styles;
- at most three compact prior deltas.

Shared tokens are loaded only when measurements prove a cross-region cause.

### 4. Externalized run memory

Attempt history, gate evidence, and best-candidate state remain in `.pwc`
artifacts. The Agent reads a compact current-state digest rather than carrying
the full history in every reasoning turn.

### 5. Cost-aware monotonic iteration

Each attempted repair records quality delta and Token delta. The next target is
chosen using required-gate order first, then expected quality gain per Token.
No cheaper target may skip an earlier hard failure.

Rejected repairs count against the budget. Two non-improving attempts stop the
target. A full-page recapture occurs only after all regions pass or after every
fourth accepted repair.

### 6. Clean-run recommendation

The Harness records a warning when a clone starts inside a long unrelated Agent
thread because repeated host context can dominate usage even if Harness packets
are small. This is advisory, not a new user-facing command or a reason to refuse
the run.

## Reports

Every handoff includes:

- actual and estimated totals, kept separate;
- cached and non-cached input;
- output and reasoning output when available;
- usage by phase, agent, target, and accepted/rejected repair;
- budget status;
- quality before/after;
- Token cost per accepted repair and per quality-point improvement;
- missing accounting segments;
- top three Token optimization opportunities.

The report must state the measurement boundary and cannot describe a repair
packet estimate as total run usage.

## Failure Handling

- Unavailable provider telemetry selects the estimated collector and marks the
  run accordingly.
- Malformed or decreasing provider counters start a new segment and record a
  residual.
- Duplicate event ids are ignored idempotently.
- A resumed run continues the same ledger without recounting prior snapshots.
- Child usage without the parent `run_id` is rejected and surfaced.
- Ledger write failure is a Harness integrity failure. The clone may be
  preserved, but handoff status is `failed_with_residuals`.
- Actual/estimated mixing never silently fills gaps with zero.

## Testing Strategy

### Unit tests

- actual usage deltas are calculated from cumulative snapshots;
- cached input is a subset of input and non-cached input is derived correctly;
- counter resets create a new segment without negative usage;
- estimated events remain separate from actual totals;
- duplicate event ids are idempotent;
- invalid phases, negative counters, and mismatched run ids fail;
- child Agent usage aggregates into the parent run;
- budget thresholds select the correct action;
- efficiency metrics use only accepted measured improvement.

### Integration tests

- `assemble_project` creates a `run_id`, budget, and empty Token aggregate;
- begin/end phase snapshots append JSONL and update `.pwc/run.json`;
- repair-packet size and repair usage appear on the same attempt;
- resumed runs do not double count;
- missing provider telemetry produces an explicitly estimated run;
- hard-budget exhaustion preserves the best candidate and records a residual;
- agent-facing tool outputs stay within their response budgets.

### Skill regression

The Agent Harness contract requires:

- accounting throughout every clone run;
- real usage when available and estimates otherwise;
- actual and estimated totals kept separate;
- child Agent attribution;
- budget-aware stopping without quality waivers;
- final Token/quality reporting.

## Validation Trial

Use the corrected FlipClocker source and comparison contract because it has:

- strict static regions;
- a naturally changing clock;
- replayable settings;
- a known theme-baseline failure;
- an existing measured quality result of `0.9963`.

Run the optimized workflow in a fresh Agent task and compare it with the
reconstructed baseline:

- baseline clone-only non-cached input plus output: `1.48M`;
- baseline gross processed Tokens: `41.12M`;
- baseline valid static score: `0.9963`.

Success requires:

1. complete accounting with no unlabeled gaps;
2. at least 50% reduction in non-cached input plus output;
3. at least 50% reduction in gross processed Tokens when host telemetry permits;
4. no failed structural, interaction, build, or theme gate;
5. valid static score no lower than `0.9963 - 0.002`;
6. no increase in accepted repair count caused by optimization;
7. a report that identifies every budget warning and rejected attempt.

If the Token target is missed, the feature still reports measured data but the
optimization trial fails. It cannot be declared successful because accounting
alone works.

## Rollout

1. Add the schema, ledger, collectors, and aggregation without changing repair
   decisions.
2. Enable reporting and establish two clean-run baselines.
3. Enable soft-budget warnings and digest-first responses.
4. Enable hard-budget stopping after the validation trial proves quality is
   preserved.
5. Add provider adapters incrementally behind the shared collector interface.

This order separates observability from control, making regressions attributable
and reversible.
