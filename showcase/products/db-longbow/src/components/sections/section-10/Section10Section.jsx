import React from "react";

// Section 10 — full-bleed gallery image with decorative grid lines + squares
// Reproduced from section-10.json (Longbow British sports cars landing page).

const LOCAL_IMG = "/assets/images/68b7f0937d45df00d581aa5e_longbow-gallery-image-1.jpg";
const REMOTE_IMG =
  "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f0937d45df00d581aa5e_longbow-gallery-image-1.jpg";

// Decorative horizontal line with 5 squares + a full-width hairline.
function HorizontalLine() {
  return (
    <div
      className="horizontal-line"
      style={{
        zIndex: 10,
        width: "100%",
        height: "1px",
        position: "relative",
        transform: "translate(0, -50%)",
      }}
    >
      {[
        { left: "0%" },
        { left: "25%" },
        { left: "50%" },
        { left: "75%" },
        { left: "100%" },
      ].map((pos, i) => (
        <div
          key={i}
          className="square"
          style={{
            backgroundColor: "var(--primary, white)",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: pos.left,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
      <div
        className="horizontal-line-full-width"
        style={{
          zIndex: 1,
          backgroundColor: "var(--primary-20, #fff3)",
          width: "100vw",
          maxWidth: "100vw",
          height: "1px",
          position: "absolute",
          top: "50%",
          left: "50%",
          overflow: "hidden",
          transform: "translate(-50%, -50%)",
        }}
      />
    </div>
  );
}

export default function Section10Section() {
  return (
    <>
      <style>{`
        .s10-section {
          --primary: white;
          --primary-20: #fff3;
          width: 100%;
          min-height: min(100dvh, 63.75rem);
          display: flex;
        }
        .s10-container {
          width: 100%;
          max-width: 120rem;
          margin-left: auto;
          margin-right: auto;
          padding-left: .625rem;
          padding-right: .625rem;
          display: flex;
        }
        .s10-layout {
          z-index: 1;
          column-gap: 0px;
          row-gap: 0px;
          flex: 1;
          grid-template-rows: auto 1fr auto 1fr;
          grid-template-columns: 1fr 1fr 1fr 1fr;
          grid-auto-rows: 1fr;
          grid-auto-columns: 1fr;
          width: 100%;
          display: grid;
          position: relative;
        }
        .s10-line {
          pointer-events: none;
          width: 100%;
          position: relative;
        }
        .s10-line-1 { grid-area: 1 / 1 / 2 / 5; }
        .s10-content {
          width: 100%;
          height: 100%;
          position: relative;
          grid-area: 2 / 1 / 5 / 5;
        }
        .s10-line-2 { grid-area: 3 / 1 / 4 / 5; }
        .s10-background {
          z-index: -1;
          pointer-events: none;
          width: 100%;
          height: 100%;
          position: absolute;
          inset: 0%;
          overflow: hidden;
        }
        .s10-bg-image {
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

        @media screen and (max-width: 991px) {
          .s10-section { height: 53.333dvw; min-height: auto; }
          .s10-layout { grid-template-columns: 1fr 1fr; }
          .s10-line-1 { grid-area: 1 / 1 / 2 / 3; }
          .s10-content { grid-column-end: 3; }
          .s10-line-2 { grid-area: 3 / 1 / 4 / 3; }
          .s10-line--no-tablet { display: none; }
          .s10-section .square:nth-child(2) { left: 50%; }
          .s10-section .square:nth-child(3) { left: 100%; }
          .s10-section .square:nth-child(4),
          .s10-section .square:nth-child(5) { display: none; }
        }
        @media screen and (max-width: 767px) {
          .s10-section { min-height: 25rem; }
          .s10-layout { flex-flow: column; display: flex; }
          .s10-background { position: relative; }
          .s10-content { height: 100%; min-height: auto; }
          .s10-section .square { width: 5px; height: 5px; }
          .s10-section .square:nth-child(2) { left: 100%; }
          .s10-section .square:nth-child(3) { display: none; }
        }
      `}</style>

      <section className="s10-section section section--sm">
        <div className="s10-container container">
          <div className="s10-layout layout">
            <div className="s10-line s10-line-1 line">
              <HorizontalLine />
            </div>

            <div className="s10-content content content--sm">
              <div
                className="s10-background background background--auto-brightness"
                data-widget="image-parallax"
              >
                <img
                  alt=""
                  className="s10-bg-image background__image"
                  data-role="image"
                  width={1920}
                  height={1080}
                  loading="lazy"
                  src={LOCAL_IMG}
                  onError={(e) => {
                    if (e.currentTarget.src !== REMOTE_IMG) {
                      e.currentTarget.src = REMOTE_IMG;
                    }
                  }}
                />
              </div>
            </div>

            <div className="s10-line s10-line-2 s10-line--no-tablet line line--no-tablet">
              <HorizontalLine />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
