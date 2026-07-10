export default function Section() {
  const font = "'GT Walsheim Wero', sans-serif";

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        backgroundColor: "#fff48d",
        color: "#1d1c1c",
        fontFamily: font,
        padding: "144px 120px 290px",
      }}
    >
      {/* 3D puzzle-checkmark object (WebGL in original) cropped onto matching yellow bg */}
      <img
        src="/assets/images/obj-checkmark.png"
        alt="Interlocking puzzle checkmark"
        style={{
          position: "absolute",
          top: "50px",
          left: "850px",
          width: "555px",
          height: "auto",
          pointerEvents: "none",
          userSelect: "none",
        }}
      />

      <div style={{ maxWidth: "680px", position: "relative" }}>
        {/* label */}
        <div
          className="flex items-center"
          style={{
            gap: "0 20px",
            fontSize: "1.25rem",
            fontWeight: 500,
            lineHeight: "135%",
            marginBottom: "35px",
          }}
        >
          <span
            className="flex items-center justify-center shrink-0"
            style={{
              width: "40px",
              height: "40px",
              backgroundColor: "#fff",
              border: "1px solid #1d1c1c",
              borderRadius: "50%",
              boxShadow: "0 4px #1d1c1c",
            }}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#1d1c1c"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="4" y1="12" x2="20" y2="12" />
              <polyline points="13 5 20 12 13 19" />
            </svg>
          </span>
          <span>Ambition without borders. Sowieso.</span>
        </div>

        {/* headline */}
        <h2
          style={{
            fontSize: "50px",
            fontWeight: 800,
            lineHeight: "85%",
            letterSpacing: "-1.41px",
            marginBottom: "45px",
            textTransform: "none",
          }}
        >
          iDEAL IS BECOMING
          <br />
          WERO:
          <br />
          THE NEW EUROPEAN
          <br />
          PAYMENT SYSTEM
        </h2>

        {/* body copy */}
        <div style={{ fontSize: "18.75px", fontWeight: 500, lineHeight: "135%" }}>
          <p style={{ marginBottom: "25px" }}>
            We're going international, baby! With a new platform and the backing of
            all the banks, we're ready for the future as a payment system.
          </p>
          <p style={{ marginBottom: 0 }}>
            Wero offers the same safety and ease of use as iDEAL, but it is
            available across Europe. Plus it offers new payment options and
            services like purchase protection. Sounds good, right? Especially since
            we're making the transition smooth. So you can focus on running your
            business.
          </p>
        </div>
      </div>
    </section>
  );
}
