import React, { useState } from 'react';

const features = [
  { title: 'Designed to feel like a conversation', body: 'Chat with your Muse in the same way you message with other people, using the Muse app on mobile, Mac, or directly in WhatsApp. It’s simple, just tell Muse what you want to get done.', art: 'chat' },
  { title: 'A secure computer with a browser shared by you and your agent', body: 'Muse can browse, click, and complete tasks with you. You always see what is happening, and your private sessions stay protected in a separate, secure computer.', art: 'browser' },
  { title: 'Always working on your goals and suggesting ideas', body: 'Muse keeps your priorities in view. It can spot the next useful step, prepare options, and help you move forward while you focus on the things that matter.', art: 'goals' },
  { title: 'Works with your apps and builds its own tools', body: 'From email and calendar to research and shopping, Muse connects the apps you already use and can create small tools that make repeat tasks effortless.', art: 'tools' },
];

const stories = [
  { person: 'Ryan Serhant', muse: 'Pumpkin', art: 'pink', copy: 'talks through how his Muse gets tasks done' },
  { person: 'Ashley Graham’s', muse: 'Lux', art: 'lavender', copy: 'helps her organize her whole life' },
  { person: 'Teyana Taylor', muse: 'AunTEY', art: 'orange', copy: 'problem solves with her Muse' },
  { person: 'Ally Love’s', muse: 'Mango', art: 'green', copy: 'helps her stay on top of business' },
];

const faqs = [
  ['What can Muse do?', 'Muse can help with everyday computer work: planning, research, email and calendar tasks, shopping, creating content, and organizing information across your apps.'],
  ['How does Muse work?', 'Tell Muse what you need in a chat. It breaks a goal into steps, works across a secure browser and your connected apps, and checks in whenever your approval is needed.'],
  ['Is Muse free?', 'Muse is currently available as an early access experience. Availability and pricing can change as new capabilities roll out.'],
  ['Is Muse safe?', 'Your credentials stay in a protected store and Muse cannot read them. You decide which actions can happen, and every action has a complete audit trail.'],
  ['Does Muse keep working after I close the app?', 'Muse can continue working on tasks you have started, then notify you when it needs a decision or has finished.'],
  ['Does Muse ask before it acts on my behalf?', 'Yes. Muse asks for approval before critical actions such as sending messages, making purchases, or changing important settings.'],
  ['What is a personal AI agent?', 'A personal AI agent is software that can plan and take actions for you across tools, with your goals and preferences guiding the work.'],
  ['How is a personal agent different from a chatbot or AI assistant?', 'A chatbot answers questions. An agent can carry a goal through multiple steps, use tools, and return with proof of what it completed.'],
  ['What can a personal AI agent help with?', 'Anything from a thoughtful travel plan to keeping a busy inbox organized—Muse is designed to take busywork off your plate.'],
];

function MetaMark() {
  return <span className="meta-mark" aria-hidden="true"><i></i><i></i><i></i></span>;
}
function Arrow({ direction = 'right' }) {
  return <span className={`arrow arrow-${direction}`} aria-hidden="true">{direction === 'right' ? '↗' : '↖'}</span>;
}
function PlayButton({ playing, onClick }) {
  return <button className="play-button" aria-label={playing ? 'Pause video' : 'Play video'} onClick={onClick}><span>{playing ? 'Ⅱ' : '▶'}</span></button>;
}
function Pill({ children, href = '#try-muse' }) {
  return <a className="pill" href={href} target={href.startsWith('http') ? '_blank' : undefined} rel={href.startsWith('http') ? 'noreferrer' : undefined}>{children}<Arrow /></a>;
}

export default function App() {
  const [feature, setFeature] = useState(0);
  const [story, setStory] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

  const nextStory = () => setStory((story + 1) % stories.length);
  const prevStory = () => setStory((story - 1 + stories.length) % stories.length);

  return <div className="site-shell">
    <header className="site-nav">
      <a className="brand" href="#top" aria-label="Meta AI home"><MetaMark /><span>Meta</span></a>
      <nav className="nav-links" aria-label="Primary navigation">
        <a href="#features">Products</a><a href="#security">AI Research</a><a href="#action">Resources</a><a href="#faq">About</a><a href="#download">AI Developers</a>
      </nav>
      <a className="nav-cta" href="https://applink.muse.ai/" target="_blank" rel="noreferrer">Try Muse</a>
      <button className="menu-button" aria-label="Open menu"><span></span><span></span></button>
    </header>

    <main id="top">
      <section className="hero" aria-label="Muse introduction">
        <div className="hero-water"></div><div className="hero-orbit orbit-one"></div><div className="hero-orbit orbit-two"></div>
        <div className="hero-copy"><span className="hero-kicker">MUSE</span><h1>Muse does <span className="hero-icon">▱</span><br/>budgeting<br/>while you do you</h1><Pill href="#features">Meet Muse</Pill></div>
        <div className="scroll-hint"><span>Scroll to explore</span><b>↓</b></div><div className="hero-caption">Your personal AI agent</div>
      </section>

      <section className="intro section-pad">
        <div className="section-label">MEET MUSE</div>
        <div className="intro-grid"><h2>What Muse can do for you while you get on with life</h2><p>Muse gets to know you and your goals, working across all aspects of life so you can focus on the things that matter. It comes with strong privacy and security built in, keeping you in control.</p></div>
      </section>

      <section className="features section-pad" id="features">
        <div className="section-label">MUSE FEATURES</div><h2>Take the busywork<br className="desktop"/> off your plate</h2>
        <div className="feature-layout">
          <div className="feature-tabs">{features.map((item, i) => <button key={item.title} className={feature === i ? 'active' : ''} onClick={() => setFeature(i)}><span>{String(i + 1).padStart(2, '0')}</span><strong>{item.title}</strong><em>+</em></button>)}</div>
          <div className={`feature-art art-${features[feature].art}`}><div className="art-noise"></div><div className="phone-frame"><div className="phone-head"><span>Muse</span><span>•••</span></div><div className="bubble bubble-a">What would you like to get done?</div><div className="bubble bubble-b">Find a better flight and keep it under $400.</div><div className="bubble bubble-c">I’ll look into that now ✦</div><div className="phone-input">Message Muse <span>↑</span></div></div><div className="browser-window"><div className="browser-top"><i></i><i></i><i></i></div><div className="browser-lines"><b></b><b></b><b></b><b></b></div></div></div>
        </div>
        <div className="feature-copy"><p>{features[feature].body}</p><a href="#try-muse">Try Muse <Arrow /></a></div>
      </section>

      <section className="security section-pad" id="security">
        <div className="section-label">SECURE AND IN CONTROL</div>
        <div className="security-grid"><div><h3>Your personal data is safe and secure</h3><p>Your logins are kept in a secure credential store your agent can't read, with 1Password integration coming soon. When shopping, a one-time card number is generated at checkout so your real card is never seen by the merchant or your agent.</p><a href="#security">Learn about security <Arrow /></a></div><div><h3>Approve critical actions from your agent</h3><p>Review and approve actions from Muse before they happen, like sending emails and making purchases. See a complete audit trail of everything your agent has done and what it is planning to do.</p><a href="#faq">How approvals work <Arrow /></a></div></div>
      </section>

      <section className="action section-pad" id="action"><div className="section-label">MUSE IN ACTION</div><div className="split-heading"><h2>See how Muse works for you</h2><p>From email and calendar management to saving money, improving your health, and shopping smarter. Muse handles it all.</p></div><Pill href="#try-muse">Try Muse</Pill>
        <div className="video-card action-video"><div className="video-glow"></div><div className="video-ui"><span>MUSE / 01</span><PlayButton playing={playing} onClick={() => setPlaying(!playing)} /></div><div className="video-title">A little more time<br/><i>for what matters.</i></div><div className="video-progress"><span></span></div></div>
      </section>

      <section className="stories section-pad"><div className="section-label">CREATOR STORIES</div><h2>Get inspired</h2><div className="split-heading"><p>Muse is helping people manage and achieve their goals and everyday tasks.</p><div className="carousel-controls"><button onClick={prevStory} aria-label="Previous story">←</button><span>{String(story + 1).padStart(2, '0')} / 04</span><button onClick={nextStory} aria-label="Next story">→</button></div></div>
        <div className="story-track"><div className={`story-card story-${stories[story].art}`}><div className="story-art"><div className="story-orb"></div><span className="story-overlay">MUSE</span><PlayButton playing={false} onClick={() => setPlaying(true)} /></div><div className="story-caption"><strong>{stories[story].person}</strong> {stories[story].copy}<small>{stories[story].muse} · Muse</small></div></div><div className="story-side"><div className="side-orbit"></div><span>Make room<br/>for more.</span></div></div>
        <div className="story-dots">{stories.map((s, i) => <button key={s.muse} className={story === i ? 'active' : ''} onClick={() => setStory(i)} aria-label={`Show story ${i + 1}`}></button>)}</div>
      </section>

      <section className="download section-pad" id="download"><div className="download-art"><div className="mac-window"><div className="mac-top"><i></i><i></i><i></i><span>Muse</span></div><div className="mac-body"><div className="mac-sidebar"></div><div className="mac-main"><span className="mac-chip">GOOD MORNING</span><h4>What can I help<br/>you get done?</h4><div className="mac-line"></div><div className="mac-line short"></div></div></div></div></div><div className="download-copy"><div className="section-label">MUSE FOR MAC</div><h2>Download Muse<br/>for Mac</h2><p>Muse works with your desktop computer files, apps and browser tabs.</p><div className="download-actions"><a className="pill" href="#download">Download for macOS <Arrow /></a><a className="text-link" href="#faq">Learn more <Arrow /></a></div></div></section>

      <section className="try-section" id="try-muse"><div className="try-orb orb-a"></div><div className="try-orb orb-b"></div><div className="try-content"><div className="section-label">TRY MUSE</div><h2>Ready to get more done<br/>with Muse?</h2><a className="pill light" href="https://applink.muse.ai/" target="_blank" rel="noreferrer">Get started <Arrow /></a></div></section>

      <section className="faq section-pad" id="faq"><div className="section-label">FREQUENTLY ASKED QUESTIONS</div><h2>Questions, answered</h2><div className="faq-list">{faqs.map(([q, a], i) => <div className={`faq-item ${openFaq === i ? 'open' : ''}`} key={q}><button onClick={() => setOpenFaq(openFaq === i ? null : i)}><span>{q}</span><b>{openFaq === i ? '−' : '+'}</b></button>{openFaq === i && <p>{a}</p>}</div>)}</div></section>

      <section className="products section-pad"><div className="section-label">EXPLORE META AI PRODUCTS</div><h2>More ways to<br/>make more</h2><div className="product-grid"><article className="product-card product-meta"><div className="product-art"><div className="meta-ring"></div><div className="meta-phone">✦</div></div><div className="product-info"><span>Meta AI Assistant</span><h3>Get more done with Meta AI, your personal AI assistant.</h3><div><a href="#top">Try Meta AI <Arrow /></a><a href="#top">Learn more <Arrow /></a></div></div></article><article className="product-card product-image"><div className="product-art"><div className="image-stack"><i></i><i></i><i></i></div></div><div className="product-info"><span>Image Generation</span><h3>Explore fun presets, make precise edits and visualize your ideas.</h3><div><a href="#top">Start generating <Arrow /></a><a href="#top">Learn more <Arrow /></a></div></div></article></div></section>
    </main>

    <footer className="footer"><div className="footer-top"><a className="brand" href="#top"><MetaMark /><span>Meta</span></a><div className="socials"><a href="#top">f</a><a href="#top">◎</a><a href="#top">𝕏</a><a href="#top">▶</a><a href="#top">⌘</a></div></div><div className="footer-cols"><div><h4>Meta AI</h4><a href="#top">Assistant</a><a href="#top">Media Generation</a><a href="#top">Vibes</a></div><div><h4>Muse</h4><a href="#top">Agent</a><a href="#faq">AI agents explained</a><a href="#faq">What is agentic AI</a><a href="#faq">Agentic AI examples</a></div><div><h4>AI Research</h4><a href="#top">Overview</a><a href="#top">Projects</a><a href="#top">Resources & tools</a><a href="#top">Publications</a></div><div><h4>Resources</h4><a href="#top">Blog</a><a href="#top">Learning Hub</a><a href="#top">Demos</a></div><div><h4>About</h4><a href="#top">Overview</a><a href="#top">Open Source</a><a href="#top">Careers</a></div><div><h4>Legal</h4><a href="#top">Privacy Policy</a><a href="#top">Terms</a><a href="#top">Cookies</a></div></div><div className="footer-bottom"><span>© 2025 Meta Platforms, Inc.</span><span>English (US)⌄</span></div></footer>
  </div>;
}
