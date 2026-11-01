// walkthrough.js -- the CAD walkthrough film. Every frame is a pure function of time, renderAt(t).
// Helmet frame throughout: origin at the sphere centre, +Z up, -Y the face, millimetres.
// Numbers on screen come from docs/cad-design.md, docs/build-guide.md, cad/README.md and scene.json.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const W = 1920, H = 1080, SS = 2, BAND = 130, FPS = 30;
const AMBER = 'rgb(222,170,90)', TEXT = 'rgb(232,235,238)', TEXT2 = 'rgb(178,185,192)', DIM = 'rgb(130,138,146)', RULE = 'rgb(44,50,57)', PANEL = 'rgb(17,20,24)';
const AMBER_L = new THREE.Color(0.73, 0.40, 0.10);

// ── renderer ──────────────────────────────────────────────────────────────────
const glc = document.getElementById('gl'), ovc = document.getElementById('ov');
const ov = ovc.getContext('2d');
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: false, preserveDrawingBuffer: true, stencil: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.NoToneMapping;
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.localClippingEnabled = false;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(24, W / H, 20, 60000);
camera.setViewOffset(W, H, 0, BAND / 2, W, H);      // centre the picture in what the caption band leaves

const rt = new THREE.WebGLRenderTarget(W * SS, H * SS, { samples: 4, type: THREE.HalfFloatType, stencilBuffer: true, depthBuffer: true });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1); composer.setSize(W * SS, H * SS);
composer.renderToScreen = false;
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W * SS / 2, H * SS / 2), 0.32, 0.7, 1.5);
composer.addPass(bloom);

// display transform: a per-channel filmic curve, then sRGB, then dither. Done per sample while going
// from 2x to 1x, so bright edges stay smooth, and the dither survives (it is added after the average).
const tm = x => (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14);
const srgbDec = c => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
function invTone(v8) {          // the linear value that lands on this 8-bit display value
  const target = srgbDec(v8 / 255); let a = 0, b = 4;
  for (let i = 0; i < 40; i++) { const m = (a + b) / 2; if (tm(m) < target) a = m; else b = m; }
  return (a + b) / 2;
}
const BG = [11, 13, 16];
const BG_L = new THREE.Vector3(...BG.map(invTone));
const BG_C = new THREE.Vector3(invTone(19), invTone(22), invTone(26));

const finalMat = new THREE.ShaderMaterial({
  uniforms: { t: { value: null }, uDip: { value: 0 }, uBg: { value: new THREE.Vector3(...BG.map(v => v / 255)) } },
  glslVersion: THREE.GLSL3,
  vertexShader: `void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }`,
  fragmentShader: `
    precision highp float; precision highp sampler2D;
    uniform sampler2D t; uniform float uDip; uniform vec3 uBg; out vec4 o;
    vec3 tm(vec3 x){ x = max(x, vec3(0.0)); return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14), 0.0, 1.0); }
    vec3 enc(vec3 c){ return mix(c*12.92, 1.055*pow(c, vec3(1.0/2.4))-0.055, step(0.0031308, c)); }
    float h(vec2 p){ vec3 q = fract(vec3(p.xyx)*0.1031); q += dot(q, q.yzx+33.33); return fract((q.x+q.y)*q.z); }
    void main(){
      ivec2 p = ivec2(gl_FragCoord.xy)*2;
      vec3 c = vec3(0.0);
      for (int j=0;j<2;j++) for (int i=0;i<2;i++) c += tm(texelFetch(t, p+ivec2(i,j), 0).rgb);
      c = enc(c*0.25);
      c = mix(c, uBg, uDip);
      float n = h(gl_FragCoord.xy) + h(gl_FragCoord.xy+17.3) - 1.0;
      o = vec4(c + n/255.0, 1.0);
    }`,
  depthTest: false, depthWrite: false,
});
const finalScene = new THREE.Scene();
const finalQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), finalMat); finalQuad.frustumCulled = false; finalScene.add(finalQuad);
const finalCam = new THREE.Camera();

// backdrop: dark, with a very soft pool behind the subject
const backMat = new THREE.ShaderMaterial({
  uniforms: { a: { value: BG_L }, b: { value: BG_C }, uC: { value: new THREE.Vector2(0.5, 0.56) } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.9999, 1.0); }`,
  fragmentShader: `uniform vec3 a,b; uniform vec2 uC; varying vec2 vUv;
    void main(){ vec2 d = (vUv-uC)*vec2(1.0, 0.62); float r = smoothstep(0.62, 0.0, length(d)); gl_FragColor = vec4(mix(a,b,r*r), 1.0); }`,
  depthTest: false, depthWrite: false,
});
const backQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), backMat);
backQuad.frustumCulled = false; backQuad.renderOrder = -1000; scene.add(backQuad);

// ── studio ────────────────────────────────────────────────────────────────────
function makeEnv() {
  const s = new THREE.Scene();
  s.background = new THREE.Color(0.012, 0.014, 0.018);
  const box = (w, h, x, y, z, i, col = [1, 1, 1]) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(col[0] * i, col[1] * i, col[2] * i), side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); s.add(m);
  };
  box(14, 8, 0, 11, 2, 3.2);                       // overhead
  box(3, 16, -13, 2, 6, 3.4, [1, 0.97, 0.93]);     // left strip
  box(2.2, 16, 14, 3, 3, 5.0, [0.92, 0.96, 1]);    // right strip
  box(14, 2, 2, 1, -14, 4.0, [0.9, 0.95, 1]);      // behind, for the rims
  box(10, 2, 0, -9, 7, 0.7, [1, 0.93, 0.85]);      // low front
  const p = new THREE.PMREMGenerator(renderer);
  const t = p.fromScene(s, 0.012).texture; p.dispose();
  return t;
}
scene.environment = makeEnv();

const world = new THREE.Group(); world.rotation.x = -Math.PI / 2; scene.add(world);
const h2w = (x, y, z) => new THREE.Vector3(x, z, -y);

const key = new THREE.DirectionalLight(0xfff4e6, 1.1);
key.position.copy(h2w(-620, -900, 1100)); key.target.position.set(0, 0, 0); scene.add(key, key.target);
key.castShadow = true; key.shadow.mapSize.set(4096, 4096); key.shadow.radius = 5; key.shadow.bias = -0.0006; key.shadow.normalBias = 0.8;
Object.assign(key.shadow.camera, { left: -1100, right: 1100, top: 1100, bottom: -1100, near: 100, far: 4000 });
const rimA = new THREE.DirectionalLight(0xbcd6ff, 1.2); rimA.position.copy(h2w(900, 800, 300)); scene.add(rimA);
const rimB = new THREE.DirectionalLight(0xffe0c0, 0.7); rimB.position.copy(h2w(-900, 700, -100)); scene.add(rimB);
const fill = new THREE.DirectionalLight(0xffffff, 0.3); fill.position.copy(h2w(300, -900, -300)); scene.add(fill);

// ── materials: premultiplied so a clear part keeps its reflections at full strength ──
function mat(kind) {
  const K = {
    shell: { color: 0xe6ebee, roughness: 0.38, a0: 0.10, a1: 0.62, glass: 1, env: 0.55 },
    ear: { color: 0xdbe7f2, roughness: 0.16, a0: 0.06, a1: 0.55, glass: 1, env: 0.6 },
    tube: { color: 0xe6f3ff, roughness: 0.05, a0: 0.05, a1: 0.8, glass: 1, env: 0.45 },
    hat: { color: 0xc99a58, roughness: 0.45, a0: 0.12, a1: 0.55, glass: 1 },
    black: { color: 0x1b1d21, roughness: 0.40, a0: 1, a1: 1 },
    mount: { color: 0x3a3f46, roughness: 0.46, a0: 1, a1: 1 },
    dome: { color: 0x565c65, roughness: 0.52, a0: 1, a1: 1 },
    magnet: { color: 0xd4d8dd, roughness: 0.22, metalness: 1, a0: 1, a1: 1 },
  }[kind];
  const m = new THREE.MeshPhysicalMaterial({ color: K.color, roughness: K.roughness, metalness: K.metalness || 0, side: THREE.DoubleSide, envMapIntensity: K.env || 1.0, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
  m.premultipliedAlpha = true; m.transparent = !!K.glass; m.depthWrite = !K.glass;
  m.userData = { glass: !!K.glass, u: { uA0: { value: K.a0 }, uA1: { value: K.a1 }, uFade: { value: 1 }, uHL: { value: 0 }, uAmb: { value: AMBER_L } } };
  m.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, m.userData.u);
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uA0,uA1,uFade,uHL; uniform vec3 uAmb;')
      .replace('#include <opaque_fragment>', `
        float nv_ = saturate(dot(normalize(vViewPosition), normal));
        float fr_ = pow(1.0-nv_, 2.6);
        float a_ = mix(uA0, uA1, fr_)*uFade;
        vec3 hl_ = uAmb*uHL*(0.35+fr_*2.2);
        a_ = clamp(a_ + uHL*0.10*uFade, 0.0, 1.0);
        gl_FragColor = vec4(totalDiffuse*a_ + (totalSpecular + totalEmissiveRadiance)*uFade + hl_*uFade, a_);`)
      .replace('#include <premultiplied_alpha_fragment>', '');
  };
  m.customProgramCacheKey = () => 'mau5' + (K.glass ? 'g' : 'o');
  return m;
}

// ── parts ─────────────────────────────────────────────────────────────────────
const P = {};       // name -> part
let D, MF;
const geoCache = {}, edgeCache = {};
async function loadGeo(name) {
  const buf = await (await fetch(`build/mesh/${name}.bin`)).arrayBuffer();
  const m = MF[name]; let o = 0;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o, m.nv * 3), 3)); o += m.nv * 12;
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o, m.nv * 3), 3)); o += m.nv * 12;
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, o, m.nf * 3), 1)); o += m.nf * 12;
  geoCache[name] = g;
  if (m.ne) { const e = new THREE.BufferGeometry(); e.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o, m.ne * 3), 3)); edgeCache[name] = e; }
}
const edgeMatBase = () => new THREE.LineBasicMaterial({ color: 0xd8dde2, transparent: true, opacity: 0, depthWrite: false });
function addPart(name, geo, kind, matrix, opts = {}) {
  const parent = opts.parent || world;
  const off = new THREE.Group(); parent.add(off);            // the part's offset, in the helmet frame
  const m = mat(kind);
  const mesh = new THREE.Mesh(geoCache[geo], m);
  mesh.matrixAutoUpdate = false;
  if (matrix) mesh.matrix.copy(matrix);
  mesh.castShadow = !m.userData.glass; mesh.receiveShadow = !m.userData.glass;
  off.add(mesh);
  const part = { name, off, mesh, m, kind, group: opts.group || kind, fade: 1, hl: 0, edge: 0, geo };
  if (edgeCache[geo] && !opts.noEdges) {
    const em = edgeMatBase();
    const l = new THREE.LineSegments(edgeCache[geo], em); l.matrixAutoUpdate = false; if (matrix) l.matrix.copy(matrix);
    off.add(l); part.lines = l;
  }
  // centre, in the helmet frame, assembled
  const mf = MF[geo];
  const c = new THREE.Vector3((mf.min[0] + mf.max[0]) / 2, (mf.min[1] + mf.max[1]) / 2, (mf.min[2] + mf.max[2]) / 2);
  if (matrix) c.applyMatrix4(matrix);
  part.c = c;
  P[name] = part;
  return part;
}
const fromArr = a => new THREE.Matrix4().fromArray(a);
const translate = (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z);

// section caps, by the stencil method: back faces count up, front faces count down, the cap draws where it isn't zero
const CAP_COL = { shell: 0xa9b0b6, ear: 0x3a4650, tube: 0x7aa6c6, black: 0x62666d, hat: 0x7d6236, dome: 0x3f444b, mount: 0x565b63, magnet: 0xa8acb1 };
const capGroups = ['black', 'tube', 'ear', 'hat', 'dome', 'mount', 'shell', 'magnet'];
const clip = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);
const caps = {}, stencilMeshes = [];
function buildSections() {
  const sm = (side, op) => new THREE.MeshBasicMaterial({ side, colorWrite: false, depthWrite: false, depthTest: false, stencilWrite: true, stencilFunc: THREE.AlwaysStencilFunc, stencilFail: op, stencilZFail: op, stencilZPass: op });
  const back = sm(THREE.BackSide, THREE.IncrementWrapStencilOp), front = sm(THREE.FrontSide, THREE.DecrementWrapStencilOp);
  Object.values(P).forEach(p => {
    if (p.nosection) return;
    const ro = 10 + capGroups.indexOf(p.group) * 10;
    for (const mt of [back, front]) {
      const s = new THREE.Mesh(p.mesh.geometry, mt); s.matrixAutoUpdate = false; s.matrix.copy(p.mesh.matrix); s.renderOrder = ro; s.frustumCulled = false; s.visible = false;
      p.mesh.parent.add(s); stencilMeshes.push([s, p]);
    }
  });
  capGroups.forEach(g => {
    const m = new THREE.MeshBasicMaterial({ color: CAP_COL[g], stencilWrite: true, stencilRef: 0, stencilFunc: THREE.NotEqualStencilFunc, stencilFail: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp, stencilZPass: THREE.ReplaceStencilOp, side: THREE.DoubleSide });
    const q = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), m); q.renderOrder = 11 + capGroups.indexOf(g) * 10; q.visible = false; q.frustumCulled = false;
    q.matrixAutoUpdate = true; scene.add(q); caps[g] = q;
  });
}
function setSection(on, nh, constant) {       // nh: normal in the helmet frame; points kept where n.p + constant > 0
  if (on) {
    const nw = h2w(nh[0], nh[1], nh[2]);
    clip.normal.copy(nw); clip.constant = constant;
    renderer.clippingPlanes = [clip];
    Object.values(caps).forEach(q => {
      q.visible = true; const pt = nw.clone().multiplyScalar(-constant + 0.01); q.position.copy(pt); q.lookAt(pt.clone().add(nw));
    });
  } else { renderer.clippingPlanes = []; Object.values(caps).forEach(q => q.visible = false); }
  stencilMeshes.forEach(([s, p]) => { s.visible = on && p.fade > 0.02 && !p.nocap; });
}

// ── LEDs ──────────────────────────────────────────────────────────────────────
const uLed = { value: 0 }, uWin = { value: 0 }, uUnused = { value: 1 };
let ledInst, ledCol, ledPos = [], winInst, tubeGlow = [], rimPts, rimCol, rimPos = [];
function buildLeds() {
  const quadVS = `attribute vec3 iCol; attribute float iSize; varying vec3 vC; varying vec2 vP; varying float vS;
    void main(){ vC = iCol; vS = iSize; vP = position.xy*36.0; gl_Position = projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position.xy*36.0, 0.0, 1.0); }`;
  const shell = D.leds.filter(l => l[3] === 'shell');
  const geo = new THREE.PlaneGeometry(1, 1);
  const mt = new THREE.ShaderMaterial({
    uniforms: { uLed }, vertexShader: quadVS,
    fragmentShader: `uniform float uLed; varying vec3 vC; varying vec2 vP; varying float vS;
      void main(){ vec2 d = abs(vP)-vec2(vS*0.5-0.9); float s = 1.0-smoothstep(-0.9, 0.9, max(d.x,d.y));
        float h = exp(-dot(vP,vP)/70.0); float b = gl_FrontFacing ? 1.0 : 0.32;
        gl_FragColor = vec4(vC*(s*1.0+h*0.16)*uLed*b, 1.0); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
  });
  ledInst = new THREE.InstancedMesh(geo, mt, shell.length);
  ledCol = new THREE.InstancedBufferAttribute(new Float32Array(shell.length * 3), 3);
  const sizes = new THREE.InstancedBufferAttribute(new Float32Array(shell.length), 1);
  const dummy = new THREE.Object3D(), z = new THREE.Vector3(0, 0, 1);
  shell.forEach((l, i) => {
    const n = new THREE.Vector3(l[0], l[1], l[2]).normalize();
    dummy.position.copy(n.clone().multiplyScalar(D.R_O + 0.25)); dummy.quaternion.setFromUnitVectors(z, n); dummy.updateMatrix(); ledInst.setMatrixAt(i, dummy.matrix);
    sizes.setX(i, Math.asin(n.z) * 57.3 <= 45 ? D.params.PIX : D.params.PIX_HI);
    ledPos.push(n.clone().multiplyScalar(D.R_O));
  });
  geo.setAttribute('iCol', ledCol); geo.setAttribute('iSize', sizes);
  ledInst.frustumCulled = false; ledInst.renderOrder = 900; world.add(ledInst);

  // all 948 windows, as a pale overlay; iUsed says whether the map has an LED there
  const g2 = new THREE.PlaneGeometry(1, 1);
  const wm = new THREE.ShaderMaterial({
    uniforms: { uWin, uUnused }, vertexShader: `attribute float iUsed; attribute float iSize; varying float vU; varying vec2 vP; varying float vS;
      void main(){ vU = iUsed; vS = iSize; vP = position.xy*16.0; gl_Position = projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position.xy*16.0, 0.0, 1.0); }`,
    fragmentShader: `uniform float uWin,uUnused; varying float vU; varying vec2 vP; varying float vS;
      void main(){ vec2 d = abs(vP)-vec2(vS*0.5-0.5); float s = 1.0-smoothstep(-0.5, 0.5, max(d.x,d.y)); float b = gl_FrontFacing ? 1.0 : 0.22;
        float k = mix(uUnused, 1.0, vU); gl_FragColor = vec4(vec3(1.05,0.62,0.22)*s*uWin*k*b, 1.0); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
  });
  winInst = new THREE.InstancedMesh(g2, wm, D.windows.length);
  const used = new THREE.InstancedBufferAttribute(new Float32Array(D.windows.length), 1), wsz = new THREE.InstancedBufferAttribute(new Float32Array(D.windows.length), 1);
  let nUsed = 0;
  D.windows.forEach((w, i) => {
    const n = new THREE.Vector3(w[0], w[1], w[2]).normalize();
    dummy.position.copy(n.clone().multiplyScalar(D.R_O + 0.3)); dummy.quaternion.setFromUnitVectors(z, n); dummy.updateMatrix(); winInst.setMatrixAt(i, dummy.matrix);
    wsz.setX(i, w[3]);
    const u = shell.some(l => { const r = Math.hypot(l[0], l[1], l[2]); return (l[0] * n.x + l[1] * n.y + l[2] * n.z) / r > 0.99985; }); used.setX(i, u ? 1 : 0); if (u) nUsed++;
  });
  window.__windowsMatched = nUsed;
  g2.setAttribute('iUsed', used); g2.setAttribute('iSize', wsz);
  winInst.frustumCulled = false; winInst.renderOrder = 901; world.add(winInst);

  // rim LEDs: sharp points
  const rim = D.leds.filter(l => l[3].endsWith('_rim'));
  const pg = new THREE.BufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(rim.flatMap(l => [l[0], l[1], l[2]])), 3));
  rimCol = new THREE.BufferAttribute(new Float32Array(rim.length * 3), 3); pg.setAttribute('color', rimCol);
  rim.forEach(l => rimPos.push(new THREE.Vector3(l[0], l[1], l[2])));
  const pm = new THREE.ShaderMaterial({
    uniforms: { uLed }, vertexShader: `attribute vec3 color; varying vec3 vC; void main(){ vC = color; vec4 mv = modelViewMatrix*vec4(position,1.0); gl_Position = projectionMatrix*mv; gl_PointSize = 120.0*2160.0/(-mv.z)/4.0; }`,
    fragmentShader: `uniform float uLed; varying vec3 vC; void main(){ vec2 d = gl_PointCoord-0.5; float r = length(d)*2.0; float s = exp(-r*r*9.0)+0.9*exp(-r*r*90.0); gl_FragColor = vec4(vC*s*uLed*1.6, 1.0); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  rimPts = new THREE.Points(pg, pm); rimPts.frustumCulled = false; rimPts.renderOrder = 902; world.add(rimPts);
}
// the blades: two back-to-back strips and diffusion film inside each tube, so a soft bar of light
function addTubeGlow(tubeName, L) {
  const g = new THREE.CylinderGeometry(9.0, 9.0, L, 24, 40, true);
  g.rotateX(Math.PI / 2); g.translate(0, 0, L / 2);
  const col = new THREE.BufferAttribute(new Float32Array(g.attributes.position.count * 3), 3); g.setAttribute('color', col);
  const m = new THREE.ShaderMaterial({
    uniforms: { uLed }, vertexShader: `attribute vec3 color; varying vec3 vC; varying vec3 vN; varying vec3 vV; void main(){ vC = color; vec4 mv = modelViewMatrix*vec4(position,1.0); vV = normalize(-mv.xyz); vN = normalize(normalMatrix*normal); gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform float uLed; varying vec3 vC; varying vec3 vN; varying vec3 vV; void main(){ float k = abs(dot(normalize(vN), normalize(vV))); gl_FragColor = vec4(vC*uLed*(0.35+0.75*k), 1.0); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(g, m); mesh.matrixAutoUpdate = false; mesh.matrix.copy(P[tubeName].mesh.matrix); mesh.frustumCulled = false; mesh.renderOrder = 880;
  P[tubeName].off.add(mesh);
  mesh.updateMatrixWorld(true);
  const pos = g.attributes.position, wp = [];
  for (let i = 0; i < pos.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(mesh.matrix); wp.push(v); }
  tubeGlow.push({ col, wp, mesh });
}
const tmpC = new THREE.Color();
function ledColor(p, t, out) {
  const az = Math.atan2(p.x, -p.y), el = Math.atan2(p.z, Math.hypot(p.x, p.y));
  let h = 0.60 + 0.17 * Math.sin(az * 1.15 + t * 0.85) + 0.14 * Math.sin(el * 2.1 - t * 0.6) + 0.06 * Math.sin(p.x * 0.012 + p.z * 0.011 + t * 1.3);
  h = ((h % 1) + 1) % 1;
  tmpC.setHSL(h, 1.0, 0.5);
  out[0] = tmpC.r; out[1] = tmpC.g; out[2] = tmpC.b;
}
function updateLeds(t, gain = 1.9) {
  const o = [0, 0, 0];
  ledPos.forEach((p, i) => { ledColor(p, t, o); ledCol.setXYZ(i, o[0] * gain, o[1] * gain, o[2] * gain); }); ledCol.needsUpdate = true;
  rimPos.forEach((p, i) => { ledColor(p, t, o); rimCol.setXYZ(i, o[0] * 1.8 + 0.25, o[1] * 1.8 + 0.25, o[2] * 1.8 + 0.25); }); rimCol.needsUpdate = true;
  tubeGlow.forEach(g => { g.wp.forEach((p, i) => { ledColor(p, t, o); g.col.setXYZ(i, o[0] * 1.5, o[1] * 1.5, o[2] * 1.5); }); g.col.needsUpdate = true; });
}

// ── helpers ───────────────────────────────────────────────────────────────────
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ss = x => { x = clamp(x); return clamp(x * x * x * (x * (x * 6 - 15) + 10)); };     // smootherstep. Clamped: canvas ignores a negative globalAlpha, even -1e-16, and a one-frame flash follows
const S = (t, a, b) => ss((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const rad = d => d * Math.PI / 180;

// camera path through keys [t, az°, el°, dist, tx, ty, tz]: a cubic through every key, still at the ends
function camAt(keys, t) {
  const n = keys.length;
  if (t <= keys[0][0]) return keys[0].slice(1);
  if (t >= keys[n - 1][0]) return keys[n - 1].slice(1);
  let i = 0; while (t > keys[i + 1][0]) i++;
  const k0 = keys[i], k1 = keys[i + 1], dt = k1[0] - k0[0], u = (t - k0[0]) / dt;
  const tan = (j, c) => (j <= 0 || j >= n - 1) ? 0 : (keys[j + 1][c] - keys[j - 1][c]) / (keys[j + 1][0] - keys[j - 1][0]);
  const out = [];
  for (let c = 1; c < 7; c++) {
    const m0 = tan(i, c) * dt, m1 = tan(i + 1, c) * dt, u2 = u * u, u3 = u2 * u;
    out.push((2 * u3 - 3 * u2 + 1) * k0[c] + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * k1[c] + (u3 - u2) * m1);
  }
  return out;
}
function setCam(c) {
  const [az, el, d, x, y, z] = c, a = rad(az), e = rad(el);
  const pos = h2w(x + d * Math.sin(a) * Math.cos(e), y - d * Math.cos(a) * Math.cos(e), z + d * Math.sin(e));
  camera.position.copy(pos); camera.lookAt(h2w(x, y, z)); camera.updateMatrixWorld(true); camera.updateProjectionMatrix();
}
const project = p => { const v = h2w(p[0], p[1], p[2]).project(camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; };
const hide = names => names.forEach(n => { P[n].fade = 0; });
const fade = (names, f) => names.forEach(n => { P[n].fade = f; });
const off = (n, x, y, z) => P[n].off.position.set(x, y, z);
function at(name, local) {                 // a point on a part, as it stands now, in the helmet frame
  const p = P[name], o = p.off.position;
  const c = local ? new THREE.Vector3(...local).applyMatrix4(p.mesh.matrix) : p.c;
  let x = c.x + o.x, y = c.y + o.y, z = c.z + o.z;
  if (p.off.parent !== world) { const q = visorOff.position; x += q.x; y += q.y; z += q.z; }
  return [x, y, z];
}

// groups of part names
const EARS = ['earTop0', 'earBot0', 'earTop1', 'earBot1'];
const TUBES = [0, 1, 2, 3, 4, 5].map(i => 'tube' + i);
const THICK = ['earTopT0', 'earBotT0', 'earTopT1', 'earBotT1'];
const PLATES = [0, 1, 2, 3, 4, 5].map(i => 'plate' + i);
const CAPS = ['cap0', 'cap1'];
const MAG_S = [0, 1, 2, 3].map(i => 'magS' + i);
const MAG_V = [0, 1].map(i => 'magV' + i);
const WALL = ['wm_bracket', 'wm_cradle', 'wm_post', 'wm_dome'];
let SPACERS = [];
const INNER = () => ['crown', ...SPACERS, 'hat', 'tray'];

// ── the assembled pose: everything visible at its true place ──
let visorG, visorOff;
function resetPose() {
  Object.values(P).forEach(p => { p.fade = 1; p.hl = 0; p.edge = 0; p.off.position.set(0, 0, 0); });
  hide(THICK); hide(WALL); hide(['hat']);
  visorG.rotation.x = 0; visorOff.position.set(0, 0, 0);
  uLed.value = 0; uWin.value = 0; uUnused.value = 1;
    labelQueue.length = 0; dimQueue.length = 0; wallLine.a = 0;
  key.intensity = 1.1;
  backMat.uniforms.uC.value.set(0.5, 0.56);
  setSection(false);
}
function commit(t) {
  Object.values(P).forEach(p => {
    const f = clamp(p.fade), v = f > 0.001;
    p.mesh.visible = v; p.m.userData.u.uFade.value = f; p.m.userData.u.uHL.value = p.hl;
    const glass = p.m.userData.glass;
    p.m.transparent = glass || f < 0.999; p.m.depthWrite = !glass && f >= 0.999;
    p.mesh.castShadow = !glass && f > 0.9;
    if (p.lines) { p.lines.visible = v && p.edge > 0.001; p.lines.material.opacity = p.edge * f; }
  });
  bloom.strength = lerp(0.09, 0.32, Math.max(uLed.value, Math.min(1, uWin.value * 1.3)));
  ledInst.visible = uLed.value > 0.001; rimPts.visible = ledInst.visible; winInst.visible = uWin.value > 0.001;
  tubeGlow.forEach(g => g.mesh.visible = ledInst.visible);
  // back to front among the clear parts, by centre
  const cam = camera.position, v = new THREE.Vector3();
  Object.values(P).filter(p => p.m.userData.glass || p.fade < 0.999).forEach(p => {
    const a = at(p.name); v.copy(h2w(a[0], a[1], a[2]));
    p.mesh.renderOrder = 500 - v.distanceTo(cam) * 0.05 + (p.group === 'shell' ? 40 : 0);
  });
}

// ── overlay ───────────────────────────────────────────────────────────────────
const labelQueue = [], dimQueue = [], wallLine = { a: 0 };
// text, count ("×6" or ""), anchor (helmet point), label position (px, text baseline-left or right), side 'l'|'r'
function label(text, count, anchor, x, y, side, a = 1) { labelQueue.push({ text, count, anchor, x, y, side, a }); }
const F_LABEL = '500 25px "Avenir Next"', F_COUNT = 'bold 31px "DIN Condensed"', F_CAP = '33px "Avenir Next"', F_HEAD = 'bold 74px "DIN Condensed"', F_STAT = 'bold 92px "DIN Condensed"', F_UNIT = '26px "Avenir Next"', F_CODE = '21px Menlo';
window.__problems = [];
function drawLabels(tAbs) {
  const rects = [];
  labelQueue.forEach(l => {
    if (l.a <= 0.001) return;
    ov.save(); ov.globalAlpha = l.a;
    ov.font = F_LABEL; const tw = ov.measureText(l.text).width;
    ov.font = F_COUNT; const cw = l.count ? ov.measureText(l.count).width + 12 : 0;
    const total = tw + cw;
    const left = l.side === 'r' ? l.x : l.x - total, right = left + total;
    const lineY = l.y - 8;
    const [ax, ay] = project(l.anchor);
    // leader: anchor, then straight to a short horizontal stub at the text
    const sx = l.side === 'r' ? left - 12 : right + 12, ex = l.side === 'r' ? sx - 26 : sx + 26;
    ov.strokeStyle = 'rgba(222,170,90,0.85)'; ov.lineWidth = 1.25;
    ov.beginPath(); ov.moveTo(sx, lineY); ov.lineTo(ex, lineY); ov.lineTo(ax, ay); ov.stroke();
    ov.fillStyle = AMBER; ov.beginPath(); ov.arc(ax, ay, 3.2, 0, 7); ov.fill();
    ov.font = F_LABEL; ov.fillStyle = TEXT; ov.textBaseline = 'alphabetic';
    // a soft dark plate under the text, so it reads over anything
    ov.shadowColor = 'rgba(11,13,16,0.95)'; ov.shadowBlur = 8;
    ov.fillText(l.text, left, l.y); ov.fillText(l.text, left, l.y);
    ov.font = F_COUNT; ov.fillStyle = AMBER;
    if (l.count) ov.fillText(l.count, left + tw + 12, l.y + 1);
    ov.restore();
    rects.push({ t: l.text, x0: left, x1: right, y0: l.y - 24, y1: l.y + 8, a: [ax, ay], b: [ex, lineY] });
  });
  // record anything that breaks the rules; film.py prints these
  const Hmax = H - BAND;
  rects.forEach((r, i) => {
    if (r.x0 < 12 || r.x1 > W - 12 || r.y0 < 8 || r.y1 > Hmax - 4) window.__problems.push([tAbs, 'off screen', r.t]);
    if (r.a[0] < 0 || r.a[0] > W || r.a[1] < 0 || r.a[1] > Hmax) window.__problems.push([tAbs, 'anchor off screen', r.t]);
    for (let j = i + 1; j < rects.length; j++) {
      const q = rects[j];
      if (r.x0 < q.x1 + 6 && q.x0 < r.x1 + 6 && r.y0 < q.y1 && q.y0 < r.y1) window.__problems.push([tAbs, 'labels overlap', r.t, q.t]);
      if (cross(r.a, r.b, q.a, q.b)) window.__problems.push([tAbs, 'leaders cross', r.t, q.t]);
    }
  });
}
function drawDims() {
  if (wallLine.a > 0.001) {     // the wall, end on
    const [x0, y0] = project([0, D.wall_y, 620]), [x1, y1] = project([0, D.wall_y, -480]);
    ov.save(); ov.globalAlpha = wallLine.a; ov.strokeStyle = TEXT2; ov.lineWidth = 1.5; ov.beginPath(); ov.moveTo(x0, y0); ov.lineTo(x1, Math.min(y1, H - BAND)); ov.stroke();
    ov.globalAlpha = wallLine.a * 2; ov.font = F_LABEL; ov.fillStyle = TEXT2; ov.textAlign = 'right'; ov.fillText('Wall', x0 - 12, Math.max(y0, 0) + 150); ov.restore();
  }
  dimQueue.forEach(d => {
    if (d.alpha <= 0.001) return;
    const [x0, y0] = project(d.a), [x1, y1] = project(d.b);
    ov.save(); ov.globalAlpha = d.alpha; ov.strokeStyle = AMBER; ov.lineWidth = 1.5;
    ov.beginPath(); ov.moveTo(x0, y0 - 16); ov.lineTo(x0, y0 + 16); ov.moveTo(x1, y1 - 16); ov.lineTo(x1, y1 + 16); ov.moveTo(x0, y0); ov.lineTo(x1, y1); ov.stroke();
    ov.font = F_COUNT; ov.fillStyle = AMBER; ov.textBaseline = 'alphabetic'; ov.textAlign = 'center';
    ov.shadowColor = 'rgba(11,13,16,0.95)'; ov.shadowBlur = 8;
    ov.fillText(d.text, (x0 + x1) / 2, Math.min(y0, y1) - 26);
    ov.restore();
  });
}
function cross(a, b, c, d) {
  const o = (p, q, r) => (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
  return o(a, b, c) * o(a, b, d) < 0 && o(c, d, a) * o(c, d, b) < 0;
}
function drawBand() {
  ov.fillStyle = PANEL; ov.fillRect(0, H - BAND, W, BAND);
  ov.fillStyle = RULE; ov.fillRect(0, H - BAND, W, 1);
}
function wrap(text, font, max) {
  ov.font = font; const out = []; let line = '';
  text.split(' ').forEach(w => { const t = line ? line + ' ' + w : w; if (ov.measureText(t).width > max && line) { out.push(line); line = w; } else line = t; });
  if (line) out.push(line); return out;
}
function drawCaption(text, a) {
  if (!text || a <= 0) return;
  const lines = wrap(text, F_CAP, W - 96);
  ov.save(); ov.globalAlpha = a; ov.font = F_CAP; ov.fillStyle = TEXT; ov.textBaseline = 'middle';
  const lh = 44, y0 = H - BAND / 2 - (lines.length - 1) * lh / 2;
  lines.forEach((l, i) => ov.fillText(l, 48, y0 + i * lh));
  ov.restore();
  if (lines.length > 2) window.__problems.push([0, 'caption over two lines', text]);
}
function drawHead(text, a) {
  if (a <= 0) return;
  ov.save(); ov.globalAlpha = a; ov.textBaseline = 'alphabetic';
  const g = ov.createRadialGradient(150, 110, 10, 150, 110, 340); g.addColorStop(0, 'rgba(11,13,16,0.72)'); g.addColorStop(1, 'rgba(11,13,16,0)');
  ov.fillStyle = g; ov.fillRect(0, 0, 500, 460);
  ov.font = F_HEAD; ov.fillStyle = TEXT; ov.fillText(text, 48, 92);
  ov.restore();
}

// ── the film ──────────────────────────────────────────────────────────────────
// Each chapter: dur (s), head, captions [[from, to, text]], stats [[from, to, stat, unit]], f(t) poses the scene.
// ch 2's code panel: the real lines, read from the generator
function srcLine(prefix) { return D.source_lines.find(l => l.startsWith(prefix)).replace(/\s+#.*$/, ''); }

const CH = [];
const S_ = { pktLat: 0 };
function chapter(c) { CH.push(c); }

// 1. the whole helmet
chapter({
  id: 'helmet', dur: 8, head: 'The helmet',
  caps: [[0.5, 7.7, 'My helmet as CAD: a 354 mm sphere and two big ears. The LEDs are lit where they really are, 621 of them.']],
  stats: [[1.0, 7.5, '621', 'LEDs on the real helmet']],
  f(t) {
    uLed.value = 1; updateLeds(t + 2);
    setCam(camAt([[0, -52, 7, 1720, 0, 0, 118], [4, -8, 10, 1640, 0, 0, 118], [8, 42, 13, 1610, 0, 0, 118]], t));
  },
});

// 2. the CAD is code
chapter({
  id: 'code', dur: 13, head: 'The CAD is code',
  caps: [[0.4, 6.4, 'Nothing was drawn by hand. One Python file builds every part from about 150 named numbers.'],
         [6.5, 12.7, 'To thicken the ears I change one number and rerun it. About 90 seconds, every part rebuilt.']],
  f(t) {
    const k = S(t, 8.3, 9.4) * (1 - S(t, 11.2, 12.1));
    Object.values(P).forEach(p => { p.edge = 0.3; });
    EARS.forEach(n => P[n].fade = 1 - k);
    THICK.forEach(n => { P[n].fade = k; P[n].edge = 0.3; });
    setCam(camAt([[0, 56, 18, 2480, -360, 0, 104], [13, 66, 24, 2380, -360, 0, 104]], t));
    const la = S(t, 7.3, 7.8) * (1 - S(t, 11.8, 12.3));
    const e = D.ears[1], z = D.ear_zc + 60, O = [e.S[0] - 32 * e.u[0], e.S[1] - 32 * e.u[1], e.S[2] - 32 * e.u[2]];
    const half = lerp(30, 45, k);
    label(k > 0.5 ? 'Ear, 90 mm thick' : 'Ear, 60 mm thick', '', [O[0] + e.u[0] * z - e.n[0] * half, O[1] + e.u[1] * z - e.n[1] * half, O[2] + e.u[2] * z - e.n[2] * half], 1040, 180, 'r', la);
  },
  overlay(t) {
    const a = S(t, 0.5, 1.1) * (1 - S(t, 12.2, 12.7));
    ov.save(); ov.globalAlpha = a;
    const X = 48, Y = 140, Wd = 800;
    ov.fillStyle = 'rgba(17,20,24,0.92)'; ov.fillRect(X, Y, Wd, 512); ov.strokeStyle = RULE; ov.lineWidth = 1; ov.strokeRect(X + .5, Y + .5, Wd - 1, 511);
    ov.font = '20px "Avenir Next"'; ov.fillStyle = DIM; ov.fillText('cad/source/mau5head_hat.py', X + 22, Y + 34);
    const src = [srcLine('R_O '), srcLine('WALL '), srcLine('LEDS_PER_M'), srcLine('PIX, SKIN'), srcLine('VISOR_R'), srcLine('OPEN_ANGLE'), srcLine('EAR_W, EAR_H'), srcLine('EAR_T, EAR_RIM_T'), srcLine('DOWEL_D'), srcLine('TENON_W, TENON_T, TENON_D, TENON_CLR'), srcLine('SEAM_PADS')];
    ov.font = F_CODE;
    src.forEach((l, i) => {
      const y = Y + 76 + i * 33;
      if (l.startsWith('EAR_T')) {
        const h = S(t, 6.5, 6.9);
        ov.fillStyle = `rgba(222,170,90,${0.16 * h})`; ov.fillRect(X + 10, y - 22, Wd - 20, 31);
        ov.fillStyle = h > 0.5 ? AMBER : TEXT2;
        ov.fillText(t > 7.1 && t < 11.8 ? l.replace('60.0', '90.0') : l, X + 22, y);
      } else { ov.fillStyle = TEXT2; ov.fillText(l, X + 22, y); }
    });
    // the rerun, with the line the generator really printed for that run
    ov.globalAlpha = a * S(t, 7.4, 7.7) * (1 - S(t, 11.5, 11.9));
    ov.fillStyle = TEXT; ov.fillText('$ python3 mau5head_hat.py', X + 22, Y + 462);
    ov.globalAlpha = a * S(t, 8.2, 8.5) * (1 - S(t, 11.5, 11.9));
    ov.fillStyle = AMBER; ov.fillText('[  75.8s] DONE  pixels=948  channels=68', X + 22, Y + 494);
    ov.restore();
  },
});

// 3. shell
chapter({
  id: 'shell', dur: 14, cuts: [9.3], head: 'The shell',
  caps: [[0.4, 4.9, 'Two halves, split just below the equator so each fits the Prusa XL.'],
         [5.0, 9.2, 'The CAD has 948 LED windows, and I only use the front ones.'],
         [9.3, 13.7, 'Each pocket leaves 2 mm of skin, so the plastic glows evenly.']],
  stats: [[5.2, 7.1, '948', 'LED windows in the CAD'], [7.3, 9.0, '398', 'of them used on the shell']],
  f(t) {
    hide([...EARS, ...TUBES, 'visor', ...MAG_V, ...CAPS, ...PLATES, 'crown', ...SPACERS, 'tray', 'hat']);
    const open = S(t, 0.6, 2.2) * (1 - S(t, 3.9, 5.0));
    off('shellT', 0, 0, 62 * open); off('shellB', 0, 0, -62 * open);
    MAG_S.forEach(n => off(n, 0, 0, 62 * open));
    uWin.value = 0.8 * S(t, 5.0, 5.8) * (1 - S(t, 9.0, 9.4));
    uUnused.value = 1 - S(t, 6.8, 7.6);
    const cutTime = t > 9.3;
    if (cutTime) {
      const az = (D.params.N_CH * 0.75 + 3 + 0.5) * 360 / D.params.N_CH;       // one channel, a little off the front centre
      const a = rad(az), e = [-Math.sin(a), Math.cos(a), 0];
      setSection(true, e, 0);
      fade(['shellT', 'shellB'], 0.16); fade(MAG_S, 0);
      const lat = rad(S_.pktLat + 2.75), r = D.R_O - 6;
      const c = [Math.cos(lat) * Math.cos(a) * r, Math.cos(lat) * Math.sin(a) * r, Math.sin(lat) * r];
      const camAz = Math.atan2(-e[0], e[1]) * 57.3;
      setCam(camAt([[9.3, camAz - 14, 6, 112, c[0], c[1], c[2]], [14, camAz - 4, 1, 84, c[0], c[1], c[2]]], t));
      const la2 = S(t, 9.9, 10.5);
      const pt = (rr, dl) => { const l = rad(S_.pktLat + dl); return [Math.cos(l) * Math.cos(a) * rr, Math.cos(l) * Math.sin(a) * rr, Math.sin(l) * rr]; };
      label('2 mm skin', '', pt(D.R_O - 1, 0), 1430, 190, 'r', la2);
      label('Pocket for the LED, 9 mm square', '', pt(D.R_O - 3.2, 0), 1330, 690, 'r', la2);
      label('1 mm groove the strip lies in', '', pt(D.R_I + 0.5, 5.51 / 2), 660, 300, 'l', la2);
      label('5 mm wall', '', pt(D.R_O - 3.0, 5.51 / 2), 660, 660, 'l', la2);
    } else {
      setCam(camAt([[0, -46, 10, 1400, 0, 0, 12], [5, -14, 6, 1300, 0, 0, 12], [9.3, 66, 8, 1160, 0, 0, 12]], t));
    }
    const la = S(t, 1.8, 2.4) * (1 - S(t, 3.9, 4.4));
    if (la > 0) {
      label('Top half', '', at('shellT', [104, -104, 96]), 1480, 230, 'r', la);
      label('Bottom half', '', at('shellB', [110, -110, -80]), 1480, 760, 'r', la);
    }
  },
});

// 4. ears
function earOffset(i, d) { const u = D.ears[i].u; return [u[0] * d, u[1] * d, u[2] * d]; }
function placeEar(i, peg, tube, top) {  // peg: whole ear along u; tube, top: further along u
  const [a, b, c] = earOffset(i, peg), [p, q, r] = earOffset(i, tube), [x, y, z] = earOffset(i, top);
  off('earBot' + i, a, b, c); off('earTop' + i, a + x, b + y, c + z);
  for (let k = 0; k < 3; k++) off('tube' + (i * 3 + k), a + p, b + q, c + r);
}
const EAR = 1;
chapter({
  id: 'ears', dur: 14, cuts: [4.5, 9.5], head: 'The ears',
  caps: [[0.4, 4.5, 'Two clear PETG halves, 60 mm at the centre and 26 at the rim.'],
         [4.6, 9.4, 'My first ear snapped on its layer lines, so three tubes now cross the joint.'],
         [9.5, 13.7, 'The peg goes 32 mm into a socket in the shell, with four 10-32s.']],
  f(t) {
    hide(['visor', ...MAG_V, ...CAPS, ...PLATES, 'crown', ...SPACERS, 'tray', 'hat', 'earTop0', 'earBot0', 'tube0', 'tube1', 'tube2']);
    const e = D.ears[EAR], eZ = D.ear_zc;
    const O = [e.S[0] - 32 * e.u[0], e.S[1] - 32 * e.u[1], e.S[2] - 32 * e.u[2]];
    const mid = (zz, nn = 0, ww = 0) => [O[0] + e.u[0] * zz + e.n[0] * nn + e.w[0] * ww, O[1] + e.u[1] * zz + e.n[1] * nn + e.w[1] * ww, O[2] + e.u[2] * zz + e.n[2] * nn + e.w[2] * ww];
    const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    if (t < 4.5) {                 // cut across the disc: the lens shape, and the centre tube in its bore
      hide(['shellT', 'shellB', ...MAG_S]);
      const c = mid(eZ - 10);
      setSection(true, e.w.map(v => -v), dot(e.w, c) + 0);
      const azC = Math.atan2(e.w[0], -e.w[1]) * 57.3, elC = Math.asin(e.w[2]) * 57.3;
      setCam(camAt([[0, azC + 10, elC - 8, 1140, c[0], c[1], c[2]], [4.5, azC, elC, 1040, c[0], c[1], c[2]]], t));
      const la = S(t, 1.0, 1.6) * (1 - S(t, 3.9, 4.4));
      label('60 mm at the centre', '', mid(eZ + 30, -28), 1380, 300, 'r', la);
      label('26 mm at the rim', '', mid(eZ + 165, -11), 1380, 170, 'r', la);
      label('Centre tube in its bore', '', mid(eZ - 90, 0), 560, 620, 'l', la);
    } else if (t < 9.5) {          // the halves come apart along the tubes
      hide(['shellT', 'shellB', ...MAG_S]);
      const part = S(t, 4.5, 6.3) * (1 - S(t, 8.4, 9.3));
      placeEar(EAR, 0, 62 * part, 215 * part);
      const c = mid(eZ + 40);
      setCam(camAt([[4.5, 46, 8, 1520, c[0], c[1], c[2]], [9.5, 24, 6, 1420, c[0], c[1], c[2]]], t));
      const la = S(t, 5.7, 6.3) * (1 - S(t, 8.3, 8.9));
      label('Top half', '', at('earTop1', [60, 0, 280]), 1560, 190, 'r', la);
      label('Polycarbonate tubes, 1 inch', '×3', at('tube3', [0, 0, 170]), 500, 300, 'l', la);
      label('Bottom half', '', at('earBot1', [60, 0, 120]), 1560, 650, 'r', la);
      label('Rim channel for a 10 mm strip', '', mid(eZ, 0, -169) .map((v, i) => v + earOffset(EAR, 0)[i]), 500, 700, 'l', la);
    } else {                       // cut through the socket: the peg goes in
      fade(['shellT', 'shellB'], 0.8); hide(MAG_S);
      const peg = 70 * (1 - S(t, 10.4, 12.6));
      placeEar(EAR, peg, 0, 0);
      setSection(true, e.n, -dot(e.n, e.S));
      const c = mid(36);
      const azC = Math.atan2(-e.n[0], e.n[1]) * 57.3, elC = Math.asin(-e.n[2]) * 57.3;
      setCam(camAt([[9.5, azC - 10, elC + 4, 640, c[0], c[1], c[2]], [14, azC - 2, elC, 520, c[0], c[1], c[2]]], t));
      const la = S(t, 9.9, 10.5);
      const u = earOffset(EAR, peg);
      label('Peg, 60 × 34 × 32 mm', '', mid(14, 0, -22).map((v, i) => v + u[i]), 470, 780, 'l', la);
      label('Socket inside the shell', '', mid(14, 0, 33), 1440, 150, 'r', la);
      label('Centre tube seat', '', mid(-5), 1440, 790, 'r', la);
    }
  },
});

// 5. visor
chapter({
  id: 'visor', dur: 15, cuts: [6.0, 10.2], head: 'The visor',
  caps: [[0.4, 5.9, 'The visor sits behind the mouth slot: a 2 mm band of a smaller sphere on 12 mm pins.'],
         [6.0, 10.1, 'It swings up 40 degrees. Magnets hold it shut and hold it open.'],
         [10.2, 14.7, '2.9 mm holes, 55% open. Printed black, I can see out and people can’t see in.']],
  stats: [[10.6, 14.4, '55%', 'open']],
  f(t) {
    hide([...EARS, ...TUBES, ...PLATES, 'crown', ...SPACERS, 'tray', 'hat']);
    fade(['shellT', 'shellB'], 0.42); fade(MAG_S, 1);
    const swing = S(t, 6.3, 7.8) * (1 - S(t, 8.6, 9.9));
    visorG.rotation.x = -rad(D.params.OPEN_ANGLE) * swing;
    MAG_S.forEach((n, i) => { P[n].hl = (i < 2 ? (1 - swing) : swing) * S(t, 6.0, 6.5) * (1 - S(t, 9.6, 10.0)) * 4; });
    MAG_V.forEach(n => { P[n].hl = S(t, 6.0, 6.5) * (1 - S(t, 9.6, 10.0)) * 4; });
    const m = i => { const p = D.mag_shell[i], r = Math.hypot(...p), k = D.mag_r_shell / r; return [p[0] * k, p[1] * k, p[2] * k]; };
    if (t < 6.0) {
      setCam(camAt([[0, 64, 8, 980, 92, -20, 0], [6.0, 50, 12, 880, 92, -20, 0]], t));
      const la = S(t, 1.2, 1.8) * (1 - S(t, 5.4, 5.9));
      label('Ø12 pin, part of the shell', '', [D.X_PIN_END + 6, 6, 0], 1480, 180, 'r', la);
      label('Ø40 pad, on a Ø56 hub', '', [162, 19, -8], 1480, 300, 'r', la);
      label('Pivot cap', '×2', at('cap1'), 420, 240, 'l', la);
      label('Grab lip', '', [-20, -158, -106], 420, 760, 'l', la);
    } else if (t < 10.2) {
      setCam(camAt([[6.0, 30, 10, 1180, 0, -40, 14], [10.2, 18, 8, 1120, 0, -40, 14]], t));
      const la = S(t, 6.5, 7.0) * (1 - S(t, 9.6, 10.0));
      label('These hold it open', '', m(3), 500, 200, 'l', la);
      label('These hold it shut', '', m(1), 500, 480, 'l', la);
      label('Magnets, 6 × 3 mm', '×6', m(2), 1500, 200, 'r', la);
    } else {
      fade(['shellT', 'shellB'], 0.05); hide(MAG_S);
      setCam(camAt([[10.2, -8, -6, 240, 16, -150, -24], [15, 6, -3, 160, 16, -150, -24]], t));
    }
  },
});

// 6. hard hat
chapter({
  id: 'hat', dur: 11, cuts: [5.3], head: 'The hard hat',
  caps: [[0.4, 5.2, 'It weighs about 4.5 kg, so it rides on a hard hat bolted inside the crown.'],
         [5.3, 10.7, 'Spacer stacks set the height. The hat here is a reference shape, not my actual 3M one.']],
  stats: [[0.9, 4.9, '4.5 kg', 'carried by the hat’s suspension']],
  f(t) {
    hide([...EARS, ...TUBES, ...PLATES, 'tray', ...CAPS]);
    P.hat.fade = 1;
    if (t < 5.3) {
      hide(['visor', ...MAG_V]);
      fade(['shellT', 'shellB', ...MAG_S], 0.34);
      const k = 1 - S(t, 1.2, 4.2);
      off('hat', 0, 0, -100 * k);
      SPACERS.forEach(n => off(n, 0, 0, -(P[n].lvl + 1) * 11 * k));
      P.crown.edge = 0.5; SPACERS.forEach(n => P[n].edge = 0.5);
      setCam(camAt([[0, -40, -30, 1260, 0, 10, 40], [5.3, -26, -34, 1160, 0, 10, 40]], t));
      const la = S(t, 1.2, 1.8) * (1 - S(t, 4.6, 5.1));
      label('Crown frame, on the 4 bosses', '', at('crown', [52, 28, 146]), 1500, 200, 'r', la);
      label('Spacers: 2, 4, 8, 16 mm', '×16', at(SPACERS[4]), 520, 300, 'l', la);
      label('Hat, reference shape', '', at('hat', [-90, 0, 60]), 520, 700, 'l', la);
    } else {
      P.wm_dome.fade = 1;
      setSection(true, [1, 0, 0], 0);
      setCam(camAt([[5.3, -74, 3, 1240, 0, 8, 12], [11, -86, 2, 1120, 0, 8, 16]], t));
      const la = S(t, 5.9, 6.5) * (1 - S(t, 10.2, 10.7));
      label('Crown frame', '', [0, 58, 157], 1400, 130, 'r', la);
      label('Spacer stack', '', at(SPACERS[9]), 1400, 270, 'r', la);
      label('Hat, reference shape', '', [0, 88, 52], 1400, 410, 'r', la);
      label('Head form, from the wall mount', '', [0, 30, 48], 1400, 550, 'r', la * S(t, 6.4, 7.2));
      label('Visor', '', [0, -158, -30], 520, 550, 'l', la);
    }
  },
});

// 7. tray
chapter({
  id: 'tray', dur: 7, head: 'The electronics tray',
  caps: [[0.4, 6.7, 'A flat tray on two bosses, with the power jack hole beside it. The controller isn’t in the CAD.']],
  f(t) {
    hide([...EARS, ...TUBES, 'visor', ...MAG_V, ...CAPS, 'crown', ...SPACERS, 'hat', ...PLATES, ...MAG_S, 'shellT']);
    setSection(true, [0, 1, 0], -36);      // keep the back of the helmet, look at the inside of it
    P.tray.edge = 0.7; fade(['shellB'], 0.6);
    setCam(camAt([[0, -20, 14, 780, 20, 100, -82], [7, 14, 9, 600, 22, 100, -84]], t));
    const la = S(t, 1.0, 1.6) * (1 - S(t, 6.2, 6.7));
    label('Tray, 80 × 36 mm, M3 and zip-tie grid', '', at('tray', [-20, 113, -112]), 620, 300, 'l', la);
    label('16 mm hole for the GX16 jack', '', D.conn, 1420, 700, 'r', la);
    label('Bosses for two 10-32s', '', [D.tray_pts[1][0] * 166, D.tray_pts[1][1] * 166, D.tray_pts[1][2] * 166], 1420, 300, 'r', la);
  },
});

// 8. the exploded view
const X = { Ztop: 280, Zbot: 165, U1: 100, T: 92, K: 195, Vy: 580, Vdrop: 170, Rp: 150, Hat: 62, Ty: 330, Tz: -18 };
function explode(d) {
  for (let i = 0; i < 2; i++) placeEar(i, X.U1 * d.ear[i], X.T * d.halves[i], X.K * d.halves[i]);
  off('shellT', 0, 0, X.Ztop * d.shell); MAG_S.forEach(n => off(n, 0, 0, X.Ztop * d.shell));
  off('shellB', 0, 0, -X.Zbot * d.shell);
  PLATES.forEach((n, i) => { const r = D.plates[i].d, k = X.Rp * d.plates[i]; off(n, r[0] * k, r[1] * k, r[2] * k); });
  // the visor rides with the top half, because its pins are in it. It comes off forward and down.
  visorOff.position.set(0, -X.Vy * d.visor, X.Ztop * d.shell - X.Vdrop * d.visor);
  CAPS.forEach((n, i) => { off(n, -D.caps[i].s * 70 * d.caps[i], -X.Vy * d.visor, X.Ztop * d.shell - X.Vdrop * d.visor); });
  SPACERS.forEach(n => off(n, 0, 0, -(P[n].lvl + 1) * 13 * d.spacers));
  off('hat', 0, 0, -X.Hat * d.hat);
  // the tray waits inside the shell line while the shell closes, then goes to its bosses
  off('tray', 0, X.Ty * d.tray - 55 * d.trayIn, X.Tz * d.tray + 22 * d.trayIn);
}
function explodeState(t) {
  const O = (a, b) => S(t, a, b), B = (a, b) => 1 - S(t, a, b);
  return {
    ear: [O(1.0, 2.4) * B(23.8, 25.0), O(1.1, 2.5) * B(23.6, 24.8)],
    halves: [O(2.6, 4.3) * B(22.3, 23.6), O(2.7, 4.4) * B(22.2, 23.5)],
    shell: O(4.6, 6.2) * B(20.6, 22.0),
    plates: [0, 1, 2, 3, 4, 5].map(i => O(6.1 + i * 0.1, 7.2 + i * 0.1) * B(20.5 + i * 0.05, 21.4 + i * 0.05)),
    visor: O(7.6, 9.0) * B(18.0, 19.4),
    caps: [O(7.6, 8.3) * B(19.4, 20.2), O(7.7, 8.4) * B(19.5, 20.3)],
    spacers: O(9.0, 9.9) * B(25.0, 25.8),
    hat: O(9.4, 10.4) * B(25.3, 26.2),
    tray: O(10.4, 11.5) * B(19.6, 20.4),
    trayIn: O(19.6, 20.4) * B(26.2, 27.0),
  };
}
chapter({
  id: 'exploded', dur: 28, head: 'Everything apart', headOut: [3.0, 3.7, 24.2, 25.0],
  caps: [[0.4, 4.5, 'Ears off first, then each opens into two halves and three tubes.'],
         [4.6, 7.5, 'The shell splits and six plates come off.'],
         [7.6, 11.7, 'Visor and caps forward, then the spacers, hat and tray.'],
         [11.8, 17.9, 'That’s the whole helmet. Screws, inserts and filament stubs aren’t drawn.'],
         [18.0, 20.5, 'Back in build order: visor, then caps.'],
         [20.6, 22.1, 'The shell closes.'],
         [22.2, 25.0, 'Tubes into the ears, ears into the sockets.'],
         [25.1, 27.6, 'Then the hat and the tray.']],
  f(t) {
    P.hat.fade = 1;
    const d = explodeState(t); explode(d);
    // the small black parts need their edges to read at this distance
    [...PLATES, ...CAPS, ...SPACERS, 'crown', 'tray'].forEach(n => { P[n].edge = 0.8; });
    setCam(camAt([
      [0, -30, 6, 1900, 0, 0, 100],
      [4, -33, 9, 2650, 0, -40, 150],
      [11.5, -40, 11, 2840, -110, -40, 150],
      [18, -22, 12, 2840, -110, -40, 150],
      [23, -24, 9, 2500, 0, -20, 130],
      [28, -30, 7, 1760, 0, 0, 110]], t));
    const out = 1 - S(t, 17.5, 18.0);
    const A = a => S(t, a, a + 0.6) * out;
    label('Ear halves', '×4', at('earTop1'), 330, 180, 'l', A(3.4));
    label('Clear tubes', '×6', at('tube3', [0, 0, 160]), 330, 290, 'l', A(3.6));
    label('Crown frame', '', at('crown', [-50, 15, 150]), 330, 450, 'l', A(9.1));
    label('Hard hat, reference shape', '', at('hat', [-100, 15, 40]), 330, 545, 'l', A(9.6));
    label('Seam plates', '×6', at('plate5'), 330, 735, 'l', A(6.5));
    label('Electronics tray', '', at('tray'), 330, 640, 'l', A(11.3));
    label('Shell bottom half', '', at('shellB', [-110, -60, -90]), 330, 830, 'l', A(5.4));
    label('Shell top half', '', at('shellT', [80, -40, 130]), 1620, 150, 'r', A(5.4));
    label('Spacers', '×16', at(SPACERS[3]), 1620, 300, 'r', A(9.4));
    label('Pivot caps', '×2', at('cap0'), 1620, 480, 'r', A(8.0));
    label('Visor', '', [120, -X.Vy * d.visor - 125, X.Ztop * d.shell - X.Vdrop * d.visor - 60], 1620, 650, 'r', A(8.4));
  },
});

// 9. wall mount
chapter({
  id: 'wall', dur: 11, head: 'The wall mount',
  caps: [[0.4, 5.7, 'Felt pads cup the shell, and a dome on a post takes the hat’s suspension.'],
         [5.8, 10.7, 'Three screws into one stud, and the helmet’s back sits 28 mm off the wall.']],
  f(t) {
    fade(WALL, 1); P.hat.fade = 1;
    const hel = 245 * (1 - S(t, 2.0, 5.4));
    ['shellT', 'shellB', ...MAG_S, ...EARS, ...TUBES, ...PLATES, 'crown', ...SPACERS, 'tray', 'hat', ...CAPS].forEach(n => off(n, 0, 0, hel));
    visorOff.position.set(0, 0, hel);
    uLed.value = S(t, 5.4, 6.6); updateLeds(t + 30);     // the LED layer stays put, so it comes on once the helmet is down
    setCam(camAt([[0, -38, 5, 2650, 0, 30, 130], [5.4, -40, 5, 2320, 0, 30, 40], [8.4, -86, 2, 2240, 0, 70, 120], [11, -88, 1, 1420, 0, 120, 30]], t));
    const la = S(t, 0.7, 1.3) * (1 - S(t, 4.9, 5.4));
    label('Dome, 140 × 175 mm', '', at('wm_dome', [-30, -30, 75]), 500, 320, 'l', la);
    label('Post, pin every 10 mm', '', at('wm_post', [0, 0, 120]), 500, 500, 'l', la);
    label('Bracket, 3 screws into a stud', '', at('wm_bracket', [-25, 208, -280]), 500, 760, 'l', la);
    label('Cradle, four arms for the felt', '', at('wm_cradle', [122, 0, -135]), 1450, 640, 'r', la);
    const lb = S(t, 7.6, 8.2) * (1 - S(t, 10.2, 10.7));
    dimQueue.push({ a: [0, D.R_O, 0], b: [0, D.wall_y, 0], text: '28 mm', alpha: lb });
    wallLine.a = S(t, 7.0, 8.0) * (1 - S(t, 10.2, 10.7)) * 0.5;
  },
});

// 10. the end
chapter({
  id: 'end', dur: 5, head: 'mau5head',
  caps: [[0.5, 4.4, 'The STEP files and the code that makes them are in the repo.']],
  f(t) {
    uLed.value = 1; updateLeds(t + 50);
    setCam(camAt([[0, -36, 8, 1620, 0, 0, 118], [5, -14, 11, 1660, 0, 0, 118]], t));
  },
});

let total = 0;
CH.forEach(c => { c.start = total; total += c.dur; });
window.__duration = total;
const DIP = 0.5;

window.renderAt = function (tAbs) {
  const c = CH.find(k => tAbs >= k.start && tAbs < k.start + k.dur) || CH[CH.length - 1];
  const t = tAbs - c.start;
  resetPose();
  c.f(t);
  commit(t);
  setSection(renderer.clippingPlanes.length > 0, clipN(), clip.constant);
  composer.render();
  renderer.setRenderTarget(null);
  finalMat.uniforms.t.value = composer.readBuffer.texture;
  const dipIn = c === CH[0] ? 1 - S(t, 0, 1.0) : 1 - S(t, 0, DIP);
  const dipOut = S(t, c.dur - DIP, c.dur);
  let dipCut = 0;
  (c.cuts || []).forEach(b => { dipCut = Math.max(dipCut, 1 - S(Math.abs(t - b), 0.0, 0.42)); });
  finalMat.uniforms.uDip.value = Math.max(dipIn, dipOut, dipCut);
  renderer.render(finalScene, finalCam);
  // overlay
  ov.clearRect(0, 0, W, H);
  drawBand();
  const hk = c.headOut ? Math.max(1 - S(t, c.headOut[0], c.headOut[1]), S(t, c.headOut[2], c.headOut[3])) : 1;
  drawHead(c.head, hk * S(t, 0.25, 0.8) * (1 - S(t, c.dur - 0.7, c.dur - 0.25)));
  (c.stats || []).forEach(([a, b, s, u]) => { const k = S(t, a, a + 0.5) * (1 - S(t, b - 0.5, b)); if (k > 0) drawStat(s, u, k); });
  if (c.overlay) c.overlay(t);
  drawLabels(tAbs); drawDims();
  c.caps.forEach(([a, b, s]) => { const k = S(t, a, a + 0.3) * (1 - S(t, b - 0.3, b)); drawCaption(s, k); });
};
function clipN() { const n = clip.normal; return [n.x, -n.z, n.y]; }
function drawStat(s, u, a) {
  ov.save(); ov.globalAlpha = a; ov.textBaseline = 'alphabetic';
  ov.font = F_STAT; ov.fillStyle = AMBER; ov.fillText(s, 48, 190);
  ov.font = F_UNIT; ov.fillStyle = TEXT2; ov.fillText(u, 48, 228);
  ov.restore();
}
// composite both canvases and send the frame to film.py's server
const outc = document.createElement('canvas'); outc.width = W; outc.height = H; const outx = outc.getContext('2d', { alpha: false });
window.saveFrame = async function (name) {
  outx.drawImage(glc, 0, 0); outx.drawImage(ovc, 0, 0);
  const blob = await new Promise(r => outc.toBlob(r, 'image/png'));
  await fetch('/frame/' + name, { method: 'POST', body: blob });
};
// an assembled view from any side, for checking the geometry; not used in the film
window.debugView = async function (name, az, el, d, tx, ty, tz, sec) {
  resetPose(); P.hat.fade = 1;
  setCam([az, el, d, tx, ty, tz]);
  commit(0);
  if (sec) setSection(true, sec.slice(0, 3), sec[3]);
  composer.render(); renderer.setRenderTarget(null); finalMat.uniforms.t.value = composer.readBuffer.texture; finalMat.uniforms.uDip.value = 0; renderer.render(finalScene, finalCam);
  ov.clearRect(0, 0, W, H); await window.saveFrame(name);
};
window.chapters = () => CH.map(c => ({ id: c.id, start: c.start, dur: c.dur, head: c.head, caps: c.caps }));
window.renderLayout = function (tAbs) {     // poses and labels only, no GPU: fast checks of every frame
  const c = CH.find(k => tAbs >= k.start && tAbs < k.start + k.dur) || CH[CH.length - 1];
  resetPose(); c.f(tAbs - c.start); ov.clearRect(0, 0, W, H); drawLabels(tAbs);
};

// ── load and build ────────────────────────────────────────────────────────────
(async () => {
  D = await (await fetch('build/scene.json')).json();
  MF = await (await fetch('build/mesh/manifest.json')).json();
  await Promise.all(Object.keys(MF).map(loadGeo));

  addPart('shellT', 'shell_top', 'shell', null, { group: 'shell' });
  addPart('shellB', 'shell_bottom', 'shell', null, { group: 'shell' });
  const earM = D.ears.map(e => fromArr(e.m));
  [0, 1].forEach(i => {
    addPart('earTop' + i, 'ear_top', 'ear', earM[i]); addPart('earBot' + i, 'ear_bottom', 'ear', earM[i]);
    if (MF.ear_top_thick) { addPart('earTopT' + i, 'ear_top_thick', 'ear', earM[i]); addPart('earBotT' + i, 'ear_bottom_thick', 'ear', earM[i]); }
    D.tubes_ear.forEach((tb, k) => addPart('tube' + (i * 3 + k), tb.kind, 'tube', earM[i].clone().multiply(translate(tb.x, 0, tb.z0))));
  });
  // visor: offset group, then the hinge
  visorOff = new THREE.Group(); world.add(visorOff);
  visorG = new THREE.Group(); visorOff.add(visorG);
  const vp = addPart('visor', 'visor', 'black', null, { parent: visorG, noEdges: true });
  const magGeo = new THREE.CylinderGeometry(3, 3, 3, 32); magGeo.rotateX(Math.PI / 2);
  geoCache.__mag = magGeo; MF.__mag = { min: [-3, -3, -1.5], max: [3, 3, 1.5], ne: 0 };
  const zAxis = new THREE.Vector3(0, 0, 1);
  const magM = (p, r) => { const n = new THREE.Vector3(...p).normalize(); const q = new THREE.Quaternion().setFromUnitVectors(zAxis, n); return new THREE.Matrix4().compose(n.clone().multiplyScalar(r), q, new THREE.Vector3(1, 1, 1)); };
  D.mag_shell.forEach((p, i) => { addPart('magS' + i, '__mag', 'magnet', magM(p, D.mag_r_shell)); });
  D.mag_visor.forEach((p, i) => { addPart('magV' + i, '__mag', 'magnet', magM(p, D.mag_r_visor), { parent: visorG }); });
  D.caps.forEach((c, i) => addPart('cap' + i, 'pivot_cap', 'black', fromArr(c.m)));
  D.plates.forEach((c, i) => addPart('plate' + i, 'seam_plate', 'black', fromArr(c.m)));
  addPart('crown', 'crown_frame', 'black');
  addPart('tray', 'tray', 'black');
  addPart('hat', 'hat', 'hat', null, { noEdges: true });
  addPart('wm_bracket', 'wm_bracket', 'mount'); addPart('wm_cradle', 'wm_cradle', 'mount');
  addPart('wm_post', 'wm_post', 'dome', translate(0, 0, D.post_z)); addPart('wm_dome', 'wm_dome', 'dome');
  D.hat_pts.forEach((p, i) => {
    let z = p.z;
    [16, 8, 4, 2].forEach((h, lvl) => {
      z -= h; const n = `sp${i}_${h}`; addPart(n, 'spacer_' + h, 'black', translate(p.x, p.y, z)); P[n].lvl = lvl; SPACERS.push(n);
    });
  });
  // the pocket centre nearest 28° on the chosen channel, for the close-up's labels
  const j = D.params.N_CH * 0.75 + 3, azc = (j + 0.5) * 360 / D.params.N_CH;
  let best = 1e9;
  D.windows.forEach(w => { const a = (Math.atan2(w[1], w[0]) * 57.2958 + 360) % 360, l = Math.asin(w[2] / D.R_O) * 57.2958; if (Math.abs(a - azc) < 0.5 && Math.abs(l - 28) < best) { best = Math.abs(l - 28); S_.pktLat = l; } });

  buildLeds();
  TUBES.forEach((n, i) => addTubeGlow(n, D.tubes_ear[i % 3].L));
  buildSections();
  resetPose();
  await document.fonts.load(F_HEAD, 'A'); await document.fonts.load(F_CAP, 'A');
  window.__ready = true;
})();
