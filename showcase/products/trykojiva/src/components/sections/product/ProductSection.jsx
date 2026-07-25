import { useState } from 'react'
import { CheckIcon, Stars } from '../../Icons.jsx'
import {
  asset,
  benefits,
  faqs,
  galleryImages,
  gifts,
  mediaLogos,
  productDetails,
  purchasePlans,
  resultStats,
  socialImages,
} from '../../../data.js'

function ProductGallery() {
  const [activeImage, setActiveImage] = useState(0)

  return (
    <div className="product-gallery">
      <div className="product-thumbnails" aria-label="Product images">
        {galleryImages.map(([image, alt], index) => (
          <button
            className={activeImage === index ? 'thumbnail thumbnail--active' : 'thumbnail'}
            key={image}
            type="button"
            aria-label={`Show product image ${index + 1}`}
            aria-pressed={activeImage === index}
            onClick={() => setActiveImage(index)}
          >
            <img src={asset(image)} alt={alt} loading={index === 0 ? 'eager' : 'lazy'} />
          </button>
        ))}
      </div>
      <div className="product-gallery__stage">
        <img
          src={asset(galleryImages[activeImage][0])}
          alt={galleryImages[activeImage][1]}
          fetchPriority="high"
        />
      </div>
    </div>
  )
}

function PurchasePlan({ plan, selected, onSelect }) {
  return (
    <button
      className={selected ? 'purchase-plan purchase-plan--selected' : 'purchase-plan'}
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
    >
      {plan.badge && <span className="purchase-plan__badge">{plan.badge}</span>}
      <span className="radio"><span /></span>
      <span className="purchase-plan__name">
        <strong>{plan.name}</strong>
        {plan.saving && <small>{plan.saving}</small>}
        {plan.gift && <em>{plan.gift}</em>}
      </span>
      <span className="purchase-plan__price">
        <strong>{plan.price}</strong>
        <del>{plan.compareAt}</del>
      </span>
    </button>
  )
}

function GiftCard({ gift }) {
  return (
    <article className={gift.locked ? 'gift-card gift-card--locked' : 'gift-card'}>
      <span className="gift-card__value">{gift.value}</span>
      <div className="gift-card__visual">
        {gift.image ? (
          <img src={asset(gift.image)} alt={gift.label} loading="lazy" />
        ) : (
          <span className="locked-gift" aria-hidden="true">♙<small>Locked</small></span>
        )}
      </div>
      <strong>{gift.label}</strong>
    </article>
  )
}

function ProductDetails() {
  return (
    <div className="product-details">
      {productDetails.map(([title, text]) => (
        <details key={title}>
          <summary>{title}<span aria-hidden="true">+</span></summary>
          <p>{text}</p>
        </details>
      ))}
    </div>
  )
}

function ProductInfo() {
  const [selectedPlan, setSelectedPlan] = useState(1)
  const [cartMessage, setCartMessage] = useState('')

  return (
    <div className="product-info">
      <div className="expert-line">
        <span className="expert-avatar">
          <img src={asset('JmacTtwXjCYPoWBE.jpeg')} alt="Melissa K. Lerm" />
          <span aria-hidden="true">✓</span>
        </span>
        <p>Recommended by <strong>Melissa K. Lerm</strong><i>|</i>Esthetician</p>
        <span aria-label="Korea">🇰🇷</span>
      </div>

      <h1>Linfae Lymphatic Face Brush</h1>
      <div className="product-rating">
        <Stars />
        <span>4.8/5 Stars (3,000+ Reviews)</span>
      </div>

      <div className="featured-review">
        <img src={asset('Screenshot_2025-12-07_021109.png')} alt="Jessica M., CA" />
        <div>
          <p>Puffiness gone in week one. Hubby noticed without me saying a word.</p>
          <small>Jessica M., CA</small>
        </div>
      </div>
      <div className="review-dots" aria-label="Featured review 1 of 3">
        <button type="button" aria-label="Previous review">‹</button>
        <span className="active" />
        <span />
        <span />
        <button type="button" aria-label="Next review">›</button>
      </div>
      <p className="fluid-callout">
        Your double chin isn't fat — <em>it's trapped fluid.</em>
        <small>This brush drains it in <strong>3 minutes.</strong></small>
      </p>

      <div className="divider-title" id="product-plans"><span />Buy More, Save More<span /></div>
      <div className="purchase-plans">
        {purchasePlans.map((plan, index) => (
          <PurchasePlan
            key={plan.name}
            plan={plan}
            selected={selectedPlan === index}
            onSelect={() => setSelectedPlan(index)}
          />
        ))}
      </div>

      <section className="gift-offer" aria-labelledby="gift-title">
        <h2 id="gift-title">🎁 Free Gifts If You Order Now</h2>
        <div className="gift-grid">
          {gifts.map((gift) => <GiftCard gift={gift} key={gift.label} />)}
        </div>
        <p>Order Within <strong>09:52</strong> To Claim Your FREE Gifts</p>
      </section>

      <button
        className="add-to-cart"
        type="button"
        onClick={() => setCartMessage(`${purchasePlans[selectedPlan].name} selected`)}
      >
        Add to Cart
      </button>
      <p className="visually-hidden" aria-live="polite">{cartMessage}</p>

      <div className="community-proof">
        <span>
          <img src={asset('Screenshot_2025-12-07_021039.png')} alt="Jade" />
          <img src={asset('Screenshot_2025-12-07_021056.png')} alt="Emma" />
        </span>
        <p><strong>Jade, Emma <b>●</b></strong>and 57,000+ love our Korean skincare products</p>
      </div>

      <ProductDetails />

      <article className="expert-card">
        <img src={asset('pasted_file_wyOk0n_image_6e5c9348.webp')} alt="Melissa K. Lerm, Esthetician" />
        <div>
          <h2>Melissa K. Lerm, Esthetician: Why The K Glow Brush Works</h2>
          <p>“The K Glow Brush works because it addresses the real problem, stagnant face fluids. The textured bristles physically move that buildup out, which is why you see instant sculpting. Daily use trains your system to drain efficiently on its own.”</p>
          <strong>Melissa K. Lerm, Esthetician</strong>
        </div>
      </article>
    </div>
  )
}

function MediaStrip() {
  const logos = [...mediaLogos, ...mediaLogos, ...mediaLogos]
  return (
    <section className="media-strip" aria-label="Press mentions">
      <p>As seen on</p>
      <div>
        {logos.map((logo, index) => (
          <img src={asset(logo)} alt="" aria-hidden="true" key={`${logo}-${index}`} />
        ))}
      </div>
    </section>
  )
}

function BenefitsSection() {
  return (
    <section className="benefits-section">
      <div className="benefits-section__inner">
        <div className="benefit-copy">
          <h2>Give your face the secret<br />boost it's been waiting for.</h2>
          <p>How the K Glow™ Brush helps you:</p>
          <ul>
            {benefits.map((benefit) => (
              <li key={benefit}><CheckIcon />{benefit}</li>
            ))}
          </ul>
          <blockquote>"I've tried every face roller and tool out there, so I know what actually works. This isn't the same. The textured bristles genuinely drain fluid—my face looks sculpted, not puffy. I use it for 3 minutes every morning."</blockquote>
          <p className="verified"><span>●</span> VERIFIED BUYER</p>
          <a className="black-button" href="#product-plans">GET YOURS NOW!</a>
        </div>
        <figure className="comparison">
          <img src={asset('Untitled_design_19.png')} alt="After using the Linfae brush" />
          <span className="comparison__before">
            <img src={asset('Untitled_design_18.png')} alt="Before using the Linfae brush" />
          </span>
          <figcaption><span>Before</span><span>After</span></figcaption>
          <i aria-hidden="true">↔</i>
        </figure>
      </div>
    </section>
  )
}

function TrustBar() {
  return (
    <div className="trust-bar">
      <span>♣ <strong>CRUELTY-<br />FREE</strong></span>
      <span>♧ <strong>SUITABLE FOR<br />SENSITIVE SKIN</strong></span>
      <span>♙ <strong>NO HARSH<br />CHEMICALS</strong></span>
    </div>
  )
}

function ResultsSection() {
  return (
    <section className="results-section">
      <h2>57,000+ people have discovered their best routine yet.</h2>
      <p>The confidence that comes from healthy, radiant skin at every age.</p>
      <div className="social-gallery">
        {socialImages.map((image, index) => (
          <img src={asset(image)} alt={`Linfae customer ${index + 1}`} loading="eager" key={image} />
        ))}
      </div>
      <p className="loved-card">Loved by <strong>57,000+</strong> people around the world</p>
      <div className="result-stats">
        {resultStats.map(([percent, text]) => (
          <div className="result-stat" key={percent}>
            <span style={{ '--percent': percent }}>{percent}%</span>
            <p>{text}</p>
          </div>
        ))}
        <small>Results based on 200 customers actively using this product.</small>
      </div>
    </section>
  )
}

function NumberStrip() {
  return (
    <section className="number-strip" aria-label="Linfae customer statistics">
      <p><strong>57K+</strong><span>Customers</span></p>
      <p><strong>120K+</strong><span>Skincare Sold</span></p>
      <p><strong>1.1K</strong><span>5 Star Ratings</span></p>
    </section>
  )
}

function GuaranteeSection() {
  return (
    <section className="guarantee-section">
      <div>
        <h2>30 DAY MONEY-BACK GUARANTEE</h2>
        <p>We're so confident the Linfae Brush will reduce your double chin and sculpt your jawline that we'll give you 30 days to try it risk-free.</p>
        <blockquote>If you don't see a sharper, more defined face—send it back for a full refund.</blockquote>
        <img src={asset('brush_top_view_kglow_d596118e.webp')} alt="Linfae Brush" loading="eager" />
        <a className="black-button" href="#product-plans">GET YOURS NOW!</a>
      </div>
    </section>
  )
}

function FaqSection() {
  return (
    <section className="faq-section">
      <div>
        <h2>Frequently Asked Questions</h2>
        {faqs.map(([question, answer]) => (
          <details key={question}>
            <summary>{question}<span aria-hidden="true">+</span></summary>
            <p>{answer}</p>
          </details>
        ))}
        <a className="black-button black-button--pill" href="#product-plans">GET OFFER</a>
      </div>
    </section>
  )
}

export default function ProductSection() {
  return (
    <main>
      <section className="product-section">
        <div className="product-section__inner">
          <ProductGallery />
          <ProductInfo />
        </div>
      </section>
      <MediaStrip />
      <section className="reasons-section">
        <img
          src={asset('171d8e10-6f5c-4f74-b3cd-4be804982429_2e3d0341.webp')}
          alt="5 Reasons The K Glow Brush Transforms Your Face"
          loading="eager"
        />
      </section>
      <BenefitsSection />
      <TrustBar />
      <ResultsSection />
      <NumberStrip />
      <GuaranteeSection />
      <FaqSection />
    </main>
  )
}
