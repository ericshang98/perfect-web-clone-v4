import React from "react";

// Section 13 — "A VISION BORN OF SPIRIT & FORGED BY REASON"
// Full-viewport dark display section reproduced from the Longbow source.
// Bebas Neue display marquee headings over a centered video background with an
// italic ampersand SVG icon. Layout = 4-column CSS grid (rows: line / heading /
// line / video / line / marquee+by-reason).

const FONT_1 = '"Bebas Neue", sans-serif';
const FONT_2 = '"EB Garamond", "Ebgaramond Variablefont Wght 0", Arial, sans-serif';
const PRIMARY = "#ffffff";
const PRIMARY_20 = "#ffffff33";
const BG_ALT = "#000000";

// A horizontal hairline with 5 small squares marking the column edges.
function HorizontalLine() {
  const squares = [
    { left: "0%" },
    { left: "25%" },
    { left: "50%" },
    { left: "75%" },
    { left: "100%" },
  ];
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
      {squares.map((s, i) => (
        <div
          key={i}
          className="square"
          style={{
            backgroundColor: PRIMARY,
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: s.left,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
      <div className="horizontal-line-full-width" style={{ backgroundColor: PRIMARY_20, width: "100%", height: "1px" }} />
    </div>
  );
}

const headingMarqueeStyle = {
  fontFamily: FONT_1,
  letterSpacing: "-.06em",
  flex: "none",
  marginTop: ".0075em",
  marginBottom: "-.1em",
  paddingTop: ".01em",
  paddingRight: "0", // heading-marquee--no-pad
  fontSize: "clamp(10.625rem, 1.339rem + 14.51vw, 18.75rem)",
  fontWeight: 400,
  lineHeight: ".8em",
  color: PRIMARY,
  textTransform: "uppercase",
};

export default function Section13Section() {
  return (
    <section
      className="section section--lg-xl"
      style={{
        display: "flex",
        width: "100%",
        minHeight: "min(150dvh, 95.625rem)",
        backgroundColor: BG_ALT,
        color: PRIMARY,
        overflow: "hidden",
      }}
    >
      <style>{`
        @keyframes section13MarqueeMovingLine {
          0% { transform: translate(0); }
          100% { transform: translate(-50%); }
        }
        .section13-moving-line {
          animation-name: section13MarqueeMovingLine;
          animation-duration: 15s;
          animation-iteration-count: infinite;
          animation-timing-function: linear;
          width: max-content;
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
          className="layout layout--lg-xl layout--min-row"
          style={{
            zIndex: 1,
            flex: 1,
            display: "grid",
            position: "relative",
            width: "100%",
            columnGap: "0px",
            rowGap: "0px",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridTemplateRows: "auto 1fr auto 1fr auto 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
          }}
        >
          {/* Row 1 — top line (1 / 1 / 2 / 5) */}
          <div className="line" style={{ gridArea: "1 / 1 / 2 / 5", pointerEvents: "none", width: "100%", position: "relative" }}>
            <HorizontalLine />
          </div>

          {/* Row 2 — heading "A VISION BORN / OF SPIRIT" (2 / 1 / 3 / 5) */}
          <div
            className="text-center"
            style={{ gridArea: "2 / 1 / 3 / 5", textAlign: "center", width: "100%" }}
          >
            <div className="heading-marquee heading-marquee--no-pad" style={headingMarqueeStyle}>
              A VISION BORN
              <br />
              OF SPIRIT{" "}
            </div>
          </div>

          {/* Row 3 — line (3 / 1 / 4 / 5) */}
          <div className="line" style={{ gridArea: "3 / 1 / 4 / 5", pointerEvents: "none", width: "100%", position: "relative" }}>
            <HorizontalLine />
          </div>

          {/* Row 4 — video content (4 / 2 / 5 / 4) */}
          <div
            className="content"
            style={{ gridArea: "4 / 2 / 5 / 4", width: "100%", height: "100%", position: "relative" }}
          >
            <div
              className="background background--brightness"
              style={{
                zIndex: -1,
                pointerEvents: "none",
                width: "100%",
                height: "100%",
                position: "absolute",
                inset: "0%",
                overflow: "hidden",
                filter: "brightness(75%)",
              }}
            >
              <div
                className="background__image"
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  height: "539px",
                  position: "absolute",
                  top: "-45px",
                  left: 0,
                  transform: "translate(0px, -45px)",
                }}
              >
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68df8ce85d27c93f9f8e2268_Design.webp"
                  preload="metadata"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                >
                  <source
                    src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/68df8c79160157382efba6eb_LongbowDesignVi.mp4"
                    type="video/mp4"
                  />
                </video>
              </div>

              {/* Italic ampersand SVG icon, mix-blend difference */}
              <div
                className="background__icon"
                style={{
                  color: PRIMARY,
                  mixBlendMode: "difference",
                  justifyContent: "center",
                  alignItems: "center",
                  display: "flex",
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  fontFamily: FONT_2,
                }}
              >
                <svg
                  fill="none"
                  height="100%"
                  style={{ width: "205px", height: "180px", flex: "0 0 auto" }}
                  viewBox="0 0 210 184"
                  width="100%"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M52.3496 184C42.1203 184 32.9943 182.202 24.9713 178.606C17.149 174.81 11.0315 169.716 6.61891 163.322C2.2063 156.929 0 149.637 0 141.446C0 125.464 4.71347 112.378 14.1404 102.189C23.7679 92 35.8023 83.6091 50.2435 77.0163L56.2607 74.3192L51.7478 69.5244C49.9427 67.3268 47.4355 64.6298 44.2264 61.4332C41.2178 58.2367 38.4097 54.4408 35.8023 50.0456C33.3954 45.4506 32.192 40.2562 32.192 34.4625C32.192 27.4701 34.1977 21.3768 38.2092 16.1824C42.4212 10.9881 47.7364 6.9924 54.1547 4.19544C60.5731 1.39848 67.192 0 74.0115 0C82.6361 0 89.7564 1.99783 95.3725 5.99348C100.989 9.78936 105.201 14.5842 108.009 20.3779C110.817 25.9718 112.221 31.3659 112.221 36.5603C112.421 44.152 109.713 50.7448 104.097 56.3388C98.4814 61.9327 90.659 66.5277 80.6304 70.1238L76.4183 71.6222L80.3295 75.8176C87.9513 84.0087 94.8711 91.101 101.089 97.0945C107.307 103.088 113.424 110.48 119.441 119.27L123.052 124.665L128.467 118.971C133.281 113.776 138.195 107.983 143.209 101.59C148.424 95.1965 152.736 89.4028 156.146 84.2085C159.756 78.8143 161.562 75.418 161.562 74.0195C161.562 72.8209 160.759 71.2226 159.155 69.2248C157.751 67.2269 155.745 66.0282 153.138 65.6287C152.736 65.4289 152.034 64.9294 151.032 64.1303C150.029 63.3312 149.527 62.7318 149.527 62.3322C149.527 60.734 150.43 59.835 152.235 59.6352C154.241 59.2356 155.544 59.0358 156.146 59.0358C156.748 59.0358 158.453 59.1357 161.261 59.3355C164.269 59.5353 167.378 59.835 170.587 60.2345C173.797 60.4343 176.103 60.5342 177.507 60.5342C180.516 60.5342 183.825 60.2345 187.436 59.6352C191.046 58.8361 194.456 58.0369 197.665 57.2378C201.074 56.4387 203.983 56.0391 206.39 56.0391C206.791 56.0391 207.493 56.3388 208.496 56.9381C209.499 57.5375 210 58.1368 210 58.7362C210 59.9349 209.097 61.1336 207.292 62.3322C205.487 63.5309 203.883 64.2302 202.478 64.43C197.865 64.6298 193.653 65.7286 189.842 67.7264C186.031 69.5244 182.923 71.5223 180.516 73.7199C179.713 74.3192 177.407 76.6167 173.596 80.6124C169.785 84.608 165.172 89.4028 159.756 94.9967C154.542 100.391 149.427 105.785 144.413 111.179C139.398 116.573 135.186 121.068 131.776 124.665C128.367 128.261 126.662 130.059 126.662 130.059L131.776 137.251C138.195 146.441 144.513 153.833 150.731 159.427C156.948 164.821 163.868 167.518 171.49 167.518C175.702 167.518 179.713 167.118 183.524 166.319C187.536 165.52 191.347 164.122 194.957 162.124C195.759 161.724 196.562 161.425 197.364 161.225C198.367 160.825 199.269 160.625 200.072 160.625C201.476 160.625 202.378 160.925 202.779 161.524C203.381 161.924 203.682 162.823 203.682 164.222C203.682 165.82 201.576 168.217 197.364 171.414C193.152 174.61 188.037 177.507 182.02 180.104C176.203 182.701 170.487 184 164.871 184C157.45 184 151.232 182.701 146.218 180.104C141.203 177.707 136.59 174.011 132.378 169.016C128.367 163.822 123.754 157.229 118.539 149.238L114.628 142.945L112.822 144.743C106.605 151.535 100.587 157.928 94.7708 163.922C89.1547 169.915 83.0372 174.81 76.4183 178.606C69.7994 182.202 61.7765 184 52.3496 184ZM60.1719 164.521C70.2006 164.521 78.8252 162.423 86.0458 158.228C93.467 154.033 100.888 148.039 108.309 140.248L111.017 137.55L107.407 131.857C102.393 124.265 96.0745 116.573 88.4527 108.782C81.0315 100.99 73.0086 92.4995 64.3839 83.3095L60.7736 79.4137L54.4556 81.8111C45.2292 85.4072 38.3095 90.0022 33.6963 95.5961C29.2837 100.99 26.3754 106.884 24.9713 113.277C23.7679 119.47 23.1662 125.564 23.1662 131.557C23.1662 140.747 26.5759 148.539 33.3954 154.932C40.2149 161.325 49.1404 164.521 60.1719 164.521ZM72.5072 66.8274L76.4183 65.0293C82.0344 62.4321 86.1461 58.3366 88.7536 52.7427C91.5616 46.949 92.9656 41.0554 92.9656 35.0619C92.9656 28.0695 91.2607 21.7763 87.851 16.1824C84.6418 10.5885 79.5272 7.79154 72.5072 7.79154C66.49 7.79154 61.1748 9.68947 56.5616 13.4853C51.9484 17.0814 49.6418 21.5766 49.6418 26.9707C49.6418 30.9663 50.043 34.5624 50.8453 37.759C51.6476 40.9555 53.3524 44.3518 55.9599 47.9479C58.5673 51.544 62.4785 56.139 67.6934 61.7329L72.5072 66.8274Z"
                    fill="currentColor"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Row 5 — line (5 / 1 / 6 / 5) */}
          <div className="line" style={{ gridArea: "5 / 1 / 6 / 5", pointerEvents: "none", width: "100%", position: "relative" }}>
            <HorizontalLine />
          </div>

          {/* Row 6 col 2-4 — "FORGED" scrolling marquee (6 / 2 / 7 / 4) */}
          <div
            className="marquee-wrapper"
            style={{
              gridArea: "6 / 2 / 7 / 4",
              width: "100%",
              height: "100%",
              display: "flex",
              overflow: "hidden",
            }}
          >
            <div
              className="marquee-parent"
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
                className="section13-moving-line marquee-moving-line marquee-moving-line--y-start"
                style={{
                  flex: "none",
                  justifyContent: "flex-start",
                  alignItems: "flex-start",
                  display: "flex",
                }}
              >
                <div
                  className="marquee-list"
                  style={{
                    flex: "none",
                    justifyContent: "flex-start",
                    alignItems: "flex-end",
                    display: "flex",
                    gap: 0,
                    flexDirection: "row",
                    width: "max-content",
                  }}
                >
                  {[0, 1, 2, 3].map((i) => (
                    <div key={i} className="heading-marquee" style={headingMarqueeStyle}>
                      FORGED{" "}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Row 6 full width — "BY REASON" bottom heading (6 / 1 / 7 / 5, align end) */}
          <div
            className="text-center text-center--no-mobile"
            style={{
              gridArea: "6 / 1 / 7 / 5",
              alignSelf: "end",
              textAlign: "center",
              width: "100%",
            }}
          >
            <div className="heading-marquee heading-marquee--no-pad" style={headingMarqueeStyle}>
              BY REASON
            </div>
          </div>

          {/* Row 5 — bottom line (5 / 1 / 6 / 5) — line--no-mobile variant */}
          <div
            className="line line--no-mobile"
            style={{ gridArea: "5 / 1 / 6 / 5", pointerEvents: "none", width: "100%", position: "relative" }}
          >
            <HorizontalLine />
          </div>
        </div>
      </div>
    </section>
  );
}
