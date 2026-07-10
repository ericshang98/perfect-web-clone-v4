// HeroSection — pixel-matched to reference crop (perfect-web-clone method).
// Background comes from the site's fixed .app__background gradient; this
// section stays transparent. The 3D hands are static stills kept as-is.
const FONT = '"GT Walsheim Wero", sans-serif';

export default function HeroSection() {
  return (
    <section
      className="hero"
      style={{ position: 'relative', width: '100%', height: '100svh', overflow: 'hidden' }}
    >
      {/* 3D hands — static stills, sit BEHIND the text */}
      <img
        className="hero-hand"
        src="/assets/images/hero-hand-left.png"
        alt=""
        aria-hidden="true"
        style={{ position: 'absolute', left: 0, bottom: 0, width: '26%', height: 'auto', zIndex: 1, pointerEvents: 'none' }}
      />
      <img
        className="hero-hand"
        src="/assets/images/hero-hand-right.png"
        alt=""
        aria-hidden="true"
        style={{ position: 'absolute', right: 0, bottom: 0, width: '25%', height: 'auto', zIndex: 1, pointerEvents: 'none' }}
      />

      {/* Top logo lockup is rendered by HeaderSection (real SVG) — no duplicate here */}

      {/* Centered headline */}
      <h1
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, calc(-50% - 5vh))',
          margin: 0,
          textAlign: 'center',
          whiteSpace: 'nowrap',
          color: '#1d1c1c',
          fontFamily: FONT,
          fontWeight: 800,
          lineHeight: 0.85,
          fontFeatureSettings: '"ss06" on',
          fontSize: 'clamp(3.4375rem, 9.3851132686vw + 1.2378640777rem, 12.5rem)',
          letterSpacing: '-0.229125rem',
          zIndex: 2,
        }}
      >
        <span style={{ display: 'block' }}>iDEAL IS</span>
        <span style={{ display: 'block' }}>BECOMING</span>
        <span style={{ display: 'block' }}>WERO</span>
      </h1>

      {/* Round green "NOW IN PHASE 1" sticker, upper-right of the headline */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          right: '50%',
          transform: 'translate(403px, -301px)',
          width: '128px',
          zIndex: 5,
        }}
      >
        <img src="/assets/images/sticker-phase-1-en.png" alt="Now in phase 1" style={{ display: 'block', width: '100%', height: 'auto' }} />
      </div>

      {/* White pill scroll button */}
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: '90px', display: 'flex', justifyContent: 'center', zIndex: 6 }}>
        <button
          type="button"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '13px',
            width: '381px',
            padding: '0 13px 0 26px',
            minHeight: '66px',
            background: '#fff',
            color: '#1d1c1c',
            border: '1px solid #1d1c1c',
            borderRadius: '40px',
            boxShadow: '0 6px 0 #1d1c1c',
            fontFamily: FONT,
            fontSize: '1.125rem',
            fontWeight: 500,
            lineHeight: 1.3,
            cursor: 'pointer',
          }}
        >
          <span style={{ flex: 1, textAlign: 'center' }}>Scroll and discover what this means</span>
          <span
            style={{
              flex: '0 0 auto',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#fff48d',
              border: '1px solid #1d1c1c',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <svg width="17" height="18" viewBox="0 0 17 18" fill="none" style={{ width: '12px', height: 'auto' }} xmlns="http://www.w3.org/2000/svg">
              <path d="M0.916104 8.56259L8.38281 16.0293L15.8495 8.56259" stroke="#1D1C1C" strokeWidth="1.33333" />
              <path d="M8.38281 16.0293L8.38282 0.944268" stroke="#1D1C1C" strokeWidth="1.33333" />
            </svg>
          </span>
        </button>
      </div>
    </section>
  );
}
