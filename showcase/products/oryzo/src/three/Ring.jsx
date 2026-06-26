import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF, Center } from "@react-three/drei";
import * as THREE from "three";
import { scroll } from "../scrollStore.js";
import { samplePose } from "./keyframes.js";

const GLB = `${import.meta.env.BASE_URL}assets/models/ring-gold.glb`;

const prefersReduced =
  typeof window !== "undefined" &&
  window.matchMedia &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export default function Ring() {
  const group = useRef();
  const { scene } = useGLTF(GLB);

  // Single shared polished-gold material for all 3 meshes (anniuV3_low / da_low /
  // xiao_low share lambert3 — alphaMode MASK with baked maps reads as flat cut-out,
  // so we replace it outright). Gold only looks gold WITH the env map in RingScene.
  const gold = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color("#C9A227"),
        metalness: 1.0,
        roughness: 0.18,
        envMapIntensity: 1.25,
      }),
    []
  );

  useMemo(() => {
    scene.traverse((o) => {
      if (o.isMesh) {
        o.material = gold;
        o.castShadow = true;
        o.receiveShadow = true;
      }
    });
  }, [scene, gold]);

  useFrame((state, dt) => {
    const g = group.current;
    if (!g) return;
    const pose = samplePose(scroll.progress);
    const idle = prefersReduced ? 0 : state.clock.elapsedTime * 0.12;

    const k = 4;
    g.rotation.x = THREE.MathUtils.damp(g.rotation.x, pose.rot[0], k, dt);
    g.rotation.y = THREE.MathUtils.damp(g.rotation.y, pose.rot[1] + idle, k, dt);
    g.rotation.z = THREE.MathUtils.damp(g.rotation.z, pose.rot[2], k, dt);
    g.position.x = THREE.MathUtils.damp(g.position.x, pose.pos[0], k, dt);
    g.position.y = THREE.MathUtils.damp(g.position.y, pose.pos[1], k, dt);
    g.position.z = THREE.MathUtils.damp(g.position.z, pose.pos[2], k, dt);
    const s = THREE.MathUtils.damp(g.scale.x, pose.scale, k, dt);
    g.scale.setScalar(s);
  });

  // <Center> fixes the y≈+11 (pre-scale) off-centre geometry; the animated group
  // lives inside so our per-frame writes don't clobber Center's own transform.
  return (
    <Center>
      <group ref={group}>
        <primitive object={scene} />
      </group>
    </Center>
  );
}

useGLTF.preload(GLB);
