const SANS = "'Inter', ui-sans-serif, system-ui, sans-serif";
const SERIF = "'Lora', Georgia, 'Times New Roman', serif";

const serifStyle = {
  fontFamily: SERIF,
  fontStyle: "normal",
  fontWeight: 400,
  letterSpacing: "-0.01em",
};

const footerLinks = {
  product: [
    { label: "Features", href: "/#features" },
    { label: "FAQ", href: "/#faq" },
  ],
  company: [
    { label: "Contact us", href: "mailto:hi@" },
    { label: "Support", href: "/support/" },
    { label: "Press", href: "mailto:press@" },
  ],
  connect: [
    { label: "Instagram", href: "https://www.instagram.com/novuperformance" },
    { label: "LinkedIn", href: "https://www.linkedin.com/company/novuperformance/" },
    { label: "TikTok", href: "https://www.tiktok.com/@novuperformance" },
  ],
};

function FooterColumn({ heading, links }) {
  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-[20px] md:text-[24px]" style={serifStyle}>
        {heading}
      </h3>
      <ul className="flex flex-col gap-3">
        {links.map((link) => {
          const external = link.href.startsWith("http");
          return (
            <li key={link.label}>
              <a
                className="text-[15px] md:text-[17px] font-normal text-white/90 no-underline transition-opacity duration-300 hover:opacity-80"
                href={link.href}
                style={{ fontFamily: SANS }}
                {...(external
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
              >
                {link.label}
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default function ProductSection() {
  return (
    <section
      data-nav-theme="dark"
      className="relative z-10 flex min-h-screen flex-col overflow-hidden bg-black"
      style={{ fontFamily: SANS }}
    >
      {/* Full-width CTA background photograph (ken-burns) */}
      <div className="absolute inset-0 overflow-hidden">
        <img
          alt=""
          src="/assets/images/unknown-5.img"
          decoding="async"
          loading="lazy"
          className="absolute inset-0 h-full w-full object-cover object-center"
          style={{
            color: "transparent",
            animation: "novuKenBurns 32s ease-in-out infinite alternate",
            willChange: "transform",
          }}
        />
      </div>

      {/* Darkening gradient overlay */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(rgba(0, 0, 0, 0.15) 0%, rgba(0, 0, 0, 0.35) 55%, rgba(0, 0, 0, 0.7) 100%)",
        }}
      />

      {/* CTA copy */}
      <div className="relative z-10 flex flex-1 items-center justify-center px-6 pt-32 md:pt-48">
        <div className="max-w-2xl text-center">
          <h2
            className="text-[40px] md:text-[64px] font-light leading-[1.05] tracking-[-0.015em] text-white"
            style={{ fontFamily: SANS }}
          >
            Start your day <span style={serifStyle}>differently.</span>
          </h2>
          <p
            className="mx-auto mt-6 max-w-xl text-[17px] md:text-[20px] font-light leading-relaxed text-white/85"
            style={{ fontFamily: SANS }}
          >
            Talk it out. Get clarity. Move forward.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 w-full text-white">
        <div className="mx-auto flex w-full max-w-[80rem] flex-col gap-16 px-5 pb-10 pt-20 md:px-10 md:pb-14 md:pt-32">
          <div className="grid grid-cols-2 gap-x-8 gap-y-12 sm:grid-cols-3">
            <FooterColumn heading="Product" links={footerLinks.product} />
            <FooterColumn heading="Company" links={footerLinks.company} />
            <FooterColumn heading="Connect" links={footerLinks.connect} />
          </div>

          <div className="flex flex-col gap-3 text-[11px] uppercase tracking-[0.08em] text-white/80 sm:flex-row sm:items-center sm:gap-x-8 sm:gap-y-2">
            <span className="text-[10px] tracking-[0.06em] text-white">
              © 2026 Novu Oy · All rights reserved
            </span>
            <a
              className="text-white/75 transition-colors duration-200 hover:text-white"
              href="/privacy-policy/"
            >
              Privacy Policy
            </a>
            <a
              className="text-white/75 transition-colors duration-200 hover:text-white"
              href="/terms-and-conditions/"
            >
              Terms of Use
            </a>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes novuKenBurns {
          0% { transform: scale(1.12) translate(-0.8%, 0.5%); }
          100% { transform: scale(1.22) translate(0.6%, -0.8%); }
        }
        @media (prefers-reduced-motion: reduce) {
          section[data-nav-theme="dark"] img { animation: none !important; transform: none !important; }
        }
      `}</style>
    </section>
  );
}
