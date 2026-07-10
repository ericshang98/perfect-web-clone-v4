"""Tests for core.capture_residuals.find_canvas_residuals — surface canvas/WebGL
main visuals as explicit residuals instead of silently dropping them (a static
clone can't reproduce a canvas-drawn visual, but it must never pretend it covered
everything).
"""
from core.capture_residuals import find_canvas_residuals


def test_finds_large_canvas():
    dom = {"tag": "body", "children": [
        {"tag": "canvas", "id": "hero-gl",
         "rect": {"x": 0, "y": 0, "width": 1440, "height": 900}, "children": []}]}
    r = find_canvas_residuals(dom)
    assert len(r) == 1
    assert r[0]["kind"] == "canvas"
    assert r[0]["bounds"]["width"] == 1440


def test_ignores_tiny_canvas():
    dom = {"tag": "body", "children": [
        {"tag": "canvas", "rect": {"x": 0, "y": 0, "width": 10, "height": 10}, "children": []}]}
    assert find_canvas_residuals(dom) == []


def test_no_canvas_returns_empty():
    dom = {"tag": "body", "children": [
        {"tag": "div", "rect": {"x": 0, "y": 0, "width": 800, "height": 600}, "children": []}]}
    assert find_canvas_residuals(dom) == []


def test_finds_nested_canvas():
    dom = {"tag": "body", "children": [
        {"tag": "section", "children": [
            {"tag": "canvas", "rect": {"x": 0, "y": 0, "width": 1200, "height": 800}, "children": []}]}]}
    assert len(find_canvas_residuals(dom)) == 1
