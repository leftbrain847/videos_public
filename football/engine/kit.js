// Low-poly 3D kit for the football shorts: characters, props and sets.
// Style target: round faceted heads, chunky blocky hands and shoes, simple dot eyes with strong brows,
// bright warm studio light with soft shadows, clean sets. Every tunable is in STYLE.
import * as THREE from 'three';
import { RoundedBoxGeometry } from './node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export const STYLE = {
  skinTones: ['#f2c39b', '#e8b48f', '#c98d63', '#a8714c', '#7b4e33', '#5a3825'],
  shoe: '#3d3d40',
  eye: '#141414',
  brow: '#2b1d14',
  mouth: '#4a2219',
  headRadius: 0.56,
  headDetail: 2,          // icosahedron subdivisions: 2 = round with visible facets
  facetJitter: 0,
  exposure: 1.12,
  key: { color: '#ffe4bf', intensity: 2.6, pos: [6, 9, 7] },        // warm, low-ish sun: the reference's golden light
  fill: { sky: '#fff1df', ground: '#c9a27a', intensity: 1.35 },
  rim: { color: '#ffe2c4', intensity: 0.9, pos: [-6, 6, -6] },
  shadowRadius: 8,
  joints: { thighLen: 0.56, shinLen: 0.55, thighR: 0.21, shinR: 0.18, upperArmLen: 0.5, foreArmLen: 0.46, armR: 0.13 },
  body: {
    // smooth spline profiles [radius, height]; front-to-back is squashed in code
    hips: [[0.001, 1.08], [0.34, 1.1], [0.39, 1.25], [0.38, 1.38], [0.001, 1.4]],
    leg: [[0.001, 0.12], [0.15, 0.14], [0.155, 0.6], [0.175, 1.0], [0.19, 1.3], [0.001, 1.32]],
    torso: [[0.001, 1.24], [0.45, 1.26], [0.43, 1.45], [0.41, 1.6], [0.39, 1.75], [0.43, 2.05], [0.44, 2.22], [0.36, 2.36], [0.17, 2.42], [0.001, 2.43]],
    torsoJersey: [[0.001, 1.24], [0.46, 1.26], [0.43, 1.6], [0.47, 1.95], [0.53, 2.2], [0.46, 2.36], [0.17, 2.42], [0.001, 2.43]],
    chestY: 2.02, hipY: 1.25, shoulderX: 0.5, shoulderY: 2.24, neckY: 2.42, armLen: 1.12,
  },
};

// ---------- helpers ----------
let _seed = 1;
const rnd = () => { _seed = (_seed * 16807) % 2147483647; return _seed / 2147483647 - 0.5; };
export function mat(color, o = {}) {
  return new THREE.MeshStandardMaterial({ color, flatShading: false, roughness: 0.72, metalness: 0, ...o });
}
export function facet(geo) { // smooth style: no jitter, just clean normals (kept so old call sites still work)
  geo.computeVertexNormals();
  return geo;
}
const shadow = (o) => { o.castShadow = true; o.receiveShadow = true; return o; };
export function textTexture(lines, { w = 1024, h = 512, bg = '#ffffff', fg = '#1b2a5c', accent = '#d62828', font = '900 120px Inter, Arial' } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const x = c.getContext('2d');
  x.fillStyle = bg; x.fillRect(0, 0, w, h);
  x.textAlign = 'center'; x.textBaseline = 'middle';
  const arr = Array.isArray(lines) ? lines : [lines];
  arr.forEach((t, i) => {
    x.fillStyle = i === 0 ? fg : accent;
    let size = parseInt(font.match(/(\d+)px/)[1], 10);
    x.font = font.replace(/\d+px/, `${size}px`);
    while (x.measureText(t).width > w * 0.9 && size > 20) { size -= 4; x.font = font.replace(/\d+px/, `${size}px`); }
    x.fillText(t, w / 2, (h / (arr.length + 1)) * (i + 1));
  });
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  return tex;
}

// ---------- characters ----------
// look: { skin, shirt, pants, hair: 'short'|'long'|'bald'|'buzz'|'bun', hairColor, outfit: 'tee'|'jersey'|'suit'|'ref'|'polo'|'hoodie',
//         number, helmet (color), cap (color), headset, glasses, beard }
export function person(look = {}, seed = 1) {
  const L = { skin: STYLE.skinTones[0], shirt: '#f28c28', pants: '#2f4fa8', hair: 'short', hairColor: '#3b2416', outfit: 'tee', ...look };
  const g = new THREE.Group();
  const parts = {};
  const shirtMat = mat(L.shirt), skinMat = mat(L.skin), pantsMat = mat(L.pants);

  // ---- body: smooth sculpted shapes (reference: human-shaped, smooth and curving) ----
  const B = STYLE.body;
  const smoothLathe = (pts, seg = 40, steps = 48) => {
    const curve = new THREE.SplineCurve(pts.map(([r, y]) => new THREE.Vector2(r, y)));
    return new THREE.LatheGeometry(curve.getPoints(steps), seg);
  };
  const squash = (geo, zs, chest = 0) => { // flatten front-to-back; optional chest fullness on the front
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { let z = p.getZ(i) * zs; const y = p.getY(i);
      if (chest && z > 0) z *= 1 + chest * Math.exp(-((y - B.chestY) ** 2) / 0.06);
      p.setZ(i, z); }
    geo.computeVertexNormals(); return geo;
  };
  // ---- skeleton: pelvis -> chest (lean, twist) -> shoulder -> elbow -> hand; hip -> knee -> ankle. Clothes ride the bones.
  const J = STYLE.joints;
  const chest = new THREE.Group(); chest.position.set(0, B.hipY, 0); g.add(chest); parts.chest = chest;
  const upper = new THREE.Group(); upper.position.y = -B.hipY; chest.add(upper);     // upper-body meshes keep absolute heights
  const cap = (r, len, m, y) => { const o = shadow(new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 20), m)); o.position.y = y; return o; };
  // pants: hips piece, then thigh / knee / shin per leg, shoe on the ankle
  const hips = shadow(new THREE.Mesh(squash(smoothLathe(B.hips), 0.62), pantsMat)); g.add(hips);
  for (const sx of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(sx * 0.19, B.hipY, 0); g.add(hip);
    hip.add(cap(J.thighR, J.thighLen - 2 * J.thighR * 0.4, pantsMat, -J.thighLen / 2));
    const knee = new THREE.Group(); knee.position.y = -J.thighLen; hip.add(knee);
    knee.add(shadow(new THREE.Mesh(new THREE.SphereGeometry(J.shinR * 1.08, 20, 14), pantsMat)));
    knee.add(cap(J.shinR, J.shinLen - 2 * J.shinR * 0.4, pantsMat, -J.shinLen / 2));
    const ankle = new THREE.Group(); ankle.position.y = -J.shinLen; knee.add(ankle);
    const shoe = shadow(new THREE.Mesh(new RoundedBoxGeometry(0.33, 0.19, 0.56, 4, 0.09), mat(STYLE.shoe)));
    shoe.position.set(0, -0.03, 0.09); ankle.add(shoe);
    parts[sx < 0 ? 'legL' : 'legR'] = hip; parts[sx < 0 ? 'kneeL' : 'kneeR'] = knee; parts[sx < 0 ? 'footL' : 'footR'] = ankle;
  }
  // shirt: smooth torso with chest, waist and a soft hem; rounded shoulder caps
  const tp = L.outfit === 'jersey' ? B.torsoJersey : B.torso;
  const torso = shadow(new THREE.Mesh(squash(smoothLathe(tp), 0.66, 0.08), shirtMat)); upper.add(torso);
  parts.torso = torso;
  for (const sx of [-1, 1]) {
    const sh = shadow(new THREE.Mesh(new THREE.SphereGeometry(L.outfit === 'jersey' ? 0.25 : 0.18, 24, 16), shirtMat));
    sh.scale.set(1, 0.85, 0.95); sh.position.set(sx * (B.shoulderX - 0.07), B.shoulderY - 0.02, 0); upper.add(sh);
  }
  if (L.outfit === 'ref') {
    for (let i = -2; i <= 2; i++) for (const base of [Math.PI / 2, -Math.PI / 2]) {
      const st = new THREE.Mesh(squash(new THREE.LatheGeometry(new THREE.SplineCurve(tp.map(([r, y]) => new THREE.Vector2(r + 0.004, y))).getPoints(48), 12, base + i * 0.4 - 0.06, 0.12), 0.66, 0.08), mat('#151515', { side: THREE.DoubleSide }));
      upper.add(st);
    }
  }
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.025, 10, 24), shirtMat); collar.rotation.x = Math.PI / 2; collar.scale.y = 0.75; collar.position.y = B.neckY; upper.add(collar);
  if (L.outfit === 'suit') {
    const lap = new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.55), mat('#f4f4f4')); lap.position.set(0, B.neckY - 0.33, 0.29); lap.rotation.x = -0.15; upper.add(lap);
    const tie = new THREE.Mesh(new RoundedBoxGeometry(0.09, 0.48, 0.03, 2, 0.012), mat(L.tie || '#c0262d')); tie.position.set(0, B.neckY - 0.34, 0.305); tie.rotation.x = -0.15; upper.add(tie);
  }
  if (L.outfit === 'polo') {
    for (const sx of [-1, 1]) { const c = new THREE.Mesh(new RoundedBoxGeometry(0.16, 0.03, 0.12, 2, 0.01), shirtMat); c.position.set(sx * 0.09, B.neckY - 0.03, 0.15); c.rotation.set(0.35, 0, sx * 0.5); upper.add(c); }
  }
  if (L.outfit === 'robe') {   // mythology: draped robe with a sash
    const sash = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.05, 8, 24), mat(L.sash || '#d9a521')); sash.rotation.set(Math.PI / 2, 0.55, 0); sash.scale.set(1, 0.7, 1.4); sash.position.y = B.chestY - 0.1; upper.add(sash);
    const skirt = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.5, 0.9, 24), shirtMat)); skirt.position.y = -0.05; upper.add(skirt);
  }
  if (L.outfit === 'spacesuit') {
    const pack = shadow(new THREE.Mesh(new RoundedBoxGeometry(0.6, 0.7, 0.28, 3, 0.06), mat('#c9ced6'))); pack.position.set(0, B.chestY, -0.38); upper.add(pack);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.05, 10, 24), mat('#c9ced6')); ring.rotation.x = Math.PI / 2; ring.position.y = B.neckY + 0.02; upper.add(ring);
    const pnl = new THREE.Mesh(new RoundedBoxGeometry(0.3, 0.2, 0.04, 2, 0.02), mat('#2b4c8c')); pnl.position.set(0, B.chestY, 0.36); upper.add(pnl);
  }
  if (L.outfit === 'coat') {
    for (const sx of [-1, 1]) { const lp = new THREE.Mesh(new RoundedBoxGeometry(0.12, 0.5, 0.03, 2, 0.01), mat(L.lapel || '#2a2a2a')); lp.position.set(sx * 0.1, B.neckY - 0.3, 0.3); lp.rotation.set(-0.15, 0, sx * 0.2); upper.add(lp); }
  }
  if (L.outfit === 'hoodie') {
    const hood = shadow(new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.09, 12, 24), shirtMat)); hood.rotation.x = Math.PI / 2 - 0.3; hood.position.set(0, B.neckY - 0.02, -0.08); upper.add(hood);
  }
  if (L.number) {
    const t = textTexture(String(L.number), { w: 256, h: 256, bg: 'rgba(0,0,0,0)', fg: L.numberColor || '#ffffff', font: '900 190px Inter, Arial' });
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.46), new THREE.MeshBasicMaterial({ map: t, transparent: true }));
    plate.position.set(0, B.chestY - 0.05, L.outfit === 'jersey' ? 0.4 : 0.37); upper.add(plate);
  }
  // arms: shoulder -> upper arm (sleeve) -> elbow -> forearm -> hand (mitten)
  const longSleeve = ['suit', 'hoodie', 'robe', 'spacesuit', 'coat'].includes(L.outfit) || L.longSleeve;
  for (const sx of [-1, 1]) {
    const pivot = new THREE.Group(); pivot.position.set(sx * B.shoulderX, B.shoulderY, 0); upper.add(pivot);
    const sleeveLen = longSleeve ? J.upperArmLen + 0.05 : 0.34;
    pivot.add(shadow(new THREE.Mesh(smoothLathe([[0.001, 0.05], [0.19, 0.02], [0.185, -sleeveLen * 0.5], [0.18, -sleeveLen], [0.001, -sleeveLen - 0.005]], 24, 24), shirtMat)));
    pivot.add(cap(J.armR, J.upperArmLen - 2 * J.armR * 0.5, longSleeve ? shirtMat : skinMat, -J.upperArmLen / 2));
    const elbow = new THREE.Group(); elbow.position.y = -J.upperArmLen; pivot.add(elbow);
    elbow.add(shadow(new THREE.Mesh(new THREE.SphereGeometry(J.armR * 1.02, 16, 12), longSleeve ? shirtMat : skinMat)));
    elbow.add(cap(J.armR * 0.92, J.foreArmLen - 2 * J.armR * 0.5, longSleeve ? shirtMat : skinMat, -J.foreArmLen / 2));
    const hand = shadow(new THREE.Mesh(new RoundedBoxGeometry(0.25, 0.29, 0.26, 4, 0.1), skinMat));
    hand.position.y = -J.foreArmLen - 0.08; elbow.add(hand);
    const thumb = shadow(new THREE.Mesh(new THREE.CapsuleGeometry(0.04, 0.08, 4, 10), skinMat)); thumb.position.set(-sx * 0.1, -0.02, 0.05); thumb.rotation.z = sx * 0.5; hand.add(thumb);
    pivot.rotation.z = sx * 0.06;
    parts[sx < 0 ? 'armL' : 'armR'] = pivot; parts[sx < 0 ? 'elbowL' : 'elbowR'] = elbow;
    parts[sx < 0 ? 'handL' : 'handR'] = hand;
  }
  // neck + head
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.15, 0.3, 16), skinMat); neck.position.y = 2.5; upper.add(neck);
  const head = new THREE.Group(); head.userData.noSelfShadow = true; head.position.y = 2.55 + STYLE.headRadius * 0.92; upper.add(head); parts.head = head;
  const skull = shadow(new THREE.Mesh(new THREE.SphereGeometry(STYLE.headRadius, 40, 30), skinMat));
  skull.scale.set(1, 1.07, 0.98); head.add(skull);
  // ears
  for (const sx of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 12), skinMat);
    ear.scale.set(0.6, 1, 0.8); ear.position.set(sx * STYLE.headRadius * 0.98, -0.02, 0); head.add(ear);
  }
  // hair: built from smooth volumes (crown, side-swept fringe, back mass, strands), styles share parts
  const R = STYLE.headRadius;
  const hairMat = mat(L.hairColor, { roughness: 0.55 });
  const H = (geo, pos, scl = [1, 1, 1], rot = [0, 0, 0]) => { const m = shadow(new THREE.Mesh(geo, hairMat)); m.position.set(...pos); m.scale.set(...scl); m.rotation.set(...rot); head.add(m); return m; };
  const crown = (cover = 0.5, r = 1.07) => H(new THREE.SphereGeometry(R * r, 40, 24, 0, Math.PI * 2, 0, Math.PI * cover), [0, 0.03, -0.03], [1, 1, 1], [-0.28, 0, 0]);
  const fringe = (side = 1) => { // side-swept bang: a flattened tapered capsule across the forehead
    H(new THREE.CapsuleGeometry(R * 0.2, R * 0.9, 8, 16), [side * R * 0.18, R * 0.52, R * 0.72], [1.15, 1, 0.55], [0.35, 0, Math.PI / 2 - side * 0.38]);
  };
  const strand = (x, z, len, w = 0.15, tilt = 0) => H(new THREE.CapsuleGeometry(R * w, len, 8, 16), [x, -len * 0.45, z], [1, 1, 0.8], [0, 0, tilt]);
  const style = L.hair;
  if (style === 'short' || style === 'buzz') { crown(style === 'buzz' ? 0.4 : 0.47, style === 'buzz' ? 1.03 : 1.08); if (style === 'short') fringe(1); }
  else if (style === 'pixie') { crown(0.5, 1.08); fringe(-1); for (const sx of [-1, 1]) strand(sx * R * 0.9, -R * 0.05, R * 0.35, 0.16, sx * 0.15); }
  else if (style === 'bob' || style === 'long') {
    crown(0.52, 1.1); fringe(1);
    const len = style === 'long' ? R * 1.9 : R * 1.05;
    H(new THREE.CapsuleGeometry(R * 0.95, len * 0.6, 12, 24), [0, -len * 0.3, -R * 0.38], [1.05, 1, 0.62]);              // back mass
    for (const sx of [-1, 1]) for (const k of [0, 1]) strand(sx * R * (0.88 - k * 0.06), R * (0.18 - k * 0.38), len * (0.82 - k * 0.1), 0.2, sx * 0.06); // side strands frame the face
  }
  else if (style === 'ponytail') {
    crown(0.55, 1.08); fringe(1);
    H(new THREE.SphereGeometry(R * 0.2, 16, 12), [0, R * 0.55, -R * 0.95]);                                              // tie
    H(new THREE.CapsuleGeometry(R * 0.26, R * 1.3, 10, 20), [0, -R * 0.15, -R * 1.25], [1, 1, 0.9], [0.35, 0, 0]);       // tail
  }
  else if (style === 'bun') {
    crown(0.55, 1.08);
    H(new THREE.SphereGeometry(R * 0.42, 24, 16), [0, R * 0.85, -R * 0.55]);
  }
  else if (style === 'afro' || style === 'curly') {
    const n = style === 'afro' ? 26 : 18, big = style === 'afro' ? 1.25 : 1.12;
    for (let i = 0; i < n; i++) { const t = (i / n) * Math.PI * 2, ring = i % 2; const ph = 0.35 + ring * 0.45;
      H(new THREE.SphereGeometry(R * (0.32 + (i % 3) * 0.04), 20, 14), [Math.cos(t) * R * big * Math.sin(ph + 0.6) * 0.9, R * (0.25 + Math.cos(ph) * 0.45), Math.sin(t) * R * big * 0.85 - R * 0.15]); }
    crown(0.5, 1.12);
  }
  else if (style === 'braids') {
    crown(0.52, 1.08);
    for (const sx of [-1, 1]) for (let i = 0; i < 6; i++) H(new THREE.SphereGeometry(R * 0.17, 16, 12), [sx * R * 0.82, -R * (0.15 + i * 0.27), -R * 0.25], [1, 1.2, 1]);
  }
  if (L.beard) {
    const b = shadow(new THREE.Mesh(facet(new THREE.SphereGeometry(R * 1.04, 40, 20, 0, Math.PI * 2, Math.PI * 0.62, Math.PI * 0.38), 0.02, seed + 69), hairMat));
    b.position.set(0, -0.03, 0.02); head.add(b);
  }
  if (L.cap) {
    const c = shadow(new THREE.Mesh(facet(new THREE.SphereGeometry(R * 1.12, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.48), 0.02, seed + 71), mat(L.cap)));
    c.position.y = 0.08; head.add(c);
    const brim = shadow(new THREE.Mesh(new THREE.BoxGeometry(R * 1.3, 0.06, R * 0.75), mat(L.cap)));
    brim.position.set(0, R * 0.35, R * 0.95); brim.rotation.x = 0.12; head.add(brim);
  }
  if (L.helmet) {
    const h = shadow(new THREE.Mesh(facet(new THREE.SphereGeometry(R * 1.14, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.62), 0.02, seed + 73), mat(L.helmet, { roughness: 0.35 })));
    h.position.set(0, 0.04, -0.06); h.rotation.x = -0.2; head.add(h);
    const mask = new THREE.Mesh(new THREE.TorusGeometry(R * 0.62, 0.035, 4, 12, Math.PI), mat('#e6e6e6'));
    mask.position.set(0, -R * 0.32, R * 0.86); mask.rotation.z = Math.PI; head.add(mask);
    const bar = new THREE.Mesh(new THREE.BoxGeometry(R * 1.2, 0.05, 0.05), mat('#e6e6e6'));
    bar.position.set(0, -R * 0.1, R * 0.95); head.add(bar);
  }
  if (L.headset) {
    const band = new THREE.Mesh(new THREE.TorusGeometry(R * 1.05, 0.04, 4, 14, Math.PI), mat('#222'));
    band.position.y = 0.05; head.add(band);
    for (const sx of [-1, 1]) { const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.12, 8), mat('#222')); cup.rotation.z = Math.PI / 2; cup.position.set(sx * R * 1.03, 0, 0); head.add(cup); }
    const micArm = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.45, 4), mat('#222')); micArm.rotation.x = Math.PI / 2.4; micArm.position.set(-R * 0.75, -0.25, R * 0.5); head.add(micArm);
  }
  if (L.glasses) {
    for (const sx of [-1, 1]) { const lens = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.022, 4, 10), mat('#1a1a1a')); lens.position.set(sx * 0.21, 0.06, R * 0.95); head.add(lens); }
  }
  // face: oval eyes, angled brows, mouth shapes, small nose
  const eyeMat = new THREE.MeshStandardMaterial({ color: STYLE.eye, roughness: 0.3 });
  parts.eyes = [];
  for (const sx of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), eyeMat);
    eye.scale.set(0.85, 1.15, 0.5); eye.position.set(sx * 0.22, 0.04, R * 0.93); head.add(eye); parts.eyes.push(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.018, 6, 4), new THREE.MeshBasicMaterial({ color: '#ffffff' }));
    glint.position.set(sx * 0.22 + 0.025, 0.08, R * 0.97); head.add(glint); parts.eyes.push(glint);
    const brow = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.05, 0.04), mat(STYLE.brow));
    brow.position.set(sx * 0.22, 0.22, R * 0.9); head.add(brow);
    parts[sx < 0 ? 'browL' : 'browR'] = brow;
  }
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), skinMat);
  nose.scale.set(1, 0.9, 0.9); nose.position.set(0, -0.08, R * 0.98); head.add(nose);
  const mouthFlat = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.03, 0.03), mat(STYLE.mouth));
  mouthFlat.position.set(0, -0.26, R * 0.9); head.add(mouthFlat);
  const mouthO = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), mat(STYLE.mouth));
  mouthO.scale.set(0.9, 1.1, 0.4); mouthO.position.set(0, -0.27, R * 0.9); head.add(mouthO);
  const smileGeo = new THREE.TorusGeometry(0.11, 0.022, 4, 10, Math.PI);
  const mouthSmile = new THREE.Mesh(smileGeo, mat(STYLE.mouth)); mouthSmile.rotation.z = Math.PI; mouthSmile.position.set(0, -0.2, R * 0.9); head.add(mouthSmile);
  const mouthFrown = new THREE.Mesh(smileGeo, mat(STYLE.mouth)); mouthFrown.position.set(0, -0.33, R * 0.9); head.add(mouthFrown);
  parts.mouths = { flat: mouthFlat, o: mouthO, smile: mouthSmile, frown: mouthFrown };
  parts.held = new THREE.Group(); parts.handR.add(parts.held);
  head.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.receiveShadow = false; } });
  g.userData = { parts, look: L, mood: 'neutral', action: 'idle', seed };
  setMood(g, L.mood || 'neutral');
  return g;
}

// ---------- Capy: the channel's narrator (a calm capybara referee with an orange on her head) ----------
export const CAPY = {
  fur: '#a8703f', furDark: '#5a3a22', shirt: '#f6f6f6', stripe: '#161616', headset: '#1e1e1e', orange: '#f28c28', leaf: '#3d8b3d',
  height: 1.0,           // overall scale relative to a person (she stands about chest high on a human)
  outfit: 'ref',         // 'ref' (football) | 'raincoat' (scary) | 'detective' (heists) | 'toga' (myth) | 'astronaut' (space) | 'cardigan' (psychology)
};
// one costume per series; the orange always stays on top (her signature)
export const CAPY_OUTFITS = {
  ref:       { shirt: '#f6f6f6', stripes: true,  whistle: true,  headset: true },
  raincoat:  { shirt: '#f2c230', hood: '#e0ad1c', headset: false, held: 'flashlight' },
  detective: { shirt: '#b08a5a', lapels: '#8c6a40', hat: '#4a3b2c', headset: false, held: 'magnifier' },
  toga:      { shirt: '#f4f1e8', sash: '#d9a521', laurel: '#4f8a3c', headset: false },
  astronaut: { shirt: '#eef1f5', panel: '#2b4c8c', dome: true, headset: false },
  cardigan:  { shirt: '#7a5c8e', glasses: '#2a2a2a', headset: false, held: 'notepad' },
};
export function capy(look = {}) {
  const C = { ...CAPY, ...look }; const O = { ...(CAPY_OUTFITS[C.outfit] || CAPY_OUTFITS.ref) };   // each outfit lists everything it wears
  if (!look.shirt) C.shirt = O.shirt;
  const g = new THREE.Group(); const parts = {};
  const fur = mat(C.fur, { roughness: 0.85 }), dark = mat(C.furDark, { roughness: 0.8 });
  const add = (parent, geo, m, pos, scl = [1, 1, 1], rot = [0, 0, 0]) => { const o = shadow(new THREE.Mesh(geo, m)); o.position.set(...pos); o.scale.set(...scl); o.rotation.set(...rot); parent.add(o); return o; };
  // legs + feet
  for (const sx of [-1, 1]) { const hip = new THREE.Group(); hip.position.set(sx * 0.28, 0.7, 0); g.add(hip);
    add(hip, new THREE.CapsuleGeometry(0.17, 0.35, 8, 16), fur, [0, -0.32, 0]); add(hip, new RoundedBoxGeometry(0.32, 0.14, 0.42, 3, 0.06), dark, [0, -0.62, 0.08]);
    parts[sx < 0 ? 'legL' : 'legR'] = hip; }
  // ref shirt body with stripes that follow the curve
  const torso = add(g, new THREE.CapsuleGeometry(0.6, 0.62, 16, 32), mat(C.shirt), [0, 1.35, 0], [1, 1, 0.82]); parts.torso = torso;
  for (let i = -3; i <= 3 && O.stripes; i++) {
    const a = (i * 0.32);
    add(g, new THREE.CapsuleGeometry(0.03, 0.82, 4, 8), mat(C.stripe), [Math.sin(a) * 0.605, 1.35, Math.cos(a) * 0.605 * 0.82], [1, 1, 0.4], [0, a, 0]);
    add(g, new THREE.CapsuleGeometry(0.03, 0.82, 4, 8), mat(C.stripe), [Math.sin(a + Math.PI) * 0.605, 1.35, Math.cos(a + Math.PI) * 0.605 * 0.82], [1, 1, 0.4], [0, a, 0]);
  }
  // whistle on a cord (ref only)
  if (O.whistle) {
    add(g, new THREE.TorusGeometry(0.33, 0.012, 6, 32, Math.PI), mat('#d62828'), [0, 1.95, 0.32], [1, 1, 1], [Math.PI * 0.6, 0, Math.PI]);
    add(g, new RoundedBoxGeometry(0.15, 0.09, 0.09, 3, 0.035), mat('#c9ced6', { metalness: 0.6, roughness: 0.3 }), [0, 1.64, 0.5]);
  }
  if (O.lapels) for (const sx of [-1, 1]) add(g, new RoundedBoxGeometry(0.22, 0.7, 0.05, 2, 0.02), mat(O.lapels), [sx * 0.16, 1.62, 0.5], [1, 1, 1], [-0.25, 0, sx * 0.25]);
  if (O.lapels) add(g, new THREE.TorusGeometry(0.62, 0.05, 8, 32), mat(O.lapels), [0, 1.05, 0], [1, 1, 0.82], [Math.PI / 2, 0, 0]);   // belt
  if (O.sash) add(g, new THREE.TorusGeometry(0.62, 0.06, 8, 32), mat(O.sash, { metalness: 0.3, roughness: 0.4 }), [0, 1.4, 0], [1, 1.25, 0.84], [Math.PI / 2, 0.6, 0]);
  if (O.panel) add(g, new RoundedBoxGeometry(0.5, 0.36, 0.06, 2, 0.03), mat(O.panel), [0, 1.55, 0.5]);
  if (O.panel) add(g, new RoundedBoxGeometry(0.9, 0.95, 0.4, 3, 0.1), mat('#c9ced6'), [0, 1.5, -0.55]);   // life-support pack
  if (O.hood) add(g, new THREE.TorusGeometry(0.42, 0.13, 10, 24), mat(O.hood), [0, 2.05, -0.1], [1, 1, 1], [Math.PI / 2 - 0.4, 0, 0]);
  // arms with paws, pivot at the shoulder so pose() works
  for (const sx of [-1, 1]) {
    const pivot = new THREE.Group(); pivot.position.set(sx * 0.58, 1.82, 0); g.add(pivot);
    add(pivot, new THREE.CapsuleGeometry(0.13, 0.42, 8, 16), fur, [0, -0.3, 0]);
    const paw = add(pivot, new THREE.SphereGeometry(0.15, 20, 14), dark, [0, -0.62, 0], [1, 0.85, 1]);
    pivot.rotation.z = sx * 0.12;
    parts[sx < 0 ? 'armL' : 'armR'] = pivot; parts[sx < 0 ? 'handL' : 'handR'] = paw;
  }
  // head: big rounded block with a long snout (capybara), set on the shoulders
  const head = new THREE.Group(); head.userData.baseY = 2.55; head.position.y = 2.55; g.add(head); parts.head = head;
  add(head, new RoundedBoxGeometry(1.05, 0.95, 1.1, 8, 0.4), fur, [0, 0.05, 0]);
  add(head, new RoundedBoxGeometry(0.86, 0.58, 0.55, 8, 0.24), fur, [0, -0.12, 0.55]);
  for (const sx of [-1, 1]) {
    add(head, new THREE.SphereGeometry(0.06, 14, 10), dark, [sx * 0.14, -0.02, 0.83], [1.3, 0.7, 0.6]);           // nostrils
    add(head, new THREE.SphereGeometry(0.12, 18, 12), dark, [sx * 0.42, 0.55, -0.05], [1, 0.75, 0.55]);          // ears
  }
  parts.eyes = [];
  for (const sx of [-1, 1]) {
    const e = add(head, new THREE.SphereGeometry(0.085, 18, 14), new THREE.MeshStandardMaterial({ color: '#141414', roughness: 0.3 }), [sx * 0.3, 0.27, 0.55], [1, 0.7, 0.5]); parts.eyes.push(e);
    const gl = add(head, new THREE.SphereGeometry(0.02, 8, 6), new THREE.MeshBasicMaterial({ color: '#fff' }), [sx * 0.3 + 0.03, 0.3, 0.6]); parts.eyes.push(gl);
    const lid = add(head, new THREE.SphereGeometry(0.1, 18, 12, 0, Math.PI * 2, 0, Math.PI * 0.45), fur, [sx * 0.3, 0.28, 0.54], [1, 0.8, 0.6]); // heavy lids = the unbothered look
    const brow = add(head, new RoundedBoxGeometry(0.16, 0.035, 0.04, 2, 0.012), dark, [sx * 0.3, 0.4, 0.56]); brow.visible = false;
    parts[sx < 0 ? 'browL' : 'browR'] = brow;
  }
  const mouthMat = mat('#3a1a10');
  const mFlat = add(head, new RoundedBoxGeometry(0.16, 0.025, 0.02, 2, 0.01), mouthMat, [0, -0.31, 0.79]);
  const mO = add(head, new THREE.SphereGeometry(0.055, 14, 10), mouthMat, [0, -0.31, 0.79], [1, 1.1, 0.4]);
  const smG = new THREE.TorusGeometry(0.08, 0.018, 8, 16, Math.PI);
  const mSmile = add(head, smG, mouthMat, [0, -0.27, 0.8], [1, 1, 1], [0, 0, Math.PI]);
  const mFrown = add(head, smG, mouthMat, [0, -0.36, 0.8]);
  parts.mouths = { flat: mFlat, o: mO, smile: mSmile, frown: mFrown };
  // headphones (ref) or the series' headwear, then the orange (signature)
  if (O.headset) {
    add(head, new THREE.TorusGeometry(0.6, 0.045, 10, 32, Math.PI), mat(C.headset), [0, 0.12, -0.05]);
    for (const sx of [-1, 1]) add(head, new THREE.CylinderGeometry(0.17, 0.17, 0.12, 24), mat(C.headset), [sx * 0.58, 0.05, -0.05], [1, 1, 1], [0, 0, Math.PI / 2]);
  }
  let oy = 0.72;
  if (O.hat) { add(head, new THREE.CylinderGeometry(0.85, 0.85, 0.05, 32), mat(O.hat), [0, 0.5, 0]); add(head, new THREE.CylinderGeometry(0.45, 0.5, 0.42, 32), mat(O.hat), [0, 0.72, 0]);
    add(head, new THREE.CylinderGeometry(0.51, 0.51, 0.1, 32), mat('#2a2018'), [0, 0.58, 0]); oy = 1.12; }
  if (O.laurel) for (let i = 0; i < 14; i++) { const a = (i / 14) * Math.PI * 2;
    add(head, new THREE.SphereGeometry(0.09, 10, 8), mat(O.laurel), [Math.sin(a) * 0.55, 0.48, Math.cos(a) * 0.58], [1.6, 0.5, 0.8], [0, a, 0.5]); }
  if (O.glasses) for (const sx of [-1, 1]) add(head, new THREE.TorusGeometry(0.13, 0.018, 8, 24), mat(O.glasses), [sx * 0.3, 0.27, 0.66]);
  if (O.glasses) add(head, new THREE.BoxGeometry(0.2, 0.02, 0.02), mat(O.glasses), [0, 0.3, 0.68]);
  if (O.dome) {   // open-face helmet: a white shell behind the head and a rim around the face, so her face stays readable
    const shell = shadow(new THREE.Mesh(new THREE.SphereGeometry(0.98, 40, 28, 0, Math.PI * 2, 0, Math.PI), mat('#eef1f5', { side: THREE.DoubleSide })));
    shell.scale.set(1, 1, 0.9); shell.position.set(0, 0.15, -0.12); shell.rotation.x = 0; head.add(shell);
    shell.geometry = new THREE.SphereGeometry(0.98, 40, 28, Math.PI * 0.62, Math.PI * 1.76);   // leave the front open
    add(head, new THREE.TorusGeometry(0.86, 0.07, 12, 40), mat('#c9ced6', { metalness: 0.4, roughness: 0.3 }), [0, 0.12, 0.42]); add(head, new THREE.TorusGeometry(0.72, 0.08, 10, 32), mat('#c9ced6'), [0, -0.62, 0.05], [1, 1, 1], [Math.PI / 2, 0, 0]); oy = 0.62; }
  const orange = add(head, new THREE.SphereGeometry(0.2, 28, 20), mat(C.orange, { roughness: 0.6 }), [0, oy, 0.05]); parts.orange = orange;
  add(head, new THREE.SphereGeometry(0.06, 12, 8), mat(C.leaf), [0.06, oy + 0.2, 0.05], [1, 0.4, 1.6]);
  parts.held = new THREE.Group(); parts.handR.add(parts.held);
  if (O.held && PROPS[O.held]) { const h = PROPS[O.held](); h.position.set(0, -0.1, 0.14); parts.held.add(h); parts.held.userData.outfitProp = true; }
  g.scale.setScalar(C.height);
  g.userData = { parts, look: C, mood: 'neutral', action: 'idle', seed: 101, isCapy: true };
  setMood(g, look.mood || 'smug');
  return g;
}

// mood: neutral | angry | worried | shocked | happy | sad | smug | confused
export function setMood(p, mood) {
  const P = p.userData.parts; p.userData.mood = mood;
  const brow = { neutral: [0, 0.22], angry: [0.42, 0.19], worried: [-0.38, 0.25], shocked: [-0.1, 0.3], happy: [-0.12, 0.25], sad: [-0.45, 0.22], smug: [0.2, 0.22], confused: [0.35, 0.22] }[mood] || [0, 0.22];
  P.browL.rotation.z = -brow[0]; P.browR.rotation.z = brow[0]; P.browL.position.y = P.browR.position.y = brow[1];
  if (mood === 'confused') { P.browR.rotation.z = -0.35; P.browR.position.y = 0.28; }
  const m = { neutral: 'flat', angry: 'frown', worried: 'flat', shocked: 'o', happy: 'smile', sad: 'frown', smug: 'smile', confused: 'flat' }[mood] || 'flat';
  for (const [k, v] of Object.entries(P.mouths)) v.visible = k === m;
}

// action: idle | talk | point | cheer | facepalm | shrug | throw | hold | cross | slump | clap | wave | run | catch | kick | celebrate
// Motion rules (J, 2026-11-20 UAT): every move must mean something. Idle is still (breathing, blinks, small head drift);
// talk is a small hand beat; one-shot moves play once on their own clock (g = seconds since the move starts), then hold.
// A kick or throw starts at its action time and makes contact / releases at MOTION.contact s; a catch is marked at the
// moment the ball arrives, so the hands rise over MOTION.reach s before it and close on the ball.
export const MOTION = {
  talkBeat: 0.25, gesture: 0.4, contact: 0.2, reach: 0.3,
  // gait: rate (rad/s), thigh swing, knee flex, arm swing, elbow base bend, pelvis bob, forward lean, chest twist
  walk: { rate: 7.5, thigh: 0.45, knee: 0.7, arm: 0.42, elbow: -0.3, bob: 0.05, lean: 0.06, twist: 0.1 },
  run: { rate: 13, thigh: 0.95, knee: 1.55, arm: 0.95, elbow: -1.55, bob: 0.13, lean: 0.32, twist: 0.16 },
};
const ease = (x) => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
export function pose(p, action, t, talking, g = 1) {
  const P = p.userData.parts, s = p.userData.seed;
  const breathe = Math.sin(t * 2.1 + s) * 0.012;
  P.torso.scale.y = 1 + breathe;
  P.head.position.y = (P.head.userData.baseY ?? 2.55 + STYLE.headRadius * 0.92) + breathe * 0.5;
  const bl = ((t + s * 0.37) % 3.5) < 0.12;
  for (const e of P.eyes) { if (e.userData.sy === undefined) e.userData.sy = e.scale.y; e.scale.y = bl ? e.userData.sy * 0.1 : e.userData.sy; }
  const mouths = P.mouths;
  if (talking && p.userData.mood !== 'shocked') {
    const open = Math.max(0, Math.sin(t * 17 + s)) > 0.35;
    const cur = Object.values(mouths).find((m) => m.visible);
    mouths.o.visible = open; if (cur && cur !== mouths.o) cur.visible = !open;
    if (!open && !Object.values(mouths).some((m) => m.visible)) mouths.flat.visible = true;
  }
  const k = action === 'catch' ? ease((g + MOTION.reach) / MOTION.reach) : ease(g / MOTION.gesture);
  // joint targets (radians). Shoulder x < 0 swings the arm forward; elbow x < 0 bends the forearm up;
  // hip x < 0 swings the leg forward; knee x > 0 bends the shin back. Left z > 0 / right z < 0 lifts the arm out.
  const J = { lx: 0, rx: 0, lz: 0.08, rz: -0.08, le: -0.12, re: -0.12, hl: 0, hr: 0, kl: 0.03, kr: 0.03, fl: 0, fr: 0, lean: 0, twist: 0, bob: 0 };
  const gait = (G) => { const ph = t * G.rate + s;
    J.hl = -G.thigh * Math.sin(ph); J.hr = G.thigh * Math.sin(ph);
    // knee flexes most mid-swing (thigh passing under the hip on its way forward), nearly straight at foot strike
    J.kl = 0.08 + G.knee * Math.pow(0.5 + 0.5 * Math.cos(ph + 0.3), 2); J.kr = 0.08 + G.knee * Math.pow(0.5 + 0.5 * Math.cos(ph + 0.3 + Math.PI), 2);
    J.fl = 0.25 * Math.sin(ph + 0.6); J.fr = 0.25 * Math.sin(ph + 0.6 + Math.PI);
    J.lx = G.arm * Math.sin(ph); J.rx = -G.arm * Math.sin(ph); J.le = J.re = G.elbow; J.lz = 0.12; J.rz = -0.12;
    J.bob = G.bob * Math.abs(Math.sin(ph)); J.lean = G.lean; J.twist = G.twist * Math.sin(ph);
    if (p.userData.carrying) { J.rx = -0.35; J.re = -1.7; J.rz = 0.25; } };
  switch (action) {
    case 'walk': gait(MOTION.walk); break;
    case 'run': gait(MOTION.run); break;
    case 'talk': J.rx = -0.35; J.re = -0.9 - Math.max(0, Math.sin(t * 3.2 + s)) * MOTION.talkBeat; J.rz = -0.15; break;
    case 'point': J.rx = -1.45 * k; J.re = -0.1; J.rz = -0.1; break;
    case 'cheer': case 'celebrate': J.lz = -2.45 * k; J.rz = 2.45 * k; J.lx = J.rx = -0.2 * k; J.le = J.re = -0.15 * k;   // a V, hands clear of the head
      if (action === 'celebrate') { J.bob = Math.abs(Math.sin(t * 7)) * 0.3 * k; J.kl = J.kr = 0.25 * Math.abs(Math.sin(t * 7)) * k; } break;
    case 'facepalm': J.rx = -1.1 * k; J.re = -2.3 * k; J.rz = 0.3 * k; break;
    case 'shrug': J.lz = -0.45 * k; J.rz = 0.45 * k; J.le = J.re = -1.5 * k; J.lx = J.rx = -0.2 * k; break;
    case 'throw': { const back = ease(g / (MOTION.contact * 0.6)) * (1 - k);   // wind up, then release at k = 0.5 (g = contact)
      J.rx = -2.6 * back - 1.1 * k; J.re = -1.7 * back - 0.15 * k; J.rz = -0.25; J.lx = -0.8 * back; J.le = -0.6;
      J.hl = -0.45 * k; J.kl = 0.2 * k; J.hr = 0.25 * k; J.twist = 0.35 * back - 0.25 * k; J.lean = 0.15 * k; break; }
    case 'kick': { const sw = Math.sin(Math.PI * k);
      J.hr = 0.5 * (1 - k) - 1.4 * sw; J.kr = 1.4 * (1 - k) * 0.6 + 0.1; J.hl = 0.1 * k; J.lz = -0.6; J.rz = 0.6; J.lean = -0.1 * sw; break; }
    case 'catch': J.lx = J.rx = -1.35 * k; J.le = J.re = -0.6 * k; J.lz = -0.15 * k; J.rz = 0.15 * k; break;
    case 'hold': J.rx = -0.45; J.re = -1.5; J.rz = 0.25; break;
    case 'cross': J.lx = J.rx = -0.55; J.le = J.re = -2.0; J.lz = -0.35; J.rz = 0.35; break;
    case 'slump': J.lean = 0.12; J.le = J.re = -0.05; break;
    case 'clap': { const c = Math.abs(Math.sin(t * 8)); J.lx = J.rx = -0.75; J.le = J.re = -1.2; J.lz = -0.2 - c * 0.25; J.rz = 0.2 + c * 0.25; break; }
    case 'wave': J.rz = 2.2; J.rx = -0.3; J.re = -0.5 + Math.sin(t * 7) * 0.3; break;
    default: break;   // idle: still
  }
  // z: negative swings the left arm out to the side, positive the right (armL sits at -x)
  P.armL.rotation.set(J.lx, 0, J.lz); P.armR.rotation.set(J.rx, 0, J.rz);
  if (P.elbowL) { P.elbowL.rotation.x = J.le; P.elbowR.rotation.x = J.re; }
  if (P.legL) { P.legL.rotation.x = J.hl; P.legR.rotation.x = J.hr; }
  if (P.kneeL) { P.kneeL.rotation.x = J.kl; P.kneeR.rotation.x = J.kr; P.footL.rotation.x = J.fl - J.kl * 0.3; P.footR.rotation.x = J.fr - J.kr * 0.3; }
  if (P.chest) { P.chest.rotation.set(J.lean, J.twist, 0); } else { p.rotation.order = 'YXZ'; p.rotation.x = J.lean; }
  p.position.y = J.bob;
  P.head.rotation.x = (action === 'slump' ? 0.35 : 0) + (P.head.userData.pitch || 0) - J.lean * 0.5;
}

// ---------- props ----------
export function football() {
  const b = shadow(new THREE.Mesh(new THREE.SphereGeometry(0.22, 24, 16), mat('#7a3b1d')));
  b.scale.set(0.68, 1, 0.68);
  const lace = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.2, 0.03), mat('#f5f5f5')); lace.position.z = 0.15; b.add(lace);
  return b;
}
export const PROPS = {
  football,
  clipboard: () => { const g = new THREE.Group(); const b = shadow(new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.56, 0.04), mat('#b7834a'))); g.add(b);
    const p = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.42), mat('#fbfbf6')); p.position.z = 0.025; g.add(p); return g; },
  phone: () => shadow(new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.38, 0.04), mat('#1d1d1f', { roughness: 0.3 }))),
  flag: () => shadow(new THREE.Mesh(new RoundedBoxGeometry(0.32, 0.32, 0.06, 2, 0.02), mat('#f6d21f'))),
  mic: () => { const g = new THREE.Group(); const h = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.32, 6), mat('#222')); g.add(h);
    const top = new THREE.Mesh(new THREE.IcosahedronGeometry(0.08, 1), mat('#555')); top.position.y = 0.2; g.add(top); return g; },
  trophy: () => { const g = new THREE.Group(); const m = mat('#e8b923', { roughness: 0.35, metalness: 0.4 });
    const ball = shadow(new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 6), m)); ball.scale.set(0.7, 1, 0.7); ball.position.y = 0.55; g.add(ball);
    const stem = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.45, 6), m)); stem.position.y = 0.25; g.add(stem);
    const base = shadow(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.08, 0.22), m)); g.add(base); return g; },
  foldedShirts: (color = '#1f6f86', n = 3) => { const g = new THREE.Group();
    for (let i = 0; i < n; i++) { const f = shadow(new THREE.Mesh(new RoundedBoxGeometry(0.9, 0.2, 0.7, 5, 0.09), mat(color))); f.position.y = 0.1 + i * 0.19; g.add(f);
      const fold = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, 0.68), mat(color)); fold.position.set(-0.2, 0.18 + i * 0.17, 0); g.add(fold); }
    const coll = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.025, 4, 10, Math.PI), mat(color)); coll.rotation.x = -Math.PI / 2; coll.position.set(0, 0.09 + n * 0.17, 0.28); g.add(coll);
    return g; },
  envelope: () => shadow(new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.28, 0.02), mat('#f3efe4'))),
  flashlight: () => { const g = new THREE.Group(); const b = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.42, 12), mat('#2b2b2e'))); b.rotation.x = Math.PI / 2; g.add(b);
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.07, 0.08, 16), mat('#fff6c8', { emissive: '#fff0a0', emissiveIntensity: 1.2 })); lens.rotation.x = Math.PI / 2; lens.position.z = 0.24; g.add(lens); return g; },
  magnifier: () => { const g = new THREE.Group(); const r = shadow(new THREE.Mesh(new THREE.TorusGeometry(0.14, 0.025, 8, 24), mat('#c9a227', { metalness: 0.5, roughness: 0.3 }))); r.position.y = 0.2; g.add(r);
    const gl = new THREE.Mesh(new THREE.CircleGeometry(0.13, 24), new THREE.MeshPhysicalMaterial({ color: '#dff3ff', transparent: true, opacity: 0.35 })); gl.position.y = 0.2; g.add(gl);
    const h = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.035, 0.24, 8), mat('#5a3a22'))); g.add(h); return g; },
  notepad: () => { const g = new THREE.Group(); const b = shadow(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.46, 0.04), mat('#f4efe2'))); g.add(b);
    const top = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.06, 0.05), mat('#7a5c8e')); top.position.y = 0.22; g.add(top); return g; },
  goldbar: () => shadow(new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.18, 0.26, 2, 0.03), mat('#e8b923', { metalness: 0.6, roughness: 0.3 }))),
  bag: () => { const g = new THREE.Group(); const b = shadow(new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 12), mat('#8a7a5c'))); b.scale.set(1, 1.1, 0.9); g.add(b);
    const lbl = new THREE.Mesh(new THREE.PlaneGeometry(0.28, 0.28), new THREE.MeshBasicMaterial({ map: textTexture('$', { w: 128, h: 128, bg: '#8a7a5c', fg: '#1d1d1f', font: '900 110px Inter, Arial' }) })); lbl.position.z = 0.28; g.add(lbl); return g; },
  candle: () => { const g = new THREE.Group(); const c = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.36, 12), mat('#f3ead2'))); g.add(c);
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), mat('#ffb347', { emissive: '#ffa020', emissiveIntensity: 1.5 })); f.scale.y = 1.6; f.position.y = 0.26; g.add(f); return g; },
  scroll: () => { const g = new THREE.Group(); const p = shadow(new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.5), mat('#efe2c0', { side: THREE.DoubleSide }))); g.add(p);
    for (const y of [-0.26, 0.26]) { const r = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.48, 10), mat('#8a5a33'))); r.rotation.z = Math.PI / 2; r.position.y = y; g.add(r); } return g; },
  lyre: () => { const g = new THREE.Group(); const m = mat('#d9a521', { metalness: 0.4, roughness: 0.4 });
    for (const sx of [-1, 1]) { const a = shadow(new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.025, 8, 16, Math.PI), m)); a.position.x = sx * 0.12; a.rotation.z = sx > 0 ? 0 : Math.PI; g.add(a); }
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.5, 8), m); bar.rotation.z = Math.PI / 2; bar.position.y = 0.2; g.add(bar); return g; },
};

// ---------- sets ----------
function tileTexture(a = '#e9ddcc', b = '#d9cbb8', n = 8) {
  const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
  x.fillStyle = a; x.fillRect(0, 0, 512, 512); x.strokeStyle = b; x.lineWidth = 4;
  for (let i = 0; i <= n; i++) { const v = (i * 512) / n; x.beginPath(); x.moveTo(v, 0); x.lineTo(v, 512); x.stroke(); x.beginPath(); x.moveTo(0, v); x.lineTo(512, v); x.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(6, 6); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function floor(g, colorA, colorB, size = 60, rough = 0.45) {
  const f = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshStandardMaterial({ map: tileTexture(colorA, colorB), roughness: rough }));
  f.rotation.x = -Math.PI / 2; f.receiveShadow = true; g.add(f);
}
function wall(g, color, z = -7, w = 60, h = 14) { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat(color)); m.position.set(0, h / 2, z); m.receiveShadow = true; g.add(m); return m; }
function ceilingLights(g, y = 9, z = -2, n = 4) {
  for (let i = 0; i < n; i++) for (const zz of [z, z + 5]) { const l = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.06, 0.8), new THREE.MeshBasicMaterial({ color: '#fffaf0' })); l.position.set((i - (n - 1) / 2) * 5, y, zz); g.add(l); }
}
function board(g, pos, size, lines, opts) {
  const frame = shadow(new THREE.Mesh(new THREE.BoxGeometry(size[0] + 0.2, size[1] + 0.2, 0.12), mat(opts?.frame || '#2b2b2e')));
  frame.position.set(...pos); g.add(frame);
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(...size), new THREE.MeshBasicMaterial({ map: textTexture(lines, opts) }));
  screen.position.set(pos[0], pos[1], pos[2] + 0.07); g.add(screen);
  screen.userData.frame = frame;
  return screen;
}

// Each set returns { group, spots: named [x, z] positions, board?: (lines) => void }
export const SETS = {
  locker({ teamA = '#f28c28', teamB = '#1f3f8f', boardText = ['GAME PLAN'] } = {}) {
    const g = new THREE.Group(); floor(g, '#e8dccb', '#d6c6b1'); wall(g, '#f2e8da');
    for (let i = -8; i <= 8; i++) {
      const lk = shadow(new THREE.Mesh(new THREE.BoxGeometry(1.3, 4.4, 1.1), mat('#1d6a7e'))); lk.position.set(i * 1.4, 2.2, -6.4); g.add(lk);
      const vent = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.1, 0.02), mat('#e9e0d0')); vent.position.set(i * 1.4, 3.9, -5.84); g.add(vent);
      const jer = shadow(new THREE.Mesh(new RoundedBoxGeometry(0.85, 1.05, 0.14, 3, 0.06), mat(i % 3 === 0 ? teamB : teamA))); jer.position.set(i * 1.4, 2.6, -5.8); g.add(jer);
    }
    const bench = shadow(new THREE.Mesh(new THREE.BoxGeometry(16, 0.25, 0.85), mat('#d9984a'))); bench.position.set(0, 0.8, -4.7); g.add(bench);
    for (const x of [-7, -2, 3, 7]) { const l = shadow(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.8, 0.65), mat('#b57a37'))); l.position.set(x, 0.4, -4.7); g.add(l); }
    ceilingLights(g, 9.5, -3);
    const screen = board(g, [6.2, 5.2, -5.7], [4, 2.2], boardText, { bg: '#ffffff', fg: '#1b2a5c' });
    return { group: g, spots: { center: [0, 0], left: [-2.2, 0.3], right: [2.2, 0.3], back: [0, -3.2], bench: [-3.5, -4.2], board: [5, -4] }, screen };
  },
  // field: a broadcast view. The field runs along x (left to right on screen), the stands sit behind it (−z).
  // Yard lines every 5 units; end zones at both ends in team colors. Plays run along x.
  field({ boardText = ['HOME 0', 'AWAY 0'], grass = '#4f9a3c', length = 220, endZone = 90, zoneA = '#1f3f8f', zoneB = '#c8102e', zoneText = null } = {}) {
    const g = new THREE.Group();
    const c = document.createElement('canvas'); c.width = 1024; c.height = 64; const x = c.getContext('2d');
    for (let i = 0; i < 16; i++) { x.fillStyle = i % 2 ? grass : '#5aa846'; x.fillRect(i * 64, 0, 64, 64); }
    x.fillStyle = '#ffffff'; for (let i = 0; i < 16; i++) x.fillRect(i * 64, 0, 4, 64);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(length / 80, 1); t.colorSpace = THREE.SRGBColorSpace;
    const f = new THREE.Mesh(new THREE.PlaneGeometry(length, 60), new THREE.MeshStandardMaterial({ map: t, roughness: 0.95 })); f.rotation.x = -Math.PI / 2; f.position.z = 6; f.receiveShadow = true; g.add(f);
    for (const [sx, col] of [[1, zoneB], [-1, zoneA]]) {
      const ez = new THREE.Mesh(new THREE.PlaneGeometry(20, 60), mat(col, { roughness: 0.9 })); ez.rotation.x = -Math.PI / 2; ez.position.set(sx * (endZone + 10), 0.01, 6); ez.receiveShadow = true; g.add(ez);
      const gl = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 60), mat('#ffffff')); gl.rotation.x = -Math.PI / 2; gl.position.set(sx * endZone, 0.02, 6); g.add(gl);
      if (zoneText) { const zt = new THREE.Mesh(new THREE.PlaneGeometry(16, 4), new THREE.MeshBasicMaterial({ map: textTexture(zoneText, { w: 1024, h: 256, bg: col, fg: '#ffffff', font: '900 180px Inter, Arial' }) }));
        zt.rotation.set(-Math.PI / 2, 0, sx * Math.PI / 2); zt.position.set(sx * (endZone + 10), 0.03, 6); g.add(zt); }
    }
    // stands: stepped rows filled with seated fans (instanced bodies and heads, team-colored shirts)
    const rows = 7, perRow = Math.floor(length / 0.85);
    const bodies = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.26, 0.32, 4, 10), mat('#ffffff'), rows * perRow);
    const heads = new THREE.InstancedMesh(new THREE.SphereGeometry(0.22, 12, 10), mat('#ffffff'), rows * perRow);
    const m4 = new THREE.Matrix4(), col = new THREE.Color(); let n = 0;
    const shirts = ['#f28c28', '#1f3f8f', '#e94f37', '#f7d84a', '#ffffff', '#3a3a3a', '#4b92db', '#c8102e'];
    for (let r = 0; r < rows; r++) {
      const row = shadow(new THREE.Mesh(new THREE.BoxGeometry(length, 0.9, 1.2), mat(r % 2 ? '#c9ced6' : '#b9bfc9'))); row.position.set(0, 0.45 + r * 0.9, -14 - r * 1.2); g.add(row);
      for (let i = 0; i < perRow; i++, n++) {
        const h = Math.abs(Math.sin(i * 12.9898 + r * 78.233) * 43758.5453) % 1;   // stable pseudo-random per seat
        const x = -length / 2 + i * 0.85 + (r % 2) * 0.42 + (h - 0.5) * 0.2, y = 0.9 + r * 0.9, z = -14 - r * 1.2;
        m4.makeTranslation(x, y + 0.42, z); bodies.setMatrixAt(n, m4); bodies.setColorAt(n, col.set(shirts[Math.floor(h * shirts.length)]));
        m4.makeTranslation(x, y + 0.98 + h * 0.06, z); heads.setMatrixAt(n, m4); heads.setColorAt(n, col.set(STYLE.skinTones[Math.floor(h * 97) % STYLE.skinTones.length]));
      }
    }
    bodies.castShadow = heads.castShadow = false; g.add(bodies); g.add(heads);
    const goal = new THREE.Group(); const gm = mat('#f6d21f');
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 3, 12), gm); post.position.y = 1.5; goal.add(post);
    const cross = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 5.6, 12), gm); cross.rotation.x = Math.PI / 2; cross.position.y = 3; goal.add(cross);
    for (const sz of [-1, 1]) { const u = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 6, 12), gm); u.position.set(0, 6, sz * 2.8); goal.add(u); }
    for (const sx of [-1, 1]) { const gg = goal.clone(); gg.position.set(sx * (endZone + 20), 0, -4); g.add(gg); }
    const screen = board(g, [-7, 8.8, -22.5], [7, 3], boardText, { bg: '#101418', fg: '#ffffff', accent: '#f6d21f', font: '900 150px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2.4, 0.4], right: [2.4, 0.4], back: [0, -4], sideline: [-6, 2] }, screen, sky: '#bfe3ff', follows: true };
  },
  press({ backdrop = '#1f3f8f', boardText = ['POSTGAME'] } = {}) {
    const g = new THREE.Group(); floor(g, '#5b5f6b', '#4f535e', 60, 0.7);
    const bd = new THREE.Mesh(new THREE.PlaneGeometry(20, 8), mat(backdrop)); bd.position.set(0, 4, -3.2); bd.receiveShadow = true; g.add(bd);
    for (let i = -4; i <= 4; i++) for (let j = 0; j < 3; j++) { const lg = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.6), new THREE.MeshBasicMaterial({ map: textTexture('★', { w: 128, h: 64, bg: backdrop, fg: '#ffffff', font: '900 50px Inter, Arial' }) })); lg.position.set(i * 2, 2.2 + j * 1.8, -3.18); g.add(lg); }
    const table = shadow(new THREE.Mesh(new THREE.BoxGeometry(5, 1.1, 1.3), mat('#f2f2f2'))); table.position.set(0, 0.55, 0.9); g.add(table);
    const skirt = new THREE.Mesh(new THREE.PlaneGeometry(5, 1.0), mat(backdrop)); skirt.position.set(0, 0.55, 1.56); g.add(skirt);
    for (const x of [-0.5, 0, 0.5]) { const m = PROPS.mic(); m.position.set(x, 1.35, 1.3); m.rotation.x = -0.6; g.add(m); }
    const screen = board(g, [5.6, 4.2, -3.1], [3, 1.6], boardText, { bg: '#ffffff', fg: backdrop });
    return { group: g, spots: { center: [0, 0], left: [-1.5, 0], right: [1.5, 0], reporter: [0.5, 5] }, screen };
  },
  office({ boardText = ['DRAFT BOARD'] } = {}) {
    const g = new THREE.Group(); floor(g, '#cdb79a', '#bba487', 60, 0.6); wall(g, '#eae3d6', -5);
    const desk = shadow(new THREE.Mesh(new THREE.BoxGeometry(4.4, 1.2, 1.8), mat('#8a5a33'))); desk.position.set(0, 0.6, -1.4); g.add(desk);
    const win = new THREE.Mesh(new THREE.PlaneGeometry(6, 3.6), new THREE.MeshBasicMaterial({ color: '#cfe9ff' })); win.position.set(-4.5, 4, -4.95); g.add(win);
    for (let i = 0; i < 3; i++) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.08, 3.6, 0.1), mat('#ffffff')); m.position.set(-6 + i * 1.5 + 0.75, 4, -4.9); g.add(m); }
    const tv = board(g, [3.8, 4.2, -4.85], [4.2, 2.4], boardText, { bg: '#ffffff', fg: '#1b2a5c' });
    const plant = shadow(new THREE.Mesh(facet(new THREE.IcosahedronGeometry(0.7, 1), 0.1, 3), mat('#5c9e4a'))); plant.position.set(-2.8, 1.5, -3.5); g.add(plant);
    const pot = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.3, 0.8, 7), mat('#c46a3c'))); pot.position.set(-2.8, 0.4, -3.5); g.add(pot);
    ceilingLights(g, 9, -2, 2);
    return { group: g, spots: { center: [0, 0], desk: [0, -2.6], left: [-2, 0.4], right: [2, 0.4] }, screen: tv };
  },
  living({ boardText = ['LIVE'], couch = '#4a6fb5' } = {}) {
    const g = new THREE.Group(); floor(g, '#c9a37a', '#b68f66', 60, 0.6); wall(g, '#f3ead8', -5);
    const tv = board(g, [0, 3.6, -4.85], [5, 2.8], boardText, { bg: '#0e1b2e', fg: '#ffffff', accent: '#f6d21f' });
    const base = shadow(new THREE.Mesh(new THREE.BoxGeometry(5.5, 0.8, 0.8), mat('#7d5434'))); base.position.set(0, 0.4, -4.4); g.add(base);
    const seat = shadow(new THREE.Mesh(facet(new THREE.BoxGeometry(5, 0.8, 1.6, 4, 1, 2), 0.04, 2), mat(couch))); seat.position.set(0, 0.6, 2.6); g.add(seat);
    const back = shadow(new THREE.Mesh(facet(new THREE.BoxGeometry(5, 1.4, 0.5, 4, 2, 1), 0.04, 3), mat(couch))); back.position.set(0, 1.4, 3.4); g.add(back);
    const lamp = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.6, 0.8, 8), mat('#fff3c9', { emissive: '#ffe8a0', emissiveIntensity: 0.4 }))); lamp.position.set(-4, 3, -4); g.add(lamp);
    return { group: g, spots: { center: [0, 0], couchL: [-1.2, 2.2], couchR: [1.2, 2.2], tv: [0, -3] }, screen: tv };
  },
  // ---- story series sets (2026-11-21) ----
  haunted({ boardText = ['CASE FILE'] } = {}) {   // scary: a dark old hallway, moonlit window, candles, portraits
    const g = new THREE.Group(); floor(g, '#4a3a30', '#3e3028', 60, 0.8); wall(g, '#3b3348', -5);
    for (let i = -6; i <= 6; i++) { const s2 = new THREE.Mesh(new THREE.PlaneGeometry(0.08, 14), mat('#2e2838')); s2.position.set(i * 1.6, 7, -4.98); g.add(s2); }
    const win = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 3.4), new THREE.MeshBasicMaterial({ color: '#9fb4d8' })); win.position.set(-4.2, 4.4, -4.95); g.add(win);
    const moon = new THREE.Mesh(new THREE.CircleGeometry(0.5, 32), new THREE.MeshBasicMaterial({ color: '#fff8dc' })); moon.position.set(-3.7, 5.3, -4.93); g.add(moon);
    for (const x of [-4.2]) { const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.1, 3.4, 0.1), mat('#1e1a24')); m1.position.set(x, 4.4, -4.9); g.add(m1); const m2 = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.1, 0.1), mat('#1e1a24')); m2.position.set(x, 4.4, -4.9); g.add(m2); }
    for (const [x, c] of [[0.5, '#6b4f3a'], [3.2, '#5a4a6a']]) { const fr = shadow(new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.8, 0.1), mat('#8a6a2a', { metalness: 0.3 }))); fr.position.set(x, 4.6, -4.9); g.add(fr);
      const pic = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.5), mat(c)); pic.position.set(x, 4.6, -4.84); g.add(pic); }
    const table = shadow(new THREE.Mesh(new THREE.BoxGeometry(2, 1, 0.8), mat('#3a2a20'))); table.position.set(3.5, 0.5, -3.8); g.add(table);
    for (const x of [3, 3.6, 4.1]) { const c = PROPS.candle(); c.position.set(x, 1.18, -3.8); g.add(c); }
    const screen = board(g, [-0.2, 7.6, -4.9], [3.2, 1.1], boardText, { bg: '#1e1a24', fg: '#e8e0ff', font: '900 120px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2, 0.4], right: [2, 0.4], back: [0, -3], window: [-4, -3.4], table: [3.5, -2.8] }, screen, sky: '#141722' };
  },
  vault({ boardText = ['THE JOB'] } = {}) {   // heists: a bank vault with a round door and stacked gold
    const g = new THREE.Group(); floor(g, '#d9d4c7', '#c9c3b4', 60, 0.35); wall(g, '#8f99a3', -5);
    const door = shadow(new THREE.Mesh(new THREE.CylinderGeometry(2.4, 2.4, 0.5, 48), mat('#b7bec7', { metalness: 0.6, roughness: 0.35 }))); door.rotation.x = Math.PI / 2; door.position.set(-3, 3, -4.7); g.add(door);
    const hub = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.3, 24), mat('#7f8790', { metalness: 0.7, roughness: 0.3 }))); hub.rotation.x = Math.PI / 2; hub.position.set(-3, 3, -4.35); g.add(hub);
    for (let i = 0; i < 6; i++) { const sp = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.6, 8), mat('#5f6770', { metalness: 0.7 })); sp.position.set(-3, 3, -4.3); sp.rotation.z = (i / 6) * Math.PI; g.add(sp); }
    for (let r = 0; r < 3; r++) for (let i = 0; i < 4 - r; i++) { const gb = PROPS.goldbar(); gb.position.set(2.2 + i * 0.55 + r * 0.27, 0.09 + r * 0.18, -3.6); g.add(gb); }
    const shelf = shadow(new THREE.Mesh(new THREE.BoxGeometry(4, 3.2, 0.6), mat('#6e757d', { metalness: 0.4 }))); shelf.position.set(3.4, 1.6, -4.6); g.add(shelf);
    for (let r = 0; r < 3; r++) for (let i = 0; i < 6; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.8, 0.05), mat('#8a9299', { metalness: 0.5 })); b.position.set(1.85 + i * 0.62, 0.6 + r * 1.0, -4.28); g.add(b); }
    ceilingLights(g, 9, -2, 3);
    const screen = board(g, [1.2, 6.6, -4.9], [3.6, 1.2], boardText, { bg: '#1d1d1f', fg: '#f6d21f', font: '900 120px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2, 0.4], right: [2, 0.4], door: [-3, -2.4], gold: [2.8, -2.6] }, screen };
  },
  temple({ boardText = ['THE MYTH'], sky = '#bfe3ff' } = {}) {   // mythology: marble floor, columns, a statue plinth, open sky
    const g = new THREE.Group(); floor(g, '#efe9dc', '#e2dac8', 60, 0.3);
    for (const x of [-6, -3.6, 3.6, 6]) { const c = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.5, 7, 20), mat('#f3efe6'))); c.position.set(x, 3.5, -4.5); g.add(c);
      const cap = shadow(new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.35, 1.3), mat('#ebe5d8'))); cap.position.set(x, 7.15, -4.5); g.add(cap); }
    const lintel = shadow(new THREE.Mesh(new THREE.BoxGeometry(14, 0.8, 1.6), mat('#ebe5d8'))); lintel.position.set(0, 7.7, -4.5); g.add(lintel);
    const ped = shadow(new THREE.Mesh(new THREE.CylinderGeometry(4.8, 4.8, 0.6, 3), mat('#ebe5d8'))); ped.rotation.x = Math.PI / 2; ped.rotation.z = Math.PI / 2; ped.scale.set(1, 1, 0.3); ped.position.set(0, 9.4, -4.5); g.add(ped);
    const plinth = shadow(new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.2, 1.4), mat('#e2dac8'))); plinth.position.set(0, 0.6, -4); g.add(plinth);
    const urn = shadow(new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 14), mat('#c46a3c'))); urn.scale.set(1, 1.2, 1); urn.position.set(0, 1.8, -4); g.add(urn);
    for (const x of [-1.8, 1.8]) { const br = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.9, 12), mat('#8a7a5c', { metalness: 0.4 }))); br.position.set(x, 0.45, -3.2); g.add(br);
      const fl = new THREE.Mesh(new THREE.ConeGeometry(0.25, 0.6, 10), mat('#ffb347', { emissive: '#ff8c1a', emissiveIntensity: 1.2 })); fl.position.set(x, 1.2, -3.2); g.add(fl); }
    const screen = board(g, [0, 6.4, -4.2], [3.6, 1.0], boardText, { bg: '#2b4c8c', fg: '#f6e7b8', font: '900 120px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2.2, 0.4], right: [2.2, 0.4], altar: [0, -2.6], columnL: [-3.6, -3.2], columnR: [3.6, -3.2] }, screen, sky };
  },
  space({ boardText = ['MISSION LOG'] } = {}) {   // space: station deck with a big window onto stars and a planet
    const g = new THREE.Group(); floor(g, '#9aa3ad', '#8a939d', 60, 0.4); wall(g, '#d8dde3', -5);
    const win = new THREE.Mesh(new THREE.CircleGeometry(2.6, 48), new THREE.MeshBasicMaterial({ color: '#05060c' })); win.position.set(-2.5, 4.2, -4.95); g.add(win);
    const rim = shadow(new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.18, 12, 48), mat('#b7bec7', { metalness: 0.5 }))); rim.position.set(-2.5, 4.2, -4.9); g.add(rim);
    const planet = new THREE.Mesh(new THREE.CircleGeometry(0.9, 32), new THREE.MeshBasicMaterial({ color: '#4b92db' })); planet.position.set(-1.6, 3.5, -4.93); g.add(planet);
    const ringP = new THREE.Mesh(new THREE.RingGeometry(1.1, 1.3, 32), new THREE.MeshBasicMaterial({ color: '#e8d6a0', side: THREE.DoubleSide })); ringP.position.set(-1.6, 3.5, -4.92); ringP.scale.y = 0.3; g.add(ringP);
    for (let i = 0; i < 40; i++) { const a = i * 2.39996, rr = 0.4 + (i % 9) * 0.24; const st = new THREE.Mesh(new THREE.CircleGeometry(0.025, 6), new THREE.MeshBasicMaterial({ color: '#ffffff' }));
      st.position.set(-2.5 + Math.cos(a) * rr, 4.2 + Math.sin(a) * rr, -4.94); g.add(st); }
    const console1 = shadow(new THREE.Mesh(new THREE.BoxGeometry(3.4, 1.2, 1.2), mat('#5f6770', { metalness: 0.4 }))); console1.position.set(3, 0.6, -3.8); g.add(console1);
    for (let i = 0; i < 5; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.05, 0.2), mat(['#e94f37', '#f6d21f', '#5cd65c', '#4b92db', '#ffffff'][i], { emissive: ['#e94f37', '#f6d21f', '#5cd65c', '#4b92db', '#ffffff'][i], emissiveIntensity: 0.6 })); b.position.set(1.8 + i * 0.6, 1.23, -3.6); g.add(b); }
    ceilingLights(g, 9, -2, 3);
    const screen = board(g, [3, 4.4, -4.9], [3.4, 1.9], boardText, { bg: '#0e1b2e', fg: '#9fe3ff', font: '900 110px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2, 0.4], right: [2, 0.4], window: [-2.5, -3.2], console: [3, -2.6] }, screen };
  },
  study({ boardText = ['SESSION'] } = {}) {   // psychology: a warm therapist's study, couch, armchair, bookshelf, rug
    const g = new THREE.Group(); floor(g, '#a87c56', '#996f4b', 60, 0.6); wall(g, '#e9dcc6', -5);
    const shelf = shadow(new THREE.Mesh(new THREE.BoxGeometry(3.4, 4.6, 0.6), mat('#6b4426'))); shelf.position.set(-3.6, 2.3, -4.6); g.add(shelf);
    const cols = ['#c0392b', '#2e86c1', '#27ae60', '#f39c12', '#8e44ad', '#16a085', '#d35400'];
    for (let r = 0; r < 4; r++) for (let i = 0; i < 9; i++) { const bk = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.75, 0.4), mat(cols[(i * 3 + r) % cols.length])); bk.position.set(-4.95 + i * 0.34, 0.6 + r * 1.1, -4.4); g.add(bk); }
    const rug = new THREE.Mesh(new THREE.CircleGeometry(3, 40), mat('#7a5c8e', { roughness: 0.95 })); rug.rotation.x = -Math.PI / 2; rug.position.set(0.5, 0.02, -0.5); g.add(rug);
    const seat = shadow(new THREE.Mesh(new RoundedBoxGeometry(3.4, 0.7, 1.4, 4, 0.2), mat('#3f6b5c'))); seat.position.set(2.6, 0.5, -3.2); g.add(seat);
    const back = shadow(new THREE.Mesh(new RoundedBoxGeometry(3.4, 1.2, 0.5, 4, 0.2), mat('#3f6b5c'))); back.position.set(2.6, 1.2, -3.9); g.add(back);
    const lamp = shadow(new THREE.Mesh(new THREE.ConeGeometry(0.5, 0.6, 16, 1, true), mat('#f6e7b8', { emissive: '#ffe8a0', emissiveIntensity: 0.6, side: THREE.DoubleSide }))); lamp.position.set(0.6, 3.6, -4.2); g.add(lamp);
    const pole = shadow(new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 3.3, 8), mat('#2a2a2a'))); pole.position.set(0.6, 1.65, -4.2); g.add(pole);
    const plant = shadow(new THREE.Mesh(facet(new THREE.IcosahedronGeometry(0.7, 1), 0.1, 3), mat('#5c9e4a'))); plant.position.set(5.2, 1.5, -3.8); g.add(plant);
    const screen = board(g, [1.6, 5.4, -4.9], [3, 1.2], boardText, { bg: '#f4efe2', fg: '#5a3e6e', font: '900 110px Inter, Arial' });
    return { group: g, spots: { center: [0, 0], left: [-2, 0.4], right: [2, 0.4], couch: [2.6, -2.4], shelf: [-3.6, -3.4] }, screen };
  },
  tunnel({ boardText = ['GAME DAY'] } = {}) {
    const g = new THREE.Group(); floor(g, '#6b6f78', '#5d616a', 60, 0.5);
    for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(40, 8), mat('#d8d2c6')); w.position.set(sx * 4.5, 4, -10); w.rotation.y = -sx * Math.PI / 2; w.receiveShadow = true; g.add(w); }
    const end = new THREE.Mesh(new THREE.PlaneGeometry(9, 8), new THREE.MeshBasicMaterial({ color: '#fff6e0' })); end.position.set(0, 4, -28); g.add(end);
    const banner = board(g, [0, 6, -12], [7, 1.4], boardText, { bg: '#1f3f8f', fg: '#ffffff', font: '900 130px Inter, Arial' });
    for (let z = 0; z > -26; z -= 4) { const l = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.06, 0.6), new THREE.MeshBasicMaterial({ color: '#fffaf0' })); l.position.set(0, 7.8, z); g.add(l); }
    return { group: g, spots: { center: [0, 0], left: [-1.6, 0.3], right: [1.6, 0.3], back: [0, -6] }, screen: banner };
  },
};

export function lights(scene) {
  const hemi = new THREE.HemisphereLight(STYLE.fill.sky, STYLE.fill.ground, STYLE.fill.intensity); scene.add(hemi);
  const key = new THREE.DirectionalLight(STYLE.key.color, STYLE.key.intensity); key.position.set(...STYLE.key.pos); key.castShadow = true;
  key.shadow.mapSize.set(1536, 1536); Object.assign(key.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 0.5, far: 60 });
  key.shadow.radius = STYLE.shadowRadius; key.shadow.bias = -0.0008; key.shadow.normalBias = 0.04; scene.add(key);
  const rim = new THREE.DirectionalLight(STYLE.rim.color, STYLE.rim.intensity); rim.position.set(...STYLE.rim.pos); scene.add(rim);
  return { hemi, key, rim };
}
