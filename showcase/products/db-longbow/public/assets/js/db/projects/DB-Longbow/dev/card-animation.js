import { g as gsapWithCSS } from "./lib/50Lx19ak.js";
import { S as ScrollTrigger } from "./lib/C6o_azLH.js";
const cardAnimation = ({ widget }) => {
  gsapWithCSS.registerPlugin(ScrollTrigger);
  gsapWithCSS.set(widget, {
    opacity: 0,
    y: 50,
    scale: 0.85
  });
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const delayAttr = widget.getAttribute("data-delay");
          const delay = delayAttr ? parseInt(delayAttr) / 1e3 : 0;
          gsapWithCSS.to(widget, {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 1.2,
            ease: "power2.inOut",
            delay
          });
          observer.unobserve(widget);
        }
      });
    },
    { threshold: 0.5 }
    // 50% in view
  );
  observer.observe(widget);
};
const WIDGET_SELECTOR = '[data-widget="card-animation"]';
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
widgets.forEach((widget) => {
  cardAnimation({ widget });
});
