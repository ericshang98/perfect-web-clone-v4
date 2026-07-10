// Minimal interaction layer for the static PDP clone.
// Faithful-clone scope: header sticky shadow on scroll + gallery page-dot sync.
// Deliberately NO $100 popup / drawer scrim (those obscure the page and are not
// part of the captured product-page reference).
export function initInteractions() {
  if (typeof document === 'undefined') return;

  // header sticky shadow
  const header = document.querySelector('.pwc-header, header .Header, .Header');
  const onScroll = () => {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 8);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // gallery stack: highlight the dot nearest the viewport centre
  const dots = [...document.querySelectorAll('.Product__SlideshowNav--dots a, .Product__SlideshowNav--dots button, .pwc-dots li')];
  const slides = [...document.querySelectorAll('.Product__SlideItem, .Product__Slide')];
  if (dots.length && slides.length) {
    const sync = () => {
      const mid = window.scrollY + window.innerHeight / 2;
      let best = 0, bestD = Infinity;
      slides.forEach((s, i) => {
        const r = s.getBoundingClientRect();
        const c = window.scrollY + r.top + r.height / 2;
        const d = Math.abs(c - mid);
        if (d < bestD) { bestD = d; best = i; }
      });
      dots.forEach((d, i) => d.classList.toggle('is-on', i === best));
    };
    window.addEventListener('scroll', sync, { passive: true });
    sync();
  }
}
