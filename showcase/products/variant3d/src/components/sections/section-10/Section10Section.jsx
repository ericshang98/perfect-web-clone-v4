import { useState, useRef } from "react";

const KNIT_IMG =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31/68714f06b826e13bdbea06a0_Frame%20385.svg";
const PLUS_IMG =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31/689b556c178506cc2223f19f_plus.svg";
const MINUS_IMG =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31/6871aaa7ffd0df9b3148c632_Icon%20%20Minus.svg";

const FAQS = [
  {
    q: "What services does VARIANT3D offer?",
    a: (
      <p>
        VARIANT3D offers a comprehensive range of services powered by our
        proprietary software, LOOP. Our services include rapid prototyping,
        product development, and connecting brands with manufacturing partners
        to bring products to market.
      </p>
    ),
  },
  {
    q: "Who do I contact if I have any questions?",
    a: (
      <p>
        You can contact{" "}
        <a
          href="mailto:support@variant3d.io"
          className="underline decoration-1 transition-colors duration-200 hover:text-[#f75f2d]"
        >
          support@variant3d.io
        </a>{" "}
        if you do not see your questions in this FAQ list or if an answer to
        your question needs further clarification. Please allow 2-3 business
        days for someone on our support team to follow up with you.
      </p>
    ),
  },
  {
    q: "Where is VARIANT3D located?",
    a: (
      <p>
        Our headquarters is located in Malibu, CA. VARIANT3D also has two
        satellite offices: one in New York, NY, and the other in Detroit, MI.
      </p>
    ),
  },
];

function FaqItem({ q, a }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  return (
    <div
      role="listitem"
      className="border-b border-[#949390] pt-10 last:border-b-0 md:pt-[60px] xl:pt-20"
    >
      <div className="flex flex-col">
        {/* header */}
        <div
          role="button"
          tabIndex={0}
          onClick={() => setOpen((o) => !o)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setOpen((o) => !o);
            }
          }}
          className="mb-4 flex w-full max-w-full cursor-pointer items-center justify-between gap-4 pr-0 md:mb-5 md:pr-8 lg:mb-[30px] xl:mb-10"
        >
          <p
            className="m-0 font-light leading-[105%] text-[#1a1919]"
            style={{
              fontSize: "var(--faq-header-size)",
            }}
          >
            {q}
          </p>
          <div className="relative h-8 min-h-[32px] w-8 min-w-[32px] transition-opacity duration-200 md:h-12 md:min-h-[48px] md:w-12 md:min-w-[48px] xl:h-16 xl:min-h-[64px] xl:w-16 xl:min-w-[64px]">
            <img
              src={PLUS_IMG}
              alt=""
              loading="eager"
              className="absolute h-full w-full transition-transform duration-300"
              style={{
                transform: open
                  ? "rotate(90deg) scale(0)"
                  : "rotate(0deg) scale(1)",
              }}
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
            <img
              src={MINUS_IMG}
              alt=""
              loading="eager"
              className="absolute h-full w-full transition-transform duration-300"
              style={{
                transform: open
                  ? "rotate(0deg) scale(1)"
                  : "rotate(-90deg) scale(0)",
              }}
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
          </div>
        </div>

        {/* answer container */}
        <div
          ref={containerRef}
          className="block w-full max-w-[822px] overflow-hidden font-light leading-[110%] text-[#1a1919] transition-[max-height] duration-500 max-md:text-[#6e6e6b]"
          style={{
            maxHeight: open
              ? containerRef.current
                ? containerRef.current.scrollHeight
                : 1000
              : 0,
            fontSize: "var(--faq-body-size)",
          }}
        >
          <div className="mb-0 pb-8 pt-4 md:pt-5 lg:pt-[30px] xl:pt-10 [&_p]:mb-0">
            {a}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Section10Section() {
  return (
    <div
      style={{
        "--faq-header-size": "20px",
        "--faq-body-size": "20px",
      }}
    >
      {/* responsive font-size variables matching original @media breakpoints */}
      <style>{`
        @media (min-width: 768px) {
          .v3d-s10 { --faq-header-size: 42px; --faq-body-size: 22px; }
        }
        @media (min-width: 1440px) {
          .v3d-s10 { --faq-header-size: 52px; --faq-body-size: 24px; }
        }
      `}</style>

      <div
        className="v3d-s10"
        style={{ "--faq-header-size": "20px", "--faq-body-size": "20px" }}
      >
        {/* Start creating with LOOP CTA */}
        <section
          className="w-full bg-[#f5f3f0] px-4 pb-4 pt-4 text-[#1a1919] md:px-6 md:pb-[60px] md:pt-8 xl:px-10 xl:pb-20 xl:pt-10"
          style={{ fontFamily: '"Founders Grotesk", Arial, sans-serif' }}
        >
          <div className="flex flex-col gap-8 md:gap-8 lg:gap-20">
            <img
              src={KNIT_IMG}
              alt="Knit smarter"
              loading="lazy"
              className="w-full"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
            <div className="flex w-full max-w-full flex-col items-center justify-between gap-8 lg:gap-[30px]">
              <p className="m-0 mx-auto text-center text-[30px] font-light leading-[105%] no-underline md:text-[48px] lg:text-[52px]">
                Start creating with LOOP™
              </p>
              <a
                href="/early-access"
                className="flex h-12 w-full items-center justify-center gap-3 whitespace-nowrap rounded-lg bg-black px-6 text-base font-medium uppercase leading-[46px] tracking-[.003em] text-[#f5f3f0] no-underline transition-colors duration-200 hover:bg-[#f75f2d] md:h-[60px] md:w-auto md:text-lg md:leading-[58px]"
              >
                Get early access
              </a>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="block bg-white px-4 py-10 md:px-6 md:py-[60px] xl:px-10 xl:py-20">
          <div>
            <div
              role="list"
              className="mb-0 border-t border-[#949390] pb-10 pl-0 md:pb-[60px] xl:pb-20"
            >
              {FAQS.map((item) => (
                <FaqItem key={item.q} q={item.q} a={item.a} />
              ))}
            </div>
          </div>

          <div className="flex items-center justify-center">
            <a
              href="/faqs"
              className="flex h-12 w-full items-center justify-center gap-3 whitespace-nowrap rounded-lg border border-[#e5e3e033] bg-[#94939059] px-6 text-base font-medium uppercase leading-[46px] tracking-[.003em] text-[#1a1919] no-underline transition-colors duration-200 hover:bg-[#f75f2d] hover:text-[#f5f3f0] md:h-[60px] md:w-auto md:text-lg md:leading-[58px]"
            >
              All FAQs
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
