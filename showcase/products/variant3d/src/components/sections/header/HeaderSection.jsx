export default function HeaderSection() {
  const logoPath = (
    <path
      className="header-svg-fill-change"
      d="M10.4742 29.6224L2.32802 13.2203C2.22372 13.0072 1.95926 12.8502 1.6948 12.8502H0.741241C0.31661 12.8502 0 12.5324 0 12.1062V0.691675C0 0.317797 0.31661 0 0.741241 0H9.89314C10.2098 0 10.4221 0.104686 10.5264 0.37014L16.5569 11.8893C16.6612 12.1548 16.9256 12.3156 17.1901 12.3156H17.8233C18.2479 12.3156 18.5645 11.9978 18.5645 11.5715V0.691675C18.5645 0.321535 18.8812 0 19.2536 0H31.2588C31.6834 0 32 0.317797 32 0.691675V12.1062C32 12.5324 31.6834 12.8502 31.2588 12.8502H27.0274C24.1183 12.8502 22.7438 14.2298 22.7438 17.1498V29.3083C22.7438 29.6785 22.4272 30 22.0026 30H11.1074C10.843 30 10.6307 29.8392 10.4742 29.6299V29.6224Z"
      fill="#F5F3F0"
      style={{ transition: "fill 0.3s ease-in-out" }}
    />
  );

  return (
    <header
      className="v3-header"
      data-mode="light"
      style={{
        opacity: 1,
        transform: "translate3d(0px, 0px, 0px)",
        display: "flex",
      }}
    >
      <style>{`
        .v3-header {
          z-index: 99;
          width: 100vw;
          color: #f5f3f0;
          justify-content: space-between;
          padding: 24px;
          font-family: "Founders Grotesk", Arial, sans-serif;
          display: flex;
          position: fixed;
          top: 0;
          left: 0;
          box-sizing: border-box;
        }
        .v3-main-nav {
          width: 544px;
          max-width: 100%;
          border: 1.2px solid #e5e3e033;
          border-radius: 12px;
          background-color: #94939059;
          -webkit-backdrop-filter: blur(8px);
          backdrop-filter: blur(8px);
          box-sizing: border-box;
        }
        .v3-nav-content {
          column-gap: 40px;
          flex: 0 auto;
          justify-content: flex-start;
          align-items: center;
          height: 58px;
          padding: 4px 6px 4px 16px;
          text-decoration: none;
          display: flex;
        }
        .v3-home-link {
          display: flex;
          align-items: center;
          text-decoration: none;
        }
        .v3-logo {
          width: 32px;
          height: 30px;
          display: flex;
        }
        .v3-menu {
          column-gap: 24px;
          row-gap: 24px;
          justify-content: center;
          align-items: center;
          margin: 0;
          padding-left: 0;
          list-style-type: none;
          display: flex;
        }
        .v3-menu-item {
          margin: 0;
        }
        .v3-menu-item-link {
          height: 48px;
          padding: 0 22px 0 24px;
          column-gap: 10px;
          color: #f5f3f0;
          font-size: 18px;
          letter-spacing: .54px;
          text-transform: uppercase;
          white-space: nowrap;
          cursor: pointer;
          background-color: transparent;
          border-radius: 8px;
          flex: 0 auto;
          justify-content: center;
          align-items: center;
          line-height: 24px;
          text-decoration: none;
          transition: background-color .2s, color .3s;
          display: flex;
        }
        .v3-menu-item-link:hover {
          background-color: #ffffff14;
        }
        .v3-menu-item-link.v3-loop {
          padding-right: 18px;
        }
        .v3-case-studies-text {
          color: #f5f3f0;
          letter-spacing: .03em;
          text-transform: uppercase;
          margin: 0;
          font-family: "Founders Grotesk", Arial, sans-serif;
          font-weight: 400;
          font-size: 18px;
          line-height: 24px;
          text-decoration: none;
        }
        .v3-chevron-down {
          justify-content: center;
          align-items: center;
          width: 7px;
          height: 4px;
          transition: opacity .2s;
          display: flex;
        }
        .v3-case-studies-item {
          position: relative;
        }
        .v3-case-studies-submenu {
          position: absolute;
          top: calc(100% + 8px);
          left: 50%;
          transform: translateX(-50%);
          min-width: 220px;
          padding: 8px;
          border: 1.2px solid #e5e3e033;
          border-radius: 12px;
          background-color: #94939059;
          -webkit-backdrop-filter: blur(8px);
          backdrop-filter: blur(8px);
          opacity: 0;
          visibility: hidden;
          pointer-events: none;
          transition: opacity .2s;
          z-index: 100;
        }
        .v3-case-studies-item:hover .v3-case-studies-submenu {
          opacity: 1;
          visibility: visible;
          pointer-events: auto;
        }
        .v3-case-studies-list {
          margin: 0;
          padding: 0;
          list-style-type: none;
        }
        .v3-submenu-item-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 14px;
          color: #f5f3f0;
          font-size: 18px;
          line-height: 1;
          text-decoration: none;
          border-radius: 8px;
          white-space: nowrap;
          transition: background-color .2s;
        }
        .v3-submenu-item-link:hover {
          background-color: #ffffff14;
        }
        .v3-header-button-container {
          display: flex;
          align-items: center;
        }
        .v3-button {
          column-gap: 12px;
          row-gap: 12px;
          border-radius: 12px;
          background-color: #ffffff;
          height: 60px;
          color: #1a1919;
          font-size: 18px;
          letter-spacing: .003em;
          text-transform: uppercase;
          white-space: nowrap;
          cursor: pointer;
          flex: 0 auto;
          justify-content: center;
          align-items: center;
          padding: 0 24px;
          font-weight: 500;
          line-height: 58px;
          text-decoration: none;
          transition: color .2s, background-color .2s;
          display: flex;
        }
        .v3-button:hover {
          background-color: #f75f2d;
          color: #f5f3f0;
        }
        @media screen and (max-width: 991px) {
          .v3-header {
            height: 80px;
            padding: 20px 20px 0;
          }
          .v3-main-nav { display: none; }
          .v3-header-button-container { display: none; }
        }
      `}</style>

      <div className="v3-main-nav">
        <nav className="v3-nav-content">
          <a aria-current="page" className="v3-home-link" href="/">
            <div className="v3-logo">
              <svg
                fill="none"
                height="30"
                style={{ width: "32px", height: "30px", flex: "0 0 auto" }}
                viewBox="0 0 32 30"
                width="32"
                xmlns="http://www.w3.org/2000/svg"
              >
                {logoPath}
              </svg>
            </div>
          </a>
          <ol className="v3-menu" role="list">
            <li className="v3-menu-item">
              <a className="v3-menu-item-link v3-loop" href="/loop">
                LOOP™
              </a>
            </li>
            <li className="v3-menu-item v3-case-studies-item">
              <div className="v3-menu-item-link" id="case-studies-btn">
                <p className="v3-case-studies-text">Case studies</p>
                <div className="v3-chevron-down">
                  <svg
                    fill="none"
                    height="4"
                    style={{ width: "7px", height: "4px", flex: "0 0 auto" }}
                    viewBox="0 0 7 4"
                    width="7"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      className="header-svg-fill-change"
                      d="M0.146447 0.146447C0.341709 -0.0488155 0.658291 -0.0488155 0.853553 0.146447L3.5 2.79289L6.14645 0.146447C6.34171 -0.0488155 6.65829 -0.0488155 6.85355 0.146447C7.04882 0.341709 7.04882 0.658291 6.85355 0.853553L3.85355 3.85355C3.65829 4.04882 3.34171 4.04882 3.14645 3.85355L0.146447 0.853553C-0.0488155 0.658291 -0.0488155 0.341709 0.146447 0.146447Z"
                      fill="#F5F3F0"
                      style={{ transition: "fill 0.3s ease-in-out" }}
                    />
                  </svg>
                </div>
              </div>
              <div className="v3-case-studies-submenu">
                <ul className="v3-case-studies-list" role="list">
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/footwear">
                      Footwear
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/furniture">
                      Furniture
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/apparel">
                      Apparel
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/transportation">
                      Transportation
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/accessories">
                      Accessories
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/medical">
                      Medical
                    </a>
                  </li>
                  <li>
                    <a className="v3-submenu-item-link" href="/case-studies/home-decor">
                      Home decor
                    </a>
                  </li>
                </ul>
              </div>
            </li>
            <li className="v3-menu-item">
              <a className="v3-menu-item-link" href="/about">
                About
              </a>
            </li>
          </ol>
        </nav>
      </div>

      <div className="v3-header-button-container">
        <a className="v3-button" href="/early-access">
          Get early access
        </a>
      </div>
    </header>
  );
}
