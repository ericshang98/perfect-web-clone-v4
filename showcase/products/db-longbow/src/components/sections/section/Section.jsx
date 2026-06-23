import React from "react";

/**
 * Speedster section — Longbow British sports cars landing page.
 * Parallax background image, decorative horizontal-line square grids,
 * and a dark card with heading, price, autoplay video and Reserve button.
 */
export default function Section() {
  const css = `
    .spd-section {
      display: flex;
      position: relative;
      justify-content: center;
      align-items: center;
      width: 100%;
      min-height: 100vh;
      padding: 0;
      overflow: hidden;
      background-color: #000;
      font-family: Inter, Arial, sans-serif;
    }
    .spd-container {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 1440px;
      max-width: 100%;
      padding: 10px;
      position: relative;
      z-index: 2;
    }
    .spd-layout {
      display: grid;
      position: relative;
      width: 1420px;
      max-width: 100%;
      grid-auto-columns: 1fr;
      grid-template-columns: 1fr;
      grid-template-rows: auto auto;
      grid-row-gap: 0px;
      justify-items: center;
      align-items: center;
    }
    /* decorative line rows */
    .spd-line {
      width: 100%;
      grid-column: 1;
    }
    .spd-line--top { grid-row: 1; align-self: start; }
    .spd-line--bottom { grid-row: 2; align-self: end; }
    .spd-horizontal-line {
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
      height: 1px;
    }
    .spd-horizontal-line-full-width {
      position: absolute;
      left: 0;
      right: 0;
      top: 50%;
      height: 1px;
      background-color: rgba(255, 255, 255, 0.2);
    }
    .spd-square {
      position: absolute;
      top: 50%;
      width: 5px;
      height: 5px;
      transform: translateY(-50%) rotate(45deg);
      background-color: rgba(255, 255, 255, 0.45);
      z-index: 1;
    }
    .spd-square { left: 0; }
    .spd-square--25 { left: 25%; }
    .spd-square--50 { left: 50%; transform: translate(-50%, -50%) rotate(45deg); }
    .spd-square--75 { left: 75%; }
    .spd-square--100 { left: auto; right: 0; }

    /* parallax background */
    .spd-background {
      position: absolute;
      inset: 0;
      width: 1420px;
      max-width: 100%;
      height: 100%;
      overflow: hidden;
      z-index: 1;
      left: 50%;
      transform: translateX(-50%);
    }
    .spd-background--brightness .spd-background__image { filter: brightness(0.65); }
    .spd-background__image {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 100%;
      height: 110%;
      object-fit: cover;
      transform: translate(-50%, -50%);
    }

    /* card */
    .spd-card {
      position: relative;
      grid-column: 1;
      grid-row: 1 / span 2;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 355px;
      max-width: 100%;
      text-decoration: none;
      color: #fff;
      z-index: 3;
    }
    .spd-card__layout {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 301px;
      max-width: 100%;
      padding: 24px;
      gap: 10px;
      text-align: center;
      background-color: rgba(0, 0, 0, 0.55);
      backdrop-filter: blur(2px);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .spd-card--dark .spd-card__layout { color: #fff; }
    .spd-heading {
      margin: 0 0 4px;
      font-family: Lora, Georgia, serif;
      font-weight: 400;
      font-size: 30px;
      line-height: 1.1;
      letter-spacing: 0.01em;
      color: #fff;
    }
    .spd-heading-italic {
      font-style: italic;
      font-weight: 400;
    }
    .spd-text {
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.85);
      margin-bottom: 6px;
    }
    .spd-card__video {
      width: 100%;
      aspect-ratio: 16 / 10;
      overflow: hidden;
      margin: 6px 0 4px;
    }
    .spd-card__video video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .spd-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 20px;
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #fff;
      border: 1px solid rgba(255, 255, 255, 0.4);
      transition: background-color 0.3s ease, color 0.3s ease;
    }
    /* hover overlay video */
    .spd-hover {
      position: absolute;
      inset: 0;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.5s ease;
      z-index: -1;
    }
    .spd-hover .spd-background__image--blur { filter: blur(8px) brightness(0.6); }
    .spd-hover-overlay--inner {
      position: absolute;
      inset: 0;
      background-color: rgba(0, 0, 0, 0.25);
    }
    .spd-card:hover .spd-button {
      background-color: #fff;
      color: #000;
    }
    .spd-card:hover .spd-card__layout {
      background-color: rgba(0, 0, 0, 0.7);
    }
  `;

  return (
    <section className="spd-section" id="speedster" data-name="main-child">
      <style>{css}</style>
      <div className="spd-container">
        <div className="spd-layout">
          {/* top decorative line */}
          <div className="spd-line spd-line--top">
            <div className="spd-horizontal-line">
              <div className="spd-square" />
              <div className="spd-square spd-square--25" />
              <div className="spd-square spd-square--50" />
              <div className="spd-square spd-square--75" />
              <div className="spd-square spd-square--100" />
              <div className="spd-horizontal-line-full-width" />
            </div>
          </div>

          {/* parallax background image */}
          <div
            className="spd-background spd-background--brightness"
            data-widget="image-parallax"
          >
            <img
              alt=""
              className="spd-background__image"
              height="1080"
              width="1920"
              loading="eager"
              src="/assets/images/699453b389c0560958407f0a_HP-1.webp"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
          </div>

          {/* bottom decorative line */}
          <div className="spd-line spd-line--bottom">
            <div className="spd-horizontal-line">
              <div className="spd-square" />
              <div className="spd-square spd-square--25" />
              <div className="spd-square spd-square--50" />
              <div className="spd-square spd-square--75" />
              <div className="spd-square spd-square--100" />
              <div className="spd-horizontal-line-full-width" />
            </div>
          </div>

          {/* card */}
          <a
            className="spd-card spd-card--dark"
            data-role="hover-trigger"
            data-widget="card-animation"
            href="/speedster#reserve"
          >
            <div className="spd-card__layout">
              <h2 className="spd-heading">
                Speedster
                <br />
                <span className="spd-heading-italic">Limited edition</span>
              </h2>
              <div className="spd-text" data-widget="text-reveal">
                £125,000 / Reservation
              </div>
              <div className="spd-card__video" data-role="image">
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  preload="metadata"
                  poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/699453b389c0560958407f0a_HP-1.webp"
                >
                  <source
                    src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/699452f0ed212686218dd890_hp-v-02-boomerang.mp4"
                    type="video/mp4"
                  />
                </video>
              </div>
              <div className="spd-button" data-role="button">
                <div>Reserve +</div>
              </div>
            </div>

            {/* hover overlay video */}
            <div className="spd-hover" data-role="hover">
              <div className="spd-background spd-background--brightness">
                <div className="spd-background__image spd-background__image--blur">
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    preload="metadata"
                    poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b6bc1e9f70c63e870aa2e4_longbow-hover-poster.jpg"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  >
                    <source
                      src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/699451025704c1aa8b5c281b_new_longbow-hover-video-v2.mp4"
                      type="video/mp4"
                    />
                  </video>
                </div>
              </div>
              <div className="spd-hover-overlay spd-hover-overlay--inner" />
            </div>
          </a>
        </div>
      </div>
    </section>
  );
}
