// animations.js — loads the original db-longbow scroll-animation engine
// (GSAP/ScrollTrigger + the site's own self-initializing `features.js` which
// owns Lenis smooth-scroll + hover/page-transition/video behaviours, plus one
// widget module per `data-widget`), mirrored locally under /assets/js/db.
// Runs AFTER React mounts so the modules find their DOM nodes.

// Resolve engine module URLs relative to the document, so it works whether the
// app is mounted at "/" or under a base path like "/ring/longbow/".
const abs = (rel) => new URL(rel, document.baseURI).href;
const DEV = abs("assets/js/db/projects/DB-Longbow/dev"); // mirrored widgets + features + gsap/ScrollTrigger lib

// CSS the original injects at runtime: content-reveal mask wipe, nav-link hover
// (text-reveal), and Lenis overflow handling. Injected from JS so that if the
// engine ever fails to load, nothing is left hidden.
const ANIM_CSS = `
html.lenis,html.lenis body{height:auto}
.lenis:not(.lenis-autoToggle).lenis-stopped{overflow:clip}
.lenis [data-lenis-prevent]{overscroll-behavior:contain}
.lenis.lenis-smooth iframe{pointer-events:none}

[data-widget='content-reveal'][data-reveal]{opacity:0;-webkit-mask:linear-gradient(#fff,#fff);mask:linear-gradient(#fff,#fff);-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-size:0% 0%;mask-size:0% 0%;transition-duration:1250ms;transition-property:-webkit-mask-size,mask-size,opacity;transition-timing-function:ease-in-out}
[data-widget='content-reveal'][data-reveal='left top']{-webkit-mask-position:left top;mask-position:left top}
[data-widget='content-reveal'][data-reveal='left center']{-webkit-mask-position:left center;mask-position:left center}
[data-widget='content-reveal'][data-reveal='left bottom']{-webkit-mask-position:left bottom;mask-position:left bottom}
[data-widget='content-reveal'][data-reveal='center top']{-webkit-mask-position:center top;mask-position:center top}
[data-widget='content-reveal'][data-reveal='center center']{-webkit-mask-position:center center;mask-position:center center}
[data-widget='content-reveal'][data-reveal='center bottom']{-webkit-mask-position:center bottom;mask-position:center bottom}
[data-widget='content-reveal'][data-reveal='right top']{-webkit-mask-position:right top;mask-position:right top}
[data-widget='content-reveal'][data-reveal='right center']{-webkit-mask-position:right center;mask-position:right center}
[data-widget='content-reveal'][data-reveal='right bottom']{-webkit-mask-position:right bottom;mask-position:right bottom}
[data-widget='content-reveal'][data-reveal-state='finish']{opacity:1;-webkit-mask-size:101% 101%;mask-size:101% 101%}

[nav-link]{position:relative;margin-bottom:-.5rem;padding-bottom:.5rem;white-space:nowrap;overflow:hidden}
[nav-link] .navigation-item__word{display:inline-block}
[nav-link] .navigation-item__word .char{display:inline-block;transition:transform .4s ease-in-out}
[nav-link] .navigation-item__wrapper-word-double{position:absolute;top:.5rem;left:0;opacity:0;transition:all .3s ease-in-out;font-style:italic;pointer-events:none}
[nav-link] .navigation-item__wrapper-word{opacity:1;transition:opacity .3s ease-in-out;pointer-events:none}
[nav-link] .navigation-item__wrapper-word-double .char{transform:translate(0%,125%)}
[nav-link].js--active .navigation-item__wrapper-word-double{top:0;opacity:1}
[nav-link].js--active .navigation-item__wrapper-word{opacity:0}
`;

// Scroll-driven widgets (each module self-inits against its [data-widget] nodes).
const WIDGETS = [
  "image-parallax",
  "content-reveal",
  "card-animation",
  "text-split",
  "marquee",
  "gallery-sticky",
  "text-reveal",
];

export async function initAnimations() {
  try {
    const [{ S: ScrollTrigger }] = await Promise.all([
      import(/* @vite-ignore */ `${DEV}/lib/C6o_azLH.js`),
    ]);

    // Inject the animation-state CSS first.
    const style = document.createElement("style");
    style.setAttribute("data-db-anim", "");
    style.textContent = ANIM_CSS;
    document.head.appendChild(style);

    // features.js OWNS Lenis smooth-scroll + ScrollTrigger.scrollerProxy(body) +
    // hover/page-transition/video behaviours. Load it FIRST so the widgets'
    // ScrollTriggers register against the correct (body) scroller.
    try {
      await import(/* @vite-ignore */ `${DEV}/features.js`);
    } catch (e) {
      console.error("[anim] features.js failed:", e);
    }

    // Then each scroll widget (self-initializing on import).
    for (const w of WIDGETS) {
      try {
        await import(/* @vite-ignore */ `${DEV}/${w}.js`);
      } catch (e) {
        console.error(`[anim] widget "${w}" failed:`, e);
      }
    }

    ScrollTrigger.refresh();

    // Safety net: never leave a content-reveal permanently hidden.
    setTimeout(() => {
      document
        .querySelectorAll('[data-widget="content-reveal"]:not([data-reveal-state])')
        .forEach((el) => {
          const r = el.getBoundingClientRect();
          if (r.top < window.innerHeight && r.bottom > 0) {
            el.setAttribute("data-reveal-state", "finish");
          }
        });
      ScrollTrigger.refresh();
    }, 4000);
  } catch (e) {
    console.error("[anim] engine failed to load:", e);
  }
}
