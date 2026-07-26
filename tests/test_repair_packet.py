from core.repair_packet import build_repair_packet, select_worst_region


def _contract():
    return {
        "schema": 1,
        "regions": [
            {
                "id": "header",
                "owner": "header",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": {"x": 0, "y": 0, "width": 1440, "height": 70},
                "compare": ["pixels"],
            },
            {
                "id": "details",
                "owner": "details",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": {"x": 900, "y": 80, "width": 480, "height": 700},
                "compare": ["pixels"],
            },
        ],
    }


def _report():
    return {
        "regions": [
            {
                "id": "header",
                "owner": "header",
                "status": "fail",
                "score": 0.86,
                "source_crop": "/tmp/header-ref.png",
                "candidate_crop": "/tmp/header-cand.png",
                "diff_heatmap": "/tmp/header-diff.png",
                "measurements": {"ssim": 0.86},
            },
            {
                "id": "details",
                "owner": "details",
                "status": "fail",
                "score": 0.72,
                "source_crop": "/tmp/details-ref.png",
                "candidate_crop": "/tmp/details-cand.png",
                "diff_heatmap": "/tmp/details-diff.png",
                "measurements": {"ssim": 0.72},
            },
        ]
    }


def test_select_worst_region_prefers_lowest_failed_score():
    assert select_worst_region(_report())["id"] == "details"


def test_packet_contains_only_worst_region_and_relevant_sources():
    sources = {
        "src/components/sections/details/Details.jsx": "export default function Details() {}",
        "src/components/sections/details/Details.css": ".details { color: white; }",
        "src/components/sections/header/Header.jsx": "export default function Header() {}",
    }

    packet = build_repair_packet(
        _report(),
        _contract(),
        sources,
        max_text_bytes=16_384,
    )

    assert packet["target"]["id"] == "details"
    assert set(packet["sources"]) == {
        "src/components/sections/details/Details.jsx",
        "src/components/sections/details/Details.css",
    }
    assert packet["text_bytes"] <= 16_384
    assert packet["estimated_tokens"] <= 4096
    assert len(packet["candidate_regions"]) == 2


def test_packet_preserves_target_evidence_when_trimming():
    report = _report()
    sources = {
        "src/components/sections/details/Details.jsx": "x" * 10_000,
        "src/components/sections/details/Details.css": "y" * 10_000,
    }

    packet = build_repair_packet(
        report,
        _contract(),
        sources,
        max_text_bytes=2048,
    )

    assert packet["target"]["measurements"]
    assert packet["target"]["source_crop"]
    assert packet["target"]["candidate_crop"]
    assert packet["text_bytes"] <= 2048
    assert packet["truncated_fields"]


def test_packet_includes_previous_attempt_deltas_without_full_history():
    attempts = [
        {"target": "details", "before": 0.60, "after": 0.68, "note": "a" * 5000},
        {"target": "header", "before": 0.80, "after": 0.86},
        {"target": "details", "before": 0.68, "after": 0.72},
    ]

    packet = build_repair_packet(
        _report(),
        _contract(),
        {},
        attempts=attempts,
        max_text_bytes=4096,
    )

    assert packet["attempts"] == [
        {"target": "details", "before": 0.60, "after": 0.68},
        {"target": "details", "before": 0.68, "after": 0.72},
    ]
