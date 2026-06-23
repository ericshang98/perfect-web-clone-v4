import { useState } from "react";

const SANS = "Inter, ui-sans-serif, system-ui, sans-serif";
const SERIF = "Lora, Georgia, 'Times New Roman', serif";
const ORANGE = "#fe4e02";

const serifStyle = {
  fontFamily: SERIF,
  letterSpacing: "-0.01em",
  fontStyle: "normal",
  fontWeight: 400,
};

const testimonials = [
  "Finally a planner that fits how my brain actually works. I talk, it listens, and my day makes sense before my coffee is cold.",
  "I used to open three apps to write one task. Novu is just voice in, plan out. It's ridiculous how much calmer my mornings feel.",
  "Three priorities a day. That one constraint changed my week more than any productivity system I've tried.",
  "It doesn't nag or buzz. It just quietly organises what I say and gives me back the only list I needed.",
  "The evening wrap-up has become my favourite two minutes of the day. Quiet, honest, and somehow always encouraging.",
  "I'm ADHD and every planner has failed me. Novu is the first one that doesn't expect me to be someone I'm not.",
];

const faqs = [
  {
    q: "How is Novu different from other to-do apps?",
    a: "Most to-do apps give you more lists, more buttons, more rules. Novu runs the opposite way. You talk in the morning, it organises everything you said into real tasks, and then it asks you to choose three priorities for the day. No more pretending that fifteen things on a list deserve the same attention.",
  },
  {
    q: "How does the voice capture work?",
    a: "Open Novu in the morning and just talk. No prompts, no structure, no format. Novu transcribes your speech, pulls out the tasks, writes a description from context, and suggests a category. Your full day, organised in under a minute. You can still edit, split, or delete anything manually.",
  },
  {
    q: "Why only three priorities a day?",
    a: "Choosing three is the most important thing you'll do each morning, and it's based on science to improve productivity. Everything else is still there in your day view and your backlog, but only three things get the spotlight.",
  },
  {
    q: "What is the evening wrap-up?",
    a: "It's like a quick voice journal note that actually shows what you got done. At the end of the day Novu shows you what you finished and what didn't, and anything unfinished moves to tomorrow automatically. A clean close to today, a fair start to the next.",
  },
  {
    q: "What do the weekly insights include?",
    a: "Every Sunday you get an overview of your week — what you focused on, where your energy went, and how your time was divided between work, home, health, and personal life. It surfaces the patterns you might not notice day to day, so you can step back, see yourself clearly, and head into the next week with intention instead of inertia.",
  },
  {
    q: "What if I don't feel like talking?",
    a: "You can add tasks the normal way, just like any to-do app. Tap, type, set a category and a time. Voice is the fast lane (about 4× quicker once you get used to it), but it's never the only way in.",
  },
  {
    q: "Is my data private?",
    a: "Yes. We believe your personal data belongs to you. Your tasks and data are stored locally on your device and synced via your personal iCloud storage. We can’t access that data. Your voice inputs are sent to our secure server only for processing and automatically deleted afterwards — we don't keep copies of your audio.",
  },
  {
    q: "How much does it cost?",
    a: "You start with a full-access 7-day free trial. After that, choose a Monthly or Quarterly subscription. Manage or cancel anytime from your Apple Account settings. Subscriptions auto-renew unless you turn them off at least 24 hours before the period ends.",
  },
];

function StarIcon() {
  return (
    <svg
      aria-hidden="true"
      fill="currentColor"
      viewBox="0 0 24 24"
      style={{ width: 16, height: 16, flex: "0 0 auto" }}
    >
      <path d="M12 2l2.9 6.9 7.1.6-5.4 4.7 1.7 7L12 17.6 5.7 21.2l1.7-7L2 9.5l7.1-.6L12 2z" />
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg
      aria-hidden="true"
      fill="currentColor"
      viewBox="0 0 24 24"
      style={{ width: 17, height: 17, flex: "0 0 auto" }}
    >
      <path d="M16.365 12.56c-.01-2.02 1.65-2.99 1.72-3.04-.94-1.37-2.4-1.55-2.92-1.57-1.23-.12-2.41.73-3.04.73-.63 0-1.6-.71-2.64-.69-1.36.02-2.62.79-3.32 2-1.41 2.44-.36 6.05 1.02 8.03.67.96 1.48 2.04 2.54 2 1.02-.04 1.41-.66 2.65-.66s1.59.66 2.66.64c1.1-.02 1.8-.98 2.47-1.95.78-1.12 1.1-2.2 1.11-2.25-.02-.01-2.13-.82-2.15-3.24zM14.37 6.9c.56-.68.94-1.62.84-2.56-.81.03-1.79.54-2.37 1.22-.52.6-.97 1.56-.85 2.48.9.07 1.82-.46 2.38-1.14z" />
    </svg>
  );
}

function TestimonialCard({ quote }) {
  return (
    <article
      className="relative flex shrink-0 flex-col justify-between"
      style={{
        width: 420,
        maxWidth: "100%",
        backgroundColor: "rgb(255, 255, 255)",
        borderRadius: 40,
        padding: 32,
        minHeight: 320,
        boxShadow:
          "rgba(0, 0, 0, 0.035) 0px -4px 32px -12px, rgba(0, 0, 0, 0.024) 0px 1px 2px, rgba(0, 0, 0, 0.05) 0px 12px 36px -14px, rgba(0, 0, 0, 0.043) 0px 28px 60px -24px",
      }}
    >
      <div className="flex gap-1" style={{ color: ORANGE }}>
        <StarIcon />
        <StarIcon />
        <StarIcon />
        <StarIcon />
        <StarIcon />
      </div>
      <p
        className="mt-6 flex-1"
        style={{
          fontSize: 21,
          lineHeight: 1.45,
          color: "rgba(0,0,0,0.85)",
        }}
      >
        {"“" + quote + "”"}
      </p>
      <div
        className="mt-8 flex items-center gap-2.5"
        style={{ fontSize: 15, color: "rgba(0,0,0,0.45)" }}
      >
        <AppleIcon />
        <span>Early User Feedback</span>
      </div>
    </article>
  );
}

function FaqItem({ item, isOpen, onToggle }) {
  return (
    <div style={{ borderBottom: "1px solid rgba(0,0,0,0.1)" }}>
      <button
        type="button"
        aria-expanded={isOpen}
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-6 py-6 text-left"
        style={{
          fontSize: 18,
          fontWeight: 400,
          color: "#000",
          fontFamily: SANS,
        }}
      >
        <span>{item.q}</span>
        <span
          aria-hidden="true"
          className="relative shrink-0"
          style={{
            width: 16,
            height: 16,
            color: "rgba(0,0,0,0.6)",
            transition: "transform 400ms cubic-bezier(0.4,0,0.2,1)",
            transform: isOpen ? "rotate(45deg)" : "rotate(0deg)",
          }}
        >
          <span
            className="absolute"
            style={{
              left: 0,
              right: 0,
              top: "50%",
              height: "1.5px",
              transform: "translateY(-50%)",
              borderRadius: "9999px",
              backgroundColor: "currentColor",
            }}
          />
          <span
            className="absolute"
            style={{
              top: 0,
              bottom: 0,
              left: "50%",
              width: "1.5px",
              transform: "translateX(-50%)",
              borderRadius: "9999px",
              backgroundColor: "currentColor",
            }}
          />
        </span>
      </button>
      <div
        className="grid"
        style={{
          transition: "grid-template-rows 500ms cubic-bezier(0.4,0,0.2,1)",
          gridTemplateRows: isOpen ? "1fr" : "0fr",
        }}
      >
        <div style={{ overflow: "hidden" }}>
          <div
            className="pb-6 pr-10"
            style={{
              fontSize: 16,
              lineHeight: 1.625,
              color: "rgba(0,0,0,0.6)",
              transition: "opacity 300ms",
              opacity: isOpen ? 1 : 0,
            }}
          >
            {item.a}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState(null);
  const marqueeCards = [...testimonials, ...testimonials];

  return (
    <div style={{ fontFamily: SANS }}>
      {/* (A) Testimonials block */}
      <section
        className="relative z-10 bg-white text-black"
        data-nav-theme="light"
      >
        <div className="mx-auto max-w-[80rem] px-5 pt-24 md:px-10 md:pt-32">
          <div className="mx-auto max-w-2xl text-center">
            <h2
              className="font-light"
              style={{
                fontSize: "clamp(36px, 5vw, 48px)",
                lineHeight: 1.05,
                letterSpacing: "-0.015em",
              }}
            >
              From the <span style={serifStyle}>first users.</span>
            </h2>
            <p
              className="mx-auto mt-5 max-w-xl font-light"
              style={{
                fontSize: 18,
                lineHeight: 1.625,
                color: "rgba(0,0,0,0.55)",
              }}
            >
              Honest reactions from people using Novu in their actual mornings.
              Before launch. Before the fanfare.
            </p>
          </div>
        </div>

        <div className="mt-16 overflow-x-clip pb-24 md:pb-32">
          <div
            className="flex gap-6 animate-marquee"
            style={{ width: "max-content" }}
          >
            {marqueeCards.map((quote, i) => (
              <TestimonialCard key={i} quote={quote} />
            ))}
          </div>
        </div>
      </section>

      {/* (B) FAQ accordion */}
      <section
        className="relative z-20 bg-white text-black py-24 md:py-32"
        data-nav-theme="light"
        id="faq"
        style={{
          borderBottomLeftRadius: "2.5rem",
          borderBottomRightRadius: "2.5rem",
        }}
      >
        <div className="mx-auto max-w-[80rem] px-5 md:px-10">
          <div className="mx-auto max-w-2xl text-center">
            <h2
              className="font-light"
              style={{
                fontSize: "clamp(36px, 5vw, 48px)",
                lineHeight: 1.05,
                letterSpacing: "-0.015em",
              }}
            >
              Got <span style={serifStyle}>questions?</span>
            </h2>
          </div>

          <div
            className="mx-auto mt-14 max-w-3xl"
            style={{ borderTop: "1px solid rgba(0,0,0,0.1)" }}
          >
            {faqs.map((item, i) => (
              <FaqItem
                key={i}
                item={item}
                isOpen={openIndex === i}
                onToggle={() => setOpenIndex(openIndex === i ? null : i)}
              />
            ))}
          </div>
        </div>
      </section>

      <style>{`
        @keyframes faq-marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .animate-marquee { will-change: transform; animation: faq-marquee 60s linear infinite; }
        @media (prefers-reduced-motion: reduce) {
          .animate-marquee { animation: none !important; transform: none !important; }
        }
      `}</style>
    </div>
  );
}
