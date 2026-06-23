import { useRef, useState, useEffect, useCallback } from "react";

// Brand tokens captured from css_rules :root
const BLUE = "#1940a7";
const BG_GRAY = "#f5f3f0";
const BRAND = "#f75f2d";
const GLASS = "#94939059";
const GLASS_BORDER = "#e5e3e033";

// Press cards — real hrefs + local images from section-5.json
const CARDS = [
  {
    source: "fast company",
    href: "https://www.fastcompany.com/91076450/north-america-world-changing-ideas-2024",
    title: "12 projects that show how north american companies are creating positive change",
    logo: "/assets/images/690016a5640a1791a22ab0fb_Fast_20Company_200x200.png",
    image: "/assets/images/68a895ee9e04b7366ce256a2_7e097bef157034c7b98db5827e2ca7af4336c147.png",
  },
  {
    source: "sourcing journal",
    href: "https://sourcingjournal.com/footwear/footwear-innovations/materials-show-3d-knitting-footwear-production-technology-variant-3d-491699/",
    title: "Materials Show: 3D Knitting Could Revolutionize Footwear Production, Experts Say",
    logo: "/assets/images/690016b00357399d47324f5c_Sourcing_20Journal_200x200.png",
    image: "/assets/images/68a8961c0965798ef5080165_78efdfa2f5057d9d040f0ea1b8748fd883fc8d67.png",
  },
  {
    source: "NBC news",
    href: "https://www.nbcnews.com/now/video/fashion-tech-company-using-3d-printing-to-create-sustainable-clothing-193598021679",
    title: "Apparel tech company using 3D printing to create sustainable clothing",
    logo: "/assets/images/690015d9af1a6d916472baf1_NBC_200x200.png",
    image: "/assets/images/690018139215e3dd94b5442f_Screenshot_202025-10-27_20at_206.10.34_20PM.png",
  },
  {
    source: "Knitting Industry",
    href: "https://www.knittingindustry.com/variant3d-loop-named-finalist-in-2024-world-changing-ideas/?inf_contact_key=4df1c47d1c7ff923b97d6cc31881254309c74070ac2bf3cfa7869e3cfd4ff832",
    title: "Variant3D Loop named finalist in 2024 World Changing Ideas",
    logo: "/assets/images/69012105360099528ebc32dc_knitting_20industry_20logo_200x200.png",
    image: "/assets/images/690120dc8d7b9e3ea54c26eb_Screenshot_202025-10-28_20at_201.00.23_20PM.png",
  },
  {
    source: "The Interline",
    href: "https://www.theinterline.com/2023/11/28/digital-transformation-the-solution-to-sustainable-fashion/",
    title: "Digital Transformation – The Solution To Sustainable Fashion",
    logo: "/assets/images/69012127a4c08075a64ef34f_Interline_20logo_200x200.png",
    image: "/assets/images/690121569f0700f9101eccec_Screenshot_202025-10-28_20at_201.02.22_20PM.png",
  },
  {
    source: "Textile World",
    href: "https://www.textileworld.com/textile-world/features/2024/03/game-changing-benefits-of-3d-digital-sampling/",
    title: "Game-Changing Benefits Of 3D Digital Sampling",
    logo: "/assets/images/690121c1f755deeda681c494_TextileWorld_20logo_200x200.png",
    image: "/assets/images/690121b9bbaf290ba2b54978_Variant3Dlab-696x402.jpg",
  },
  {
    source: "Innovation in Textiles",
    href: "https://www.innovationintextiles.com/focus-on-ai-and-ar-technologies-at-heimtextil-2024/",
    title: "Focus on AI and AR technologies at Heimtextil 2024",
    logo: "/assets/images/690121cfc4c3655b900b69a7_innovation_20in_20textiles_logo_200x200.png",
    // local_url null -> remote + onError hide
    image: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/690121f3f755deeda681d245_dreamstime_m_96184113-489x408-boxed.jpg",
  },
  {
    source: "vogue business",
    href: "https://www.voguebusiness.com/story/sustainability/evrnu-is-launching-a-fashion-brand",
    title: "Why a textile recycling startup is launching an Apparel brand",
    // local_url null -> remote + onError hide
    logo: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/69001662043f2a5277374490_Vogue%20Business_200x200.png",
    image: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/690017ae56c7aee33090fb83_Screenshot%202025-10-27%20at%206.07.39%20PM.png",
  },
];

function ArrowIcon() {
  return (
    <svg fill="none" height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style={{ maxWidth: "100%", maxHeight: "100%", width: 24, height: 24, flex: "0 0 auto" }}>
      <path clipRule="evenodd" fillRule="evenodd" fill={BLUE} stroke={BLUE} d="M17.0644 5.95016C16.6647 5.92971 16.1616 5.92872 15.4982 5.92872H6.50008V3.92872L15.564 3.92871C16.4505 3.92866 17.2143 3.92862 17.826 4.01086C18.4815 4.09899 19.1098 4.29774 19.6195 4.8074C20.1292 5.31707 20.3279 5.94542 20.416 6.60094C20.4983 7.2126 20.4982 7.97642 20.4982 8.86292L20.4981 18.4287L18.4981 18.4287L18.4982 8.92873C18.4982 8.26731 18.4972 7.76519 18.4769 7.36607L5.20718 20.6358L3.79297 19.2216L17.0644 5.95016Z" />
    </svg>
  );
}

function NavArrow({ direction, disabled }) {
  const d =
    direction === "prev"
      ? "M6.40834 9.68674L11.7727 4.35898L10.6261 3.09009L5.22052 8.45872C4.65628 9.01905 4.17177 9.5002 3.83608 9.93885C3.47714 10.4079 3.20312 10.9345 3.20312 11.5901C3.20312 12.2457 3.47714 12.7723 3.83608 13.2413C4.17176 13.68 4.65627 14.1611 5.2205 14.7214L10.6261 20.0901L11.7727 18.8212L6.40834 13.4934C5.97341 13.0615 5.64672 12.7357 5.40226 12.464L21.2031 12.464L21.2031 10.7161L5.40226 10.7161C5.64672 10.4445 5.97341 10.1187 6.40834 9.68674Z"
      : "M17.5917 9.68699L12.2273 4.35923L13.3739 3.09033L18.7795 8.45897C19.3437 9.01929 19.8282 9.50044 20.1639 9.9391C20.5229 10.4081 20.7969 10.9347 20.7969 11.5903C20.7969 12.246 20.5229 12.7725 20.1639 13.2416C19.8282 13.6802 19.3437 14.1614 18.7795 14.7217L13.3739 20.0903L12.2273 18.8214L17.5917 13.4937C18.0266 13.0617 18.3533 12.7359 18.5977 12.4643L2.79688 12.4643V10.7164L18.5977 10.7164C18.3533 10.4447 18.0266 10.1189 17.5917 9.68699Z";
  const color = disabled ? "#ffffff19" : "var(--_colors---font-light, #ffffff)";
  return (
    <svg fill="none" height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style={{ width: 24, height: 24, flex: "0 0 auto" }}>
      <path clipRule="evenodd" fillRule="evenodd" d={d} fill={color} stroke={color} style={{ transition: "stroke ease 0.2s, fill ease 0.2s" }} />
    </svg>
  );
}

function NewsCard({ card }) {
  return (
    <article
      className="news-card"
      style={{
        borderRadius: "var(--_spacing---radius-md, 12px)",
        backgroundColor: "white",
        cursor: "pointer",
        flexFlow: "column",
        justifyContent: "space-between",
        alignItems: "flex-start",
        width: "100%",
        padding: "32px",
        display: "flex",
      }}
    >
      <div
        className="news-header"
        style={{ justifyContent: "space-between", alignItems: "center", width: "100%", marginBottom: "var(--news-header-mb, 40px)", display: "flex" }}
      >
        <p
          className="news-source"
          style={{ color: BLUE, fontSize: "var(--_font-sizes---font-button, 18px)", textTransform: "uppercase", margin: 0, fontWeight: 500, lineHeight: "100%" }}
        >
          {card.source}
        </p>
        <div className="news-arrow" style={{ width: 24, height: 24, marginLeft: "auto" }}>
          <ArrowIcon />
        </div>
      </div>

      <a
        className="news-link"
        href={card.href}
        target="_blank"
        rel="noopener noreferrer"
        style={{ textDecoration: "none", width: "90%", maxWidth: "100%" }}
      >
        <h3
          className="news-title"
          style={{
            color: BLUE,
            fontSize: "var(--news-title-fs, 52px)",
            textTransform: "uppercase",
            marginTop: 0,
            marginBottom: "var(--news-title-mb, 25%)",
            fontWeight: 300,
            lineHeight: "80%",
          }}
        >
          {card.title}
        </h3>
      </a>

      <div
        className="news-gallery"
        style={{ columnGap: 8, rowGap: 8, marginTop: "auto", display: "flex", flex: "0 0 auto" }}
      >
        <img
          alt=""
          className="news-logo"
          loading="lazy"
          src={card.logo}
          onError={(e) => (e.currentTarget.style.display = "none")}
          style={{
            borderRadius: "var(--_spacing---radius-md, 12px)",
            backgroundColor: BG_GRAY,
            objectFit: "contain",
            width: "var(--news-logo-w, 120px)",
            height: "var(--news-logo-w, 120px)",
            padding: 12,
          }}
        />
        <img
          alt=""
          className="news-image"
          loading="lazy"
          src={card.image}
          onError={(e) => (e.currentTarget.style.display = "none")}
          style={{
            borderRadius: "var(--_spacing---radius-md, 12px)",
            objectFit: "cover",
            width: "var(--news-image-w, 180px)",
            height: "var(--news-logo-w, 120px)",
          }}
        />
      </div>
    </article>
  );
}

export default function Section5Section() {
  const scrollerRef = useRef(null);
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(false);

  const updateNav = useCallback(() => {
    const el = scrollerRef.current;
    if (!el) return;
    setAtStart(el.scrollLeft <= 4);
    setAtEnd(el.scrollLeft + el.clientWidth >= el.scrollWidth - 4);
  }, []);

  useEffect(() => {
    updateNav();
    const el = scrollerRef.current;
    if (!el) return;
    el.addEventListener("scroll", updateNav, { passive: true });
    window.addEventListener("resize", updateNav);
    return () => {
      el.removeEventListener("scroll", updateNav);
      window.removeEventListener("resize", updateNav);
    };
  }, [updateNav]);

  const slideBy = (dir) => {
    const el = scrollerRef.current;
    if (!el) return;
    const card = el.querySelector(".news-slide");
    const amount = card ? card.getBoundingClientRect().width : el.clientWidth * 0.6;
    el.scrollBy({ left: dir * amount, behavior: "smooth" });
  };

  return (
    <section
      className="default-section section-light press-section"
      id="press"
      style={{
        fontFamily: "'Founders Grotesk', Arial, sans-serif",
        backgroundColor: BG_GRAY,
        flexFlow: "column",
        padding: "0 0 40px",
        display: "flex",
        position: "relative",
        overflow: "hidden",
        minHeight: "var(--app-height, 100vh)",
      }}
    >
      <style>{`
        #press { --news-title-fs: 52px; --news-title-mb: 20%; --news-header-mb: 32px; --news-logo-w: 120px; --news-image-w: 180px; }
        #press .news-scroller { scrollbar-width: none; -ms-overflow-style: none; }
        #press .news-scroller::-webkit-scrollbar { display: none; }
        #press .glass-btn { transition: background-color .2s cubic-bezier(.25,.46,.45,.94), border-color .2s cubic-bezier(.25,.46,.45,.94); }
        #press .glass-btn:not([data-disabled="true"]):hover { border-color: ${BRAND} !important; background-color: ${BRAND} !important; }
        #press .news-card { transition: box-shadow .25s ease; }
        @media (min-width: 1440px) { #press { --news-title-mb: 25%; --news-header-mb: 40px; } }
        @media (min-width: 1920px) { #press { --news-title-fs: 72px; --news-title-mb: 30%; --news-logo-w: 160px; --news-image-w: 240px; } }
        @media (max-width: 991px) {
          #press .press-container { flex-flow: column !important; gap: 40px !important; padding-top: 40px !important; }
          #press .press-left-container { padding-top: 0 !important; padding-left: 4.8% !important; }
          #press .press-navigation-container { display: none !important; }
          #press .news-swiper { width: 100% !important; }
          #press .news-slide { min-width: 90vw !important; padding-right: 0 !important; }
          #press .press-background { display: block; }
        }
        @media (max-width: 767px) {
          #press { --news-title-fs: 30px; --news-logo-w: 86px; --news-image-w: 130px; --news-header-mb: 20px; }
          #press .news-card { padding: 20px !important; }
          #press .press-left-container { padding-left: 28px !important; }
          #press .press-background { display: none !important; }
        }
      `}</style>

      {/* Blue background SVG (desktop) */}
      <div
        className="press-background"
        style={{ zIndex: 0, height: "100%", padding: "var(--_spacing---page-padding, 40px)", position: "absolute", top: 0, bottom: "0%", left: "0%", width: "100%", maxWidth: "100%" }}
      >
        <svg preserveAspectRatio="xMidYMid meet" style={{ height: "100%" }} viewBox="0 0 1429 752" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 487.139V719.619C0 737.233 14.2507 751.5 31.8451 751.5H236.513L372.014 480.173C374.641 474.897 380.023 471.581 385.914 471.581H399.608C408.19 471.581 415.148 478.547 415.148 487.139V751.5H667.155C684.749 751.5 699 737.233 699 719.619V378.28H585.163C533.685 378.28 491.968 336.499 491.968 284.979V157.564C491.968 70.8145 421.734 0.5 335.083 0.5H0V487.139Z" fill={BLUE} />
          <path d="M1094.4 749.863C1008.42 749.863 938.735 680.116 938.735 594.065L938.735 466.867C938.735 414.883 896.632 372.724 844.675 372.724L732 372.724L732 32.9638C732 15.9308 745.784 2.13666 762.8 2.13666L1013.45 2.13668L1013.45 265.05C1013.45 274.179 1020.84 281.581 1029.96 281.581L1043.64 281.581C1049.7 281.581 1055.26 278.275 1058.14 272.97L1058.41 272.45L1193.44 2.1367L1397.2 2.13672C1414.22 2.13672 1428 15.9308 1428 32.9639L1428 749.863L1094.4 749.863Z" fill={BLUE} stroke={BLUE} strokeWidth="2" />
        </svg>
      </div>

      {/* Blue background SVG (mobile) */}
      <div
        className="press-background-mobile"
        style={{ zIndex: 0, height: "100%", padding: "120px var(--_spacing---page-padding, 16px) 40px", display: "none", position: "absolute", top: 0, bottom: "0%", left: "0%" }}
      >
        <svg fill="none" height="371" style={{ width: "100%", height: "auto" }} viewBox="0 0 345 371" width="345" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 240.123V354.836C0 363.527 7.0336 370.567 15.7175 370.567H116.734L183.612 236.686C184.909 234.082 187.565 232.446 190.473 232.446H197.231C201.467 232.446 204.901 235.883 204.901 240.123V370.567H329.282C337.966 370.567 345 363.527 345 354.836V186.408H288.814C263.407 186.408 242.817 165.792 242.817 140.371V77.5003C242.817 34.6954 208.152 0 165.384 0H0V240.123Z" fill={BLUE} />
        </svg>
      </div>

      {/* Foreground content */}
      <div
        className="press-container"
        style={{
          zIndex: 10,
          justifyContent: "space-between",
          alignItems: "flex-start",
          width: "100%",
          marginTop: "auto",
          marginBottom: "auto",
          paddingTop: 120,
          display: "flex",
          position: "relative",
        }}
      >
        <div className="press-left-container" style={{ width: "100%", paddingLeft: 135 }}>
          <h2
            className="press-title"
            style={{ fontSize: "var(--news-title-fs, 52px)", textTransform: "uppercase", margin: 0, fontWeight: 300, lineHeight: "80%" }}
          >
            In the<br />Press
          </h2>
          <div className="press-navigation-container" style={{ columnGap: 8, rowGap: 8, marginTop: 46, display: "flex" }}>
            <div
              role="button"
              aria-label="Previous slide"
              aria-disabled={atStart}
              data-disabled={atStart}
              onClick={() => !atStart && slideBy(-1)}
              className="glass-bg press-prev glass-btn"
              style={{
                border: `1.2px solid ${GLASS_BORDER}`,
                backgroundColor: GLASS,
                backdropFilter: "blur(8px)",
                WebkitBackdropFilter: "blur(8px)",
                cursor: atStart ? "default" : "pointer",
                borderRadius: "50%",
                justifyContent: "center",
                alignItems: "center",
                width: 80,
                height: 80,
                display: "flex",
                pointerEvents: atStart ? "none" : "auto",
              }}
            >
              <div className="press-navigation-icon" style={{ width: 24, height: 24 }}>
                <NavArrow direction="prev" disabled={atStart} />
              </div>
            </div>
            <div
              role="button"
              aria-label="Next slide"
              aria-disabled={atEnd}
              data-disabled={atEnd}
              onClick={() => !atEnd && slideBy(1)}
              className="glass-bg press-next glass-btn"
              style={{
                border: `1.2px solid ${GLASS_BORDER}`,
                backgroundColor: GLASS,
                backdropFilter: "blur(8px)",
                WebkitBackdropFilter: "blur(8px)",
                cursor: atEnd ? "default" : "pointer",
                borderRadius: "50%",
                justifyContent: "center",
                alignItems: "center",
                width: 80,
                height: 80,
                display: "flex",
                pointerEvents: atEnd ? "none" : "auto",
              }}
            >
              <div className="press-navigation-icon" style={{ width: 24, height: 24 }}>
                <NavArrow direction="next" disabled={atEnd} />
              </div>
            </div>
          </div>
        </div>

        {/* Carousel */}
        <div className="news-swiper" style={{ width: "57%", maxWidth: "100%" }}>
          <div
            ref={scrollerRef}
            className="news-scroller"
            style={{ display: "flex", overflowX: "auto", scrollSnapType: "x mandatory", cursor: "grab" }}
          >
            {CARDS.map((card, i) => (
              <div
                key={i}
                className="news-slide"
                style={{ minWidth: "49vw", height: "auto", paddingRight: 24, display: "flex", flexShrink: 0, scrollSnapAlign: "start" }}
              >
                <NewsCard card={card} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
