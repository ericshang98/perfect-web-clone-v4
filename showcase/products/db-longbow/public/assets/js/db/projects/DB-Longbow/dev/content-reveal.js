const contentReveal = ({ widget }) => {
  const intersectionObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const delayAttr = widget.getAttribute("data-reveal-delay");
          let delayMs = 0;
          if (delayAttr) {
            const parsedDelay = parseInt(delayAttr);
            delayMs = isNaN(parsedDelay) ? 0 : Math.max(0, parsedDelay);
          }
          const applyAnimation = () => {
            widget.setAttribute("data-reveal-state", "finish");
            observer.unobserve(widget);
          };
          if (delayMs > 0) {
            setTimeout(applyAnimation, delayMs);
          } else {
            applyAnimation();
          }
        }
      });
    },
    { threshold: 0.5 }
  );
  if (!widget.hasAttribute("data-reveal")) {
    const POSITIONS_HORIZONTAL = ["left", "center", "right"];
    const POSITIONS_VERTICAL = ["top", "center", "bottom"];
    const positionHorizontal = POSITIONS_HORIZONTAL[Math.floor(Math.random() * 3)];
    const positionVertical = POSITIONS_VERTICAL[Math.floor(Math.random() * 3)];
    widget.setAttribute("data-reveal", `${positionHorizontal} ${positionVertical}`);
  }
  intersectionObserver.observe(widget);
};
const WIDGET_SELECTOR = '[data-widget="content-reveal"]';
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
widgets.forEach((widget) => {
  contentReveal({ widget });
});
