import React from 'react'
import {
  benefits,
  essentials,
  faqs,
  footerLinks,
  gallery,
  navigation,
  results,
  steps,
  ugcFrames,
} from './data'

const asset = (name) => `/assets/${name}`

function SaleBar() {
  return (
    <div className="sale-bar">
      <span>Summer Sale:</span>
      <div className="timer">
        <strong>10</strong><small>hrs</small>
      </div>
      <b>:</b>
      <div className="timer">
        <strong>59</strong><small>mins</small>
      </div>
      <b>:</b>
      <div className="timer">
        <strong>45</strong><small>secs</small>
      </div>
    </div>
  )
}

function Header() {
  return (
    <>
      <SaleBar />
      <header className="site-header">
        <nav aria-label="Primary navigation">
          {navigation.map(([label, href]) => <a key={label} href={href}>{label}</a>)}
        </nav>
        <a className="logo-link" href="https://livora.co/" aria-label="Livora home">
          <img src={asset('logo.png')} alt="LIVORA" />
        </a>
        <div className="header-icons">
          <a href="https://livora.co/customer_authentication/redirect?locale=en&region_country=US" aria-label="Log in" className="user-icon" />
          <a href="https://livora.co/cart" aria-label="Cart" className="bag-icon" />
        </div>
      </header>
    </>
  )
}

function BundleRow({ image, title, oldPrice, price, free }) {
  return (
    <div className="bundle-row">
      <div className="bundle-image-wrap">
        <img src={asset(image)} alt="" />
        {free && <span className="gift-tag">FREE</span>}
      </div>
      <div className="bundle-copy">
        <strong>{title}</strong>
        {title === 'SilkGlide Pro 2.0™' && <select aria-label="Color" defaultValue="Pink"><option>Pink</option></select>}
      </div>
      <span className="bundle-price"><del>{oldPrice}</del> <b>{price}</b></span>
    </div>
  )
}

function TrustBadges() {
  return (
    <div className="trust-badges">
      <div><img src={asset('badge-90.jpg')} alt="" /><strong>90 Day<br />Guarantee</strong></div>
      <div><img src={asset('badge-warranty.jpg')} alt="" /><strong>Lifetime<br />Warranty</strong></div>
      <div><img src={asset('badge-shipping.jpg')} alt="" /><strong>Expedited<br />Processing</strong></div>
    </div>
  )
}

function ProductSection() {
  return (
    <section className="product-section">
      <div className="product-layout page-width">
        <div className="gallery">
          <img className="hero-product" src={asset(gallery[0])} alt="SilkGlide Pro 2.0 in pink" />
          <div className="thumbnails">
            {gallery.map((image, index) => (
              <img key={image} className={index === 0 ? 'active' : ''} src={asset(image)} alt="" />
            ))}
          </div>
        </div>
        <div className="product-info">
          <div className="promo">
            <span>SUMMER SALE!</span>
            <strong>Up To 70% Off + Free Gifts!</strong>
            <small>While supplies last. Once it's gone, it's gone.</small>
          </div>
          <div className="rating"><span>★★★★★</span> Excellent 4.5 | <strong>990+ Reviews</strong></div>
          <h1>SilkGlide Pro 2.0™</h1>
          <p className="tagline">Effortlessly silky smooth. Anywhere. Everywhere.</p>
          <div className="price-line"><strong>$29.95</strong> <del>$99.95</del> <b>70% OFF</b></div>
          <div className="feature-grid">
            <span>◯ Smooth Shaving</span><span>♡ Painless</span>
            <span>◉ Fully Waterproof</span><span>⊙ Reduces Irritation</span>
          </div>
          <div className="bundle">
            <BundleRow image="essential-product.png" title="SilkGlide Pro 2.0™" oldPrice="$99.95" price="$29.95" />
            <i className="bundle-plus">+</i>
            <BundleRow image="bundle-face.png" title="FREE Facial Head" oldPrice="$30.00" price="FREE" free />
            <i className="bundle-plus">+</i>
            <BundleRow image="bundle-glove.png" title="FREE Exfoliation Glove" oldPrice="$20.00" price="FREE" free />
          </div>
          <p className="remaining">Only 5 SilkGlide Pro bundles left!</p>
          <div className="offer-note"><span className="refund-icon">↻</span><span>70% OFF first order. Try risk free for 90 days. Offer includes subscription blade refills.</span></div>
          <button className="add-button">ADD TO CART</button>
          <div className="stock"><b>● In stock</b> Ships by Sat, Jul 25</div>
          <div className="autopilot"><strong>Your shave and trim on autopilot.</strong><br />Enjoy a lifetime warranty – you'll never pay for a replacement. Receive 2 blades every 8 weeks for just $17.99 each. Your first refill ships after 6 weeks, and you can skip or cancel anytime.</div>
          <TrustBadges />
        </div>
      </div>
    </section>
  )
}

function StickyCart() {
  return (
    <div className="sticky-cart">
      <div className="sticky-inner">
        <img src={asset('essential-product.png')} alt="" />
        <div><strong>SilkGlide Pro 2.0™</strong><br /><b>$29.95</b> <del>$99.95</del></div>
        <select aria-label="Choose color" defaultValue="Pink"><option>Pink</option></select>
        <button>Add to cart</button>
      </div>
    </div>
  )
}

function BrandStrip() {
  return (
    <section className="brand-strip" aria-label="Featured publications">
      <span>Women'sHealth</span><span>COSMOPOLITAN</span><span>VOGUE</span>
      <span>allure</span><span>Women'sHealth</span><span>COSMOPOLITAN</span>
    </section>
  )
}

function Essentials() {
  return (
    <section className="essentials">
      <div className="page-width">
        <h2><span>Unveil the Essentials Inside</span><strong>SilkGlide Pro 2.0™</strong></h2>
        <p className="essentials-subtitle">Enjoy Free Premium Attachments Worth $50</p>
        <div className="essentials-grid">
          {essentials.map((item, index) => (
            <article key={item.title} className={index < 3 ? 'large-card' : 'small-card'}>
              {item.free && <span className="free-pill">FREE</span>}
              <img src={asset(item.image)} alt="" />
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function SocialProof() {
  return (
    <>
      <section className="trusted">
        <h2>Trusted by over <span>120,000+ women!</span></h2>
        <p>Women everywhere are throwing out their old razors and switching to SilkGlide Pro.</p>
      </section>
      <section className="ugc-section">
        <div className="ugc-row page-width">
          {ugcFrames.map((mediaId, index) => (
            <div className="ugc-card" key={mediaId}>
              <video
                muted
                loop
                playsInline
                preload="metadata"
                poster={asset(`ugc-${mediaId}.jpg`)}
                aria-label="SilkGlide Pro customer demonstration"
              >
                <source src={asset(`ugc-${mediaId}.mp4`)} type="video/mp4" />
              </video>
              {(index === 0 || index === 4) && <span className={index === 0 ? 'ugc-arrow left' : 'ugc-arrow right'}>{index === 0 ? '‹' : '›'}</span>}
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

function StepSection() {
  return (
    <section className="steps-section">
      <div className="steps-grid page-width">
        {steps.map((step, index) => (
          <article key={step.title}>
            <div className="step-image">
              <span>Step {index + 1}</span>
              <img src={asset(step.image)} alt="" />
            </div>
            <h3>{step.title}</h3>
            <p>{step.text}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

function Benefits() {
  return (
    <section className="benefits-section">
      <h2>Why Women Are Ditching Their Razors For The SilkGlide Pro</h2>
      <div className="benefits-grid">
        {benefits.map((item) => (
          <article key={item.title}>
            <img src={asset(item.image)} alt="" />
            <div><h3>{item.title}</h3><p>{item.text}</p></div>
          </article>
        ))}
      </div>
      <div className="carousel-buttons"><button aria-label="Previous">‹</button><button aria-label="Next">›</button></div>
    </section>
  )
}

function Comparison() {
  const rows = [
    ['No Ingrowns', '✓', 'ⓧ'],
    ['Shave Time', '90 Seconds', '5 to 30 Minutes'],
    ['Dry Shaving', '✓', 'ⓧ'],
    ['No Nicks', '✓', 'ⓧ'],
    ['Extra Attachments Included', '✓', 'ⓧ'],
    ['Lifetime Warranty', '✓', 'ⓧ'],
  ]
  return (
    <section className="comparison">
      <h2><span>Ditch the Razor.</span><strong>Upgrade Your Shave.</strong></h2>
      <div className="compare-grid">
        <div className="compare-head label">Smooth to Touch Shave</div>
        <div className="compare-head featured"><img src={asset('essential-product.png')} alt="" /><b>SilkGlide Pro</b></div>
        <div className="compare-head"><img src={asset('razor.png')} alt="" /><b>Razor</b></div>
        {rows.map(([label, silk, razor]) => (
          <div className="compare-row" key={label}>
            <div>{label}</div>
            <div className="featured">{silk === '✓' ? <i>✓</i> : silk}</div>
            <div>{razor}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

function Results() {
  return (
    <section className="results">
      <h2><span>Real Results.</span><strong>Backed by 120,000+ Customers.</strong></h2>
      <div className="results-grid">
        {results.map(([image, percentage, text]) => (
          <article key={percentage}>
            <div className="result-icon"><img src={asset(image)} alt="" /></div>
            <h3>{percentage}</h3>
            <p>{text}</p>
          </article>
        ))}
      </div>
      <p className="survey">BASED ON A RANDOMIZED SURVEY OF LIVORA CUSTOMERS CONDUCTED IN 2026</p>
    </section>
  )
}

function Guarantee() {
  return (
    <section className="guarantee">
      <div className="guarantee-cta">
        <h2>Still Not Convinced?<br /><strong>Try It Risk-Free Today.</strong></h2>
        <button>ADD TO CART</button>
        <p>100% money back guarantee</p>
      </div>
      <div className="guarantee-list">
        <article><img src={asset('guarantee-90.png')} alt="" /><div><h3>90 Day Money Back Guarantee</h3><p>Not loving your results? Return within 90 days for a full refund.</p></div></article>
        <article><img src={asset('guarantee-life.png')} alt="" /><div><h3>Lifetime Warranty</h3><p>Your SilkGlide Pro is covered for life as long as you maintain an active refill plan.</p></div></article>
      </div>
    </section>
  )
}

function Faq() {
  return (
    <section className="faq">
      <div className="faq-inner">
        <h2>FAQ</h2>
        {faqs.map(([question, answer]) => (
          <details key={question}>
            <summary>{question}</summary>
            <p>{answer}</p>
          </details>
        ))}
      </div>
    </section>
  )
}

function Footer() {
  return (
    <>
      <footer className="footer">
        <div className="footer-inner">
          <div>
            <h2>Quick links</h2>
            {footerLinks.map(([label, href]) => <a key={label} href={href}>{label}</a>)}
          </div>
          <div className="subscribe">
            <h2>Subscribe to our emails</h2>
            <p>Join our email list for exclusive offers and<br />the latest news.</p>
            <label><span className="sr-only">Email</span><input type="email" placeholder="Email" /></label>
            <button>Sign up</button>
          </div>
        </div>
      </footer>
      <section className="disclaimer">
        <div className="payments" aria-label="Accepted payment methods">
          <span>amazon</span><span>AMEX</span><span>Pay</span><span>◐</span><span>DISC</span><span>G Pay</span><span>●</span><span>shop</span><span>VISA</span>
        </div>
        <p className="copyright">© 2026, Livora</p>
        <h2>General Disclaimer</h2>
        <p>The information provided on this website is for educational and cosmetic purposes only. Our products are<br />formulated to support the look and feel of healthy skin and are not intended to diagnose, treat, cure, or<br />prevent any medical condition. Individual results may vary. Always perform a patch test before first use<br />and consult your healthcare provider if you have any specific concerns or sensitivities.</p>
      </section>
    </>
  )
}

export default function App() {
  return (
    <>
      <Header />
      <main>
        <ProductSection />
        <BrandStrip />
        <Essentials />
        <SocialProof />
        <StepSection />
        <Benefits />
        <Comparison />
        <Results />
        <Guarantee />
        <div className="source-spacer" aria-hidden="true" />
        <Faq />
      </main>
      <Footer />
      <StickyCart />
    </>
  )
}
