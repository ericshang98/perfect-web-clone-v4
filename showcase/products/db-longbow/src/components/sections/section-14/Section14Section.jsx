import React from "react";

const ASSET = "/assets/images";

// Decorative horizontal line with measure squares (matches .horizontal-line markup)
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
      {[
        { left: "0%" },
        { left: "25%" },
        { left: "50%" },
        { left: "75%" },
        { left: "100%" },
      ].map((s, i) => (
        <div
          key={i}
          style={{
            backgroundColor: "white",
            width: "7px",
            height: "7px",
            position: "absolute",
            top: "-50%",
            left: s.left,
            transform: "translate(-50%, -50%)",
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

// A team member portrait card with brightness filter + blurred name plate
function TeamPortrait({ src, srcSet, sizes, name }) {
  return (
    <div
      style={{
        zIndex: -1,
        pointerEvents: "none",
        width: "100%",
        height: "100%",
        position: "absolute",
        inset: "0%",
        overflow: "hidden",
        filter: "brightness(75%)",
      }}
    >
      <img
        alt=""
        data-role="image"
        loading="lazy"
        sizes={sizes}
        src={src}
        srcSet={srcSet}
        width={400}
        height={400}
        onError={(e) => {
          e.currentTarget.onerror = null;
          e.currentTarget.srcset = "";
        }}
        style={{
          zIndex: -1,
          objectFit: "cover",
          width: "100%",
          maxWidth: "none",
          height: "539px",
          position: "absolute",
          top: "-45px",
          left: 0,
          transform: "translate(0px, -45px)",
        }}
      />
      <div
        style={{
          zIndex: 2,
          WebkitBackdropFilter: "blur(1.75rem)",
          backdropFilter: "blur(1.75rem)",
          textAlign: "center",
          display: "flex",
          flexFlow: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "clamp(3rem, 3.1553rem - .1294vw, 3.125rem)",
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
        }}
      >
        <h2
          style={{
            fontFamily:
              '"Ebgaramond Variablefont Wght 0", Arial, sans-serif',
            letterSpacing: "-.03em",
            margin: 0,
            marginBottom: "-.1em",
            paddingBottom: ".1em",
            color: "white",
            fontSize:
              "clamp(1.75rem, 1.6893rem + .2589vw, 2rem)",
            fontWeight: 400,
            lineHeight: ".85em",
          }}
        >
          {name}
        </h2>
      </div>
    </div>
  );
}

function SignImage({ src }) {
  return (
    <img
      alt=""
      className="content__image"
      loading="lazy"
      src={src}
      onError={(e) => {
        e.currentTarget.onerror = null;
      }}
      style={{ width: "14.375rem" }}
    />
  );
}

export default function Section14Section() {
  const teamImg = (id, file) => ({
    src: `${ASSET}/${file}.jpg`,
  });

  return (
    <section
      style={{
        width: "100%",
        minHeight: "min(150dvh, 95.625rem)",
        display: "flex",
        color: "white",
      }}
    >
      <div
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
          id="team"
          style={{
            zIndex: 1,
            flex: 1,
            width: "100%",
            display: "grid",
            position: "relative",
            columnGap: "0px",
            rowGap: "0px",
            gridTemplateRows: "auto 1fr auto 1fr auto 1fr",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gridAutoRows: "1fr",
            gridAutoColumns: "1fr",
          }}
        >
          {/* Row 1: top line, full width */}
          <div
            style={{
              gridArea: "1 / 1 / 2 / 5",
              pointerEvents: "none",
              width: "100%",
              position: "relative",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Row 2: centered intro text */}
          <div
            style={{
              gridArea: "2 / 1 / 3 / 5",
              placeSelf: "center",
              textAlign: "center",
              maxWidth: "39.25rem",
              width: "628px",
              paddingLeft: "1.625rem",
              paddingRight: "1.625rem",
            }}
          >
            <p
              style={{
                textTransform: "uppercase",
                margin: 0,
                color: "white",
                fontFamily: "Arial, sans-serif",
              }}
            >
              A steadfast commitment to delivering the antidote to autonomy. A
              passion anchored in the immutable truths of physics and first
              principles. The creation of a machine driven by pure spirit and
              timeless dedication.
            </p>
          </div>

          {/* Row 3: middle line */}
          <div
            style={{
              gridArea: "3 / 1 / 4 / 5",
              pointerEvents: "none",
              width: "100%",
              position: "relative",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Team portrait 1 (Mark Tapscott) - content cell row 4 col 1, image spans 1/3/3/5 inside */}
          <div
            style={{
              gridArea: "4 / 1 / 5 / 2",
              width: "355px",
              maxWidth: "100%",
              flex: "0 0 auto",
              height: "100%",
              position: "relative",
            }}
          >
            <TeamPortrait
              src={`${ASSET}/68b7f092c8dc2f9d2136c1a2_longbow-team-image-1.jpg`}
              srcSet={`https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f092c8dc2f9d2136c1a2_longbow-team-image-1-p-500.jpg 500w, ${ASSET}/68b7f092c8dc2f9d2136c1a2_longbow-team-image-1.jpg 1066w`}
              sizes="26vw"
              name="Mark Tapscott"
            />
          </div>

          {/* Row 5: line */}
          <div
            style={{
              gridArea: "5 / 1 / 6 / 5",
              pointerEvents: "none",
              width: "100%",
              position: "relative",
            }}
          >
            <HorizontalLine />
          </div>

          {/* Sign image 1 - centered, row 6 col 2 */}
          <div
            style={{
              gridArea: "6 / 2 / 7 / 3",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              width: "355px",
              maxWidth: "100%",
              flex: "0 0 auto",
              height: "100%",
              position: "relative",
            }}
          >
            <SignImage src={`${ASSET}/68bf8679de370174b73881db_longbow-sign-image-1.png`} />
          </div>

          {/* Team portrait 2 (Jenny Keisu) - content cell row 4 col 4 */}
          <div
            style={{
              gridArea: "4 / 4 / 5 / 5",
              width: "355px",
              maxWidth: "100%",
              flex: "0 0 auto",
              height: "100%",
              position: "relative",
            }}
          >
            <TeamPortrait
              src={`${ASSET}/68b7f09c9c1146aa8f9604f2_longbow-team-image-2.jpg`}
              srcSet={`https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f09c9c1146aa8f9604f2_longbow-team-image-2-p-500.jpg 500w, https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f09c9c1146aa8f9604f2_longbow-team-image-2-p-800.jpg 800w, ${ASSET}/68b7f09c9c1146aa8f9604f2_longbow-team-image-2.jpg 1059w`}
              sizes="26vw"
              name="Jenny Keisu"
            />
          </div>

          {/* Sign image 2 - centered, row 6 col 3 */}
          <div
            style={{
              gridArea: "6 / 3 / 7 / 4",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              width: "355px",
              maxWidth: "100%",
              flex: "0 0 auto",
              height: "100%",
              position: "relative",
            }}
          >
            <SignImage src={`${ASSET}/68bf86795bc1a459757a23d1_longbow-sign-image-2.png`} />
          </div>

          {/* Team portrait 3 (Daniel Davey) - content cell row 4 col 4 (mobile/overlay) */}
          <div
            style={{
              gridArea: "4 / 4 / 5 / 5",
              width: "355px",
              maxWidth: "100%",
              flex: "0 0 auto",
              height: "100%",
              position: "relative",
              display: "none",
            }}
          >
            <TeamPortrait
              src={`${ASSET}/68b7f092332b049af5f9733a_longbow-team-image-3.jpg`}
              srcSet={`https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f092332b049af5f9733a_longbow-team-image-3-p-500.jpg 500w, https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68b7f092332b049af5f9733a_longbow-team-image-3-p-800.jpg 800w, ${ASSET}/68b7f092332b049af5f9733a_longbow-team-image-3.jpg 1062w`}
              sizes="26vw"
              name="Daniel Davey"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
