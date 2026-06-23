import React from "react";

// Section 12 — full-bleed gallery image with grid layout + horizontal divider lines.
// Reproduces the Webflow "section section--sm" block: a 4x grid containing two
// horizontal lines (each with 5 dot "squares" + a full-width hairline) and a
// parallax-style background image filling the lower portion of the grid.

const PRIMARY = "white";
const PRIMARY_20 = "#fff3"; // rgba(255,255,255,0.2)

const LOCAL_IMG = "/assets/images/68b7f09373087cdadb40a4be_longbow-gallery-image-3.jpg";
const REMOTE_IMG =
  "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f09373087cdadb40a4be_longbow-gallery-image-3.jpg";

function HorizontalLine() {
  // .horizontal-line: 100% wide, 1px tall, translateY(-50%); z-index 10
  return (
    <div
      className="relative w-full"
      style={{ zIndex: 10, height: "1px", transform: "translate(0, -50%)" }}
    >
      {/* .square dots positioned at 0/25/50/75/100% */}
      {[
        { left: "0%" },
        { left: "25%" },
        { left: "50%" },
        { left: "75%" },
        { left: "100%" },
      ].map((pos, i) => (
        <div
          key={i}
          style={{
            backgroundColor: PRIMARY,
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: pos.left,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
      {/* .horizontal-line-full-width: 100vw hairline at 20% white */}
      <div
        style={{
          zIndex: 1,
          backgroundColor: PRIMARY_20,
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

export default function Section12Section() {
  return (
    <section
      className="section section--sm"
      style={{
        width: "100%",
        minHeight: "min(100dvh, 63.75rem)",
        display: "flex",
      }}
    >
      <div
        className="container"
        style={{
          width: "100%",
          maxWidth: "120rem",
          marginLeft: "auto",
          marginRight: "auto",
          paddingLeft: ".625rem",
          paddingRight: ".625rem",
          display: "flex",
        }}
      >
        <div
          className="layout"
          style={{
            zIndex: 1,
            flex: 1,
            display: "grid",
            position: "relative",
            columnGap: "0px",
            rowGap: "0px",
            gridTemplateRows: "auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
            width: "100%",
          }}
        >
          {/* Top line — grid-area: 1 / 1 / 2 / 5 */}
          <div
            className="line"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "1 / 1 / 2 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Content with background image — grid-area: 2 / 1 / 5 / 5 */}
          <div
            className="content content--sm"
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              gridArea: "2 / 1 / 5 / 5",
            }}
          >
            <div
              className="background background--auto-brightness"
              data-widget="image-parallax"
              style={{
                zIndex: -1,
                pointerEvents: "none",
                width: "100%",
                height: "100%",
                position: "absolute",
                inset: "0%",
                overflow: "hidden",
              }}
            >
              <img
                alt=""
                className="background__image"
                loading="lazy"
                width="1920"
                height="1080"
                src={LOCAL_IMG}
                onError={(e) => {
                  if (e.currentTarget.src !== REMOTE_IMG) {
                    e.currentTarget.src = REMOTE_IMG;
                  }
                }}
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  maxWidth: "none",
                  height: "100%",
                  transformStyle: "preserve-3d",
                  position: "absolute",
                  top: 0,
                  left: 0,
                  transform: "translateZ(0)",
                }}
              />
            </div>
          </div>

          {/* Bottom line (hidden on tablet) — grid-area: 3 / 1 / 4 / 5 */}
          <div
            className="line line--no-tablet"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "3 / 1 / 4 / 5",
            }}
          >
            <HorizontalLine />
          </div>
        </div>
      </div>
    </section>
  );
}
