const features = [
  ["De-Puff & Define", "Visibly reduces morning swelling so cheekbones and jawline look more sculpted."],
  ["Soothe Jaw Tension", "Light strokes relax tight areas around jaw and temples—face looks less “held.”"],
  ["Ultra-Soft, Product-Free", "Plush bristles glide on dry skin; use before skincare to boost absorption."],
  ["Fast A.M. Ritual", "90 seconds, neck → jaw → cheeks → under-eyes → forehead"],
];

export default function Section2Section() {
  return (
    <section className="feature-section">
      <div className="feature-inner">
        <div className="feature-copy">
          <h2>Instant <span>Face De-Puff</span></h2>
          <p className="feature-lede">Brush-on lymphatic drainage for a fresher, lifted look—in ~90 seconds. Ultra-soft bristles guide fluid upward and outward; no oils needed.</p>
          <div className="feature-card">
            {features.map(([title, body]) => (
              <div className="feature-item" key={title}>
                <span aria-hidden="true">✿</span>
                <div><h3>{title}</h3><p>{body}</p></div>
              </div>
            ))}
          </div>
        </div>
        <img className="feature-image" src="/assets/images/Lymphatic_Brush.png" alt="Kojeva brush held in a hand" />
      </div>
    </section>
  );
}
