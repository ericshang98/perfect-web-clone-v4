// pagerie runtime interaction layer — faithful reproduction of the live site's effects
// (fade-in images, fade carousels, product hover image-swap, sticky header,
//  search/cart/menu drawers, and the $100-OFF signup popup).

export function initInteractions() {
  // The page is a client-side React render, so the section DOM does not exist at
  // DOMContentLoaded. Wait until the sections are actually mounted before wiring
  // up the runtime effects (otherwise every querySelector finds nothing).
  let tries = 0;
  const boot = () => {
    const ready = document.querySelector('.pwc-footer') && document.querySelector('.flickity-enabled, .ProductItem');
    if (!ready && tries++ < 120) { setTimeout(boot, 40); return; }
    fadeInImages();
    slideCarousels();
    productHover();
    stickyHeader();
    drawers();
    setTimeout(signupPopup, 1600);
  };
  boot();
}

// Images fade in as they "load" (Image--lazyLoad → Image--lazyLoaded)
function fadeInImages() {
  document.querySelectorAll('.Image--lazyLoad').forEach((img) => {
    const show = () => img.classList.add('is-loaded');
    if (img.tagName === 'IMG') {
      if (img.complete) show();
      else img.addEventListener('load', show, { once: true });
    }
    setTimeout(show, 900);
  });
}

// Flickity carousels → real horizontal slide (translateX) with autoPlay, page
// dots and pointer drag, matching the captured data-flickity-config.
function slideCarousels() {
  document.querySelectorAll('.flickity-enabled').forEach((car) => {
    const viewport = car.querySelector('.flickity-viewport');
    const slider = car.querySelector('.flickity-slider');
    if (!slider) return;
    const cells = Array.from(slider.children);
    if (cells.length < 2) return;
    const cfg = car.getAttribute('data-flickity-config') || '';

    if (viewport) viewport.style.overflow = 'hidden';
    slider.style.position = 'relative';
    slider.style.display = 'flex';
    slider.style.left = '0';
    slider.style.transition = 'transform .6s cubic-bezier(.25,.46,.45,.94)';
    cells.forEach((c) => {
      c.style.position = 'relative';
      c.style.left = '0';
      c.style.flex = '0 0 100%';
      c.style.width = '100%';
      c.style.opacity = '1';
    });

    let idx = 0;
    const apply = () => { slider.style.transform = `translateX(${-idx * 100}%)`; if (dots) updateDots(); };
    const go = (i) => { idx = (i + cells.length) % cells.length; apply(); };

    // page dots
    let dots = null;
    if (/pageDots"?\s*:\s*true/.test(cfg)) {
      dots = document.createElement('ol');
      dots.className = 'pwc-dots';
      cells.forEach((_, i) => {
        const d = document.createElement('li');
        d.addEventListener('click', () => { go(i); restart(); });
        dots.appendChild(d);
      });
      car.appendChild(dots);
    }
    function updateDots() {
      Array.from(dots.children).forEach((d, i) => d.classList.toggle('is-on', i === idx));
    }

    // autoplay
    const m = cfg.match(/autoPlay"?\s*:\s*(\d+)/);
    let timer = null;
    const restart = () => { if (!m) return; clearInterval(timer); timer = setInterval(() => go(idx + 1), parseInt(m[1], 10)); };

    // pointer drag
    let down = false, startX = 0;
    viewport && viewport.addEventListener('pointerdown', (e) => { down = true; startX = e.clientX; });
    window.addEventListener('pointerup', (e) => {
      if (!down) return; down = false;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 40) { go(dx < 0 ? idx + 1 : idx - 1); restart(); }
    });

    apply();
    restart();
  });
}

// Product card: swap to the alternate image on hover
function productHover() {
  document.querySelectorAll('.ProductItem').forEach((pi) => {
    const alt = pi.querySelector('.ProductItem__Image--alternate');
    if (!alt) return;
    if (getComputedStyle(pi).position === 'static') pi.style.position = 'relative';
    pi.addEventListener('mouseenter', () => { alt.style.opacity = '1'; });
    pi.addEventListener('mouseleave', () => { alt.style.opacity = '0'; });
  });
}

// Sticky header: keeps following scroll, gains a subtle shadow once scrolled
function stickyHeader() {
  const h = document.querySelector('.pwc-header');
  if (!h) return;
  const onScroll = () => h.classList.toggle('is-scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// Search toggle + cart/menu drawers
function drawers() {
  const closeAll = () => {
    document.querySelectorAll('.Drawer.is-open').forEach((d) => d.classList.remove('is-open'));
    const s = document.querySelector('.Search');
    if (s) s.classList.remove('is-visible');
    document.body.classList.remove('pwc-locked');
    const sc = document.querySelector('.pwc-scrim');
    if (sc) sc.classList.remove('is-open');
  };
  let scrim = document.querySelector('.pwc-scrim');
  if (!scrim) {
    scrim = document.createElement('div');
    scrim.className = 'pwc-scrim';
    scrim.addEventListener('click', closeAll);
    document.body.appendChild(scrim);
  }
  document.querySelectorAll('[data-action="open-drawer"]').forEach((b) =>
    b.addEventListener('click', (e) => {
      e.preventDefault();
      const id = b.getAttribute('data-drawer-id');
      const d = (id && document.getElementById(id)) || document.querySelector('.Drawer');
      if (d) {
        d.classList.add('is-open');
        document.body.classList.add('pwc-locked');
        scrim.classList.add('is-open');
      }
    })
  );
  document.querySelectorAll('[data-action="close-drawer"],[data-action="close-search"],[data-action="close-popover"]').forEach((b) =>
    b.addEventListener('click', (e) => { e.preventDefault(); closeAll(); })
  );
  document.querySelectorAll('[data-action="toggle-search"]').forEach((b) =>
    b.addEventListener('click', (e) => {
      e.preventDefault();
      const s = document.querySelector('.Search');
      if (s) s.classList.toggle('is-visible');
    })
  );
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(); });
}

// The $100-OFF signup popup (Klaviyo modal on the live site)
function signupPopup() {
  if (sessionStorage.getItem('pwc-popup-dismissed')) return;
  const wrap = document.createElement('div');
  wrap.className = 'pwc-popup-overlay';
  wrap.innerHTML = `
    <div class="pwc-popup" role="dialog" aria-modal="true">
      <button class="pwc-popup__close" aria-label="Close">&times;</button>
      <div class="pwc-popup__media">
        <img src="/assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1x1.jpg" alt="PAGERIE" />
      </div>
      <div class="pwc-popup__body">
        <div class="pwc-popup__brand">PAGERIE</div>
        <div class="pwc-popup__kicker">SIGN UP FOR</div>
        <div class="pwc-popup__deal">$100 OFF</div>
        <div class="pwc-popup__sub">YOUR FIRST PURCHASE</div>
        <p class="pwc-popup__legal">By submitting your email address, you agree to receive marketing emails from PAGERIE. Consent is not a condition of purchase.</p>
        <form class="pwc-popup__form">
          <input type="email" placeholder="Email Address" required />
          <button type="submit">GET $100 OFF NOW</button>
        </form>
        <div class="pwc-popup__foot">when you sign up for emails</div>
      </div>
    </div>`;
  document.body.appendChild(wrap);
  const close = () => {
    wrap.classList.remove('is-open');
    sessionStorage.setItem('pwc-popup-dismissed', '1');
    setTimeout(() => wrap.remove(), 320);
  };
  wrap.querySelector('.pwc-popup__close').addEventListener('click', close);
  wrap.addEventListener('click', (e) => { if (e.target === wrap) close(); });
  wrap.querySelector('form').addEventListener('submit', (e) => { e.preventDefault(); close(); });
  requestAnimationFrame(() => wrap.classList.add('is-open'));
}
