import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const W = 1280, H = 720;
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0e1016);
const camera = new THREE.PerspectiveCamera(32, W / H, 5, 6000);

scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x23262e, 0.9));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(500, 800, 900); scene.add(key);
const rim = new THREE.DirectionalLight(0x8fc6ff, 1.2); rim.position.set(-700, 300, -600); scene.add(rim);
const fill = new THREE.DirectionalLight(0xffe2c4, 0.5); fill.position.set(-400, -300, 600); scene.add(fill);

// helmet frame (Z up, -Y front) → three (Y up, +Z toward the viewer)
const world = new THREE.Group(); world.rotation.x = -Math.PI / 2; scene.add(world);
const helmet = new THREE.Group(); world.add(helmet);
const visorPivot = new THREE.Group(); helmet.add(visorPivot);

const M = {
  shell: new THREE.MeshStandardMaterial({ color: 0xf1eee6, roughness: 0.55, metalness: 0.0, transparent: true, opacity: 1, side: THREE.DoubleSide }),
  ear: new THREE.MeshPhysicalMaterial({ color: 0xd7e6f3, roughness: 0.25, transparent: true, opacity: 0.62, side: THREE.DoubleSide }),
  tube: new THREE.MeshStandardMaterial({ color: 0x9fdcff, emissive: 0x2aa9ff, emissiveIntensity: 0.0, transparent: true, opacity: 0.55, roughness: 0.15 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x24272e, roughness: 0.6 }),
  visor: new THREE.MeshStandardMaterial({ color: 0x17181c, roughness: 0.55, side: THREE.DoubleSide }),
  hat: new THREE.MeshStandardMaterial({ color: 0xf6f4ee, roughness: 0.4, transparent: true, opacity: 0.9 }),
  mount: new THREE.MeshStandardMaterial({ color: 0x3b4150, roughness: 0.5 }),
  dome: new THREE.MeshStandardMaterial({ color: 0x5a6273, roughness: 0.5 }),
  wall: new THREE.MeshStandardMaterial({ color: 0xcfc9bf, roughness: 0.95 }),
};
const P = {};
const loader = new GLTFLoader();
function load(name, mat, parent) {
  return new Promise(res => loader.load(`glb/${name}.glb`, g => {
    const grp = new THREE.Group();
    g.scene.traverse(o => { if (o.isMesh) { o.material = mat; o.geometry.computeVertexNormals(); } });
    grp.add(g.scene); parent.add(grp); P[name] = grp; res();
  }));
}
let D;
const ready = (async () => {
  D = await (await fetch('glb/scene.json')).json();
  await Promise.all([
    load('shell', M.shell, helmet), load('shell_half_TOP', M.shell, helmet), load('shell_half_BOTTOM', M.shell, helmet),
    load('ear_L', M.ear, helmet), load('ear_R', M.ear, helmet),
    load('visor', M.visor, visorPivot), load('pivot_cap', M.dark, helmet),
    load('electronics_tray', M.dark, helmet), load('hat_crown_plate', M.dark, helmet),
    load('hardhat_envelope_REFERENCE', M.hat, helmet),
    load('wm_bracket', M.mount, world), load('wm_cradle', M.mount, world), load('wm_post', M.dome, world), load('wm_dome', M.dome, world),
  ]);
  // ear blade tubes
  D.tubes.forEach((t, i) => {
    const a = new THREE.Vector3(...t[0]), b = new THREE.Vector3(...t[1]);
    const len = a.distanceTo(b), geo = new THREE.CylinderGeometry(D.tube_d / 2, D.tube_d / 2, len, 28, 1, true);
    const m = new THREE.Mesh(geo, M.tube.clone());
    m.position.copy(a.clone().add(b).multiplyScalar(0.5));
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    const g = new THREE.Group(); g.add(m); helmet.add(g); P['tube' + i] = g; g.userData.ear = i < 3 ? 0 : 1;
  });
  // LED windows: front half only (as built), small emissive squares just proud of the shell
  const front = D.pixels.filter(p => p[1] < 0);
  const geo = new THREE.PlaneGeometry(8.5, 8.5);
  const mat = new THREE.MeshBasicMaterial({ toneMapped: false, side: THREE.DoubleSide });
  const inst = new THREE.InstancedMesh(geo, mat, front.length);
  const dummy = new THREE.Object3D(), z = new THREE.Vector3(0, 0, 1);
  front.forEach((p, i) => {
    const n = new THREE.Vector3(...p).normalize();
    dummy.position.copy(n.clone().multiplyScalar(D.R_O + 0.4));
    dummy.quaternion.setFromUnitVectors(z, n); dummy.updateMatrix(); inst.setMatrixAt(i, dummy.matrix);
    inst.setColorAt(i, new THREE.Color(0, 0, 0));
  });
  helmet.add(inst); P.leds = inst; P.ledPts = front;
  // wall
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(1400, 1200), M.wall);
  wall.position.set(0, 205.17 + 10, -150); wall.rotation.x = Math.PI / 2; world.add(wall); P.wall = wall;
  window.__ready = true;
})();

// ── helpers ──
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const seg = (t, a, b) => ease((t - a) / (b - a));
function show(names, on) { names.forEach(n => { if (P[n]) P[n].visible = on; }); }
function allTubes(f) { for (let i = 0; i < 6; i++) f(P['tube' + i], i); }
function ledColors(t, mode, k = 1) {
  const c = new THREE.Color();
  P.ledPts.forEach((p, i) => {
    if (mode === 'off') c.setRGB(0.05, 0.05, 0.05);
    else {
      const az = Math.atan2(p[0], -p[1]), el = Math.atan2(p[2], Math.hypot(p[0], p[1]));
      const h = (0.55 + 0.25 * Math.sin(az * 1.6 + t * 2.2) + 0.15 * el + t * 0.05) % 1;
      c.setHSL((h + 1) % 1, 1.0, 0.55 * k);
    }
    P.leds.setColorAt(i, c);
  });
  P.leds.instanceColor.needsUpdate = true;
}
function tubesGlow(k) { allTubes(g => { g.children[0].material.emissiveIntensity = 1.6 * k; }); }
function cam(az, el, dist, target = [0, 0, 60]) {
  const t = new THREE.Vector3(target[0], target[2], -target[1]);       // helmet coords → three
  camera.position.set(t.x + dist * Math.cos(el) * Math.sin(az), t.y + dist * Math.sin(el), t.z + dist * Math.cos(el) * Math.cos(az));
  camera.lookAt(t); camera.updateMatrixWorld(true);
}
function title(a, b, alpha) {
  const T = document.getElementById('title'), S = document.getElementById('sub');
  T.textContent = a; S.textContent = b; T.style.opacity = alpha; S.style.opacity = alpha;
}
function labels(list, alpha) {     // list: [text, [x,y,z] helmet coords]
  const box = document.getElementById('labels'); box.innerHTML = '';
  list.forEach(([txt, p]) => {
    const v = new THREE.Vector3(p[0], p[2], -p[1]).project(camera);
    const d = document.createElement('div'); d.className = 'lab'; d.textContent = txt;
    d.style.left = ((v.x + 1) / 2 * W) + 'px'; d.style.top = ((1 - v.y) / 2 * H) + 'px'; d.style.opacity = alpha;
    box.appendChild(d);
  });
}
function labelsObj(list, alpha) {   // list: [text, objectName, [dx,dy] px]
  scene.updateMatrixWorld(true);
  const box = document.getElementById('labels'); box.innerHTML = '';
  list.forEach(([txt, name, off]) => {
    const c = new THREE.Box3().setFromObject(P[name]).getCenter(new THREE.Vector3()).project(camera);
    const d = document.createElement('div'); d.className = 'lab'; d.textContent = txt;
    d.style.left = ((c.x + 1) / 2 * W + (off ? off[0] : 0)) + 'px'; d.style.top = ((1 - c.y) / 2 * H + (off ? off[1] : 0)) + 'px'; d.style.opacity = alpha;
    box.appendChild(d);
  });
}
function resetPose() {
  helmet.position.set(0, 0, 0); visorPivot.rotation.x = 0;
  for (const k in P) if (P[k] && P[k].position && k !== 'wall' && k !== 'leds') P[k].position.set(0, 0, 0);
  M.shell.opacity = 1; M.shell.depthWrite = true;
  labels([], 0); title('', '', 0);
}
const VIS_HELMET = ['shell', 'ear_L', 'ear_R', 'visor', 'pivot_cap', 'electronics_tray', 'hat_crown_plate', 'leds'];

window.renderFrame = function (sceneName, t) {
  resetPose();
  Object.keys(P).forEach(k => { if (P[k] && P[k].visible !== undefined) P[k].visible = false; });
  allTubes(g => g.visible = true);
  P.wall.visible = false;

  if (sceneName === 'turntable') {             // 10 s
    show(VIS_HELMET, true);
    ledColors(t, 'on'); tubesGlow(0.8);
    cam(-0.35 + t / 10 * Math.PI * 2, 0.18, 1380, [0, 0, 110]);
    title('mau5head', 'Parametric CAD · CadQuery · Prusa XL in PETG', clamp(1 - Math.abs(t - 1.8) / 1.8) * 1.0);
  }
  if (sceneName === 'exploded') {              // 13 s
    show(['shell_half_TOP', 'shell_half_BOTTOM', 'ear_L', 'ear_R', 'visor', 'pivot_cap', 'electronics_tray', 'hat_crown_plate', 'hardhat_envelope_REFERENCE'], true);
    ledColors(t, 'off'); tubesGlow(0.0);
    const e = seg(t, 1.2, 4.2) * (1 - seg(t, 10.0, 12.6));
    const v = (n, x, y, z) => P[n].position.set(x * e, y * e, z * e);
    v('shell_half_TOP', 0, 0, 140); v('shell_half_BOTTOM', 0, 0, -110);
    D.ears.forEach((ear, i) => { const u = ear.u; const n = i === 0 ? 'ear_L' : 'ear_R';
      P[n].position.set(u[0] * 210 * e, u[1] * 210 * e, u[2] * 210 * e + 40 * e); });
    allTubes((g, i) => { const u = D.ears[g.userData.ear].u; g.position.set(u[0] * 140 * e, u[1] * 140 * e, u[2] * 140 * e + 40 * e); });
    P.visor.position.set(0, -320 * e, -30 * e);
    P.pivot_cap.position.set(0, -320 * e, -30 * e);
    P.hat_crown_plate.position.set(0, 0, 330 * e);
    P.hardhat_envelope_REFERENCE.position.set(0, 0, -400 * e + 20);
    P.electronics_tray.position.set(260 * e, 200 * e, 40 * e);
    cam(-0.70 + 0.30 * Math.sin(t / 13 * Math.PI), 0.09, 2600, [0, 0, 20]);
    title('How it goes together', '2 shell halves · 2 ears (4 halves + 6 tubes) · internal visor · crown frame · hard hat', clamp(1 - Math.abs(t - 1.6) / 1.6));
    const la = clamp((t - 4.4) / 0.6) * (1 - clamp((t - 9.6) / 0.5));
    labelsObj([
      ['shell — top half', 'shell_half_TOP', [0, -70]], ['shell — bottom half', 'shell_half_BOTTOM', [-190, 10]],
      ['ear: 2 halves + 3 clear tubes', 'ear_R', [60, 125]], ['internal visor', 'visor', [0, 70]],
      ['crown frame', 'hat_crown_plate', [0, -28]], ['3M hard hat', 'hardhat_envelope_REFERENCE', [0, 0]], ['electronics tray', 'electronics_tray', [0, -32]],
    ], la);
  }
  if (sceneName === 'visor') {                 // 8 s
    show(VIS_HELMET, true); P.ear_L.visible = false; P.ear_R.visible = false; allTubes(g => g.visible = false);
    ledColors(t, 'on', 0.7);
    M.shell.opacity = 0.28; M.shell.depthWrite = false;
    const a = seg(t, 1.0, 3.2) * (1 - seg(t, 5.0, 7.2));
    visorPivot.rotation.x = -40 * Math.PI / 180 * a;
    P.pivot_cap.visible = true;
    cam(0.55, 0.10, 980, [0, -30, -5]);
    title('Internal flip-up visor', 'Pivots on Ø12 pins inside the shell · magnets hold it shut · 0–40°', clamp(1 - Math.abs(t - 1.4) / 1.4));
    labels([['Ø40 pivot pad + Ø56 hub', [176, 0, 0]], ['2.9 mm holes @ 3.8 mm · 55% open', [-60, -175, -20]]], clamp((t - 2.0) / 0.5) * (1 - clamp((t - 7.3) / 0.4)));
  }
  if (sceneName === 'wallmount') {             // 9 s
    show(['shell', 'ear_L', 'ear_R', 'visor', 'pivot_cap', 'hat_crown_plate', 'hardhat_envelope_REFERENCE', 'leds', 'wm_bracket', 'wm_cradle', 'wm_post', 'wm_dome'], true);
    P.wall.visible = true; ledColors(t, 'on', 0.8); tubesGlow(0.7);
    const drop = 1 - seg(t, 0.8, 4.0);
    helmet.position.set(0, 0, 320 * drop);
    P.wm_post.position.set(0, 0, -150);   // post bottom at the nominal (middle) pin hole
    M.shell.opacity = 1 - 0.65 * seg(t, 5.2, 6.4); M.shell.depthWrite = M.shell.opacity > 0.99;
    cam(-0.62 + 0.18 * (t / 9), 0.13, 1550, [0, 0, 0]);
    title('Wall mount', 'Felt pads cup the rim · a head-form dome holds it from the centre', clamp(1 - Math.abs(t - 1.5) / 1.5));
    labels([['4 felt pads on the rim', [170, -40, -150]], ['head-form dome (inside the hard hat)', [-140, -40, 40]], ['wall bracket', [0, 205, -260]]],
      clamp((t - 6.4) / 0.5));
  }
  renderer.render(scene, camera);
};
