import { useEffect, useRef, useState } from "react";

const ITEMS = [
  {
    label: "Footwear",
    img: "/assets/images/68cc0961b280206b654e58e2_89ced2402873245f068e00509e75cb4e_Footwear.webp",
  },
  {
    label: "Apparel",
    img: "/assets/images/68cc2986afafe4b8241d59c5_18e3874bebdf68a043e6534cad8bafe0_Apparel.webp",
  },
  {
    label: "Accessories",
    img: "/assets/images/68cc29aaf732ee52e8d88da8_4f2f8befb1b4bc513b6b015d3001542d_Accessories.webp",
  },
  {
    label: "Home decor",
    img: "/assets/images/68cc09614d81294abb5a7748_799e82c24e1dd7255e10ebe790a476ab_Home_20Decor.webp",
  },
  {
    label: "Furniture",
    img: "/assets/images/68cc0961724b0c5826d9416e_789fdf69bf480d17d9b919d0af3f8e87_Furniture.webp",
  },
  {
    label: "Transportation",
    img: "/assets/images/68cc09617783ed57f1637b37_5dcc210e577823a2cf670becb08558b7_Transport.webp",
  },
  {
    label: "Medical",
    img: "/assets/images/68cc29ab430643d66ba16ea9_915e61e21da379ae1c1331e50fb0f634_Medical.webp",
  },
];

// Brand-arrow icon shown on the active item (from raw SVG in source).
function ItemIcon({ active }) {
  return (
    <div
      aria-hidden="true"
      className="absolute bottom-0 left-0 flex h-[30px] items-center pr-[10px]"
      style={{
        transition:
          "transform .3s cubic-bezier(.25,.46,.45,.94), opacity .3s cubic-bezier(.25,.46,.45,.94)",
        opacity: active ? 1 : 0,
        transform: active ? "translateX(0)" : "translateX(-100%)",
      }}
    >
      <svg
        fill="none"
        height="33"
        style={{ maxHeight: "100%", width: "auto" }}
        viewBox="0 0 70 33"
        width="70"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M69.9903 19.0118C69.9903 19.3005 69.7538 19.5363 69.4641 19.5363H67.7356C65.0704 19.5363 62.9074 21.692 62.9074 24.3482V32.4755C62.9074 32.7642 62.6708 33 62.3811 33H48.4905C48.2008 33 47.9642 32.7642 47.9642 32.4755V26.2152C47.9642 26.0179 48.0753 25.8351 48.2539 25.7485L62.6129 18.5932C62.7915 18.5066 62.9026 18.3237 62.9026 18.1264V18.1457C62.9026 17.857 62.666 17.6212 62.3763 17.6212H0.526271C0.23658 17.6212 0 17.3854 0 17.0967V15.8985C0 15.6098 0.23658 15.374 0.526271 15.374H62.386C62.6757 15.374 62.9122 15.1382 62.9122 14.8495V14.8688C62.9122 14.6715 62.8012 14.4886 62.6226 14.402L48.2636 7.24672C48.0849 7.16011 47.9739 6.97725 47.9739 6.77996V0.524497C47.9739 0.235783 48.2104 0 48.5001 0H62.3908C62.6805 0 62.9171 0.235783 62.9171 0.524497V8.65179C62.9171 11.308 65.0801 13.4637 67.7452 13.4637H69.4737C69.7634 13.4637 70 13.6995 70 13.9882V19.0166L69.9903 19.0118Z"
          fill="#f75f2d"
        />
      </svg>
    </div>
  );
}

export default function Section4Section() {
  const [current, setCurrent] = useState(0);
  const [inView, setInView] = useState(false);
  const sectionRef = useRef(null);

  // Start cycling once the section scrolls into view (IntersectionObserver,
  // threshold 0.3 — matches the source script).
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setInView(true);
        });
      },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!inView) return;
    const id = setInterval(() => {
      setCurrent((i) => (i + 1) % ITEMS.length);
    }, 2000);
    return () => clearInterval(id);
  }, [inView]);

  return (
    <section
      ref={sectionRef}
      id="case-studies"
      className="section-dark case-studies-section flex flex-col bg-black lg:block"
      style={{ paddingLeft: "var(--_spacing---page-padding, 32px)" }}
    >
      <div
        className="case-studies-container mx-auto flex w-[76%] max-w-[536px] flex-col-reverse items-start gap-[60px] pt-[120px] pb-0 lg:mx-0 lg:h-[var(--app-height,100vh)] lg:w-full lg:max-w-none lg:flex-row lg:items-center lg:justify-between lg:gap-6 lg:py-6 max-[767px]:w-full max-[767px]:max-w-full max-[767px]:gap-10 max-[767px]:pt-[70px]"
        style={{
          paddingRight: "var(--_spacing---page-padding, 32px)",
        }}
      >
        {/* Texts column */}
        <div className="case-studies-texts-container flex w-full flex-col items-start justify-center pb-[60px] lg:h-full lg:flex-1 lg:items-center lg:pb-0">
          <div className="case-studies-texts-wrapper w-full max-w-full lg:w-[410px]">
            <h2
              className="case-studies-list-title m-0 font-light uppercase leading-[80%]"
              style={{
                fontFamily: "'Founders Grotesk', Arial, sans-serif",
                fontSize: "var(--_font-sizes---font-body-lg, 48px)",
              }}
            >
              We serve
            </h2>

            <ul className="case-studies-items m-0 mb-[60px] mt-0 flex list-none flex-col p-0 max-[767px]:mb-10">
              {ITEMS.map((item, i) => {
                const active = i === current;
                return (
                  <li
                    key={item.label}
                    className="case-studies-list-item relative flex items-center justify-start gap-[10px]"
                    style={{ color: "#6e6e6b" }}
                  >
                    <ItemIcon active={active} />
                    <div
                      className="case-studies-list-text m-0 font-light uppercase leading-[80%]"
                      style={{
                        fontFamily: "'Founders Grotesk', Arial, sans-serif",
                        fontSize: "var(--_font-sizes---font-body-lg, 48px)",
                        color: active ? "#f5f3f0" : "#6e6e6b",
                        WebkitTextStrokeColor: "#f5f3f0",
                        transform: active
                          ? "translateX(74px)"
                          : "translateX(0)",
                        transition:
                          "transform .3s cubic-bezier(.25,.46,.45,.94), color .3s cubic-bezier(.25,.46,.45,.94)",
                      }}
                    >
                      {item.label}
                    </div>
                  </li>
                );
              })}
            </ul>

            <a
              href="/case-studies/footwear"
              className="button button-glass-light inline-flex h-[60px] items-center justify-center whitespace-nowrap rounded-[12px] px-6 font-medium uppercase no-underline max-[767px]:h-12 max-[767px]:w-full"
              style={{
                gap: "12px",
                border: "1px solid #e5e3e033",
                backgroundColor: "#94939059",
                backdropFilter: "blur(6px)",
                WebkitBackdropFilter: "blur(6px)",
                color: "#f5f3f0",
                fontSize: "var(--_font-sizes---font-button, 18px)",
                letterSpacing: ".003em",
                lineHeight: "58px",
                transition: "color .2s, background-color .2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "#f75f2d";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "#94939059";
              }}
            >
              check the case studies
            </a>
          </div>
        </div>

        {/* Image swiper (fade) */}
        <div className="case-studies-swiper relative w-full overflow-hidden lg:h-full lg:flex-1">
          <div className="relative w-full" style={{ aspectRatio: "1 / 1" }}>
            {ITEMS.map((item, i) => {
              const active = i === current;
              return (
                <div
                  key={item.label}
                  className="absolute inset-0 flex flex-col items-center justify-center bg-black"
                  style={{
                    opacity: active ? 1 : 0,
                    transition: "opacity .9s ease",
                    pointerEvents: active ? "auto" : "none",
                  }}
                >
                  <img
                    src={item.img}
                    alt=""
                    loading="lazy"
                    className="case-studies-image w-full rounded-[20px] object-cover"
                    style={{
                      aspectRatio: "1 / 1",
                      transform: active ? "translateX(0%)" : "translateX(10%)",
                      transition: "transform 0.5s ease",
                    }}
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
