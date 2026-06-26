// HeaderSection — clean JSX (route-(c) phase 2; theme.css styles real class names)
export default function HeaderSection() {
  return (
    <div className="pwc-section pwc-header">
      <div className="site-section site-section--header" id="site-section-header">
        <div aria-hidden="true" className="Search" id="Search" style={{ display: 'none !important' }}>
          <div className="Search__Inner">
            <div className="Search__SearchBar">
              <form action="/search" className="Search__Form" name="GET" role="search">
                <div className="Search__InputIconWrapper">
                  <span className="hidden-tablet-and-up">
                    <svg className="Icon Icon--search" role="presentation" viewbox="0 0 18 17">
                      <g fill="none" fillRule="evenodd" stroke="currentColor" strokeLinecap="square" transform="translate(1 1)">
                        <path d="M16 16l-5.0752-5.0752" />
                        <circle cx="6.4" cy="6.4" r="6.4" />
                      </g>
                    </svg>
                  </span>
                  <span className="hidden-phone">
                    <svg className="Icon Icon--search-desktop" role="presentation" viewbox="0 0 21 21">
                      <g fill="none" fillRule="evenodd" stroke="currentColor" strokeLinecap="square" strokeWidth="2" transform="translate(1 1)">
                        <path d="M18 18l-5.7096-5.7096" />
                        <circle cx="7.2" cy="7.2" r="7.2" />
                      </g>
                    </svg>
                  </span>
                </div>
                <input autocapitalize="off" autoComplete="off" autocorrect="off" autoFocus className="Search__Input Heading" name="q" placeholder="Search..." type="search" />
                <input name="type" type="hidden" value="product" />
              </form>
              <button className="Search__Close Link Link--primary" data-action="close-search">
                <svg className="Icon Icon--close" role="presentation" viewbox="0 0 16 14">
                  <path d="M15 0L1 14m14 0L1 0" fill="none" fillRule="evenodd" stroke="currentColor" />
                </svg>
              </button>
            </div>
            <div aria-hidden="true" className="Search__Results">
              <div className="PageLayout PageLayout--breakLap">
                <div className="PageLayout__Section" />
                <div className="PageLayout__Section PageLayout__Section--secondary" />
              </div>
            </div>
          </div>
        </div>
        <header className="Header Header--inline Header--initialized" data-section-settings={"{\n  \"navigationStyle\": \"inline\",\n  \"hasTransparentHeader\": false,\n  \"isSticky\": true\n}"} id="section-header" role="banner">
          <div className="Header__Wrapper" style={{ display: 'flex' }}>
            <div className="Header__FlexItem Header__FlexItem--fill" style={{ display: 'flex' }}>
              <button aria-expanded="false" aria-label="Open navigation" className="Header__Icon Icon-Wrapper Icon-Wrapper--clickable hidden-desk" data-action="open-drawer" data-drawer-id="sidebar-menu" style={{ display: 'none !important' }}>
                <span className="hidden-tablet-and-up">
                  <svg className="Icon Icon--nav" id="Layer_1" role="presentation" style={{ enableBackground: 'new 0 0 30 16' }} version="1.1" viewbox="0 0 20 14" x="0px" xmlSpace="preserve" xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink" y="0px">
                    <rect className="st0" height="1" width="30" />
                    <rect className="st0" height="1" width="30" y="13" />
                  </svg>
                </span>
                <span className="hidden-phone">
                  <svg className="Icon Icon--nav-desktop" role="presentation" viewbox="0 0 24 16">
                    <path d="M0 15.985v-2h24v2H0zm0-9h24v2H0v-2zm0-7h24v2H0v-2z" fill="currentColor" />
                  </svg>
                </span>
              </button>
              <nav aria-label="Main navigation" className="Header__MainNav hidden-pocket hidden-lap">
                <ul className="HorizontalList HorizontalList--spacingExtraLoose">
                  <li className="HorizontalList__Item">
                    <a className="Heading u-h6" href="/collections">
                      SHOP
                      <span className="Header__LinkSpacer">
                        SHOP
                      </span>
                    </a>
                  </li>
                  <li className="HorizontalList__Item">
                    <a className="Heading u-h6" href="/collections/the-lana-bags">
                      LANA BAG
                      <span className="Header__LinkSpacer">
                        LANA BAG
                      </span>
                    </a>
                  </li>
                  <li className="HorizontalList__Item">
                    <a className="Heading u-h6" href="/pages/the-house-of-pagerie">
                      HERITAGE
                      <span className="Header__LinkSpacer">
                        HERITAGE
                      </span>
                    </a>
                  </li>
                  <li className="HorizontalList__Item">
                    <a className="Heading u-h6" href="">
                      STORIES
                      <span className="Header__LinkSpacer">
                        STORIES
                      </span>
                    </a>
                  </li>
                </ul>
              </nav>
            </div>
            <div className="Header__FlexItem Header__FlexItem--logo" style={{ display: 'flex' }}>
              <h1 className="Header__Logo">
                <a className="Header__LogoLink" href="/">
                  <img alt="PAGERIE" className="Header__LogoImage Header__LogoImage--primary" src="/assets/images/pagerie-logo-white_140x.svg" srcSet="/assets/images/pagerie-logo-white_140x.svg 1x, /assets/images/pagerie-logo-white_140x@2x.1c6c56.svg 2x" width="140" />
                </a>
              </h1>
            </div>
            <div className="Header__FlexItem Header__FlexItem--fill" style={{ display: 'flex' }}>
              <nav className="Header__SecondaryNav hidden-phone">
                <ul className="HorizontalList HorizontalList--spacingLoose hidden-pocket hidden-lap">
                  <li className="HorizontalList__Item">
                    <a className="Heading Link Link--primary Text--subdued u-h8" href="/account">
                      Account
                    </a>
                  </li>
                  <li className="HorizontalList__Item">
                    <a className="Heading Link Link--primary Text--subdued u-h8" data-action="toggle-search" href="javascript:void(0);">
                      Search
                    </a>
                  </li>
                  <li className="HorizontalList__Item">
                    <a aria-label="Open cart" className="Heading u-h6" data-action="open-drawer" data-drawer-id="sidebar-cart" href="/cart">
                      Cart (
                      <span className="Header__CartCount">
                        0
                      </span>
                      )
                    </a>
                  </li>
                </ul>
              </nav>
              <a aria-label="Search" className="Header__Icon Icon-Wrapper Icon-Wrapper--clickable hidden-desk" data-action="toggle-search" href="/search" style={{ display: 'none !important' }}>
                <span className="hidden-tablet-and-up">
                  <svg className="Icon Icon--search" role="presentation" viewbox="0 0 18 17">
                    <g fill="none" fillRule="evenodd" stroke="currentColor" strokeLinecap="square" transform="translate(1 1)">
                      <path d="M16 16l-5.0752-5.0752" />
                      <circle cx="6.4" cy="6.4" r="6.4" />
                    </g>
                  </svg>
                </span>
                <span className="hidden-phone">
                  <svg className="Icon Icon--search-desktop" role="presentation" viewbox="0 0 21 21">
                    <g fill="none" fillRule="evenodd" stroke="currentColor" strokeLinecap="square" strokeWidth="2" transform="translate(1 1)">
                      <path d="M18 18l-5.7096-5.7096" />
                      <circle cx="7.2" cy="7.2" r="7.2" />
                    </g>
                  </svg>
                </span>
              </a>
              <a aria-expanded="false" aria-label="Open cart" className="Header__Icon Icon-Wrapper Icon-Wrapper--clickable hidden-desk" data-action="open-drawer" data-drawer-id="sidebar-cart" href="/cart" style={{ display: 'none !important' }}>
                <span className="hidden-tablet-and-up">
                  <svg className="Icon Icon--cart" role="presentation" viewbox="0 0 17 20">
                    <path d="M0 20V4.995l1 .006v.015l4-.002V4c0-2.484 1.274-4 3.5-4C10.518 0 12 1.48 12 4v1.012l5-.003v.985H1V19h15V6.005h1V20H0zM11 4.49C11 2.267 10.507 1 8.5 1 6.5 1 6 2.27 6 4.49V5l5-.002V4.49z" fill="currentColor" />
                  </svg>
                </span>
                <span className="hidden-phone">
                  <svg className="Icon Icon--cart-desktop" role="presentation" viewbox="0 0 19 23">
                    <path d="M0 22.985V5.995L2 6v.03l17-.014v16.968H0zm17-15H2v13h15v-13zm-5-2.882c0-2.04-.493-3.203-2.5-3.203-2 0-2.5 1.164-2.5 3.203v.912H5V4.647C5 1.19 7.274 0 9.5 0 11.517 0 14 1.354 14 4.647v1.368h-2v-.912z" fill="currentColor" />
                  </svg>
                </span>
                <span className="Header__CartDot" />
              </a>
            </div>
          </div>
        </header>
      </div>
    </div>
  );
}
