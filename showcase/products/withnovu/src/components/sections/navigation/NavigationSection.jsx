const SANS = "'Inter', ui-sans-serif, system-ui, sans-serif";

export default function NavigationSection() {
  return (
    <nav
      className="fixed inset-x-0 top-0 z-[100] pt-6 translate-y-0"
      style={{
        transitionProperty: "transform",
        transitionDuration: "900ms",
        transitionTimingFunction: "cubic-bezier(0.22,1,0.36,1)",
        transitionDelay: "2100ms",
        maxWidth: "100%",
        fontFamily: SANS,
      }}
    >
      <div
        className="mx-auto grid w-full max-w-[80rem] grid-cols-[1fr_auto_1fr] items-center gap-4 px-5 md:px-10"
      >
        {/* Brand wordmark (original used an inline SVG logo) */}
        <a
          aria-label="Novu home"
          className="flex items-center justify-self-start text-white"
          href="/"
          style={{
            transitionProperty: "color",
            transitionDuration: "300ms",
            textDecoration: "none",
            fontFamily: SANS,
            fontWeight: 600,
            fontSize: "20px",
            lineHeight: 1,
            letterSpacing: "-0.01em",
          }}
        >
          novu
        </a>

        {/* Center pill with nav links (desktop only) */}
        <div
          className="relative hidden items-center gap-1 overflow-hidden p-1 text-[15px] justify-self-center md:flex text-white"
          style={{
            backdropFilter: "blur(3px)",
            WebkitBackdropFilter: "blur(3px)",
            backgroundColor: "rgba(255, 255, 255, 0.15)",
            boxShadow:
              "rgba(255, 255, 255, 0.4) 1px 1px 1px 0px inset, rgba(255, 255, 255, 0.2) -1px -1px 1px 0px inset",
            borderRadius: "50vw",
            transitionProperty: "color",
            transitionDuration: "300ms",
          }}
        >
          <a
            className="inline-flex h-[42px] items-center rounded-full px-[1.375rem] no-underline transition text-white/85 hover:bg-white/10 hover:text-white"
            href="/#features"
            style={{ textDecoration: "none" }}
          >
            Features
          </a>
          <a
            className="inline-flex h-[42px] items-center rounded-full px-[1.375rem] no-underline transition text-white/85 hover:bg-white/10 hover:text-white"
            href="/#faq"
            style={{ textDecoration: "none" }}
          >
            FAQ
          </a>
        </div>

        <div aria-hidden="true" className="justify-self-end" />
      </div>
    </nav>
  );
}
