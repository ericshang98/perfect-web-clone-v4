import React from "react";

/**
 * HeroSection — Longbow British sports cars landing page hero.
 * Reproduced from extractor JSON (raw_html + css_rules).
 * - Full-bleed dark video background (poster + mp4), brightness-dimmed.
 * - Foreground card: marquee ".Longbow" tag, heading "Be moved — / At The Speed Of Lightness", body copy.
 * - Decorative horizontal lines with progress squares.
 * - Large scrolling "Longbow" wordmark marquee.
 */
export default function HeroSection() {
  const POSTER =
    "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b18a91eb96897d6b22cd33_longbow-hero-image.webp";
  const VIDEO =
    "https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/69945506f2c454c4497b659b_new-longbow-hero-boomerang-video.mp4";

  return (
    <section
      id="hero"
      data-name="main-child"
      className="hero-section"
      style={{
        position: "relative",
        display: "flex",
        width: "100%",
        minHeight: "100vh",
        color: "var(--hero-primary, #ffffff)",
        overflow: "hidden",
        fontFamily: '"Inter", Arial, sans-serif',
      }}
    >
      <style>{`
        .hero-section {
          --hero-primary: #ffffff;
          --hero-primary-20: #ffffff33;
          --hero-primary-10: #ffffff1a;
          --hero-primary-5: #ffffff0d;
        }
        .hero-bg__video {
          width: 100%;
          height: 100%;
          object-fit: cover;
          filter: brightness(0.62);
        }
        @keyframes hero-marquee-scroll {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
        .hero-marquee-moving {
          display: flex;
          width: max-content;
          will-change: transform;
          animation: hero-marquee-scroll linear infinite;
        }
        .hero-tag .hero-marquee-moving { animation-duration: 15s; }
        .hero-longbow .hero-marquee-moving { animation-duration: 15s; }

        .hero-heading {
          font-family: '"Bebas Neue", "Inter", sans-serif';
          font-family: "Bebas Neue", "Inter", sans-serif;
          font-weight: 400;
          line-height: 0.92;
          letter-spacing: 0.01em;
          text-transform: uppercase;
          margin: 0;
        }
        .hero-heading-italic {
          font-family: "Lora", Georgia, serif;
          font-style: italic;
          text-transform: none;
          letter-spacing: 0;
        }
        .hero-tag__text {
          font-family: "Inter", Arial, sans-serif;
          font-size: 0.8125rem;
          letter-spacing: 0.04em;
          white-space: nowrap;
          padding-right: 1.25rem;
          opacity: 0.9;
        }
        .hero-wordmark {
          font-family: "Bebas Neue", "Inter", sans-serif;
          text-transform: uppercase;
          line-height: 1;
          white-space: nowrap;
          padding-right: 4rem;
          opacity: 0.96;
        }
        .hero-square {
          width: 5px;
          height: 5px;
          background: var(--hero-primary);
          opacity: 0.85;
          flex: 0 0 auto;
        }
        .hero-square--dim { opacity: 0.45; }

        @media (max-width: 767px) {
          .hero-card { width: 100% !important; max-width: 100% !important; }
          .hero-card__header { width: 100% !important; max-width: 100% !important; }
          .hero-text { width: 100% !important; max-width: 100% !important; }
          .hero-heading { width: 100% !important; }
          .hero-tag-wrapper--no-mobile { display: none !important; }
          .hero-wordmark { font-size: 22vw; }
        }
      `}</style>

      {/* Background video, brightness-dimmed */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 0,
          width: "100%",
          height: "100%",
        }}
      >
        <video
          className="hero-bg__video"
          autoPlay
          loop
          muted
          playsInline
          poster={POSTER}
          preload="metadata"
          onError={(e) => {
            // hide a broken/blocked video and fall back to the dark gradient below
            e.currentTarget.style.display = "none";
          }}
        >
          <source src={VIDEO} type="video/mp4" />
        </video>
        {/* darkening / vignette so foreground text reads on any frame */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(8,8,9,0.55) 0%, rgba(8,8,9,0.15) 35%, rgba(8,8,9,0.35) 100%)",
          }}
        />
      </div>

      {/* Foreground layout */}
      <div
        className="container"
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          justifyContent: "center",
          width: "100%",
          maxWidth: "100%",
        }}
      >
        <div
          className="layout layout--hero"
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-end",
            gap: "1.75rem",
            width: "1420px",
            maxWidth: "100%",
            minHeight: "100vh",
            padding: "7rem 1.5rem 2.5rem",
            boxSizing: "border-box",
          }}
        >
          {/* Decorative line (top of stack) */}
          <HorizontalLine />

          {/* Hero card */}
          <div
            className="hero-card card card--hero"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1.5rem",
              width: "355px",
              maxWidth: "100%",
            }}
          >
            <div
              className="hero-card__header card__header--hero"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
                width: "284px",
                maxWidth: "100%",
              }}
            >
              {/* Marquee tag */}
              <div className="hero-tag-wrapper--no-mobile" style={{ overflow: "hidden" }}>
                <div className="hero-tag" style={{ overflow: "hidden", maxWidth: "100%" }}>
                  <div
                    style={{
                      display: "flex",
                      overflow: "hidden",
                      borderTop: "1px solid var(--hero-primary-20)",
                      borderBottom: "1px solid var(--hero-primary-20)",
                      padding: "0.35rem 0",
                    }}
                  >
                    <div className="hero-marquee-moving">
                      {[0, 1].map((group) => (
                        <div key={group} style={{ display: "flex" }}>
                          {[0, 1, 2, 3].map((i) => (
                            <div key={i} className="hero-tag__text">
                              .Longbow
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Mobile-only heading is hidden on desktop in source (display:none !important) */}
              <h1
                className="hero-heading"
                style={{ display: "none", fontSize: "3rem" }}
                aria-hidden="true"
              >
                Longbow
              </h1>

              {/* Main heading */}
              <h2
                className="hero-heading"
                style={{ width: "284px", maxWidth: "100%", fontSize: "2.5rem" }}
              >
                Be moved —<br />
                <span className="hero-heading-italic">At The Speed Of Lightness</span>
              </h2>
            </div>

            <p
              className="hero-text"
              style={{
                width: "301px",
                maxWidth: "100%",
                margin: 0,
                fontSize: "0.9375rem",
                lineHeight: 1.55,
                color: "var(--hero-primary)",
                opacity: 0.92,
              }}
            >
              Craftsmanship that doesn&rsquo;t distract, uniting a trinity of driver, road and
              vehicled. Inspired by a rich history, engineered for the future, Speedster &amp;
              Roadster feature tactile cockpits that define time to become timeless
            </p>
          </div>

          {/* Decorative line (above wordmark) */}
          <HorizontalLine />

          {/* Large scrolling Longbow wordmark */}
          <div
            className="hero-longbow"
            style={{ display: "flex", overflow: "hidden", width: "710px", maxWidth: "100%" }}
          >
            <div className="hero-marquee-moving">
              {[0, 1].map((group) => (
                <div
                  key={group}
                  className="hero-wordmark"
                  aria-label="Longbow"
                  style={{ fontSize: "clamp(3.5rem, 7vw, 6.5rem)" }}
                >
                  Longbow
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/** Decorative horizontal rule with progress squares (matches .horizontal-line / .square markup). */
function HorizontalLine() {
  return (
    <div className="line" style={{ width: "100%" }}>
      <div
        className="horizontal-line"
        style={{
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
        }}
      >
        <div className="hero-square" />
        <div className="hero-square hero-square--dim" />
        <div className="hero-square hero-square--dim" />
        <div className="hero-square hero-square--dim" />
        <div className="hero-square" />
        <div
          className="horizontal-line-full-width"
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: "50%",
            height: "1px",
            background: "var(--hero-primary-20)",
            zIndex: -1,
          }}
        />
      </div>
    </div>
  );
}
