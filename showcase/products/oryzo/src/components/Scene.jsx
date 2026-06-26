import { useEffect, useRef } from "react";

// Full-viewport scroll section. Text creates the page height; the fixed ring
// canvas stays behind it. Content reveals on enter via IntersectionObserver.
export default function Scene({ id, children, className = "", align = "items-center" }) {
  const ref = useRef();

  useEffect(() => {
    const el = ref.current;
    const io = new IntersectionObserver(
      ([e]) => e.target.classList.toggle("is-in", e.isIntersecting),
      { threshold: 0.3 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section
      id={id}
      ref={ref}
      className={`relative flex min-h-screen ${align} px-[3.125vw] py-[12vh] ${className}`}
    >
      {children}
    </section>
  );
}
