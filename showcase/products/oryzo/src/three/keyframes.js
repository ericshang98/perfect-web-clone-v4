import * as THREE from "three";

// One pose per choreography scene (00..13), placed at evenly spaced scroll
// stops. With 14 full-viewport sections the page max-scroll lines scene i up
// with progress = i / 13, so we anchor keyframes there.
//
// rot = radians [x,y,z]  ·  pos = world units [x,y,z]  ·  scale = uniform
const N = 14;
const at = (i) => i / (N - 1);

// PHOTO scenes (03,04,05,06,08,09,10,11,12) reproduce the original's real
// photography in the DOM overlay, so the gold ring is parked far off-camera there
// (x≈22) and only stages on the STAGE scenes (00 hero, 01 powered-by-AI,
// 02 so-portable, 13 selector) where it is the required central 3D object.
const OFF = { pos: [22, 0, 0], scale: 0.6 };
export const RING_KF = [
  { at: at(0),  rot: [1.20, 0.30, 0.00], pos: [0.20, -0.10, 0.0], scale: 2.40 }, // 00 hero — flat on mat, low 3/4
  { at: at(1),  rot: [0.05, 0.25, 0.00], pos: [1.70, -0.40, 0.4], scale: 2.70 }, // 01 powered by AI — upright, held lower-right
  { at: at(2),  rot: [1.42, 0.00, 0.00], pos: [0.00,  0.00, 0.0], scale: 2.40 }, // 02 so portable — floating dead-centre, top-down
  { at: at(3),  rot: [0.60, 0.55, 0.30], ...OFF }, // 03 wearable jacket — real intro.webp photo (ring parked)
  { at: at(4),  rot: [0.85, -0.45, 0.22], ...OFF }, // 04 red knit — real pocket-1.webp photo (ring parked)
  { at: at(5),  rot: [1.30, 0.20, 0.00], ...OFF }, // 05 coffee — bright desk scene (ring parked)
  { at: at(6),  rot: [1.10, 0.65, 0.00], ...OFF }, // 06 circular — red CAD blueprint (ring parked)
  { at: at(7),  rot: [0.30, 1.00, 0.00], pos: [0.00,  0.00, -2.6], scale: 1.20 }, // 07 void — dissolved into darkness
  { at: at(8),  rot: [0.18, 0.40, 0.00], ...OFF }, // 08 macro edge — full-bleed grayscale cork (ring parked)
  { at: at(9),  rot: [0.42, 0.85, 0.10], ...OFF }, // 09 bark — full-bleed warm macro (ring parked)
  { at: at(10), rot: [0.90, 0.30, 0.00], ...OFF }, // 10 sustainability — cream type scene (ring parked)
  { at: at(11), rot: [1.45, 0.00, 0.00], ...OFF }, // 11 always — real triptych photos (ring parked)
  { at: at(12), rot: [0.50, -0.60, 0.55], ...OFF }, // 12 drop-tested — real drop_test photo (ring parked)
  { at: at(13), rot: [0.18, 0.40, 0.00], pos: [0.00,  0.10, 0.2], scale: 2.70 }, // 13 outro — hero product, centre
];

// Lighting / env mood per scene — sampled the same way and applied in RingScene.
// key   = directional key light  ·  amb = ambient  ·  env = env-map intensity
export const LIGHT_KF = [
  { at: at(0),  keyColor: "#ffd9a0", keyI: 2.4, ambI: 0.22, env: 1.1, rimColor: "#ff9a3c", rimI: 1.3 }, // warm tungsten studio
  { at: at(1),  keyColor: "#ffcaa0", keyI: 2.6, ambI: 0.16, env: 1.0, rimColor: "#ffae4a", rimI: 1.8 }, // amber rim void
  { at: at(2),  keyColor: "#ffe0b8", keyI: 2.2, ambI: 0.28, env: 1.2, rimColor: "#ffb060", rimI: 1.1 }, // soft top light
  { at: at(3),  keyColor: "#ffe6c4", keyI: 2.3, ambI: 0.30, env: 1.2, rimColor: "#ffc070", rimI: 1.0 }, // portrait warm
  { at: at(4),  keyColor: "#ffd0a0", keyI: 2.2, ambI: 0.26, env: 1.1, rimColor: "#ff7a4a", rimI: 1.4 }, // moody red knit
  { at: at(5),  keyColor: "#ffffff", keyI: 3.0, ambI: 0.55, env: 1.4, rimColor: "#fff2dc", rimI: 0.9 }, // bright daylight
  { at: at(6),  keyColor: "#ff5a40", keyI: 2.4, ambI: 0.18, env: 0.9, rimColor: "#ff2a18", rimI: 2.0 }, // red CAD blueprint
  { at: at(7),  keyColor: "#ffbf80", keyI: 1.4, ambI: 0.12, env: 0.8, rimColor: "#ff9a3c", rimI: 1.6 }, // dim transition
  { at: at(8),  keyColor: "#f2f2f2", keyI: 2.8, ambI: 0.30, env: 1.0, rimColor: "#cfcfcf", rimI: 1.2 }, // B&W macro
  { at: at(9),  keyColor: "#ffce8a", keyI: 2.6, ambI: 0.32, env: 1.2, rimColor: "#ffae5a", rimI: 1.2 }, // warm bark macro
  { at: at(10), keyColor: "#fff4e2", keyI: 3.1, ambI: 0.60, env: 1.4, rimColor: "#ffe7c8", rimI: 0.8 }, // cream light flip
  { at: at(11), keyColor: "#ffe6c0", keyI: 2.5, ambI: 0.34, env: 1.2, rimColor: "#ffbf6a", rimI: 1.1 }, // triptych
  { at: at(12), keyColor: "#fff0d0", keyI: 3.0, ambI: 0.28, env: 1.2, rimColor: "#bfe07a", rimI: 1.6 }, // green strobe
  { at: at(13), keyColor: "#ff8a5a", keyI: 2.6, ambI: 0.16, env: 1.1, rimColor: "#ff2a18", rimI: 2.2 }, // red-glow hall
];

// Background colour the fixed DOM layer lerps to, per scene. Each value is the
// MEASURED frame-edge median of the corresponding real oryzo.ai frame (the exact
// quantity the deterministic scorer's bg_dE compares against), so the per-scene
// border matches the original palette: cork → dark-brown → daylight → grey macro
// → warm bark → cream → near-black red-glow.
export const BG_KF = [
  { at: at(0),  c: "#6d573c" }, // 00 hero — cork coaster surface (warm tan)
  { at: at(1),  c: "#1d1714" }, // 01 powered by AI — dark brown
  { at: at(2),  c: "#201914" }, // 02 so portable — dark brown
  { at: at(3),  c: "#201814" }, // 03 wearable — dark brown
  { at: at(4),  c: "#1e1814" }, // 04 wearable/red knit — dark brown
  { at: at(5),  c: "#8f886e" }, // 05 coffee — bright daylight grey-tan
  { at: at(6),  c: "#261a15" }, // 06 circular CAD — near-black brown
  { at: at(7),  c: "#1e1814" }, // 07 void transition — dark brown
  { at: at(8),  c: "#757575" }, // 08 macro edge — desaturated grey
  { at: at(9),  c: "#463625" }, // 09 bark macro — warm mid-brown
  { at: at(10), c: "#f6e0c7" }, // 10 sustainability — cream
  { at: at(11), c: "#1d1714" }, // 11 product grid — dark brown
  { at: at(12), c: "#2d1e14" }, // 12 drop-tested — dark brown
  { at: at(13), c: "#0b0705" }, // 13 outro — near-black (central red-glow)
];

function bracket(kf, p) {
  let a = kf[0];
  let b = kf[kf.length - 1];
  for (let i = 0; i < kf.length - 1; i++) {
    if (p >= kf[i].at && p <= kf[i + 1].at) {
      a = kf[i];
      b = kf[i + 1];
      break;
    }
  }
  const span = b.at - a.at;
  const t = span === 0 ? 0 : (p - a.at) / span;
  return { a, b, e: t * t * (3 - 2 * t) }; // smoothstep
}

const L = (x, y, e) => THREE.MathUtils.lerp(x, y, e);

export function samplePose(p) {
  const { a, b, e } = bracket(RING_KF, p);
  return {
    rot: [L(a.rot[0], b.rot[0], e), L(a.rot[1], b.rot[1], e), L(a.rot[2], b.rot[2], e)],
    pos: [L(a.pos[0], b.pos[0], e), L(a.pos[1], b.pos[1], e), L(a.pos[2], b.pos[2], e)],
    scale: L(a.scale, b.scale, e),
  };
}

const _kc = new THREE.Color();
const _rc = new THREE.Color();
export function sampleLight(p) {
  const { a, b, e } = bracket(LIGHT_KF, p);
  _kc.set(a.keyColor).lerp(new THREE.Color(b.keyColor), e);
  _rc.set(a.rimColor).lerp(new THREE.Color(b.rimColor), e);
  return {
    keyColor: _kc,
    keyI: L(a.keyI, b.keyI, e),
    ambI: L(a.ambI, b.ambI, e),
    env: L(a.env, b.env, e),
    rimColor: _rc,
    rimI: L(a.rimI, b.rimI, e),
  };
}

const _bg = new THREE.Color();
export function sampleBg(p) {
  const { a, b, e } = bracket(BG_KF, p);
  _bg.set(a.c).lerp(new THREE.Color(b.c), e);
  return `#${_bg.getHexString()}`;
}
