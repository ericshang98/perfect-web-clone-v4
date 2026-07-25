import { asset, footerLinks } from '../../../data.js'

export default function FooterSection() {
  return (
    <footer className="site-footer">
      <div className="site-footer__inner">
        <div className="footer-columns">
          <section>
            <h2>Quick links</h2>
            <ul>
              {footerLinks.map(([label, href]) => (
                <li key={href}><a href={href}>{label}</a></li>
              ))}
            </ul>
          </section>

          <section>
            <h2>Store Information</h2>
            <p>Customer Support : 9:00 am to 5:00 pm</p>
            <p>Email: help@linfaeshop.com</p>
          </section>

          <section>
            <h2>Subscribe to our emails</h2>
            <form className="subscribe-form" action="https://trykojiva.com/" method="get">
              <label className="visually-hidden" htmlFor="footer-email">Email</label>
              <input id="footer-email" name="email" placeholder="Email" type="email" />
              <button type="submit" aria-label="Subscribe">✉</button>
            </form>
          </section>
        </div>

        <div className="footer-bottom">
          <p>
            © 2026, <a href="https://trykojiva.com/">Linfae</a>
            <span> | GROUP J S TRAVEL LLC</span>
            <small>407 LINCOLN RD STE, MIAMI BEACH FL 33139</small>
          </p>
          <img src={asset('iREiPEhXkQPmILks.png')} alt="Linfae" />
        </div>
      </div>
    </footer>
  )
}
