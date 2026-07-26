import { useState } from "react";

const reviews = [
  {
    name: "Mia R.",
    date: "JUN 2026",
    title: "De-puffed fast",
    body: "I wake up with puffy cheeks most mornings and this actually fixes it fast. I do light strokes up my neck and jaw for like a minute and my face looks way less swollen—under-eyes calm down too. No oil, no mess, just soft bristles and I’m out the door. It’s the first “de-puff” thing that stuck for me.",
    image: "/assets/images/Xhdx148AJQ.jpg",
    helpful: 36,
  },
  {
    name: "Emily S.",
    date: "JUN 2026",
    title: "Jawline showed up",
    body: "Did my neck to jaw and cheeks and boom, subtle lift. Way easier than oils or stones.",
    image: "/assets/images/mTExaddNnE.jpg",
    helpful: 28,
  },
  {
    name: "Morgan C.",
    date: "MAY 2026",
    title: "Morning reset",
    body: "I’ve tried stones and they were too hard for me, but this feels like a gentle massage. After a week of daily use, my under-eyes don’t balloon as much and my jawline looks a bit sharper. The case is clutch for keeping it clean in my bag. It’s the only step I never skip now.",
    image: null,
    helpful: 16,
  },
];

const moreReviews = [
  {
    name: "Nina G.",
    date: "APR 2026",
    title: "Soft but effective",
    body: "Bristles are crazy gentle but you still feel it working. No tugging, just glide and go",
    image: "/assets/images/OU8DVgCkg.jpg",
    helpful: 9,
  },
];

function Review({ review }) {
  return (
    <article className="review">
      <header>
        <h3>{review.name}</h3>
        <time>{review.date}</time>
      </header>
      <div className="review-stars" aria-label="Five stars">★★★★★</div>
      <div className="verified"><span>✿</span> Verified Buyer</div>
      <h4>{review.title}</h4>
      <p>{review.body}</p>
      {review.image && <img className="review-photo" src={review.image} alt="" />}
      <div className="review-product">
        <img src="/assets/images/1_bca3748e-966b-40f0-8399-0ea78958c8da_medium.png" alt="" />
        <span>Kojeva Lymphatic Face Brush</span>
        <span className="helpful">Was this helpful?　👍 {review.helpful}　👎 0</span>
      </div>
    </article>
  );
}

export default function AboutSection() {
  const [showMore, setShowMore] = useState(false);
  const visibleReviews = showMore ? [...reviews, ...moreReviews] : reviews;

  return (
    <section className={showMore ? "reviews-section expanded" : "reviews-section"} id="lmReview">
      <div className="reviews-summary">
        <h2>what our customers say about us</h2>
        <strong>4.9</strong>
        <div aria-label="4.9 stars">★★★★★</div>
        <p>Based on 3,598 Reviews</p>
      </div>
      <div className="reviews-list">
        {visibleReviews.map((review) => <Review review={review} key={review.name} />)}
      </div>
      <button className="load-more" type="button" onClick={() => setShowMore((value) => !value)}>
        {showMore ? "Show Less" : "Load More"}
      </button>
    </section>
  );
}
