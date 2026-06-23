"""weight_gate (R3) — measure the transfer size of a built ``dist/``.

R3 says the output must be lightweight & fast: ``dist/`` total transfer ≤ budget
(default 120 KB gzipped, target 50–80 KB). Text assets (html/css/js) are gzipped
to estimate over-the-wire size; binary assets (images/fonts/video) are counted at
raw size since they're already compressed and aren't gzipped again in transit.

Pure / deterministic. No LLM.
"""

from __future__ import annotations

import gzip
import os
from typing import Any, Dict

# Map extension -> by_type bucket. Text buckets are gzipped; everything else is
# bucketed under "assets" and counted at raw size.
_TEXT_EXT_TO_TYPE = {
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".js": "js",
    ".mjs": "js",
    ".cjs": "js",
    ".jsx": "js",
    ".ts": "js",
    ".tsx": "js",
    ".json": "json",
    ".svg": "svg",
}

DEFAULT_BUDGET_KB = 120


def _gzipped_size(path: str) -> int:
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return 0
    return len(gzip.compress(raw, compresslevel=9))


def _raw_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def measure_dist(dirpath: str, budget_kb: int = DEFAULT_BUDGET_KB) -> Dict[str, Any]:
    """Sum transfer size of ``dirpath`` and compare to ``budget_kb``.

    Returns ``{ok, total_kb, budget_kb, by_type}`` where ``by_type`` always
    contains the ``html``/``css``/``js`` buckets (0 if absent) plus any other
    bucket present (``json``, ``svg``, ``assets``). Text assets are gzipped to
    estimate transfer; binary assets are counted at raw size.
    """
    by_type_bytes: Dict[str, int] = {"html": 0, "css": 0, "js": 0}

    for root, _dirs, names in os.walk(dirpath):
        for name in names:
            path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()
            bucket = _TEXT_EXT_TO_TYPE.get(ext)
            if bucket is not None:
                size = _gzipped_size(path)
            else:
                bucket = "assets"
                size = _raw_size(path)
            by_type_bytes[bucket] = by_type_bytes.get(bucket, 0) + size

    total_bytes = sum(by_type_bytes.values())
    total_kb = total_bytes / 1024.0
    by_type_kb = {k: round(v / 1024.0, 3) for k, v in by_type_bytes.items()}

    return {
        "ok": total_kb <= budget_kb,
        "total_kb": round(total_kb, 3),
        "budget_kb": budget_kb,
        "by_type": by_type_kb,
    }
