"""Provider usage collectors with a deterministic observable-text fallback."""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from core.token_accounting import UsageSnapshot


_THREAD_ID_RE = re.compile(r"^[A-Za-z0-9-]+$")


class UsageCollector(Protocol):
    def snapshot(self) -> UsageSnapshot | None:
        """Return the newest cumulative provider snapshot, if available."""


class CodexSessionCollector:
    """Read only cumulative ``token_count`` metadata for the active Codex task."""

    def __init__(
        self,
        *,
        thread_id: str | None = None,
        roots: Sequence[Path] | None = None,
        model: str | None = None,
    ) -> None:
        resolved_thread = str(
            thread_id if thread_id is not None else os.getenv("CODEX_THREAD_ID", "")
        ).strip()
        if resolved_thread and not _THREAD_ID_RE.fullmatch(resolved_thread):
            raise ValueError("invalid Codex thread id")
        self.thread_id = resolved_thread
        self.roots = list(
            roots
            if roots is not None
            else (
                Path.home() / ".codex" / "sessions",
                Path.home() / ".codex" / "archived_sessions",
            )
        )
        self.model = str(
            model if model is not None else os.getenv("CODEX_MODEL", "")
        )

    def _candidate_files(self) -> list[Path]:
        if not self.thread_id:
            return []
        candidates: list[Path] = []
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in root.rglob("*.jsonl"):
                if self.thread_id in path.name:
                    candidates.append(path)
        return sorted(
            candidates,
            key=lambda path: (path.stat().st_mtime_ns, str(path)),
        )

    def snapshot(self) -> UsageSnapshot | None:
        latest: UsageSnapshot | None = None
        for path in self._candidate_files():
            try:
                handle = path.open("r", encoding="utf-8")
            except OSError:
                continue
            with handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    if record.get("type") != "event_msg":
                        continue
                    payload = record.get("payload") or {}
                    if payload.get("type") != "token_count":
                        continue
                    usage = (payload.get("info") or {}).get("total_token_usage")
                    if not isinstance(usage, Mapping):
                        continue
                    try:
                        latest = explicit_snapshot(
                            "codex",
                            {
                                **usage,
                                "model": self.model,
                                "session_id": self.thread_id,
                            },
                        )
                    except (TypeError, ValueError):
                        continue
        return latest


def explicit_snapshot(
    provider: str,
    usage: Mapping[str, Any],
) -> UsageSnapshot:
    """Normalize usage returned directly by a model host."""

    provider_name = str(provider or "").strip()
    if not provider_name:
        raise ValueError("provider is required")
    return UsageSnapshot.from_mapping(
        {
            "provider": provider_name,
            "model": usage.get("model"),
            "session_id": usage.get("session_id"),
            "input_tokens": usage.get("input_tokens"),
            "cached_input_tokens": usage.get("cached_input_tokens"),
            "cache_write_input_tokens": usage.get(
                "cache_write_input_tokens"
            ),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_output_tokens": usage.get(
                "reasoning_output_tokens"
            ),
        }
    )


def estimate_observable_tokens(text_bytes: int) -> int:
    """Estimate observable text at four UTF-8 bytes per Token, rounded up."""

    if isinstance(text_bytes, bool):
        raise ValueError("text_bytes must be a non-negative integer")
    try:
        size = int(text_bytes)
    except (TypeError, ValueError) as exc:
        raise ValueError("text_bytes must be a non-negative integer") from exc
    if size < 0:
        raise ValueError("text_bytes must be non-negative")
    return math.ceil(size / 4)


__all__ = [
    "CodexSessionCollector",
    "UsageCollector",
    "estimate_observable_tokens",
    "explicit_snapshot",
]
