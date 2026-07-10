// FooterSection — yellow footer for the sowieso / wero page.
// Layout (matches reference crop): two decorative gradient "sparkle" stickers in
// the top corners, then a 3-column card row —
//   LEFT   : green "ALWAYS AVAILABLE WITH OUR PSP PARTNERS" card + bank/hearts art
//   MIDDLE : two stacked white cards (iDEAL, wero) each with a round arrow button
//   RIGHT  : pink/orange "Frequently Asked Questions" CTA card + a green social column
// then the giant edge-to-edge "sowieso." wordmark and the italic disclaimer.
// Colors/geometry sampled from the reference crop + captured css_rules.
const INK = "#1d1c1c";
const YELLOW = "#fff48d";
const FONT = '"GT Walsheim Wero", sans-serif';

// diagonal up-right arrow (↗)
function Arrow({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={INK}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M7 17 L17 7" />
      <path d="M8.5 7 H17 V15.5" />
    </svg>
  );
}

// round arrow button used inside the white iDEAL / wero cards (yellow, 59px)
function PartyArrow() {
  return (
    <span
      style={{
        alignItems: "center",
        backgroundColor: YELLOW,
        border: `1px solid ${INK}`,
        borderRadius: "50%",
        boxShadow: `0 6px ${INK}`,
        display: "flex",
        flex: "none",
        height: "59px",
        width: "59px",
        justifyContent: "center",
      }}
    >
      <Arrow size={30} />
    </span>
  );
}

export default function FooterSection() {
  return (
    <footer
      style={{
        backgroundColor: YELLOW,
        color: INK,
        fontFamily: FONT,
        paddingBottom: "clamp(6.25rem, 6.47vw + 4.73rem, 12.5rem)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* top-corner decorative sparkle stickers (rendered on matching yellow) */}
      <img
        src="/assets/images/footer-blob-left.png"
        alt=""
        aria-hidden="true"
        style={{ position: "absolute", top: 0, left: 0, width: "177px", zIndex: 0, pointerEvents: "none" }}
      />
      <img
        src="/assets/images/footer-blob-right.png"
        alt=""
        aria-hidden="true"
        style={{ position: "absolute", top: 0, right: 0, width: "178px", zIndex: 0, pointerEvents: "none" }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          marginLeft: "auto",
          marginRight: "auto",
          width: "min(1320px, calc(100% - 120px))",
          paddingTop: "535px",
        }}
      >
        {/* card row */}
        <div style={{ display: "flex", flexDirection: "row", gap: "0 20px", alignItems: "stretch" }}>
          {/* LEFT group: partners card + stacked parties */}
          <div style={{ display: "flex", flexDirection: "row", gap: "0 20px", width: "820px", flex: "none" }}>
            {/* green PSP partners card */}
            <div
              style={{
                background: "linear-gradient(180deg,#83f582,#7af7f7)",
                border: `1px solid ${INK}`,
                borderRadius: "5px",
                height: "520px",
                overflow: "hidden",
                padding: "38px 20px 0 27px",
                position: "relative",
                width: "360px",
                flex: "none",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <h2
                style={{
                  color: INK,
                  fontSize: "2.0625rem",
                  fontWeight: 800,
                  letterSpacing: "-1.551px",
                  lineHeight: "100%",
                  textTransform: "uppercase",
                  margin: 0,
                  position: "relative",
                  zIndex: 1,
                }}
              >
                Always available with our PSP partners
              </h2>
              <div
                style={{
                  alignItems: "center",
                  backgroundColor: "#fff",
                  border: `1px solid ${INK}`,
                  borderRadius: "50%",
                  boxShadow: `0 4px ${INK}`,
                  display: "flex",
                  height: "42px",
                  width: "42px",
                  justifyContent: "center",
                  marginLeft: "auto",
                  marginTop: "10px",
                  position: "relative",
                  zIndex: 1,
                }}
              >
                <Arrow />
              </div>
              {/* bank-cards + hearts illustration, anchored bottom-center, overflowing sides */}
              <img
                src="/assets/images/footer-banks.svg"
                alt=""
                aria-hidden="true"
                style={{
                  position: "absolute",
                  bottom: "-25px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  width: "440px",
                  pointerEvents: "none",
                }}
              />
            </div>

            {/* parties column: iDEAL + wero */}
            <div style={{ display: "flex", flexDirection: "column", gap: "20px 0", width: "440px", flex: "none" }}>
              <div
                style={{
                  alignItems: "center",
                  backgroundColor: "#fff",
                  border: `1px solid ${INK}`,
                  borderRadius: "5px",
                  display: "flex",
                  height: "250px",
                  justifyContent: "space-between",
                  padding: "25px 30px",
                }}
              >
                <img src="/assets/images/footer-ideal.svg" alt="iDEAL logo" style={{ height: "70px", width: "auto" }} />
                <PartyArrow />
              </div>
              <div
                style={{
                  alignItems: "center",
                  backgroundColor: "#fff",
                  border: `1px solid ${INK}`,
                  borderRadius: "5px",
                  display: "flex",
                  height: "250px",
                  justifyContent: "space-between",
                  padding: "25px 30px",
                }}
              >
                <img src="/assets/images/footer-wero-logo.svg" alt="Wero logo" style={{ height: "45px", width: "auto" }} />
                <PartyArrow />
              </div>
            </div>
          </div>

          {/* RIGHT group: FAQ CTA + socials */}
          <div style={{ display: "flex", flexDirection: "row", gap: "0 20px", flex: 1 }}>
            {/* pink FAQ CTA card */}
            <div
              style={{
                background: "linear-gradient(221deg,#fd97fd -1.12%,#fdad70 103%)",
                border: `1px solid ${INK}`,
                borderRadius: "5px",
                height: "520px",
                overflow: "hidden",
                padding: "57px 20px 0",
                position: "relative",
                flex: 1,
              }}
            >
              <div style={{ maxWidth: "320px", marginLeft: "auto", marginRight: "auto", position: "relative", zIndex: 1 }}>
                <p
                  style={{
                    color: INK,
                    fontSize: "1.125rem",
                    fontWeight: 500,
                    lineHeight: "130%",
                    marginBottom: "17px",
                    marginTop: 0,
                    textAlign: "center",
                  }}
                >
                  Frequently Asked Questions
                </p>
                <h2
                  style={{
                    color: INK,
                    fontSize: "2.9375rem",
                    fontWeight: 800,
                    letterSpacing: "-1.88px",
                    lineHeight: "100%",
                    textAlign: "center",
                    textTransform: "uppercase",
                    margin: 0,
                  }}
                >
                  Will wero be{" "}
                  <span
                    style={{
                      backgroundColor: "#fd74fd",
                      border: `1px solid ${INK}`,
                      borderRadius: "4px",
                      padding: "0 6px 0 2px",
                      display: "inline-block",
                      lineHeight: "1.05",
                    }}
                  >
                    just as easy
                  </span>{" "}
                  for my customers to use?
                </h2>
              </div>
              {/* clock / sunburst decorative graphic (incl. the round arrow button)
                  anchored to the card bottom */}
              <img
                src="/assets/images/footer-faq-graphic.png"
                alt=""
                aria-hidden="true"
                style={{ position: "absolute", left: 0, right: 0, bottom: 0, width: "100%", pointerEvents: "none" }}
              />
            </div>

            {/* socials column */}
            <div
              style={{
                alignItems: "center",
                background: "linear-gradient(90deg,#83f582,#7af7f7)",
                border: `1px solid ${INK}`,
                borderRadius: "5px",
                display: "flex",
                flexDirection: "column",
                height: "520px",
                justifyContent: "space-evenly",
                width: "99px",
                flex: "none",
              }}
            >
              {[
                <svg key="f" width="20" height="20" viewBox="0 0 24 24" fill={INK} aria-hidden="true">
                  <path d="M15 3h-2.5C10.6 3 9 4.6 9 6.5V9H7v3h2v9h3v-9h2.3l.7-3H12V6.8c0-.5.4-.8.9-.8H15V3z" />
                </svg>,
                <svg key="ig" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={INK} strokeWidth="2" aria-hidden="true">
                  <rect x="3" y="3" width="18" height="18" rx="5" />
                  <circle cx="12" cy="12" r="4" />
                  <circle cx="17.5" cy="6.5" r="1.2" fill={INK} stroke="none" />
                </svg>,
                <svg key="tt" width="22" height="22" viewBox="0 0 24 24" fill={INK} aria-hidden="true">
                  <path d="M16.5 3c.3 2 1.6 3.6 3.5 3.9v2.5c-1.3 0-2.5-.4-3.5-1v5.9c0 3-2.4 5.2-5.2 5.2S6 22.3 6 19.3 8.4 14 11.3 14c.3 0 .6 0 .9.1v2.6c-.3-.1-.6-.2-.9-.2-1.4 0-2.6 1.2-2.6 2.7s1.2 2.7 2.6 2.7 2.6-1.2 2.6-2.7V3h2.6z" />
                </svg>,
              ].map((icon, i) => (
                <span
                  key={i}
                  style={{
                    alignItems: "center",
                    backgroundColor: "#fff",
                    border: `1px solid ${INK}`,
                    borderRadius: "50%",
                    boxShadow: `0 6px ${INK}`,
                    display: "flex",
                    height: "67px",
                    width: "67px",
                    justifyContent: "center",
                    flex: "none",
                  }}
                >
                  {icon}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* giant edge-to-edge wordmark */}
        <svg
          viewBox="0 0 1320 210"
          width="100%"
          style={{ display: "block", height: "auto", marginTop: "20px" }}
          aria-label="sowieso."
          role="img"
        >
          <text
            x="0"
            y="170"
            textLength="1320"
            lengthAdjust="spacing"
            fontFamily={FONT}
            fontWeight="800"
            fontSize="240"
            letterSpacing="-6"
            fill={INK}
          >
            sowieso.
          </text>
        </svg>

        {/* disclaimer */}
        <p style={{ fontStyle: "italic", margin: "35px 20% 0", textAlign: "center" }}>
          © 2026 EPI Company SE |{" "}
          <a href="#" style={{ color: INK, textDecoration: "underline" }}>
            Website Terms of Use
          </a>
        </p>
      </div>
    </footer>
  );
}
