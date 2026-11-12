// "A porta e o porteiro" — cenas em pintura a óleo com espátula (motor impasto do Lemo-Opuscar, MIT).
// ?cena=colmeias (abertura, fala 1) | colmeias_fim (fala 9, fim de tarde). Tudo pintado em código. Quadro 1080x1080.
import { Impasto, Strokes, KNIFE, DAB, hex, shade } from './engine/impasto.js';
import { Ref, paintRef } from './engine/plate.js';

const V = 1080, TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const P = pts => c => { c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]); c.closePath(); };
const El = (x, y, rx, ry, r = 0) => c => c.ellipse(x, y, rx, ry, r, 0, TAU);
const Rc = (x, y, w, h) => c => c.rect(x, y, w, h);
const lin = (x0, y0, x1, y1, st) => c => { const g = c.createLinearGradient(x0, y0, x1, y1); st.forEach(([o, k]) => g.addColorStop(o, k)); return g; };
const hsh = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const q = new URLSearchParams(location.search), CENA = q.get('cena') || 'colmeias';

const VW = 1500, VH = 1300;
const HIVES = [[330, 860, '#f2c230'], [520, 880, '#3a7ad0'], [710, 870, '#d04030'], [900, 885, '#f4efe2'], [1090, 865, '#4aa860']];
function drawCampo(R) {
  R.fill(Rc(0, 0, VW, 560), lin(0, 0, 0, 560, [[0, '#1f68d8'], [.6, '#5aa8ec'], [1, '#c6e8f6']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  const nuvem = (x, y, w) => R.fill(c => { c.ellipse(x, y, w, w * .28, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .5, w * .2, 0, 0, TAU); c.ellipse(x + w * .5, y + 12, w * .45, w * .2, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#ffffff'], [1, '#e2ecf4']]), { dir: -3, fallback: -3, group: 'ceu', maxR: 20 });
  nuvem(300, 140, 130); nuvem(900, 100, 160); nuvem(1300, 220, 110);
  R.fill(c => { c.moveTo(0, 560); c.quadraticCurveTo(400, 470, 800, 520); c.quadraticCurveTo(1200, 470, VW, 530); c.lineTo(VW, 600); c.lineTo(0, 600); c.closePath(); }, '#3f8a4a', { dir: 0, group: 'morro', maxR: 14 });
  R.fill(Rc(0, 580, VW, VH - 580), lin(0, 580, 0, VH, [[0, '#7cc23e'], [.5, '#4fa83a'], [1, '#2f7a2e']]), { dir: 75, fallback: 75, group: 'campo', maxR: 30, jit: .1 });
  // manchas de flores: amarelo, branco, lilás, laranja
  const FL = ['#ffd23a', '#fff8e8', '#b07ad8', '#ff8a2a', '#ffe26a'];
  for (let i = 0; i < 150; i++) { const x = hsh(i * 3.1) * VW, y = 640 + hsh(i * 7.3) * 640, s = .6 + (y - 600) / 700;
    R.fill(c => { for (let k = 0; k < 7; k++) { const dx = (hsh(i * 11 + k) - .5) * 70 * s, dy = (hsh(i * 13 + k) - .5) * 24 * s; c.moveTo(x + dx + 8 * s, y + dy); c.ellipse(x + dx, y + dy, 8 * s, 6 * s, 0, 0, TAU); } }, FL[i % FL.length], { dir: 0, group: 'flor' + i, maxR: 3 + 3 * s });
    R.fill(c => { for (let k = 0; k < 7; k++) { const dx = (hsh(i * 11 + k) - .5) * 70 * s, dy = (hsh(i * 13 + k) - .5) * 24 * s; c.moveTo(x + dx + 2.5 * s, y + dy); c.ellipse(x + dx, y + dy, 2.5 * s, 2.5 * s, 0, 0, TAU); } }, '#7a4a10', { dir: 0, group: 'mio' + i, maxR: 2 }); }
  // ipê-amarelo à direita
  R.fill(P([[1290, 900], [1312, 600], [1330, 600], [1350, 900]]), '#5a3a24', { dir: 90, group: 'tronco', maxR: 8 });
  R.fill(c => { c.ellipse(1320, 470, 210, 150, 0, 0, TAU); c.ellipse(1200, 540, 120, 90, 0, 0, TAU); c.ellipse(1440, 540, 110, 90, 0, 0, TAU); }, lin(1100, 330, 1500, 640, [[0, '#ffe24a'], [.6, '#f2b818'], [1, '#d89810']]), { dir: 20, fallback: 20, group: 'ipe', maxR: 18, detail: 1.4 });
  // colmeias coloridas (caixas de madeira), com tampa e cavalete
  HIVES.forEach(([x, y, cor], i) => {
    R.fill(P([[x - 70, y + 10], [x - 64, y + 70], [x - 52, y + 70], [x - 56, y + 10], [x + 56, y + 10], [x + 52, y + 70], [x + 64, y + 70], [x + 70, y + 10]]), '#5a3a22', { dir: 90, group: 'cav' + i, maxR: 5 });
    R.fill(Rc(x - 66, y - 130, 132, 140), cor, { dir: 90, group: 'cx' + i, maxR: 12 });
    R.fill(Rc(x - 66, y - 62, 132, 6), shade_hex(cor, .75), { dir: 0, group: 'cx' + i, maxR: 3 });
    R.fill(P([[x - 78, y - 130], [x + 78, y - 130], [x + 72, y - 152], [x - 72, y - 152]]), '#8a8a90', { dir: 0, group: 'tp' + i, maxR: 6 });
    R.fill(Rc(x - 30, y - 6, 60, 8), '#2a1a10', { dir: 0, group: 'cx' + i, maxR: 2 });
  });
}
function shade_hex(h, k) { const c = hex(h).map(v => Math.round(v * k * 255)); return '#' + c.map(v => v.toString(16).padStart(2, '0')).join(''); }

let E, dyn, PL;
export async function setup(canvas) {
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(4096);
  const R = new Ref(VW, VH, 1); drawCampo(R);
  const st = paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 9 });
  PL = { b: E.batch(st.data()), tex: E.texture(R.ctx.canvas) };
  window.DUR = +(q.get('dur') || 6.5);
  return frame;
}
// abelhas: pinceladas pequenas em laço em volta das colmeias, semente fixa por abelha
function abelhas(t, n = 46) {
  for (let i = 0; i < n; i++) {
    const [hx, hy] = HIVES[i % HIVES.length], ph = hsh(i * 9.1) * TAU, sp = .8 + hsh(i) * .9, rx = 70 + hsh(i * 2.2) * 120, ry = 40 + hsh(i * 3.3) * 70;
    const a = ph + t * sp * 2.2, x = hx + Math.cos(a) * rx + Math.sin(a * 2.3) * 12, y = hy - 80 + Math.sin(a) * ry;
    dyn.push({ x, y, ang: a + Math.PI / 2, len: 9, wid: 7, c: hex('#2a1e0c'), c2: hex('#f2c230'), type: DAB, seed: 200 + i, hgt: 1.2 });
    dyn.push({ x: x + 3, y: y - 4, ang: a, len: 6, wid: 4, c: hex('#fff6dc'), type: DAB, seed: 400 + i, alpha: .7, hgt: .6 });
  }
}
function frame(t) {
  E.begin();
  const fim = CENA === 'colmeias_fim';
  const k = ss(seg(t, 0, fim ? 3.6 : 6.4));
  const C = fim ? { x: lerp(690, 760, k), y: lerp(760, 720, k), zoom: lerp(1.3, 1.18, k) } : { x: lerp(900, 700, k), y: lerp(600, 760, k), zoom: lerp(1.0, 1.24, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  abelhas(t, fim ? 22 : 46); E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  E.finish(fim ? { expo: .82, sat: 1.0, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .76, .5], gain: [1.1, .88, .72] }
               : { expo: 1.04, sat: 1.12, contrast: 1.05, vig: .22, spec: .26, light: [-.6, -.55, .7] });
}
