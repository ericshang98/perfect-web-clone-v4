import React, { useEffect, useMemo, useState } from "react";

const NAV_LINKS = [
  ["Flip Clock", "/"],
  ["Countdown Timer", "/countdown-timer"],
  ["World Time", "/world-time"],
];

const FEATURES = [
  [
    "Made for Focus",
    "Keep the current time visible without distracting controls or clutter.",
  ],
  [
    "Full-Screen Flip Clock",
    "Fill your monitor, tablet, or shared display with a bold digital flip clock.",
  ],
  [
    "Free in Your Browser",
    "Launch FlipClocker instantly with no download, signup, or setup.",
  ],
];

function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header data-pwc-section="header">
      <nav
        className="top-nav"
        data-pwc-critical="navigation-1"
        data-pwc-compare="navigation"
      >
        <a className="brand" aria-label="FlipClock" href="/">
          FlipClocker
        </a>
        <button
          className="menu-toggle"
          type="button"
          aria-expanded={open}
          aria-controls="main-navigation"
          aria-label="Toggle navigation"
          data-pwc-interaction="mobile-navigation"
          onClick={() => setOpen((value) => !value)}
        >
          <span />
          <span />
          <span />
        </button>
        <div
          id="main-navigation"
          className={`nav-links ${open ? "is-open" : ""}`}
          data-pwc-controlled="mobile-navigation"
        >
          {NAV_LINKS.map(([label, href]) => (
            <a href={href} key={label}>
              {label}
            </a>
          ))}
          <button type="button">City Time</button>
        </div>
      </nav>
    </header>
  );
}

function ClockUnit({ label, value, hiddenLabel }) {
  return (
    <div className="clock-unit" data-clock-unit={label.toLowerCase()}>
      <div className="digit-shell">
        <span className="clock-number">{value}</span>
        <span className="divider" />
      </div>
      {!hiddenLabel && <div className="clock-label">{label}</div>}
    </div>
  );
}

function Controls({
  classic,
  hideSeconds,
  hideLabels,
  settingsOpen,
  onClassic,
  onSettings,
  onSeconds,
  onLabels,
}) {
  const enterFullscreen = () => {
    document.documentElement.requestFullscreen?.();
  };
  return (
    <div className="clock-controls" data-pwc-compare="clock-controls">
      <button
        className="pill pill-primary"
        type="button"
        data-pwc-interaction="fullscreen"
        onClick={enterFullscreen}
      >
        <span className="control-icon">↗</span>
        <span>
          Full Screen
          <small>= No Ads =</small>
        </span>
      </button>
      <button
        className="pill pill-accent"
        type="button"
        aria-pressed={classic}
        data-pwc-interaction="clock-style"
        onClick={onClassic}
      >
        <span className="control-icon">▭</span>
        <span>{classic ? "Modern" : "Classic"}</span>
      </button>
      <div className="settings-wrap">
        <button
          className="pill pill-secondary"
          type="button"
          aria-expanded={settingsOpen}
          aria-controls="clock-settings"
          data-pwc-interaction="clock-settings"
          onClick={onSettings}
        >
          <span className="control-icon">☼</span>
          <span>Settings</span>
        </button>
        <ul
          id="clock-settings"
          className={`settings-menu ${settingsOpen ? "is-open" : ""}`}
          data-pwc-controlled="clock-settings"
        >
          <li>
            <button
              type="button"
              aria-pressed={hideSeconds}
              data-pwc-interaction="toggle-seconds"
              onClick={onSeconds}
            >
              <span>{hideSeconds ? "Show Seconds" : "Hide Seconds"}</span>
              <span aria-hidden="true">◷</span>
            </button>
          </li>
          <li>
            <button
              type="button"
              aria-pressed={hideLabels}
              data-pwc-interaction="toggle-labels"
              onClick={onLabels}
            >
              <span>{hideLabels ? "Show Labels" : "Hide Labels"}</span>
              <span aria-hidden="true">☰</span>
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
}

function ClockHero() {
  const [now, setNow] = useState(() => new Date());
  const [classic, setClassic] = useState(false);
  const [hideSeconds, setHideSeconds] = useState(false);
  const [hideLabels, setHideLabels] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const parts = useMemo(
    () => ({
      hours: String(now.getHours()).padStart(2, "0"),
      minutes: String(now.getMinutes()).padStart(2, "0"),
      seconds: String(now.getSeconds()).padStart(2, "0"),
    }),
    [now],
  );

  return (
    <section
      className={`clock-hero ${classic ? "is-classic" : ""}`}
      aria-labelledby="flip-clock-title"
      data-pwc-critical="hero-1"
    >
      <div className="sr-only">
        <h1 id="flip-clock-title">FlipClocker: Free Online Flip Clock</h1>
        <p>
          Open FlipClocker in your browser for a clean retro flip clock built
          for focus, study, work, meetings, and full-screen display.
        </p>
      </div>
      <div
        className={`live-clock ${hideSeconds ? "hide-seconds" : ""}`}
        aria-label="Live online flip clock showing the current time"
        aria-live="off"
        data-pwc-compare="live-clock"
      >
        <ClockUnit label="HOURS" value={parts.hours} hiddenLabel={hideLabels} />
        <ClockUnit
          label="MINUTES"
          value={parts.minutes}
          hiddenLabel={hideLabels}
        />
        {!hideSeconds && (
          <ClockUnit
            label="SECONDS"
            value={parts.seconds}
            hiddenLabel={hideLabels}
          />
        )}
      </div>
      <Controls
        classic={classic}
        hideSeconds={hideSeconds}
        hideLabels={hideLabels}
        settingsOpen={settingsOpen}
        onClassic={() => setClassic((value) => !value)}
        onSettings={() => setSettingsOpen((value) => !value)}
        onSeconds={() => setHideSeconds((value) => !value)}
        onLabels={() => setHideLabels((value) => !value)}
      />
    </section>
  );
}

function Information() {
  return (
    <section
      className="information"
      data-pwc-critical="hero-2"
      data-pwc-compare="information"
    >
      <h2>A Simple Online Flip Clock for Focus and Display</h2>
      <p>
        FlipClocker turns any browser into a large, easy-to-read flip clock.
        Use the classic animated flip clock at your desk, while studying, in
        meetings, or as an ambient full-screen clock—no account or installation
        required.
      </p>
      <div className="feature-grid">
        {FEATURES.map(([title, body]) => (
          <article key={title}>
            <h3>{title}</h3>
            <p>{body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer
      data-pwc-section="footer"
      data-pwc-critical="footer-1"
      data-pwc-compare="footer"
    >
      <strong>© 2026 FlipClocker</strong>
      <div className="languages" aria-label="Languages">
        <a href="/de/">🇩🇪 DE</a>
        <a className="selected" href="/">
          🇺🇸 EN
        </a>
        <a href="/cn/">🇨🇳 CN</a>
        <a href="/ja/">🇯🇵 JA</a>
        <a href="/ko/">🇰🇷 KO</a>
        <a href="/fr/">🇫🇷 FR</a>
        <a href="/es/">🇪🇸 ES</a>
      </div>
      <nav aria-label="Legal">
        <a href="/privacy">Privacy</a>
        <a href="/terms">Terms</a>
        <button type="button">Cookies</button>
        <span>Thanks for @pqina</span>
      </nav>
    </footer>
  );
}

export default function App() {
  return (
    <>
      <Header />
      <main data-pwc-section="section">
        <ClockHero />
        <Information />
      </main>
      <Footer />
    </>
  );
}
