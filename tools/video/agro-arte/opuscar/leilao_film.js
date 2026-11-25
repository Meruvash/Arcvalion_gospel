// "O banco leiloa a sua fazenda sem juiz?" — fala 2: "alienação fiduciária" pintado a espátula sobre uma fazenda de soja
// madura com silos metálicos ao amanhecer (motor impasto do Lemo-Opuscar, MIT). Tudo pintado em código. 1080x1080.
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
function drawFazenda(R) {
  R.fill(Rc(0, 0, VW, 560), lin(0, 0, 0, 560, [[0, '#f2a65a'], [.45, '#f8cf8a'], [1, '#fdebc4']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  R.fill(El(1180, 470, 120, 120), lin(0, 350, 0, 590, [[0, '#fff3c8'], [1, '#ffd27a']]), { dir: 0, group: 'sol', maxR: 18 });
  [[420, 180, 160], [980, 140, 190], [1460, 230, 120]].forEach(([x, y, w], k) => R.fill(c => { c.ellipse(x, y, w, w * .24, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .5, w * .18, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#fff1dc'], [1, '#f2b880']]), { dir: -3, fallback: -3, group: 'nuvem' + k, maxR: 18 }));
  R.fill(c => { c.moveTo(0, 560); c.quadraticCurveTo(500, 500, 900, 540); c.quadraticCurveTo(1300, 500, VW, 545); c.lineTo(VW, 600); c.lineTo(0, 600); c.closePath(); }, '#6a8a4a', { dir: 0, group: 'morro', maxR: 14 });
  R.fill(Rc(0, 590, VW, VH - 590), lin(0, 590, 0, VH, [[0, '#e8c25a'], [.5, '#d8a63a'], [1, '#b8862a']]), { dir: 90, fallback: 90, group: 'soja', maxR: 26, jit: .1 });
  for (let r = 0; r < 18; r++) { const y = 620 + r * 38; R.line(c => { c.moveTo(0, y + r * 2); c.lineTo(VW, y - r); }, r % 2 ? '#c4922e' : '#f0d070', 3 + r * .3, { group: 'fileira' + (r % 4), maxR: 3 }); }
  // silos metálicos, armazém e a sede com varanda ao fundo
  [[1040, 1], [1150, 1.1], [1270, .95]].forEach(([x, s], k) => { R.fill(Rc(x, 600 - 210 * s, 90 * s, 210 * s), lin(x, 0, x + 90 * s, 0, [[0, '#9aa4b0'], [.5, '#e6ecf2'], [1, '#7a8490']]), { dir: 90, group: 'silo' + k, maxR: 5 });
    R.fill(P([[x - 4, 600 - 210 * s], [x + 45 * s, 600 - 260 * s], [x + 94 * s, 600 - 210 * s]]), '#b8c0c8', { dir: 20, group: 'silo' + k, maxR: 4 }); });
  R.fill(Rc(1380, 470, 220, 130), '#c8ccd0', { dir: 90, group: 'armazem', maxR: 6 }); R.fill(P([[1370, 472], [1490, 420], [1610, 472]]), '#8a949c', { dir: 20, group: 'armazem', maxR: 4 });
  R.fill(Rc(560, 500, 240, 100), '#f6efe0', { dir: 90, group: 'sede', maxR: 6 }); R.fill(P([[548, 502], [680, 440], [812, 502]]), '#a8402a', { dir: 20, group: 'sede', maxR: 4 });
  for (let k = 0; k < 4; k++) R.fill(Rc(584 + k * 56, 528, 26, 40), '#4a6a8a', { dir: 90, group: 'jan' + k, maxR: 3 });
  R.fill(c => { c.ellipse(430, 520, 90, 70, 0, 0, TAU); c.ellipse(380, 550, 60, 45, 0, 0, TAU); }, '#3f6a32', { dir: 30, group: 'arvore', maxR: 10 });
  R.fill(P([[700, VH], [860, VH], [760, 600], [740, 600]]), lin(0, 600, 0, VH, [[0, '#c89a5a'], [1, '#a87a3a']]), { dir: 90, fallback: 90, group: 'estrada', maxR: 12 });
}
function textoPlate(str, cor) { const R = new Ref(1000, 260, 1); R.text(str, 500, 180, `italic 600 108px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }
let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); drawFazenda(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 31 }).data()), tex: E.texture(R.ctx.canvas) };
  const t = textoPlate('alienação fiduciária', '#2b1a10'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 9, app: x => x / 1000 * 1.2 }).data()) };
  window.DUR = +(q.get('dur') || 7.0); return frame;
}
function frame(t) {
  E.begin();
  const tp = +(q.get('tp') || 0.9), k = ss(seg(t, 0, 7));
  const C = FIM ? { x: lerp(980, 900, k), y: lerp(620, 600, k), zoom: lerp(1.2, 1.08, k) } : { x: lerp(860, 900, k), y: lerp(640, 700, k), zoom: lerp(1.0, 1.16, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  for (let i = 0; i < 16; i++) { const ph = (t * .08 + i / 16) % 1, x = 200 + i * 90 + Math.sin(i * 3.1 + t) * 20, y = 700 + ph * 300; dyn.push({ x, y, ang: .3, len: 8, wid: 4, c: hex('#f6d878'), type: DAB, seed: 500 + i, alpha: .6, hgt: .5 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!FIM && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 40, 30], grey: 0, appear: tp, appDur: 1.4, alpha: 1 });
  E.finish(FIM ? { expo: .8, sat: .98, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .7, .45], gain: [1.12, .84, .66] }
               : { expo: 1.03, sat: 1.1, contrast: 1.06, vig: .26, spec: .28, light: [.7, -.4, .6], lightCol: [1, .88, .7] });
}
