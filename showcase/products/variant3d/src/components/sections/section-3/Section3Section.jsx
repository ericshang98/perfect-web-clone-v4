export default function Section3Section() {
  return (
    <section
      className="loop-section section-dark"
      style={{
        display: "flex",
        flexFlow: "column",
        justifyContent: "center",
        alignItems: "flex-start",
        backgroundColor: "black",
        paddingTop: "var(--loop-pt, 60px)",
        paddingRight: "var(--page-padding, 32px)",
        paddingLeft: "var(--page-padding, 32px)",
        gap: "var(--loop-gap, 40px)",
      }}
    >
      <style>{`
        .loop-section {
          --page-padding: 32px;
          --loop-pt: 60px;
          --loop-gap: 40px;
          --font-body-lg: 52px;
        }
        .loop-section .loop-text {
          font-size: var(--font-body-lg);
          line-height: 105%;
          font-weight: 300;
          margin-bottom: 0;
          max-width: 699px;
          width: 454px;
        }
        .loop-section .loop-button {
          display: flex;
          height: 60px;
          padding: 0 24px;
          align-items: center;
          justify-content: center;
          gap: 12px;
          border-radius: 12px;
          border: 1px solid #e5e3e033;
          background-color: #94939059;
          -webkit-backdrop-filter: blur(6px);
          backdrop-filter: blur(6px);
          color: #f5f3f0;
          font-size: 18px;
          font-weight: 500;
          line-height: 58px;
          letter-spacing: .003em;
          text-transform: uppercase;
          white-space: nowrap;
          text-decoration: none;
          cursor: pointer;
          flex: 0 auto;
          transition: color .2s, background-color .2s;
        }
        .loop-section .loop-button:hover {
          background-color: #f75f2d;
          color: #f5f3f0;
        }
        @media screen and (min-width: 1440px) {
          .loop-section {
            --page-padding: 40px;
            --loop-pt: 80px;
            --loop-gap: 60px;
            --font-body-lg: 52px;
          }
        }
        @media screen and (max-width: 991px) {
          .loop-section {
            --page-padding: 24px;
            --font-body-lg: 42px;
          }
          .loop-section .loop-text {
            max-width: none;
            width: auto;
          }
        }
        @media screen and (max-width: 767px) {
          .loop-section {
            --page-padding: 16px;
            --font-body-lg: 30px;
          }
          .loop-section .loop-button {
            width: 100%;
            height: 48px;
            padding-bottom: 1px;
            line-height: 46px;
            font-size: 16px;
          }
        }
      `}</style>

      <p className="loop-text" style={{ color: "#f5f3f0" }}>
        Design it, see it, feel it.{" "}
        <br />
        Be in the loop.
      </p>

      <a className="loop-button" href="/loop">
        Check out LOOP™
      </a>
    </section>
  );
}
