import React from "react";

const navLinks = [
  { href: "/", label: "Main", current: true },
  { href: "/roadster", label: "Roadster" },
  { href: "/speedster", label: "Speedster" },
  { href: "/#gallery", label: "Gallery" },
  { href: "/#team", label: "Team" },
];

const FooterPoster =
  "https://cdn.prod.website-files.com/689c67bcc7193a0725e2aecf/68c857672308a50ed1479a72_longbow-footer-poster-1.jpg";
const FooterVideo =
  "https://s3.amazonaws.com/webflow-prod-assets/689c67bcc7193a0725e2aecf/68c85755fe1e0cf96d4d079b_longbow-footer-video-1.mp4";

const InstagramIcon = () => (
  <svg fill="none" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" style={{ width: 17, height: 24, flex: "0 0 auto" }}>
    <path d="M7.38 1H16.62C20.14 1 23 3.86 23 7.38V16.62C23 18.3121 22.3278 19.9349 21.1313 21.1313C19.9349 22.3278 18.3121 23 16.62 23H7.38C3.86 23 1 20.14 1 16.62V7.38C1 5.68792 1.67218 4.06514 2.86866 2.86866C4.06514 1.67218 5.68792 1 7.38 1ZM7.16 3.2C6.10974 3.2 5.1025 3.61721 4.35986 4.35986C3.61721 5.1025 3.2 6.10974 3.2 7.16V16.84C3.2 19.029 4.971 20.8 7.16 20.8H16.84C17.8903 20.8 18.8975 20.3828 19.6401 19.6401C20.3828 18.8975 20.8 17.8903 20.8 16.84V7.16C20.8 4.971 19.029 3.2 16.84 3.2H7.16ZM17.775 4.85C18.1397 4.85 18.4894 4.99487 18.7473 5.25273C19.0051 5.51059 19.15 5.86033 19.15 6.225C19.15 6.58967 19.0051 6.93941 18.7473 7.19727C18.4894 7.45513 18.1397 7.6 17.775 7.6C17.4103 7.6 17.0606 7.45513 16.8027 7.19727C16.5449 6.93941 16.4 6.58967 16.4 6.225C16.4 5.86033 16.5449 5.51059 16.8027 5.25273C17.0606 4.99487 17.4103 4.85 17.775 4.85ZM12 6.5C13.4587 6.5 14.8576 7.07946 15.8891 8.11091C16.9205 9.14236 17.5 10.5413 17.5 12C17.5 13.4587 16.9205 14.8576 15.8891 15.8891C14.8576 16.9205 13.4587 17.5 12 17.5C10.5413 17.5 9.14236 16.9205 8.11091 15.8891C7.07946 14.8576 6.5 13.4587 6.5 12C6.5 10.5413 7.07946 9.14236 8.11091 8.11091C9.14236 7.07946 10.5413 6.5 12 6.5ZM12 8.7C11.1248 8.7 10.2854 9.04768 9.66655 9.66655C9.04768 10.2854 8.7 11.1248 8.7 12C8.7 12.8752 9.04768 13.7146 9.66655 14.3335C10.2854 14.9523 11.1248 15.3 12 15.3C12.8752 15.3 13.7146 14.9523 14.3335 14.3335C14.9523 13.7146 15.3 12.8752 15.3 12C15.3 11.1248 14.9523 10.2854 14.3335 9.66655C13.7146 9.04768 12.8752 8.7 12 8.7Z" fill="currentColor" />
  </svg>
);

const LinkedInIcon = () => (
  <svg fill="none" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg" style={{ width: 17, height: 24, flex: "0 0 auto" }}>
    <path clipRule="evenodd" d="M9.429 8.969H13.143V10.819C13.678 9.755 15.05 8.799 17.111 8.799C21.062 8.799 22 10.917 22 14.803V22H18V15.688C18 13.475 17.465 12.227 16.103 12.227C14.214 12.227 13.429 13.572 13.429 15.687V22H9.429V8.969ZM2.57 21.83H6.57V8.799H2.57V21.83ZM7.143 4.55C7.14315 4.88528 7.07666 5.21724 6.94739 5.52659C6.81812 5.83594 6.62865 6.11651 6.39 6.352C6.15064 6.59012 5.86671 6.77874 5.55442 6.90708C5.24214 7.03543 4.90763 7.10098 4.57 7.1C3.8896 7.09847 3.23691 6.83029 2.752 6.353C2.5143 6.11665 2.32553 5.83575 2.1965 5.52637C2.06746 5.21699 2.00069 4.88521 2 4.55C2 3.873 2.27 3.225 2.753 2.747C3.2367 2.26788 3.89018 1.99938 4.571 2C5.253 2 5.907 2.269 6.39 2.747C6.873 3.225 7.143 3.873 7.143 4.55Z" fill="currentColor" fillRule="evenodd" />
  </svg>
);

const XIcon = () => (
  <svg fill="none" height="16" viewBox="0 0 18 16" width="18" xmlns="http://www.w3.org/2000/svg" style={{ width: 17, height: 16, flex: "0 0 auto" }}>
    <path d="M14.175 0H16.9354L10.9054 6.7768L18 16H12.4457L8.09229 10.4073L3.11657 16H0.353571L6.80271 8.74905L0 0.00126102H5.69571L9.62486 5.11223L14.175 0ZM13.2043 14.3758H14.7343L4.86 1.53972H3.21943L13.2043 14.3758Z" fill="currentColor" />
  </svg>
);

const YouTubeIcon = () => (
  <svg fill="none" height="18" viewBox="0 0 22 18" width="22" xmlns="http://www.w3.org/2000/svg" style={{ width: 17, height: 18, flex: "0 0 auto" }}>
    <path d="M11 0C11.9405 0 12.9052 0.0247501 13.8402 0.0652501L14.9446 0.11925L16.0017 0.183375L16.9917 0.252L17.8959 0.324C18.8773 0.400378 19.8009 0.828488 20.504 1.53293C21.207 2.23737 21.6445 3.17294 21.7393 4.17487L21.7833 4.653L21.8658 5.67675C21.9428 6.73762 22 7.89412 22 9C22 10.1059 21.9428 11.2624 21.8658 12.3233L21.7833 13.347L21.7393 13.8251C21.6445 14.8272 21.2068 15.763 20.5035 16.4674C19.8002 17.1719 18.8764 17.5999 17.8948 17.676L16.9928 17.7469L16.0028 17.8166L14.9446 17.8807L13.8402 17.9347C12.894 17.9767 11.9471 17.9984 11 18C10.0529 17.9984 9.10599 17.9767 8.1598 17.9347L7.0554 17.8807L5.9983 17.8166L5.0083 17.7469L4.1041 17.676C3.12269 17.5996 2.19912 17.1715 1.49605 16.4671C0.792977 15.7626 0.35551 14.8271 0.2607 13.8251L0.2167 13.347L0.1342 12.3233C0.050416 11.2175 0.00565361 10.109 0 9C0 7.89412 0.0572 6.73762 0.1342 5.67675L0.2167 4.653L0.2607 4.17487C0.355473 3.17312 0.792783 2.23768 1.49563 1.53327C2.19848 0.828854 3.12179 0.400631 4.103 0.324L5.0061 0.252L5.9961 0.183375L7.0543 0.11925L8.1587 0.0652501C9.10525 0.0233181 10.0526 0.00156328 11 0ZM11 2.25C10.0925 2.25 9.1586 2.27475 8.25 2.313L7.1742 2.36588L6.1413 2.42775L5.1711 2.49525L4.2823 2.56613C3.81501 2.59958 3.37446 2.80139 3.03893 3.13569C2.70339 3.46999 2.49462 3.91513 2.4497 4.392C2.321 5.75212 2.2 7.44525 2.2 9C2.2 10.5548 2.321 12.2479 2.4497 13.608C2.5432 14.589 3.3044 15.3517 4.2823 15.4339L5.1711 15.5036L6.1413 15.5711L7.1742 15.6341L8.25 15.687C9.1586 15.7253 10.0925 15.75 11 15.75C11.9075 15.75 12.8414 15.7253 13.75 15.687L14.8258 15.6341L15.8587 15.5722L16.8289 15.5047L17.7177 15.4339C18.185 15.4004 18.6255 15.1986 18.9611 14.8643C19.2966 14.53 19.5054 14.0849 19.5503 13.608C19.679 12.2479 19.8 10.5548 19.8 9C19.8 7.44525 19.679 5.75212 19.5503 4.392C19.5054 3.91513 19.2966 3.46999 18.9611 3.13569C18.6255 2.80139 18.185 2.59958 17.7177 2.56613L16.8289 2.49637L15.8587 2.42887L14.8258 2.36588L13.75 2.313C12.8339 2.27278 11.917 2.25178 11 2.25ZM8.8 6.27187C8.79993 6.16192 8.82612 6.05361 8.8763 5.95637C8.92648 5.85913 8.99913 5.7759 9.08793 5.71391C9.17673 5.65193 9.27899 5.61307 9.38582 5.60071C9.49264 5.58835 9.60081 5.60287 9.7009 5.643L9.79 5.688L14.41 8.415C14.502 8.46929 14.5798 8.54549 14.6369 8.63712C14.6939 8.72875 14.7285 8.83311 14.7377 8.94133C14.7469 9.04955 14.7304 9.15844 14.6896 9.25875C14.6488 9.35906 14.585 9.44782 14.5035 9.5175L14.41 9.585L9.79 12.3131C9.6969 12.3683 9.59203 12.3993 9.48452 12.4035C9.37702 12.4077 9.27014 12.385 9.17318 12.3373C9.07623 12.2896 8.99215 12.2184 8.92826 12.1299C8.86436 12.0413 8.8226 11.9382 8.8066 11.8294L8.8 11.7281V6.27187Z" fill="currentColor" />
  </svg>
);

const socials = [
  { href: "https://www.instagram.com/longbowmotors", Icon: InstagramIcon },
  { href: "https://www.linkedin.com/company/longbowmotors/", Icon: LinkedInIcon },
  { href: "http://x.com/longbowmotors", Icon: XIcon },
  { href: "https://www.youtube.com/@longbowmotors", Icon: YouTubeIcon },
];

const HorizontalLine = () => (
  <div className="footer-line" style={{ gridColumn: "1 / -1" }}>
    <div style={{ position: "relative", display: "flex", alignItems: "center", height: 12 }}>
      {[0, 25, 50, 75, 100].map((p) => (
        <div
          key={p}
          style={{
            position: "absolute",
            left: `${p}%`,
            transform: "translateX(-50%)",
            width: 1,
            height: 12,
            background: "var(--primary-20)",
          }}
        />
      ))}
      <div style={{ width: "100%", height: 1, background: "var(--primary-20)" }} />
    </div>
  </div>
);

export default function FooterSection() {
  return (
    <section
      className="section section--footer"
      style={{
        position: "relative",
        display: "flex",
        justifyContent: "center",
        overflow: "hidden",
        background: "#000",
        color: "var(--primary, #fff)",
        fontFamily: 'Inter, "Bebas Neue", Arial, sans-serif',
      }}
    >
      <style>{`
        :root {
          --primary: white;
          --primary-5: #ffffff0d;
          --primary-10: #ffffff1a;
          --primary-15: #ffffff26;
          --primary-20: #fff3;
        }
        .footer-nav__link {
          position: relative;
          display: block;
          color: var(--primary);
          text-decoration: none;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          font-size: 14px;
          line-height: 1.2;
          padding: 4px 0;
          opacity: 0.7;
          transition: opacity 0.3s ease;
        }
        .footer-nav__link:hover,
        .footer-nav__link.is-current { opacity: 1; }
        .footer-social {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 44px;
          height: 44px;
          color: var(--primary);
          border: 1px solid var(--primary-15);
          border-radius: 999px;
          transition: background 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }
        .footer-social:hover {
          background: var(--primary);
          color: #000;
          border-color: var(--primary);
        }
        .footer-mail {
          color: var(--primary);
          text-decoration: none;
          opacity: 0.7;
          transition: opacity 0.3s ease;
          display: inline-block;
        }
        .footer-mail:hover { opacity: 1; }
        @keyframes footerMarquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
        .footer-marquee-line {
          display: flex;
          width: max-content;
          animation: footerMarquee 15s linear infinite;
        }
        @media (max-width: 991px) {
          .footer-layout { grid-template-columns: 1fr !important; }
        }
      `}</style>

      {/* Background video */}
      <div
        className="background background--footer"
        style={{ position: "absolute", inset: 0, zIndex: 0, pointerEvents: "none" }}
      >
        <video
          autoPlay
          loop
          muted
          playsInline
          poster={FooterPoster}
          preload="metadata"
          style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.55 }}
        >
          <source src={FooterVideo} type="video/mp4" />
        </video>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.65), rgba(0,0,0,0.85))" }} />
      </div>

      <div
        className="container"
        style={{ position: "relative", zIndex: 1, width: 1440, maxWidth: "100%", padding: "80px 24px 0", boxSizing: "border-box" }}
      >
        <div
          className="footer-layout"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "40px 24px",
            alignItems: "start",
          }}
        >
          <HorizontalLine />

          {/* Nav */}
          <nav className="nav" style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {navLinks.map((l) => (
              <a
                key={l.href + l.label}
                href={l.href}
                {...(l.current ? { "aria-current": "page" } : {})}
                className={"footer-nav__link" + (l.current ? " is-current" : "")}
              >
                {l.label}
              </a>
            ))}
          </nav>

          {/* Socials */}
          <div className="socials" style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
            {socials.map(({ href, Icon }) => (
              <a
                key={href}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="footer-social"
              >
                <Icon />
              </a>
            ))}
          </div>

          {/* Contact card */}
          <div className="card card--footer" style={{ display: "flex", flexDirection: "column", gap: 24, width: 355, maxWidth: "100%" }}>
            <div className="card__header" style={{ display: "flex", flexDirection: "column", gap: 16, width: 301, maxWidth: "100%" }}>
              <div
                className="tag"
                style={{
                  display: "inline-block",
                  fontSize: 12,
                  letterSpacing: "0.04em",
                  opacity: 0.6,
                  textTransform: "lowercase",
                }}
              >
                .contacts
              </div>
              <div className="text text--normal" style={{ fontSize: 15, lineHeight: 1.5, opacity: 0.85 }}>
                L71-75 Shelton Street, Covent Garden, London, WC2H 9JQ, United Kingdom
              </div>
            </div>
            <div className="card__footer" style={{ display: "flex", flexDirection: "column", gap: 16, width: 301, maxWidth: "100%" }}>
              <div className="links" style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <a className="footer-mail" href="mailto:enquiries@longbowmotors.com">
                  <span className="text text--normal" style={{ fontSize: 15, lineHeight: 1.5 }}>
                    enquiries@longbowmotors.com
                  </span>
                </a>
                <a className="footer-mail" href="mailto:press@longbowmotors.com">
                  <span className="text text--normal" style={{ fontSize: 15, lineHeight: 1.5 }}>
                    press@longbowmotors.com
                  </span>
                </a>
              </div>
              <div className="text text--normal" style={{ fontSize: 15, lineHeight: 1.5, opacity: 0.85 }}>
                Longbow Motorcar Company Limited – Company number 15044627
              </div>
            </div>
          </div>

          <HorizontalLine />
        </div>

        {/* Longbow marquee */}
        <div className="marquee-wrapper" style={{ overflow: "hidden", width: "100%", marginTop: 40 }}>
          <div className="footer-marquee-line">
            {[0, 1].map((i) => (
              <div
                key={i}
                className="heading-marquee heading-marquee--lg"
                style={{
                  fontFamily: '"Bebas Neue", "Lora", Arial, sans-serif',
                  fontSize: "clamp(80px, 18vw, 280px)",
                  lineHeight: 0.9,
                  textTransform: "none",
                  whiteSpace: "nowrap",
                  paddingRight: 40,
                  fontWeight: 400,
                }}
              >
                Longbow
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
