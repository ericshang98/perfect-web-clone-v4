import React from "react";

// Section 7 — "Celeritas levitatis" speed/lightness section (Longbow clone)
// Background grey #888c8f, EB Garamond headings (italic), Geist Mono body.
// Layout: 4-col grid (layout--lg) with horizontal divider lines and 3 numbered cards.

const GARAMOND = '"Ebgaramond Variablefont Wght 0", "EB Garamond", Lora, Georgia, serif';
const MONO = '"Geist Mono", "Geist Mono V4", "Inter", monospace';

const CDN = "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/";

const PARTNER_LOGOS = [
  "68b6cdd827bb1a94982d745a_partner-logo-1.png",
  "68b6cdd8ceccbbf522a08381_partner-logo-2.png",
  "68b6cdd8d6b38a4035ad1e3a_partner-logo-3.png",
  "68b6cdd861a5e3783183ad84_partner-logo-4.png",
  "68b6cdd8a300cadb24d061bd_partner-logo-5.png",
  "68b6cdd8b4023932856b47ac_partner-logo-6.png",
  "68b6cdd86e8e2aa18cf24e23_partner-logo-7.png",
  "68b6cdd8aa28547d00f8044d_partner-logo-8.png",
  "68b6cdd8ed835efaedd596ea_partner-logo-9.png",
  "68b6cdd80a451b7e7aba7feb_partner-logo-10.png",
  "68b6cdd885a313e6cfc7d2b9_partner-logo-11.png",
  "68b6cdd8be1b36fdd3349c92_partner-logo-12.png",
];

// Horizontal divider with the 5 square markers (square / 25 / 50 / 75 / 100)
function HorizontalLine({ gridArea, className = "", style }) {
  const squarePositions = ["0%", "25%", "50%", "75%", "100%"];
  return (
    <div
      className={`line ${className}`}
      style={{ pointerEvents: "none", width: "100%", position: "relative", gridArea, ...style }}
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
        {squarePositions.map((left, i) => (
          <div
            key={i}
            className="square"
            style={{
              backgroundColor: "white",
              width: "7px",
              height: "7px",
              position: "absolute",
              top: "-50%",
              left,
              transform: "translate(-50%, -50%)",
            }}
          />
        ))}
        <div
          className="horizontal-line-full-width"
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
    </div>
  );
}

// Numbered feature card
function FeatureCard({ number, heading, paragraph, gridArea }) {
  return (
    <div
      className="card"
      style={{
        gridArea,
        zIndex: 2,
        gap: "2rem",
        backgroundColor: "#ffffff0d",
        backdropFilter: "blur(1.75rem)",
        WebkitBackdropFilter: "blur(1.75rem)",
        color: "white",
        display: "flex",
        flexFlow: "column",
        justifyContent: "space-between",
        alignItems: "flex-start",
        paddingBlock: "clamp(1.25rem, 2.23vw - .179rem, 2.5rem)",
        paddingInline: "clamp(1rem, 2.68vw - .714rem, 2.5rem)",
        position: "relative",
        maxWidth: "100%",
      }}
    >
      <div
        className="card__header"
        style={{ gap: "2rem", display: "flex", flexFlow: "column", justifyContent: "flex-start", alignItems: "flex-start" }}
      >
        <div className="tag-wrapper tag-wrapper--sm" style={{ width: "auto" }}>
          <div
            className="tag"
            style={{
              backgroundColor: "#ffffff1a",
              textTransform: "uppercase",
              borderRadius: ".75rem",
              padding: ".625rem",
              fontSize: "clamp(.688rem, .33rem + .56vw, 1rem)",
              lineHeight: ".8em",
              overflow: "hidden",
              fontFamily: MONO,
              letterSpacing: "-.03em",
            }}
          >
            <div className="tag__text-number" style={{ marginLeft: "-.2em" }}>
              {number}
            </div>
          </div>
        </div>
        <h2
          className="heading"
          style={{
            fontFamily: GARAMOND,
            letterSpacing: "-.03em",
            margin: "0 0 -.1em 0",
            paddingBottom: ".1em",
            fontSize: "clamp(1.5rem, .357rem + 1.79vw, 2.5rem)",
            fontWeight: 400,
            lineHeight: ".85em",
          }}
        >
          {heading}
        </h2>
      </div>
      <p
        className="text"
        style={{
          textTransform: "uppercase",
          margin: 0,
          width: "301px",
          maxWidth: "100%",
          fontFamily: MONO,
          letterSpacing: "-.03em",
          fontSize: "clamp(.688rem, .33rem + .56vw, 1rem)",
          fontWeight: 400,
          lineHeight: "1.5em",
        }}
      >
        {paragraph}
      </p>
    </div>
  );
}

export default function Section7Section() {
  // Duplicated logo list for seamless marquee loop (matches source: 12 + 12)
  const marqueeLogos = [...PARTNER_LOGOS, ...PARTNER_LOGOS];

  return (
    <section
      className="section section--lg"
      style={{
        display: "flex",
        width: "100%",
        minHeight: "min(150dvh, 95.625rem)",
        backgroundColor: "#888c8f",
        color: "white",
        fontFamily: MONO,
        letterSpacing: "-.03em",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <style>{`
        @keyframes section7MarqueeMove { 0% { transform: translate(0); } 100% { transform: translate(-50%); } }
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
          className="layout layout--lg"
          style={{
            zIndex: 1,
            flex: 1,
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridTemplateRows: "auto 1fr auto 1fr auto 1fr",
            gap: 0,
            width: "100%",
            maxWidth: "100%",
            position: "relative",
          }}
        >
          {/* Row 1: top divider */}
          <HorizontalLine gridArea="1 / 1 / 2 / 5" />

          {/* Row 2: speed / heading + marquees */}
          <div
            className="speed"
            style={{
              gridArea: "2 / 2 / 3 / 4",
              display: "flex",
              flexFlow: "column",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "clamp(1.75rem, 1.568rem + .7767vw, 2.5rem)",
              maxWidth: "100%",
            }}
          >
            <div
              className="speed__content"
              style={{
                display: "flex",
                gap: "1.625rem",
                textAlign: "center",
                justifyContent: "center",
                alignItems: "center",
                paddingTop: "clamp(2.25rem, 2.1893rem + .2589vw, 2.5rem)",
                paddingLeft: "1.625rem",
                paddingRight: "1.625rem",
                maxWidth: "100%",
              }}
            >
              {/* left bracket */}
              <div
                className="speed__bracket"
                style={{ display: "flex", justifyContent: "center", alignItems: "center", flex: "0 0 auto", width: "1.125rem", color: "white" }}
              >
                <svg fill="none" height="110" viewBox="0 0 18 110" width="18" style={{ width: "18px", height: "110px", flex: "0 0 auto" }} xmlns="http://www.w3.org/2000/svg">
                  <path d="M14.7626 110C4.92086 91.6667 0 73.3333 0 55C0 36.6667 4.92086 18.3333 14.7626 0H18C-0.129497 36.6667 -0.129497 73.3333 18 110H14.7626Z" fill="currentColor" />
                </svg>
              </div>

              {/* heading */}
              <div className="speed__text" style={{ maxWidth: "45.125rem" }}>
                <p
                  className="heading heading--lh-md"
                  style={{
                    fontFamily: GARAMOND,
                    letterSpacing: "-.03em",
                    margin: "0 0 -.2em 0",
                    paddingBottom: ".2em",
                    fontSize: "clamp(1.5rem, .357rem + 1.79vw, 2.5rem)",
                    fontWeight: 400,
                    lineHeight: "1.3em",
                  }}
                >
                  <span className="heading-italic" style={{ fontFamily: GARAMOND, fontStyle: "italic", lineHeight: ".8em" }}>
                    Celeritas levitatis
                  </span>{" "}
                  — speaks not just of modern capability but of nimble agility and near-weightless poise, evoking the effortless thrill that defined Britain&rsquo;s most legendary sports cars.
                </p>
              </div>

              {/* right bracket */}
              <div
                className="speed__bracket"
                style={{ display: "flex", justifyContent: "center", alignItems: "center", flex: "0 0 auto", width: "1.125rem", color: "white" }}
              >
                <svg fill="none" height="110" viewBox="0 0 18 110" width="18" style={{ width: "18px", height: "110px", flex: "0 0 auto" }} xmlns="http://www.w3.org/2000/svg">
                  <path d="M3.23741 110C13.0791 91.6667 18 73.3333 18 55C18 36.6667 13.0791 18.3333 3.23741 0H0C18.1295 36.6667 18.1295 73.3333 0 110H3.23741Z" fill="currentColor" />
                </svg>
              </div>
            </div>

            {/* marquees */}
            <div
              className="speed__marquees"
              style={{
                display: "flex",
                flexFlow: "column",
                justifyContent: "flex-start",
                alignItems: "center",
                gap: "clamp(.5rem, .318rem + .7767vw, 1.25rem)",
                width: "100%",
              }}
            >
              {/* "AS FEATURED IN" text marquee */}
              <div className="tag-wrapper tag-wrapper--xl" style={{ width: "9.75rem" }}>
                <div
                  className="tag tag--dark"
                  style={{
                    backgroundColor: "#191919",
                    color: "#fff9",
                    textTransform: "uppercase",
                    borderRadius: ".75rem",
                    width: "100%",
                    padding: ".625rem",
                    fontSize: "clamp(.688rem, .33rem + .56vw, 1rem)",
                    lineHeight: ".8em",
                    overflow: "hidden",
                    fontFamily: MONO,
                    letterSpacing: "-.03em",
                  }}
                >
                  <div style={{ display: "flex", overflow: "hidden", width: "100%" }}>
                    <div
                      style={{
                        display: "flex",
                        width: "max-content",
                        animation: "section7MarqueeMove 15s linear infinite",
                      }}
                    >
                      <div style={{ display: "flex", width: "max-content" }}>
                        {[0, 1, 2, 3].map((i) => (
                          <div key={i} className="tag__text" style={{ flex: "none", marginLeft: "-.1em", paddingTop: ".1em", paddingRight: "1em" }}>
                            .AS FEATURED IN
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* partner logo marquee — 12 images (duplicated for loop) */}
              <div
                className="marquee-wrapper marquee-wrapper--mobile"
                style={{ display: "flex", width: "100%", maxWidth: "100%", height: "100%", overflow: "hidden" }}
              >
                <div style={{ display: "flex", width: "100%", maxWidth: "100%", overflow: "hidden" }}>
                  <div
                    style={{
                      display: "flex",
                      width: "max-content",
                      maxWidth: "100%",
                      animation: "section7MarqueeMove 30s linear infinite",
                    }}
                  >
                    <div style={{ display: "flex", width: "max-content", alignItems: "flex-end" }}>
                      {marqueeLogos.map((file, i) => (
                        <img
                          key={i}
                          alt=""
                          loading="eager"
                          className="marquee-logo"
                          src={`/assets/images/${file}`}
                          onError={(e) => {
                            if (e.currentTarget.src.indexOf(CDN) === -1) e.currentTarget.src = CDN + file;
                          }}
                          style={{
                            flex: "none",
                            height: "clamp(5.125rem, 5.0036rem + .5178vw, 5.625rem)",
                            paddingRight: "clamp(1.25rem, 1.1286rem + .5178vw, 1.75rem)",
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Row 3: divider */}
          <HorizontalLine gridArea="3 / 1 / 4 / 5" />

          {/* Row 4: card .01 (cols 1-2) */}
          <FeatureCard
            number=".01"
            gridArea="4 / 1 / 5 / 2"
            heading={
              <>
                Adding{" "}
                <span className="heading-italic" style={{ fontFamily: GARAMOND, fontStyle: "italic", lineHeight: ".8em" }}>
                  Lightness
                </span>
              </>
            }
            paragraph="This is the open secret to achieving true speed. It's not just about going fast in a straight line, but a foundational principle that enhances every aspect of movement and interaction."
          />

          {/* Row 4: card .02 (cols 4-5) */}
          <FeatureCard
            number=".02"
            gridArea="4 / 4 / 5 / 5"
            heading={
              <>
                Precision{" "}
                <span className="heading-italic" style={{ fontFamily: GARAMOND, fontStyle: "italic", lineHeight: ".8em" }}>
                  &amp;
                  <br />
                  Weight Elimination
                </span>
              </>
            }
            paragraph="Lightness manifests not just in straight-line motion, but in every nuance, every turn, and every maneuver. Excess weight inevitably invites complexity, blunts agility, and dulls the senses, while its removal unlocks true potential."
          />

          {/* Row 5: divider */}
          <HorizontalLine gridArea="5 / 1 / 6 / 5" />

          {/* Row 6: card .03 (cols 3-4) */}
          <FeatureCard
            number=".03"
            gridArea="6 / 3 / 7 / 4"
            heading={
              <>
                The Art{" "}
                <span className="heading-italic" style={{ fontFamily: GARAMOND, fontStyle: "italic", lineHeight: ".8em" }}>
                  of
                  <br />
                  Lightweight Engineering
                </span>
              </>
            }
            paragraph="Speed, agility, and safety are inseparable; they are intrinsically linked and shaped by the artistry of lightweight engineering. This points to weight optimization as an art form that sculpts fundamental characteristics and performance."
          />
        </div>
      </div>
    </section>
  );
}
