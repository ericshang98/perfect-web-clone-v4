(function() {
  "use strict";
  try {
    if (typeof document != "undefined") {
      var elementStyle = document.createElement("style");
      elementStyle.appendChild(document.createTextNode("/* global styles */\n\n:focus-visible {\n  transition: var(--transition-default);\n  outline: currentColor solid 1px;\n  outline-offset: 0.25em;\n}\n\n.visually-hidden {\n  position: absolute !important;\n  margin: -1px !important;\n  padding: 0 !important;\n  border: 0 !important;\n  white-space: nowrap !important;\n  block-size: 1px !important;\n  clip: rect(0, 0, 0, 0) !important;\n  inline-size: 1px !important;\n  overflow: hidden !important;\n}\n\n* {\n  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);\n}\n\nhtml.lenis,html.lenis body{height:auto}\n\n.lenis:not(.lenis-autoToggle).lenis-stopped{overflow:clip}\n\n.lenis [data-lenis-prevent],.lenis [data-lenis-prevent-wheel],.lenis [data-lenis-prevent-touch]{overscroll-behavior:contain}\n\n.lenis.lenis-smooth iframe{pointer-events:none}\n\n.lenis.lenis-autoToggle{transition-property:overflow;transition-duration:1ms;transition-behavior:allow-discrete}\n\nbody {\n\n  /** {\n    backdrop-filter: unset !important;\n  } */\n}\n\nbody.js--locked {\n    overflow: hidden;\n    padding-inline-end: var(--js-scrollbar-width);\n  }\n\nbody {\n\n  overflow: unset;\n  overflow-x: hidden;\n}\n\n[data-role='hover-trigger']:hover [data-role='hover'] {\n      opacity: 1;\n    }\n\n[data-role='hover-trigger']:hover [data-role='image'],\n    [data-role='hover-trigger']:hover [data-role='button'] {\n      border-radius: 1.25rem;\n    }\n\n[data-role='inner-hover-trigger']:hover [data-role='inner-hover'] {\n      opacity: 1;\n    }\n\n[data-role='inner-hover-trigger']:hover [data-role='inner-image'],\n    [data-role='inner-hover-trigger']:hover [data-role='inner-button'] {\n      border-radius: 1.25rem;\n    }\n\n@media (max-width: 767px) {\n    [data-role='inner-hover-trigger'] [data-role='inner-hover'] {\n      opacity: 1 !important;\n    }\n    [data-role='inner-hover-trigger'] [data-role='inner-image'],\n    [data-role='inner-hover-trigger'] [data-role='inner-button'] {\n      border-radius: 1.25rem !important;\n    }\n  }\n\n::-webkit-scrollbar-track {\n  background-color: var(--scrollbar-background-color);\n}\n\n::-webkit-scrollbar {\n  width: var(--scrollbar-width);\n  background-color: var(--scrollbar-background-color);\n}\n\n::-webkit-scrollbar-thumb {\n  background-color: var(--scrollbar-thumb-color);\n}\n\n* {\n  scrollbar-color: var(--scrollbar-thumb-color) var(--scrollbar-background-color);\n  scrollbar-width: thin;\n}\n\nhtml::-webkit-scrollbar {\n  display: none;\n  width: 0;\n  height: 0;\n}\n\nhtml {\n  scrollbar-width: none;\n}\n\n.card.card--privacy,\n.layout.layout--privacy {\n  scrollbar-width: unset;\n}\n\n.card.card--privacy::-webkit-scrollbar, .layout.layout--privacy::-webkit-scrollbar {\n    display: none !important;\n    width: 6px;\n    height: auto;\n  }\n\n.card.card--privacy::-webkit-scrollbar-thumb, .layout.layout--privacy::-webkit-scrollbar-thumb {\n    border-radius: 10px;\n    background-color: rgba(25, 25, 25, 0.5);\n  }\n\n@media (max-width: 991px) {\n    .card.card--privacy::-webkit-scrollbar, .layout.layout--privacy::-webkit-scrollbar {\n      display: none !important;\n    }\n  }\n\n::selection {\n  color: #fff !important;\n  background-color: #000 !important;\n  background-clip: unset !important;\n  -webkit-text-fill-color: #fff !important;\n}\n\ntextarea {\n  resize: vertical;\n}\n\n.w-webflow-badge {\n  display: none !important;\n}\n\n.w-richtext ol,\n  .w-richtext ul {\n    overflow: visible;\n  }\n\n.w-richtext > :first-child {\n    margin-block-start: 0;\n  }\n\n.w-richtext > :last-child {\n    margin-block-end: 0;\n  }\n[data-role='preloader'] {\n  opacity: 1;\n  overflow: hidden;\n}\n  /* transition: opacity 0.3s ease-in-out; */\n\n  [data-role='preloader'].js--hidden {\n    opacity: 0;\n    pointer-events: none;\n  }\n[data-role='main'] {\n  opacity: 1;\n  transition: opacity 0.3s ease-in-out;\n}\n[data-role='main'] [data-name='main-child'] {\n    transition: opacity 0.3s ease-in-out;\n  }\n[data-role='main'].js--hidden {\n    opacity: 0;\n    pointer-events: none;\n  }\n[data-role='main'].js--loading [data-name='main-child'] {\n      opacity: 0;\n      transition: opacity 0.3s ease-in-out;\n    }\n[data-role='loading-tag'] {\n  opacity: 0;\n}\n[data-role='loading-tag'].js--active {\n    top: unset;\n    left: unset;\n    transform: unset;\n  }\n[nav-link] {\n  position: relative;\n  margin-bottom: -0.5rem;\n  padding-bottom: 0.5rem;\n  white-space: nowrap;\n  overflow: hidden;\n}\n\n  [nav-link] .navigation-item__word {\n    display: inline-block;\n  }\n\n  [nav-link] .navigation-item__word .char {\n    display: inline-block;\n    transition: transform 0.4s ease-in-out;\n  }\n\n  [nav-link] .navigation-item__wrapper-word-double {\n    position: absolute;\n    top: 0.5rem;\n    left: 0;\n    opacity: 0;\n    transition: all 0.3s ease-in-out;\n    font-style: italic;\n    pointer-events: none;\n  }\n\n  [nav-link] .navigation-item__wrapper-word {\n    opacity: 1;\n    transition: opacity 0.3s ease-in-out;\n    pointer-events: none;\n  }\n\n  [nav-link] .navigation-item__wrapper-word-double .char {\n    transform: translate(0%, 125%);\n  }\n\n  [nav-link].js--active .navigation-item__wrapper-word-double {\n      top: 0;\n      opacity: 1;\n    }\n\n  [nav-link].js--active .navigation-item__wrapper-word {\n      opacity: 0;\n    }\n[data-widget='card-animation'] {\n  /* your styles */\n}\n[data-widget='content-reveal'][data-reveal] {\n    opacity: 0;\n    mask: linear-gradient(white, white);\n\n    /* WebKit префикс для Safari */\n    mask-repeat: no-repeat;\n    mask-size: 0% 0%;\n    transition-duration: 1250ms;\n\n    transition-property: mask-size, opacity;\n    transition-timing-function: ease-in-out;\n  }\n  [data-widget='content-reveal'][data-reveal='left top'] {\n    mask-position: left top;\n  }\n  [data-widget='content-reveal'][data-reveal='left center'] {\n    mask-position: left center;\n  }\n  [data-widget='content-reveal'][data-reveal='left bottom'] {\n    mask-position: left bottom;\n  }\n  [data-widget='content-reveal'][data-reveal='center top'] {\n    mask-position: center top;\n  }\n  [data-widget='content-reveal'][data-reveal='center center'] {\n    mask-position: center center;\n  }\n  [data-widget='content-reveal'][data-reveal='center bottom'] {\n    mask-position: center bottom;\n  }\n  [data-widget='content-reveal'][data-reveal='right top'] {\n    mask-position: right top;\n  }\n  [data-widget='content-reveal'][data-reveal='right center'] {\n    mask-position: right center;\n  }\n  [data-widget='content-reveal'][data-reveal='right bottom'] {\n    mask-position: right bottom;\n  }\n  [data-widget='content-reveal'][data-reveal-state='finish'] {\n    opacity: 1;\n    mask-size: 101% 101%;\n  }\n[data-widget='gallery-sticky'] {\n  /* your styles */\n}\n[data-widget='header'] {\n  backdrop-filter: unset;\n}\n\n  [data-widget='header']::before {\n    position: absolute;\n    top: 0;\n    left: 0;\n    bottom: 0;\n    right: 0;\n    z-index: -1;\n    backdrop-filter: blur(20px);\n    content: '';\n  }\n\n  [data-widget='header']:hover .hover-overlay {\n      backdrop-filter: blur(40px);\n    }\n\n  [data-widget='header'] [data-role='navmenu'] {\n    opacity: 0;\n    transition:\n      opacity 300ms ease,\n      height 400ms ease-in-out;\n    overflow: hidden;\n    will-change: opacity, height;\n  }\n\n  [data-widget='header'].js--open [data-role='navmenu'] {\n      opacity: 1;\n    }\n\n  @media (max-height: 600px) {\n\n  [data-widget='header'].js--open [data-role='navmenu'] {\n        max-height: calc(100vh - var(--size--header-height) - 1.25rem);\n        overflow: auto\n    }\n      }\n\n  [data-widget='header'].js--open .header__button .header__button-line--top {\n        transform: translate(0, 0) rotate(45deg);\n      }\n\n  [data-widget='header'].js--open .header__button .header__button-line--bottom {\n        transform: translate(0, 0) rotate(-45deg);\n      }\n\n  [data-widget='header'].js--open [data-role='hover'] {\n      opacity: 1;\n    }\n\n  [data-widget='header'].js--open [data-role='hover'] .hover-overlay {\n        backdrop-filter: blur(100px);\n      }\n[data-widget='header'] [data-role='navmenu'][aria-hidden='true'] {\n  pointer-events: none;\n}\n@media (prefers-reduced-motion: reduce) {\n  [data-widget='header'] [data-role='navmenu'] {\n    transition: none;\n  }\n}\n[data-widget='image-parallax'] {\n  /* your styles */\n}\n[data-widget='text-split'] {\n  opacity: 0;\n  overflow: hidden;\n}\n\n  [data-widget='text-split'] .line {\n    position: relative;\n    margin-top: -0.01em;\n\n    /* margin-right: -.1em; */\n    padding-top: 0.01em;\n    /* padding-right: 0.1em; */\n  }\n\n  [data-widget='text-split'][data-start-opacity] .line {\n      margin-bottom: -0.3em;\n      padding-bottom: 0.1em;\n      overflow: hidden;\n    }\n\n  [data-widget='text-split'] .char {\n    display: inline-block;\n    opacity: 1;\n  }\n@keyframes marqueeMovingLine{0%{transform:translate(0)}to{transform:translate(-50%)}}[data-marquee-role=parent] [data-marquee-role=moving-line]{animation-play-state:running;animation-iteration-count:infinite;animation-timing-function:linear}[data-marquee-role=parent][data-marquee-state=disabled] [data-marquee-role=moving-line]{animation-name:none}[data-marquee-role=parent][data-marquee-state=enabled]{overflow:hidden;display:flex;flex-direction:row;justify-content:start}[data-marquee-role=parent][data-marquee-state=enabled] [data-marquee-role=moving-line]{animation-name:marqueeMovingLine;width:max-content}[data-marquee-role=parent][data-marquee-state=enabled] [data-marquee-role=list]{display:flex;gap:0;flex-direction:row;justify-content:start;width:max-content}[data-widget='marquee'] {\n  /* stylelint-enable keyframes-name-pattern */\n}[data-widget='marquee'].js--disabled [data-marquee-role='parent'] [data-marquee-role='moving-line'] {\n        animation-play-state: paused;\n      }/* stylelint-disable keyframes-name-pattern */@keyframes marqueeMovingLine {\n    0% {\n      transform: translateX(-50%);\n    }\n    100% {\n      transform: translateX(0);\n    }\n  }\n[data-widget='text-reveal'] {\n  /* your styles */\n}"));
      document.head.appendChild(elementStyle);
    }
  } catch (e) {
    console.error("vite-plugin-css-injected-by-js", e);
  }
})();
import { g as gsapWithCSS } from "./lib/50Lx19ak.js";
import { C as CLASSES } from "./lib/DxoHJvy8.js";
const initPreloaderAnimation = (onComplete) => {
  gsapWithCSS.set(".preloader-line", { autoAlpha: 0 });
  gsapWithCSS.set(".preloader-wrapper", { autoAlpha: 0 });
  gsapWithCSS.set(".center-sub-square", { autoAlpha: 0, scale: 0, rotation: 45 });
  gsapWithCSS.set(".preloader-square-logo", { autoAlpha: 0 });
  let flag1 = false;
  let flag2 = false;
  let flag3 = false;
  const tl = gsapWithCSS.timeline({
    defaults: { ease: "power1.inOut" },
    onComplete
  });
  tl.fromTo(".preloader-wrapper", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }).fromTo(
    ".horizontal-1",
    { autoAlpha: 0, scaleX: 0, transformOrigin: "left center" },
    { autoAlpha: 1, scaleX: 1, transformOrigin: "left center", duration: 0.5 }
  ).fromTo(
    ".vertical-1",
    { autoAlpha: 0, scaleY: 0, transformOrigin: "bottom center" },
    {
      autoAlpha: 1,
      scaleY: 1,
      duration: 0.5,
      onUpdate: function() {
        if (!flag1 && this.progress() > 0.6) {
          flag1 = true;
          gsapWithCSS.to(".center-sub-square:nth-child(1)", {
            autoAlpha: 1,
            scale: 1,
            rotation: 0,
            duration: 0.4,
            ease: "back.out(1.5)"
          });
        }
      }
    },
    "-=0.1"
  ).addLabel("afterVertical1").fromTo(
    ".vertical-2",
    { scaleY: 0, transformOrigin: "top center" },
    {
      autoAlpha: 1,
      scaleY: 1,
      transformOrigin: "top center",
      duration: 0.5,
      onUpdate: function() {
        if (!flag2 && this.progress() > 0.4) {
          flag2 = true;
          gsapWithCSS.to(".center-sub-square:nth-child(2)", {
            autoAlpha: 1,
            scale: 1,
            rotation: 0,
            duration: 0.4,
            ease: "back.out(1.5)"
          });
        }
      }
    },
    "-=0.1"
  ).addLabel("afterVertical2").fromTo(
    ".horizontal-2",
    { scaleX: 0, transformOrigin: "right center" },
    {
      autoAlpha: 1,
      scaleX: 1,
      transformOrigin: "right center",
      duration: 0.5,
      onUpdate: function() {
        if (!flag3 && this.progress() > 0.5) {
          flag3 = true;
          gsapWithCSS.timeline().to(".center-sub-square:nth-child(3), .center-sub-square:nth-child(4)", {
            autoAlpha: 1,
            scale: 1,
            rotation: 0,
            duration: 0.4,
            ease: "back.out(1.5)",
            stagger: {
              each: 0.1,
              from: "start"
            }
          });
        }
      }
    },
    "afterVertical2"
  ).to(
    ".preloader-square-logo",
    {
      autoAlpha: 1,
      // scale: 1,
      duration: 1.3,
      ease: "power1.inOut"
    },
    "afterVertical1"
  );
};
const SELECTORS = {
  PRELOADER: '[data-role="preloader"]',
  LOADING_TAG: '[data-role="loading-tag"]',
  MAIN_CONTENT: '[data-role="main"]'
};
const initPreloader = (callbackFunction) => {
  const mainContent = document.querySelector(SELECTORS.MAIN_CONTENT);
  const preloader = document.querySelector(SELECTORS.PRELOADER);
  const loadingTag = document.querySelector(SELECTORS.LOADING_TAG);
  const minDisplayTime = 3e3;
  let loadStartTime;
  let cleanupCursor;
  let progressInterval = null;
  if (!preloader) {
    setTimeout(() => {
      showContent(function() {
        initOtherFeatures();
      });
    }, 1e3);
  }
  mainContent.classList.add(CLASSES.HIDDEN);
  mainContent.classList.add(CLASSES.LOADING);
  function initLoadingCursor() {
    if (!loadingTag) return;
    document.body.style.cursor = "none";
    gsapWithCSS.set(loadingTag, { autoAlpha: 0 });
    gsapWithCSS.to(loadingTag, {
      autoAlpha: 1,
      duration: 0.3
    });
    const moveCursor = (e) => {
      loadingTag.classList.add(CLASSES.ACTIVE);
      gsapWithCSS.to(loadingTag, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.9,
        ease: "power2.out"
      });
    };
    document.addEventListener("mousemove", moveCursor);
    return () => {
      document.removeEventListener("mousemove", moveCursor);
      document.body.style.cursor = "";
    };
  }
  function updateLoadingProgress(progress) {
    if (!loadingTag) return;
    const overlay = loadingTag.querySelector(".loading-tag-overlay");
    if (overlay) {
      gsapWithCSS.to(overlay, {
        width: `${progress}%`,
        duration: 0.2,
        ease: "power1.out"
      });
    }
  }
  function simulateLoadingProgress() {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      updateLoadingProgress(progress);
    }, 200);
    return interval;
  }
  function startPreloader() {
    loadStartTime = Date.now();
    document.body.classList.add(CLASSES.LOCKED);
    cleanupCursor = initLoadingCursor();
    progressInterval = loadingTag ? simulateLoadingProgress() : null;
    initPreloaderAnimation(() => {
      handlePageLoad();
    });
    setTimeout(function() {
      if (mainContent.classList.contains(CLASSES.HIDDEN)) {
        handlePageLoad();
      }
    }, 5e3);
  }
  startPreloader();
  function handlePageLoad() {
    const currentTime = Date.now();
    const elapsedTime = currentTime - loadStartTime;
    const remainingTime = minDisplayTime - elapsedTime;
    if (remainingTime > 0) {
      setTimeout(hidePreloaderAndShowContent, remainingTime);
    } else {
      hidePreloaderAndShowContent();
    }
  }
  function hidePreloaderAndShowContent() {
    hidePreloaderAnimation(() => {
      showContent(initOtherFeatures);
    });
  }
  function hidePreloaderAnimation(callback) {
    gsapWithCSS.to(preloader, {
      autoAlpha: 0,
      // scale: 0.8,
      duration: 0.3,
      ease: "power2.inOut",
      onComplete: callback
    });
  }
  function showContent(callback) {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    updateLoadingProgress(100);
    if (cleanupCursor) {
      cleanupCursor();
      cleanupCursor = void 0;
    }
    if (loadingTag) {
      gsapWithCSS.to(loadingTag, {
        autoAlpha: 0,
        duration: 0.3
      });
    }
    if (callback) callback();
    mainContent.classList.remove(CLASSES.HIDDEN);
    mainContent.classList.remove(CLASSES.LOADING);
    document.body.classList.remove(CLASSES.LOCKED);
  }
  function initOtherFeatures() {
    if (callbackFunction) callbackFunction();
  }
  window.addEventListener("error", function() {
    setTimeout(hidePreloaderAndShowContent, 1e3);
  });
  return () => {
    document.body.style.cursor = "";
    if (loadingTag) {
      gsapWithCSS.set(loadingTag, { autoAlpha: 0, x: 0, y: 0 });
    }
  };
};
(() => {
  let ModuleType;
  ((ModuleType2) => {
    ModuleType2["Widgets"] = "widgets";
    ModuleType2["Features"] = "features";
  })(ModuleType || (ModuleType = {}));
  const projectName = "DB-Longbow";
  const baseSourceUrl = "https://cdn.digitalbutlers.me/projects";
  const isLocalMode = Boolean(window.location.port);
  const getUrl = (segments) => {
    return new URL(segments.join("/")).toString();
  };
  const getModuleUrl = ({ moduleType, moduleName }) => {
    !window.location.hostname.endsWith("webflow.io") && !isLocalMode && false;
    const modeFolder = "dev";
    const origin = window.location.origin;
    const segmentsLocal = [.../* @__PURE__ */ new Set([origin, "src", moduleType, moduleName, "index.ts"])];
    const segmentsRemote = [baseSourceUrl, projectName, modeFolder, `${moduleName}.js`];
    const sourceUrl = isLocalMode ? segmentsLocal : segmentsRemote;
    return getUrl(sourceUrl);
  };
  const initWidgets = () => {
    const loadWidget = async (widgetName) => {
      const moduleUrl = getModuleUrl({ moduleType: "widgets", moduleName: widgetName });
      try {
        await import(
          /* @vite-ignore */
          moduleUrl
        );
      } catch (error) {
        console.error(`Error load widget "${widgetName}":`, error);
      }
    };
    document.querySelectorAll("[data-widget]").forEach((widgetEl) => {
      const widgetName = widgetEl.getAttribute("data-widget");
      widgetName && loadWidget(widgetName);
    });
  };
  const initFeatures = async () => {
    const moduleUrl = getModuleUrl({
      moduleType: "features",
      moduleName: "features"
      /* Features */
    });
    try {
      await import(
        /* @vite-ignore */
        moduleUrl
      );
    } catch (error) {
      console.error(`Error features load:`, error);
    }
  };
  initPreloader(() => {
    initWidgets();
    initFeatures();
  });
})();
