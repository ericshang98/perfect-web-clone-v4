"""core.gates.manifest_gate — replay the checklist on the clone and reconcile it.

The anti-Goodhart requirement (learned from the pagerie full-page-SSIM failure):
the metric must RANK candidates correctly — identical beats shifted, shifted
beats blank.
"""
import os

import pytest
from PIL import Image

from core.gates.fidelity import ssim_images
from core.gates.manifest_gate import reconcile, verify_manifest
from core.manifest import add_state, new_manifest


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


def _mk_manifest(tmp_path, ref_color=(200, 30, 30)):
    m = new_manifest("file://x", [800])
    refs = tmp_path / "refs" / "800"
    refs.mkdir(parents=True, exist_ok=True)
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


def test_verify_manifest_replays_required_menu_interaction(tmp_path):
    pytest.importorskip("playwright.sync_api")
    clone = tmp_path / "menu.html"
    clone.write_text(
        """
        <button id="menu-button" aria-controls="site-menu"
                aria-expanded="false">Menu</button>
        <nav id="site-menu" style="display:none">Navigation</nav>
        <script>
          document.querySelector('#menu-button').addEventListener('click', event => {
            const button = event.currentTarget;
            const menu = document.querySelector('#site-menu');
            const open = button.getAttribute('aria-expanded') !== 'true';
            button.setAttribute('aria-expanded', open ? 'true' : 'false');
            menu.style.display = open ? 'block' : 'none';
          });
        </script>
        """,
        encoding="utf-8",
    )
    m = new_manifest(clone.as_uri(), [800])
    add_state(
        m,
        {
            "id": "i_800_menu",
            "section": "header",
            "breakpoint": 800,
            "trigger": [{"kind": "click", "target": "#menu-button"}],
            "expect": {
                "observable": "aria_expanded_and_menu_visibility_toggle",
                "controlled": "#site-menu",
            },
            "channel": "interaction",
            "interaction_kind": "menu",
            "required": True,
            "evidence": None,
            "stability": "stable",
            "status": "pending",
        },
    )

    out = verify_manifest(
        m,
        clone_url=clone.as_uri(),
        base_dir=tmp_path,
        out_dir=tmp_path / "out-menu",
    )

    assert out["summary"]["ok"] is True
    assert out["states"][0]["status"] == "pass"
    assert out["states"][0]["observable"] == "aria_expanded_and_menu_visibility_toggle"


def test_broken_required_menu_interaction_is_a_hard_failure(tmp_path):
    pytest.importorskip("playwright.sync_api")
    clone = tmp_path / "broken-menu.html"
    clone.write_text(
        """
        <button id="menu-button" aria-controls="site-menu"
                aria-expanded="false">Menu</button>
        <nav id="site-menu" style="display:none">Navigation</nav>
        """,
        encoding="utf-8",
    )
    m = new_manifest(clone.as_uri(), [800])
    add_state(
        m,
        {
            "id": "i_800_menu",
            "section": "header",
            "breakpoint": 800,
            "trigger": [{"kind": "click", "target": "#menu-button"}],
            "expect": {
                "observable": "aria_expanded_and_menu_visibility_toggle",
                "controlled": "#site-menu",
            },
            "channel": "interaction",
            "interaction_kind": "menu",
            "required": True,
            "evidence": None,
            "stability": "stable",
            "status": "pending",
        },
    )

    out = verify_manifest(
        m,
        clone_url=clone.as_uri(),
        base_dir=tmp_path,
        out_dir=tmp_path / "out-broken-menu",
    )

    assert out["summary"]["ok"] is False
    assert out["states"][0]["status"] == "fail"


def test_verify_manifest_replays_required_native_accordion(tmp_path):
    pytest.importorskip("playwright.sync_api")
    clone = tmp_path / "accordion.html"
    clone.write_text(
        """
        <details>
          <summary data-pwc-interaction="shipping">Shipping</summary>
          <p>Tomorrow</p>
        </details>
        """,
        encoding="utf-8",
    )
    m = new_manifest(clone.as_uri(), [800])
    add_state(
        m,
        {
            "id": "i_800_shipping",
            "section": "faq",
            "breakpoint": 800,
            "trigger": [
                {
                    "kind": "click",
                    "target": '[data-pwc-interaction="shipping"]',
                }
            ],
            "expect": {"observable": "details_open_toggles"},
            "channel": "interaction",
            "interaction_kind": "accordion",
            "required": True,
            "evidence": None,
            "stability": "stable",
            "status": "pending",
        },
    )

    out = verify_manifest(
        m,
        clone_url=clone.as_uri(),
        base_dir=tmp_path,
        out_dir=tmp_path / "out-accordion",
    )

    assert out["summary"]["ok"] is True
    assert out["states"][0]["status"] == "pass"


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
