import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Environment, ContactShadows, Lightformer } from "@react-three/drei";
import Ring from "./Ring.jsx";
import { scroll } from "../scrollStore.js";
import { sampleLight } from "./keyframes.js";

export default function RingScene() {
  const key = useRef();
  const rim = useRef();
  const amb = useRef();

  // Drive lights off scroll so the gold reads warm-studio -> daylight -> red CAD
  // -> B&W -> cream -> red-glow across the choreography. No React re-renders.
  useFrame(() => {
    const l = sampleLight(scroll.progress);
    if (key.current) {
      key.current.intensity = l.keyI;
      key.current.color.copy(l.keyColor);
    }
    if (rim.current) {
      rim.current.intensity = l.rimI;
      rim.current.color.copy(l.rimColor);
    }
    if (amb.current) amb.current.intensity = l.ambI;
  });

  return (
    <>
      {/* transparent canvas — the fixed DOM bg layer provides per-scene colour */}
      <ambientLight ref={amb} intensity={0.25} />
      <directionalLight
        ref={key}
        position={[4, 6, 5]}
        intensity={2.4}
        color="#ffd9a0"
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-bias={-0.0002}
      />
      <directionalLight ref={rim} position={[-5, 2, -4]} intensity={1.4} color="#ff9a3c" />

      {/* Procedural studio env — gives the gold real reflections with NO CDN/HDRI
          fetch, so headless screenshots render deterministically. */}
      <Environment resolution={256}>
        <color attach="background" args={["#202020"]} />
        <Lightformer intensity={3.0} color="#fff0d8" position={[0, 4, -6]} scale={[12, 6, 1]} />
        <Lightformer intensity={2.2} color="#ffd9a0" position={[5, 2, 2]} scale={[6, 8, 1]} rotation={[0, -Math.PI / 3, 0]} />
        <Lightformer intensity={1.4} color="#ff8a4a" position={[-6, 1, -2]} scale={[5, 8, 1]} rotation={[0, Math.PI / 3, 0]} />
        <Lightformer intensity={2.5} color="#ffffff" position={[0, -3, 4]} scale={[10, 4, 1]} />
      </Environment>

      <Ring />

      <ContactShadows
        position={[0, -1.4, 0]}
        opacity={0.45}
        blur={2.6}
        scale={9}
        far={4}
        resolution={512}
      />
    </>
  );
}
