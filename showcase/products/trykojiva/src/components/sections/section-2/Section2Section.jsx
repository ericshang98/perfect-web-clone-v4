import { Stars } from '../../Icons.jsx'
import {
  asset,
  ratingBreakdown,
  resultImages,
  reviews,
} from '../../../data.js'

function RatingSummary() {
  return (
    <div className="rating-summary">
      <div className="rating-summary__score">
        <strong>4.8</strong>
        <span>/5</span>
        <Stars />
        <small>Based on 1,198 Reviews</small>
      </div>
      <div className="rating-bars">
        {ratingBreakdown.map(([stars, count, percentage]) => (
          <div key={stars}>
            <span>{stars}★</span>
            <i><b style={{ width: `${percentage}%` }} /></i>
            <small>{count}</small>
          </div>
        ))}
      </div>
    </div>
  )
}

function ReviewCard({ review }) {
  const facts = [
    ['Age', review.age],
    ['Skin type', review.skin],
    ['Skin concerns', review.concern],
    ['Recommends?', 'Yes'],
  ]

  return (
    <article className="review-card">
      <header>
        <span className="review-card__initials">{review.initials}</span>
        <p><strong>{review.name}</strong><small>✓ Verified Buyer</small></p>
        <time>{review.date}</time>
      </header>
      <Stars count={review.stars} />
      <dl>
        {facts.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <h3>{review.title}</h3>
      <p>{review.text}</p>
    </article>
  )
}

export default function Section2Section() {
  return (
    <section className="reviews-section" aria-labelledby="customer-results-title">
      <div className="reviews-section__inner">
        <RatingSummary />

        <h2 id="customer-results-title">Real Results From Real Customers</h2>
        <div className="result-image-grid">
          {resultImages.map((image, index) => (
            <img
              src={asset(image)}
              alt={`Before and after result ${index + 1}`}
              loading="eager"
              key={image}
            />
          ))}
        </div>

        <div className="review-grid">
          {reviews.map((review) => <ReviewCard review={review} key={review.name} />)}
        </div>

        <div className="reviews-cta">
          <p>Ready to transform your face?</p>
          <a href="#product-plans">GET OFFER</a>
        </div>
      </div>
    </section>
  )
}
