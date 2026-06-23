export default function FooterSection() {
  const ICON_LINK = "https://cdn.prod.website-files.com/685c9371c8316839f0948d31/689380fca298f093b7b0b659_IconLink.svg";
  const VECTOR = "https://cdn.prod.website-files.com/685c9371c8316839f0948d31/689380fe519a8a6b524e524b_979dd49e5d69315e1b70378f9f198945_Vector.svg";

  const hideOnError = (e) => {
    e.currentTarget.style.display = "none";
  };

  const navLinks = [
    { href: "/loop", label: "LOOP™ software" },
    { href: "/case-studies/footwear", label: "Case studies" },
    { href: "/about", label: "About" },
    { href: "/faqs", label: "FAQs" },
    { href: "/early-access", label: "Early access" },
  ];

  const socialLinks = [
    { href: "https://www.instagram.com/variant3d/?hl=it", label: "Instagram" },
    { href: "https://www.linkedin.com/company/variant-3d/", label: "Linkedin" },
    { href: "https://it.pinterest.com/variant3d/", label: "Pinterest" },
    { href: "https://www.tiktok.com/@variant3d", label: "TikTok" },
    { href: "https://www.youtube.com/channel/UCfSZVt3wni2DbOwgmES8hIA", label: "Youtube" },
    { href: "https://www.facebook.com/?mibextid=LQQJ4d", label: "Facebook" },
  ];

  return (
    <footer
      className="block"
      style={{ backgroundColor: "var(--_colors---bg-dark, #000)" }}
    >
      {/* Scoped styles to faithfully reproduce footer typography, colors, hover and responsive behavior */}
      <style>{`
        .v3-footer {
          --footer-page-padding: 32px;
          --footer-link-size: 22px;
          --footer-policies-size: 18px;
          --footer-brand: #f75f2d;
          --footer-font-light: #f5f3f0;
          --footer-gray-500: #949390;
          background-color: #000;
          color: var(--footer-font-light);
        }
        .v3-footer-content {
          z-index: 0;
          width: 100%;
          padding: 120px var(--footer-page-padding) 32px;
          row-gap: 20px;
          background-color: #000;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-items: flex-start;
        }
        .v3-footer-links {
          column-gap: 32px;
          justify-content: space-between;
          align-items: flex-start;
          width: 100%;
          max-width: 960px;
          text-decoration: none;
          display: flex;
        }
        .v3-footer-links-list {
          row-gap: 6px;
          flex-direction: column;
          justify-content: flex-start;
          align-items: flex-start;
          text-decoration: none;
          display: flex;
        }
        .v3-footer-links-contact {
          row-gap: 20px;
          font-style: normal;
        }
        .v3-footer-link {
          color: var(--footer-font-light);
          font-size: var(--footer-link-size);
          margin: 0;
          font-style: normal;
          line-height: 110%;
          text-decoration: none;
          transition: color .2s;
        }
        .v3-footer-link:hover { color: var(--footer-brand); }
        .v3-footer-text {
          width: 100%;
          color: var(--footer-font-light);
          font-size: var(--footer-link-size);
          white-space: pre-line;
          margin: 0;
          font-style: normal;
          line-height: 110%;
        }
        .v3-footer-text-gray { color: var(--footer-gray-500); }
        .v3-footer-booking {
          column-gap: 20px;
          row-gap: 6px;
          flex-flow: row;
          justify-content: flex-start;
          align-items: center;
          text-decoration: none;
          display: flex;
        }
        .v3-footer-link-booking {
          column-gap: 8px;
          flex: 0 auto;
          justify-content: flex-start;
          align-items: center;
          text-decoration: none;
          white-space: nowrap;
          display: flex;
        }
        .v3-arrow-icon {
          width: 24px;
          min-width: 24px;
          height: 24px;
          min-height: 24px;
          overflow: hidden;
        }
        .v3-footer-bottom {
          row-gap: 22px;
          flex-direction: column;
          justify-content: center;
          align-items: flex-start;
          width: 100%;
          text-decoration: none;
          display: flex;
        }
        .v3-policies {
          column-gap: 80px;
          justify-content: flex-start;
          align-items: center;
          display: flex;
        }
        .v3-policies-link {
          color: var(--footer-font-light);
          font-family: 'Founders Grotesk', Arial, sans-serif;
          font-size: var(--footer-policies-size);
          letter-spacing: .03em;
          text-transform: uppercase;
          font-weight: 500;
          line-height: 100%;
          text-decoration: none;
          transition: color .2s;
        }
        .v3-policies-link:hover { color: var(--footer-brand); }
        .v3-image-5 { width: 100%; }

        @media screen and (min-width: 1440px) {
          .v3-footer {
            --footer-page-padding: 40px;
            --footer-link-size: 24px;
          }
          .v3-footer-content {
            row-gap: 80px;
            justify-content: flex-end;
            padding-top: 40px;
            padding-bottom: 40px;
          }
        }
        @media screen and (min-width: 1920px) {
          .v3-footer-content { row-gap: 120px; }
        }
        @media screen and (max-width: 991px) {
          .v3-footer { --footer-page-padding: 24px; --footer-link-size: 22px; }
          .v3-footer-content { row-gap: 60px; justify-content: flex-end; }
          .v3-policies { column-gap: 60px; }
        }
        @media screen and (max-width: 767px) {
          .v3-footer {
            --footer-page-padding: 16px;
            --footer-link-size: 18px;
            --footer-policies-size: 12px;
          }
          .v3-footer-content { row-gap: 40px; }
          .v3-footer-links { row-gap: 40px; flex-flow: column; }
          .v3-footer-booking {
            flex-flow: column;
            justify-content: center;
            align-items: flex-start;
          }
          .v3-footer-bottom { row-gap: 20px; }
          .v3-policies { column-gap: 20px; justify-content: space-between; width: 100%; }
        }
      `}</style>

      <div className="v3-footer">
        <div className="v3-footer-content">
          {/* Footer link columns */}
          <div className="v3-footer-links">
            <div className="v3-footer-links-list">
              {navLinks.map((l) => (
                <a key={l.href} className="v3-footer-link" href={l.href}>
                  {l.label}
                </a>
              ))}
            </div>

            <div className="v3-footer-links-list">
              {socialLinks.map((l) => (
                <a
                  key={l.href}
                  className="v3-footer-link"
                  href={l.href}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {l.label}
                </a>
              ))}
            </div>

            <address className="v3-footer-links-list v3-footer-links-contact">
              <p className="v3-footer-text">
                327 Latigo Canyon Rd.
                <br />
                Malibu, CA 90265
              </p>
              <a className="v3-footer-link" href="mailto:support@variant3d.io">
                support@variant3d.io
              </a>
              <a className="v3-footer-link" href="tel:8188896280">
                <p className="v3-footer-link" style={{ marginBottom: 0 }}>
                  818-889-6280
                </p>
                Ext. 715
              </a>
            </address>
          </div>

          {/* Booking */}
          <div className="v3-footer-booking">
            <p className="v3-footer-text v3-footer-text-gray">
              Arrange a visit to VARIANT3D in Malibu
            </p>
            <a className="v3-footer-link-booking v3-footer-link" href="/booking">
              <p className="v3-footer-link" style={{ marginBottom: 0 }}>
                Booking form
              </p>
              <img
                alt=""
                className="v3-arrow-icon"
                loading="lazy"
                src={ICON_LINK}
                onError={hideOnError}
              />
            </a>
          </div>

          {/* Bottom: policies + brand vector */}
          <div className="v3-footer-bottom">
            <div className="v3-policies">
              <a className="v3-policies-link" href="/privacy-policy">
                Privacy Policy
              </a>
              <a className="v3-policies-link" href="/terms-and-conditions">
                Terms &amp; Conditions
              </a>
            </div>
            <img
              alt=""
              className="v3-image-5"
              loading="lazy"
              src={VECTOR}
              onError={hideOnError}
            />
          </div>
        </div>
      </div>
    </footer>
  );
}
