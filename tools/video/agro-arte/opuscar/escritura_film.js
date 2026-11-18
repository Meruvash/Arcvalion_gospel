// "Comprou a terra e não é dono?" — sítio colorido ao entardecer, porteira aberta e placa "VENDIDO" na cerca; "registro"
// a espátula (fala 2). ?cena=fim: o mesmo sítio no fim de tarde (fala 9). Motor impasto do Lemo-Opuscar (MIT). 1080x1080.
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
function drawSitio(R) {
  R.fill(Rc(0, 0, VW, 560), lin(0, 0, 0, 560, [[0, '#3a6ad0'], [.5, '#f0a0c0'], [1, '#ffd08a']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  R.fill(El(300, 480, 110, 110), lin(0, 370, 0, 590, [[0, '#fff2c0'], [1, '#ffb050']]), { dir: 0, group: 'sol', maxR: 16 });
  [[700, 170, 170], [1250, 120, 200], [1550, 260, 120]].forEach(([x, y, w], k) => R.fill(c => { c.ellipse(x, y, w, w * .24, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .5, w * .18, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#ffe4f0'], [1, '#f0a0a0']]), { dir: -3, fallback: -3, group: 'nuvem' + k, maxR: 18 }));
  R.fill(c => { c.moveTo(0, 560); c.quadraticCurveTo(400, 490, 850, 535); c.quadraticCurveTo(1300, 490, VW, 540); c.lineTo(VW, 600); c.lineTo(0, 600); c.closePath(); }, '#3a7a4a', { dir: 0, group: 'morro', maxR: 14 });
  R.fill(Rc(0, 590, VW, VH - 590), lin(0, 590, 0, VH, [[0, '#8ad050'], [1, '#3a8a2a']]), { dir: 75, fallback: 75, group: 'pasto', maxR: 28, jit: .1 });
  // horta e pomar coloridos à direita, casinha azul com varanda
  for (let r = 0; r < 6; r++) R.fill(Rc(1100, 640 + r * 40, 520, 22), ['#e05a3a', '#f0c030', '#7ac040', '#c04a8a', '#40a0c0', '#f08a30'][r], { dir: 0, group: 'horta' + r, maxR: 6 });
  R.fill(Rc(820, 470, 220, 130), '#5aa0d8', { dir: 90, group: 'casa', maxR: 6 }); R.fill(P([[806, 472], [930, 410], [1054, 472]]), '#c0402a', { dir: 20, group: 'casa', maxR: 4 });
  R.fill(Rc(860, 530, 40, 70), '#f6efe0', { dir: 90, group: 'porta', maxR: 3 }); R.fill(Rc(940, 520, 60, 36), '#fff2c0', { dir: 90, group: 'janela', maxR: 3 });
  [[620, 520, 90], [1500, 500, 110]].forEach(([x, y, w], k) => { R.fill(P([[x - 8, 600], [x - 4, y + 40], [x + 4, y + 40], [x + 8, 600]]), '#5a3a24', { dir: 90, group: 'tronco' + k, maxR: 5 });
    R.fill(c => { c.ellipse(x, y, w, w * .8, 0, 0, TAU); }, lin(0, y - w, 0, y + w, [[0, k ? '#ffd040' : '#ff80b0'], [1, k ? '#e0a020' : '#d04a80']]), { dir: 20, group: 'copa' + k, maxR: 14 }); });   // ipê e paineira
  // estrada que entra pela porteira aberta; cerca com a placa VENDIDO
  R.fill(P([[700, VH], [940, VH], [900, 600], [880, 600]]), lin(0, 600, 0, VH, [[0, '#e0b070'], [1, '#c08a4a']]), { dir: 90, fallback: 90, group: 'estrada', maxR: 12 });
  for (let k = 0; k < 12; k++) { const x = 40 + k * 140; if (x > 600 && x < 1000) continue; R.fill(Rc(x, 960, 18, 200), '#6a4426', { dir: 90, group: 'mour' + k, maxR: 4 }); }
  [1000, 1050].forEach((y, k) => { R.line(c => { c.moveTo(0, y); c.lineTo(620, y); c.moveTo(1010, y); c.lineTo(VW, y); }, '#4a3a2a', 4, { group: 'arame' + k, maxR: 2 }); });
  R.fill(Rc(600, 940, 22, 230), '#5a3a20', { dir: 90, group: 'porteira', maxR: 4 }); R.fill(Rc(1000, 940, 22, 230), '#5a3a20', { dir: 90, group: 'porteira', maxR: 4 });
  for (let k = 0; k < 4; k++) R.fill(P([[1022, 970 + k * 44], [1200, 1010 + k * 44], [1200, 1026 + k * 44], [1022, 986 + k * 44]]), '#8a6a44', { dir: 10, group: 'folha', maxR: 3 });   // folha aberta
  R.fill(Rc(330, 800, 300, 110), '#f6efe0', { dir: 0, group: 'placa', maxR: 4 }); R.fill(Rc(470, 900, 20, 160), '#5a3a20', { dir: 90, group: 'placa', maxR: 3 });
  R.text('VENDIDO', 480, 880, '900 64px Georgia, serif', '#b0281a', { dir: 0, group: 'placa_t', maxR: 3 });
}
function textoPlate(str, cor) { const R = new Ref(1000, 260, 1); R.text(str, 500, 190, `italic 600 180px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }
let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); drawSitio(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 41 }).data()), tex: E.texture(R.ctx.canvas) };
  if (!FIM) { const t = textoPlate('registro', '#fff6dc'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 11, app: x => x / 1000 * 1.2 }).data()) }; }
  window.DUR = +(q.get('dur') || 10.5); return frame;
}
function frame(t) {
  E.begin();
  const tp = +(q.get('tp') || 8.8), k = ss(seg(t, 0, FIM ? 4 : 10));
  const C = FIM ? { x: lerp(860, 820, k), y: lerp(720, 700, k), zoom: lerp(1.15, 1.05, k) } : { x: lerp(800, 840, k), y: lerp(760, 700, k), zoom: lerp(1.0, 1.18, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  for (let i = 0; i < 14; i++) { const ph = (t * .1 + i / 14) % 1, x = 600 + Math.sin(i * 4.1) * 80 + ph * 40, y = 440 + ph * 400; dyn.push({ x, y, ang: ph * 6, len: 9, wid: 7, c: hex('#ff80b0'), type: DAB, seed: 600 + i, alpha: .8, hgt: .6 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!FIM && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 40, 40], grey: 0, appear: tp, appDur: 1.2, alpha: 1 });
  E.finish(FIM ? { expo: .8, sat: .98, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .7, .45], gain: [1.12, .84, .66] }
               : { expo: 1.04, sat: 1.15, contrast: 1.06, vig: .22, spec: .26, light: [-.6, -.5, .7] });
}
