import React from "react";

/**
 * Section8Section — Longbow "sticky" section.
 * A full-bleed sticky section whose background gradient splits the area
 * 50/50 (black top half), overlaid by an XL grid layout of horizontal
 * guide-lines with positional squares, plus a sticky background video.
 * Reproduced from section-8.json (DOM + css_rules).
 */
export default function Section8Section() {
  const POSTER =
    "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/699ebce3a0e750246795a8a7_new-home-reverse.webp";
  const VIDEO =
    "https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/699ebca3f1e8e212bc6b59c5_new-home-video-reverse.mp4";

  // Local CSS vars + scoped rules, faithful to the source css_rules.
  const css = `
    .s8-root {
      --background-alt: #000;
      --primary: #ffffff;
      --primary-20: #ffffff33;
      width: 100%;
      min-height: min(200dvh, 127.5rem);
      display: flex;
      background-image: linear-gradient(180deg, var(--background-alt) 49.999%, transparent 50.001%);
    }
    .s8-container {
      width: 100%;
      max-width: 120rem;
      margin-left: auto;
      margin-right: auto;
      padding-left: .625rem;
      padding-right: .625rem;
      display: flex;
    }
    .s8-layout {
      z-index: 1;
      grid-column-gap: 0px;
      grid-row-gap: 0px;
      flex: 1;
      grid-template-rows: auto 1fr auto 1fr auto 1fr auto 1fr;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      grid-auto-rows: 1fr;
      grid-auto-columns: 1fr;
      width: 100%;
      display: grid;
      position: relative;
    }
    .s8-line {
      pointer-events: none;
      width: 100%;
      position: relative;
    }
    .s8-horizontal-line {
      z-index: 10;
      width: 100%;
      height: 1px;
      position: relative;
      transform: translate(0, -50%);
    }
    .s8-horizontal-line-full-width {
      z-index: 1;
      background-color: var(--primary-20);
      width: 100vw;
      max-width: 100vw;
      height: 1px;
      position: absolute;
      top: 50%;
      left: 50%;
      overflow: hidden;
      transform: translate(-50%, -50%);
    }
    .s8-square {
      background-color: var(--primary);
      width: 7px;
      height: 7px;
      position: absolute;
      top: -50%;
      left: 0%;
      transform: translate(-50%, -50%);
    }
    .s8-square--25 { left: 25%; }
    .s8-square--50 { left: 50%; }
    .s8-square--75 { left: 75%; }
    .s8-square--100 { display: block; left: 100%; }

    .s8-content-sticky {
      justify-content: center;
      align-items: flex-start;
      width: 100%;
      height: min(100dvh, 63.75rem);
      display: flex;
      position: sticky;
      inset: 0%;
    }
    .s8-content--sticky {
      width: 50%;
      height: min(100dvh, 63.75rem);
      position: relative;
    }
    .s8-background {
      z-index: -1;
      pointer-events: none;
      width: 100%;
      height: 100%;
      position: absolute;
      inset: 0%;
      overflow: hidden;
    }
    .s8-background--brightness { filter: brightness(75%); }
    .s8-background__image {
      z-index: -1;
      object-fit: cover;
      width: 100%;
      max-width: none;
      height: 100%;
      transform-style: preserve-3d;
      position: absolute;
      top: 0;
      left: 0;
      transform: translateZ(0);
    }

    /* grid placement */
    .s8-node-line-1 { grid-area: 1 / 1 / 2 / 5; }
    .s8-node-content-sticky { grid-area: 2 / 1 / 5 / 5; }
    .s8-node-content { grid-area: 2 / 1 / 5 / 4; }
    .s8-node-bg { grid-area: 1 / 3 / 3 / 5; }
    .s8-node-line-3 { grid-area: 3 / 1 / 4 / 5; }
    .s8-node-line-5 { grid-area: 5 / 1 / 6 / 5; }
    .s8-node-line-7 { grid-area: 7 / 1 / 8 / 5; }

    @media screen and (min-width: 1440px) {
      .s8-content--sticky { width: 50%; }
    }
    @media screen and (max-width: 991px) {
      .s8-root {
        background-image: none;
        height: 25rem;
        min-height: auto;
      }
      .s8-layout { grid-template-columns: 1fr 1fr; }
      .s8-content--sticky { width: 100%; height: 100%; }
      .s8-square--25 { left: 50%; }
      .s8-square--50 { left: 100%; }
      .s8-square--75, .s8-square--100 { display: none; }
      .s8-line--no-tablet { display: none; }
      .s8-content-sticky { height: 100%; }
      .s8-node-line-1 { grid-area: 1 / 1 / 2 / 3; }
      .s8-node-content-sticky { grid-row-end: 9; grid-column-end: 3; }
      .s8-node-content { grid-column-end: 3; }
      .s8-node-line-3 { grid-area: 3 / 1 / 4 / 3; }
      .s8-node-line-5, .s8-node-line-7 { grid-area: 1 / 1 / 2 / 3; }
    }
    @media screen and (max-width: 767px) {
      .s8-root { min-height: 25rem; }
      .s8-layout { flex-flow: column; display: flex; }
      .s8-background { position: relative; }
      .s8-background__image { pointer-events: none; }
      .s8-content--sticky { height: auto; min-height: 25rem; }
      .s8-square { width: 5px; height: 5px; }
      .s8-square--25 { left: 100%; }
      .s8-square--50 { display: none; }
    }
  `;

  const HLine = () => (
    <div className="s8-horizontal-line">
      <div className="s8-square" />
      <div className="s8-square s8-square--25" />
      <div className="s8-square s8-square--50" />
      <div className="s8-square s8-square--75" />
      <div className="s8-square s8-square--100" />
      <div className="s8-horizontal-line-full-width" />
    </div>
  );

  return (
    <section
      className="s8-root"
      style={{ fontFamily: "Inter, sans-serif" }}
    >
      <style>{css}</style>
      <div className="s8-container" style={{ width: "1440px", maxWidth: "100%" }}>
        <div className="s8-layout" style={{ width: "1420px", maxWidth: "100%" }}>
          {/* line 1 */}
          <div className="s8-line s8-node-line-1">
            <HLine />
          </div>

          {/* content-sticky (hidden in source via display:none !important) */}
          <div
            className="s8-content-sticky s8-node-content-sticky"
            data-role="content-sticky"
            style={{ display: "none" }}
          >
            <div
              className="s8-content s8-content--sticky s8-node-content"
              data-role="content"
              style={{ height: "min(100dvh, 63.75rem)", width: "50%" }}
            >
              <div className="s8-background s8-background--brightness s8-node-bg">
                <div className="s8-background__image">
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    poster={POSTER}
                    preload="metadata"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  >
                    <source src={VIDEO} type="video/mp4" />
                  </video>
                </div>
              </div>
            </div>
          </div>

          {/* line 3 (no-tablet) */}
          <div className="s8-line s8-line--no-tablet s8-node-line-3">
            <HLine />
          </div>

          {/* line 5 (no-tablet) */}
          <div className="s8-line s8-line--no-tablet s8-node-line-5">
            <HLine />
          </div>

          {/* line 7 (no-tablet) */}
          <div className="s8-line s8-line--no-tablet s8-node-line-7">
            <HLine />
          </div>
        </div>
      </div>
    </section>
  );
}

export { Section8Section };
