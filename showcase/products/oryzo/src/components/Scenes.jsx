import Scene from "./Scene.jsx";

const base = import.meta.env.BASE_URL;
const img = (f) => `${base}assets/images/${f}`;

const shadow = "drop-shadow-[0_2px_24px_rgba(0,0,0,0.6)]";

// Scenes 01..12 of the choreography. The gold ring travels behind every panel
// (fixed canvas); these supply the headlines, eyebrows and localized stills.
export default function Scenes() {
  return (
    <>
      {/* 01 — Powered by AI */}
      <Scene id="scene-01" align="items-center">
        <div className="reveal w-full">
          <div className="mx-auto max-w-[1400px]">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              ORYZO-1
            </p>
            <h2 className={`wordmark mt-4 text-cream text-[clamp(3rem,11vw,11rem)] ${shadow}`}>
              Powered by AI
            </h2>
            <p className="mt-6 font-mono text-[11px] uppercase tracking-[0.18em] text-cream/55">
              <sup>1</sup> Adobe Illustrator
            </p>
          </div>
        </div>
      </Scene>

      {/* 02 — So portable (targeting reticle) */}
      <Scene id="scene-02" align="items-center justify-center">
        <div className="reveal relative flex w-full items-center justify-center">
          {/* technical framing reticle */}
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[42vmin] w-[42vmin] -translate-x-1/2 -translate-y-1/2">
            <span className="absolute inset-0 border border-cream/25" />
            <span className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-cream/15" />
            <span className="absolute top-1/2 left-0 w-full h-px -translate-y-1/2 bg-cream/15" />
            {["top-0 left-0", "top-0 right-0", "bottom-0 left-0", "bottom-0 right-0"].map((c) => (
              <span key={c} className={`absolute ${c} h-4 w-4 border border-orange`} />
            ))}
          </div>
          <h2 className={`relative wordmark text-center text-cream text-[clamp(2.4rem,9vw,9rem)] ${shadow}`}>
            SO PORTABLE,
          </h2>
          <p className="absolute bottom-[6vh] left-1/2 -translate-x-1/2 font-mono text-[10px] uppercase tracking-[0.3em] text-cream/55">
            Scroll to continue
          </p>
        </div>
      </Scene>

      {/* 03 — Wearable (jacket) */}
      <Scene id="scene-03" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1400px] items-center gap-10 md:grid-cols-[1.3fr_1fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              So portable,
            </p>
            <h2 className={`wordmark mt-3 text-cream text-[clamp(2.6rem,8vw,8rem)] ${shadow}`}>
              it&rsquo;s wearable
            </h2>
            <div className="mt-8 inline-block rounded-lg border border-cream/15 bg-ink/60 px-4 py-3 font-mono text-[11px] uppercase tracking-[0.14em] text-cream/80 backdrop-blur">
              Chest-pocket fit · 45&deg; reveal
            </div>
          </div>
          <div className="relative h-[clamp(16rem,34vw,30rem)] overflow-hidden rounded-2xl border border-cream/10 bg-brown/40">
            <img src={img("pocket-1.webp")} alt="Worn in a chest pocket" loading="lazy" className="h-full w-full object-cover opacity-95" />
            <div className="absolute right-3 top-3 flex gap-2">
              <img src={img("yoga.webp")} alt="" className="h-12 w-12 rounded object-cover ring-1 ring-cream/20" />
              <img src={img("shoulder-1.webp")} alt="" className="h-12 w-12 rounded object-cover ring-1 ring-cream/20" />
            </div>
          </div>
        </div>
      </Scene>

      {/* 04 — Wearable (red knit) */}
      <Scene id="scene-04" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1400px] items-center gap-10 md:grid-cols-[1fr_1.3fr]">
          <div className="order-2 md:order-1 flex gap-3">
            <img src={img("bite.webp")} alt="Biting the coaster" loading="lazy" className="h-32 w-24 rounded-lg object-cover ring-1 ring-cream/15" />
            <img src={img("glasses-1.webp")} alt="" loading="lazy" className="h-32 w-24 rounded-lg object-cover ring-1 ring-cream/15" />
          </div>
          <div className="order-1 md:order-2 text-right">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              So portable,
            </p>
            <h2 className={`wordmark mt-3 text-cream text-[clamp(2.6rem,8vw,8rem)] ${shadow}`}>
              it&rsquo;s wearable
            </h2>
            <div className="mt-6 inline-block rounded-md bg-orange/90 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.2em] text-cream">
              RISE — issue 01
            </div>
          </div>
        </div>
      </Scene>

      {/* 05 — Elevate your coffee experience */}
      <Scene id="scene-05" align="items-center">
        <div className="reveal mx-auto w-full max-w-[1100px]">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-green">
            Rise above mediocrity
          </p>
          <h2 className="wordmark mt-4 max-w-[18ch] text-ink text-[clamp(2.4rem,7vw,7rem)]">
            Elevate your coffee experience
          </h2>
          <p className="mt-6 max-w-[52ch] text-[clamp(1rem,1.3vw,1.35rem)] leading-snug text-ink/80">
            With a precision-engineered fit (exactly one coaster thick), Oryzo
            doesn&rsquo;t just hold your mug &mdash; it elevates it. Literally.
          </p>
          <p className="mt-6 font-mono text-[11px] uppercase tracking-[0.18em] text-ink/50">
            Constant fill via geometry &nbsp;·&nbsp; &Delta;h &asymp; t
          </p>
        </div>
      </Scene>

      {/* 06 — Now 37.9% more circular */}
      <Scene id="scene-06" align="items-center">
        <div className="reveal mx-auto w-full max-w-[1200px]">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#ff3a24]">
            Perfectly round, seriously
          </p>
          <h2 className="wordmark mt-4 max-w-[16ch] text-[#ff3a24] text-[clamp(2.6rem,8vw,8rem)] drop-shadow-[0_0_24px_rgba(255,42,24,0.35)]">
            Now 37.9% more circular
          </h2>
          <p className="mt-6 max-w-[52ch] text-[clamp(0.95rem,1.2vw,1.2rem)] leading-snug text-cream/75">
            Our engineers recalibrated its circumference with disturbing levels of
            attention to detail &mdash; just because we could.
          </p>
          <p className="mt-6 font-mono text-[11px] uppercase tracking-[0.18em] text-[#ff3a24]/70">
            RoPE: Roundness Optimization &amp; Perimeter Engineering &nbsp;·&nbsp; circularity yields &asymp; 1.0
          </p>
        </div>
      </Scene>

      {/* 07 — Transition void */}
      <Scene id="scene-07" align="items-center justify-center">
        <div className="reveal relative flex w-full flex-col items-center justify-center">
          <h2 className="wordmark text-center text-cream/15 text-[clamp(4rem,18vw,16rem)]">
            ORYZO
          </h2>
          <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.3em] text-cream/40">
            Scroll to continue
          </p>
        </div>
      </Scene>

      {/* 08 — Macro edge (desaturated cork macro filling the frame) */}
      <Scene id="scene-08" align="items-center justify-center">
        <div className="reveal relative mx-auto h-[clamp(20rem,68vh,46rem)] w-[86vw] max-w-[1200px] overflow-hidden rounded-xl">
          <img
            src={img("edge_MOBILE.webp")}
            alt="Macro view of the cork edge"
            loading="lazy"
            className="h-full w-full object-cover grayscale contrast-110"
          />
          <p className="absolute bottom-5 left-1/2 -translate-x-1/2 font-mono text-[10px] uppercase tracking-[0.3em] text-white/70">
            Scroll to continue
          </p>
        </div>
      </Scene>

      {/* 09 — Bark texture macro (warm material close-up filling the frame) */}
      <Scene id="scene-09" align="items-center justify-center">
        <div className="reveal relative mx-auto h-[clamp(20rem,68vh,46rem)] w-[86vw] max-w-[1200px] overflow-hidden rounded-xl">
          <img
            src={img("bite.webp")}
            alt="Cork material macro"
            loading="lazy"
            className="h-full w-full object-cover saturate-[0.85]"
          />
          <h2 className="absolute inset-0 flex items-center justify-center wordmark text-center text-cream/80 mix-blend-overlay text-[clamp(4rem,18vw,16rem)]">
            ORYZO
          </h2>
        </div>
      </Scene>

      {/* 10 — Sustainability (cream light flip) */}
      <Scene id="scene-10" align="items-center">
        <div className="reveal relative mx-auto grid w-[88vw] max-w-[1320px] items-center gap-10 md:grid-cols-[1.2fr_1fr]">
          <div>
            <h2 className="wordmark text-ink text-[clamp(3rem,13vw,12rem)] lowercase">
              sustainability
            </h2>
            <div className="mt-8 max-w-[44ch]">
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-green">
                Vegan-friendly
              </p>
              <p className="mt-3 text-[clamp(0.95rem,1.2vw,1.2rem)] leading-snug text-ink/75">
                Pure cork &mdash; sourced sustainably. Completely vegan: no cows were
                harmed, but it might be full of &lsquo;bull&rsquo;sh*t.
              </p>
            </div>
          </div>
          <figure className="relative h-[clamp(16rem,42vh,30rem)] overflow-hidden rounded-2xl">
            <img
              src={img("drop_test_MOBILE.webp")}
              alt="Natural cork / bark texture"
              loading="lazy"
              className="h-full w-full object-cover"
            />
            <figcaption className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/55 to-transparent p-4 font-mono text-[10px] uppercase tracking-[0.2em] text-cream">
              100% natural cork
            </figcaption>
          </figure>
        </div>
      </Scene>

      {/* 11 — Always (triptych) */}
      <Scene id="scene-11" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1400px] grid-cols-1 gap-4 md:grid-cols-3">
          <figure className="relative h-[44vh] overflow-hidden rounded-xl border border-cream/10 bg-brown/40">
            <img src={img("3090_MOBILE.webp")} alt="" loading="lazy" className="h-full w-full object-cover" />
          </figure>
          <figure className="relative h-[44vh] overflow-hidden rounded-xl border border-cream/10 bg-brown/40">
            <img src={img("sticker_1_MOBILE.webp")} alt="Sticker-covered coaster" loading="lazy" className="h-full w-full object-cover" />
          </figure>
          <figure className="relative h-[44vh] overflow-hidden rounded-xl border border-cream/10 bg-[#2a3a52]">
            <img src={img("always_on_MOBILE.webp")} alt="" loading="lazy" className="h-full w-full object-cover opacity-90" />
            <figcaption className="absolute inset-0 flex flex-col items-start justify-end p-5">
              <h3 className="wordmark text-cream text-[clamp(2rem,4vw,3.5rem)]">Always</h3>
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-cream/80">
                24/7 uptime. No power required.
              </p>
            </figcaption>
          </figure>
        </div>
      </Scene>

      {/* 12 — Drop-Tested */}
      <Scene id="scene-12" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1400px] items-center gap-10 md:grid-cols-[1fr_1.2fr]">
          <figure className="relative h-[clamp(14rem,30vw,26rem)] overflow-hidden rounded-2xl border border-cream/10 bg-green/30">
            <img src={img("perfect_MOBILE.webp")} alt="Perfect by design" loading="lazy" className="h-full w-full object-cover" />
            <figcaption className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-ink/80 to-transparent p-4 font-mono text-[10px] uppercase tracking-[0.2em] text-cream">
              Perfect by design
            </figcaption>
          </figure>
          <div className="text-right md:text-left">
            <h2 className={`wordmark text-cream text-[clamp(2.6rem,9vw,9rem)] ${shadow}`}>
              Drop-Tested
            </h2>
            <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.18em] text-cream/70">
              Test conditions: hard surface
            </p>
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cream/50">
              Date: 02/26/2026
            </p>
          </div>
        </div>
      </Scene>
    </>
  );
}
