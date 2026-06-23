import { useState } from "react";

export default function Section() {
  const [imgOk, setImgOk] = useState(true);

  return (
    <section
      id="top"
      data-nav-theme="dark"
      className="sticky top-0 z-0 flex w-full flex-col items-center justify-end px-[5vw] pb-16 text-center"
      style={{ height: "100dvh" }}
    >
      {/* Background image + overlays */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 overflow-hidden bg-black"
        style={{ bottom: "-120px", width: "1440px", maxWidth: "100%" }}
      >
        <div
          className="absolute inset-0"
          style={{
            transform: "scale(1)",
            transition:
              "transform 1800ms cubic-bezier(0.22,1,0.36,1)",
          }}
        >
          <div
            className="absolute"
            style={{
              inset: "-5%",
              willChange: "transform",
              animation: "kenBurns 120s ease-in-out infinite alternate",
            }}
          >
            {imgOk && (
              <img
                alt=""
                decoding="async"
                src="/assets/images/unknown.img"
                onError={() => setImgOk(false)}
                style={{
                  position: "absolute",
                  height: "100%",
                  width: "100%",
                  inset: "0px",
                  objectFit: "cover",
                  objectPosition: "center",
                }}
              />
            )}
          </div>
        </div>

        {/* Dark gradient overlay */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.35) 45%, rgba(0,0,0,0.88) 100%)",
          }}
        />

        {/* Noise overlay */}
        <div
          className="absolute inset-0"
          style={{
            opacity: 0.04,
            mixBlendMode: "overlay",
            pointerEvents: "none",
            backgroundImage:
              "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>\")",
          }}
        />
      </div>

      {/* Foreground content */}
      <div
        className="relative z-10 flex flex-col items-center"
        style={{ width: "711px", maxWidth: "100%", willChange: "transform" }}
      >
        <div style={{ width: "711px", maxWidth: "100%" }}>
          <h1
            className="mx-auto font-light text-white"
            style={{
              maxWidth: "22ch",
              fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
              fontWeight: 300,
              letterSpacing: "-0.005em",
              lineHeight: 1.1,
              fontSize: "clamp(2.75rem, 7vw, 5.5rem)",
            }}
          >
            <span
              className="block overflow-hidden"
              style={{ paddingBottom: "0.08em" }}
            >
              <span className="block">
                Talk your{" "}
                <span style={serifStyle}>day.</span>
              </span>
            </span>
            <span
              className="block overflow-hidden"
              style={{ paddingBottom: "0.08em" }}
            >
              <span className="block">
                Own your{" "}
                <span style={serifStyle}>time.</span>
              </span>
            </span>
          </h1>
        </div>

        <div style={{ width: "672px", maxWidth: "100%" }}>
          <p
            className="mt-6 mx-auto font-light leading-relaxed text-white/80"
            style={{
              maxWidth: "42rem",
              fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
              fontWeight: 300,
              fontSize: "clamp(1rem, 1.4vw, 1.25rem)",
            }}
          >
            Speak freely about your day. Novu turns your thoughts into tasks,
            helps you focus on what matters, and reflects it back to you.
          </p>
          <p
            className="mt-6 mx-auto font-light leading-relaxed text-white/60"
            style={{
              maxWidth: "42rem",
              fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
              fontWeight: 300,
              fontSize: "clamp(0.9rem, 1.2vw, 1.05rem)",
            }}
          >
            Novu is being discontinued. Thank you to everyone who was part of the
            journey.
          </p>
        </div>
      </div>

      <style>{`
        @keyframes kenBurns {
          0% { transform: scale(1); }
          100% { transform: scale(1.006); }
        }
        @media (prefers-reduced-motion: reduce) {
          [data-nav-theme="dark"] [style*="kenBurns"] {
            animation: none !important;
            transform: none !important;
          }
        }
      `}</style>
    </section>
  );
}

const serifStyle = {
  fontFamily: "'Lora', Georgia, 'Times New Roman', serif",
  fontStyle: "normal",
  fontWeight: 400,
  letterSpacing: "-0.01em",
};
