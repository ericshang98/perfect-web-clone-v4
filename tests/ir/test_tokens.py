"""Task 2 — Design-token extractor."""

from core.ir.schema import DesignTokens
from core.ir.tokens import extract_tokens, tokenize_value


def test_dedup_colors():
    styles = [{"color": "#111111"}, {"color": "#111111"}, {"background": "#ffffff"}]
    t = extract_tokens(styles)
    assert len(t.colors) == 2  # #111111 and #ffffff, deduped


def test_returns_design_tokens():
    t = extract_tokens([{"color": "#111111"}])
    assert isinstance(t, DesignTokens)


def test_tokenize_value_known():
    styles = [{"color": "#111111"}]
    t = extract_tokens(styles)
    ref = tokenize_value("#111111", "color", t)
    assert ref.startswith("token.color.")


def test_tokenize_value_unknown_passthrough():
    styles = [{"color": "#111111"}]
    t = extract_tokens(styles)
    assert tokenize_value("#abcabc", "color", t) == "#abcabc"


def test_space_bucketing():
    styles = [
        {"gap": "16px"},
        {"padding": "16px"},
        {"margin": "32px"},
    ]
    t = extract_tokens(styles)
    assert "16px" in t.space.values()
    assert "32px" in t.space.values()
    ref = tokenize_value("16px", "space", t)
    assert ref.startswith("token.space.")


def test_radius_and_shadow_buckets():
    styles = [
        {"border-radius": "8px"},
        {"box-shadow": "0 1px 2px rgba(0,0,0,0.1)"},
    ]
    t = extract_tokens(styles)
    assert "8px" in t.radius.values()
    assert any(v.startswith("0 1px 2px") for v in t.shadow.values())


def test_deterministic_names():
    styles = [{"color": "#111111"}, {"color": "#ffffff"}]
    a = extract_tokens(styles)
    b = extract_tokens(styles)
    assert a.colors == b.colors  # stable / deterministic


def test_frequency_orders_names():
    # #111111 appears more often than #999999 -> gets the earlier (c1) name
    styles = [
        {"color": "#111111"},
        {"color": "#111111"},
        {"color": "#111111"},
        {"color": "#999999"},
    ]
    t = extract_tokens(styles)
    # find which name maps to which value
    name_for = {v: k for k, v in t.colors.items()}
    assert name_for["#111111"] < name_for["#999999"]
