import Lenis from "lenis";

// Global, mutable scroll state read every frame by the R3F scene.
// NEVER stored in React state — that would re-render the tree at 60fps.
export const scroll = { progress: 0, velocity: 0 };

// Low-frequency subscribers (e.g. the DOM background-colour layer).
const subscribers = new Set();
export function onScroll(fn) {
  subscribers.add(fn);
  fn(scroll.progress);
  return () => subscribers.delete(fn);
}

function computeProgress() {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  scroll.progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
  subscribers.forEach((fn) => fn(scroll.progress));
}

export function initLenis() {
  const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
  lenis.on("scroll", ({ velocity }) => {
    scroll.velocity = velocity;
    computeProgress();
  });

  let raf;
  const loop = (t) => {
    lenis.raf(t);
    raf = requestAnimationFrame(loop);
  };
  raf = requestAnimationFrame(loop);

  computeProgress();
  window.addEventListener("resize", computeProgress);

  // returned cleanup — important so StrictMode double-mount doesn't spawn 2 loops
  return () => {
    cancelAnimationFrame(raf);
    lenis.destroy();
    window.removeEventListener("resize", computeProgress);
  };
}
