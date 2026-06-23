import React from "react";

const FONT_STACK = '"Bebas Neue", sans-serif';

// Reusable horizontal line with 5 squares + full-width hairline
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
      {[0, 25, 50, 75, 100].map((pos) => (
        <div
          key={pos}
          style={{
            backgroundColor: "white",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: `${pos}%`,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
      <div
        style={{
          zIndex: 1,
          backgroundColor: "#fff3",
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

const headingMarqueeBase = {
  fontFamily: FONT_STACK,
  letterSpacing: "-.06em",
  flex: "none",
  marginTop: ".0075em",
  marginBottom: "-.1em",
  paddingTop: ".01em",
  paddingRight: ".2em",
  fontSize: "clamp(10.625rem, 1.339rem + 14.51vw, 18.75rem)",
  fontWeight: 400,
  lineHeight: ".8em",
  color: "white",
};

const noPad = { ...headingMarqueeBase, paddingRight: 0 };
const bottomRight = {
  ...headingMarqueeBase,
  paddingRight: ".05em",
  textAlign: "right",
};

export default function Section6Section() {
  return (
    <section className="section" style={{ width: "100%", minHeight: "min(100vh - 1.25rem, 100vh - 1.25rem)", display: "flex" }}>
      <style>{`
        @keyframes section6-marqueeMovingLine { 0% { transform: translate(0); } 100% { transform: translate(-50%); } }
      `}</style>
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
          className="layout layout--min-row"
          style={{
            zIndex: 1,
            columnGap: 0,
            rowGap: 0,
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
          {/* Top line: row 1, spans all columns */}
          <div
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "1 / 1 / 2 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* "The" : row 2, col 1 */}
          <div style={{ ...noPad, gridArea: "2 / 1 / 3 / 2" }}>The</div>

          {/* Marquee "Speed" : row 2, col 2 */}
          <div
            style={{
              gridArea: "2 / 2 / 3 / 3",
              width: "100%",
              height: "100%",
              display: "flex",
              overflow: "hidden",
            }}
          >
            <div
              data-marquee-role="parent"
              data-marquee-state="enabled"
              style={{
                flex: "none",
                width: "100%",
                display: "flex",
                flexDirection: "row",
                justifyContent: "start",
                overflow: "hidden",
              }}
            >
              <div
                data-marquee-role="moving-line"
                style={{
                  flex: "none",
                  justifyContent: "flex-start",
                  alignItems: "flex-start",
                  display: "flex",
                  width: "max-content",
                  animationName: "section6-marqueeMovingLine",
                  animationDuration: "9s",
                  animationTimingFunction: "linear",
                  animationIterationCount: "infinite",
                  animationPlayState: "running",
                }}
              >
                <div
                  data-marquee-role="list"
                  style={{
                    flex: "none",
                    justifyContent: "flex-start",
                    alignItems: "flex-end",
                    display: "flex",
                    flexDirection: "row",
                    gap: 0,
                    width: "max-content",
                  }}
                >
                  <div style={headingMarqueeBase}>Speed</div>
                  <div style={headingMarqueeBase}>Speed</div>
                </div>
              </div>
            </div>
          </div>

          {/* "Of" : row 2, col 4 */}
          <div style={{ ...noPad, gridArea: "2 / 4 / 3 / 5" }}>Of</div>

          {/* "Lightness" : row 2, cols 1-3, bottom aligned, right text */}
          <div style={{ ...bottomRight, gridArea: "2 / 1 / 3 / 4", alignSelf: "end" }}>
            Lightness
          </div>

          {/* Bottom line: row 3, spans all columns */}
          <div
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "3 / 1 / 4 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Logo video : row 4, cols 2-3, centered */}
          <div
            data-role="image"
            style={{
              opacity: 1,
              gridArea: "4 / 2 / 5 / 4",
              placeSelf: "center",
              aspectRatio: "1 / 1.55",
              justifyContent: "center",
              alignItems: "center",
              width: "auto",
              height: "min(100%, 20.75rem)",
              display: "flex",
              position: "relative",
            }}
          >
            <div
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
              <div className="w-embed" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b6c41772f17c06d2d46aed_longbow-logo-poster.jpg"
                  preload="metadata"
                  style={{ width: "100%", height: "100%", objectFit: "contain" }}
                >
                  <source
                    src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/68b6c36d9e9a0dbce2c8bcd8_longbow-logo-video.mp4"
                    type="video/mp4"
                  />
                </video>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
