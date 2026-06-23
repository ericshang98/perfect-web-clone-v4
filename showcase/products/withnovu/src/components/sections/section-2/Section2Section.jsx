import { useState, useRef, useEffect } from "react";

const SANS = "'Inter', ui-sans-serif, system-ui, sans-serif";
const SERIF = "'Lora', Georgia, 'Times New Roman', serif";

// The center phone's screen is a scroll-driven crossfade of looping app-demo
// videos (one per feature copy), exactly like the original sticky-phone section.
// Index order matches FEATURE_BLOCKS top-to-bottom.
const PHONE_VIDEOS = [
  "/videos/list.mp4", // Just talk. We'll organize. → spoken update becomes a task list
  "/videos/Alex-cut.mp4", // Prioritise what actually matters.
  "/videos/Focus-cut.mp4", // Stay out of your own way.
  "/videos/Wrap-up.mp4", // See your day clearly. → evening wrap-up
];

// Reusable serif word (matches original .serif / em: Lora 400 normal)
function Serif({ children }) {
  return (
    <span
      style={{
        fontFamily: SERIF,
        fontStyle: "normal",
        fontWeight: 400,
        letterSpacing: "-0.01em",
      }}
    >
      {children}
    </span>
  );
}

// ---- Feature copy blocks (alternating left/right) ----
const FEATURE_BLOCKS = [
  {
    side: "left",
    title: (
      <>
        Just talk. <br />
        We&rsquo;ll <Serif>organize.</Serif>
      </>
    ),
    body: "Say whatever is on your mind. Novu transcribes it, pulls out the tasks, and structures your day in seconds.",
  },
  {
    side: "right",
    title: (
      <>
        Prioritise what <br />
        actually <Serif>matters.</Serif>
      </>
    ),
    body: "You always pick three priorities. No more pretending that everything on your list deserves the same attention.",
  },
  {
    side: "left",
    title: (
      <>
        Stay out of <br />
        your own <Serif>way.</Serif>
      </>
    ),
    body: "No endless lists. No constant notifications. Just the day you set yourself, structured and clear.",
  },
  {
    side: "right",
    title: (
      <>
        See your day <br />
        <Serif>clearly.</Serif>
      </>
    ),
    body: "At night, reflect on what actually happened and carry the bits worth keeping into tomorrow.",
  },
];

function FeatureCopy({ title, body, center }) {
  return (
    <div className={`max-w-sm w-full ${center ? "mx-auto text-center" : "text-left"}`}>
      <h2
        className="text-[32px] md:text-[40px]"
        style={{
          fontFamily: SANS,
          fontWeight: 300,
          lineHeight: 1.1,
          letterSpacing: "-0.015em",
        }}
      >
        {title}
      </h2>
      <p
        className="mt-4 text-[16px] md:text-[17px]"
        style={{
          fontFamily: SANS,
          fontWeight: 300,
          lineHeight: 1.625,
          color: "rgba(0,0,0,0.65)",
        }}
      >
        {body}
      </p>
    </div>
  );
}

// ---- Phone mockup ----
// The device images already include the phone bezel baked in. unknown-1.img is an
// EMPTY frame with a transparent screen (the live site fills it with a video we
// can't reproduce); over the white page that transparent screen reads as a clean
// blank phone. unknown-2/3/4.img are complete app renders. So render every device
// image PLAINLY (object-contain) — no extra CSS bezel, no black backdrop (that was
// what turned the transparent-screen frame into a black slab).
function PhoneMockup({ screenSrc = "/assets/images/unknown-1.img", screenAlt = "Novu app screen" }) {
  return (
    <div
      className="relative mx-auto h-[58vh] min-h-[400px] max-h-[620px] md:h-[72vh] md:max-h-[820px]"
      style={{ aspectRatio: "1380 / 2880" }}
    >
      <img
        alt={screenAlt}
        className="relative h-full w-full select-none object-contain"
        decoding="async"
        draggable="false"
        loading="lazy"
        src={screenSrc}
        style={{ color: "transparent" }}
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />
    </div>
  );
}

// ---- Scroll-driven center phone ----
// The screen stacks one looping <video> per feature; as the reader scrolls the
// feature section, `activeIndex` crossfades to the matching demo (900ms opacity
// transition) — the same mechanic as the original sticky phone. videoRefs lets the
// parent play only the active video and pause the rest.
function ScrollPhone({ activeIndex, videoRefs }) {
  return (
    <div
      className="relative mx-auto h-[58vh] min-h-[400px] max-h-[620px] md:h-[72vh] md:max-h-[820px]"
      style={{ aspectRatio: "1380 / 2880" }}
    >
      {/* video screen cutout (behind the transparent device frame) */}
      <div
        className="absolute overflow-hidden bg-white"
        style={{ top: "2.9%", bottom: "2.9%", left: "4.4%", right: "4.4%", borderRadius: "13% / 6.3%" }}
      >
        {PHONE_VIDEOS.map((src, i) => (
          <video
            key={src}
            ref={(el) => {
              videoRefs.current[i] = el;
            }}
            className="absolute inset-0 h-full w-full select-none object-cover transition-opacity duration-[900ms] ease-[cubic-bezier(0.4,0,0.2,1)]"
            style={{ opacity: i === activeIndex ? 1 : 0 }}
            src={src}
            muted
            loop
            playsInline
            preload="auto"
            disablePictureInPicture
          />
        ))}
      </div>
      {/* transparent-screen device frame on top — its bezel masks the video edges */}
      <img
        alt="Novu app demo on iPhone"
        className="pointer-events-none relative h-full w-full select-none object-contain"
        decoding="async"
        draggable="false"
        src="/assets/images/unknown-1.img"
        style={{ color: "transparent" }}
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />
    </div>
  );
}

// ---- Highlights carousel cards ----
const CARD_FRAME =
  "relative flex flex-col overflow-hidden rounded-[20px] md:rounded-[30px] w-[calc(100vw-80px)] md:w-auto aspect-[5/8] md:aspect-[11/10] md:h-[calc(78svh-32px)] md:max-h-[800px] md:min-h-[600px]";

function CardGradientGlow() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-x-0 bottom-0 h-[225px] lg:h-[325px] overflow-hidden"
    >
      <div
        className="absolute -inset-x-[50px] -bottom-[50px] top-0 blur-[50px] lg:blur-[86px]"
        style={{
          transform: "scaleX(-1)",
          background:
            "linear-gradient(90deg, rgba(255,121,73,0.30) 0%, rgba(161,196,119,0.30) 33%, rgba(172,113,204,0.30) 66%, rgba(133,174,255,0.30) 100%)",
          maskImage:
            "radial-gradient(ellipse 120% 100% at 50% 100%, black 0%, black 40%, transparent 80%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 120% 100% at 50% 100%, black 0%, black 40%, transparent 80%)",
        }}
      />
    </div>
  );
}

function CardTopShade() {
  return (
    <div
      aria-hidden="true"
      className="absolute inset-x-0 top-0 min-h-[173px] lg:min-h-[236px] rounded-t-[20px] lg:rounded-t-[30px] bg-gradient-to-b from-black/40 via-black/30 to-transparent"
    />
  );
}

function CardHeader({ title, body, light }) {
  return (
    <div className="relative z-20 flex flex-col gap-3 px-[25px] pt-[25px] lg:px-[40px] lg:pt-[40px]">
      <h3
        className="text-[28px] lg:text-[36px]"
        style={{ fontFamily: SANS, fontWeight: 300, lineHeight: 1.1, letterSpacing: "-0.015em" }}
      >
        {title}
      </h3>
      <p
        className="text-[16px] lg:text-[18px] max-w-[320px] lg:max-w-[460px]"
        style={{
          fontFamily: SANS,
          fontWeight: 300,
          lineHeight: 1.625,
          color: light ? "rgba(255,255,255,0.85)" : "rgba(0,0,0,0.65)",
        }}
      >
        {body}
      </p>
    </div>
  );
}

const TASK_CHIPS = [
  { label: "Write a report", tag: "Work" },
  { label: "Call Alex", tag: "Personal" },
  { label: "Go to the gym", tag: "Health" },
];

function TaskChips() {
  return (
    <div
      className="absolute z-0 flex w-full justify-center left-0"
      style={{ top: "calc(50% + var(--shift))", transform: "translateY(-50%)" }}
    >
      <div className="relative w-full" style={{ maxWidth: "100%", width: 516, containerType: "inline-size" }}>
        <ul className="flex flex-col items-center" style={{ gap: "2cqi" }}>
          {TASK_CHIPS.map((c) => (
            <li
              key={c.label}
              className="flex items-center backdrop-blur-[10px]"
              style={{
                width: "82%",
                padding: "2.1cqi 2.4cqi",
                borderRadius: "2.4cqi",
                backgroundColor: "rgba(255,255,255,0.8)",
              }}
            >
              <span
                aria-hidden="true"
                className="flex shrink-0 items-center justify-center"
                style={{
                  width: "4.4cqi",
                  height: "4.4cqi",
                  borderRadius: "1.1cqi",
                  borderWidth: "0.26cqi",
                  borderStyle: "dashed",
                  borderColor: "rgba(0,0,0,0.28)",
                }}
              />
              <span
                className="relative ml-[2.4cqi] whitespace-nowrap"
                style={{
                  fontFamily: SANS,
                  fontWeight: 300,
                  fontSize: "4.3cqi",
                  lineHeight: 1.05,
                  letterSpacing: "-0.01em",
                  color: "#0B0F11",
                }}
              >
                {c.label}
              </span>
              <span
                className="ml-auto inline-flex shrink-0 items-center rounded-full"
                style={{
                  backgroundColor: "rgb(242,254,128)",
                  color: "rgb(11,15,17)",
                  fontFamily: SANS,
                  fontSize: "2.9cqi",
                  lineHeight: 1,
                  letterSpacing: "-0.005em",
                  padding: "1.2cqi 2.1cqi",
                  gap: "0.8cqi",
                }}
              >
                <span aria-hidden="true" className="rounded-full bg-current" style={{ width: "1cqi", height: "1cqi" }} />
                {c.tag}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

const HIGHLIGHT_CARDS = [
  {
    key: "talk",
    bgImage: "/assets/images/cheerful-phone-user.jpg",
    light: true,
    title: (
      <>
        Just open and <Serif>talk</Serif>
      </>
    ),
    body: "Open Novu in the morning and say what's on your mind. It transcribes you, pulls out the tasks, and writes them up so you don't have to.",
  },
  {
    key: "structure",
    bgColor: "#ffffff",
    textColor: "#010703",
    light: false,
    title: (
      <>
        Structure in <Serif>seconds</Serif>
      </>
    ),
    body: "Novu reads what you said, finds the real tasks inside it, and lays out your full day in less time than it takes to pour coffee.",
    media: {
      type: "img",
      src: "/assets/images/unknown-2.img",
      alt: "Novu turning a spoken morning update into a structured list of tasks for the day",
      top: "calc(34% + var(--shift))",
      maxWidth: "52%",
    },
  },
  {
    key: "three",
    bgImage: "/assets/images/contemplative-back.jpg",
    light: true,
    title: (
      <>
        The power of <Serif>three</Serif>
      </>
    ),
    body: "You always pick three priorities. Not five, not ten. The constraint forces clarity and gives every day a real shape before it starts.",
    media: { type: "chips" },
  },
  {
    key: "wrist",
    bgImage: "/assets/images/misty-cabin.jpg",
    light: true,
    title: (
      <>
        Right from your <Serif>wrist</Serif>
      </>
    ),
    body: "Glance at your three priorities, capture a quick task by voice, and tick off what you finished without ever reaching for your phone.",
    media: {
      type: "img",
      src: "/assets/images/unknown-3.img",
      alt: "Novu on Apple Watch showing the day's three priorities ready to check off",
      top: "calc(50% + var(--shift))",
      transform: "translateY(-50%)",
      maxWidth: "70%",
    },
  },
  {
    key: "weekly",
    bgColor: "#ffffff",
    textColor: "#010703",
    light: false,
    title: (
      <>
        A weekly <Serif>moment</Serif>
      </>
    ),
    body: "Every Sunday Novu turns your week into a Word, a pattern, a highlight, and a challenge for the week ahead. It's a moment, not a dashboard.",
    media: { type: "phone", src: "/assets/images/unknown-4.img", alt: "Novu's Sunday weekly insights screen summarising the past week" },
  },
];

function HighlightCard({ card }) {
  const frameStyle = {
    boxShadow: "0 24px 60px -30px rgba(0,0,0,0.55)",
    "--shift": "0px",
  };
  if (card.bgImage) {
    frameStyle.backgroundImage = `url("${card.bgImage}")`;
    frameStyle.backgroundSize = "cover";
    frameStyle.backgroundPosition = "center";
  } else if (card.bgColor) {
    frameStyle.backgroundColor = card.bgColor;
  }
  if (card.textColor) frameStyle.color = card.textColor;

  return (
    <div
      className="[scroll-snap-align:start] [scroll-snap-stop:always]"
      style={{ width: 737, maxWidth: "100%" }}
    >
      <article className="shrink-0 select-none">
        <div className={`${CARD_FRAME} ${card.light ? "text-white" : ""}`} style={frameStyle}>
          {card.bgImage && <CardTopShade />}
          {card.bgImage && <CardGradientGlow />}
          <CardHeader title={card.title} body={card.body} light={card.light} />

          {card.media && card.media.type === "img" && (
            <div
              className="absolute z-0 flex w-full justify-center left-0"
              style={{ top: card.media.top, transform: card.media.transform }}
            >
              <img
                alt={card.media.alt}
                className="block h-auto select-none object-cover"
                decoding="async"
                draggable="false"
                loading="lazy"
                src={card.media.src}
                style={{ color: "transparent", width: "100%", maxWidth: card.media.maxWidth }}
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }}
              />
            </div>
          )}

          {card.media && card.media.type === "chips" && <TaskChips />}

          {card.media && card.media.type === "phone" && (
            <div
              className="absolute z-0 flex w-full justify-center left-0"
              style={{ top: "calc(30% + var(--shift))" }}
            >
              <div className="flex w-full justify-center">
                <PhoneMockup screenSrc={card.media.src} screenAlt={card.media.alt} />
              </div>
            </div>
          )}
        </div>
      </article>
    </div>
  );
}

// ---- Privacy band (dark) ----
function PrivacyBand() {
  const [spot, setSpot] = useState({ mx: "50%", my: "-50%", on: 0 });
  return (
    <section className="relative z-20 bg-white text-black" style={{ fontFamily: SANS }}>
      <div className="px-5 py-16 md:px-10 md:py-24">
        <div
          className="relative flex min-h-[480px] items-center justify-center overflow-hidden rounded-[20px] md:rounded-[30px] text-white md:h-[calc(78svh-32px)] md:max-h-[800px] md:min-h-[600px]"
          style={{
            backgroundColor: "rgb(1,7,3)",
            boxShadow: "0 24px 60px -30px rgba(0,0,0,0.55)",
            "--mx": spot.mx,
            "--my": spot.my,
            "--spotlight": spot.on,
          }}
          onMouseMove={(e) => {
            const r = e.currentTarget.getBoundingClientRect();
            setSpot({ mx: `${e.clientX - r.left}px`, my: `${e.clientY - r.top}px`, on: 1 });
          }}
          onMouseLeave={() => setSpot((s) => ({ ...s, on: 0 }))}
        >
          {/* lime glow */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(circle at 50% 0%, rgba(242,254,128,0) 35%, rgba(242,254,128,0.1) 80%, rgba(242,254,128,0.25) 100%)",
            }}
          />
          {/* padlock graphic */}
          <svg
            aria-hidden="true"
            className="pointer-events-none absolute left-1/2 top-1/2 h-[55%] w-auto -translate-x-1/2 -translate-y-1/2 md:left-3/4 md:h-[70%]"
            style={{ opacity: 0.09 }}
            viewBox="0 0 200 280"
          >
            <defs>
              <linearGradient id="lockBody" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
                <stop offset="55%" stopColor="#ffffff" stopOpacity="0.78" />
                <stop offset="100%" stopColor="#ffffff" stopOpacity="0.42" />
              </linearGradient>
              <linearGradient id="lockShackle" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stopColor="#ffffff" stopOpacity="0.55" />
                <stop offset="50%" stopColor="#ffffff" stopOpacity="1" />
                <stop offset="100%" stopColor="#ffffff" stopOpacity="0.55" />
              </linearGradient>
              <linearGradient id="lockShine" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
                <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
              </linearGradient>
              <radialGradient cx="0.5" cy="1" fx="0.5" fy="1" id="lockBaseShade" r="0.6">
                <stop offset="0%" stopColor="#000000" stopOpacity="0.45" />
                <stop offset="100%" stopColor="#000000" stopOpacity="0" />
              </radialGradient>
            </defs>
            <path
              d="M100 22c-31 0-56 25-56 56v52h20V78c0-20 16-36 36-36s36 16 36 36v52h20V78c0-31-25-56-56-56z"
              fill="url(#lockShackle)"
            />
            <rect fill="url(#lockBody)" height="150" rx="16" ry="16" width="164" x="18" y="114" />
            <rect fill="url(#lockShine)" height="44" rx="16" ry="16" width="164" x="18" y="114" />
            <rect fill="url(#lockBaseShade)" height="90" rx="16" ry="16" width="164" x="18" y="174" />
            <circle cx="100" cy="180" fill="rgba(0,0,0,0.35)" r="9" />
            <path d="M96 180 h8 l-2 24 h-4 z" fill="rgba(0,0,0,0.35)" />
          </svg>

          {/* copy */}
          <div className="relative z-10 mx-auto max-w-2xl px-6 py-24 text-center md:absolute md:inset-y-0 md:left-0 md:mx-0 md:flex md:max-w-none md:flex-col md:justify-center md:px-[8%] md:py-0 md:text-left">
            <div className="md:max-w-[460px]">
              <h2
                className="text-[36px] md:text-[48px]"
                style={{ fontFamily: SANS, fontWeight: 300, lineHeight: 1.05, letterSpacing: "-0.015em" }}
              >
                Built for <Serif>privacy.</Serif>
              </h2>
              <p
                className="mx-auto mt-5 max-w-xl text-[17px] md:mx-0 md:text-[18px]"
                style={{ fontFamily: SANS, fontWeight: 300, lineHeight: 1.625, color: "rgba(255,255,255,0.65)" }}
              >
                Your data remains on your device. We never sell it, never share it, and protect it with
                industry-standard security. Just anonymous analytics to make the app better.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Section2Section() {
  const featuresRef = useRef(null);
  const videoRefs = useRef([]);
  const videoRefsMobile = useRef([]);
  const [activeIndex, setActiveIndex] = useState(0);

  // Map scroll progress through the (tall, pinned) feature section onto one of the
  // four feature/video stops, so the phone's demo changes as you scroll.
  useEffect(() => {
    const el = featuresRef.current;
    if (!el) return;
    let raf = 0;
    const update = () => {
      raf = 0;
      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight || 1;
      const total = rect.height - vh; // scrollable distance while the phone is pinned
      const scrolled = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
      const progress = total > 0 ? scrolled / total : 0;
      const idx = Math.min(PHONE_VIDEOS.length - 1, Math.max(0, Math.floor(progress * PHONE_VIDEOS.length - 1e-6)));
      setActiveIndex((prev) => (prev === idx ? prev : idx));
    };
    const onScroll = () => {
      if (!raf) raf = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) window.cancelAnimationFrame(raf);
    };
  }, []);

  // Play only the active video; pause the rest (keeps decoding light and matches
  // the original, where the off-screen layers are idle).
  useEffect(() => {
    [videoRefs, videoRefsMobile].forEach((group) => {
      group.current.forEach((v, i) => {
        if (!v) return;
        if (i === activeIndex) {
          const p = v.play();
          if (p && typeof p.catch === "function") p.catch(() => {});
        } else {
          v.pause();
        }
      });
    });
  }, [activeIndex]);

  return (
    <div style={{ fontFamily: SANS }}>
      {/* ===== Feature scroll block (alternating copy + center phone) ===== */}
      <section
        ref={featuresRef}
        className="relative z-10 bg-white text-black rounded-t-[24px] md:rounded-t-[48px]"
        id="features"
      >
        {/* Desktop: 3-column alternating layout */}
        <div className="mx-auto hidden max-w-[80rem] px-5 md:block md:px-10">
          <div className="grid grid-cols-[1fr_auto_1fr] items-stretch gap-8 lg:gap-16">
            {/* left column */}
            <div className="relative z-10 flex flex-col">
              {FEATURE_BLOCKS.map((b, i) =>
                b.side === "left" ? (
                  <div key={i} className="flex h-[80svh] items-center justify-start">
                    <FeatureCopy title={b.title} body={b.body} />
                  </div>
                ) : (
                  <div key={i} className="flex h-[80svh] items-center justify-start" />
                )
              )}
            </div>

            {/* center sticky phone — renders unknown-1.img as its screen */}
            <div className="relative" style={{ flex: "0 0 auto" }}>
              <div className="sticky top-0 flex h-[100svh] items-center justify-center py-[10svh]">
                <div
                  aria-hidden="true"
                  className="pointer-events-none absolute left-1/2 top-0 z-0 h-full w-screen -translate-x-1/2 rounded-t-[24px] md:rounded-t-[48px]"
                  style={{
                    background:
                      "radial-gradient(80% 75% at 18% 28%, rgba(238,228,250,0.55), transparent 72%), radial-gradient(90% 85% at 82% 70%, rgba(218,232,248,0.6), transparent 72%)",
                    maskImage: "linear-gradient(black 0%, black 68%, transparent 100%)",
                    WebkitMaskImage: "linear-gradient(black 0%, black 68%, transparent 100%)",
                  }}
                />
                <div className="relative z-10">
                  <div
                    aria-hidden="true"
                    className="pointer-events-none absolute left-1/2 top-full h-[140px] w-[140%] -translate-x-1/2 -translate-y-[30%]"
                    style={{
                      borderRadius: "50%",
                      background:
                        "radial-gradient(ellipse at center, rgba(0,0,0,0.22), rgba(0,0,0,0.08) 45%, transparent 70%)",
                      filter: "blur(24px)",
                    }}
                  />
                  <ScrollPhone activeIndex={activeIndex} videoRefs={videoRefs} />
                </div>
              </div>
            </div>

            {/* right column */}
            <div className="relative z-10 flex flex-col">
              {FEATURE_BLOCKS.map((b, i) =>
                b.side === "right" ? (
                  <div key={i} className="flex h-[80svh] items-center justify-start">
                    <FeatureCopy title={b.title} body={b.body} />
                  </div>
                ) : (
                  <div key={i} className="flex h-[80svh] items-center justify-start" />
                )
              )}
            </div>
          </div>
        </div>

        {/* Mobile: stacked phone + copy */}
        <div className="md:hidden px-5 py-16">
          <div className="origin-center scale-[0.85] mx-auto mb-10">
            <ScrollPhone activeIndex={activeIndex} videoRefs={videoRefsMobile} />
          </div>
          <div className="flex flex-col gap-12">
            {FEATURE_BLOCKS.map((b, i) => (
              <FeatureCopy key={i} title={b.title} body={b.body} center />
            ))}
          </div>
        </div>
      </section>

      {/* ===== Highlights carousel ===== */}
      <section className="relative z-10 bg-white pt-12 pb-12 text-black md:pt-20 md:pb-20">
        <div
          className="scrollbar-hide flex select-none gap-4 lg:gap-6 overflow-x-auto px-5 py-20 md:px-10 md:py-24"
          style={{
            scrollPaddingLeft: "1.25rem",
            scrollSnapType: "x mandatory",
            msOverflowStyle: "none",
            scrollbarWidth: "none",
          }}
        >
          {HIGHLIGHT_CARDS.map((card) => (
            <HighlightCard key={card.key} card={card} />
          ))}
        </div>
      </section>

      {/* ===== Privacy band ===== */}
      <PrivacyBand />
    </div>
  );
}
