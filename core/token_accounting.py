"""Pure per-run Token accounting, aggregation, and budget decisions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


PHASES = {
    "capture",
    "understand",
    "plan",
    "generate",
    "build",
    "verify",
    "repair",
    "debug",
    "handoff",
}
MEASUREMENTS = {"actual", "estimated"}
USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "non_cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


def _non_negative_int(value: Any, name: str) -> int:
    try:
        number = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


@dataclass(frozen=True)
class UsageSnapshot:
    """One cumulative provider usage observation."""

    provider: str
    model: str = ""
    session_id: str = ""
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0

    def __post_init__(self) -> None:
        if not str(self.provider).strip():
            raise ValueError("provider is required")
        for name in (
            "input_tokens",
            "cached_input_tokens",
            "cache_write_input_tokens",
            "output_tokens",
            "reasoning_output_tokens",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{name} must be an integer")
            if value < 0:
                raise ValueError("usage counters must be non-negative")
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input cannot exceed input")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "UsageSnapshot":
        return cls(
            provider=str(value.get("provider") or ""),
            model=str(value.get("model") or ""),
            session_id=str(value.get("session_id") or ""),
            input_tokens=_non_negative_int(
                value.get("input_tokens"), "input_tokens"
            ),
            cached_input_tokens=_non_negative_int(
                value.get("cached_input_tokens"), "cached_input_tokens"
            ),
            cache_write_input_tokens=_non_negative_int(
                value.get("cache_write_input_tokens"),
                "cache_write_input_tokens",
            ),
            output_tokens=_non_negative_int(
                value.get("output_tokens"), "output_tokens"
            ),
            reasoning_output_tokens=_non_negative_int(
                value.get("reasoning_output_tokens"),
                "reasoning_output_tokens",
            ),
        )


def _same_segment(before: UsageSnapshot, after: UsageSnapshot) -> bool:
    return (
        before.provider == after.provider
        and before.model == after.model
        and before.session_id == after.session_id
        and after.input_tokens >= before.input_tokens
        and after.cached_input_tokens >= before.cached_input_tokens
        and after.cache_write_input_tokens >= before.cache_write_input_tokens
        and after.output_tokens >= before.output_tokens
        and after.reasoning_output_tokens >= before.reasoning_output_tokens
    )


def usage_delta(
    before: UsageSnapshot | None,
    after: UsageSnapshot,
) -> dict[str, int | bool]:
    """Return a non-negative interval, starting a new segment on counter reset."""

    reset = before is not None and not _same_segment(before, after)
    if before is None or reset:
        input_tokens = after.input_tokens
        cached_input_tokens = after.cached_input_tokens
        cache_write_input_tokens = after.cache_write_input_tokens
        output_tokens = after.output_tokens
        reasoning_output_tokens = after.reasoning_output_tokens
    else:
        input_tokens = after.input_tokens - before.input_tokens
        cached_input_tokens = (
            after.cached_input_tokens - before.cached_input_tokens
        )
        cache_write_input_tokens = (
            after.cache_write_input_tokens - before.cache_write_input_tokens
        )
        output_tokens = after.output_tokens - before.output_tokens
        reasoning_output_tokens = (
            after.reasoning_output_tokens - before.reasoning_output_tokens
        )
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "non_cached_input_tokens": input_tokens - cached_input_tokens,
        "cache_write_input_tokens": cache_write_input_tokens,
        "output_tokens": output_tokens,
        "reasoning_output_tokens": reasoning_output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "segment_reset": reset,
    }


def empty_usage() -> dict[str, int]:
    return {key: 0 for key in USAGE_KEYS}


def _normalized_usage(value: Mapping[str, Any] | None) -> dict[str, int]:
    raw = dict(value or {})
    usage = empty_usage()
    for key in USAGE_KEYS:
        usage[key] = _non_negative_int(raw.get(key), key)
    if usage["cached_input_tokens"] > usage["input_tokens"]:
        raise ValueError("cached input cannot exceed input")
    expected_non_cached = (
        usage["input_tokens"] - usage["cached_input_tokens"]
    )
    if (
        "non_cached_input_tokens" in raw
        and usage["non_cached_input_tokens"] != expected_non_cached
    ):
        raise ValueError("non-cached input does not match input minus cached")
    usage["non_cached_input_tokens"] = expected_non_cached
    expected_total = usage["input_tokens"] + usage["output_tokens"]
    if "total_tokens" in raw and usage["total_tokens"] != expected_total:
        raise ValueError("total_tokens does not match input plus output")
    usage["total_tokens"] = expected_total
    return usage


def _add_usage(bucket: dict[str, int], usage: Mapping[str, Any]) -> None:
    for key in USAGE_KEYS:
        bucket[key] += int(usage.get(key) or 0)


def _bucket() -> dict[str, int]:
    return {**empty_usage(), "estimated_tokens": 0, "events": 0}


def aggregate_events(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate idempotent Token events without merging estimates into actuals."""

    unique: dict[str, Mapping[str, Any]] = {}
    for raw in events:
        event_id = str(raw.get("event_id") or "").strip()
        if not event_id:
            raise ValueError("event_id is required")
        unique.setdefault(event_id, raw)

    actual = empty_usage()
    observable_estimate = 0
    fallback_estimate = 0
    by_phase: dict[str, dict[str, int]] = {}
    by_agent: dict[str, dict[str, int]] = {}
    actual_rows = 0
    estimated_rows = 0
    accepted = 0
    rejected = 0
    accepted_actual_rows = 0
    accepted_actual_tokens = 0
    accepted_actual_quality_points = 0.0
    accepted_estimated_rows = 0
    accepted_estimated_tokens = 0
    accepted_estimated_quality_points = 0.0

    for raw in unique.values():
        phase = str(raw.get("phase") or "")
        if phase not in PHASES:
            raise ValueError(f"invalid phase: {phase}")
        measurement = str(raw.get("measurement") or "")
        if measurement not in MEASUREMENTS:
            raise ValueError(f"invalid measurement: {measurement}")
        agent_id = str(raw.get("agent_id") or "").strip()
        if not agent_id:
            raise ValueError("agent_id is required")

        context = raw.get("context") or {}
        estimated_tokens = _non_negative_int(
            context.get("estimated_tokens"), "estimated_tokens"
        )
        observable_estimate += estimated_tokens
        usage = _normalized_usage(raw.get("usage"))
        phase_bucket = by_phase.setdefault(phase, _bucket())
        agent_bucket = by_agent.setdefault(agent_id, _bucket())
        phase_bucket["events"] += 1
        agent_bucket["events"] += 1
        phase_bucket["estimated_tokens"] += estimated_tokens
        agent_bucket["estimated_tokens"] += estimated_tokens

        if measurement == "actual":
            actual_rows += 1
            _add_usage(actual, usage)
            _add_usage(phase_bucket, usage)
            _add_usage(agent_bucket, usage)
        else:
            estimated_rows += 1
            fallback_estimate += estimated_tokens

        quality = raw.get("quality") or {}
        if quality:
            if quality.get("accepted"):
                accepted += 1
                before = float(quality.get("before") or 0)
                after = float(quality.get("after") or 0)
                quality_points = max(0.0, after - before) * 100
                if measurement == "actual":
                    accepted_actual_rows += 1
                    accepted_actual_quality_points += quality_points
                    accepted_actual_tokens += (
                        usage["non_cached_input_tokens"]
                        + usage["output_tokens"]
                    )
                else:
                    accepted_estimated_rows += 1
                    accepted_estimated_quality_points += quality_points
                    accepted_estimated_tokens += estimated_tokens
            else:
                rejected += 1

    if actual_rows and estimated_rows:
        measurement_status = "mixed"
    elif actual_rows:
        measurement_status = "actual"
    else:
        measurement_status = "estimated"

    return {
        "measurement_status": measurement_status,
        "actual": actual,
        "estimated": {
            "observable_tokens": observable_estimate,
            "fallback_tokens": fallback_estimate,
        },
        "by_phase": by_phase,
        "by_agent": by_agent,
        "efficiency": {
            "accepted_repairs": accepted,
            "rejected_repairs": rejected,
            "tokens_per_accepted_repair": (
                accepted_actual_tokens // accepted_actual_rows
                if accepted_actual_rows
                else None
            ),
            "tokens_per_quality_point": (
                round(
                    accepted_actual_tokens / accepted_actual_quality_points,
                    2,
                )
                if accepted_actual_quality_points
                else None
            ),
            "estimated_tokens_per_accepted_repair": (
                accepted_estimated_tokens // accepted_estimated_rows
                if accepted_estimated_rows
                else None
            ),
            "estimated_tokens_per_quality_point": (
                round(
                    accepted_estimated_tokens
                    / accepted_estimated_quality_points,
                    2,
                )
                if accepted_estimated_quality_points
                else None
            ),
        },
    }


def budget_decision(
    actual: Mapping[str, Any],
    *,
    soft_tokens: int = 250_000,
    hard_tokens: int = 500_000,
) -> dict[str, Any]:
    """Evaluate the repair budget using non-cached input plus output."""

    soft = _non_negative_int(soft_tokens, "soft_tokens")
    hard = _non_negative_int(hard_tokens, "hard_tokens")
    if soft <= 0:
        raise ValueError("soft budget must be greater than zero")
    if hard < soft:
        raise ValueError("soft budget cannot exceed hard budget")
    used = _non_negative_int(
        actual.get("non_cached_input_tokens"),
        "non_cached_input_tokens",
    ) + _non_negative_int(actual.get("output_tokens"), "output_tokens")
    if used >= hard:
        status = "hard_stop"
    elif used >= soft:
        status = "soft_warning"
    elif used >= int(soft * 0.8):
        status = "approaching_soft"
    else:
        status = "ok"
    return {
        "basis": "non_cached_input_plus_output",
        "used_tokens": used,
        "soft_tokens": soft,
        "hard_tokens": hard,
        "status": status,
        "can_start_repair": status != "hard_stop",
    }


def new_token_usage_summary(
    *,
    soft_tokens: int = 250_000,
    hard_tokens: int = 500_000,
) -> dict[str, Any]:
    report = aggregate_events([])
    report.update(
        {
            "accounting_complete": False,
            "missing_segments": ["begin snapshot"],
            "budget": {
                "soft_tokens": soft_tokens,
                "hard_tokens": hard_tokens,
                "basis": "non_cached_input_plus_output",
            },
            "budget_status": budget_decision(
                report["actual"],
                soft_tokens=soft_tokens,
                hard_tokens=hard_tokens,
            ),
        }
    )
    return report


__all__ = [
    "MEASUREMENTS",
    "PHASES",
    "USAGE_KEYS",
    "UsageSnapshot",
    "aggregate_events",
    "budget_decision",
    "empty_usage",
    "new_token_usage_summary",
    "usage_delta",
]
