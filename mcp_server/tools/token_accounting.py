"""Run-scoped Token accounting tools for the Agent Harness."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from core.boxlite import get_sandbox
from core.token_accounting import (
    PHASES,
    UsageSnapshot,
    aggregate_events,
    budget_decision,
    new_token_usage_summary,
    usage_delta,
)
from core.usage_collectors import (
    CodexSessionCollector,
    estimate_observable_tokens,
    explicit_snapshot,
)


_SOURCE_MARKER = ".pwc/source-id"
_RUN_LEDGER = ".pwc/run.json"
_TOKEN_LEDGER = ".pwc/token-usage.jsonl"
_TOKEN_STATE = ".pwc/token-state.json"
_DEFAULT_BUDGET = {
    "soft_tokens": 250_000,
    "hard_tokens": 500_000,
    "basis": "non_cached_input_plus_output",
}


def _err(message: str, **extra: Any) -> dict[str, Any]:
    return {"ok": False, "error": message, **extra}


def _read_json_text(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def _read_events(value: str | None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in (value or "").splitlines():
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


async def _load_active_run(
    source_id: str,
) -> tuple[Any | None, dict[str, Any] | None, list[dict[str, Any]], dict[str, Any], dict[str, Any] | None]:
    source = str(source_id or "").strip()
    if not source:
        return None, None, [], {}, _err("source_id is required.")
    sandbox = get_sandbox()
    if sandbox is None:
        return None, None, [], {}, _err("no active clone sandbox.", source_id=source)
    active_source = await sandbox.read_file(_SOURCE_MARKER)
    if active_source != source:
        return (
            sandbox,
            None,
            [],
            {},
            _err(
                f"active sandbox belongs to {active_source!r}, not {source!r}.",
                source_id=source,
            ),
        )
    ledger = _read_json_text(await sandbox.read_file(_RUN_LEDGER), None)
    if not isinstance(ledger, dict) or not ledger.get("run_id"):
        return (
            sandbox,
            None,
            [],
            {},
            _err(
                "run ledger is missing run_id; assemble the project first.",
                source_id=source,
            ),
        )
    events = _read_events(await sandbox.read_file(_TOKEN_LEDGER))
    state = _read_json_text(await sandbox.read_file(_TOKEN_STATE), {})
    if not isinstance(state, dict):
        state = {}
    return sandbox, ledger, events, state, None


def _collect_snapshot(
    provider_hint: str | None = None,
    explicit_usage: Mapping[str, Any] | None = None,
) -> UsageSnapshot | None:
    if explicit_usage is not None:
        provider = str(
            explicit_usage.get("provider") or provider_hint or "explicit"
        )
        return explicit_snapshot(provider, explicit_usage)
    hint = str(provider_hint or "codex").lower()
    if hint == "codex":
        return CodexSessionCollector().snapshot()
    return None


def _compact_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = dict(context or {})
    text_bytes = int(raw.get("text_bytes") or 0)
    if text_bytes < 0:
        raise ValueError("text_bytes must be non-negative")
    estimated = raw.get("estimated_tokens")
    if estimated is None:
        estimated = estimate_observable_tokens(text_bytes)
    estimated_tokens = int(estimated)
    if estimated_tokens < 0:
        raise ValueError("estimated_tokens must be non-negative")
    compact: dict[str, Any] = {
        "text_bytes": text_bytes,
        "estimated_tokens": estimated_tokens,
    }
    artifact_paths = raw.get("artifact_paths")
    if artifact_paths is not None:
        if not isinstance(artifact_paths, list) or not all(
            isinstance(item, str) for item in artifact_paths
        ):
            raise ValueError("artifact_paths must be a list of strings")
        compact["artifact_paths"] = artifact_paths[:20]
    for key in ("image_count", "image_dimensions"):
        if key in raw:
            compact[key] = raw[key]
    stored_keys = {
        "text_bytes",
        "estimated_tokens",
        "artifact_paths",
        "image_count",
        "image_dimensions",
    }
    if set(raw) - stored_keys:
        canonical = json.dumps(
            raw,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        compact["content_digest"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return compact


def _report(
    ledger: Mapping[str, Any],
    events: list[dict[str, Any]],
    state: Mapping[str, Any],
    *,
    finalized: bool | None = None,
) -> dict[str, Any]:
    aggregate = aggregate_events(events)
    token_config = ledger.get("token_usage") or {}
    budget = dict(token_config.get("budget") or _DEFAULT_BUDGET)
    aggregate["budget"] = budget
    actual = aggregate["actual"]
    fallback_tokens = aggregate["estimated"]["fallback_tokens"]
    measurement_status = aggregate["measurement_status"]
    if measurement_status == "actual":
        budget_usage = actual
    elif measurement_status == "estimated":
        budget_usage = {
            "non_cached_input_tokens": fallback_tokens,
            "output_tokens": 0,
        }
    else:
        budget_usage = {
            "non_cached_input_tokens": (
                actual["non_cached_input_tokens"] + fallback_tokens
            ),
            "output_tokens": actual["output_tokens"],
        }
    budget_status = budget_decision(
        budget_usage,
        soft_tokens=int(budget.get("soft_tokens") or 250_000),
        hard_tokens=int(budget.get("hard_tokens") or 500_000),
    )
    budget_status["measurement"] = measurement_status
    aggregate["budget_status"] = budget_status
    missing = list(dict.fromkeys(state.get("missing_segments") or []))
    expected_agents = [
        str(agent).strip()
        for agent in (token_config.get("expected_agents") or [])
        if str(agent).strip()
    ]
    aggregate["expected_agents"] = expected_agents
    for agent in expected_agents:
        if agent not in aggregate["by_agent"]:
            missing.append(f"agent:{agent} usage missing")
    missing = list(dict.fromkeys(missing))
    is_finalized = (
        bool(state.get("finalized")) if finalized is None else finalized
    )
    aggregate["accounting_complete"] = bool(
        is_finalized
        and events
        and aggregate["measurement_status"] == "actual"
        and not missing
    )
    aggregate["missing_segments"] = missing
    return aggregate


async def _persist(
    sandbox: Any,
    ledger: dict[str, Any],
    events: list[dict[str, Any]],
    state: dict[str, Any],
    report: dict[str, Any],
) -> None:
    ledger["token_usage"] = report
    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    event_text = "".join(
        json.dumps(
            event,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for event in events
    )
    await sandbox.write_file(_TOKEN_LEDGER, event_text)
    await sandbox.write_file(
        _TOKEN_STATE,
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    )
    await sandbox.write_file(
        _RUN_LEDGER,
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
    )


async def begin_token_accounting(
    source_id: str,
    provider_hint: str | None = None,
) -> dict[str, Any]:
    """Start or resume Token accounting for the active source-scoped run."""

    sandbox, ledger, events, state, error = await _load_active_run(source_id)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    if state.get("begun"):
        report = _report(ledger, events, state)
        return {
            "ok": True,
            "source_id": source_id,
            "run_id": ledger["run_id"],
            "measurement": state.get("measurement", "estimated"),
            "duplicate": True,
            "report": report,
        }
    snapshot = _collect_snapshot(provider_hint)
    missing: list[str] = []
    if snapshot is None:
        measurement = "estimated"
        missing.append("begin snapshot unavailable")
    else:
        measurement = "actual"
    state = {
        "schema": 1,
        "run_id": ledger["run_id"],
        "begun": True,
        "finalized": False,
        "measurement": measurement,
        "snapshot": snapshot.to_dict() if snapshot is not None else None,
        "missing_segments": missing,
    }
    report = _report(ledger, events, state)
    await _persist(sandbox, ledger, events, state, report)
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": ledger["run_id"],
        "measurement": measurement,
        "duplicate": False,
        "report": report,
    }


async def checkpoint_token_accounting(
    source_id: str,
    phase: str,
    operation: str,
    context: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    explicit_usage: dict[str, Any] | None = None,
    agent_id: str = "owner",
    provider_hint: str | None = None,
) -> dict[str, Any]:
    """Record one idempotent phase/operation usage interval."""

    sandbox, ledger, events, state, error = await _load_active_run(source_id)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    if not state.get("begun"):
        return _err(
            "Token accounting has not begun.",
            source_id=source_id,
            run_id=ledger["run_id"],
        )
    phase_name = str(phase or "").strip()
    if phase_name not in PHASES:
        return _err(f"invalid phase: {phase_name!r}", source_id=source_id)
    operation_name = str(operation or "").strip()
    if not operation_name:
        return _err("operation is required.", source_id=source_id)
    agent = str(agent_id or "").strip()
    if not agent:
        return _err("agent_id is required.", source_id=source_id)
    event_id = f"{agent}:{phase_name}:{operation_name}"
    existing = next(
        (event for event in events if event.get("event_id") == event_id),
        None,
    )
    if existing is not None:
        report = _report(ledger, events, state)
        return {
            "ok": True,
            "source_id": source_id,
            "run_id": ledger["run_id"],
            "event_id": event_id,
            "duplicate": True,
            "measurement": existing["measurement"],
            "usage": existing["usage"],
            "context": existing["context"],
            "report": report,
        }
    try:
        compact_context = _compact_context(context)
        current = _collect_snapshot(provider_hint, explicit_usage)
    except (TypeError, ValueError) as exc:
        return _err(str(exc), source_id=source_id, run_id=ledger["run_id"])
    previous_value = state.get("snapshot")
    previous = (
        UsageSnapshot.from_mapping(previous_value)
        if isinstance(previous_value, dict)
        else None
    )
    if current is not None and previous is not None:
        measurement = "actual"
        usage = usage_delta(previous, current)
        state["snapshot"] = current.to_dict()
        if usage["segment_reset"]:
            marker = f"{phase_name}:{operation_name} counter reset"
            state.setdefault("missing_segments", []).append(marker)
    else:
        measurement = "estimated"
        usage = {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "non_cached_input_tokens": 0,
            "cache_write_input_tokens": 0,
            "output_tokens": 0,
            "reasoning_output_tokens": 0,
            "total_tokens": 0,
            "segment_reset": False,
        }
        marker = f"{phase_name}:{operation_name} actual usage unavailable"
        state.setdefault("missing_segments", []).append(marker)
        if current is not None:
            state["snapshot"] = current.to_dict()
    event = {
        "schema": 1,
        "event_id": event_id,
        "run_id": ledger["run_id"],
        "agent_id": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase_name,
        "operation": operation_name,
        "provider": current.provider if current is not None else provider_hint or "unknown",
        "model": current.model if current is not None else "",
        "measurement": measurement,
        "usage": usage,
        "context": compact_context,
        "quality": dict(quality or {}),
    }
    events.append(event)
    report = _report(ledger, events, state)
    await _persist(sandbox, ledger, events, state, report)
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": ledger["run_id"],
        "event_id": event_id,
        "duplicate": False,
        "measurement": measurement,
        "usage": usage,
        "context": compact_context,
        "report": report,
    }


async def get_token_report(source_id: str) -> dict[str, Any]:
    """Return the compact run aggregate and the detailed ledger path."""

    _sandbox, ledger, events, state, error = await _load_active_run(source_id)
    if error:
        return error
    assert ledger is not None
    return {
        "ok": True,
        "source_id": source_id,
        "run_id": ledger["run_id"],
        "report": _report(ledger, events, state),
        "ledger": _TOKEN_LEDGER,
    }


async def finalize_token_accounting(
    source_id: str,
    explicit_usage: dict[str, Any] | None = None,
    provider_hint: str | None = None,
) -> dict[str, Any]:
    """Record the closing interval and validate accounting completeness."""

    result = await checkpoint_token_accounting(
        source_id,
        "handoff",
        "run:finalize",
        explicit_usage=explicit_usage,
        provider_hint=provider_hint,
    )
    if not result.get("ok"):
        return result
    sandbox, ledger, events, state, error = await _load_active_run(source_id)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    state["finalized"] = True
    report = _report(ledger, events, state, finalized=True)
    await _persist(sandbox, ledger, events, state, report)
    result["finalized"] = True
    result["report"] = report
    return result


__all__ = [
    "begin_token_accounting",
    "checkpoint_token_accounting",
    "finalize_token_accounting",
    "get_token_report",
]
