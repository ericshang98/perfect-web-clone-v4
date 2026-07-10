// NavigationSection — clean JSX (route-(c) phase 2). Edit freely; the
// theme stylesheet (public/theme.css) styles the real class names.
export default function NavigationSection() {
  return (
    <>
      <nav className="navigation" data-v-59cd3fe9="" style={{ display: 'flex', width: '511px', maxWidth: '100%' }}>
        <button className="navigation__label" data-v-59cd3fe9="">
          Menu
          <div className="hamburger-icon" data-v-59cd3fe9="">
            <span className="hamburger-line hamburger-line--top" data-v-59cd3fe9="" />
            <span className="hamburger-line hamburger-line--middle" data-v-59cd3fe9="" />
            <span className="hamburger-line hamburger-line--bottom" data-v-59cd3fe9="" />
          </div>
        </button>
        <ul className="navigation__list" data-v-59cd3fe9="" style={{ display: 'flex', width: '511px', maxWidth: '100%' }}>
          <li className="navigation__item" data-v-59cd3fe9="">
            <a className="navigation__link" data-v-59cd3fe9="" href="#wat-is-het">
              What is it?
            </a>
          </li>
          <li className="navigation__item" data-v-59cd3fe9="">
            <a className="navigation__link" data-v-59cd3fe9="" href="#tijdlijn">
              When?
            </a>
          </li>
          <li className="navigation__item" data-v-59cd3fe9="">
            <a className="navigation__link" data-v-59cd3fe9="" href="#veelgestelde-vragen">
              FAQ
            </a>
          </li>
          <li className="navigation__item" data-v-59cd3fe9="">
            <a className="navigation__link" data-v-59cd3fe9="" href="#psp-partners">
              Your PSP Partners
            </a>
          </li>
        </ul>
      </nav>
    </>
  );
}
