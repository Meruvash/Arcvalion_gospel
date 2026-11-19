// "O irmão vira dono da herança?" — a sede antiga da fazenda da família, de manhã: varanda com uma cadeira ocupada (o irmão
// que toca a fazenda) e as outras vazias; "posse exclusiva" a espátula (fala 2). ?cena=fim: a mesma sede no fim de tarde,
// com uma única janela acesa (fala 9). Motor impasto do Lemo-Opuscar (MIT). 1080x1080.
import { Impasto, Strokes, DAB, hex } from './engine/impasto.js';
import { Ref, paintRef } from './engine/plate.js';
const V = 1080, TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, k) => a + (b - a) * k;
const P = pts => c => { c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]); c.closePath(); };
const El = (x, y, rx, ry, r = 0) => c => c.ellipse(x, y, rx, ry, r, 0, TAU);
const Rc = (x, y, w, h) => c => c.rect(x, y, w, h);
const lin = (x0, y0, x1, y1, st) => c => { const g = c.createLinearGradient(x0, y0, x1, y1); st.forEach(([o, k]) => g.addColorStop(o, k)); return g; };
const q = new URLSearchParams(location.search), FIM = q.get('cena') === 'fim';
const SERIF = '"News", Georgia, serif', VW = 1700, VH = 1300;
function drawSede(R) {
  const ceu = FIM ? [[0, '#2a3070'], [.55, '#d0607a'], [1, '#ffb060']] : [[0, '#3a8ae8'], [.7, '#a8d8f8'], [1, '#f4f8f0']];
  R.fill(Rc(0, 0, VW, 560), lin(0, 0, 0, 560, ceu), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  R.fill(El(FIM ? 300 : 1420, FIM ? 500 : 140, 90, 90), lin(0, 50, 0, 590, FIM ? [[0, '#fff0c0'], [1, '#ff8a40']] : [[0, '#fffbe0'], [1, '#ffe080']]), { dir: 0, group: 'sol', maxR: 14 });
  R.fill(c => { c.moveTo(0, 520); c.quadraticCurveTo(400, 420, 800, 500); c.quadraticCurveTo(1200, 430, VW, 500); c.lineTo(VW, 600); c.lineTo(0, 600); c.closePath(); }, FIM ? '#3a3050' : '#3a7a4a', { dir: 0, group: 'serra', maxR: 14 });
  R.fill(Rc(0, 580, VW, VH - 580), lin(0, 580, 0, VH, FIM ? [[0, '#6a6a2a'], [1, '#2a2a14']] : [[0, '#a0d858'], [1, '#4a9a2a']]), { dir: 75, fallback: 75, group: 'pasto', maxR: 28, jit: .1 });
  // a sede: casa comprida caiada, telhado de barro, varanda com colunas
  R.fill(Rc(470, 470, 760, 240), FIM ? '#d8c0a0' : '#f8f0dc', { dir: 90, group: 'parede', maxR: 6 });
  R.fill(P([[430, 476], [850, 360], [1270, 476]]), FIM ? '#7a3020' : '#c85a2a', { dir: 15, group: 'telhado', maxR: 5 });
  R.fill(P([[430, 560], [1270, 560], [1300, 600], [400, 600]]), FIM ? '#6a2a18' : '#b04a22', { dir: 0, group: 'beiral', maxR: 4 });
  for (let k = 0; k < 6; k++) R.fill(Rc(470 + k * 150, 600, 16, 110), FIM ? '#c8b090' : '#fff8ea', { dir: 90, group: 'col' + k, maxR: 3 });
  [[540, 500], [700, 500], [1000, 500], [1140, 500]].forEach(([x, y], k) => R.fill(Rc(x, y, 60, 50), FIM ? (k === 2 ? '#ffd060' : '#2a2a3a') : '#2a6aa0', { dir: 90, group: 'jan' + k, maxR: 3 }));
  R.fill(Rc(830, 610, 60, 100), FIM ? '#3a2a1a' : '#2a5a8a', { dir: 90, group: 'porta', maxR: 3 });
  R.fill(Rc(450, 700, 800, 20), '#8a6a4a', { dir: 0, group: 'piso', maxR: 4 });
  // cadeiras na varanda: uma ocupada (o irmão, de chapéu), as outras vazias
  [[560, 0], [700, 1], [980, 1], [1110, 1]].forEach(([x, vazia], k) => { R.fill(Rc(x, 640, 50, 60), '#7a4a2a', { dir: 90, group: 'cad' + k, maxR: 3 }); R.fill(Rc(x, 610, 8, 40), '#6a3a1a', { dir: 90, group: 'enc' + k, maxR: 2 }); });
  R.fill(P([[560, 650], [568, 590], [608, 590], [612, 650]]), FIM ? '#3a3a4a' : '#3a5a8a', { dir: 90, group: 'irmao', maxR: 3 });
  R.fill(El(588, 575, 15, 16), '#8a5a3a', { dir: 0, group: 'rosto', maxR: 3 }); R.fill(El(588, 562, 30, 8), '#e0c070', { dir: 0, group: 'chapeu', maxR: 3 });
  // mangueira grande, curral e estrada até a porteira
  R.fill(Rc(285, 470, 26, 250), '#4a3020', { dir: 90, group: 'tronco', maxR: 4 });
  R.fill(c => { c.ellipse(300, 420, 190, 140, 0, 0, TAU); }, lin(0, 280, 0, 560, FIM ? [[0, '#2a4a2a'], [1, '#1a2a1a']] : [[0, '#3aa040'], [1, '#2a7a2a']]), { dir: 30, group: 'copa', maxR: 14 });
  for (let k = 0; k < 8; k++) R.fill(Rc(1330 + k * 40, 640, 10, 90), '#6a4a2a', { dir: 90, group: 'cur' + k, maxR: 2 });
  for (let k = 0; k < 30; k++) R.fill(El(470 + k * 27, 735 + (k % 2) * 6, 14, 10), ['#e04a6a', '#f0c030', '#ffffff', '#c04ac0'][k % 4], { dir: 0, group: 'flor' + (k % 4), maxR: 3 });   // canteiro na frente da varanda
  [[300, 1000], [1350, 960], [520, 1150], [1200, 1180]].forEach(([x, y], k) => R.fill(El(x, y, 70, 26), FIM ? '#3a4a1a' : '#5ab840', { dir: 0, group: 'moita' + k, maxR: 5 }));
  R.fill(P([[760, VH], [1040, VH], [880, 720], [840, 720]]), lin(0, 720, 0, VH, [[0, '#d8b080'], [1, '#a07a4a']]), { dir: 90, fallback: 90, group: 'estrada', maxR: 12 });
}
function textoPlate(str, cor) { const R = new Ref(1000, 260, 1); R.text(str, 500, 190, `italic 600 120px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }
let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); drawSede(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: FIM ? 83 : 61 }).data()), tex: E.texture(R.ctx.canvas) };
  if (!FIM) { const t = textoPlate('posse exclusiva', '#fff6dc'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 17, app: x => x / 1000 * 1.2 }).data()) }; }
  window.DUR = +(q.get('dur') || 10.6); return frame;
}
function frame(t) {
  E.begin();
  const tp = +(q.get('tp') || 8.2), k = ss(seg(t, 0, FIM ? 6 : 10.5));
  const C = FIM ? { x: lerp(860, 860, k), y: lerp(700, 660, k), zoom: lerp(1.05, 1.16, k) } : { x: lerp(850, 690, k), y: lerp(720, 660, k), zoom: lerp(1.0, 1.42, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  for (let i = 0; i < 14; i++) { const ph = (t * .09 + i / 14) % 1, x = 120 + i * 110 + Math.sin(t * .7 + i) * 20, y = FIM ? 820 - ph * 80 : 420 + Math.sin(t + i) * 30;
    dyn.push({ x, y, ang: ph * 6, len: 8, wid: 6, c: hex(FIM ? '#ffe070' : '#ffffff'), type: DAB, seed: 700 + i, alpha: FIM ? .7 * Math.abs(Math.sin(t * 2 + i)) : .45, hgt: .6 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!FIM && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 40, 560], grey: 0, appear: tp, appDur: 1.0, alpha: 1 });
  E.finish(FIM ? { expo: .84, sat: 1.0, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .7, .45], gain: [1.12, .84, .66] }
               : { expo: 1.04, sat: 1.15, contrast: 1.05, vig: .2, spec: .26, light: [-.6, -.5, .7] });
}
