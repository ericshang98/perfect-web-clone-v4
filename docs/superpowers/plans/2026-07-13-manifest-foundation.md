# Manifest Foundation (M0+M1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teach the pwc4 pipeline to speak "state checklist": generate a per-site
`manifest.json` (baseline scroll states), verify it item-by-item against the live
clone via trigger replay, emit an HTML reconciliation report, and wire the loop into
the skill — Plan 1 of the interaction-layer program (spec:
`docs/superpowers/specs/2026-07-13-interaction-layer-design.md`, §3/§6/§7 + M0/M1).

**Architecture:** Pure-Python manifest schema + trigger vocabulary (`core/manifest.py`,
`core/trigger_replay.py`), a deterministic gate that replays each state on the running
clone and scores SSIM vs reference rasters (`core/gates/manifest_gate.py`), an HTML
report renderer (`core/manifest_report.py`), and two new LLM-free MCP tools
(`generate_manifest`, `verify_manifest`). Reuses `core/scroll_capture`,
`core/gates/fidelity`, `core/png_dims`, `SourceStore`. NO probes/evidence packs yet
(that's Plan 2 / M2) — baseline states only.

**Tech Stack:** Python 3.12, pytest, sync Playwright (`RUN_LIVE=1` convention for
browser tests), PIL, scikit-image SSIM (via existing `core/gates/fidelity`).

**Out of scope (later plans):** heuristic probes, evidence packs, interaction
recognizers, B-channel subagent authoring, asset-optimization stage.

---

## File map

| File | Responsibility |
|---|---|
| Create `core/manifest.py` | manifest dict schema: new/validate/add/update/save/load + `baseline_states` |
| Create `core/trigger_replay.py` | trigger vocabulary validation (pure) + sync-Playwright replay |
| Create `core/gates/manifest_gate.py` | `verify_manifest`: replay each state on clone, SSIM vs ref, statuses + side-by-side crops |
| Modify `core/gates/fidelity.py` | expose public `ssim_images(a_png, b_png)` (wraps `_ssim_images`) |
| Create `core/manifest_report.py` | deterministic HTML reconciliation report |
| Modify `mcp_server/tools/verify.py` | MCP tools `generate_manifest` + `verify_manifest` |
| Modify `mcp_server/server.py` | register the two tools |
| Modify `skill/SKILL.md` | wire checklist verify + self-heal loop into the operating procedure |
| Tests | `tests/test_manifest.py`, `tests/test_trigger_replay.py`, `tests/gates/test_manifest_gate.py`, `tests/test_manifest_report.py`, `tests/mcp/test_manifest_tools.py` |

Conventions honored: dict-based payloads (no dataclasses), Google-style docstrings with
"THE IRON RULE: no LLM here" framing in MCP tools, browser tests behind
`RUN_LIVE=1` + `pytest.importorskip("playwright")`, never silently drop items.

---

### Task 1: Manifest schema (`core/manifest.py`)

**Files:**
- Create: `core/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_manifest.py
"""core.manifest — the per-site state-checklist contract (spec §3).

Pure dict schema; the manifest is born at capture, verified at gate time,
shipped with the deliverable. Statuses: pending|pass|fail|waived.
"""
import json

import pytest

from core.manifest import (
    VALID_STATUSES,
    add_state,
    load_manifest,
    new_manifest,
    save_manifest,
    update_status,
    validate_state,
)


def _state(sid="s_scroll_0", **over):
    st = {
        "id": sid,
        "section": None,
        "breakpoint": 1440,
        "trigger": [{"kind": "scroll", "y": 0}],
        "expect": {"ref": f"refs/1440/{sid}.png", "ssim": 0.97,
                   "bounds": {"x": 0, "y": 0, "width": 1440, "height": 900}},
        "channel": "baseline",
        "evidence": None,
        "stability": "stable",
        "status": "pending",
    }
    st.update(over)
    return st


def test_new_manifest_shape():
    m = new_manifest("https://example.com", [1440, 375])
    assert m["url"] == "https://example.com"
    assert m["breakpoints"] == [1440, 375]
    assert m["states"] == []
    assert m["schema"] == 1


def test_validate_state_ok():
    assert validate_state(_state()) == []


def test_validate_state_rejects_bad_trigger_kind_and_status():
    errs = validate_state(_state(trigger=[{"kind": "teleport"}], status="maybe"))
    assert any("trigger" in e for e in errs)
    assert any("status" in e for e in errs)


def test_add_state_rejects_duplicate_id():
    m = new_manifest("u", [1440])
    add_state(m, _state())
    with pytest.raises(ValueError):
        add_state(m, _state())


def test_add_state_rejects_invalid_state():
    m = new_manifest("u", [1440])
    with pytest.raises(ValueError):
        add_state(m, _state(trigger=[{"kind": "teleport"}]))


def test_update_status_lifecycle():
    m = new_manifest("u", [1440])
    add_state(m, _state())
    update_status(m, "s_scroll_0", "pass")
    assert m["states"][0]["status"] == "pass"
    with pytest.raises(ValueError):
        update_status(m, "s_scroll_0", "nope")
    with pytest.raises(KeyError):
        update_status(m, "missing", "pass")
    assert VALID_STATUSES == {"pending", "pass", "fail", "waived"}


def test_save_load_roundtrip(tmp_path):
    m = new_manifest("u", [1440])
    add_state(m, _state())
    p = tmp_path / "manifest.json"
    save_manifest(m, p)
    assert load_manifest(p) == m
    # file is stable, human-diffable json
    assert json.loads(p.read_text(encoding="utf-8"))["states"][0]["id"] == "s_scroll_0"
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.manifest'`

- [ ] **Step 3: Implement `core/manifest.py`**

```python
"""The per-site state-checklist contract (interaction manifest).

"100% 复刻" is contracted as this finite checklist: breakpoints × observable
states × behaviors. Born at capture time, verified by
:mod:`core.gates.manifest_gate`, shipped with the deliverable. Statuses are the
honest vocabulary: pending | pass | fail | waived — `waived` is an explicit,
reported exemption; nothing is silently dropped.

Pure dict/JSON schema — no browser, no LLM.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SCHEMA_VERSION = 1
VALID_STATUSES = {"pending", "pass", "fail", "waived"}
VALID_STABILITY = {"stable", "unstable"}
TRIGGER_KINDS = {"scroll", "hover", "click", "wait", "viewport"}
_TRIGGER_REQUIRED = {
    "scroll": ("y",),
    "hover": ("target",),
    "click": ("target",),
    "wait": ("ms",),
    "viewport": ("width", "height"),
}


def new_manifest(url: str, breakpoints: List[int]) -> Dict[str, Any]:
    return {"schema": SCHEMA_VERSION, "url": url,
            "breakpoints": list(breakpoints), "states": []}


def validate_trigger(step: Dict[str, Any]) -> List[str]:
    kind = step.get("kind")
    if kind not in TRIGGER_KINDS:
        return [f"trigger kind {kind!r} not in {sorted(TRIGGER_KINDS)}"]
    missing = [k for k in _TRIGGER_REQUIRED[kind] if k not in step]
    return [f"trigger {kind!r} missing {missing}"] if missing else []


def validate_state(state: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    if not state.get("id"):
        errs.append("state missing id")
    if state.get("status") not in VALID_STATUSES:
        errs.append(f"status {state.get('status')!r} not in {sorted(VALID_STATUSES)}")
    if state.get("stability", "stable") not in VALID_STABILITY:
        errs.append(f"stability {state.get('stability')!r} invalid")
    trigger = state.get("trigger")
    if not isinstance(trigger, list) or not trigger:
        errs.append("trigger must be a non-empty list")
    else:
        for step in trigger:
            errs.extend(validate_trigger(step))
    expect = state.get("expect") or {}
    if state.get("channel") != "residual" and not expect.get("ref"):
        errs.append("non-residual state needs expect.ref")
    return errs


def add_state(manifest: Dict[str, Any], state: Dict[str, Any]) -> None:
    errs = validate_state(state)
    if errs:
        raise ValueError("; ".join(errs))
    if any(s["id"] == state["id"] for s in manifest["states"]):
        raise ValueError(f"duplicate state id {state['id']!r}")
    manifest["states"].append(state)


def update_status(manifest: Dict[str, Any], state_id: str, status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}")
    for s in manifest["states"]:
        if s["id"] == state_id:
            s["status"] = status
            return
    raise KeyError(state_id)


def save_manifest(manifest: Dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def load_manifest(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v` — Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add core/manifest.py tests/test_manifest.py
git commit -m "feat(manifest): state-checklist contract schema (spec §3)"
```

---

### Task 2: Baseline state generation (`baseline_states`)

**Files:**
- Modify: `core/manifest.py` (append function)
- Test: `tests/test_manifest.py` (append)

- [ ] **Step 1: Write failing tests** (append to `tests/test_manifest.py`)

```python
from core.manifest import baseline_states
from core.scroll_capture import scroll_capture_positions


def test_baseline_states_follow_scroll_positions():
    states = baseline_states(page_height=8000, viewport=(1440, 900), breakpoint=1440)
    ys = scroll_capture_positions(8000, 900, n=5)
    assert [s["trigger"][0]["y"] for s in states] == ys
    for s, y in zip(states, ys):
        assert s["id"] == f"s_1440_scroll_{y}"
        assert s["channel"] == "baseline"
        assert s["status"] == "pending"
        assert s["expect"]["ref"] == f"refs/1440/s_1440_scroll_{y}.png"
        assert s["expect"]["bounds"] == {"x": 0, "y": y, "width": 1440, "height": 900}
        assert validate_state(s) == []


def test_baseline_states_short_page_yields_at_least_initial():
    states = baseline_states(page_height=500, viewport=(1440, 900), breakpoint=1440)
    assert states and states[0]["trigger"] == [{"kind": "scroll", "y": 0}]
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v -k baseline`
Expected: FAIL — `ImportError: cannot import name 'baseline_states'`

- [ ] **Step 3: Implement** (append to `core/manifest.py`)

```python
def baseline_states(page_height: float, viewport: tuple[int, int],
                    breakpoint: int, ref_dir: str = "refs") -> List[Dict[str, Any]]:
    """M1 checklist seed: one state per scroll offset (no probes yet).

    Reuses :func:`core.scroll_capture.scroll_capture_positions` so the checklist
    aligns 1:1 with the multi-state reference rasters extraction already takes.
    """
    from core.scroll_capture import scroll_capture_positions

    vw, vh = viewport
    states = []
    for y in scroll_capture_positions(page_height, vh, n=5):
        sid = f"s_{breakpoint}_scroll_{y}"
        states.append({
            "id": sid, "section": None, "breakpoint": breakpoint,
            "trigger": [{"kind": "scroll", "y": y}],
            "expect": {"ref": f"{ref_dir}/{breakpoint}/{sid}.png", "ssim": 0.97,
                       "bounds": {"x": 0, "y": y, "width": vw, "height": vh}},
            "channel": "baseline", "evidence": None,
            "stability": "stable", "status": "pending",
        })
    return states
```

Note: if `scroll_capture_positions` returns an empty list for short pages, check its
actual behavior first (`sed -n '14,40p' core/scroll_capture.py`); if it already
returns `[0]` the second test passes as-is — do NOT add a redundant guard.

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_manifest.py -v` — Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add core/manifest.py tests/test_manifest.py
git commit -m "feat(manifest): baseline scroll states aligned with multi-state rasters"
```

---

### Task 3: Trigger replay (`core/trigger_replay.py`)

**Files:**
- Create: `core/trigger_replay.py`
- Test: `tests/test_trigger_replay.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_trigger_replay.py
"""core.trigger_replay — the tiny replayable trigger vocabulary (spec §3).

Triggers must replay deterministically on BOTH original and clone; anything
outside the vocabulary is a residual by definition. Pure validation always
runs; the Playwright executor follows the repo's RUN_LIVE=1 convention.
"""
import os

import pytest

from core.trigger_replay import replay_triggers, validate_triggers


def test_validate_ok_for_full_vocabulary():
    assert validate_triggers([
        {"kind": "scroll", "y": 100},
        {"kind": "hover", "target": ".card"},
        {"kind": "click", "target": ".dot"},
        {"kind": "wait", "ms": 50},
        {"kind": "viewport", "width": 375, "height": 667},
    ]) == []


def test_validate_reports_unknown_kind_and_missing_field():
    errs = validate_triggers([{"kind": "swipe"}, {"kind": "scroll"}])
    assert len(errs) == 2


@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="RUN_LIVE=1 only")
def test_replay_scroll_click_on_local_fixture(tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    fixture = tmp_path / "page.html"
    fixture.write_text(
        "<body style='margin:0'><div style='height:3000px'></div>"
        "<button id='b' onclick=\"this.textContent='clicked'\">go</button></body>",
        encoding="utf-8")
    with playwright.sync_playwright() as p:
        page = p.chromium.launch().new_page(viewport={"width": 800, "height": 600})
        page.goto(fixture.as_uri())
        replay_triggers(page, [
            {"kind": "scroll", "y": 1200},
            {"kind": "click", "target": "#b"},
            {"kind": "wait", "ms": 20},
        ])
        assert page.evaluate("window.scrollY") == 1200
        assert page.text_content("#b") == "clicked"
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_trigger_replay.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.trigger_replay'`

- [ ] **Step 3: Implement `core/trigger_replay.py`**

```python
"""Replay a manifest state's trigger script on a live page.

The vocabulary is deliberately tiny (scroll/hover/click/wait/viewport) because
every trigger must replay deterministically on BOTH the original site and the
clone — that is what makes "the behavior matches" provable. Validation is pure;
``replay_triggers`` drives a sync-Playwright ``Page`` provided by the caller.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.manifest import validate_trigger

_ACTION_TIMEOUT_MS = 5_000


def validate_triggers(triggers: List[Dict[str, Any]]) -> List[str]:
    errs: List[str] = []
    for step in triggers:
        errs.extend(validate_trigger(step))
    return errs


def replay_triggers(page: Any, triggers: List[Dict[str, Any]]) -> None:
    """Execute a validated trigger sequence. Raises on invalid input."""
    errs = validate_triggers(triggers)
    if errs:
        raise ValueError("; ".join(errs))
    for step in triggers:
        kind = step["kind"]
        if kind == "scroll":
            page.evaluate(f"window.scrollTo(0, {int(step['y'])})")
            page.wait_for_timeout(100)  # let scroll-linked effects settle
        elif kind == "hover":
            page.hover(step["target"], timeout=_ACTION_TIMEOUT_MS)
        elif kind == "click":
            page.click(step["target"], timeout=_ACTION_TIMEOUT_MS)
        elif kind == "wait":
            page.wait_for_timeout(int(step["ms"]))
        elif kind == "viewport":
            page.set_viewport_size(
                {"width": int(step["width"]), "height": int(step["height"])})
```

- [ ] **Step 4: Run to verify pass (both modes)**

Run: `.venv/bin/python -m pytest tests/test_trigger_replay.py -v` — Expected: 2 PASS, 1 skipped
Run: `RUN_LIVE=1 .venv/bin/python -m pytest tests/test_trigger_replay.py -v` — Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add core/trigger_replay.py tests/test_trigger_replay.py
git commit -m "feat(replay): deterministic trigger vocabulary + playwright executor"
```

---

### Task 4: Public `ssim_images` helper in fidelity gate

**Files:**
- Modify: `core/gates/fidelity.py` (add public wrapper near `_ssim_images`, line ~137)
- Test: `tests/gates/test_manifest_gate.py` (new file, first test here)

- [ ] **Step 1: Write failing test**

```python
# tests/gates/test_manifest_gate.py
"""core.gates.manifest_gate — replay the checklist on the clone and reconcile it.

The anti-Goodhart requirement (learned from the pagerie full-page-SSIM failure):
the metric must RANK candidates correctly — identical beats shifted, shifted
beats blank.
"""
from PIL import Image

from core.gates.fidelity import ssim_images


def _png(tmp_path, name, color, size=(200, 120)):
    p = tmp_path / name
    Image.new("RGB", size, color).save(p)
    return str(p)


def test_ssim_images_ranks_identical_above_different(tmp_path):
    a = _png(tmp_path, "a.png", (200, 30, 30))
    same = _png(tmp_path, "same.png", (200, 30, 30))
    diff = _png(tmp_path, "diff.png", (30, 30, 200))
    assert ssim_images(a, same) > ssim_images(a, diff)
    assert ssim_images(a, same) > 0.95
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/gates/test_manifest_gate.py -v`
Expected: FAIL — `ImportError: cannot import name 'ssim_images'`

- [ ] **Step 3: Implement** (add to `core/gates/fidelity.py`, after `_ssim_images`)

```python
def ssim_images(a_png: str, b_png: str) -> float:
    """Public file-path SSIM on the shared canvas (0..1) for other gates."""
    return _ssim_images(Image.open(a_png), Image.open(b_png))
```

- [ ] **Step 4: Run to verify pass + no regressions**

Run: `.venv/bin/python -m pytest tests/gates/ tests/test_fidelity_mask.py -v` — Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/gates/fidelity.py tests/gates/test_manifest_gate.py
git commit -m "feat(gates): public ssim_images helper for the manifest gate"
```

---

### Task 5: Manifest gate (`core/gates/manifest_gate.py`)

**Files:**
- Create: `core/gates/manifest_gate.py`
- Test: `tests/gates/test_manifest_gate.py` (append)

- [ ] **Step 1: Write failing tests** (append)

```python
import os

import pytest

from core.gates.manifest_gate import reconcile, verify_manifest
from core.manifest import add_state, new_manifest


def _mk_manifest(tmp_path, ref_color=(200, 30, 30)):
    m = new_manifest("file://x", [800])
    refs = tmp_path / "refs" / "800"
    refs.mkdir(parents=True)
    Image.new("RGB", (800, 600), ref_color).save(refs / "s_800_scroll_0.png")
    add_state(m, {
        "id": "s_800_scroll_0", "section": None, "breakpoint": 800,
        "trigger": [{"kind": "scroll", "y": 0}],
        "expect": {"ref": "refs/800/s_800_scroll_0.png", "ssim": 0.97,
                   "bounds": {"x": 0, "y": 0, "width": 800, "height": 600}},
        "channel": "baseline", "evidence": None,
        "stability": "stable", "status": "pending",
    })
    return m


def test_reconcile_summarizes_and_never_hides_items():
    rows = [{"id": "a", "status": "pass"}, {"id": "b", "status": "fail"},
            {"id": "c", "status": "waived"}, {"id": "d", "status": "pending"}]
    out = reconcile(rows)
    assert out == {"total": 4, "pass": 1, "fail": 1, "waived": 1,
                   "pending": 1, "ok": False}


def test_reconcile_ok_requires_all_pass_or_waived():
    assert reconcile([{"id": "a", "status": "pass"},
                      {"id": "b", "status": "waived"}])["ok"] is True


def test_residual_states_are_skipped_but_reported(tmp_path):
    m = _mk_manifest(tmp_path)
    add_state(m, {"id": "s_webgl", "section": None, "breakpoint": 800,
                  "trigger": [{"kind": "wait", "ms": 0}],
                  "expect": {}, "channel": "residual", "evidence": None,
                  "stability": "stable", "status": "pending"})
    # residual: no browser needed to know it can't be verified
    rows = verify_manifest(m, clone_url=None, base_dir=tmp_path,
                           out_dir=tmp_path / "out", dry_run=True)["states"]
    assert {r["id"]: r["status"] for r in rows}["s_webgl"] == "waived"
    assert {r["id"]: r["status"] for r in rows}["s_800_scroll_0"] == "pending"


@pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="RUN_LIVE=1 only")
def test_verify_manifest_passes_matching_clone_and_fails_wrong_one(tmp_path):
    pytest.importorskip("playwright.sync_api")
    clone = tmp_path / "clone.html"
    clone.write_text(
        "<body style='margin:0;background:rgb(200,30,30)'>"
        "<div style='height:600px'></div></body>", encoding="utf-8")
    m = _mk_manifest(tmp_path)  # ref = solid (200,30,30)
    out = verify_manifest(m, clone_url=clone.as_uri(), base_dir=tmp_path,
                          out_dir=tmp_path / "out")
    assert out["summary"]["pass"] == 1 and out["summary"]["ok"] is True
    assert m["states"][0]["status"] == "pass"
    # side-by-side evidence crop exists
    assert (tmp_path / "out" / "s_800_scroll_0_sbs.png").is_file()

    m2 = _mk_manifest(tmp_path, ref_color=(30, 200, 30))  # wrong ref
    out2 = verify_manifest(m2, clone_url=clone.as_uri(), base_dir=tmp_path,
                           out_dir=tmp_path / "out2")
    assert out2["summary"]["fail"] == 1 and out2["summary"]["ok"] is False
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/gates/test_manifest_gate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.gates.manifest_gate'`

- [ ] **Step 3: Implement `core/gates/manifest_gate.py`**

```python
"""Verify the state checklist on the LIVE clone (the reconciliation gate).

For each manifest state: replay its trigger script on the running clone
(same vocabulary that captured the reference), raster the viewport, score SSIM
vs the reference raster, write the status back into the manifest, and emit a
side-by-side evidence image. Residual-channel states are auto-waived (they are
reported, never verified, never hidden).

THE IRON RULE: no LLM here — replay + raster + SSIM + bookkeeping only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image

from core.gates.fidelity import ssim_images
from core.manifest import update_status
from core.trigger_replay import replay_triggers

_SETTLE_MS = 400


def reconcile(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {s: sum(1 for r in rows if r["status"] == s)
              for s in ("pass", "fail", "waived", "pending")}
    return {"total": len(rows), **counts,
            "ok": len(rows) > 0 and counts["fail"] == 0 and counts["pending"] == 0}


def _side_by_side(ref_png: str, cand_png: str, out_png: Path) -> None:
    a, b = Image.open(ref_png), Image.open(cand_png)
    h = max(a.height, b.height)
    canvas = Image.new("RGB", (a.width + b.width + 8, h), (255, 255, 255))
    canvas.paste(a, (0, 0)); canvas.paste(b, (a.width + 8, 0))
    canvas.save(out_png)


def verify_manifest(manifest: Dict[str, Any], clone_url: Optional[str],
                    base_dir: str | Path, out_dir: str | Path,
                    dry_run: bool = False) -> Dict[str, Any]:
    """Returns {states: [{id, status, ssim, ref, shot, sbs}], summary: {...}}."""
    base, out = Path(base_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []

    verifiable = [s for s in manifest["states"] if s["channel"] != "residual"]
    for s in manifest["states"]:
        if s["channel"] == "residual":
            update_status(manifest, s["id"], "waived")
            rows.append({"id": s["id"], "status": "waived",
                         "reason": "residual channel — reported, not verified"})

    if dry_run or not verifiable:
        rows.extend({"id": s["id"], "status": s["status"]} for s in verifiable)
        return {"states": rows, "summary": reconcile(rows)}

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for s in verifiable:
            bounds = (s.get("expect") or {}).get("bounds") or {}
            vw = int(bounds.get("width") or s["breakpoint"])
            vh = int(bounds.get("height") or 900)
            page = browser.new_page(viewport={"width": vw, "height": vh},
                                    device_scale_factor=1)
            row: Dict[str, Any] = {"id": s["id"]}
            try:
                page.goto(clone_url, wait_until="networkidle", timeout=60_000)
                replay_triggers(page, s["trigger"])
                page.wait_for_timeout(_SETTLE_MS)
                shot = out / f"{s['id']}.png"
                page.screenshot(path=str(shot))  # viewport raster = ref geometry
                ref = base / s["expect"]["ref"]
                if not ref.is_file():
                    row.update(status="pending", reason=f"missing ref {ref}")
                else:
                    score = ssim_images(str(ref), str(shot))
                    ok = score >= float(s["expect"].get("ssim", 0.97))
                    sbs = out / f"{s['id']}_sbs.png"
                    _side_by_side(str(ref), str(shot), sbs)
                    row.update(status="pass" if ok else "fail", ssim=score,
                               ref=str(ref), shot=str(shot), sbs=str(sbs))
            except Exception as exc:  # noqa: BLE001 — a state must never kill the run
                row.update(status="fail", reason=f"replay error: {exc}")
            finally:
                page.close()
            update_status(manifest, s["id"], row["status"]) if row["status"] in (
                "pass", "fail", "waived") else None
            rows.append(row)
        browser.close()

    return {"states": rows, "summary": reconcile(rows)}
```

- [ ] **Step 4: Run to verify pass (both modes)**

Run: `.venv/bin/python -m pytest tests/gates/test_manifest_gate.py -v` — Expected: 4 PASS, 1 skipped
Run: `RUN_LIVE=1 .venv/bin/python -m pytest tests/gates/test_manifest_gate.py -v` — Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add core/gates/manifest_gate.py tests/gates/test_manifest_gate.py
git commit -m "feat(gates): manifest reconciliation gate — replay checklist on live clone"
```

---

### Task 6: Reconciliation report (`core/manifest_report.py`)

**Files:**
- Create: `core/manifest_report.py`
- Test: `tests/test_manifest_report.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_manifest_report.py
"""core.manifest_report — the printed face of '100%': one row per checklist item."""
from core.manifest_report import render_report


ROWS = [
    {"id": "s_1440_scroll_0", "status": "pass", "ssim": 0.991,
     "sbs": "out/s_1440_scroll_0_sbs.png"},
    {"id": "s_carousel", "status": "fail", "ssim": 0.71, "sbs": "out/s_carousel_sbs.png"},
    {"id": "s_webgl", "status": "waived", "reason": "residual channel — reported, not verified"},
]
SUMMARY = {"total": 3, "pass": 1, "fail": 1, "waived": 1, "pending": 0, "ok": False}


def test_report_contains_every_item_and_summary(tmp_path):
    out = tmp_path / "report.html"
    render_report({"url": "https://x", "states": []}, ROWS, SUMMARY, out)
    html = out.read_text(encoding="utf-8")
    for r in ROWS:
        assert r["id"] in html
    assert "1 / 3" in html          # pass count over total
    assert "waived" in html and "residual" in html
    assert "0.991" in html and "0.71" in html
    assert 'src="out/s_carousel_sbs.png"' in html


def test_report_verdict_reflects_ok_flag(tmp_path):
    out = tmp_path / "r.html"
    render_report({"url": "u", "states": []}, ROWS,
                  {**SUMMARY, "fail": 0, "pending": 0, "ok": True}, out)
    assert "CHECKLIST GREEN" in out.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_manifest_report.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement `core/manifest_report.py`**

```python
"""Render the checklist reconciliation report (HTML).

This is what "100% 复刻" looks like when printed: one row per contracted state
— trigger, side-by-side evidence, SSIM, pass/fail/waived — plus an explicit
residual/waived section. Deterministic string building; no LLM, no templates.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, List

_BADGE = {"pass": "#16a34a", "fail": "#dc2626", "waived": "#ca8a04",
          "pending": "#6b7280"}


def render_report(manifest: Dict[str, Any], rows: List[Dict[str, Any]],
                  summary: Dict[str, Any], out_html: str | Path) -> None:
    verdict = ("CHECKLIST GREEN" if summary.get("ok")
               else "CHECKLIST NOT GREEN — see failing/pending items")
    parts = [
        "<!doctype html><meta charset='utf-8'><title>Reconciliation report</title>",
        "<body style='font:14px system-ui;margin:2rem'>",
        f"<h1>State checklist — {escape(str(manifest.get('url', '')))}</h1>",
        f"<p><strong>{verdict}</strong> · pass {summary['pass']} / {summary['total']}"
        f" (fail {summary['fail']}, waived {summary['waived']},"
        f" pending {summary['pending']})</p>",
        f"<p>Verdict shorthand: {summary['pass']} / {summary['total']} pass.</p>",
        "<table border='1' cellpadding='6' style='border-collapse:collapse'>",
        "<tr><th>state</th><th>status</th><th>ssim</th><th>evidence</th></tr>",
    ]
    for r in rows:
        color = _BADGE.get(r["status"], "#6b7280")
        ssim = f"{r['ssim']:.3f}".rstrip("0").rstrip(".") if r.get("ssim") is not None else "—"
        ev = (f"<img src=\"{escape(r['sbs'])}\" style='max-width:640px'>"
              if r.get("sbs") else escape(r.get("reason", "")))
        parts.append(
            f"<tr><td><code>{escape(r['id'])}</code></td>"
            f"<td style='color:{color};font-weight:600'>{r['status']}</td>"
            f"<td>{ssim}</td><td>{ev}</td></tr>")
    parts.append("</table></body>")
    Path(out_html).write_text("\n".join(parts), encoding="utf-8")
```

Note on the `"1 / 3"` assertion: it is satisfied by the `pass X / total` line.
Keep the SSIM formatting (`0.991`, `0.71`) exactly as asserted — format with
`:.3f` then strip trailing zeros.

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_manifest_report.py -v` — Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/manifest_report.py tests/test_manifest_report.py
git commit -m "feat(report): checklist reconciliation report (HTML)"
```

---

### Task 7: MCP tools `generate_manifest` + `verify_manifest`

**Files:**
- Modify: `mcp_server/tools/verify.py` (append two async tools, following the
  existing `capture_clone_sections`/`score_clone_sections` pattern: async def,
  `anyio.to_thread.run_sync` for browser work, `_err` for failures)
- Modify: `mcp_server/server.py` (register both next to line ~138 where
  `verify.capture_clone_sections` is listed)
- Test: `tests/mcp/test_manifest_tools.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/mcp/test_manifest_tools.py
"""MCP manifest tools — generate the checklist from a captured source and
verify it against the live clone. Deterministic; no LLM."""
import json

import pytest

from core.extractor.storage import SourceStore
from mcp_server.tools import verify as verify_tools


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    st = SourceStore("src_test")
    st.dir.mkdir(parents=True, exist_ok=True)
    (st.dir / "sections.json").write_text(
        json.dumps({"source_url": "https://example.com",
                    "viewport": {"width": 1440, "height": 900},
                    "page_height": 4000}), encoding="utf-8")
    return st


@pytest.mark.anyio
async def test_generate_manifest_writes_baseline_manifest(store):
    out = await verify_tools.generate_manifest(source_id="src_test")
    assert out["ok"] is True
    m = json.loads((store.dir / "manifest.json").read_text(encoding="utf-8"))
    assert m["url"] == "https://example.com"
    assert out["states"] == len(m["states"]) > 0
    assert all(s["channel"] == "baseline" for s in m["states"])


@pytest.mark.anyio
async def test_generate_manifest_missing_source_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("PWC3_SOURCES_DIR", str(tmp_path))
    out = await verify_tools.generate_manifest(source_id="nope")
    assert out["ok"] is False and "nope" in out["error"]


@pytest.mark.anyio
async def test_verify_manifest_requires_manifest(store):
    out = await verify_tools.verify_manifest(source_id="src_test", url="http://x")
    assert out["ok"] is False and "generate_manifest" in out["error"]
```

Check first how existing async MCP-tool tests drive anyio
(`grep -rn "anyio\|async def test" tests/mcp/ tests/test_verify_tool.py | head`) and
copy that exact convention (marker vs `anyio_backend` fixture) instead of the
`@pytest.mark.anyio` guess above if it differs.

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/mcp/test_manifest_tools.py -v`
Expected: FAIL — `AttributeError: ... no attribute 'generate_manifest'`

- [ ] **Step 3: Implement tools** (append to `mcp_server/tools/verify.py`)

```python
async def generate_manifest(source_id: str) -> Dict[str, Any]:
    """Generate the per-site state checklist (manifest.json) — M1: baseline states.

    Reads the captured source's url/viewport/page_height, seeds one state per
    scroll offset (aligned with the multi-state reference rasters), and writes
    ``manifest.json`` into the source dir. THE IRON RULE: no LLM here.
    """
    from core import manifest as mf

    store = SourceStore(source_id)
    sj = store.dir / "sections.json"
    if not sj.is_file():
        return _err(f"no captured source {source_id!r}; run extract_page first.",
                    source_id=source_id)
    meta = json.loads(sj.read_text(encoding="utf-8"))
    vp = meta.get("viewport") or {}
    vw, vh = int(vp.get("width", 1440)), int(vp.get("height", 900))
    page_h = float(meta.get("page_height") or 0)
    if page_h <= 0:
        return _err("source has no page_height; re-extract with current harness.",
                    source_id=source_id)
    m = mf.new_manifest(meta.get("source_url", ""), [vw])
    for st in mf.baseline_states(page_h, (vw, vh), vw):
        mf.add_state(m, st)
    mf.save_manifest(m, store.dir / "manifest.json")
    return {"ok": True, "source_id": source_id, "states": len(m["states"]),
            "manifest": str(store.dir / "manifest.json")}


async def verify_manifest(source_id: str, url: str) -> Dict[str, Any]:
    """Replay the checklist on the live clone and reconcile it (spec §6).

    Returns the per-state rows + summary; writes statuses back into
    manifest.json and renders report.html next to it.
    """
    from core.gates import manifest_gate
    from core import manifest as mf
    from core.manifest_report import render_report

    store = SourceStore(source_id)
    mpath = store.dir / "manifest.json"
    if not mpath.is_file():
        return _err(f"no manifest for {source_id!r}; run generate_manifest first.",
                    source_id=source_id)
    m = mf.load_manifest(mpath)
    out_dir = store.dir / "manifest_out"

    def _run():
        return manifest_gate.verify_manifest(m, url, store.dir, out_dir)

    result = await anyio.to_thread.run_sync(_run)
    mf.save_manifest(m, mpath)
    render_report(m, result["states"], result["summary"],
                  store.dir / "report.html")
    return {"ok": True, "source_id": source_id, **result,
            "report": str(store.dir / "report.html")}
```

Adjust field names to reality: if `sections.json` does not carry
`viewport`/`page_height` (check one real capture under `PWC3_SOURCES_DIR`,
e.g. `python -c "from core.extractor.storage import SourceStore; ..."` or inspect a
`showcase` era source dir), read `page_height` from the extraction raster via
`core.png_dims` instead, and default viewport to 1440×900 — note whichever you did in
the commit message.

- [ ] **Step 4: Register in `mcp_server/server.py`**

Add next to the existing verify registrations (around line 138):

```python
        verify.generate_manifest,
        verify.verify_manifest,
```

And extend the module docstring tool list (lines ~49-62) with one line each:

```
    * ``generate_manifest``  — write the per-site state checklist (baseline states)
    * ``verify_manifest``    — replay the checklist on the live clone + report
```

- [ ] **Step 5: Run to verify pass + full suite**

Run: `.venv/bin/python -m pytest tests/mcp/test_manifest_tools.py -v` — Expected: PASS
Run: `.venv/bin/python -m pytest -q` — Expected: full suite green (300+ tests)

- [ ] **Step 6: Commit**

```bash
git add mcp_server/tools/verify.py mcp_server/server.py tests/mcp/test_manifest_tools.py
git commit -m "feat(mcp): generate_manifest + verify_manifest tools (checklist contract)"
```

---

### Task 8: Wire the loop into the skill (M0 debt: self-heal actually closes)

**Files:**
- Modify: `skill/SKILL.md` (the verify/self-heal phase)

- [ ] **Step 1: Read the current loop**

Run: `grep -n "score\|self-heal\|iterate\|gate" skill/SKILL.md | head -30` and read the
surrounding phase text.

- [ ] **Step 2: Insert the wired loop instructions**

Add to the verify phase (adapt heading level to the file):

```markdown
### Gate-driven self-heal loop (run until green or 5 iterations)
1. `generate_manifest(source_id)` — once, right after extraction.
2. After every build: `score_clone_sections(source_id, url)` (static per-section R4)
   AND `verify_manifest(source_id, url)` (state checklist).
3. If any section/state fails: pick the WORST item (lowest SSIM), open its
   side-by-side evidence (`manifest_out/<id>_sbs.png`), repair ONLY that
   section/interaction, rebuild, re-run step 2.
4. Stop at all-green or after 5 iterations; report `report.html` + remaining
   fails/waived items explicitly — never claim done while items are red.
```

- [ ] **Step 3: Sanity-check + commit**

Run: `grep -n "verify_manifest" skill/SKILL.md` — Expected: present in the loop text.

```bash
git add skill/SKILL.md
git commit -m "docs(skill): wire manifest checklist + per-section gate into self-heal loop"
```

---

### Task 9: End-to-end smoke on a real showcase clone

**Files:** none created (verification task)

- [ ] **Step 1: Pick a served clone** — e.g. `showcase/products/pagerie-v4` (port 5192/5201
  family; start it with its usual `npm run preview`/`python -m http.server` route if down).

- [ ] **Step 2: Run the two tools end-to-end via a driver snippet**

```bash
RUN_LIVE=1 .venv/bin/python - <<'PY'
import anyio, json
from mcp_server.tools import verify as v
async def main():
    print(json.dumps(await v.generate_manifest(source_id="<real_source_id>"), indent=2)[:400])
    print(json.dumps(await v.verify_manifest(source_id="<real_source_id>",
                                             url="http://localhost:<port>"), indent=2)[:800])
anyio.run(main)
PY
```

(Fill `<real_source_id>` from `ls "$PWC3_SOURCES_DIR" 2>/dev/null || ls ~/.pwc3/sources 2>/dev/null` —
check `core/extractor/storage.py:48` for the default dir.)

- [ ] **Step 3: Open `report.html`, eyeball rows, confirm statuses look sane.**
  Expected: baseline states listed; pass/fail plausible vs what the clone actually
  looks like (anti-Goodhart eyeball: a good clone must not score worse than a broken one).

- [ ] **Step 4: Record findings** — append a short "M1 smoke" note (scores, gaps found)
  to `docs/superpowers/plans/2026-07-13-manifest-foundation.md` under a `## Smoke log`
  heading, commit.

```bash
git add docs/superpowers/plans/2026-07-13-manifest-foundation.md
git commit -m "docs(plan): M1 smoke log on real clone"
```

---

## Self-review notes

- **Spec coverage:** manifest schema (§3) → Tasks 1–2; trigger replay (§3) → Task 3;
  verify gate + statuses + evidence (§6) → Tasks 4–5; report (§7) → Task 6; MCP wiring
  (§6) → Task 7; self-heal loop wiring (M0 debt) → Task 8. NOT in this plan (by scope):
  probes/evidence (§4, Plan 2), channels A/B production (§5, Plans 2–3),
  asset-optimization (M0 item 3, its own small plan), branch landing (a release
  decision for Eric, not a code task).
- **Known uncertainty flagged inline:** exact `sections.json` fields (Task 7 step 3
  note), anyio test convention (Task 7 step 1 note), `scroll_capture_positions`
  short-page behavior (Task 2 step 3 note). Executors must resolve against real code,
  not assume.
- **Type consistency:** trigger dicts `{kind,...}` identical across Tasks 1/3/5;
  gate row shape `{id,status,ssim?,sbs?,reason?}` identical across Tasks 5/6/7.
