import { useRef } from "react";

/**
 * Section2Section — "Roadster / Autograph Edition" feature section.
 *
 * Faithful reproduction of the Longbow Webflow section #roadster:
 *  - Full-viewport-height background image (parallax) at 75% brightness.
 *  - Two decorative horizontal "lines" with measure squares spanning the grid.
 *  - A frosted-glass dark card anchored in the lower-right grid cell containing
 *    the heading, price text, an autoplaying boomerang video, and a Reserve button.
 *  - Hover on the card rounds the inner video + button to 1.25rem (matches
 *    [data-role='hover-trigger']:hover [data-role='image'|'button'] rule).
 */
export default function Section2Section() {
  const imgFallback = (e) => {
    if (e.currentTarget.src.indexOf("cdn.prod.website-files.com") === -1) {
      e.currentTarget.src =
        "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b54c73e45bf5c218603026_longbow-roadster.jpg";
    }
  };

  const HorizontalLine = () => (
    <div
      className="horizontal-line"
      style={{
        zIndex: 10,
        width: "100%",
        height: "1px",
        position: "relative",
        transform: "translate(0, -50%)",
        backgroundColor: "transparent",
      }}
    >
      {/* full-width hairline */}
      <div
        className="horizontal-line-full-width"
        style={{
          position: "absolute",
          inset: 0,
          height: "1px",
          width: "100%",
          backgroundColor: "var(--primary)",
          opacity: 0.2,
        }}
      />
      {[0, 25, 50, 75, 100].map((pos) => (
        <div
          key={pos}
          className={`square${pos ? ` square--${pos}` : ""}`}
          style={{
            backgroundColor: "var(--primary)",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: `${pos}%`,
            transform: "translate(-50%, -50%)",
          }}
        />
      ))}
    </div>
  );

  return (
    <section
      className="section"
      data-name="main-child"
      id="roadster"
      style={{
        width: "100%",
        minHeight: "min(100vh - 1.25rem, 100vh - 1.25rem)",
        display: "flex",
        backgroundColor: "var(--background-alt, #000)",
        color: "var(--primary, #fff)",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <style>{`
        #roadster .layout { grid-template-columns: 1fr 1fr 1fr 1fr; }
        #roadster .roadster-card { grid-area: 4 / 3 / 5 / 4; }
        @media (max-width: 991px) {
          #roadster .layout { grid-template-columns: 1fr 1fr; }
          #roadster .roadster-card { grid-area: auto / 1 / auto / 2 !important; }
        }
        @media (max-width: 767px) {
          #roadster .layout { display: flex !important; flex-flow: column; }
          #roadster .roadster-line { display: none; }
        }
        #roadster .roadster-card [data-role='image'],
        #roadster .roadster-card [data-role='button'] {
          transition: border-radius .3s ease;
        }
        #roadster .roadster-card:hover [data-role='image'],
        #roadster .roadster-card:hover [data-role='button'] {
          border-radius: 1.25rem;
        }
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
          className="layout"
          style={{
            zIndex: 1,
            flex: 1,
            gridTemplateRows: "auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
            width: "100%",
            display: "grid",
            position: "relative",
            columnGap: 0,
            rowGap: 0,
          }}
        >
          {/* Top measure line: spans all columns (1 / 1 / 2 / 5) */}
          <div
            className="line roadster-line"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "1 / 1 / 2 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Background parallax image */}
          <div
            className="background background--brightness background--mobile"
            data-widget="image-parallax"
            style={{
              zIndex: -1,
              pointerEvents: "none",
              position: "absolute",
              inset: "0%",
              width: "100%",
              height: "100%",
              minHeight: "25rem",
              overflow: "hidden",
              filter: "brightness(75%)",
            }}
          >
            <img
              alt=""
              className="background__image"
              data-role="image"
              height="1080"
              loading="eager"
              width="1920"
              src="/assets/images/68b54c73e45bf5c218603026_longbow-roadster.jpg"
              onError={imgFallback}
              style={{
                zIndex: -1,
                objectFit: "cover",
                width: "100%",
                maxWidth: "none",
                height: "100%",
                position: "absolute",
                top: 0,
                left: 0,
                transform: "translateZ(0)",
              }}
            />
          </div>

          {/* Bottom measure line: spans all columns (3 / 1 / 4 / 5) */}
          <div
            className="line roadster-line"
            style={{
              pointerEvents: "none",
              width: "100%",
              position: "relative",
              gridArea: "3 / 1 / 4 / 5",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Card (lower-right cell: 4 / 3 / 5 / 4) */}
          <a
            className="card card--dark roadster-card w-inline-block"
            data-role="hover-trigger"
            data-widget="card-animation"
            href="/roadster#reserve"
            style={{
              zIndex: 2,
              rowGap: "2rem",
              columnGap: "2rem",
              backgroundColor: "var(--grey-20, #3a3a3a33)",
              backdropFilter: "blur(1.75rem)",
              WebkitBackdropFilter: "blur(1.75rem)",
              color: "var(--primary, #fff)",
              flexFlow: "column",
              justifyContent: "space-between",
              alignItems: "flex-start",
              paddingBlock: "clamp(1.25rem, 2.23vw - .179rem, 2.5rem)",
              paddingInline: "clamp(1rem, 2.68vw - .714rem, 2.5rem)",
              textDecoration: "none",
              display: "flex",
              position: "relative",
              minHeight: "25rem",
              alignSelf: "stretch",
            }}
          >
            <div
              className="card__layout"
              style={{
                zIndex: 2,
                rowGap: "1.125rem",
                columnGap: "1.125rem",
                textAlign: "center",
                flexFlow: "column",
                justifyContent: "center",
                alignItems: "center",
                width: "100%",
                height: "100%",
                display: "flex",
                position: "relative",
              }}
            >
              <h2
                className="heading"
                style={{
                  fontFamily: "Lora, Georgia, serif",
                  letterSpacing: "-.03em",
                  marginTop: 0,
                  marginBottom: "-.1em",
                  paddingBottom: ".1em",
                  fontSize: "clamp(1.5rem, .357rem + 1.79vw, 2.5rem)",
                  fontWeight: 400,
                  lineHeight: ".85em",
                }}
              >
                Roadster
                <br />
                <span
                  className="heading-italic"
                  style={{
                    fontFamily: "Lora, Georgia, serif",
                    fontStyle: "italic",
                    lineHeight: ".8em",
                  }}
                >
                  Autograph Edition
                </span>
              </h2>

              <div
                className="text"
                data-widget="text-reveal"
                style={{ textTransform: "uppercase", marginBottom: 0 }}
              >
                £125,000 / Reservation
              </div>

              <div
                className="card__video"
                data-role="image"
                style={{
                  aspectRatio: "1.65",
                  width: "clamp(7.875rem, 13.17vw - .554rem, 15.25rem)",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <div
                  className="background background--mobile"
                  style={{
                    position: "relative",
                    width: "100%",
                    height: "100%",
                    overflow: "hidden",
                  }}
                >
                  <div
                    className="background__image w-embed"
                    style={{
                      position: "absolute",
                      inset: 0,
                      width: "100%",
                      height: "100%",
                    }}
                  >
                    <video
                      autoPlay
                      loop
                      muted
                      playsInline
                      preload="metadata"
                      poster="https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/69946f2c15c8537fcbb8b701_Block-1-boomer-poster.webp"
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                    >
                      <source
                        src="https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/69946f2c90e935d82e71cb71_Block-1-boomer.mp4"
                        type="video/mp4"
                      />
                    </video>
                  </div>
                </div>
              </div>

              <div
                className="button"
                data-role="button"
                style={{
                  rowGap: ".625rem",
                  columnGap: ".625rem",
                  backgroundColor: "var(--primary, #fff)",
                  color: "var(--background-alt, #000)",
                  letterSpacing: "-.03em",
                  justifyContent: "center",
                  alignItems: "center",
                  paddingBlock: "clamp(1rem, .357rem + 1vw, 1.563rem)",
                  paddingInline: "clamp(1rem, 2.23vw - .429rem, 2.25rem)",
                  lineHeight: "1em",
                  textDecoration: "none",
                  display: "flex",
                }}
              >
                <div>Reserve +</div>
              </div>
            </div>
          </a>
        </div>
      </div>
    </section>
  );
}
