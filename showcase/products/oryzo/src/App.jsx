import { Suspense, useEffect, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import RingScene from "./three/RingScene.jsx";
import { initLenis, onScroll } from "./scrollStore.js";
import { sampleBg } from "./three/keyframes.js";
import Nav from "./components/Nav.jsx";
import Hero from "./components/Hero.jsx";
import Scenes from "./components/Scenes.jsx";
import Outro from "./components/Outro.jsx";

const GRAIN = `${import.meta.env.BASE_URL}assets/images/grain.png`;

export default function App() {
  const bgRef = useRef();

  useEffect(() => initLenis(), []);

  // Per-scene background colour, mutated directly (no React re-render).
  useEffect(
    () =>
      onScroll((p) => {
        if (bgRef.current) bgRef.current.style.backgroundColor = sampleBg(p);
      }),
    []
  );

  return (
    <>
      {/* fixed per-scene background colour — behind the canvas */}
      <div ref={bgRef} className="fixed inset-0 -z-10" style={{ backgroundColor: "#15100b" }} />

      {/* fixed WebGL ring layer — transparent, never scrolls */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <Canvas
          camera={{ position: [0, 0, 6], fov: 35 }}
          dpr={[1, 2]}
          gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        >
          <Suspense fallback={null}>
            <RingScene />
          </Suspense>
        </Canvas>
      </div>

      {/* tall, normally-scrolling DOM overlay */}
      <div id="ui" className="relative z-10 text-cream">
        <Nav />
        <Hero />
        <Scenes />
        <Outro />
      </div>

      {/* top-most film-grain — overlay blend preserves each scene's background
          MEDIAN colour while breaking up flat dark regions so no scene reads as
          an empty void. */}
      <div
        className="grain pointer-events-none fixed inset-0 z-40"
        style={{ backgroundImage: `url(${GRAIN})` }}
      />
    </>
  );
}
