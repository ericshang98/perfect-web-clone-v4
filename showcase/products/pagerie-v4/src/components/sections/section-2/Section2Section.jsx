// Section2Section — clean JSX (v4 new-code pipeline)
export default function Section2Section() {
  return (
    <div className="pwc-section pwc-section-2">
      <div aria-hidden="true" className="shop-section" id="shop-section-sidebar-menu">
        <section aria-hidden="true" className="SidebarMenu Drawer Drawer--small Drawer--fromLeft" data-section-id="sidebar-menu" data-section-type="sidebar-menu" id="sidebar-menu" style={{ display: 'none !important' }}>
          <header className="Drawer__Header" data-drawer-animated-left="">
            <button aria-label="Close navigation" className="Drawer__Close Icon-Wrapper--clickable" data-action="close-drawer" data-drawer-id="sidebar-menu">
              <svg className="Icon Icon--close" role="presentation" viewbox="0 0 16 14">
                <path d="M15 0L1 14m14 0L1 0" fill="none" fillRule="evenodd" stroke="currentColor" />
              </svg>
            </button>
          </header>
          <div className="Drawer__Content">
            <div className="Drawer__Main" data-drawer-animated-left="" data-scrollable="">
              <div className="Drawer__Container">
                <nav aria-label="Sidebar navigation" className="SidebarMenu__Nav SidebarMenu__Nav--primary">
                  <div className="Collapsible">
                    <a className="Collapsible__Button Heading Link Link--primary u-h6" href="/collections">
                      SHOP
                    </a>
                  </div>
                  <div className="Collapsible">
                    <a className="Collapsible__Button Heading Link Link--primary u-h6" href="/collections/the-lana-bags">
                      LANA BAG
                    </a>
                  </div>
                  <div className="Collapsible">
                    <a className="Collapsible__Button Heading Link Link--primary u-h6" href="/pages/the-house-of-pagerie">
                      HERITAGE
                    </a>
                  </div>
                  <div className="Collapsible">
                    <a className="Collapsible__Button Heading Link Link--primary u-h6" href="">
                      STORIES
                    </a>
                  </div>
                </nav>
                <nav className="SidebarMenu__Nav SidebarMenu__Nav--secondary">
                  <ul className="Linklist Linklist--spacingLoose">
                    <li className="Linklist__Item">
                      <a className="Text--subdued Link Link--primary" href="/account">
                        Account
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </section>
      </div>
      <div className="shop-section" id="shop-section-announcement" />
    </div>
  );
}
