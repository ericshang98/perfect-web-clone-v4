import React from "react";

/**
 * Section 9 — Longbow clone
 * Full-bleed autoplay video panel set inside a 4-column grid with thin
 * horizontal divider lines (with square nodes) top and bottom.
 * Reproduced from section-9.json (raw_html + css_rules).
 */
function Section9Section() {
  function squareStyle(fraction) {
    return {
      backgroundColor: "var(--primary, white)",
      width: "7px",
      height: "7px",
      position: "absolute",
      top: "-50%",
      left: `${fraction * 100}%`,
      transform: "translate(-50%, -50%)",
    };
  }

  return (
    <section
      className="section section--sm"
      style={{
        display: "flex",
        width: "100%",
        minHeight: "min(100dvh, 63.75rem)",
        background: "#000",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <style>{`
        .pwc-s9-line[data-no-tablet="true"] { display: block; }
        @media screen and (max-width: 991px) {
          .pwc-s9-section { height: 53.333dvw; min-height: auto !important; }
          .pwc-s9-layout { grid-template-columns: 1fr 1fr !important; }
          .pwc-s9-line[data-no-tablet="true"] { display: none !important; }
        }
        @media screen and (max-width: 767px) {
          .pwc-s9-section { min-height: 25rem !important; }
          .pwc-s9-layout { display: flex !important; flex-flow: column; }
        }
      `}</style>

      <div
        className="container"
        style={{
          display: "flex",
          width: "100%",
          maxWidth: "120rem",
          marginLeft: "auto",
          marginRight: "auto",
          paddingLeft: ".625rem",
          paddingRight: ".625rem",
        }}
      >
        <div
          className="layout pwc-s9-layout"
          style={{
            zIndex: 1,
            columnGap: "0px",
            rowGap: "0px",
            flex: 1,
            gridTemplateRows: "auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
            width: "100%",
            display: "grid",
            position: "relative",
          }}
        >
          {/* top horizontal line: grid-area 1 / 1 / 2 / 5 */}
          <div
            className="line pwc-s9-line"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "1 / 1 / 2 / 5",
            }}
          >
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
              <div style={squareStyle(0)} />
              <div style={squareStyle(0.25)} />
              <div style={squareStyle(0.5)} />
              <div style={squareStyle(0.75)} />
              <div style={squareStyle(1)} />
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
          </div>

          {/* content: grid-area 2 / 1 / 5 / 3 */}
          <div
            className="content content--sm"
            style={{
              width: "710px",
              maxWidth: "100%",
              height: "100%",
              position: "relative",
              gridArea: "2 / 1 / 5 / 3",
            }}
          >
            {/* background video: grid-area 1 / 3 / 3 / 5, but positioned absolute fill */}
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
              <div
                className="background__image w-embed"
                data-role="image"
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  maxWidth: "none",
                  height: "1079px",
                  transformStyle: "preserve-3d",
                  position: "absolute",
                  top: "-90px",
                  left: 0,
                  transform: "translate(0px, -90px)",
                }}
              >
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/699462b4ad134eeed985c2a2_Home-Page-6-poster.webp"
                  preload="metadata"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                >
                  <source
                    src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/6994613970e8c61e405cbfc1_Home%20page%206.mp4"
                    type="video/mp4"
                  />
                </video>
              </div>
            </div>
          </div>

          {/* bottom horizontal line (no tablet): grid-area 3 / 1 / 4 / 5 */}
          <div
            className="line line--no-tablet pwc-s9-line"
            data-no-tablet="true"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "3 / 1 / 4 / 5",
            }}
          >
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
              <div style={squareStyle(0)} />
              <div style={squareStyle(0.25)} />
              <div style={squareStyle(0.5)} />
              <div style={squareStyle(0.75)} />
              <div style={squareStyle(1)} />
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
          </div>
        </div>
      </div>
    </section>
  );
}

export default Section9Section;
export { Section9Section };
