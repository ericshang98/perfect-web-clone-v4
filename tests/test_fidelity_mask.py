"""R4 region-masking — exclude a known third-party-overlay region (e.g. a Klaviyo
popup baked into the reference raster) from the SSIM score, WITHOUT letting a real
fidelity miss be masked away. Masks are normalized y-fractions [0,1]; the report
flags an oversized mask loudly (never silent)."""
import numpy as np
from PIL import Image

from core.gates import fidelity
from core.visual_diff import ssim_score


def _save(arr, p):
    Image.fromarray(arr.astype("uint8"), "L").save(p)


def _popup_pair(tmp_path):
    """Identical pages except the reference has a 'popup' across the top quarter."""
    base = np.full((256, 256), 200, dtype=np.uint8)
    ref, cand = base.copy(), base.copy()
    ref[:64, :] = 30  # the popup, only in the reference top 25%
    rp, cp = tmp_path / "ref.png", tmp_path / "cand.png"
    _save(ref, rp); _save(cand, cp)
    return str(rp), str(cp)


def test_unmasked_score_penalized_by_top_difference(tmp_path):
    rp, cp = _popup_pair(tmp_path)
    assert fidelity.score(rp, cp) < 0.95  # the popup drags the score down


def test_masking_the_popup_band_recovers_score(tmp_path):
    rp, cp = _popup_pair(tmp_path)
    masked = fidelity.score(rp, cp, mask_regions=[{"y0": 0.0, "y1": 0.25}])
    assert masked > 0.98  # excluding the popup band → near-identical


def test_no_mask_equals_plain_ssim(tmp_path):
    rp, cp = _popup_pair(tmp_path)
    assert fidelity.score(rp, cp) == ssim_score(rp, cp)


def test_report_flags_oversized_mask(tmp_path):
    rp, cp = _popup_pair(tmp_path)
    big = fidelity.score_report(rp, cp, mask_regions=[{"y0": 0.0, "y1": 0.5}])
    assert big["masked_fraction"] >= 0.5
    assert big["mask_oversized"] is True   # > cap → flagged, not silently accepted
    small = fidelity.score_report(rp, cp, mask_regions=[{"y0": 0.0, "y1": 0.1}])
    assert small["mask_oversized"] is False
    assert small["masked_regions"] == [{"y0": 0.0, "y1": 0.1}]  # logged
