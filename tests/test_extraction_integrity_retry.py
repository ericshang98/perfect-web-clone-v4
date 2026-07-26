import asyncio
import json

from core.extractor import api
from core.extractor.models import ExtractionResult, PageMetadata


def _metadata():
    return PageMetadata(
        url="https://example.com",
        title="Example",
        viewport_width=1440,
        viewport_height=900,
        page_width=1440,
        page_height=2000,
        total_elements=10,
        max_depth=4,
        load_time_ms=20,
    )


def _result(status: str):
    ok = status == "passed"
    return ExtractionResult(
        success=ok,
        message="extracted" if ok else "capture integrity failed",
        error=None if ok else "capture_integrity_failed",
        metadata=_metadata(),
        capture_integrity={
            "ok": ok,
            "status": status,
            "issues": [] if ok else [{"code": "critical_region_missing"}],
            "missing_critical": [] if ok else ["hero"],
        },
        raw_structure={"page": {"height": 2000}, "regions": []},
        normalized_structure={"page": {"height": 2000}, "regions": []},
        interactions=[],
    )


class _FakeService:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    async def extract(self, url, options):
        self.calls += 1
        return self.results.pop(0)


def test_extract_retries_integrity_failure_and_promotes_third_valid_attempt(
    tmp_path, monkeypatch
):
    service = _FakeService([_result("failed"), _result("failed"), _result("passed")])
    monkeypatch.setattr(api, "_get_service", lambda: service)

    response = asyncio.run(
        api.aextract_page(
            "https://example.com",
            {"max_capture_attempts": 3},
            storage_root=tmp_path,
        )
    )

    assert service.calls == 3
    assert response["summary"]["success"] is True
    assert response["summary"]["capture_attempts"] == 3
    assert response["summary"]["capture_integrity"]["status"] == "passed"
    source = tmp_path / response["source_id"]
    assert (source / "attempts/01/capture_integrity.json").is_file()
    assert (source / "attempts/02/capture_integrity.json").is_file()
    assert (source / "capture_integrity.json").is_file()


def test_extract_hard_fails_after_three_inconsistent_attempts(tmp_path, monkeypatch):
    service = _FakeService(
        [_result("failed"), _result("failed"), _result("failed"), _result("passed")]
    )
    monkeypatch.setattr(api, "_get_service", lambda: service)

    response = asyncio.run(
        api.aextract_page(
            "https://example.com",
            {"max_capture_attempts": 3},
            storage_root=tmp_path,
        )
    )

    assert service.calls == 3
    assert response["summary"]["success"] is False
    assert response["summary"]["capture_attempts"] == 3
    assert response["summary"]["capture_integrity"]["status"] == "failed"
    source = tmp_path / response["source_id"]
    manifest = json.loads((source / "manifest.json").read_text())
    assert manifest["success"] is False
    assert manifest["capture_integrity"]["status"] == "failed"


def test_extract_persists_compact_volatility_evidence(tmp_path, monkeypatch):
    result = _result("passed")
    result.raw_structure["volatile_candidates"] = [
        {
            "id": "player",
            "tag": "video",
            "bounds": {"x": 20, "y": 40, "width": 400, "height": 700},
            "hint": "runtime_media",
            "signature": "1.2|false|4",
        }
    ]
    result.raw_structure["volatility_summary"] = {
        "schema": 1,
        "sample_count": 3,
        "candidates": [
            {
                "id": "player",
                "tag": "video",
                "bounds": {"x": 20, "y": 40, "width": 400, "height": 700},
                "hint": "runtime_media",
                "changed_samples": 2,
                "total_samples": 3,
                "suggested_mode": "layout_behavior",
                "requires_agent_decision": True,
            }
        ],
        "truncated": 0,
    }
    service = _FakeService([result])
    monkeypatch.setattr(api, "_get_service", lambda: service)

    response = asyncio.run(
        api.aextract_page(
            "https://example.com",
            {"max_capture_attempts": 1},
            storage_root=tmp_path,
        )
    )

    source = tmp_path / response["source_id"]
    evidence = json.loads(
        (source / "evidence/volatility_summary.json").read_text(encoding="utf-8")
    )
    assert evidence["candidates"][0]["id"] == "player"
    assert evidence["candidates"][0]["suggested_mode"] == "layout_behavior"
    assert evidence["candidates"][0]["changed_samples"] == 2
    assert "signature" not in evidence["candidates"][0]
