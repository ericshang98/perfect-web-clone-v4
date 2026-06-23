import React from "react";

const PRIMARY = "white";
const PRIMARY_20 = "#fff3";

const HorizontalLine = ({ noTablet }) => (
  <div
    className="s11-line"
    style={{
      pointerEvents: "none",
      width: "100%",
      position: "relative",
      ...(noTablet ? { display: "var(--s11-no-tablet-display, block)" } : {}),
    }}
  >
    <div
      className="s11-horizontal-line"
      style={{
        zIndex: 10,
        width: "100%",
        height: "1px",
        position: "relative",
        transform: "translate(0, -50%)",
      }}
    >
      <Square left="0%" />
      <Square left="25%" variant="25" />
      <Square left="50%" variant="50" />
      <Square left="75%" variant="75" />
      <Square left="100%" variant="100" />
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
  </div>
);

const Square = ({ left, variant }) => (
  <div
    className={`s11-square${variant ? " s11-square--" + variant : ""}`}
    style={{
      backgroundColor: PRIMARY,
      width: "7px",
      height: "7px",
      position: "absolute",
      top: "-50%",
      left,
      transform: "translate(-50%, -50%)",
    }}
  />
);

export default function Section11Section() {
  return (
    <section
      className="s11-section"
      style={{
        width: "100%",
        minHeight: "min(100dvh, 63.75rem)",
        display: "flex",
        position: "relative",
        backgroundColor: "#000",
      }}
    >
      <style>{`
        .s11-section { min-height: min(100dvh, 63.75rem); }
        .s11-container { max-width: 120rem; }
        .s11-layout {
          grid-template-rows: auto 1fr auto 1fr;
          grid-template-columns: 1fr 1fr 1fr 1fr;
          grid-auto-rows: 1fr;
          grid-auto-columns: 1fr;
        }
        .s11-node-top { grid-area: 1 / 1 / 2 / 5; }
        .s11-node-content { grid-area: 2 / 3 / 5 / 5; }
        .s11-node-bg { grid-area: 1 / 3 / 3 / 5; }
        .s11-node-bottom { grid-area: 3 / 1 / 4 / 5; }
        .s11-square--25 { left: 25%; }
        .s11-square--50 { left: 50%; }
        .s11-square--75 { left: 75%; }
        .s11-square--100 { display: block; left: 100%; }

        @media screen and (min-width: 1440px) {
          .s11-node-top { grid-area: 1 / 1 / 2 / 5; }
          .s11-node-content { grid-column: 3 / 5; }
          .s11-node-bottom { grid-area: 3 / 1 / 4 / 5; }
        }

        @media screen and (max-width: 991px) {
          .s11-section { height: 53.333dvw; min-height: auto; }
          .s11-layout { grid-template-columns: 1fr 1fr; }
          .s11-square--25 { left: 50%; }
          .s11-square--50 { left: 100%; }
          .s11-square--75, .s11-square--100 { display: none; }
          .s11-line--no-tablet { display: none; }
          .s11-node-top { grid-area: 1 / 1 / 2 / 3; }
          .s11-node-content { grid-column: 1 / 3; }
          .s11-node-bottom { grid-area: 3 / 1 / 4 / 3; }
        }

        @media screen and (max-width: 767px) {
          .s11-section { min-height: 25rem; }
          .s11-layout { display: flex; flex-flow: column; }
          .s11-bg { position: relative; }
          .s11-bg-image { pointer-events: none; }
          .s11-content { height: auto; min-height: 25rem; }
          .s11-content--sm { height: 100%; min-height: auto; }
          .s11-square { width: 5px; height: 5px; }
          .s11-square--25 { left: 100%; }
          .s11-square--50 { display: none; }
        }
      `}</style>

      <div
        className="s11-container"
        style={{
          width: "100%",
          marginLeft: "auto",
          marginRight: "auto",
          paddingLeft: ".625rem",
          paddingRight: ".625rem",
          display: "flex",
        }}
      >
        <div
          className="s11-layout"
          style={{
            zIndex: 1,
            gridColumnGap: "0px",
            gridRowGap: "0px",
            flex: 1,
            width: "100%",
            display: "grid",
            position: "relative",
          }}
        >
          {/* top line */}
          <div className="s11-node-top s11-line">
            <HorizontalLine />
          </div>

          {/* content with background image */}
          <div
            className="s11-node-content s11-content s11-content--sm"
            style={{
              width: "710px",
              maxWidth: "100%",
              height: "100%",
              position: "relative",
            }}
          >
            <div
              className="s11-bg"
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
                className="s11-bg-image"
                data-role="image"
                width="800"
                height="800"
                loading="lazy"
                src="/assets/images/699ec0449febdd02353efe44_LON-20250307-AVCG_LongbowV11.webp"
                onError={(e) => {
                  e.currentTarget.onerror = null;
                  e.currentTarget.src =
                    "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/699ec0449febdd02353efe44_LON-20250307-AVCG_LongbowV11.webp";
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

          {/* bottom line (hidden on tablet) */}
          <div className="s11-node-bottom s11-line s11-line--no-tablet">
            <HorizontalLine />
          </div>
        </div>
      </div>
    </section>
  );
}
