// AboutSection (id=q-and-a) — "CURIOUS ABOUT THE MOVE FROM iDEAL TO WERO?"
// The real site ships this as a frozen Plyr player (renders as a black block
// statically). Rebuilt clean/data-driven: 3 real <video> with local posters +
// the captured mp4 sources. Heading class names are styled by public/theme.css.
const VIDEOS = [
  { poster: "/assets/images/video-01-poster.jpg", src: "https://sowieso-wero-assets.s3.eu-central-1.amazonaws.com/videos/q-and-a-en.mp4", label: "Wero Q&A" },
  { poster: "/assets/images/video-02-poster.jpg", src: "https://sowieso-wero-assets.s3.eu-central-1.amazonaws.com/videos/aankoopbescherming-en.mp4", label: "Purchase protection" },
  { poster: "/assets/images/video-03-poster.jpg", src: "https://sowieso-wero-assets.s3.eu-central-1.amazonaws.com/videos/transactiekosten-en.mp4", label: "Pricing" },
];

export default function AboutSection() {
  return (
    <section className="video-section py-24" id="q-and-a">
      <div className="video-section__title-container">
        <p className="video-section__top-title">Our Wero Q&amp;A Series</p>
        <h2 className="video-section__title">CURIOUS ABOUT THE<br />MOVE FROM iDEAL<br />TO WERO?</h2>
      </div>
      <p className="mx-auto max-w-2xl px-4 text-center text-lg">
        Our expert breaks it down in this short interview, clear, simple, and everything
        you need to know about the transition.
      </p>
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-14 md:grid-cols-3">
        {VIDEOS.map((v) => (
          <video
            key={v.src}
            controls
            playsInline
            preload="none"
            poster={v.poster}
            aria-label={v.label}
            className="w-full rounded-xl bg-black shadow-md"
          >
            <source src={v.src} type="video/mp4" />
          </video>
        ))}
      </div>
      <p className="mx-auto max-w-2xl px-4 pb-6 text-center text-lg">
        Got more questions? We’ve got you covered! Dive into our videos on purchase
        protection and pricing.
      </p>
    </section>
  );
}
