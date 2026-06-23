export default function FeaturesSection() {
  const benefits = [
    {
      value: "80%",
      line1: "Time",
      line2: "Savings",
      num: "(01)",
      description: "Turn 12-month development cycles into 3-week prototypes",
    },
    {
      value: "60%",
      line1: "Cost",
      line2: "Savings",
      num: "(02)",
      description: "Reduce material costs using interactive digital twins for virtual sampling",
    },
    {
      value: "70%",
      line1: "More",
      line2: "Iterations",
      num: "(03)",
      description:
        "Remove workflow constraints through automation enabling teams to explore and refine ideas",
    },
    {
      value: "100%",
      line1: "Design",
      line2: "Integrity",
      num: "(04)",
      description: "Preserve every detail at each stage with machine-ready files",
    },
  ];

  return (
    <section
      className="benefits-section"
      style={{
        // --_font-sizes--- variables (default / <1440px breakpoint)
        "--font-lg": "100px",
        "--font-body-md": "48px",
        "--font-body-lg": "48px",
        "--font-body": "22px",
        "--page-padding": "32px",
        "--brand": "#f75f2d",
        "--gray-700": "#474746",
        "--bg-dark": "black",
        backgroundColor: "var(--bg-dark)",
        display: "flex",
        flexFlow: "column",
        justifyContent: "center",
        alignItems: "flex-start",
        rowGap: "60px",
        columnGap: "60px",
        padding: "120px var(--page-padding) 60px",
      }}
    >
      {/* Intro paragraph */}
      <p
        className="features-body-large"
        style={{
          maxWidth: "699px",
          width: "699px",
          margin: 0,
          fontWeight: 300,
          fontSize: "var(--font-body-md)",
          lineHeight: "105%",
          color: "#fff",
        }}
      >
        We are establishing a new method of making— faster, smarter, better.
      </p>

      {/* Benefits list */}
      <ul
        role="list"
        style={{
          display: "flex",
          flexFlow: "column",
          width: "100%",
          margin: 0,
          padding: 0,
          listStyleType: "none",
        }}
      >
        {benefits.map((b, i) => (
          <li
            key={i}
            className="benefits-list-item group"
            style={{
              borderTop: "1px solid var(--gray-700)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              paddingTop: "32px",
            }}
          >
            <div
              className="benefit-value"
              style={{
                color: "var(--gray-700)",
                fontSize: "var(--font-lg)",
                fontWeight: 300,
                lineHeight: "75%",
              }}
            >
              {b.value}
            </div>

            <div
              className="benefit-text"
              style={{
                display: "flex",
                flexFlow: "column",
                width: "493px",
                minWidth: "493px",
              }}
            >
              <div
                className="benefit-name"
                style={{
                  color: "var(--gray-700)",
                  fontSize: "var(--font-body-lg)",
                  textTransform: "uppercase",
                  fontWeight: 300,
                  lineHeight: "80%",
                }}
              >
                <p style={{ margin: 0 }}>{b.line1}</p>
                <p style={{ margin: 0 }}>
                  {b.line2}{" "}
                  <sup
                    style={{
                      color: "var(--brand)",
                      fontSize: "60%",
                      lineHeight: 0,
                      verticalAlign: "baseline",
                      position: "relative",
                      top: "-.5em",
                    }}
                  >
                    {b.num}
                  </sup>
                </p>
              </div>

              {/* Hover-revealed description (Webflow interaction) */}
              <div
                className="benefit-container"
                style={{ display: "flex", overflow: "hidden" }}
              >
                <div
                  className="benefit-description"
                  style={{
                    width: "92%",
                    fontSize: "var(--font-body)",
                    marginTop: "auto",
                    paddingTop: "20px",
                    paddingBottom: "32px",
                    fontWeight: 300,
                    lineHeight: "110%",
                    color: "#fff",
                    opacity: 0,
                    maxHeight: 0,
                    transition: "opacity .4s ease, max-height .4s ease",
                  }}
                >
                  {b.description}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <style>{`
        /* Hover reveal of benefit description (Webflow data-w-id interaction) */
        .benefits-list-item:hover .benefit-description {
          opacity: 1 !important;
          max-height: 200px !important;
        }
        .benefits-list-item:hover .benefit-value,
        .benefits-list-item:hover .benefit-name {
          color: #fff !important;
          transition: color .4s ease;
        }
        .benefit-value,
        .benefit-name { transition: color .4s ease; }

        /* >=1440px */
        @media screen and (min-width: 1440px) {
          .benefits-section {
            --font-lg: 120px;
            --font-body-md: 52px;
            --font-body-lg: 52px;
            --font-body: 24px;
            --page-padding: 40px;
            row-gap: 80px !important;
            column-gap: 80px !important;
            padding-top: 80px !important;
            padding-bottom: 80px !important;
          }
        }
        /* >=1920px */
        @media screen and (min-width: 1920px) {
          .benefits-section { --font-lg: 180px; }
        }
        /* <=991px */
        @media screen and (max-width: 991px) {
          .benefits-section {
            --font-lg: 80px;
            --font-body-md: 42px;
            --font-body-lg: 42px;
            --font-body: 22px;
            --page-padding: 24px;
          }
          .features-body-large { max-width: 100% !important; width: auto !important; }
          .benefits-list-item {
            flex-flow: column !important;
            row-gap: 80px;
            column-gap: 80px;
          }
          .benefit-text { width: 100% !important; min-width: 100% !important; }
        }
        /* <=767px */
        @media screen and (max-width: 767px) {
          .benefits-section {
            --font-lg: 52px;
            --font-body-md: 20px;
            --font-body-lg: 30px;
            --font-body: 20px;
            --page-padding: 16px;
          }
          .features-body-large { font-size: var(--font-body-lg) !important; }
        }
      `}</style>
    </section>
  );
}
