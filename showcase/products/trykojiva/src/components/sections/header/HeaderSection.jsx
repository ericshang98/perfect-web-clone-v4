import { BagIcon, GlobeIcon, MenuIcon, SearchIcon } from '../../Icons.jsx'
import { asset } from '../../../data.js'

const navigation = [
  ['Clothing', 'https://trykojiva.com/clothing'],
  ['Lymphatic Brush', 'https://trykojiva.com/brush'],
]

export default function HeaderSection() {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <button className="icon-button menu-button" type="button" aria-label="Open menu">
          <MenuIcon />
        </button>

        <a className="brand" href="https://trykojiva.com/brush" aria-label="Linfae home">
          <img src={asset('iREiPEhXkQPmILks.png')} alt="Linfae" />
        </a>

        <nav className="main-navigation" aria-label="Main navigation">
          {navigation.map(([label, href]) => (
            <a href={href} key={href}>{label}</a>
          ))}
        </nav>

        <div className="header-actions">
          <button className="language-button" type="button" aria-label="Select language">
            <GlobeIcon />
            <span>🇬🇧 EN</span>
            <span aria-hidden="true">⌄</span>
          </button>
          <a className="icon-button desktop-action" href="https://trykojiva.com/search" aria-label="Search Linfae">
            <SearchIcon />
          </a>
          <a className="icon-button" href="https://trykojiva.com/cart" aria-label="View cart">
            <BagIcon />
          </a>
        </div>
      </div>
    </header>
  )
}
