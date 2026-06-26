const base = import.meta.env.BASE_URL;

// The original site renders these product "scenes" in a pinned WebGL scroll
// sequence. Here they are localized stills, presented as a marquee + grid.
const SCENES = [
  { src: "bikini.webp", label: "On the beach" },
  { src: "glasses-1.webp", label: "On your face" },
  { src: "pocket-1.webp", label: "In your pocket" },
  { src: "shoulder-1.webp", label: "On your shoulder" },
  { src: "yoga.webp", label: "On the mat" },
];

const MARQUEE = [...SCENES, ...SCENES];

export default function Showcase() {
  return (
    <section id="showcase" className="relative bg-ink py-24 sm:py-32">
      <div className="px-[3.125vw]">
        <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
          Features
        </p>
        <h2 className="wordmark mt-4 max-w-[20ch] text-cream text-[clamp(2.2rem,5.5vw,5rem)]">
          Designed to lift, insulate, and grip in all the right ways.
        </h2>
        <p className="mt-5 max-w-[44ch] text-[clamp(0.95rem,1.1vw,1.15rem)] leading-snug text-cream/70">
          The world&rsquo;s most unnecessarily sophisticated cork coaster.
        </p>
      </div>

      {/* infinite marquee of product stills */}
      <div className="relative mt-16 overflow-hidden py-2">
        <div className="marquee-track flex w-max gap-6">
          {MARQUEE.map((s, i) => (
            <figure
              key={i}
              className="relative h-[clamp(18rem,30vw,30rem)] w-[clamp(13rem,22vw,22rem)] shrink-0 overflow-hidden rounded-xl bg-brown"
            >
              <img
                src={`${base}assets/images/${s.src}`}
                alt={`Oryzo coaster — ${s.label}`}
                loading="lazy"
                className="h-full w-full object-cover"
              />
              <figcaption className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-ink/80 to-transparent p-4 font-mono text-[11px] uppercase tracking-[0.18em] text-cream">
                {s.label}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
