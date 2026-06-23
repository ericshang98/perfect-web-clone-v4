import React from "react";

// Section 5 — Longbow ".03 The Soul of a Classic" preview grid
// Reproduced from section-5.json (raw_html + css_rules).
function Section5Section() {
  const onImgError = (e) => {
    const remote = e.currentTarget.getAttribute("data-remote");
    if (remote && e.currentTarget.src !== remote) {
      e.currentTarget.src = remote;
    }
  };

  // Decorative horizontal line with squares (reused 3x)
  const HorizontalLine = () => (
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
      ].map((sq, i) => (
        <div
          key={i}
          style={{
            backgroundColor: "var(--primary)",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: sq.left,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
      <div
        style={{
          zIndex: 1,
          backgroundColor: "var(--primary-20)",
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

  return (
    <section
      className="section"
      data-name="main-child"
      id="preview"
      style={{
        width: "100%",
        minHeight: "min(100vh - 1.25rem, 100vh - 1.25rem)",
        display: "flex",
        // section-local CSS variables (from :root in css_rules)
        ["--primary"]: "white",
        ["--primary-20"]: "#fff3",
        ["--primary-5"]: "#ffffff0d",
        ["--primary-10"]: "#ffffff1a",
        ["--font-family--2-variable"]:
          '"EB Garamond", "Ebgaramond Variablefont Wght 0", Arial, sans-serif',
      }}
    >
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
          className="layout layout--min-row"
          style={{
            zIndex: 1,
            columnGap: "0px",
            rowGap: "0px",
            flex: 1,
            display: "grid",
            gridTemplateRows: "auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
            width: "100%",
            position: "relative",
          }}
        >
          {/* line — grid 1 / 1 / 2 / 5 */}
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

          {/* content (video) — grid 2 / 3 / 5 / 5 */}
          <div
            className="content"
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              gridArea: "2 / 3 / 5 / 5",
              opacity: 1,
            }}
          >
            {/* background--auto-brightness, grid 1 / 3 / 3 / 5 (overlaps upward) */}
            <div
              className="background background--auto-brightness"
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
                className="background__image"
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  maxWidth: "none",
                  height: "100%",
                  position: "absolute",
                  top: 0,
                  left: 0,
                }}
              >
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b49b8bd0f80cfb0a8e7495_longbow-new-image-4.jpg"
                  preload="metadata"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                >
                  <source
                    src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/6994613958f9745854eaca58_Home%20page%204.mp4"
                    type="video/mp4"
                  />
                </video>
              </div>
            </div>
          </div>

          {/* line — grid 3 / 1 / 4 / 5 */}
          <div
            className="line"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "3 / 1 / 4 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* card (mobile-only, hidden on this static render) */}
          <div
            className="card card--mobile-show"
            style={{ display: "none" }}
          >
            <div
              className="card__header"
              style={{
                columnGap: "2rem",
                rowGap: "2rem",
                display: "flex",
                flexFlow: "column",
                justifyContent: "flex-start",
                alignItems: "flex-start",
              }}
            >
              <div className="tag-wrapper tag-wrapper--sm" style={{ width: "auto" }}>
                <div
                  className="tag"
                  style={{
                    backgroundColor: "var(--primary-10)",
                    textTransform: "uppercase",
                    borderRadius: ".75rem",
                    width: "100%",
                    padding: ".625rem",
                    fontSize: "clamp(.688rem, .33rem + .56vw, 1rem)",
                    lineHeight: ".8em",
                    overflow: "hidden",
                  }}
                >
                  <div>.03</div>
                </div>
              </div>
              <h2
                className="heading"
                style={{
                  fontFamily: "var(--font-family--2-variable)",
                  letterSpacing: "-.03em",
                  marginTop: 0,
                  marginBottom: "-.1em",
                  paddingBottom: ".1em",
                  fontSize: "clamp(1.5rem, .357rem + 1.79vw, 2.5rem)",
                  fontWeight: 400,
                  lineHeight: ".85em",
                }}
              >
                The Soul of a Classic,
                <br />
                <span
                  className="heading-italic"
                  style={{
                    fontFamily: "var(--font-family--2-variable)",
                    fontStyle: "italic",
                    lineHeight: ".8em",
                  }}
                >
                  the Heart of the Future
                </span>
              </h2>
            </div>
            <p
              className="text"
              style={{ textTransform: "uppercase", marginBottom: 0 }}
            >
              Longbow is the spiritual successor to legends like the Lotus Elise
              and Jaguar E-Type, inspired by their "less is more" principle. We
              combine this rich heritage with advanced electric technology to
              create a 21st-century sports car, hand-built in the heart of Great
              Britain.
            </p>
          </div>

          {/* line--mobile (hidden) */}
          <div
            className="line line--mobile"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              display: "none",
            }}
          >
            <HorizontalLine />
          </div>

          {/* content (image 003c) — grid 4 / 1 / 5 / 2 */}
          <div
            className="content"
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              gridArea: "4 / 1 / 5 / 2",
              flex: "0 0 auto",
              opacity: 1,
            }}
          >
            <div
              className="background"
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
                height="600"
                width="500"
                loading="lazy"
                src="/assets/images/696f477faa5daae22a49d7ca_003c.webp"
                data-remote="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/696f477faa5daae22a49d7ca_003c.webp"
                onError={onImgError}
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  maxWidth: "none",
                  height: "100%",
                  position: "absolute",
                  top: 0,
                  left: 0,
                }}
              />
            </div>
          </div>

          {/* content (image 002c) — grid 1 / 1 / 2 / 2 */}
          <div
            className="content"
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              gridArea: "1 / 1 / 2 / 2",
              opacity: 1,
            }}
          >
            <div
              className="background"
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
                height="600"
                width="500"
                loading="lazy"
                src="/assets/images/696f44640e98f91aebeb645a_002c.webp"
                data-remote="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/696f44640e98f91aebeb645a_002c.webp"
                onError={onImgError}
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  width: "100%",
                  maxWidth: "none",
                  height: "100%",
                  position: "absolute",
                  top: 0,
                  left: 0,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Section5Section;
export { Section5Section };
