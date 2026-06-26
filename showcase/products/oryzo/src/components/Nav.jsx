const LINKS = [
  { label: "Intro", href: "#hero" },
  { label: "Features", href: "#showcase" },
  { label: "Product", href: "#showcase" },
  { label: "Contact", href: "#contact" },
];

export default function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 mix-blend-difference">
      <div className="flex items-center justify-between px-[3.125vw] py-5">
        {/* wordmark */}
        <a href="#hero" className="wordmark text-cream text-[22px] tracking-tight">
          ORYZO
        </a>

        {/* centre tagline */}
        <span className="hidden md:block font-mono text-[11px] uppercase tracking-[0.18em] text-cream/90">
          Made for mugs. Built for shelves.
        </span>

        {/* nav links */}
        <nav className="flex items-center gap-6 font-mono text-[11px] uppercase tracking-[0.18em] text-cream/90">
          {LINKS.map((l) => (
            <a key={l.label} href={l.href} className="hidden sm:inline hover:text-orange transition-colors">
              {l.label}
            </a>
          ))}
        </nav>
      </div>

      {/* vertical "try our cloud" tab on the far right edge */}
      <a
        href="https://lusion.co/"
        target="_blank"
        rel="noreferrer"
        className="fixed right-0 top-1/2 z-50 hidden -translate-y-1/2 rotate-180 bg-cream px-2 py-4 font-mono text-[10px] uppercase tracking-[0.2em] text-ink [writing-mode:vertical-rl] lg:block hover:bg-orange hover:text-cream transition-colors"
      >
        Try our cloud
      </a>
    </header>
  );
}
