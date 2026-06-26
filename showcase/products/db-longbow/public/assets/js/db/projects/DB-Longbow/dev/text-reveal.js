const textReveal = ({ widget }) => {
  const DURATION = 500;
  const STAGGER = 600;
  const UPDATE_INTERVAL = 80;
  const getRandomBit = () => Math.random() < 0.5 ? "0" : "1";
  const isCharForChanging = (char) => /^[\p{L}\p{N}]$/u.test(char);
  const binaryReveal = (element) => {
    const targetChars = [...element.textContent];
    const delays = targetChars.map(() => Math.random() * STAGGER);
    const lastUpdate = new Array(targetChars.length).fill(0);
    const displayChars = targetChars.map((char) => isCharForChanging(char) ? getRandomBit() : char);
    let startTime = null;
    const tick = (now) => {
      if (startTime === null) startTime = now;
      let allFixed = true;
      for (let index = 0; index < targetChars.length; index++) {
        const targetChar = targetChars[index];
        if (!isCharForChanging(targetChar)) {
          displayChars[index] = targetChar;
          continue;
        }
        const charTick = () => {
          if (now - lastUpdate[index] > UPDATE_INTERVAL) {
            displayChars[index] = getRandomBit();
            lastUpdate[index] = now;
          }
          allFixed = false;
        };
        const localStart = startTime + delays[index];
        const localEnd = localStart + DURATION;
        if (now < localStart) charTick();
        else if (now >= localEnd) displayChars[index] = targetChar;
        else charTick();
      }
      element.textContent = displayChars.join("");
      if (!allFixed) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const triggerType = widget.getAttribute("data-trigger");
  if (triggerType === "text-hover") {
    let isAnimating = false;
    widget.addEventListener("mouseenter", () => {
      if (!isAnimating) {
        isAnimating = true;
        binaryReveal(widget);
        setTimeout(
          () => {
            isAnimating = false;
          },
          DURATION + STAGGER + 100
        );
      }
    });
  } else {
    const intersectionObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            binaryReveal(widget);
            observer.unobserve(widget);
          }
        });
      },
      { threshold: 0 }
    );
    intersectionObserver.observe(widget);
  }
};
const WIDGET_SELECTOR = '[data-widget="text-reveal"]';
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
widgets.forEach((widget) => {
  textReveal({ widget });
});
