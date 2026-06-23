import React from 'react'

/**
 * Section3Section — Longbow "A NEW SPECIES IS BORN" / "Celeritas Levitas" philosophy section.
 * Reproduced from extracted DOM + css_rules (Webflow grid layout).
 */
function Section3Section() {
  const IMG = '/assets/images/696f3ad6feb5e65c0e8e794d_AVCG_Longbow.webp'

  // --- CSS variables from :root ---
  const vars = {
    '--primary': 'white',
    '--primary-5': '#ffffff0d',
    '--primary-10': '#ffffff1a',
    '--primary-20': '#fff3',
    '--background': '#888c8f',
    '--font-family--1': '"Bebas Neue", sans-serif',
    '--font-family--2-variable': '"Lora", "Ebgaramond Variablefont Wght 0", Arial, sans-serif',
  }

  // Big marquee heading (Bebas Neue)
  const headingMarquee = {
    fontFamily: 'var(--font-family--1)',
    letterSpacing: '-0.06em',
    flex: 'none',
    marginTop: '0.0075em',
    marginBottom: '-0.1em',
    paddingTop: '0.01em',
    fontSize: 'clamp(10.625rem, 1.339rem + 14.51vw, 18.75rem)',
    fontWeight: 400,
    lineHeight: '0.8em',
    color: 'var(--primary)',
    whiteSpace: 'nowrap',
  }

  // Decorative horizontal line w/ squares
  const HorizontalLine = () => (
    <div className="line" style={{ width: '100%', position: 'relative', pointerEvents: 'none' }}>
      <div
        className="horizontal-line"
        style={{ width: '100%', height: '1px', position: 'relative', zIndex: 10, transform: 'translate(0, -50%)' }}
      >
        {['0%', '25%', '50%', '75%', '100%'].map((left, i) => (
          <div
            key={i}
            style={{
              backgroundColor: 'var(--primary)',
              width: '7px',
              height: '7px',
              position: 'absolute',
              top: '-50%',
              left,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}
        <div
          style={{
            zIndex: 1,
            backgroundColor: 'var(--primary-20)',
            width: '100vw',
            maxWidth: '100vw',
            height: '1px',
            position: 'absolute',
            top: '50%',
            left: '50%',
            overflow: 'hidden',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </div>
    </div>
  )

  return (
    <section
      className="section"
      id="philosophy"
      style={{
        ...vars,
        display: 'flex',
        width: '100%',
        minHeight: 'min(100vh - 1.25rem, 100vh - 1.25rem)',
        backgroundColor: 'var(--background)',
        color: 'var(--primary)',
        fontFamily: '"Inter", Arial, sans-serif',
      }}
    >
      <style>{`
        @keyframes section3-marquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
        @media (max-width: 991px) {
          .section3-marquee-line { animation-duration: 6s !important; }
        }
      `}</style>

      <div
        className="container"
        style={{
          display: 'flex',
          width: '100%',
          maxWidth: '120rem',
          marginLeft: 'auto',
          marginRight: 'auto',
          paddingLeft: '0.625rem',
          paddingRight: '0.625rem',
        }}
      >
        <div
          className="layout"
          style={{
            zIndex: 1,
            flex: 1,
            display: 'grid',
            gridTemplateRows: 'auto auto auto 1fr',
            gridTemplateColumns: '1fr 1fr 1fr 1fr',
            gridAutoColumns: '1fr',
            width: '100%',
            position: 'relative',
          }}
        >
          {/* Row 1: top line spanning all columns */}
          <div style={{ gridArea: '1 / 1 / 2 / 5' }}>
            <HorizontalLine />
          </div>

          {/* Row 1 headings: A | new | Species */}
          <div style={{ ...headingMarquee, gridArea: '1 / 1 / 2 / 2' }}>A</div>
          <div style={{ ...headingMarquee, gridArea: '1 / 2 / 2 / 3' }}>new</div>
          <div style={{ ...headingMarquee, gridArea: '1 / 3 / 2 / 5', justifySelf: 'end' }}>Species</div>

          {/* Row 2: "IS Born" marquee */}
          <div
            style={{
              gridArea: '2 / 3 / 3 / 4',
              alignSelf: 'end',
              display: 'flex',
              width: '100%',
              height: '100%',
              overflow: 'hidden',
              paddingTop: '3.125rem',
            }}
          >
            <div style={{ flex: 'none', width: '100%', display: 'flex' }}>
              <div
                className="section3-marquee-line"
                style={{
                  flex: 'none',
                  display: 'flex',
                  justifyContent: 'flex-start',
                  alignItems: 'stretch',
                  animation: 'section3-marquee 9s linear infinite',
                  willChange: 'transform',
                }}
              >
                <div style={{ flex: 'none', display: 'flex', alignItems: 'flex-end', justifyContent: 'flex-start' }}>
                  <div style={{ ...headingMarquee, paddingRight: '0.2em' }}>IS Born</div>
                  <div style={{ ...headingMarquee, paddingRight: '0.2em' }}>IS Born</div>
                </div>
              </div>
            </div>
          </div>

          {/* Row 3: bottom line spanning all columns */}
          <div style={{ gridArea: '3 / 1 / 4 / 5' }}>
            <HorizontalLine />
          </div>

          {/* Row 4 col 3: parallax image content */}
          <div
            style={{
              gridArea: '4 / 3 / 5 / 4',
              flex: '0 0 auto',
              width: '100%',
              height: '100%',
              position: 'relative',
            }}
          >
            <div
              style={{
                zIndex: -1,
                pointerEvents: 'none',
                width: '100%',
                height: '100%',
                position: 'absolute',
                inset: '0%',
                overflow: 'hidden',
              }}
            >
              <img
                alt=""
                loading="lazy"
                width="600"
                height="600"
                src={IMG}
                onError={(e) => {
                  e.currentTarget.onerror = null
                  e.currentTarget.src =
                    'https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/696f3ad6feb5e65c0e8e794d_AVCG_Longbow.webp'
                }}
                style={{
                  zIndex: -1,
                  objectFit: 'cover',
                  width: '100%',
                  maxWidth: 'none',
                  height: '100%',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  transform: 'translateZ(0)',
                }}
              />
            </div>
          </div>

          {/* Row 4 col 1: philosophy card */}
          <div
            style={{
              gridArea: '4 / 1 / 5 / 2',
              zIndex: 2,
              alignSelf: 'end',
              display: 'flex',
              flexFlow: 'column',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              rowGap: '2rem',
              columnGap: '2rem',
              backgroundColor: 'var(--primary-5)',
              backdropFilter: 'blur(1.75rem)',
              WebkitBackdropFilter: 'blur(1.75rem)',
              color: 'var(--primary)',
              paddingBlock: 'clamp(1.25rem, 2.23vw - .179rem, 2.5rem)',
              paddingInline: 'clamp(1rem, 2.68vw - .714rem, 2.5rem)',
              position: 'relative',
            }}
          >
            <div
              className="card__header"
              style={{
                display: 'flex',
                flexFlow: 'column',
                justifyContent: 'flex-start',
                alignItems: 'flex-start',
                rowGap: '2rem',
                columnGap: '2rem',
              }}
            >
              <div style={{ width: 'auto' }}>
                <div
                  style={{
                    backgroundColor: 'var(--primary-10)',
                    textTransform: 'uppercase',
                    borderRadius: '0.75rem',
                    width: '100%',
                    padding: '0.625rem',
                    fontSize: 'clamp(.688rem, .33rem + .56vw, 1rem)',
                    lineHeight: '0.8em',
                    overflow: 'hidden',
                  }}
                >
                  <div style={{ marginLeft: '-0.2em' }}>.01</div>
                </div>
              </div>
              <h2
                className="heading"
                style={{
                  fontFamily: 'var(--font-family--2-variable)',
                  letterSpacing: '-0.03em',
                  marginTop: 0,
                  marginBottom: '-0.1em',
                  paddingBottom: '0.1em',
                  fontSize: 'clamp(1.5rem, .357rem + 1.79vw, 2.5rem)',
                  fontWeight: 400,
                  lineHeight: '0.85em',
                }}
              >
                The "Celeritas Levitas"
                <br />
                <span
                  style={{
                    fontFamily: 'var(--font-family--2-variable)',
                    fontStyle: 'italic',
                    lineHeight: '0.85em',
                  }}
                >
                  Philosophy
                </span>
              </h2>
            </div>
            <p
              className="text"
              style={{
                width: '301px',
                maxWidth: '100%',
                textTransform: 'uppercase',
                marginBottom: 0,
                marginTop: 0,
                letterSpacing: '-0.03em',
                fontSize: 'clamp(.688rem, .33rem + .56vw, 1rem)',
                fontWeight: 400,
                lineHeight: '1.2em',
                color: 'var(--primary)',
              }}
            >
              Our motto, meaning "speed in lightness," is at the core of everything we do. Instead of chasing
              excessive power, we focus on reducing weight. This makes our cars incredibly responsive and agile,
              reviving the pure driving pleasure inherent in classic British sports cars.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Section3Section
