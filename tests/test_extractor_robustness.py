"""Tests for core.extractor.robustness — site-agnostic extraction hardening.

Two general gaps these guard against (NOT site-specific tuning):
1. Dead source: the target returns an HTTP error / "site down" page. The system
   must detect it and fail clearly, never clone an error page.
2. No time budget: heavy in-page passes (huge SPA DOM, CSS enumeration) run
   unbounded and hang the whole extraction. Each pass must be time-boxed and
   degrade to a fallback instead of stalling forever.
"""

import asyncio

from core.extractor import robustness


# --- dead-source detection ---

def test_is_error_status_flags_4xx_5xx():
    assert robustness.is_error_status(404) is True
    assert robustness.is_error_status(503) is True
    assert robustness.is_error_status(521) is True  # Cloudflare "web server is down"


def test_is_error_status_allows_success_and_redirect():
    assert robustness.is_error_status(200) is False
    assert robustness.is_error_status(301) is False


def test_is_error_status_none_is_not_an_error():
    # Some navigations (file://, data:) have no HTTP status — don't false-positive.
    assert robustness.is_error_status(None) is False


# --- time-boxed evaluate ---

def test_eval_budgeted_returns_value_when_fast():
    async def fast():
        return {"ok": 1}

    out = asyncio.run(robustness.eval_budgeted(fast(), 1.0, fallback={}))
    assert out == {"ok": 1}


def test_eval_budgeted_returns_fallback_on_timeout():
    async def slow():
        await asyncio.sleep(5)
        return "late"

    out = asyncio.run(robustness.eval_budgeted(slow(), 0.05, fallback="FB"))
    assert out == "FB"


def test_eval_budgeted_returns_fallback_on_error():
    async def boom():
        raise RuntimeError("page crashed")

    out = asyncio.run(robustness.eval_budgeted(boom(), 1.0, fallback=[]))
    assert out == []
