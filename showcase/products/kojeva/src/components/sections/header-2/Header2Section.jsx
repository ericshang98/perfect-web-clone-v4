const navLinks = [
  { label: "Home", href: "https://kojeva.com/" },
  { label: "Shop Now", href: "https://kojeva.com/collections/products" },
  { label: "Track Your Order", href: "https://kojeva.com/apps/parcelpanel" },
  { label: "Contact", href: "https://kojeva.com/pages/contact" },
];

const productUrl = "https://kojeva.com/products/kojeva-lymphatic-face-brush";

const countries = [
  ["Australia", "AUD $"],
  ["Austria", "EUR €"],
  ["Belgium", "EUR €"],
  ["Canada", "CAD $"],
  ["Czechia", "CZK Kč"],
  ["Denmark", "DKK kr."],
  ["Finland", "EUR €"],
  ["France", "EUR €"],
  ["Germany", "EUR €"],
  ["Hong Kong SAR", "HKD $"],
  ["Ireland", "EUR €"],
  ["Israel", "ILS ₪"],
  ["Italy", "EUR €"],
  ["Japan", "JPY ¥"],
  ["Malaysia", "MYR RM"],
  ["Netherlands", "EUR €"],
  ["New Zealand", "NZD $"],
  ["Norway", "USD $"],
  ["Poland", "PLN zł"],
  ["Portugal", "EUR €"],
  ["Singapore", "SGD $"],
  ["South Korea", "KRW ₩"],
  ["Spain", "EUR €"],
  ["Sweden", "SEK kr"],
  ["Switzerland", "CHF CHF"],
  ["United Arab Emirates", "AED د.إ"],
  ["United Kingdom", "GBP £"],
  ["United States", "USD $"],
];

export default function Header2Section() {
  return (
    <header className="site-header">
      <div className="nav-shell">
        <a className="brand-link" href="https://kojeva.com/" aria-label="Kojeva home">
          <img src="/assets/images/Kojeva_Logo.png" alt="Kojeva" />
        </a>
        <nav className="desktop-nav" aria-label="Primary">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
        <div className="nav-tools">
          <details className="country-menu">
            <summary>Singapore | SGD $ <span aria-hidden="true">⌄</span></summary>
            <div className="country-options" aria-label="Country/region">
              {countries.map(([country, currency]) => (
                <a href={productUrl} key={country}>
                  <span>{country}</span><span>{currency}</span>
                </a>
              ))}
            </div>
          </details>
          <a className="search-icon" href="https://kojeva.com/search" aria-label="Search">
            <span />
          </a>
          <a className="cart-icon" href="https://kojeva.com/cart" aria-label="Cart">
            <span />
          </a>
        </div>
      </div>
    </header>
  );
}
