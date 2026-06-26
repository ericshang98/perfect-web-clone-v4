import Scene from "./Scene.jsx";

const SOCIALS = [
  { label: "X", href: "https://x.com/lusionltd" },
  { label: "Instagram", href: "https://www.instagram.com/lusionltd" },
  { label: "Linkedin", href: "https://www.linkedin.com/company/lusionltd" },
];

const VARIANTS = ["ORYZO ONE", "ORYZO PRO", "ORYZO PRO MAX"];
const BULLETS = [
  "Single layer lift",
  "Natural cork insulation",
  "Stable grip on everyday surfaces",
];

export default function Outro() {
  return (
    <>
      {/* 13 — Choose your own (red-glow product hall) */}
      <Scene id="scene-13" align="items-center justify-center">
        {/* warm red bloom behind the ring — centred, edges stay near-black */}
        <div className="red-glow pointer-events-none absolute inset-0" />
        <div className="reveal relative mx-auto w-full max-w-[1100px] text-center">
          <h2 className="wordmark text-cream text-[clamp(3rem,12vw,12rem)] drop-shadow-[0_0_40px_rgba(192,52,31,0.45)]">
            ORYZO
          </h2>
          <p className="mt-4 font-mono text-[11px] uppercase tracking-[0.3em] text-[#ff5a3c]">
            Choose your own
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            {VARIANTS.map((v, i) => (
              <button
                key={v}
                className={`rounded-full px-6 py-2.5 font-mono text-[12px] uppercase tracking-[0.16em] transition-colors ${
                  i === 0
                    ? "bg-cream text-ink"
                    : "border border-cream/30 text-cream/80 hover:border-orange hover:text-cream"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
          <p className="mx-auto mt-8 max-w-[48ch] text-[clamp(0.95rem,1.2vw,1.2rem)] leading-snug text-cream/80">
            The original. Refined until it feels inevitable. Lifts just enough, grips
            just right, and quietly disappears into your day like it was never there.
          </p>
          <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 font-mono text-[11px] uppercase tracking-[0.14em] text-cream/55">
            {BULLETS.map((b) => (
              <li key={b} className="flex items-center gap-2">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-orange" />
                {b}
              </li>
            ))}
          </ul>
        </div>
      </Scene>

      {/* real footer */}
      <footer id="contact" className="relative z-10 bg-ink">
        {/* verbatim CTA */}
        <div className="px-[3.125vw] py-28 sm:py-40">
          <div className="mx-auto max-w-[1400px]">
            <h2 className="wordmark max-w-[28ch] text-cream text-[clamp(2rem,5vw,4.5rem)]">
              We caught your attention with a non-existent product. If we can sell a
              coaster, imagine what we can do for your brand.
            </h2>
            <a
              href="https://lusion.co/"
              target="_blank"
              rel="noreferrer"
              className="mt-12 inline-flex items-center gap-2 rounded-full bg-brown px-7 py-3 font-mono text-[13px] uppercase tracking-[0.16em] text-cream transition-colors hover:bg-orange"
            >
              lusion.co
            </a>
          </div>
        </div>

        {/* footer grid */}
        <div className="border-t border-cream/10 px-[3.125vw] py-16">
          <div className="mx-auto grid max-w-[1400px] gap-12 md:grid-cols-[1.4fr_1fr_1fr]">
            {/* newsletter */}
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cream/60">
                Subscribe to Lusion&rsquo;s Newsletter:
              </p>
              <form
                className="mt-4 flex max-w-sm items-center gap-2 border-b border-cream/30 pb-2"
                onSubmit={(e) => e.preventDefault()}
              >
                <input
                  type="email"
                  placeholder="Your email"
                  className="w-full bg-transparent text-cream placeholder:text-cream/40 focus:outline-none"
                />
                <button type="submit" aria-label="Subscribe" className="text-cream/70 hover:text-orange">
                  &rarr;
                </button>
              </form>
              <p className="mt-8 font-mono text-[11px] uppercase tracking-[0.18em] text-cream/40">
                Made in Lusion with love.
              </p>
            </div>

            {/* contact */}
            <div className="space-y-4 font-mono text-[12px] uppercase tracking-[0.12em] text-cream/70">
              <div>
                <span className="block text-cream/40">New Business:</span>
                <a href="mailto:business@lusion.co" className="hover:text-orange">
                  business@lusion.co
                </a>
              </div>
              <div>
                <span className="block text-cream/40">General Enquires:</span>
                <a href="mailto:hello@lusion.co" className="hover:text-orange">
                  hello@lusion.co
                </a>
              </div>
            </div>

            {/* socials + legal */}
            <div className="space-y-4 font-mono text-[12px] uppercase tracking-[0.12em] text-cream/70">
              <div className="flex flex-col gap-1">
                {SOCIALS.map((s) => (
                  <a key={s.label} href={s.href} target="_blank" rel="noreferrer" className="hover:text-orange">
                    {s.label}
                  </a>
                ))}
              </div>
              <div className="flex flex-col gap-1 pt-2">
                <a href="https://oryzo.ai/terms_and_conditions.pdf" className="hover:text-orange">
                  Terms &amp; Conditions
                </a>
                <a href="https://oryzo.ai/privacy_policy.pdf" className="hover:text-orange">
                  Privacy Policy
                </a>
              </div>
            </div>
          </div>

          {/* satire disclaimer */}
          <p className="mx-auto mt-16 max-w-[1400px] font-mono text-[11px] leading-relaxed text-cream/35">
            This entire site is a fictional creative project by Lusion. Oryzo
            doesn&rsquo;t exist. No products are for sale. All claims are satirical and
            for entertainment purposes only.
          </p>
        </div>
      </footer>
    </>
  );
}
