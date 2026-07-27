"""Deterministic runtime and responsive evidence collection/evaluation."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def _failure(code: str, breakpoint: int, **details: Any) -> dict[str, Any]:
    return {"code": code, "breakpoint": int(breakpoint), **details}


def _content_type_matches(resource_type: str, content_type: str) -> bool:
    value = content_type.lower().split(";", 1)[0].strip()
    expected = {
        "script": (
            "application/javascript",
            "text/javascript",
            "application/ecmascript",
            "text/ecmascript",
        ),
        "stylesheet": ("text/css",),
        "image": ("image/",),
        "media": ("audio/", "video/", "application/octet-stream"),
        "font": (
            "font/",
            "application/font",
            "application/vnd.ms-fontobject",
            "application/octet-stream",
        ),
    }.get(str(resource_type or "").lower())
    if not expected or not value:
        return True
    return any(value == prefix or value.startswith(prefix) for prefix in expected)


def evaluate_runtime_observations(
    page_url: str,
    observations: list[dict[str, Any]],
    *,
    required_breakpoints: list[int],
) -> dict[str, Any]:
    """Evaluate browser-owned observations without accepting Agent assertions."""

    allowed_origin = (
        f"{urlparse(page_url).scheme}://{urlparse(page_url).netloc}".lower()
    )
    runtime_failures: list[dict[str, Any]] = []
    responsive_failures: list[dict[str, Any]] = []
    seen: set[int] = set()
    for observation in observations:
        breakpoint = int(observation.get("breakpoint") or 0)
        seen.add(breakpoint)
        navigation = observation.get("navigation") or {}
        status = navigation.get("status")
        if (
            not navigation.get("ok")
            or not isinstance(status, int)
            or status >= 400
        ):
            runtime_failures.append(
                _failure(
                    "navigation_failed",
                    breakpoint,
                    status=status,
                    error=navigation.get("error"),
                )
            )
        for row in observation.get("console") or []:
            level = str(row.get("type") or "").lower()
            if level in {"warning", "warn", "error", "assert"}:
                runtime_failures.append(
                    _failure(
                        "console_error" if level in {"error", "assert"} else "console_warning",
                        breakpoint,
                        text=str(row.get("text") or ""),
                    )
                )
        for error in observation.get("page_errors") or []:
            runtime_failures.append(
                _failure("page_error", breakpoint, error=str(error))
            )
        for row in observation.get("request_failures") or []:
            # Chromium may cancel an in-flight media range request after it has
            # buffered enough data. That is not a broken clone when the media
            # element itself subsequently reports a usable readyState.
            if (
                str(row.get("resource_type") or "").lower() == "media"
                and "ERR_ABORTED" in str(row.get("error") or "")
                and any(
                    not media.get("error")
                    and int(media.get("readyState") or 0) > 0
                    for media in (observation.get("media") or [])
                )
            ):
                continue
            runtime_failures.append(
                _failure("request_failed", breakpoint, **dict(row))
            )
        for row in observation.get("http_errors") or []:
            runtime_failures.append(
                _failure("http_error", breakpoint, **dict(row))
            )
        for resource in observation.get("resources") or []:
            url = str(resource.get("url") or "")
            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"}:
                origin = f"{parsed.scheme}://{parsed.netloc}".lower()
                if origin != allowed_origin:
                    runtime_failures.append(
                        _failure(
                            "external_http_origin",
                            breakpoint,
                            url=url,
                            origin=origin,
                        )
                    )
            if not _content_type_matches(
                str(resource.get("resource_type") or ""),
                str(resource.get("content_type") or ""),
            ):
                runtime_failures.append(
                    _failure(
                        "resource_content_type_mismatch",
                        breakpoint,
                        url=url,
                        resource_type=resource.get("resource_type"),
                        content_type=resource.get("content_type"),
                    )
                )
        for font in observation.get("fonts") or []:
            # An unused @font-face legitimately remains "unloaded". Reject a
            # browser-owned load error or a family that CSS cannot resolve.
            if font.get("status") == "error" or font.get("check") is not True:
                runtime_failures.append(
                    _failure("font_not_loaded", breakpoint, **dict(font))
                )
        for image in observation.get("images") or []:
            if (
                image.get("complete") is True
                and int(image.get("naturalWidth") or 0) <= 0
            ) or (
                image.get("visible") is True
                and image.get("complete") is not True
            ):
                runtime_failures.append(
                    _failure("broken_image", breakpoint, **dict(image))
                )
        for media in observation.get("media") or []:
            if media.get("error") or (
                media.get("visible") is True
                and int(media.get("readyState") or 0) <= 0
            ):
                runtime_failures.append(
                    _failure("broken_media", breakpoint, **dict(media))
                )
        layout = observation.get("layout") or {}
        viewport_width = int(
            layout.get("viewport_width") or breakpoint or 0
        )
        scroll_width = int(layout.get("scroll_width") or 0)
        reachable = int(layout.get("reachable_scroll_x") or 0)
        if scroll_width > viewport_width + 1 or reachable > 1:
            responsive_failures.append(
                _failure(
                    "document_horizontal_overflow",
                    breakpoint,
                    viewport_width=viewport_width,
                    scroll_width=scroll_width,
                    reachable_scroll_x=reachable,
                    offenders=list(layout.get("offenders") or []),
                )
            )
    for breakpoint in required_breakpoints:
        if int(breakpoint) not in seen:
            responsive_failures.append(
                {"code": "missing_breakpoint", "breakpoint": int(breakpoint)}
            )
    runtime = {"ok": not runtime_failures, "failures": runtime_failures}
    responsive = {
        "ok": not responsive_failures,
        "failures": responsive_failures,
    }
    return {
        "ok": runtime["ok"] and responsive["ok"],
        "runtime": runtime,
        "responsive": responsive,
        "breakpoints": sorted(seen),
    }


def collect_runtime_observations(
    url: str,
    breakpoints: list[int],
    *,
    viewport_height: int = 900,
    settle_ms: int = 800,
) -> list[dict[str, Any]]:
    """Capture browser-owned runtime evidence at every required breakpoint."""

    from playwright.sync_api import sync_playwright

    observations: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for width in breakpoints:
                page = browser.new_page(
                    viewport={"width": int(width), "height": int(viewport_height)}
                )
                console: list[dict[str, str]] = []
                page_errors: list[str] = []
                request_failures: list[dict[str, Any]] = []
                http_errors: list[dict[str, Any]] = []
                resources: list[dict[str, Any]] = []
                page.on(
                    "console",
                    lambda message, bucket=console: bucket.append(
                        {"type": message.type, "text": message.text}
                    ),
                )
                page.on(
                    "pageerror",
                    lambda error, bucket=page_errors: bucket.append(str(error)),
                )
                page.on(
                    "requestfailed",
                    lambda request, bucket=request_failures: bucket.append(
                        {
                            "url": request.url,
                            "resource_type": request.resource_type,
                            "error": (
                                request.failure
                                if isinstance(request.failure, str)
                                else str(request.failure or "")
                            ),
                        }
                    ),
                )

                def _response(response):
                    content_type = response.headers.get("content-type", "")
                    row = {
                        "url": response.url,
                        "status": response.status,
                        "resource_type": response.request.resource_type,
                        "content_type": content_type,
                    }
                    resources.append(row)
                    if response.status >= 400:
                        http_errors.append(
                            {"url": response.url, "status": response.status}
                        )

                page.on("response", _response)
                navigation: dict[str, Any]
                try:
                    response = page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=30_000,
                    )
                    navigation = {
                        "ok": response is not None and response.status < 400,
                        "status": response.status if response is not None else None,
                        "error": None if response is not None else "no response",
                    }
                except Exception as exc:  # noqa: BLE001
                    navigation = {"ok": False, "status": None, "error": str(exc)}
                page.wait_for_timeout(max(0, int(settle_ms)))
                evidence = page.evaluate(
                    """() => {
                      const selector = (el) => {
                        if (el.id) return `#${CSS.escape(el.id)}`;
                        const cls = [...el.classList].slice(0, 2)
                          .map((x) => `.${CSS.escape(x)}`).join('');
                        return `${el.tagName.toLowerCase()}${cls}`;
                      };
                      const clipped = (el) => {
                        let parent = el.parentElement;
                        while (parent && parent !== document.documentElement) {
                          const style = getComputedStyle(parent);
                          if (['hidden','clip','auto','scroll'].includes(style.overflowX)) {
                            return true;
                          }
                          parent = parent.parentElement;
                        }
                        return false;
                      };
                      const offenders = [...document.querySelectorAll('body *')]
                        .filter((el) => {
                          const rect = el.getBoundingClientRect();
                          return !clipped(el) &&
                            (rect.right > innerWidth + 1 || rect.left < -1);
                        }).slice(0, 20).map((el) => {
                          const rect = el.getBoundingClientRect();
                          return {selector: selector(el), left: rect.left,
                            right: rect.right, width: rect.width};
                        });
                      const contained = [...document.querySelectorAll('body *')]
                        .filter((el) => el.scrollWidth > el.clientWidth + 1 &&
                          ['hidden','clip','auto','scroll'].includes(
                            getComputedStyle(el).overflowX))
                        .slice(0, 20).map((el) => ({selector: selector(el),
                          client_width: el.clientWidth,
                          scroll_width: el.scrollWidth}));
                      const oldX = scrollX;
                      scrollTo(1e7, scrollY);
                      const reachable = scrollX;
                      scrollTo(oldX, scrollY);
                      return {
                        fonts: [...document.fonts].map((font) => {
                          let check = false;
                          let check_error = null;
                          try {
                            // FontFace.weight may be a variable-font range
                            // such as "400 800", which is invalid in the
                            // document.fonts.check() shorthand. The face's own
                            // status checks the concrete resource; the family
                            // probe verifies CSS usability without reusing the
                            // potentially ranged descriptor.
                            check = document.fonts.check(
                              `16px ${JSON.stringify(font.family)}`);
                          } catch (error) {
                            check_error = String(error);
                          }
                          return {family: font.family, status: font.status,
                            check, check_error};
                        }),
                        images: [...document.images].map((image) => {
                          const rect = image.getBoundingClientRect();
                          return {
                            src: image.currentSrc || image.src,
                            complete: image.complete,
                            naturalWidth: image.naturalWidth,
                            loading: image.loading || null,
                            visible: rect.bottom > 0 && rect.right > 0 &&
                              rect.top < innerHeight && rect.left < innerWidth
                          };
                        }),
                        media: [...document.querySelectorAll('video,audio')].map((media) => {
                          const rect = media.getBoundingClientRect();
                          return {
                            src: media.currentSrc || media.src,
                            readyState: media.readyState,
                            error: media.error ? media.error.message || String(media.error.code) : null,
                            visible: rect.bottom > 0 && rect.right > 0 &&
                              rect.top < innerHeight && rect.left < innerWidth
                          };
                        }),
                        layout: {
                          viewport_width: innerWidth,
                          scroll_width: document.documentElement.scrollWidth,
                          reachable_scroll_x: reachable,
                          offenders,
                          contained_overflows: contained
                        }
                      };
                    }"""
                )
                observations.append(
                    {
                        "breakpoint": int(width),
                        "navigation": navigation,
                        "console": console,
                        "page_errors": page_errors,
                        "request_failures": request_failures,
                        "http_errors": http_errors,
                        "resources": resources,
                        **evidence,
                    }
                )
                page.close()
        finally:
            browser.close()
    return observations


__all__ = [
    "collect_runtime_observations",
    "evaluate_runtime_observations",
]
