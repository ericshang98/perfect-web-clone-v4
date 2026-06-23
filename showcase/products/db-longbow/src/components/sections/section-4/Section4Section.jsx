import React from "react";

const IMG = "/assets/images/68b43c4a00503ee3a44a52df_longbow-new-image-2.jpg";
const IMG_REMOTE =
  "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b43c4a00503ee3a44a52df_longbow-new-image-2.jpg";

function HorizontalLine() {
  return (
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
      {[0, 25, 50, 75, 100].map((pct) => (
        <div
          key={pct}
          style={{
            backgroundColor: "white",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: `${pct}%`,
            transform: "translate(-50%, -50%)",
            display: "block",
          }}
        />
      ))}
      <div
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
  );
}

function Card({ number, headingLine1, headingItalic, text, gridArea, noMobile }) {
  return (
    <div
      className={noMobile ? "card card--no-mobile" : "card"}
      style={{
        zIndex: 2,
        gridArea,
        rowGap: "2rem",
        columnGap: "2rem",
        backgroundColor: "#ffffff0d",
        WebkitBackdropFilter: "blur(1.75rem)",
        backdropFilter: "blur(1.75rem)",
        color: "white",
        willChange: "transform",
        flexFlow: "column",
        justifyContent: "space-between",
        alignItems: "flex-start",
        paddingBlock: "clamp(1.25rem, 2.23vw - .179rem, 2.5rem)",
        paddingInline: "clamp(1rem, 2.68vw - .714rem, 2.5rem)",
        textDecoration: "none",
        display: "flex",
        position: "relative",
        maxWidth: "100%",
      }}
    >
      <div
        className="card__header"
        style={{
          rowGap: "2rem",
          columnGap: "2rem",
          flexFlow: "column",
          justifyContent: "flex-start",
          alignItems: "flex-start",
          display: "flex",
        }}
      >
        <div style={{ width: "auto" }}>
          <div
            style={{
              backgroundColor: "#ffffff1a",
              textTransform: "uppercase",
              borderRadius: ".75rem",
              width: "100%",
              padding: ".625rem",
              fontSize: "clamp(.688rem, .33rem + .56vw, 1rem)",
              lineHeight: ".8em",
              overflow: "hidden",
              fontFamily: "'Geist Mono V4', monospace",
            }}
          >
            <div style={{ marginLeft: "-.2em" }}>{number}</div>
          </div>
        </div>
        <h2
          style={{
            fontFamily:
              '"Ebgaramond Variablefont Wght 0", Arial, sans-serif',
            letterSpacing: "-.03em",
            marginTop: 0,
            marginBottom: "-.1em",
            paddingBottom: ".1em",
            fontSize: "clamp(1.5rem, .357rem + 1.79vw, 2.5rem)",
            fontWeight: 400,
            lineHeight: ".85em",
          }}
        >
          {headingLine1}
          <br />
          <span
            style={{
              fontFamily:
                '"Ebgaramond Variablefont Wght 0", Arial, sans-serif',
              fontStyle: "italic",
              lineHeight: ".8em",
            }}
          >
            {headingItalic}
          </span>
        </h2>
      </div>
      <p
        style={{
          textTransform: "uppercase",
          marginBottom: 0,
          marginTop: 0,
          maxWidth: "100%",
          fontFamily: "'Geist Mono V4', monospace",
          fontSize: "14px",
          lineHeight: "20px",
        }}
      >
        {text}
      </p>
    </div>
  );
}

export default function Section4Section() {
  return (
    <section
      className="section"
      id="creating"
      style={{
        width: "100%",
        minHeight: "min(100vh - 1.25rem, 100vh - 1.25rem)",
        display: "flex",
        backgroundColor: "#000",
      }}
    >
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
            columnGap: "0px",
            rowGap: "0px",
            flex: 1,
            gridTemplateRows: "auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
            width: "100%",
            display: "grid",
            position: "relative",
          }}
        >
          {/* top line: row 1 / cols 1-5 */}
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

          {/* content with parallax image: rows 2-5 / cols 1-3 */}
          <div
            className="content"
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              maxWidth: "100%",
              gridArea: "2 / 1 / 5 / 3",
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
                width="600"
                height="600"
                loading="eager"
                src={IMG}
                onError={(e) => {
                  if (e.currentTarget.src !== IMG_REMOTE)
                    e.currentTarget.src = IMG_REMOTE;
                }}
                style={{
                  zIndex: -1,
                  objectFit: "cover",
                  objectPosition: "20% 50%",
                  width: "100%",
                  maxWidth: "none",
                  height: "100%",
                  transformStyle: "preserve-3d",
                  position: "absolute",
                  top: 0,
                  left: 0,
                  transform: "translateZ(0)",
                }}
              />
            </div>
          </div>

          {/* middle line: row 3 / cols 1-5 */}
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

          {/* card .02: row 2 / col 4 */}
          <Card
            number=".02"
            headingLine1="Creating a New"
            headingItalic="Class: FEV"
            text="Our Speedster weighs just 895 kg, making it almost half the weight of many modern electric sports cars. This approach not only dramatically improves dynamics but also allows for more compact and energy-efficient batteries."
            gridArea="2 / 4 / 3 / 5"
          />

          {/* card .03: row 4 / col 3 */}
          <Card
            number=".03"
            headingLine1="The Soul of a Classic,"
            headingItalic="the Heart of the Future"
            text='Longbow is the spiritual successor to legends like the Lotus Elise and Jaguar E-Type, inspired by their "less is more" principle. We combine this rich heritage with advanced electric technology to create a 21st-century sports car, hand-built in the heart of Great Britain.'
            gridArea="4 / 3 / 5 / 4"
            noMobile
          />
        </div>
      </div>
    </section>
  );
}
