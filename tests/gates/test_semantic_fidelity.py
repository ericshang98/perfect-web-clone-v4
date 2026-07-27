from PIL import Image, ImageDraw

from core.gates.semantic_fidelity import (
    evaluate_contract,
    masked_ssim_2d,
)


def _save(path, color, size=(200, 120)):
    Image.new("RGB", size, color).save(path)
    return str(path)


def _video_contract():
    return {
        "schema": 1,
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "importance": "critical",
                "mode": "layout_behavior",
                "bounds": {"x": 10, "y": 10, "width": 80, "height": 100},
                "compare": [
                    "bounds",
                    "aspect_ratio",
                    "container_style",
                    "controls",
                    "interaction",
                ],
                "ignore_observations": ["media_frame_pixels"],
                "reason": "decoded live video frame changes independently of CSS",
            }
        ],
    }


def _matching_player_facts():
    return {
        "bounds": {"x": 10, "y": 10, "width": 80, "height": 100},
        "style": {
            "display": "block",
            "objectFit": "cover",
            "borderRadius": "0px",
        },
        "controls": ["play", "progress", "mute", "fullscreen"],
        "interaction": {"play_pause": True, "mute": True},
    }


def test_changing_video_pixels_do_not_fail_when_invariants_match(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    facts = {"player": _matching_player_facts()}

    report = evaluate_contract(
        ref_png=ref,
        cand_png=cand,
        contract=_video_contract(),
        ref_facts=facts,
        cand_facts=facts,
    )

    region = report["regions"][0]
    assert report["ok"] is True
    assert region["status"] == "pass"
    assert region["excluded_observations"] == ["media_frame_pixels"]
    assert region["score"] is None


def test_video_geometry_change_still_fails(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    ref_facts = {"player": _matching_player_facts()}
    changed = _matching_player_facts()
    changed["bounds"] = {"x": 10, "y": 10, "width": 72, "height": 100}

    report = evaluate_contract(
        ref_png=ref,
        cand_png=cand,
        contract=_video_contract(),
        ref_facts=ref_facts,
        cand_facts={"player": changed},
    )

    region = report["regions"][0]
    assert report["ok"] is False
    assert region["status"] == "fail"
    assert "bounds" in region["failed_invariants"]
    assert "aspect_ratio" in region["failed_invariants"]


def test_video_controls_change_still_fails(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    changed = _matching_player_facts()
    changed["controls"] = ["play"]

    report = evaluate_contract(
        ref,
        cand,
        _video_contract(),
        {"player": _matching_player_facts()},
        {"player": changed},
    )

    assert "controls" in report["regions"][0]["failed_invariants"]


def test_declared_behavior_must_replay_successfully(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    contract = _video_contract()
    contract["regions"][0]["compare"].append("behavior")
    contract["regions"][0]["behaviors"] = [
        {
            "id": "play-toggle",
            "trigger": '[data-pwc-interaction="play-toggle"]',
            "target": '[data-pwc-controlled="play-toggle"]',
            "assert": "visible",
        }
    ]
    expected = _matching_player_facts()
    expected["behavior"] = [{"id": "play-toggle", "passed": True}]
    broken = _matching_player_facts()
    broken["behavior"] = [{"id": "play-toggle", "passed": False}]

    report = evaluate_contract(
        ref,
        cand,
        contract,
        {"player": expected},
        {"player": broken},
    )

    assert "behavior" in report["regions"][0]["failed_invariants"]


def test_failed_source_behavior_replay_is_not_accepted_as_the_expectation(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    contract = _video_contract()
    contract["regions"][0]["compare"].append("behavior")
    contract["regions"][0]["behaviors"] = [
        {
            "id": "play-toggle",
            "trigger": '[data-pwc-interaction="play-toggle"]',
            "assert": "visible",
        }
    ]
    failed_source = _matching_player_facts()
    failed_source["behavior"] = [{"id": "play-toggle", "passed": False}]
    successful_clone = _matching_player_facts()
    successful_clone["behavior"] = [{"id": "play-toggle", "passed": True}]

    report = evaluate_contract(
        ref,
        cand,
        contract,
        {"player": failed_source},
        {"player": successful_clone},
    )

    assert "behavior" in report["regions"][0]["failed_invariants"]


def test_every_declared_behavior_id_must_have_replay_evidence(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")
    contract = _video_contract()
    contract["regions"][0]["compare"].append("behavior")
    contract["regions"][0]["behaviors"] = [
        {
            "id": "play-toggle",
            "trigger": '[data-pwc-interaction="play-toggle"]',
            "assert": "visible",
        },
        {
            "id": "settings-open",
            "trigger": '[data-pwc-interaction="settings"]',
            "assert": "visible",
        },
    ]
    incomplete_source = _matching_player_facts()
    incomplete_source["behavior"] = [{"id": "play-toggle", "passed": True}]
    incomplete_clone = _matching_player_facts()
    incomplete_clone["behavior"] = [{"id": "play-toggle", "passed": True}]

    report = evaluate_contract(
        ref,
        cand,
        contract,
        {"player": incomplete_source},
        {"player": incomplete_clone},
    )

    assert "behavior" in report["regions"][0]["failed_invariants"]


def test_static_image_pixels_remain_strict(tmp_path):
    ref = _save(tmp_path / "ref.png", "white")
    cand = _save(tmp_path / "cand.png", "black")
    contract = {
        "schema": 1,
        "regions": [
            {
                "id": "hero",
                "owner": "hero",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": {"x": 0, "y": 0, "width": 200, "height": 120},
                "compare": ["pixels"],
            }
        ],
    }

    bounds = contract["regions"][0]["bounds"]
    report = evaluate_contract(
        ref, cand, contract, {"hero": {"bounds": bounds}}, {"hero": {"bounds": bounds}}
    )

    assert report["ok"] is False
    assert report["regions"][0]["score"] < 0.1
    assert report["regions"][0]["failed_invariants"] == ["pixels"]


def test_static_pixels_always_enforce_bounds_even_when_contract_only_names_pixels(
    tmp_path,
):
    ref = _save(tmp_path / "ref.png", "white")
    cand = _save(tmp_path / "cand.png", "white")
    bounds = {"x": 0, "y": 0, "width": 120, "height": 100}
    contract = {
        "schema": 1,
        "regions": [
            {
                "id": "hero",
                "owner": "hero",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": bounds,
                "compare": ["pixels"],
            }
        ],
    }

    report = evaluate_contract(
        ref,
        cand,
        contract,
        {"hero": {"bounds": bounds}},
        {"hero": {"bounds": {**bounds, "x": 12}}},
    )

    assert report["ok"] is False
    assert report["regions"][0]["score"] == 1.0
    assert report["regions"][0]["failed_invariants"] == ["bounds"]


def test_static_pixels_also_enforce_declared_geometry(tmp_path):
    ref = _save(tmp_path / "ref.png", "white")
    cand = _save(tmp_path / "cand.png", "white")
    contract = {
        "schema": 1,
        "regions": [
            {
                "id": "hero",
                "owner": "hero",
                "importance": "critical",
                "mode": "static_pixels",
                "bounds": {"x": 0, "y": 0, "width": 200, "height": 120},
                "compare": ["pixels", "bounds", "aspect_ratio"],
            }
        ],
    }

    report = evaluate_contract(
        ref,
        cand,
        contract,
        {"hero": {"bounds": contract["regions"][0]["bounds"]}},
        {"hero": {"bounds": {"x": 0, "y": 0, "width": 180, "height": 120}}},
    )

    assert report["ok"] is False
    assert report["regions"][0]["score"] == 1.0
    assert report["regions"][0]["failed_invariants"] == [
        "bounds",
        "aspect_ratio",
    ]


def test_two_dimensional_exclusion_ignores_only_declared_rectangle(tmp_path):
    ref_image = Image.new("RGB", (200, 100), "white")
    cand_image = ref_image.copy()
    ImageDraw.Draw(ref_image).rectangle((0, 0, 99, 99), fill="red")
    ImageDraw.Draw(cand_image).rectangle((0, 0, 99, 99), fill="blue")

    unmasked = masked_ssim_2d(ref_image, cand_image, [])
    masked = masked_ssim_2d(
        ref_image,
        cand_image,
        [{"x": 0, "y": 0, "width": 100, "height": 100}],
    )

    assert unmasked["score"] < 0.9
    assert masked["score"] > 0.99
    assert 0.49 <= masked["excluded_fraction"] <= 0.51


def test_missing_candidate_facts_fail_layout_region(tmp_path):
    ref = _save(tmp_path / "ref.png", "red")
    cand = _save(tmp_path / "cand.png", "blue")

    report = evaluate_contract(
        ref,
        cand,
        _video_contract(),
        {"player": _matching_player_facts()},
        {},
    )

    assert report["ok"] is False
    assert report["regions"][0]["reason"] == "missing candidate facts"


def test_dynamic_measurements_are_bounded_before_returning(tmp_path):
    ref = _save(tmp_path / "ref.png", "white")
    cand = _save(tmp_path / "cand.png", "white")
    contract = {
        "schema": 1,
        "regions": [
            {
                "id": "player",
                "owner": "player",
                "importance": "important",
                "mode": "layout_behavior",
                "bounds": {"x": 0, "y": 0, "width": 100, "height": 100},
                "compare": [
                    "bounds",
                    "aspect_ratio",
                    "container_style",
                    "controls",
                ],
                "reason": "runtime video frames vary",
                "ignore_observations": ["media_frame_pixels"],
            }
        ],
    }
    facts = {
        "player": {
            "bounds": {"x": 0, "y": 0, "width": 100, "height": 100},
            "style": {"display": "block"},
            "controls": [
                f"control-{index}-" + "x" * 300
                for index in range(40)
            ],
        }
    }

    result = evaluate_contract(str(ref), str(cand), contract, facts, facts)
    measured = result["regions"][0]["measurements"]["candidate"]["controls"]

    assert len(measured) == 16
    assert all(len(value) <= 160 for value in measured)
