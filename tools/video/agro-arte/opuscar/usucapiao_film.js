// "O caseiro e o vizinho" — cenas em pintura a óleo com espátula (motor impasto do Lemo-Opuscar, MIT).
// ?cena=sede (falas 1 e 2; "POSSE" pintado a espátula) | sede_fim (fala 9, fim de tarde). Tudo pintado em código. 1080x1080.
import { Impasto, Strokes, KNIFE, DAB, hex } from './engine/impasto.js';
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
const q = new URLSearchParams(location.search), CENA = q.get('cena') || 'sede';
const SERIF = '"News", Georgia, serif';
const VW = 1700, VH = 1300;

function casa(R, x, y, w, h, parede, telhado, id) {
  R.fill(P([[x - 16, y], [x + w / 2, y - h * .55], [x + w + 16, y]]), telhado, { dir: 20, group: 'tel' + id, maxR: 10 });
  R.fill(Rc(x, y, w, h), parede, { dir: 90, group: 'par' + id, maxR: 14 });
}
function drawSede(R) {
  R.fill(Rc(0, 0, VW, 560), lin(0, 0, 0, 560, [[0, '#1f66d0'], [.6, '#62acee'], [1, '#d2ecf6']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  const nuvem = (x, y, w) => R.fill(c => { c.ellipse(x, y, w, w * .28, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .5, w * .2, 0, 0, TAU); c.ellipse(x + w * .5, y + 12, w * .45, w * .2, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#ffffff'], [1, '#e4ecf4']]), { dir: -3, fallback: -3, group: 'ceu', maxR: 20 });
  nuvem(380, 150, 140); nuvem(1100, 110, 170); nuvem(1500, 240, 110);
  R.fill(c => { c.moveTo(0, 560); c.quadraticCurveTo(500, 480, 900, 530); c.quadraticCurveTo(1300, 470, VW, 540); c.lineTo(VW, 620); c.lineTo(0, 620); c.closePath(); }, '#3f8a4a', { dir: 0, group: 'morro', maxR: 14 });
  // lavoura em faixas atrás e pasto na frente
  const FX = ['#7cc23e', '#2f9e44', '#f0c22a', '#a6d84a'];
  [[580, 640], [640, 720]].forEach(([y0, y1], i) => R.fill(Rc(0, y0, VW, y1 - y0), FX[i], { dir: 2, fallback: 2, group: 'faixa' + i, maxR: 14 }));
  R.fill(Rc(0, 720, VW, VH - 720), lin(0, 720, 0, VH, [[0, '#6cbc3a'], [1, '#2f7a2e']]), { dir: 75, fallback: 75, group: 'pasto', maxR: 28, jit: .1 });
  // caminho de terra até a porteira, mangueira e gado no pasto
  R.fill(P([[760, 1300], [960, 1300], [900, 800], [840, 800]]), lin(0, 800, 0, 1300, [[0, '#d8b878'], [1, '#c09a58']]), { dir: 90, fallback: 90, group: 'caminho', maxR: 14 });
  R.fill(c => { c.ellipse(980, 600, 130, 100, 0, 0, TAU); c.ellipse(920, 640, 90, 70, 0, 0, TAU); c.ellipse(1050, 650, 90, 70, 0, 0, TAU); }, lin(860, 500, 1100, 720, [[0, '#2f7a32'], [1, '#1e5a26']]), { dir: 30, fallback: 30, group: 'mangueira', maxR: 14 });
  R.fill(P([[968, 790], [975, 680], [990, 680], [996, 790]]), '#5a3a24', { dir: 90, group: 'tronco2', maxR: 5 });
  [[1180, 900, 1], [1330, 940, 1.15], [1480, 910, .95], [560, 930, 1.05]].forEach(([x, y, s2], k) => {
    R.fill(El(x, y, 60 * s2, 30 * s2), k % 2 ? '#f4efe4' : '#8a5a3a', { dir: 0, group: 'boi' + k, maxR: 6 });
    R.fill(El(x + 58 * s2, y - 10 * s2, 20 * s2, 14 * s2), k % 2 ? '#e8e2d4' : '#7a4a30', { dir: 0, group: 'boi' + k, maxR: 4 });
    [-36, -12, 14, 38].forEach((dx, j) => R.fill(Rc(x + dx * s2, y + 22 * s2, 7 * s2, 28 * s2), '#3a2a20', { dir: 90, group: 'boi' + k, maxR: 2 })); });
  // sede: casa branca grande com telhado vermelho e varanda
  casa(R, 260, 600, 420, 190, '#fbf6ea', '#c8402a', 'sede');
  for (let k = 0; k < 6; k++) R.fill(Rc(285 + k * 66, 650, 30, 60), '#2f5a9a', { dir: 90, group: 'jan' + k, maxR: 4 });
  R.fill(Rc(260, 760, 420, 30), '#8a5a34', { dir: 0, group: 'varanda', maxR: 6 });
  // casinha do caseiro: amarela, janela azul, à direita
  casa(R, 1080, 690, 200, 120, '#f2cf6a', '#a8402a', 'cas');
  R.fill(Rc(1120, 730, 40, 40), '#3a7ad0', { dir: 90, group: 'jcas', maxR: 4 }); R.fill(Rc(1200, 740, 44, 70), '#6a3a1e', { dir: 90, group: 'pcas', maxR: 4 });
  // varal com chapéu e roupa
  R.line(c => { c.moveTo(1300, 720); c.lineTo(1480, 728); }, '#5a4a3a', 4, { group: 'varal', maxR: 2 });
  [[1320, 728, '#d04030'], [1370, 730, '#3a7ad0'], [1420, 732, '#fff6e8']].forEach(([x, y, c2], k) => R.fill(Rc(x, y, 34, 46), c2, { dir: 90, group: 'roupa' + k, maxR: 4 }));
  R.fill(El(1460, 742, 30, 9), '#e8c060', { dir: 0, group: 'chapeu', maxR: 4 }); R.fill(c => c.ellipse(1460, 736, 16, 12, 0, Math.PI, TAU), '#d8a840', { dir: 0, group: 'chapeu', maxR: 3 });
  // ipê-roxo à esquerda
  R.fill(P([[120, 860], [140, 560], [158, 560], [178, 860]]), '#5a3a24', { dir: 90, group: 'tronco', maxR: 8 });
  R.fill(c => { c.ellipse(150, 440, 190, 140, 0, 0, TAU); c.ellipse(60, 520, 110, 80, 0, 0, TAU); c.ellipse(260, 520, 100, 80, 0, 0, TAU); }, lin(0, 300, 340, 620, [[0, '#e47ad8'], [.6, '#b04ab8'], [1, '#8a3098']]), { dir: 20, fallback: 20, group: 'ipe', maxR: 18, detail: 1.4 });
  // cerca de arame em primeiro plano
  for (let k = 0; k < 13; k++) R.fill(P([[40 + k * 130, 1180], [52 + k * 130, 1000], [64 + k * 130, 1000], [70 + k * 130, 1180]]), '#6a4426', { dir: 90, group: 'mour' + k, maxR: 5 });
  [1040, 1090, 1140].forEach((y, k) => R.line(c => { c.moveTo(0, y); c.lineTo(VW, y - 8); }, '#3a3a3a', 3, { group: 'arame' + k, maxR: 2 }));
}
function textoPlate(str, cor) { const R = new Ref(820, 260, 1); R.text(str, 410, 210, `italic 600 230px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }

let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); drawSede(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 13 }).data()), tex: E.texture(R.ctx.canvas) };
  if (CENA === 'sede') { const t = textoPlate('posse', '#fff6dc'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 5, app: x => x / 820 * .6 }).data()) }; }
  window.DUR = +(q.get('dur') || 9.6);
  return frame;
}
function frame(t) {
  E.begin();
  const fim = CENA === 'sede_fim', tp = +(q.get('tp') || 8.35);
  const k = ss(seg(t, 0, fim ? 4 : 6.2));
  const C = fim ? { x: lerp(1000, 900, k), y: lerp(720, 700, k), zoom: lerp(1.2, 1.08, k) } : { x: lerp(800, 1180, k), y: lerp(660, 740, k), zoom: lerp(.98, 1.32, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  // roupa no varal balançando (pinceladas leves por cima)
  for (let i = 0; i < 3; i++) { const x = 1337 + i * 50, y = 760 + Math.sin(t * 2.2 + i) * 4; dyn.push({ x, y, ang: Math.PI / 2 + Math.sin(t * 2 + i) * .08, len: 40, wid: 30, c: hex(['#d04030', '#3a7ad0', '#fff6e8'][i]), type: KNIFE, seed: 90 + i, alpha: .55, hgt: .7 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!fim && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 130, 60], grey: 0, appear: tp, appDur: .8, alpha: 1 });
  E.finish(fim ? { expo: .8, sat: .98, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .74, .5], gain: [1.1, .86, .7] }
               : { expo: 1.04, sat: 1.12, contrast: 1.05, vig: .22, spec: .26, light: [-.6, -.55, .7] });
}
