import { useEffect } from "react";

/**
 * Section 9 — collaborators marquee code embed.
 *
 * In the source this is a Webflow `.w-embed .w-script` block:
 *   <div class="collaborators-marquee-code w-embed w-script" style="display:none">
 *     <script>…drives .collaborators-list marquee…</script>
 *   </div>
 *
 * It renders nothing visible (`.collaborators-marquee-code { display: none }`).
 * Its only job is to clone the `.collaborators-list` element and animate both
 * copies leftward via requestAnimationFrame, pausing on hover of the parent.
 * We reproduce that behavior with an effect so the marquee still works if a
 * `.collaborators-list` exists elsewhere on the page.
 */
export default function Section9Section() {
  useEffect(() => {
    const marquee = document.querySelector(".collaborators-list");
    if (!marquee || !marquee.parentElement) return;

    const parent = marquee.parentElement;
    const clone = marquee.cloneNode(true);
    parent.appendChild(clone);

    let x = 0;
    let isPaused = false;
    let raf;

    const animate = () => {
      if (!isPaused) {
        x -= 1; // speed (px per frame)
        marquee.style.transform = `translateX(${x}px)`;
        clone.style.transform = `translateX(${x}px)`;
        if (x <= -marquee.offsetWidth) {
          x = 0;
        }
      }
      raf = requestAnimationFrame(animate);
    };

    const onEnter = () => {
      isPaused = true;
    };
    const onLeave = () => {
      isPaused = false;
    };

    parent.addEventListener("mouseenter", onEnter);
    parent.addEventListener("mouseleave", onLeave);

    animate();

    return () => {
      cancelAnimationFrame(raf);
      parent.removeEventListener("mouseenter", onEnter);
      parent.removeEventListener("mouseleave", onLeave);
      if (clone.parentElement === parent) {
        parent.removeChild(clone);
      }
    };
  }, []);

  return (
    <div
      className="collaborators-marquee-code w-embed w-script"
      data-eapps-font-size="16"
      data-eapps-line-height="17.6"
      style={{ display: "none" }}
      aria-hidden="true"
    />
  );
}
