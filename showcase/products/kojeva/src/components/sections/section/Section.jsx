import { useState } from "react";

const gallery = [
  {
    full: "/assets/images/1_bca3748e-966b-40f0-8399-0ea78958c8da-11.png",
    thumb: "/assets/images/1_bca3748e-966b-40f0-8399-0ea78958c8da-18.png",
    alt: "Kojeva brush and travel case",
  },
  {
    full: "/assets/images/2_371970f3-929d-414b-bebc-fe63be488818-11.png",
    thumb: "/assets/images/2_371970f3-929d-414b-bebc-fe63be488818-18.png",
    alt: "Kojeva brush benefits",
  },
  {
    full: "/assets/images/3_f20000e3-fe33-4067-a89e-2532953f8656-11.png",
    thumb: "/assets/images/3_f20000e3-fe33-4067-a89e-2532953f8656-18.png",
    alt: "Before and after",
  },
  {
    full: "/assets/images/4_cd640566-6756-4694-a4ad-55029080a1f0-11.png",
    thumb: "/assets/images/4_cd640566-6756-4694-a4ad-55029080a1f0-18.png",
    alt: "How to use Kojeva brush",
  },
];

const offers = [
  { name: "Single", save: "SAVE $33.00", price: "$22.99", old: "$66.00" },
  { name: "Duo", save: "SAVE $74.99", price: "$33.99", old: "$132.00", badge: "Most Popular" },
  { name: "Trio", save: "SAVE $99.98", price: "$65.99", old: "$198.00", badge: "Best Value", note: "Free Shipping Included" },
];

const accordionItems = [
  {
    label: "Is this right for you?",
    content: (
      <>
        <ul>
          <li>Gua sha feels too harsh or time-consuming</li>
          <li>Morning puffiness or a “tired” look?</li>
          <li>Jaw/temple tension you want to calm</li>
          <li>Under-eye swelling you’d like to de-puff</li>
          <li>Prefer a quick, no-mess A.M. ritual (90 seconds)</li>
          <li>Want product-free brushing (no oils/serums)</li>
          <li>Sensitive skin that needs ultra-soft bristles</li>
        </ul>
        <p>If you nodded yes, try Lymphatic Face Brush for 30 days.</p>
      </>
    ),
  },
  {
    label: "What is the brush made of?",
    content: (
      <p>The Kojeva Lymphatic Facial Brush uses hypoallergenic, ultra-soft bristles that are gentle on skin yet firm enough to stimulate lymphatic flow. Kind to your skin and the planet.</p>
    ),
  },
  {
    label: "How do I clean it?",
    content: (
      <>
        <p>To clean, apply the Kojeva Brush Cleanser directly to the bristles and massage gently. Rinse thoroughly with water and let air-dry in a well-ventilated area to maintain maximum hygiene and brush life.</p>
        <p>Tip: Avoid harsh detergents or soaking the wooden handle, as this may cause damage.</p>
      </>
    ),
  },
  {
    label: "Use Cases",
    content: (
      <>
        <p>Target These 5 Drainage Zones:</p>
        <ul>
          <li>Jawline &amp; Chin: Brush upward from under chin to ears along the jaw.</li>
          <li>Cheeks: Sweep upward from mouth corners to temples.</li>
          <li>Under-Eyes: Lightly brush from inner corner to temple.</li>
          <li>Forehead: Brush upward from brows to hairline.</li>
          <li>Neck: Brush upward from the base of the neck to the jaw.</li>
        </ul>
      </>
    ),
  },
  {
    label: "How to Use (Quick)",
    content: (
      <ol>
        <li>Start on clean, dry skin (no products).</li>
        <li>Brush upward : neck to jaw, cheeks to temples, under-eyes (very light), forehead up.</li>
        <li>Use feather-light pressure —let the bristles glide.</li>
        <li>90 seconds total.</li>
        <li>Apply skincare after to boost absorption.</li>
        <li>Use every morning (and anytime you feel puffy or tense).</li>
        <li>No oils needed.</li>
      </ol>
    ),
  },
];

export default function Section() {
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedOffer, setSelectedOffer] = useState(1);

  return (
    <section className="product-hero" id="product-information">
      <a className="skip-product" href="#product-information">Skip to product information</a>
      <div className="product-shell">
        <div className="thumbnail-list" aria-label="Product gallery">
          {gallery.map((image, index) => (
            <button
              className={selectedImage === index ? "thumbnail active" : "thumbnail"}
              type="button"
              key={image.full}
              onClick={() => setSelectedImage(index)}
              aria-label={`Show image ${index + 1}`}
            >
              <img src={image.thumb} alt="" />
            </button>
          ))}
        </div>
        <div className="main-product-image">
          <img src={gallery[selectedImage].full} alt={gallery[selectedImage].alt} />
        </div>
        <div className="product-copy" id="product-details">
          <a href="https://kojeva.com/products/kojeva-lymphatic-face-brush"><h1>Kojeva Lymphatic<br />Face Brush</h1></a>
          <a className="rating-line" href="#lmReview">
            <span aria-label="Five stars">★★★★★</span> 4.8/5 Stars (3,000+ Reviews)
          </a>
          <div className="exclusive"><b>★</b> Exclusively available on Kojeva</div>
          <ul className="benefit-list">
            <li>Reduces Puffiness &amp; Sculpts Jawline<br />in Minutes</li>
            <li>Safe for Sensitive &amp; Mature Skin</li>
            <li>No Messy Oils or Serums Needed</li>
          </ul>
          <div className="bundle-title"><span />BUNDLE &amp; SAVE<span /></div>
          <div className="offer-list">
            {offers.map((offer, index) => (
              <button
                key={offer.name}
                className={selectedOffer === index ? "offer-card selected" : "offer-card"}
                type="button"
                onClick={() => setSelectedOffer(index)}
              >
                {offer.badge && <em>{offer.badge}</em>}
                <i aria-hidden="true" />
                <span className="offer-name">{offer.name}<small>{offer.note}</small></span>
                <span className="save">{offer.save}</span>
                <span className="offer-price">{offer.price}<del>{offer.old}</del></span>
              </button>
            ))}
          </div>
          <button className="add-button" type="button">Add to cart</button>
          <div className="stock-warning">
            <strong><span aria-hidden="true">!</span> WARNING: Low Stock<br />Notice</strong>
            <p>This product sold out <b>12 times</b> last year. We encourage you to take advantage of the <b>limited sale</b> and buy now.</p>
            <p><b>PS:</b> Only available here, don't buy fakes on Amazon/eBay.</p>
          </div>
          <div className="product-accordions">
            {accordionItems.map((item) => (
              <details key={item.label}>
                <summary>{item.label}</summary>
                <div className="accordion-answer">{item.content}</div>
              </details>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
