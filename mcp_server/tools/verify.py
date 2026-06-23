"""Fidelity-gate MCP tools for Perfect Web Clone v3.

Deterministic verification that the generated clone kept what the extractor
captured. The first gate here is **real links**: a section sub-agent must
reproduce the section's real ``href``s, not fabricate ``#`` / ``javascript:``
placeholders. ``verify_links`` reads each generated component from the sandbox
and reports, per section, whether every real navigational link survived — so the
orchestrator can re-dispatch any section that dropped them.

THE IRON RULE: no LLM here. This is filesystem reads + string checks (the
matching/aggregation logic lives in ``core.link_verifier``). All judgement
belongs to Claude Code.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from core import asset_verifier, link_verifier
from core.boxlite import get_sandbox
from core.extractor.storage import SourceStore


def _err(message: str, **extra: Any) -> Dict[str, Any]:
    return {"ok": False, "error": message, **extra}


def _load_page_url(store: SourceStore) -> str:
    """Best-effort page URL (for skipping same-page self/anchor links)."""
    sj = store.dir / "sections.json"
    if sj.is_file():
        try:
            return json.loads(sj.read_text(encoding="utf-8")).get("source_url", "") or ""
        except Exception:  # noqa: BLE001
            return ""
    return ""


async def _load_sections_and_sources(source_id: str):
    """Shared loader for the fidelity gates.

    Returns ``(sections, sources, page_url, None)`` on success, or
    ``(None, None, None, error_dict)`` on a setup failure. ``sources`` maps each
    section name to its generated component text (or ``None`` if unreadable).
    """
    store = SourceStore(source_id)
    full_path = store.dir / "sections_full.json"
    if not full_path.is_file():
        return None, None, None, _err(
            f"no section data for {source_id!r}; run get_section_plan first.",
            source_id=source_id,
        )
    try:
        sections = json.loads(full_path.read_text(encoding="utf-8")).get("sections", [])
    except Exception as exc:  # noqa: BLE001
        return None, None, None, _err(f"could not read section data: {exc}", source_id=source_id)

    sb = get_sandbox()
    if sb is None:
        return None, None, None, _err(
            "No sandbox exists yet; create the sandbox and assemble the project "
            "before verifying.",
            source_id=source_id,
        )

    sources: Dict[str, Any] = {}
    for sec in sections:
        name = sec.get("name")
        cp = sec.get("component_path")
        if not cp:
            sources[name] = None
            continue
        try:
            sources[name] = await sb.read_file(cp)
        except Exception:  # noqa: BLE001
            sources[name] = None
    return sections, sources, _load_page_url(store), None


async def verify_assets(source_id: str) -> Dict[str, Any]:
    """Verify each section uses the DOWNLOADED local assets, not hotlinks.

    After localization, an image with a local copy must be referenced by its
    ``/assets/...`` path. This reads each generated component and reports sections
    that still hotlink the CDN (when a local copy exists) or dropped the image.

    Returns ``{"ok", "source_id", "section_count", "passed", "failing",
    "unreadable", "summary"}``. ``failing`` entries carry ``hotlinked`` (remote
    URLs still used) and ``missing`` (local paths not referenced) — re-dispatch
    those sections. On setup errors: ``{"ok": False, "error"}``.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    sections, sources, _page_url, err = await _load_sections_and_sources(source_id)
    if err:
        return err

    result = asset_verifier.verify_sections_assets(sections, sources)
    result["source_id"] = source_id
    result["summary"] = (
        f"{len(result['passed'])}/{result['section_count']} sections use local assets"
        + (
            f"; {len(result['failing'])} hotlinking/missing, "
            f"{len(result['unreadable'])} unreadable"
            if not result["ok"]
            else ""
        )
    )
    return result


async def verify_links(source_id: str) -> Dict[str, Any]:
    """Verify every section kept its real links in the generated component.

    Loads the persisted section data for ``source_id``, reads each section's
    component from the sandbox, and checks the real ``href``s survived.

    Args:
        source_id: The id from ``extract_page`` (after ``get_section_plan`` and
            the section sub-agents have written their components).

    Returns:
        ``{"ok", "source_id", "section_count", "passed", "failing",
        "unreadable", "summary"}``. ``ok`` is true only when nothing is failing
        or unreadable. ``failing`` / ``unreadable`` list the sections to
        re-dispatch (each with ``name`` and ``component_path``); ``failing``
        entries also carry ``missing`` (the real link URLs that were dropped)
        and ``placeholder_count``. On setup errors: ``{"ok": False, "error"}``.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        return _err("source_id is required and must be a non-empty string.")
    source_id = source_id.strip()

    sections, sources, page_url, err = await _load_sections_and_sources(source_id)
    if err:
        return err

    result = link_verifier.verify_sections(sections, sources, page_url=page_url or None)
    result["source_id"] = source_id
    ok_n = len(result["passed"])
    total = result["section_count"]
    result["summary"] = (
        f"{ok_n}/{total} sections preserved all real links"
        + (
            f"; {len(result['failing'])} failing, {len(result['unreadable'])} unreadable"
            if not result["ok"]
            else ""
        )
    )
    return result


__all__ = ["verify_links", "verify_assets"]
