// Scene 00 — hero. Transparent so the gold ring (fixed canvas behind) shows
// through; only the wordmark + intro copy sit on top.
export default function Hero() {
  return (
    <section
      id="hero"
      className="relative flex min-h-screen flex-col justify-between overflow-hidden px-[3.125vw] pb-10 pt-28"
    >
      {/* full-bleed cork/desk surface (warm tone matching the real frame) so the
          ring sits on a coaster-like backdrop, never empty black */}
      <div className="cork-surface-hero pointer-events-none absolute inset-0" />
      <div className="cork-grid pointer-events-none absolute inset-0 opacity-[0.7]" />

      {/* wordmark — sized down and anchored top so the gold ring reads centre */}
      <div className="relative z-10">
        <h1 className="wordmark text-cream drop-shadow-[0_2px_30px_rgba(0,0,0,0.55)] text-[clamp(3rem,12vw,9rem)]">
          ORYZO
        </h1>
      </div>

      {/* left designer tag */}
      <p className="relative z-10 max-w-[34ch] font-mono text-[11px] uppercase tracking-[0.18em] text-cream/70">
        Designed by Lusion, the award-winning design studio.
      </p>

      {/* right-side intro copy */}
      <div className="relative z-10 ml-auto max-w-[28ch] pb-[4vh] text-right text-[clamp(1rem,1.5vw,1.6rem)] font-medium leading-snug text-cream drop-shadow-[0_2px_18px_rgba(0,0,0,0.6)]">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.2em] text-orange">
          Made for mugs. Built for shelves.
        </p>
        Designed to lift, insulate, and grip in all the right ways. Oryzo makes the
        simplest moment feel considered.
      </div>

      {/* bottom row */}
      <div className="relative z-10 flex items-end justify-between gap-8">
        <p className="text-[clamp(0.9rem,1.1vw,1.1rem)] leading-snug text-cream/80">
          The world&rsquo;s most unnecessarily sophisticated cork coaster.
        </p>
        <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-cream/60">
          <span className="inline-block h-3 w-3 animate-pulse rounded-full border border-cream/50" />
          Scroll to continue
        </div>
      </div>
    </section>
  );
}
