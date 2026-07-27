from playwright.sync_api import sync_playwright


URL = "http://127.0.0.1:4181/"
TOLERANCE = 2.0
TIGHT_TOLERANCE = 0.25


def _close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= TOLERANCE


def _tight(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= TIGHT_TOLERANCE


def test_reelshort_desktop_geometry_and_header_style():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page.goto(URL, wait_until="networkidle", timeout=60_000)
        facts = page.evaluate(
            """() => {
              const read = selector => {
                const element = document.querySelector(selector);
                if (!element) return null;
                const rect = element.getBoundingClientRect();
                const style = getComputedStyle(element);
                return {
                  bounds: {
                    x: rect.x + scrollX,
                    y: rect.y + scrollY,
                    width: rect.width,
                    height: rect.height,
                  },
                  display: style.display,
                  backgroundColor: style.backgroundColor,
                  fontWeight: style.fontWeight,
                  lineHeight: style.lineHeight,
                };
              };
              return {
                header: read(".site-header"),
                hero: read(".hero-carousel"),
                main: read("main"),
                footer: read(".site-footer"),
                footerLogo: read(".footer-brand img"),
                footerCopyright: read(".footer-brand p"),
                footerSocials: read(".socials"),
                footerSocialImageCount: document.querySelectorAll(".socials img").length,
                footerList: read(".footer-list"),
                footerAbout: read(".footer-list .footer-column:nth-child(1)"),
                footerAboutTitle: read(".footer-list .footer-column:nth-child(1) h3"),
                footerSupport: read(".footer-list .footer-column:nth-child(2)"),
                footerSupportTitle: read(".footer-list .footer-column:nth-child(2) h3"),
                footerDownload: read(".footer-list .download-column"),
                footerDownloadTitle: read(".footer-list .download-column h3"),
                footerQr: read(".footer-qr"),
                footerDownloadCopy: read(".download-column p"),
                footerQrCorner: (() => {
                  const image = document.querySelector(".footer-qr img");
                  const canvas = document.createElement("canvas");
                  canvas.width = image.naturalWidth;
                  canvas.height = image.naturalHeight;
                  const context = canvas.getContext("2d");
                  context.drawImage(image, 0, 0);
                  return Array.from(context.getImageData(5, 5, 1, 1).data);
                })(),
              };
            }"""
        )
        browser.close()

    assert facts["header"]["display"] == "flex"
    assert facts["header"]["backgroundColor"] == "rgba(0, 0, 0, 0)"
    assert _close(facts["hero"]["bounds"]["height"], 484)
    assert _close(facts["main"]["bounds"]["y"], 540)
    assert _close(facts["main"]["bounds"]["height"], 5558.390625)
    assert _close(facts["footer"]["bounds"]["y"], 6098.390625)
    assert facts["footerList"] is not None
    assert _close(facts["footerLogo"]["bounds"]["x"], 57.6)
    assert _tight(facts["footerLogo"]["bounds"]["y"], 6163.390625)
    assert _tight(facts["footerCopyright"]["bounds"]["y"], 6219.390625)
    assert _tight(facts["footerSocials"]["bounds"]["y"], 6346.390625)
    assert facts["footerSocialImageCount"] == 4
    assert _close(facts["footerAbout"]["bounds"]["x"], 720)
    assert _tight(facts["footerAbout"]["bounds"]["y"], 6163.390625)
    assert _close(facts["footerSupport"]["bounds"]["x"], 940.8)
    assert _close(facts["footerDownload"]["bounds"]["x"], 1161.6)
    assert facts["footerAboutTitle"]["fontWeight"] == "500"
    assert facts["footerSupportTitle"]["fontWeight"] == "500"
    assert facts["footerDownloadTitle"]["fontWeight"] == "500"
    assert _close(facts["footerQr"]["bounds"]["x"], 1161.6)
    assert _tight(facts["footerQr"]["bounds"]["y"], 6202.390625)
    assert _tight(facts["footerDownloadCopy"]["bounds"]["width"], 196.8)
    assert _tight(facts["footerDownloadCopy"]["bounds"]["y"], 6364.390625)
    assert facts["footerDownloadCopy"]["lineHeight"] == "normal"
    assert facts["footerQrCorner"][:3] == [255, 255, 255]
