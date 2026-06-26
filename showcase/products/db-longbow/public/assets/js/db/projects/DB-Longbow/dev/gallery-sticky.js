import { g as gsapWithCSS } from "./lib/50Lx19ak.js";
import { S as ScrollTrigger } from "./lib/C6o_azLH.js";
const gallerySticky = ({ widget }) => {
  const contentStickyElement = widget.querySelector('[data-role="content-sticky"]');
  const contentElement = widget.querySelector('[data-role="content"]');
  const followerWrapperElement = widget.querySelector('[data-role="follower-wrapper"]');
  const followerElement = widget.querySelector('[data-role="follower"]');
  const followerTextElements = followerElement && followerElement.querySelectorAll('[data-role="follower-text"]');
  const mm = gsapWithCSS.matchMedia();
  mm.add("(min-width: 992px)", () => {
    if (followerWrapperElement && followerElement) {
      let isStickyToBottom = false;
      let isWrapperInViewport = false;
      const lastMousePosition = { x: 0, y: 0 };
      let isMouseInWrapper = false;
      const originalText = followerTextElements[0].textContent;
      const newText = followerTextElements[0].getAttribute("data-new-text");
      const updateFollowerVisibility = () => {
        if (isWrapperInViewport && !isStickyToBottom) {
          gsapWithCSS.to(followerElement, { opacity: 1, duration: 0.3 });
        } else if (isStickyToBottom) {
          gsapWithCSS.to(followerElement, { opacity: 1, duration: 0.3 });
        } else {
          gsapWithCSS.to(followerElement, { opacity: 0, duration: 0.3 });
        }
      };
      const updateFollowerPosition = () => {
        if (isStickyToBottom || !isWrapperInViewport || !isMouseInWrapper) return;
        const rect = followerWrapperElement.getBoundingClientRect();
        const x = lastMousePosition.x - rect.left;
        const y = lastMousePosition.y - rect.top;
        gsapWithCSS.to(followerElement, {
          x: x - followerElement.offsetWidth / 2,
          y: y - followerElement.offsetHeight / 2,
          duration: 0.5,
          ease: "power2.out"
        });
      };
      ScrollTrigger.create({
        trigger: widget,
        start: `top+=${window.innerHeight / 2} top`,
        end: "bottom top",
        onEnter: () => {
          isWrapperInViewport = true;
          updateFollowerVisibility();
          if (isMouseInWrapper) updateFollowerPosition();
        },
        onLeave: () => {
          isWrapperInViewport = false;
          updateFollowerVisibility();
        },
        onEnterBack: () => {
          isWrapperInViewport = true;
          updateFollowerVisibility();
          if (isMouseInWrapper) updateFollowerPosition();
        },
        onLeaveBack: () => {
          isWrapperInViewport = false;
          updateFollowerVisibility();
        }
      });
      const handleScroll = () => {
        if (isMouseInWrapper && isWrapperInViewport && !isStickyToBottom) {
          updateFollowerPosition();
        }
      };
      window.addEventListener("scroll", handleScroll, { passive: true });
      followerWrapperElement.addEventListener("mouseenter", () => {
        isMouseInWrapper = true;
        if (isWrapperInViewport && !isStickyToBottom) {
          gsapWithCSS.to(followerElement, { opacity: 1, duration: 0.3 });
        }
      });
      followerWrapperElement.addEventListener("mouseleave", () => {
        isMouseInWrapper = false;
        if (isWrapperInViewport && !isStickyToBottom) {
          gsapWithCSS.to(followerElement, { opacity: 1, duration: 0.3 });
        }
      });
      followerWrapperElement.addEventListener("mousemove", (event) => {
        if (isStickyToBottom || !isWrapperInViewport) return;
        lastMousePosition.x = event.clientX;
        lastMousePosition.y = event.clientY;
        const rect = followerWrapperElement.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        gsapWithCSS.to(followerElement, {
          x: x - followerElement.offsetWidth / 2,
          y: y - followerElement.offsetHeight / 2,
          duration: 1,
          ease: "power3.out"
        });
      });
      const stickToBottom = () => {
        const followerLocalTextElements = followerElement.querySelectorAll('[data-role="follower-text"]');
        if (!isStickyToBottom) {
          isStickyToBottom = true;
          const rect = followerWrapperElement.getBoundingClientRect();
          gsapWithCSS.set(followerElement, { opacity: 1, duration: 0.3 });
          followerLocalTextElements.forEach((element) => {
            gsapWithCSS.set(element, { opacity: 0.5, duration: 0.3 });
            if (newText && element.textContent !== newText) {
              element.textContent = newText;
            }
            gsapWithCSS.to(element, {
              opacity: 1,
              duration: 0.3,
              ease: "power3.out",
              overwrite: true,
              delay: 0.2
            });
          });
          gsapWithCSS.to(followerElement, {
            y: rect.height - followerElement.offsetHeight,
            opacity: 1,
            duration: 0.5,
            ease: "power3.out",
            overwrite: true,
            delay: 0.2
          });
        }
      };
      const unstickFromBottom = () => {
        const followerLocalTextElements = followerElement.querySelectorAll('[data-role="follower-text"]');
        if (isStickyToBottom && isWrapperInViewport) {
          isStickyToBottom = false;
          gsapWithCSS.set(followerElement, { opacity: 1, duration: 0.3 });
          followerLocalTextElements.forEach((element) => {
            gsapWithCSS.set(element, { opacity: 0.5, duration: 0.3 });
            if (originalText && element.textContent !== originalText) {
              element.textContent = originalText;
            }
            gsapWithCSS.to(element, {
              opacity: 1,
              duration: 0.3,
              ease: "power3.out",
              overwrite: true,
              delay: 0.2
            });
          });
          gsapWithCSS.to(followerElement, {
            opacity: 1,
            duration: 0.5,
            ease: "power3.out",
            overwrite: true,
            delay: 0.2
          });
          if (isMouseInWrapper) {
            setTimeout(() => {
              updateFollowerPosition();
            }, 250);
          }
        }
      };
      ScrollTrigger.create({
        trigger: widget,
        start: "bottom center",
        onEnter: () => {
          stickToBottom();
        },
        onEnterBack: () => {
          unstickFromBottom();
        },
        onLeave: () => {
          stickToBottom();
        },
        onLeaveBack: () => {
          unstickFromBottom();
        }
      });
      ScrollTrigger.refresh();
    }
    if (contentStickyElement && contentElement) {
      gsapWithCSS.fromTo(
        contentElement,
        {
          height: "min(50dvh, 31.875rem)"
        },
        {
          width: "100%",
          height: "min(100dvh, 63.75rem)",
          scrollTrigger: {
            trigger: contentStickyElement,
            start: "top center",
            end: "bottom top",
            scrub: true
          }
        }
      );
    }
  });
};
const WIDGET_SELECTOR = '[data-widget="gallery-sticky"]';
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
widgets.forEach((widget) => {
  gallerySticky({ widget });
});
