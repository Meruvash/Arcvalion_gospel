// "O banco toma o seu sítio?" — sítio pequeno de manhã, a família colhendo feijão e milho; "impenhorável" a espátula
// (fala 2). ?cena=porteira: a porteira fechada do sítio no fim de tarde (fala 9). Motor impasto do Lemo-Opuscar (MIT).
import { Impasto, Strokes, DAB, hex } from './engine/impasto.js';
import { Ref, paintRef } from './engine/plate.js';
const V = 1080, TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const seg = (t, a, b) => clamp((t - a) / (b - a)), lerp = (a, b, k) => a + (b - a) * k;
const P = pts => c => { c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]); c.closePath(); };
const El = (x, y, rx, ry, r = 0) => c => c.ellipse(x, y, rx, ry, r, 0, TAU);
const Rc = (x, y, w, h) => c => c.rect(x, y, w, h);
const lin = (x0, y0, x1, y1, st) => c => { const g = c.createLinearGradient(x0, y0, x1, y1); st.forEach(([o, k]) => g.addColorStop(o, k)); return g; };
const q = new URLSearchParams(location.search), PORT = q.get('cena') === 'porteira';
const SERIF = '"News", Georgia, serif', VW = 1700, VH = 1300;
function pessoa(R, x, y, s, roupa, chapeu, g, curva = 0) {   // figura de lavrador, de corpo inclinado na colheita
  R.fill(P([[x - 22 * s, y], [x - 18 * s + curva, y - 90 * s], [x + 18 * s + curva, y - 90 * s], [x + 22 * s, y]]), roupa, { dir: 90, group: g + 'c', maxR: 4 });
  R.fill(El(x + curva * 1.3, y - 104 * s, 14 * s, 15 * s), '#8a5a3a', { dir: 0, group: g + 'r', maxR: 3 });
  if (chapeu) R.fill(El(x + curva * 1.3, y - 116 * s, 30 * s, 8 * s), '#e8c870', { dir: 0, group: g + 'h', maxR: 3 });
  R.fill(P([[x - 14 * s, y], [x - 10 * s, y + 40 * s], [x - 2 * s, y + 40 * s], [x - 2 * s, y]]), '#3a3a5a', { dir: 90, group: g + 'p', maxR: 3 });
  R.fill(P([[x + 2 * s, y], [x + 2 * s, y + 40 * s], [x + 10 * s, y + 40 * s], [x + 14 * s, y]]), '#3a3a5a', { dir: 90, group: g + 'q', maxR: 3 });
}
function drawSitio(R) {
  R.fill(Rc(0, 0, VW, 520), lin(0, 0, 0, 520, [[0, '#2a7ae0'], [.7, '#8ac8f0'], [1, '#e8f4f0']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  R.fill(El(1380, 150, 80, 80), lin(0, 70, 0, 230, [[0, '#fffbe0'], [1, '#ffe080']]), { dir: 0, group: 'sol', maxR: 14 });
  [[420, 140, 160], [900, 90, 190]].forEach(([x, y, w], k) => R.fill(c => { c.ellipse(x, y, w, w * .26, 0, 0, TAU); c.ellipse(x + w * .45, y - 14, w * .45, w * .22, 0, 0, TAU); }, '#ffffff', { dir: -3, fallback: -3, group: 'nuvem' + k, maxR: 18 }));
  R.fill(c => { c.moveTo(0, 500); c.quadraticCurveTo(300, 380, 650, 470); c.quadraticCurveTo(1000, 360, 1350, 450); c.quadraticCurveTo(1550, 400, VW, 460); c.lineTo(VW, 560); c.lineTo(0, 560); c.closePath(); }, lin(0, 380, 0, 560, [[0, '#2a6a6a'], [1, '#3a8a4a']]), { dir: 0, group: 'serra', maxR: 14 });
  R.fill(Rc(0, 540, VW, VH - 540), lin(0, 540, 0, VH, [[0, '#9ad850'], [1, '#4a9a2a']]), { dir: 70, fallback: 70, group: 'pasto', maxR: 28, jit: .1 });
  // casinha branca de janelas verdes, telhado de barro; bananeiras
  R.fill(Rc(980, 440, 220, 120), '#f6f0e0', { dir: 90, group: 'casa', maxR: 6 }); R.fill(P([[962, 444], [1090, 380], [1218, 444]]), '#d0602a', { dir: 20, group: 'telha', maxR: 4 });
  [[1010, 470], [1130, 470]].forEach(([x, y], k) => R.fill(Rc(x, y, 42, 40), '#2a9a5a', { dir: 90, group: 'jan' + k, maxR: 3 })); R.fill(Rc(1072, 480, 36, 80), '#2a7a4a', { dir: 90, group: 'porta', maxR: 3 });
  [[1260, 470], [1330, 500], [920, 480]].forEach(([x, y], k) => { R.fill(Rc(x - 6, y, 12, 90), '#6a8a3a', { dir: 90, group: 'bt' + k, maxR: 3 });
    for (let f = 0; f < 5; f++) R.fill(El(x + Math.cos(f * 1.3) * 40, y - 10 + Math.sin(f * 1.3) * 18, 50, 12, f * 1.3), '#4ab03a', { dir: f * 70, group: 'bf' + k + f, maxR: 4 }); });
  // milharal ao fundo e leiras de feijão em primeiro plano
  for (let k = 0; k < 22; k++) R.fill(Rc(300 + k * 26, 510 + (k % 3) * 6, 8, 70), '#c8c040', { dir: 90, group: 'milho' + (k % 6), maxR: 3 });
  for (let r = 0; r < 18; r++) { const vx = 820, vy = 600, a0 = -60 + r * 120, a1 = a0 + 120;   // leiras em perspectiva, abrindo até o primeiro plano
    R.fill(P([[vx + (a0 - 1020) * .04, vy], [vx + (a1 - 1020) * .04, vy], [vx + (a1 - 1020) * 1.1, VH], [vx + (a0 - 1020) * 1.1, VH]]), r % 2 ? '#2a8a2a' : '#6a4424', { dir: 90, group: 'leira' + r, maxR: 8 }); }
  // a família: pai de chapéu, mãe de vestido vermelho, filho com o cesto
  pessoa(R, 560, 860, 1.3, '#2a5aa0', true, 'pai', 22);
  R.line(c => { c.moveTo(600, 760); c.lineTo(660, 900); }, '#5a3a20', 6, { group: 'enxada', maxR: 2 }); R.fill(Rc(648, 892, 34, 12), '#8a8a8a', { dir: 0, group: 'enxadaf', maxR: 2 });
  pessoa(R, 800, 830, 1.15, '#c0302a', true, 'mae', 16);
  pessoa(R, 1000, 820, .9, '#f0b020', false, 'filho', 0);
  R.fill(c => { c.ellipse(1050, 830, 34, 22, 0, 0, TAU); }, '#a8783a', { dir: 0, group: 'cesto', maxR: 4 });
  R.fill(El(1050, 814, 28, 9), '#7a3a20', { dir: 0, group: 'feijao', maxR: 3 });
  [[300, 980], [1250, 1000], [420, 1150], [1150, 1160]].forEach(([x, y], k) => R.fill(El(x, y, 60, 26), k % 2 ? '#3aa03a' : '#58b840', { dir: 0, group: 'pe' + k, maxR: 5 }));   // pés de feijão
}
function drawPorteira(R) {   // a porteira fechada no fim de tarde, o sítio ao fundo
  R.fill(Rc(0, 0, VW, 640), lin(0, 0, 0, 640, [[0, '#3a3a8a'], [.5, '#e07a6a'], [1, '#ffc070']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07 });
  R.fill(El(1250, 560, 120, 120), lin(0, 440, 0, 680, [[0, '#fff0c0'], [1, '#ff9040']]), { dir: 0, group: 'sol', maxR: 16 });
  R.fill(c => { c.moveTo(0, 620); c.quadraticCurveTo(500, 540, 900, 600); c.quadraticCurveTo(1300, 560, VW, 610); c.lineTo(VW, 700); c.lineTo(0, 700); c.closePath(); }, '#4a3a5a', { dir: 0, group: 'serra', maxR: 14 });
  R.fill(Rc(0, 680, VW, VH - 680), lin(0, 680, 0, VH, [[0, '#8a7a3a'], [1, '#3a3a1a']]), { dir: 70, fallback: 70, group: 'chao', maxR: 26, jit: .1 });
  R.fill(Rc(380, 600, 120, 80), '#f0d8b0', { dir: 90, group: 'casa', maxR: 5 }); R.fill(P([[370, 602], [440, 560], [510, 602]]), '#8a3a2a', { dir: 20, group: 'telha', maxR: 4 });
  R.fill(Rc(470, 620, 24, 22), '#ffd070', { dir: 0, group: 'luz', maxR: 3 });
  R.fill(P([[700, VH], [1000, VH], [880, 690], [860, 690]]), lin(0, 690, 0, VH, [[0, '#c09060'], [1, '#7a5a3a']]), { dir: 90, fallback: 90, group: 'estrada', maxR: 12 });
  // porteira de cinco tábuas com a diagonal, fechada
  R.fill(Rc(330, 760, 40, 420), '#3a2414', { dir: 90, group: 'mourao1', maxR: 5 }); R.fill(Rc(1330, 760, 40, 420), '#3a2414', { dir: 90, group: 'mourao2', maxR: 5 });
  for (let k = 0; k < 5; k++) R.fill(Rc(370, 800 + k * 70, 960, 28), k % 2 ? '#8a6a3a' : '#a07a44', { dir: 0, group: 'tab' + k, maxR: 4 });
  R.fill(P([[380, 1110], [410, 1130], [1330, 800], [1300, 780]]), '#9a7440', { dir: -18, group: 'diag', maxR: 4 });
  R.fill(Rc(1290, 870, 70, 30), '#5a5a5a', { dir: 0, group: 'tranca', maxR: 3 });
}
function textoPlate(str, cor) { const R = new Ref(1000, 260, 1); R.text(str, 500, 190, `italic 600 128px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }
let E, dyn, PL, TX;
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(2048);
  const R = new Ref(VW, VH, 1); PORT ? drawPorteira(R) : drawSitio(R);
  PL = { b: E.batch(paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: PORT ? 77 : 53 }).data()), tex: E.texture(R.ctx.canvas) };
  if (!PORT) { const t = textoPlate('impenhorável', '#fff6dc'); TX = { b: E.batch(paintRef(t, { R: [16, 8, 4], T: 10, seed: 13, app: x => x / 1000 * 1.2 }).data()) }; }
  window.DUR = +(q.get('dur') || 11.5); return frame;
}
function frame(t) {
  E.begin();
  const tp = +(q.get('tp') || 9.2), k = ss(seg(t, 0, PORT ? 5.5 : 11));
  const C = PORT ? { x: lerp(850, 850, k), y: lerp(800, 760, k), zoom: lerp(1.0, 1.12, k) } : { x: lerp(820, 790, k), y: lerp(750, 730, k), zoom: lerp(1.0, 1.16, k) };
  E.under(PL.tex, VW, VH, { t, cam: C, grey: 0 }); E.draw(PL.b, { t, cam: C, grey: 0 });
  for (let i = 0; i < 16; i++) { const ph = (t * .08 + i / 16) % 1, x = 200 + i * 90 + Math.sin(t + i) * 20, y = PORT ? 760 - ph * 60 : 560 - ph * 30;   // capim balançando / vaga-lumes
    dyn.push({ x, y, ang: ph * 6, len: 8, wid: 6, c: hex(PORT ? '#ffe070' : '#ffffff'), type: DAB, seed: 900 + i, alpha: PORT ? .7 * Math.abs(Math.sin(t * 2 + i)) : .5, hgt: .6 }); }
  E.drawNow(dyn.data(), { t, cam: C, grey: 0, run: 0 }); dyn.clear();
  if (!PORT && t > tp) E.draw(TX.b, { t, cam: { x: V / 2, y: V / 2, zoom: 1 }, M: [1, 0, 0, 1, 40, 300], grey: 0, appear: tp, appDur: 1.0, alpha: 1 });
  E.finish(PORT ? { expo: .82, sat: 1.0, contrast: 1.1, vig: .45, spec: .34, light: [.85, -.3, .45], lightCol: [1, .7, .45], gain: [1.12, .84, .66] }
                : { expo: 1.05, sat: 1.18, contrast: 1.05, vig: .2, spec: .26, light: [-.6, -.5, .7] });
}
