// "O gado do vizinho comeu a sua roça" — cenas em pintura a óleo com espátula (motor impasto do Lemo-Opuscar, MIT).
// ?cena=roca (falas 1 e 2; "culpa" a espátula) | roca_fim (fala 9, fim de tarde, cerca refeita). Tudo pintado em código. 1080x1080.
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
const q = new URLSearchParams(location.search), CENA = q.get('cena') || 'roca', FIM = CENA === 'roca_fim';
const SERIF = '"News", Georgia, serif';
const VW = 1700, VH = 1300, DIV = 760;               // a cerca da divisa corre na diagonal; à esquerda o pasto do vizinho, à direita a sua roça

function boi(R, x, y, s, k, v = 1) {               // boi malhado (branco com manchas pretas), de lado, cabeça baixa comendo
  const g = { dir: 0, group: 'boi' + k, maxR: 5 };
  [-48, -26, 30, 50].forEach(dx => R.fill(P([[x + dx * s * v - 6 * s, y + 18 * s], [x + dx * s * v + 6 * s, y + 18 * s], [x + dx * s * v + 5 * s, y + 66 * s], [x + dx * s * v - 5 * s, y + 66 * s]]), '#2a2420', { dir: 90, group: 'boi' + k, maxR: 2 }));
  R.fill(c => { c.ellipse(x, y, 82 * s, 36 * s, 0, 0, TAU); c.ellipse(x - 50 * s * v, y - 6 * s, 34 * s, 34 * s, 0, 0, TAU); }, '#f6f2ea', g);   // corpo e anca
  R.fill(El(x - 10 * s * v, y - 10 * s, 26 * s, 17 * s, .3 * v), '#1e1a18', g); R.fill(El(x + 36 * s * v, y + 8 * s, 18 * s, 12 * s, -.4 * v), '#1e1a18', g);
  R.fill(P([[x + 70 * s * v, y - 14 * s], [x + 104 * s * v, y + 24 * s], [x + 122 * s * v, y + 52 * s], [x + 100 * s * v, y + 60 * s], [x + 76 * s * v, y + 20 * s]]), '#efe8de', g);   // pescoço e cabeça baixa
  R.fill(El(x + 112 * s * v, y + 58 * s, 13 * s, 9 * s), '#d8a8a0', g);                                             // focinho
  R.line(c => { c.moveTo(x + 96 * s * v, y + 22 * s); c.quadraticCurveTo(x + 104 * s * v, y + 4 * s, x + 118 * s * v, y + 2 * s); }, '#e8dcc0', 4 * s, { group: 'boi' + k, maxR: 2 });   // chifre
  R.line(c => { c.moveTo(x - 80 * s * v, y - 6 * s); c.quadraticCurveTo(x - 92 * s * v, y + 20 * s, x - 86 * s * v, y + 48 * s); }, '#2a2420', 3 * s, { group: 'boi' + k, maxR: 2 });   // rabo
}
function drawRoca(R) {
  R.fill(Rc(0, 0, VW, 540), lin(0, 0, 0, 540, [[0, '#2a72d8'], [.6, '#6cb4f0'], [1, '#e2f2f6']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  const nuvem = (x, y, w) => R.fill(c => { c.ellipse(x, y, w, w * .28, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .5, w * .2, 0, 0, TAU); c.ellipse(x + w * .5, y + 12, w * .45, w * .2, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#ffffff'], [1, '#e6eef4']]), { dir: -3, fallback: -3, group: 'ceu', maxR: 20 });
  nuvem(520, 170, 150); nuvem(1250, 120, 180);
  R.fill(c => { c.moveTo(0, 540); c.quadraticCurveTo(600, 470, 1000, 520); c.quadraticCurveTo(1400, 480, VW, 530); c.lineTo(VW, 600); c.lineTo(0, 600); c.closePath(); }, '#4a8f4e', { dir: 0, group: 'morro', maxR: 14 });
  // pasto do vizinho (esquerda) e a sua roça de milho (direita), separados pela cerca em diagonal
  R.fill(P([[0, 590], [DIV + 120, 590], [DIV - 160, VH], [0, VH]]), lin(0, 590, 0, VH, [[0, '#9ccc5a'], [1, '#5a9a34']]), { dir: 75, fallback: 75, group: 'pasto', maxR: 28, jit: .1 });
  R.fill(P([[DIV + 120, 590], [VW, 590], [VW, VH], [DIV - 160, VH]]), lin(0, 590, 0, VH, [[0, '#4aa83a'], [1, '#1f6e26']]), { dir: 90, fallback: 90, group: 'roca', maxR: 22 });
  for (let r = 0; r < 26; r++) {                                   // pés de milho em fileiras, com pendões amarelos
    const yb = 620 + r * 26, xs = DIV + 120 - (yb - 590) * (280 / 710) + 30;
    for (let x = xs + (r % 2) * 22; x < VW; x += 46 + r * 1.5) {
      const h = 40 + r * 7; R.fill(P([[x - 3, yb + h * .2], [x, yb - h], [x + 3, yb + h * .2]]), r % 3 ? '#2f8a2a' : '#3fa236', { dir: 90, group: 'milho' + (r % 5), maxR: 3 });
      R.fill(P([[x - 9 - r * .4, yb - h * .35], [x, yb - h * .55], [x + 9 + r * .4, yb - h * .25]]), '#3c9a30', { dir: 30, group: 'folha' + (r % 3), maxR: 3 });
      if ((r + Math.round(x)) % 3 === 0) R.fill(El(x, yb - h, 2 + r * .12, 5 + r * .25), '#e8c84a', { dir: 90, group: 'pendao' + (r % 4), maxR: 2 });
    }
  }
  // ipê-amarelo no pasto do vizinho e a casinha dele ao fundo
  R.fill(Rc(330, 520, 90, 64), '#f4ead2', { dir: 90, group: 'casa', maxR: 6 }); R.fill(P([[318, 522], [375, 488], [432, 522]]), '#a8402a', { dir: 20, group: 'casa', maxR: 4 });
  R.fill(P([[180, 760], [196, 540], [212, 540], [228, 760]]), '#5a3a24', { dir: 90, group: 'tronco', maxR: 8 });
  R.fill(c => { c.ellipse(204, 450, 170, 120, 0, 0, TAU); c.ellipse(110, 520, 100, 70, 0, 0, TAU); c.ellipse(300, 520, 100, 70, 0, 0, TAU); }, lin(0, 330, 360, 600, [[0, '#ffe45a'], [.6, '#f4c21e'], [1, '#d89a10']]), { dir: 20, fallback: 20, group: 'ipe', maxR: 18, detail: 1.4 });
  // a cerca da divisa: moirões e arame; na roça, um trecho caído (cena roca) ou refeito (roca_fim)
  for (let k = 0; k < 11; k++) { const y = 600 + k * 66, x = DIV + 120 - (y - 590) * (280 / 710);
    if (!FIM && k >= 5 && k <= 7) { R.fill(P([[x - 30, y + 40], [x + 40, y + 20], [x + 44, y + 30], [x - 26, y + 52]]), '#6a4426', { dir: 0, group: 'caido' + k, maxR: 4 }); continue; }
    R.fill(P([[x - 7, y + 40], [x - 5, y - 30 - k * 6], [x + 7, y - 30 - k * 6], [x + 9, y + 40]]), '#6a4426', { dir: 90, group: 'mour' + k, maxR: 4 }); }
  [0, 26, 52].forEach((d, j) => R.line(c => { const a = [DIV + 120, 560 + d], b = [DIV - 160, VH - 80 + d * 2]; if (!FIM) { c.moveTo(a[0], a[1]); c.lineTo(lerp(a[0], b[0], .46), lerp(a[1], b[1], .46)); c.moveTo(lerp(a[0], b[0], .74), lerp(a[1], b[1], .74)); c.lineTo(b[0], b[1]); } else { c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); } }, '#3a3a3a', 3, { group: 'arame' + j, maxR: 2 }));
  // o gado: na cena roca, dois bois já dentro do milho pela cerca caída; no fim, todos do lado de lá
  const BOIS = FIM ? [[300, 860, 1.05, -1], [420, 1000, 1.25, 1], [150, 1100, 1.35, 1]] : [[320, 880, 1.05, 1], [860, 940, 1.3, 1], [1120, 860, 1.1, -1], [190, 1080, 1.4, 1]];
  BOIS.forEach(([x, y, s, v], k) => boi(R, x, y, s, k, v));
  if (!FIM) [[980, 1010], [1050, 935]].forEach(([x, y], k) => R.fill(El(x, y + 50, 110, 22), '#7a6a3a', { dir: 0, group: 'pisado' + k, maxR: 4 }));   // milho pisoteado
}
function textoPlate(str, cor) { const R = new Ref(1000, 260, 1); R.text(str, 500, 200, `italic 600 210px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }

let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); drawRoca(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 23 }).data()), tex: E.texture(R.ctx.canvas) };
  if (!FIM) { const t = textoPlate('culpa', '#fff6dc'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 7, app: x => x / 1000 * 1.2 }).data()) }; }
  window.DUR = +(q.get('dur') || 11.1);
  return frame;
}
function frame(t) {
  E.begin();
  const tp = +(q.get('tp') || 9.7), k = ss(seg(t, 0, FIM ? 4 : 9));
  const C = FIM ? { x: lerp(820, 760, k), y: lerp(760, 730, k), zoom: lerp(1.16, 1.05, k) } : { x: lerp(760, 880, k), y: lerp(700, 800, k), zoom: lerp(.98, 1.2, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  // flores do ipê caindo e pendões balançando (pinceladas leves)
  for (let i = 0; i < 12; i++) { const ph = (t * .1 + i / 12) % 1, x = 160 + Math.sin(i * 5.1) * 150 + ph * 50, y = 470 + ph * 360; dyn.push({ x, y, ang: ph * 6, len: 9, wid: 7, c: hex('#f4c21e'), type: DAB, seed: 400 + i, alpha: .8, hgt: .6 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!FIM && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 40, 40], grey: 0, appear: tp, appDur: 1.2, alpha: 1 });
  E.finish(FIM ? { expo: .8, sat: .98, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .74, .5], gain: [1.1, .86, .7] }
               : { expo: 1.04, sat: 1.12, contrast: 1.05, vig: .22, spec: .26, light: [-.6, -.55, .7] });
}
