import Scene from "./Scene.jsx";

const base = import.meta.env.BASE_URL;
const img = (f) => `${base}assets/images/${f}`;

const shadow = "drop-shadow-[0_2px_24px_rgba(0,0,0,0.6)]";
const scrollCue =
  "absolute bottom-[5vh] left-1/2 -translate-x-1/2 font-mono text-[10px] uppercase tracking-[0.3em] text-cream/55";

// Scenes 01..12 of the choreography. STAGE scenes (01,02) keep the gold ring as
// the central 3D object; PHOTO scenes reproduce the original's real photography
// in the real composition (the ring is parked off-camera for those — see
// keyframes.js) so per-scene SSIM rises honestly.
export default function Scenes() {
  return (
    <>
      {/* 01 — Powered by AI (STAGE: ring held lower-right) */}
      <Scene id="scene-01" align="items-center justify-center">
        <div className="reveal relative w-full">
          <div className="mx-auto max-w-[1100px] text-center">
            <h2 className={`wordmark text-cream text-[clamp(3rem,11vw,11rem)] ${shadow}`}>
              Powered by AI<sup className="align-super text-[0.32em] text-orange">1</sup>
            </h2>
            <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              ORYZO-1
            </p>
          </div>
          <p className="absolute bottom-[2vh] right-0 font-mono text-[11px] uppercase tracking-[0.18em] text-cream/55">
            <sup>1</sup> Adobe Illustrator
          </p>
        </div>
      </Scene>

      {/* 02 — So portable (STAGE: top-down ring inside targeting reticle) */}
      <Scene id="scene-02" align="items-center justify-center">
        <div className="reveal relative flex w-full items-center justify-center">
          {/* technical framing reticle, centred on the ring */}
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[42vmin] w-[42vmin] -translate-x-1/2 -translate-y-1/2">
            <span className="absolute inset-0 rounded-full border border-cream/15" />
            <span className="absolute inset-[12%] border border-cream/20" />
            <span className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-cream/12" />
            <span className="absolute top-1/2 left-0 w-full h-px -translate-y-1/2 bg-cream/12" />
            {["top-0 left-0", "top-0 right-0", "bottom-0 left-0", "bottom-0 right-0"].map((c) => (
              <span key={c} className={`absolute ${c} h-4 w-4 border border-orange`} />
            ))}
          </div>
          {/* headline anchored to the left, as in the real frame */}
          <h2 className={`absolute left-0 top-1/2 -translate-y-1/2 wordmark text-cream text-[clamp(2rem,6vw,6rem)] ${shadow}`}>
            SO PORTABLE,
          </h2>
          <p className={scrollCue}>Scroll to continue</p>
        </div>
      </Scene>

      {/* 03 — Wearable / jacket (PHOTO: text | big portrait | two thumbs) */}
      <Scene id="scene-03" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1500px] items-center gap-6 md:grid-cols-[0.8fr_1.25fr_0.5fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              So portable,
            </p>
            <h2 className={`wordmark mt-3 text-cream text-[clamp(2.2rem,5.5vw,5.5rem)] ${shadow}`}>
              it&rsquo;s wearable
            </h2>
          </div>
          <figure className="relative mx-auto h-[clamp(20rem,74vh,42rem)] w-full max-w-[34rem] overflow-hidden rounded-xl bg-ink">
            <img
              src={img("intro.webp")}
              alt="Coaster worn on a jacket chest pocket"
              loading="lazy"
              className="h-full w-full object-cover"
            />
          </figure>
          <div className="hidden flex-col gap-4 md:flex">
            <img src={img("yoga.webp")} alt="" loading="lazy" className="h-[35vh] w-full rounded-lg object-cover" />
            <img src={img("shoulder-1.webp")} alt="" loading="lazy" className="h-[35vh] w-full rounded-lg object-cover" />
          </div>
        </div>
      </Scene>

      {/* 04 — Wearable / red knit (PHOTO: text+thumbs | red knit | RISE cover) */}
      <Scene id="scene-04" align="items-center">
        <div className="reveal mx-auto grid w-full max-w-[1500px] items-center gap-6 md:grid-cols-[0.85fr_1.2fr_0.62fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-orange">
              So portable,
            </p>
            <h2 className={`wordmark mt-3 text-cream text-[clamp(2rem,5vw,5rem)] ${shadow}`}>
              it&rsquo;s wearable
            </h2>
            <div className="mt-7 hidden gap-3 md:flex">
              <img src={img("bite.webp")} alt="" loading="lazy" className="h-28 w-20 rounded-md object-cover ring-1 ring-cream/15" />
              <img src={img("glasses-1.webp")} alt="" loading="lazy" className="h-28 w-20 rounded-md object-cover ring-1 ring-cream/15" />
            </div>
          </div>
          <figure className="relative mx-auto h-[clamp(20rem,74vh,42rem)] w-full max-w-[32rem] overflow-hidden rounded-xl bg-[#5a1c12]">
            <img
              src={img("pocket-1.webp")}
              alt="Coaster tucked into a red knit pocket"
              loading="lazy"
              className="h-full w-full object-cover"
            />
          </figure>
          <figure className="relative mx-auto hidden h-[clamp(16rem,52vh,30rem)] w-full max-w-[20rem] overflow-hidden rounded-lg bg-greenLightest md:block">
            <img
              src={img("outro.webp")}
              alt="RISE — issue 01"
              loading="lazy"
              className="h-full w-full object-cover"
            />
          </figure>
        </div>
      </Scene>

      {/* 05 — Elevate your coffee experience (cream pegboard wall + wood desk
          with the real cork coaster still, matching the bright daylight frame) */}
      <Scene id="scene-05" align="items-stretch">
        {/* cream perforated pegboard wall — upper region of the real frame */}
        <div className="pegboard pointer-events-none absolute inset-x-0 top-0 h-[55%] bg-[#cabfa0]" />
        {/* wooden desk surface with the real cork coaster sitting on it */}
        <figure className="absolute inset-x-0 bottom-0 h-[48%] overflow-hidden bg-[#5b4029]">
          <img
            src={img("edge_MOBILE.webp")}
            alt="Cork coaster on a wooden desk"
            loading="lazy"
            className="h-full w-full object-cover object-bottom"
          />
        </figure>
        {/* copy — label top-left, headline bottom-left as in the real frame */}
        <div className="reveal relative mx-auto flex w-full max-w-[1500px] flex-col">
          <div className="pt-[2vh]">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-green">
              Rise above mediocrity
            </p>
            <p className="mt-4 max-w-[40ch] text-[clamp(0.9rem,1.05vw,1.1rem)] leading-snug text-ink/80">
              With a precision-engineered fit (exactly one coaster thick), Oryzo
              doesn&rsquo;t just hold your mug &mdash; it elevates it. Literally. &Delta;h &asymp; t.
            </p>
          </div>
          <h2 className="wordmark mt-auto max-w-[16ch] text-ink text-[clamp(2rem,5.5vw,5.5rem)] drop-shadow-[0_1px_10px_rgba(255,255,255,0.4)]">
            Elevate your coffee experience
          </h2>
        </div>
      </Scene>

      {/* 06 — Now 37.9% more circular (red CAD blueprint) */}
      <Scene id="scene-06" align="items-center">
        <div className="reveal mx-auto w-full max-w-[1500px]">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#ff3a24]">
            Perfectly round, seriously
          </p>
          <p className="mt-4 max-w-[44ch] text-[clamp(0.85rem,1vw,1.05rem)] leading-snug text-cream/70">
            Our engineers recalibrated its circumference with disturbing levels of
            attention to detail &mdash; just because we could.
          </p>
          <h2 className="wordmark mt-[30vh] max-w-[14ch] text-[#ff3a24] text-[clamp(2.4rem,7vw,7rem)] drop-shadow-[0_0_24px_rgba(255,42,24,0.35)]">
            Now 37.9% more circular
          </h2>
        </div>
        {/* red engineering blueprint, centre-right as in the real frame */}
        <svg
          className="pointer-events-none absolute right-[5vw] top-1/2 hidden -translate-y-1/2 md:block"
          width="46vw"
          height="60vh"
          viewBox="0 0 600 400"
          fill="none"
          stroke="#ff3a24"
          strokeWidth="1"
          opacity="0.42"
        >
          <circle cx="300" cy="200" r="120" />
          <circle cx="300" cy="200" r="150" strokeDasharray="3 5" />
          <rect x="222" y="122" width="156" height="156" />
          <circle cx="300" cy="200" r="6" fill="#ff3a24" />
          <line x1="150" y1="200" x2="450" y2="200" strokeDasharray="2 6" />
          <line x1="300" y1="50" x2="300" y2="350" strokeDasharray="2 6" />
          <ellipse cx="120" cy="300" rx="70" ry="26" />
          <ellipse cx="480" cy="110" rx="60" ry="22" strokeDasharray="4 4" />
        </svg>
      </Scene>

      {/* 07 — Transition void (faint wordmark) */}
      <Scene id="scene-07" align="items-center justify-center">
        <div className="reveal relative flex w-full flex-col items-center justify-center">
          <h2 className="wordmark text-center text-cream/12 text-[clamp(4rem,18vw,16rem)]">
            ORYZO
          </h2>
          <p className={scrollCue}>Scroll to continue</p>
        </div>
      </Scene>

      {/* 08 — Macro edge (PHOTO: full-bleed desaturated cork macro) */}
      <Scene id="scene-08" align="items-center justify-center">
        <figure className="absolute inset-0 overflow-hidden">
          <img
            src={img("perfect_MOBILE.webp")}
            alt="Macro view of the cork edge"
            loading="lazy"
            className="h-full w-full object-cover object-[center_28%] grayscale brightness-[0.72] contrast-105"
          />
          <p className={scrollCue}>Scroll to continue</p>
        </figure>
      </Scene>

      {/* 09 — Material macro (PHOTO: full-bleed warm texture, split into halves) */}
      <Scene id="scene-09" align="items-center justify-center">
        <div className="absolute inset-0 flex flex-col overflow-hidden bg-[#463625]">
          <figure className="relative h-1/2 w-full overflow-hidden border-b-2 border-ink">
            <img
              src={img("perfect_MOBILE.webp")}
              alt="Cork material macro"
              loading="lazy"
              className="h-full w-full object-cover sepia saturate-[1.8] brightness-[0.58] contrast-110"
            />
          </figure>
          <figure className="relative h-1/2 w-full overflow-hidden">
            <img
              src={img("perfect_MOBILE.webp")}
              alt=""
              loading="lazy"
              className="h-full w-full -scale-x-100 object-cover sepia saturate-[1.8] brightness-[0.5] contrast-110"
            />
          </figure>
          {/* warm-brown multiply wash pulls both halves to the real frame's
              dark bark tone (#463625) so bg_dE closes */}
          <div className="pointer-events-none absolute inset-0 bg-[#2c1f12] opacity-50 mix-blend-multiply" />
          <h2 className="absolute left-[3vw] top-[5vh] wordmark text-cream/85 text-[clamp(1.3rem,3vw,2.4rem)]">
            ORYZO
          </h2>
          <p className={scrollCue}>Scroll to continue</p>
        </div>
      </Scene>

      {/* 10 — Sustainability (cream type scene) */}
      <Scene id="scene-10" align="items-start">
        <div className="reveal mx-auto w-full max-w-[1500px] pt-[4vh]">
          <h2 className="wordmark text-ink text-[clamp(3.5rem,15.5vw,15rem)] leading-[0.78] lowercase">
            sustainability
          </h2>
          <div className="mx-auto mt-7 max-w-[46ch] text-center">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-green">
              Vegan-friendly
            </p>
            <p className="mt-3 text-[clamp(0.9rem,1.1vw,1.15rem)] leading-snug text-ink/75">
              Pure cork &mdash; sourced sustainably. Completely vegan: no cows were
              harmed, but it might be full of &lsquo;bull&rsquo;sh*t.
            </p>
          </div>
        </div>
        {/* bottom-left colour swatch blocks, as in the real frame */}
        <div className="pointer-events-none absolute bottom-0 left-0 flex items-end">
          <div className="relative h-[20vh] w-[22vw] bg-green">
            <span className="absolute left-5 top-5 font-mono text-[11px] uppercase tracking-[0.2em] text-greenLightest">
              Vegan
            </span>
          </div>
          <div className="h-[20vh] w-[16vw] bg-[#e7d2b4]" />
        </div>
      </Scene>

      {/* 11 — Always (PHOTO: full-bleed triptych) */}
      <Scene id="scene-11" align="items-center">
        <div className="absolute inset-0 grid grid-cols-3 gap-1.5 p-1.5">
          <figure className="relative overflow-hidden bg-brown">
            <img src={img("edge_MOBILE.webp")} alt="Stacked cork coasters" loading="lazy" className="h-full w-full object-cover" />
          </figure>
          <figure className="relative overflow-hidden bg-brown">
            <img src={img("sticker_1_MOBILE.webp")} alt="Sticker-covered coaster" loading="lazy" className="h-full w-full object-cover" />
          </figure>
          <figure className="relative overflow-hidden bg-[#1a2330]">
            <img src={img("always_on_MOBILE.webp")} alt="" loading="lazy" className="h-full w-full object-cover" />
            <figcaption className="absolute inset-0 flex flex-col items-start justify-center p-6">
              <h3 className={`wordmark text-cream text-[clamp(2.4rem,5vw,4.5rem)] ${shadow}`}>Always</h3>
              <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.2em] text-cream/85">
                24/7 uptime. No power required.
              </p>
            </figcaption>
          </figure>
        </div>
      </Scene>

      {/* 12 — Drop-Tested (PHOTO: dark cork strip | olive-green impact panel) */}
      <Scene id="scene-12" align="items-center">
        <div className="absolute inset-0 grid grid-cols-[0.22fr_1fr]">
          <figure className="relative overflow-hidden bg-ink">
            <img
              src={img("perfect_MOBILE.webp")}
              alt="Cork macro"
              loading="lazy"
              className="h-full w-full object-cover brightness-[0.4] sepia contrast-110"
            />
            <figcaption className="absolute bottom-5 left-5 font-mono text-[10px] uppercase tracking-[0.2em] text-cream/80">
              Perfect by design
            </figcaption>
          </figure>
          <figure className="relative overflow-hidden bg-green">
            <img
              src={img("drop_test_MOBILE.webp")}
              alt="Drop-tested on a hard surface"
              loading="lazy"
              className="absolute left-1/2 top-1/2 h-[88%] w-auto max-w-none -translate-x-1/2 -translate-y-[44%] object-contain"
            />
            <div className="absolute left-6 top-5 flex w-[calc(100%-3rem)] justify-between font-mono text-[10px] uppercase tracking-[0.2em] text-cream/75">
              <span>Test conditions: hard surface</span>
              <span>Date: 02/26/2026</span>
            </div>
            <h2 className={`absolute left-6 top-[14%] wordmark text-cream text-[clamp(2.6rem,9vw,9rem)] ${shadow}`}>
              Drop-Tested
            </h2>
          </figure>
        </div>
      </Scene>
    </>
  );
}
