const customerImages = [
  "/assets/images/Screenshot_2025-10-22_at_11.04.07_PM.png",
  "/assets/images/Screenshot_2025-10-22_at_11.03.27_PM.png",
  "/assets/images/Screenshot_2025-10-22_at_11.01.59_PM.png",
  "/assets/images/Screenshot_2025-10-22_at_11.04.07_PM.png",
];

export default function ProductSection() {
  return (
    <section className="social-strip">
      <div className="social-copy">
        <h2>Look At How<br />Others Are<br />Loving Their<br />Product!</h2>
        <p>Real Reviews From Real People</p>
        <a href="https://kojeva.com/products/kojeva-lymphatic-face-brush">CLAIM OFFER</a>
        <div><span>★★★★★</span> Rated 4.8/5 by 3,000+</div>
      </div>
      <div className="customer-gallery">
        {customerImages.map((src, index) => (
          <img src={src} alt={`Customer using the Kojeva brush ${index + 1}`} key={`${src}-${index}`} />
        ))}
      </div>
    </section>
  );
}
