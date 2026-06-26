import { g as gsapWithCSS } from "./lib/50Lx19ak.js";
import { S as ScrollTrigger } from "./lib/C6o_azLH.js";
gsapWithCSS.registerPlugin(ScrollTrigger);
const imageParallax = ({ widget }) => {
  const imageElement = widget.querySelector('[data-role="image"]');
  if (!imageElement) return;
  const fitImage = (imageElement2) => {
    const widgetEl = widget;
    const widgetHeight = widgetEl.offsetHeight;
    const viewportHeight = window.innerHeight;
    const scale = viewportHeight > 1200 ? 1.4 : viewportHeight > 900 ? 1.3 : 1.2;
    const height = Math.ceil(widgetHeight * scale);
    const top = Math.ceil((widgetHeight - height) / 2);
    gsapWithCSS.set(imageElement2, {
      height,
      top
    });
    return { widgetHeight, imageHeight: height };
  };
  const animate = () => {
    const { widgetHeight, imageHeight } = fitImage(imageElement);
    const movement = (imageHeight - widgetHeight) / 2;
    gsapWithCSS.fromTo(
      imageElement,
      {
        y: -movement
      },
      {
        y: movement,
        ease: "none",
        scrollTrigger: {
          trigger: widget,
          start: "top bottom",
          end: "bottom top",
          scrub: true,
          invalidateOnRefresh: true
        }
      }
    );
  };
  animate();
  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => fitImage(imageElement), 50);
  });
};
const WIDGET_SELECTOR = '[data-widget="image-parallax"]';
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
widgets.forEach((widget) => {
  imageParallax({ widget });
});
