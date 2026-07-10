// Section4Section — "fist-bump" section. Yellow (#fff48d) full-width band with a
// big bold centered headline "iDEAL BECOMES WERO" and two colorful 3D fist
// objects entering from the left (purple) and right (orange) edges.
//
// On the live site the fists + headline are a WebGL/Lottie scroll-driven
// animation (the original DOM held base64 <image> layers), so the primary
// screenshot captured only the fists — the headline is reconstructed verbatim
// from the DOM data with the captured type styles. The fists are cropped from
// the reference as <img>; their baked-in #fff48d background blends seamlessly
// with the section background.
export default function Section4Section() {
  return (
    <section
      className="fist-bump-section"
      style={{
        position: "relative",
        width: "100%",
        minHeight: "80dvh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        padding: "clamp(0rem, 6.4724919094vw + -1.5169902913rem, 6.25rem) 30px",
        background: "#fff48d",
      }}
    >
      {/* Left purple fist — enters from the left edge, vertically centered */}
      <img
        src="/assets/images/obj-fist-left.png"
        alt=""
        aria-hidden="true"
        style={{
          position: "absolute",
          left: 0,
          top: "50%",
          transform: "translateY(-50%)",
          width: "clamp(90px, 13.2vw, 190px)",
          height: "auto",
          pointerEvents: "none",
          userSelect: "none",
        }}
      />

      {/* Right orange fist — enters from the right edge, vertically centered */}
      <img
        src="/assets/images/obj-fist-right.png"
        alt=""
        aria-hidden="true"
        style={{
          position: "absolute",
          right: 0,
          top: "50%",
          transform: "translateY(-50%)",
          width: "clamp(88px, 12.85vw, 185px)",
          height: "auto",
          pointerEvents: "none",
          userSelect: "none",
        }}
      />

      <div
        className="fist-bump-section__content"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "80dvh",
        }}
      >
        <h2
          className="fist-bump-section__title"
          style={{
            color: "#1d1c1c",
            fontFamily: '"GT Walsheim Wero", sans-serif',
            fontSize:
              "clamp(2.9375rem, 5.3721682848vw + 1.6783980583rem, 8.125rem)",
            fontStyle: "normal",
            fontWeight: 800,
            letterSpacing: "-2.209px",
            lineHeight: "85%",
            textAlign: "center",
            width:
              "clamp(20.9375rem, 37.8640776699vw + 12.0631067961rem, 57.5rem)",
            margin: 0,
          }}
        >
          <span className="line" style={{ display: "block" }}>
            iDEAL
          </span>
          <span className="line" style={{ display: "block" }}>
            BECOMES
          </span>
          <span className="line" style={{ display: "block" }}>
            WERO
          </span>
        </h2>
      </div>
    </section>
  );
}
