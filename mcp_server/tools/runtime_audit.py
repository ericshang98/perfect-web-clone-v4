"""Browser-owned runtime/responsive gates and composite candidate verification."""
from __future__ import annotations

import functools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import anyio

from core.boxlite import get_sandbox
from core.run_controller import harness_decision, record_gate_evidence
from core.runtime_audit import (
    collect_runtime_observations,
    evaluate_runtime_observations,
)
from mcp_server.run_ledger import require_owned_preview_url
from mcp_server.tools import build_deploy, pipeline, verify


_SOURCE_MARKER = ".pwc/source-id"
_RUN_LEDGER = ".pwc/run.json"
_RUNTIME_EVIDENCE = ".pwc/runtime-audit.json"


def _err(message: str, **extra: Any) -> Dict[str, Any]:
    return {"ok": False, "error": message, **extra}


async def _load_run(source_id: str):
    sandbox = get_sandbox()
    if sandbox is None:
        return None, None, _err("no active clone sandbox.", source_id=source_id)
    if await sandbox.read_file(_SOURCE_MARKER) != source_id:
        return sandbox, None, _err(
            "active sandbox belongs to another source.",
            source_id=source_id,
        )
    try:
        ledger = json.loads(await sandbox.read_file(_RUN_LEDGER) or "")
    except (json.JSONDecodeError, TypeError):
        ledger = None
    if not isinstance(ledger, dict) or not ledger.get("run_id"):
        return sandbox, None, _err(
            "run ledger is missing; assemble the project first.",
            source_id=source_id,
        )
    return sandbox, ledger, None


async def _persist(sandbox: Any, ledger: dict[str, Any]) -> None:
    ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
    await sandbox.write_file(
        _RUN_LEDGER,
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
    )


def _breakpoint_widths(values: list[Any]) -> list[int]:
    widths: list[int] = []
    for value in values:
        if isinstance(value, dict):
            value = value.get("width")
        try:
            width = int(value)
        except (TypeError, ValueError):
            continue
        if width > 0 and width not in widths:
            widths.append(width)
    return widths


def _interaction_gate_result(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Derive interaction status only from a complete interaction-state replay."""

    states = manifest.get("states")
    if not isinstance(states, list):
        return {
            "ok": False,
            "reason": "manifest execution produced no state evidence",
            "required_states": None,
            "observed_states": 0,
            "failed_states": [],
            "missing_states": None,
        }
    expected = manifest.get("interaction_states_expected")
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 0:
        return {
            "ok": False,
            "reason": "manifest omitted required interaction-state count",
            "required_states": None,
            "observed_states": 0,
            "failed_states": [],
            "missing_states": None,
        }
    interaction_rows = [
        row for row in states if row.get("channel") == "interaction"
    ]
    failed = [
        str(row.get("id"))
        for row in interaction_rows
        if row.get("status") != "pass"
    ]
    missing = max(0, expected - len(interaction_rows))
    return {
        "ok": not failed and missing == 0,
        "required_states": expected,
        "observed_states": len(interaction_rows),
        "failed_states": failed,
        "missing_states": missing,
    }


async def audit_runtime(
    source_id: str,
    url: str,
    breakpoints: Optional[list[int]] = None,
    viewport_height: int = 900,
    settle_ms: int = 800,
) -> Dict[str, Any]:
    """Measure runtime/resources/overflow at every required breakpoint."""

    source_id = str(source_id or "").strip()
    if not source_id:
        return _err("source_id is required.")
    if not isinstance(url, str) or not url.strip():
        return _err("url is required.", source_id=source_id)
    sandbox, ledger, error = await _load_run(source_id)
    if error:
        return error
    assert sandbox is not None and ledger is not None
    owned_url, ownership_error = await require_owned_preview_url(sandbox, url)
    if ownership_error:
        return _err(ownership_error, source_id=source_id)
    assert owned_url is not None
    widths = _breakpoint_widths(list(ledger.get("breakpoints") or []))
    for width in _breakpoint_widths(list(breakpoints or [])):
        if width not in widths:
            widths.append(width)
    for required in (1440, 390):
        if required not in widths:
            widths.append(required)
    try:
        observations = await anyio.to_thread.run_sync(
            functools.partial(
                collect_runtime_observations,
                owned_url,
                widths,
                viewport_height=int(viewport_height),
                settle_ms=int(settle_ms),
            )
        )
        report = evaluate_runtime_observations(
            owned_url,
            observations,
            required_breakpoints=widths,
        )
    except Exception as exc:  # noqa: BLE001
        observations = []
        failure = {
            "code": "runtime_audit_failed",
            "breakpoint": 0,
            "error": str(exc),
        }
        report = {
            "ok": False,
            "runtime": {"ok": False, "failures": [failure]},
            "responsive": {"ok": False, "failures": [failure]},
            "breakpoints": [],
        }
    evidence = {
        "schema": 1,
        "source_id": source_id,
        "url": owned_url,
        "required_breakpoints": widths,
        "observations": observations,
        "report": report,
    }
    await sandbox.write_file(
        _RUNTIME_EVIDENCE,
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
    )
    ledger = record_gate_evidence(
        ledger,
        gate="runtime",
        passed=bool(report["runtime"]["ok"]),
        evidence=[_RUNTIME_EVIDENCE],
        details=report["runtime"],
    )
    ledger = record_gate_evidence(
        ledger,
        gate="responsive",
        passed=bool(report["responsive"]["ok"]),
        evidence=[_RUNTIME_EVIDENCE],
        details=report["responsive"],
    )
    await _persist(sandbox, ledger)
    return {
        "ok": bool(report["ok"]),
        "source_id": source_id,
        "evidence": _RUNTIME_EVIDENCE,
        **report,
        **harness_decision(ledger),
    }


async def verify_harness_candidate(
    source_id: str,
    url: str,
    dist_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run every non-visual post-edit gate and stamp one fresh epoch."""

    sandbox, ledger, error = await _load_run(str(source_id or "").strip())
    if error:
        return error
    assert sandbox is not None and ledger is not None
    owned_url, ownership_error = await require_owned_preview_url(sandbox, url)
    if ownership_error:
        return _err(ownership_error, source_id=source_id)
    assert owned_url is not None
    results: dict[str, Any] = {}

    build = await build_deploy.build_project()
    results["build"] = build
    ledger = record_gate_evidence(
        ledger,
        gate="build",
        passed=bool(build.get("success")),
        evidence=[str(build.get("dist_dir") or "npm run build")],
        details={
            "exit_code": build.get("exit_code"),
            "errors": build.get("errors") or [],
        },
    )
    built_dist = str(build.get("dist_dir") or "")
    if dist_dir and (
        not built_dist
        or Path(dist_dir).resolve() != Path(built_dist).resolve()
    ):
        return _err(
            "dist_dir must match the canonical just-built dist directory.",
            source_id=source_id,
        )
    resolved_dist = built_dist
    fingerprints = (
        pipeline.check_fingerprints(resolved_dist)
        if resolved_dist
        else _err("build produced no dist directory")
    )
    results["fingerprints"] = fingerprints
    ledger = record_gate_evidence(
        ledger,
        gate="fingerprints",
        passed=bool(fingerprints.get("ok")),
        evidence=[resolved_dist or "missing dist"],
        details=fingerprints,
    )
    weight = (
        pipeline.check_weight(resolved_dist)
        if resolved_dist
        else _err("build produced no dist directory")
    )
    results["weight"] = weight
    ledger = record_gate_evidence(
        ledger,
        gate="weight",
        passed=bool(weight.get("ok")),
        evidence=[resolved_dist or "missing dist"],
        details=weight,
    )
    structure_result = await verify.score_clone_sections(
        source_id,
        url=owned_url,
    )
    results["critical_structure"] = structure_result
    structure = structure_result.get("structure") or {}
    structure_ok = bool(structure.get("ok"))
    structure_evidence = [
        str(
            structure_result.get("png")
            or structure_result.get("ref_png")
            or "score_clone_sections"
        )
    ]
    ledger = record_gate_evidence(
        ledger,
        gate="critical_structure",
        passed=structure_ok,
        evidence=structure_evidence,
        details=structure or {
            "ok": False,
            "error": structure_result.get("error")
            or "missing structure result",
        },
    )

    manifest = await verify.verify_manifest(source_id, owned_url)
    results["manifest"] = manifest
    manifest_evidence = [
        str(manifest.get("report") or "checklist.json")
    ]
    interaction_details = _interaction_gate_result(manifest)
    ledger = record_gate_evidence(
        ledger,
        gate="interactions",
        passed=bool(interaction_details["ok"]),
        evidence=manifest_evidence,
        details=interaction_details,
    )
    await _persist(sandbox, ledger)

    runtime = await audit_runtime(source_id, owned_url)
    results["runtime_responsive"] = runtime
    _, ledger, reload_error = await _load_run(source_id)
    if reload_error:
        return reload_error
    assert ledger is not None
    gates = {
        gate: (ledger.get("gate_results") or {}).get(gate)
        for gate in (
            "critical_structure",
            "interactions",
            "build",
            "fingerprints",
            "weight",
            "runtime",
            "responsive",
        )
    }
    return {
        "ok": all((result or {}).get("status") == "pass" for result in gates.values()),
        "source_id": source_id,
        "gates": gates,
        "results": results,
        **harness_decision(ledger),
    }


__all__ = ["audit_runtime", "verify_harness_candidate"]
