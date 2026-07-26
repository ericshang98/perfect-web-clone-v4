# Agent Harness Contract

Use this contract to keep a one-request clone run continuous, inspectable, and
honest across tool calls.

## Progress ledger

The first `assemble_project` call creates `.pwc/run.json` in the source-scoped
sandbox. Read and update it after each phase, repair attempt, or terminal
failure. Preserve prior attempt entries rather than overwriting history.

```json
{
  "schema": 2,
  "run_id": "019f-example-run-id",
  "url": "https://example.com/",
  "source_id": "source-id",
  "phase": "author",
  "status": "running",
  "started_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "breakpoints": [1440, 390],
  "planned_sections": ["header", "hero", "content", "footer"],
  "completed_sections": ["header", "hero"],
  "comparison_contract": {
    "path": ".pwc/comparison-contract.json",
    "regions": 8,
    "status": "valid"
  },
  "gate_results": {
    "capture_integrity": {"status": "pass", "evidence": []},
    "critical_structure": {"status": "pending", "evidence": []},
    "interactions": {"status": "pending", "evidence": []},
    "build": {"status": "pending", "evidence": []},
    "fingerprints": {"status": "pending", "evidence": []},
    "weight": {"status": "pending", "evidence": []},
    "visual": {"status": "pending", "evidence": []}
  },
  "attempts": [
    {
      "target": "hero-copy",
      "packet_bytes": 9120,
      "before": 0.91,
      "after": 0.975,
      "accepted": true
    }
  ],
  "token_usage": {
    "measurement_status": "mixed",
    "accounting_complete": false,
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
    "estimated": {"observable_tokens": 71000},
    "by_phase": {},
    "by_agent": {},
    "efficiency": {}
  },
  "residuals": []
}
```

Allowed `phase` values:

- `capture`
- `plan`
- `assemble`
- `author`
- `build`
- `verify`
- `repair`
- `handoff`

Allowed run `status` values:

- `running`
- `ready_for_user_review`
- `failed_with_residuals`

Allowed gate statuses:

- `pending`
- `pass`
- `fail`
- `waived`

Use `waived` only when the user explicitly accepts an exception or the source
classification establishes a measurable technical ceiling. Add the reason and
evidence to `residuals`; never use a waiver to make a red result disappear.

## Resume rule

When `.pwc/run.json` exists:

1. Compare its normalized URL with the requested URL.
2. Resume the first incomplete phase when the URLs match and the status is
   `running`.
3. Re-check the last recorded artifact before trusting it.
4. Start a fresh sandbox run when the URLs differ.
5. Never convert a prior terminal failure to success without fresh gate output.

## Attempt record

Append one entry for each repair:

```json
{
  "number": 1,
  "gate": "critical_structure",
  "target": "hero",
  "before": {"status": "fail", "score": 0.12},
  "change": "Restored the omitted hero region from raw source evidence.",
  "after": {"status": "pass", "score": 1.0},
  "evidence": ["manifest_out/hero_sbs.png"]
}
```

Record a non-improving attempt too. Keep the best measured artifact.
The deterministic iteration ledger is authoritative for whether a candidate is
accepted, whether the target plateaued, and which candidate must be restored.

## Comparison contract

Before visual scoring, persist `.pwc/comparison-contract.json` from the compact
source evidence. Each important region declares its owner and bounds, importance
and comparison mode, and either strict pixel/state requirements or exact
non-static observations plus replacement invariants.

Volatility hints do not make the decision. Unknown critical regions remain
strict, and a critical residual is a hard failure. Whole-page SSIM remains
diagnostic when valid volatile observations exist.

## Token and monotonicity record

Each repair attempt records `packet_bytes`, estimated tokens, before/after
measurements, hard-gate regressions, `accepted`, and the best candidate path.
Default textual repair packets are limited to 16 KiB. Repair one owner at a
time; do not repeatedly load the full DOM, CSS, or all prior attempts.

Accept only strict target improvement with no hard-gate regression. After two
consecutive non-improving attempts, stop that target and preserve the best
measured candidate as the review artifact.

The first source-scoped assembly also creates `run_id` and the empty Token
aggregate. Call `begin_token_accounting` as soon as that ledger exists, then
checkpoint every phase and repair. Detailed idempotent events are append-only
in `".pwc/token-usage.jsonl"`; `.pwc/run.json` contains only the compact
aggregate.

Each event records:

```json
{
  "event_id": "owner:repair:hero:1",
  "run_id": "019f-example-run-id",
  "agent_id": "owner",
  "phase": "repair",
  "operation": "hero:1",
  "measurement": "actual",
  "usage": {
    "input_tokens": 12000,
    "cached_input_tokens": 9000,
    "non_cached_input_tokens": 3000,
    "output_tokens": 900,
    "total_tokens": 12900
  },
  "context": {
    "text_bytes": 16061,
    "estimated_tokens": 4016,
    "artifact_paths": ["manifest_out/hero-diff.png"]
  },
  "quality": {
    "target": "hero",
    "before": 0.91,
    "after": 0.975,
    "accepted": true,
    "hard_gate_regressions": []
  }
}
```

Use provider-reported usage when available and a deterministic, labeled estimate
otherwise. Actual and estimated values remain separate. `measurement_status`
is `actual`, `estimated`, or `mixed`; `accounting_complete=false` lists missing
pre-baseline, image, child-Agent, or provider segments instead of filling them
with zero.

Child Agents, when explicitly authorized by the user, receive the parent
`run_id` and a unique `agent_id`. Missing child usage is an accounting residual.

The soft budget is 250K and the hard budget is 500K non-cached input plus
output. At the hard budget preserve the best measured artifact and stop new
repairs. A budget stop never waives a red gate; record the unresolved gate and
return `failed_with_residuals`.

## Residual record

Every unresolved item contains:

```json
{
  "gate": "visual",
  "target": "hero@390",
  "expected": 0.97,
  "measured": 0.91,
  "attempts": 5,
  "evidence": ["manifest_out/hero-mobile-sbs.png"],
  "reason": "Repair budget exhausted"
}
```

Never replace the item with a vague sentence such as “mostly matches.”

## Dependency order

Evaluate gates in this order:

1. source capture integrity;
2. complete planned structure and critical anchors;
3. required common interaction behavior;
4. production build;
5. fingerprint and weight constraints;
6. visual fidelity by breakpoint and state;
7. comparison to a valid baseline, when present.

A failure in an earlier gate blocks `ready_for_user_review`, regardless of later
scores.

## Interaction acceptance

At minimum, support discovered contracts for:

- carousel next/previous and resulting active slide;
- menu open/close and controlled panel visibility;
- tabs and active panel selection;
- accordion/details open/close and content visibility.

Replay each contract through stable `data-pwc-interaction` and
`data-pwc-controlled` hooks. Static look-alikes fail.

## Handoff vocabulary

Use `ready_for_user_review` only for a machine-green result. It means the
artifact is ready for the user's inspection, not that the user accepted it.

Use `failed_with_residuals` whenever any required gate remains red or a captured
requirement cannot be reproduced within the attempt budget. Return the working
artifact plus the complete residual ledger so the user can decide what happens
next.
