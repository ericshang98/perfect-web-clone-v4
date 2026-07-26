# Per-run Token Accounting and Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record honest actual-or-estimated Token usage for every clone run and
reduce repeated Agent context through budgets, compact reports, and
quality-normalized repair accounting.

**Architecture:** A pure core module validates snapshots, computes non-negative
deltas, aggregates append-only events, and evaluates budgets. Provider adapters
collect Codex metadata or explicit host usage with a deterministic estimate
fallback. Four deterministic MCP tools persist run-scoped JSONL events and a
compact `.pwc/run.json` aggregate; the Agent skill checkpoints every phase and
uses the report to stop low-value work without waiving red gates.

**Tech Stack:** Python 3.11, pytest, FastMCP, BoxLite sandbox JSON files, Codex
JSONL usage metadata, Markdown Agent skill contracts.

---

## File map

- Create `core/token_accounting.py` — usage schema, deltas, aggregation,
  efficiency, and budget decisions.
- Create `core/usage_collectors.py` — collector protocol, Codex metadata reader,
  explicit-usage normalizer, and byte estimate fallback.
- Create `mcp_server/tools/token_accounting.py` — run-scoped begin, checkpoint,
  report, and finalize tools.
- Modify `mcp_server/tools/build_deploy.py` — initialize `run_id`, Token budget,
  and empty aggregate in every run ledger.
- Modify `mcp_server/tools/verify.py` — preserve packet bytes/estimated Tokens on
  semantic attempt records.
- Modify `mcp_server/server.py` and `mcp_server/tools/__init__.py` — register the
  four tools.
- Modify `skill/SKILL.md` and `skill/references/harness-contract.md` — require
  checkpoints, budget rules, and honest handoff reporting.
- Create `tests/test_token_accounting.py` and
  `tests/test_usage_collectors.py` — pure unit coverage.
- Create `tests/mcp/test_token_accounting_tools.py` — sandbox persistence and
  MCP behavior.
- Modify `tests/mcp/test_harness_sandbox_scope.py`,
  `tests/mcp/test_semantic_comparison_tools.py`,
  `tests/mcp/test_pipeline_tools.py`, and
  `tests/test_agent_harness_skill.py` — integration contracts.
- Modify `docs/architecture.md`, `README.md`, and the FlipClocker validation
  report — document the accounting boundary and optimization evidence.

### Task 1: Pure usage schema, aggregation, and budget decisions

**Files:**
- Create: `tests/test_token_accounting.py`
- Create: `core/token_accounting.py`

- [ ] **Step 1: Write failing snapshot/delta tests**

```python
from core.token_accounting import UsageSnapshot, usage_delta


def test_delta_separates_cached_and_non_cached_input():
    before = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="thread",
        input_tokens=100,
        cached_input_tokens=60,
        output_tokens=10,
    )
    after = UsageSnapshot(
        provider="codex",
        model="gpt",
        session_id="thread",
        input_tokens=160,
        cached_input_tokens=90,
        output_tokens=25,
    )

    delta = usage_delta(before, after)

    assert delta["input_tokens"] == 60
    assert delta["cached_input_tokens"] == 30
    assert delta["non_cached_input_tokens"] == 30
    assert delta["output_tokens"] == 15
    assert delta["total_tokens"] == 75


def test_counter_reset_starts_a_new_segment_without_negative_usage():
    before = UsageSnapshot(
        provider="codex", model="gpt", session_id="old",
        input_tokens=100, cached_input_tokens=50, output_tokens=20,
    )
    after = UsageSnapshot(
        provider="codex", model="gpt", session_id="new",
        input_tokens=12, cached_input_tokens=8, output_tokens=3,
    )

    delta = usage_delta(before, after)

    assert delta["segment_reset"] is True
    assert delta["input_tokens"] == 12
    assert delta["non_cached_input_tokens"] == 4
    assert delta["output_tokens"] == 3
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
./.venv/bin/pytest -q tests/test_token_accounting.py
```

Expected: collection fails because `core.token_accounting` does not exist.

- [ ] **Step 3: Implement the minimal snapshot and delta API**

```python
@dataclass(frozen=True)
class UsageSnapshot:
    provider: str
    model: str = ""
    session_id: str = ""
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0

    def __post_init__(self):
        values = (
            self.input_tokens,
            self.cached_input_tokens,
            self.cache_write_input_tokens,
            self.output_tokens,
            self.reasoning_output_tokens,
        )
        if any(value < 0 for value in values):
            raise ValueError("usage counters must be non-negative")
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input cannot exceed input")


def usage_delta(before: UsageSnapshot, after: UsageSnapshot) -> dict:
    reset = (
        before.provider != after.provider
        or before.model != after.model
        or before.session_id != after.session_id
        or after.input_tokens < before.input_tokens
        or after.cached_input_tokens < before.cached_input_tokens
        or after.output_tokens < before.output_tokens
    )
    base = UsageSnapshot(provider=after.provider) if reset else before
    input_tokens = after.input_tokens - base.input_tokens
    cached = after.cached_input_tokens - base.cached_input_tokens
    output = after.output_tokens - base.output_tokens
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "non_cached_input_tokens": input_tokens - cached,
        "cache_write_input_tokens": (
            after.cache_write_input_tokens - base.cache_write_input_tokens
        ),
        "output_tokens": output,
        "reasoning_output_tokens": (
            after.reasoning_output_tokens - base.reasoning_output_tokens
        ),
        "total_tokens": input_tokens + output,
        "segment_reset": reset,
    }
```

- [ ] **Step 4: Add failing aggregation, idempotency, and budget tests**

```python
from core.token_accounting import aggregate_events, budget_decision


def test_actual_and_estimated_totals_never_merge():
    events = [
        {
            "event_id": "a",
            "phase": "repair",
            "agent_id": "owner",
            "measurement": "actual",
            "usage": {
                "input_tokens": 100,
                "cached_input_tokens": 60,
                "non_cached_input_tokens": 40,
                "output_tokens": 10,
                "total_tokens": 110,
            },
            "context": {"estimated_tokens": 4000},
            "quality": {
                "before": 0.90, "after": 0.95, "accepted": True
            },
        },
        {
            "event_id": "b",
            "phase": "understand",
            "agent_id": "owner",
            "measurement": "estimated",
            "usage": {},
            "context": {"estimated_tokens": 2000},
        },
    ]

    report = aggregate_events(events)

    assert report["actual"]["total_tokens"] == 110
    assert report["estimated"]["observable_tokens"] == 6000
    assert report["measurement_status"] == "mixed"
    assert report["efficiency"]["accepted_repairs"] == 1


def test_duplicate_event_ids_are_counted_once():
    event = {
        "event_id": "same",
        "phase": "verify",
        "agent_id": "owner",
        "measurement": "actual",
        "usage": {
            "input_tokens": 20,
            "cached_input_tokens": 0,
            "non_cached_input_tokens": 20,
            "output_tokens": 5,
            "total_tokens": 25,
        },
        "context": {},
    }
    assert aggregate_events([event, event])["actual"]["total_tokens"] == 25


def test_budget_uses_non_cached_input_plus_output():
    decision = budget_decision(
        {"non_cached_input_tokens": 240_000, "output_tokens": 20_000},
        soft_tokens=250_000,
        hard_tokens=500_000,
    )
    assert decision["status"] == "soft_warning"
    assert decision["can_start_repair"] is True

    stopped = budget_decision(
        {"non_cached_input_tokens": 480_000, "output_tokens": 20_000},
        soft_tokens=250_000,
        hard_tokens=500_000,
    )
    assert stopped["status"] == "hard_stop"
    assert stopped["can_start_repair"] is False
```

- [ ] **Step 5: Run to verify the new tests fail for missing APIs**

Run:

```bash
./.venv/bin/pytest -q tests/test_token_accounting.py
```

Expected: delta tests pass; aggregation and budget tests fail because the
functions are not defined.

- [ ] **Step 6: Implement aggregation and budgets**

Implement:

```python
PHASES = {
    "capture", "understand", "plan", "generate", "build",
    "verify", "repair", "debug", "handoff",
}


def aggregate_events(events: list[dict]) -> dict:
    unique = {}
    for event in events:
        unique.setdefault(event["event_id"], event)
    rows = list(unique.values())
    actual = {
        key: 0 for key in (
            "input_tokens", "cached_input_tokens",
            "non_cached_input_tokens", "cache_write_input_tokens",
            "output_tokens", "reasoning_output_tokens", "total_tokens",
        )
    }
    estimated = 0
    by_phase = {}
    by_agent = {}
    actual_rows = estimated_rows = 0
    accepted = rejected = 0
    accepted_delta = 0.0
    accepted_tokens = 0
    for event in rows:
        if event["phase"] not in PHASES:
            raise ValueError(f"invalid phase: {event['phase']}")
        estimated += int((event.get("context") or {}).get("estimated_tokens") or 0)
        if event["measurement"] == "actual":
            actual_rows += 1
            for key in actual:
                actual[key] += int((event.get("usage") or {}).get(key) or 0)
        else:
            estimated_rows += 1
        # Add the same usage totals into by_phase and by_agent buckets.
        quality = event.get("quality") or {}
        if quality:
            if quality.get("accepted"):
                accepted += 1
                accepted_delta += max(
                    0.0, float(quality.get("after", 0))
                    - float(quality.get("before", 0))
                )
                accepted_tokens += int(
                    (event.get("usage") or {}).get("non_cached_input_tokens", 0)
                ) + int((event.get("usage") or {}).get("output_tokens", 0))
            else:
                rejected += 1
    status = (
        "mixed" if actual_rows and estimated_rows
        else "actual" if actual_rows
        else "estimated"
    )
    return {
        "measurement_status": status,
        "actual": actual,
        "estimated": {"observable_tokens": estimated},
        "by_phase": by_phase,
        "by_agent": by_agent,
        "efficiency": {
            "accepted_repairs": accepted,
            "rejected_repairs": rejected,
            "tokens_per_accepted_repair": (
                accepted_tokens // accepted if accepted else None
            ),
            "tokens_per_quality_point": (
                round(accepted_tokens / (accepted_delta * 100), 2)
                if accepted_delta else None
            ),
        },
    }


def budget_decision(actual, *, soft_tokens=250_000, hard_tokens=500_000):
    used = int(actual.get("non_cached_input_tokens", 0)) + int(
        actual.get("output_tokens", 0)
    )
    status = (
        "hard_stop" if used >= hard_tokens
        else "soft_warning" if used >= soft_tokens
        else "ok"
    )
    return {
        "basis": "non_cached_input_plus_output",
        "used_tokens": used,
        "soft_tokens": soft_tokens,
        "hard_tokens": hard_tokens,
        "status": status,
        "can_start_repair": status != "hard_stop",
    }
```

- [ ] **Step 7: Run the unit tests and commit**

Run:

```bash
./.venv/bin/pytest -q tests/test_token_accounting.py
git add core/token_accounting.py tests/test_token_accounting.py
git commit -m "feat: aggregate run token usage"
```

Expected: all focused tests pass; commit succeeds.

### Task 2: Provider collectors and explicit estimate fallback

**Files:**
- Create: `tests/test_usage_collectors.py`
- Create: `core/usage_collectors.py`

- [ ] **Step 1: Write failing collector tests**

```python
import json
from pathlib import Path

from core.usage_collectors import (
    CodexSessionCollector,
    explicit_snapshot,
    estimate_observable_tokens,
)


def test_codex_collector_reads_only_latest_token_count(tmp_path):
    session = tmp_path / "rollout-thread.jsonl"
    session.write_text(
        "\n".join([
            json.dumps({"type": "response_item", "payload": {
                "type": "message", "role": "user", "content": ["secret"]
            }}),
            json.dumps({"type": "event_msg", "payload": {
                "type": "token_count", "info": {"total_token_usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 60,
                    "output_tokens": 10,
                    "reasoning_output_tokens": 2,
                    "total_tokens": 110,
                }}
            }}),
        ]) + "\n",
        encoding="utf-8",
    )

    snapshot = CodexSessionCollector(
        thread_id="thread", roots=[tmp_path]
    ).snapshot()

    assert snapshot.input_tokens == 100
    assert snapshot.cached_input_tokens == 60
    assert snapshot.output_tokens == 10
    assert snapshot.session_id == "thread"


def test_unavailable_codex_session_returns_none(tmp_path):
    assert CodexSessionCollector(
        thread_id="missing", roots=[tmp_path]
    ).snapshot() is None


def test_explicit_usage_is_validated_and_bytes_use_ceiling_estimate():
    snapshot = explicit_snapshot("claude", {
        "input_tokens": 20,
        "cached_input_tokens": 5,
        "output_tokens": 4,
    })
    assert snapshot.input_tokens == 20
    assert estimate_observable_tokens(16_061) == 4_016
```

- [ ] **Step 2: Run and verify RED**

Run:

```bash
./.venv/bin/pytest -q tests/test_usage_collectors.py
```

Expected: collection fails because `core.usage_collectors` does not exist.

- [ ] **Step 3: Implement the collectors**

Implement a `UsageCollector` protocol, use `CODEX_THREAD_ID` by default, search
only `~/.codex/sessions` and `~/.codex/archived_sessions`, open only files whose
name contains the exact thread id, parse only `event_msg/token_count` records,
and return the final valid snapshot. Add:

```python
def explicit_snapshot(provider: str, usage: Mapping[str, Any]) -> UsageSnapshot:
    return UsageSnapshot(
        provider=provider,
        model=str(usage.get("model") or ""),
        session_id=str(usage.get("session_id") or ""),
        input_tokens=int(usage.get("input_tokens") or 0),
        cached_input_tokens=int(usage.get("cached_input_tokens") or 0),
        cache_write_input_tokens=int(
            usage.get("cache_write_input_tokens") or 0
        ),
        output_tokens=int(usage.get("output_tokens") or 0),
        reasoning_output_tokens=int(
            usage.get("reasoning_output_tokens") or 0
        ),
    )


def estimate_observable_tokens(text_bytes: int) -> int:
    if text_bytes < 0:
        raise ValueError("text_bytes must be non-negative")
    return math.ceil(text_bytes / 4)
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
./.venv/bin/pytest -q tests/test_usage_collectors.py
git add core/usage_collectors.py tests/test_usage_collectors.py
git commit -m "feat: collect provider token snapshots"
```

Expected: all collector tests pass; commit succeeds.

### Task 3: MCP persistence and compact reports

**Files:**
- Create: `tests/mcp/test_token_accounting_tools.py`
- Create: `mcp_server/tools/token_accounting.py`
- Modify: `mcp_server/server.py`
- Modify: `mcp_server/tools/__init__.py`

- [ ] **Step 1: Write failing begin/checkpoint/report tests**

Use an in-memory sandbox with `.pwc/source-id` and `.pwc/run.json`. Test:

```python
def test_begin_checkpoint_report_and_finalize_are_run_scoped(monkeypatch):
    sandbox = _FakeSandbox({
        ".pwc/source-id": "source-a",
        ".pwc/run.json": json.dumps({
            "schema": 2,
            "run_id": "run-a",
            "source_id": "source-a",
            "status": "running",
            "token_usage": {
                "budget": {
                    "soft_tokens": 250000,
                    "hard_tokens": 500000,
                    "basis": "non_cached_input_plus_output",
                }
            },
        }),
    })
    snapshots = iter([
        UsageSnapshot(
            provider="codex", session_id="thread",
            input_tokens=100, cached_input_tokens=60, output_tokens=10,
        ),
        UsageSnapshot(
            provider="codex", session_id="thread",
            input_tokens=160, cached_input_tokens=90, output_tokens=25,
        ),
    ])
    monkeypatch.setattr(token_tools, "get_sandbox", lambda: sandbox)
    monkeypatch.setattr(token_tools, "_collect_snapshot", lambda *_: next(snapshots))

    begin = asyncio.run(token_tools.begin_token_accounting("source-a"))
    checkpoint = asyncio.run(token_tools.checkpoint_token_accounting(
        "source-a", "repair", "repair:hero:1",
        context={"text_bytes": 16061},
        quality={"target": "hero", "before": .90, "after": .95,
                 "accepted": True, "hard_gate_regressions": []},
    ))
    report = asyncio.run(token_tools.get_token_report("source-a"))

    assert begin["ok"] is True
    assert checkpoint["usage"]["non_cached_input_tokens"] == 30
    assert report["report"]["actual"]["total_tokens"] == 75
    assert report["report"]["estimated"]["observable_tokens"] == 4016
    assert "secret" not in sandbox.files[".pwc/token-usage.jsonl"]
```

Also test mismatched `source_id`, duplicate operation id, estimated fallback,
counter reset, and `accounting_complete=false` for a missing child segment.

- [ ] **Step 2: Run and verify RED**

Run:

```bash
./.venv/bin/pytest -q tests/mcp/test_token_accounting_tools.py
```

Expected: collection fails because the MCP module does not exist.

- [ ] **Step 3: Implement the four tools**

Implement:

```python
async def begin_token_accounting(
    source_id: str,
    provider_hint: str | None = None,
) -> dict:
    return await _record_boundary(
        source_id=source_id,
        phase="capture",
        operation="run:begin",
        provider_hint=provider_hint,
        begin=True,
    )

async def checkpoint_token_accounting(
    source_id: str,
    phase: str,
    operation: str,
    context: dict | None = None,
    quality: dict | None = None,
    explicit_usage: dict | None = None,
    agent_id: str = "owner",
) -> dict:
    return await _record_boundary(
        source_id=source_id,
        phase=phase,
        operation=operation,
        context=context,
        quality=quality,
        explicit_usage=explicit_usage,
        agent_id=agent_id,
    )

async def get_token_report(source_id: str) -> dict:
    _sandbox, ledger, events, _state = await _load_active_run(source_id)
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": ledger["run_id"],
        "report": _report(ledger, events),
        "ledger": ".pwc/token-usage.jsonl",
    }

async def finalize_token_accounting(source_id: str) -> dict:
    result = await _record_boundary(
        source_id=source_id,
        phase="handoff",
        operation="run:finalize",
        finalize=True,
    )
    result["finalized"] = True
    return result
```

Internal helpers must:

- validate `.pwc/source-id` and `.pwc/run.json`;
- keep the baseline snapshot in `.pwc/token-state.json`;
- use `phase:operation:agent_id` as the stable event id;
- append compact JSON to `.pwc/token-usage.jsonl`;
- reject a duplicate event without recounting it;
- calculate the aggregate and budget after every checkpoint;
- write only the aggregate into `.pwc/run.json`;
- replace repeated large context metadata with a stable content digest and
  artifact path rather than duplicating the payload;
- return the aggregate and artifact paths, never the full JSONL by default.

- [ ] **Step 4: Register tools and add registration assertions**

Import the module in `mcp_server/server.py`, register all four functions before
the verification tools, expose the module in `mcp_server/tools/__init__.py`, and
assert these names in the MCP test:

```python
for name in (
    "begin_token_accounting",
    "checkpoint_token_accounting",
    "get_token_report",
    "finalize_token_accounting",
):
    assert name in REGISTERED_TOOLS
```

- [ ] **Step 5: Run focused MCP tests and commit**

Run:

```bash
./.venv/bin/pytest -q \
  tests/mcp/test_token_accounting_tools.py \
  tests/mcp/test_pipeline_tools.py
git add \
  mcp_server/tools/token_accounting.py \
  mcp_server/tools/__init__.py \
  mcp_server/server.py \
  tests/mcp/test_token_accounting_tools.py \
  tests/mcp/test_pipeline_tools.py
git commit -m "feat: persist per-run token accounting"
```

Expected: focused MCP tests pass; commit succeeds.

### Task 4: Initialize every run and connect repair evidence

**Files:**
- Modify: `tests/mcp/test_harness_sandbox_scope.py`
- Modify: `mcp_server/tools/build_deploy.py`
- Modify: `tests/mcp/test_semantic_comparison_tools.py`
- Modify: `mcp_server/tools/verify.py`

- [ ] **Step 1: Write failing run-ledger assertions**

Add:

```python
assert ledger["schema"] == 2
assert ledger["run_id"]
assert ledger["token_usage"]["measurement_status"] == "estimated"
assert ledger["token_usage"]["accounting_complete"] is False
assert ledger["token_usage"]["budget"] == {
    "soft_tokens": 250_000,
    "hard_tokens": 500_000,
    "basis": "non_cached_input_plus_output",
}
```

- [ ] **Step 2: Run and verify RED**

Run:

```bash
./.venv/bin/pytest -q tests/mcp/test_harness_sandbox_scope.py
```

Expected: assertions fail because the current ledger is schema 1 and has no
Token fields.

- [ ] **Step 3: Initialize schema 2**

Update `_new_run_ledger` to use `uuid.uuid4()` and include:

```python
"schema": 2,
"run_id": str(uuid.uuid4()),
"token_usage": {
    "measurement_status": "estimated",
    "accounting_complete": False,
    "budget": {
        "soft_tokens": 250_000,
        "hard_tokens": 500_000,
        "basis": "non_cached_input_plus_output",
    },
    "actual": {},
    "estimated": {"observable_tokens": 0},
    "by_phase": {},
    "by_agent": {},
    "efficiency": {},
},
```

- [ ] **Step 4: Write a failing repair-evidence test**

Extend the semantic tool test:

```python
result = asyncio.run(verify.record_semantic_attempt(
    source_id,
    target="hero",
    before=.90,
    after=.95,
    hard_gate_regressions=[],
    candidate_path="candidate.png",
    packet_bytes=16061,
    estimated_tokens=4016,
))
ledger = json.loads(Path(result["ledger"]).read_text())
assert ledger["attempts"][-1]["packet_bytes"] == 16061
assert ledger["attempts"][-1]["estimated_tokens"] == 4016
```

- [ ] **Step 5: Run and verify RED**

Run:

```bash
./.venv/bin/pytest -q \
  tests/mcp/test_semantic_comparison_tools.py::test_record_semantic_attempt
```

Expected: function rejects the new keyword arguments or the fields are absent.

- [ ] **Step 6: Preserve packet evidence and verify**

Add optional non-negative `packet_bytes` and `estimated_tokens` parameters.
After `record_attempt`, update the newly appended attempt with these fields
before writing the ledger.

Run:

```bash
./.venv/bin/pytest -q \
  tests/mcp/test_harness_sandbox_scope.py \
  tests/mcp/test_semantic_comparison_tools.py
git add \
  mcp_server/tools/build_deploy.py \
  mcp_server/tools/verify.py \
  tests/mcp/test_harness_sandbox_scope.py \
  tests/mcp/test_semantic_comparison_tools.py
git commit -m "feat: connect token usage to clone attempts"
```

Expected: both integration files pass; commit succeeds.

### Task 5: Make accounting and budgets mandatory in the Agent Harness

**Files:**
- Modify: `tests/test_agent_harness_skill.py`
- Modify: `skill/SKILL.md`
- Modify: `skill/references/harness-contract.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Write failing Agent contract tests**

Add:

```python
def test_harness_accounts_tokens_and_never_merges_estimates_with_actuals():
    text = _skill()
    for tool in (
        "begin_token_accounting",
        "checkpoint_token_accounting",
        "get_token_report",
        "finalize_token_accounting",
    ):
        assert f"`{tool}`" in text
    assert "actual and estimated" in text
    assert "never merge" in text
    assert "non-cached input plus output" in text


def test_hard_token_budget_stops_repairs_without_waiving_failures():
    text = _skill()
    assert "250K" in text
    assert "500K" in text
    assert "failed_with_residuals" in text
    assert "cannot waive" in text
```

- [ ] **Step 2: Run and verify RED**

Run:

```bash
./.venv/bin/pytest -q tests/test_agent_harness_skill.py
```

Expected: the new assertions fail because the skill has no accounting tools.

- [ ] **Step 3: Update the workflow contract**

Add a Token accounting subsection to `skill/SKILL.md` that requires:

1. begin immediately after the run ledger exists;
2. checkpoint after every phase and repair;
3. classify unexpected work as `debug`;
4. use actual provider usage when available and a labeled estimate otherwise;
5. never merge actual and estimated totals;
6. use non-cached input plus output for the 250K/500K budget;
7. stop new repairs at the hard budget while preserving the best candidate;
8. finalize and include the compact report at handoff.

Expand `harness-contract.md` with the schema 2 `token_usage` example, event
fields, child attribution, incomplete-accounting behavior, and budget residual.
Update architecture/README with the four tools and the distinction between a
repair packet estimate and total run usage.

- [ ] **Step 4: Verify and commit**

Run:

```bash
./.venv/bin/pytest -q tests/test_agent_harness_skill.py
git add \
  skill/SKILL.md \
  skill/references/harness-contract.md \
  tests/test_agent_harness_skill.py \
  README.md \
  docs/architecture.md
git commit -m "docs: require token-aware clone runs"
```

Expected: skill regression passes; commit succeeds.

### Task 6: Verification, live accounting smoke test, and baseline report

**Files:**
- Modify: `docs/validation/2026-07-26-flipclocker-semantic-ab.md`
- Create: `.artifacts/semantic-ab/token-accounting-smoke/` (ignored evidence)

- [ ] **Step 1: Run focused and full tests**

Run:

```bash
./.venv/bin/pytest -q \
  tests/test_token_accounting.py \
  tests/test_usage_collectors.py \
  tests/mcp/test_token_accounting_tools.py \
  tests/mcp/test_harness_sandbox_scope.py \
  tests/mcp/test_semantic_comparison_tools.py \
  tests/test_agent_harness_skill.py
./.venv/bin/pytest -q
```

Expected: focused tests and the complete suite pass with no new warning class.

- [ ] **Step 2: Verify code and tool surface**

Run:

```bash
git diff --check
./.venv/bin/python -m compileall -q core mcp_server
./.venv/bin/python - <<'PY'
from mcp_server.server import REGISTERED_TOOLS
required = {
    "begin_token_accounting",
    "checkpoint_token_accounting",
    "get_token_report",
    "finalize_token_accounting",
}
assert required <= set(REGISTERED_TOOLS)
print("token_tools=4")
PY
```

Expected: exit 0 and `token_tools=4`.

- [ ] **Step 3: Run a real local accounting smoke test**

Use the active Codex thread and an isolated fake source sandbox to:

1. create a run ledger;
2. record a baseline actual snapshot;
3. run one bounded repair-packet build against the corrected FlipClocker
   artifacts;
4. checkpoint with packet bytes and quality metadata;
5. finalize;
6. verify `.pwc/token-usage.jsonl` contains only usage metadata and
   `.pwc/run.json` contains the compact aggregate.

Do not claim the 50% full-clone reduction from this smoke test. A clean
from-scratch clone run is required for that result.

- [ ] **Step 4: Update the validation report honestly**

Add:

- the reconstructed baseline (`41.12M` gross, `1.48M` non-cached input plus
  output);
- the new accounting artifact paths;
- whether actual or estimated measurement was used;
- focused/full test output;
- the statement that full-clone reduction remains unproven until a fresh clone
  run is executed.

- [ ] **Step 5: Final verification and commit**

Run:

```bash
git diff --check
./.venv/bin/pytest -q
git status --short
git add \
  docs/validation/2026-07-26-flipclocker-semantic-ab.md
git commit -m "test: validate token accounting workflow"
```

Expected: full suite passes; only intentional ignored artifacts remain
untracked; commit succeeds.

### Task 7: Branch completion

**Files:**
- No new files.

- [ ] **Step 1: Review the complete diff against the design**

Run:

```bash
git diff 38e66ea..HEAD --stat
git log --oneline 38e66ea..HEAD
git status --short
```

Confirm every design requirement maps to committed code, tests, skill contract,
or an explicitly unproven validation item.

- [ ] **Step 2: Run fresh completion evidence**

Run:

```bash
./.venv/bin/pytest -q
./.venv/bin/python -m compileall -q core mcp_server
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Use the finishing branch workflow**

Read and follow `superpowers:finishing-a-development-branch`. Preserve the
existing `codex/semantic-comparison-loop` worktree and present the verified
result without claiming the clean-run 50% reduction until that benchmark has
actually run.
