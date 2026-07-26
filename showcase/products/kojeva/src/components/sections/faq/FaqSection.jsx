const faqs = [
  ["When will I see results?", <>Most people notice reduced puffiness <strong>almost instantly</strong>, with more defined contours and a radiant glow over consistent use.</>],
  ["What is the brush made of?", <>The Kojeva Lymphatic Facial Brush uses hypoallergenic, ultra-soft bristles that are gentle on skin yet firm enough to stimulate lymphatic flow. Kind to your skin and the planet.</>],
  ["How often should I use it?", <>We recommend using it daily, especially in the morning, to reduce puffiness and stimulate circulation.</>],
  ["Can I use it with oils or serums?", <>Absolutely! It works beautifully on dry skin or paired with your favorite facial oil or serum for added glide.</>],
];

export default function FaqSection() {
  return (
    <section className="faq-section">
      <h2>FAQs</h2>
      <div className="faq-list">
        {faqs.map(([question, answer]) => (
          <details key={question}>
            <summary>{question}</summary>
            <p>{answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
