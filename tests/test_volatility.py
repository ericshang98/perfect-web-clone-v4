import asyncio

from core.volatility import (
    build_volatility_summary,
    capture_volatility_samples,
    merge_volatility_samples,
)


def test_video_is_hint_not_automatic_waiver():
    summary = build_volatility_summary(
        [
            {
                "id": "player",
                "tag": "video",
                "bounds": {"x": 10, "y": 20, "width": 400, "height": 700},
                "changed_samples": 2,
                "total_samples": 3,
                "hint": "runtime_media",
            }
        ]
    )

    candidate = summary["candidates"][0]
    assert candidate["hint"] == "runtime_media"
    assert candidate["suggested_mode"] == "layout_behavior"
    assert candidate["requires_agent_decision"] is True


def test_static_image_remains_strict_hint():
    summary = build_volatility_summary(
        [
            {
                "id": "hero-image",
                "tag": "img",
                "bounds": {"x": 0, "y": 0, "width": 900, "height": 600},
                "changed_samples": 0,
                "total_samples": 3,
                "hint": "static_media",
            }
        ]
    )

    assert summary["candidates"][0]["suggested_mode"] == "static_pixels"


def test_temporal_samples_count_changes_without_repeating_signatures():
    samples = [
        [{"id": "clock", "tag": "time", "bounds": {"width": 40, "height": 20}, "signature": "10:00"}],
        [{"id": "clock", "tag": "time", "bounds": {"width": 40, "height": 20}, "signature": "10:01"}],
        [{"id": "clock", "tag": "time", "bounds": {"width": 40, "height": 20}, "signature": "10:01"}],
    ]

    records = merge_volatility_samples(samples)

    assert records[0]["changed_samples"] == 1
    assert records[0]["total_samples"] == 3
    assert "signature" not in records[0]


def test_summary_is_bounded_and_largest_candidates_win():
    records = [
        {
            "id": f"item-{index}",
            "tag": "div",
            "bounds": {"x": 0, "y": index, "width": index + 1, "height": 10},
            "changed_samples": 0,
            "total_samples": 1,
            "hint": "stateful_content",
        }
        for index in range(5)
    ]

    summary = build_volatility_summary(records, max_candidates=2)

    assert [item["id"] for item in summary["candidates"]] == ["item-4", "item-3"]
    assert summary["truncated"] == 3


def test_browser_sampling_merges_three_compact_inventories():
    class FakePage:
        def __init__(self):
            self.index = 0

        async def evaluate(self, _script):
            value = {
                "volatile_candidates": [
                    {
                        "id": "clock",
                        "tag": "time",
                        "bounds": {"width": 40, "height": 20},
                        "hint": "live_text",
                        "signature": f"10:0{self.index}",
                    }
                ]
            }
            self.index += 1
            return value

    summary = asyncio.run(
        capture_volatility_samples(
            FakePage(),
            "inventory-script",
            sample_count=3,
            interval_ms=0,
        )
    )

    assert summary["sample_count"] == 3
    assert summary["candidates"][0]["changed_samples"] == 2
