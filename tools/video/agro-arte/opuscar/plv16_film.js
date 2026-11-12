// "O relógio zerou" — cenas em pintura a óleo com espátula (motor impasto do Lemo-Opuscar, MIT).
// Três clipes isolados, escolhidos por ?cena=: relogio (fala 1), folhinha (fala 3), mapa (fala 6), fim (fala 9).
// Tudo pintado em código: nenhuma imagem gerada por IA, nenhuma foto. Quadro 1080x1080.
import { Impasto, Strokes, KNIFE, DAB, hex, shade } from './engine/impasto.js';
import { Ref, paintRef } from './engine/plate.js';

const V = 1080, NEVER = 1e6, TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const P = pts => c => { c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]); c.closePath(); };
const El = (x, y, rx, ry, r = 0) => c => c.ellipse(x, y, rx, ry, r, 0, TAU);
const Rc = (x, y, w, h) => c => c.rect(x, y, w, h);
const lin = (x0, y0, x1, y1, st) => c => { const g = c.createLinearGradient(x0, y0, x1, y1); st.forEach(([o, k]) => g.addColorStop(o, k)); return g; };
const rad = (x, y, r0, r1, st) => c => { const g = c.createRadialGradient(x, y, r0, x, y, r1); st.forEach(([o, k]) => g.addColorStop(o, k)); return g; };
const hsh = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const q = new URLSearchParams(location.search), CENA = q.get('cena') || 'relogio';
const SERIF = '"News", Georgia, serif';

// ============ VARANDA DA SEDE (relógio + folhinha + lavoura vista pela abertura) ============
const VW = 1800, VH = 1300, CLK = [520, 440, 165], FOL = [830, 470, 230, 330];
function drawVaranda(R) {
  // céu e lavoura, vistos pela abertura da varanda (x > 1230)
  R.fill(P([[1180, 0], [VW, 0], [VW, 620], [1180, 620]]), lin(0, 0, 0, 620, [[0, '#2a6fd0'], [.55, '#5ea6ea'], [1, '#cfe9f6']]), { dir: -4, fallback: -4, group: 'ceu', maxR: 40, jit: .07, aj: .3 });
  const nuvem = (x, y, w) => R.fill(c => { c.ellipse(x, y, w, w * .3, 0, 0, TAU); c.ellipse(x - w * .5, y + 10, w * .55, w * .22, 0, 0, TAU); c.ellipse(x + w * .55, y + 12, w * .5, w * .2, 0, 0, TAU); }, lin(0, y - 40, 0, y + 30, [[0, '#ffffff'], [1, '#e6eef6']]), { dir: -3, fallback: -3, group: 'ceu', maxR: 22 });
  nuvem(1420, 150, 120); nuvem(1660, 260, 90); nuvem(1330, 360, 70);
  R.fill(P([[1180, 560], [1450, 520], [1800, 545], [1800, 640], [1180, 640]]), '#4f8a9a', { dir: 0, group: 'serra', maxR: 12 });
  const COL = ['#6cc232', '#2f9e44', '#f0c22a', '#a6d84a', '#e5a224', '#3cb860'];
  const ys = [610, 640, 690, 770, 900, 1100];
  for (let b = 0; b < ys.length - 1; b++) R.fill(P([[1180, ys[b]], [VW, ys[b] - 6], [VW, ys[b + 1]], [1180, ys[b + 1] + 4]]), COL[b % COL.length], { dir: 2, fallback: 2, group: 'roca' + b, maxR: 10 + b * 5, jit: .08 });
  // silos e galpão ao longe
  [[1500, 70], [1530, 82], [1560, 70]].forEach(([x, h]) => R.fill(P([[x - 13, 612], [x - 13, 612 - h], [x, 612 - h - 10], [x + 13, 612 - h], [x + 13, 612]]), lin(x - 13, 0, x + 13, 0, [[0, '#9fb4cc'], [.5, '#f2f6fa'], [1, '#7f94ae']]), { dir: 90, group: 'silo' + x, maxR: 5 }));
  R.fill(P([[1360, 612], [1360, 578], [1395, 556], [1430, 578], [1430, 612]]), '#c8321e', { dir: 90, group: 'galpao', maxR: 5 });
  // parede da varanda: reboco caiado em ocre quente, com mancha de sol
  R.fill(P([[0, 0], [1180, 0], [1180, 1100], [0, 1100]]), lin(0, 0, 1180, 1100, [[0, '#d9b47c'], [.5, '#ecd2a0'], [1, '#c99c62']]), { dir: 80, fallback: 80, group: 'parede', maxR: 40, detail: 1.4, aj: .25 });
  R.tint(P([[300, 0], [1180, 0], [1180, 1100], [700, 1100]]), lin(300, 0, 1180, 600, [[0, 'rgba(255,236,190,0)'], [.6, 'rgba(255,236,190,.55)'], [1, 'rgba(255,244,214,.75)']]));
  R.fill(P([[0, 1040], [1180, 1040], [1180, 1100], [0, 1100]]), '#8a5a34', { dir: 0, group: 'rodape', maxR: 10 });
  // esteio de madeira e guarda-corpo
  R.fill(P([[1180, 0], [1238, 0], [1238, 1300], [1180, 1300]]), lin(1180, 0, 1238, 0, [[0, '#6a4024'], [.4, '#a8703c'], [1, '#5a3420']]), { dir: 90, fallback: 90, group: 'esteio', maxR: 14 });
  R.fill(P([[1238, 840], [VW, 840], [VW, 872], [1238, 872]]), '#7a4a26', { dir: 0, group: 'guarda', maxR: 10 });
  for (let k = 0; k < 6; k++) R.fill(Rc(1290 + k * 92, 872, 22, 228), '#6a3e20', { dir: 90, group: 'guarda', maxR: 8 });
  // piso de lajota
  R.fill(P([[0, 1100], [VW, 1100], [VW, VH], [0, VH]]), lin(0, 1100, 0, VH, [[0, '#b8582e'], [1, '#8a3a20']]), { dir: 0, fallback: 0, group: 'piso', maxR: 26, jit: .1 });
  // relógio de parede: aro de madeira, mostrador creme, marcas das horas
  const [cx, cy, r] = CLK;
  R.tint(El(cx + 18, cy + 22, r + 20, r + 20), rad(cx + 18, cy + 22, r - 10, r + 40, [[0, 'rgba(90,60,30,.45)'], [1, 'rgba(90,60,30,0)']]));
  R.fill(El(cx, cy, r, r), lin(cx - r, cy - r, cx + r, cy + r, [[0, '#9a5a2a'], [.5, '#6a3818'], [1, '#4a2410']]), { dir: 'edge', group: 'aro', maxR: 14 });
  R.fill(El(cx, cy, r - 24, r - 24), rad(cx - 40, cy - 50, 10, r, [[0, '#fff8e6'], [1, '#ecdcb6']]), { dir: 'edge', group: 'face', maxR: 18 });
  for (let k = 0; k < 12; k++) { const a = k / 12 * TAU, r1 = r - 34, r2 = r - (k % 3 ? 48 : 60), w = k % 3 ? 5 : 9;
    R.line(c => { c.moveTo(cx + Math.sin(a) * r1, cy - Math.cos(a) * r1); c.lineTo(cx + Math.sin(a) * r2, cy - Math.cos(a) * r2); }, '#2a1a10', w, { dir: 'edge', group: 'face', maxR: 3 }); }
  R.text('12', cx, cy - r + 104, `italic 600 48px ${SERIF}`, '#2a1a10', { group: 'face', maxR: 3 });
  R.text('6', cx, cy + r - 72, `italic 600 42px ${SERIF}`, '#2a1a10', { group: 'face', maxR: 3 });
  R.text('3', cx + r - 88, cy + 15, `italic 600 42px ${SERIF}`, '#2a1a10', { group: 'face', maxR: 3 });
  R.text('9', cx - r + 88, cy + 15, `italic 600 42px ${SERIF}`, '#2a1a10', { group: 'face', maxR: 3 });
  // chapéu de palha pendurado num prego, à esquerda do relógio
  R.fill(El(210, 770, 120, 34), lin(90, 0, 330, 0, [[0, '#c89a48'], [.5, '#f0d07a'], [1, '#b8863a']]), { dir: 0, group: 'aba', maxR: 10 });
  R.fill(c => { c.ellipse(210, 742, 64, 46, 0, Math.PI, TAU); c.lineTo(274, 760); c.lineTo(146, 760); }, lin(150, 0, 270, 0, [[0, '#b8863a'], [.5, '#e8c46a'], [1, '#a87830']]), { dir: 0, group: 'copa', maxR: 8 });
  R.fill(Rc(148, 744, 124, 14), '#5a3418', { dir: 0, group: 'fita', maxR: 4 });
  R.fill(El(210, 690, 6, 6), '#3a2a1a', { group: 'prego', maxR: 2 });
  // folhinha (calendário de parede) do dia 12 de novembro
  const [fx, fy, fw, fh] = FOL;
  R.line(c => { c.moveTo(fx + fw / 2, fy - 50); c.lineTo(fx + 30, fy); c.moveTo(fx + fw / 2, fy - 50); c.lineTo(fx + fw - 30, fy); }, '#5a3a20', 4, { group: 'fio', maxR: 3 });
  R.tint(Rc(fx + 14, fy + 16, fw, fh), 'rgba(90,60,30,.35)');
  R.fill(Rc(fx, fy, fw, fh), '#fbf6ea', { dir: 0, group: 'folha', maxR: 12 });
  R.fill(Rc(fx, fy, fw, 70), '#c3301e', { dir: 0, group: 'folhaTopo', maxR: 8 });
  R.text('NOVEMBRO', fx + fw / 2, fy + 48, `600 34px ${SERIF}`, '#fbf6ea', { group: 'folhaTopo', maxR: 3 });
  R.text('12', fx + fw / 2, fy + 250, `italic 600 190px ${SERIF}`, '#241812', { group: 'folha', maxR: 4 });
  R.text('QUINTA-FEIRA', fx + fw / 2, fy + 305, `600 26px ${SERIF}`, '#5a4a3a', { group: 'folha', maxR: 3 });
}

// ============ MAPA DO BRASIL EM ÓLEO ============
const REG = { N: ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'], NE: ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'], CO: ['DF', 'GO', 'MS', 'MT'] };
const RCOL = { N: '#2f8a3c', NE: '#e0a228', CO: '#7cbf3a', S: '#c4b08c' };
const regiao = uf => Object.keys(REG).find(k => REG[k].includes(uf)) || 'S';
let proj;
function drawMapa(R, M) {
  R.fill(Rc(0, 0, V, V), rad(540, 500, 100, 900, [[0, '#efe1bf'], [1, '#c9b48a']]), { dir: 20, fallback: 20, group: 'fundo', maxR: 40, aj: .3 });
  M.getContext('2d').clearRect(0, 0, V, V);
  proj = d3.geoMercator().fitExtent([[150, 90], [1000, 990]], BR);
  const path = d3.geoPath(proj);
  const m = M.getContext('2d');
  for (const f of BR.features) {
    const uf = f.properties.uf, rg = regiao(uf);
    R.fill(c => d3.geoPath(proj, c)(f), RCOL[rg], { dir: 35, fallback: 35, group: 'uf' + uf, maxR: 22, jit: .1, rule: 'evenodd' });
    m.fillStyle = { N: '#ff0000', NE: '#00ff00', CO: '#0000ff', S: '#000000' }[rg]; m.fill(new Path2D(path(f)));
  }
  for (const f of BR.features) R.line(c => d3.geoPath(proj, c)(f), '#3a2a1a', 3, { dir: 'edge', group: 'borda', maxR: 3 });
}

// ============ TEXTO A ESPÁTULA ============
function textoPlate(str, cor) { const R = new Ref(460, 230, 1); R.text(str, 230, 185, `italic 600 200px ${SERIF}`, cor, { dir: 10, group: 't', maxR: 7 }); return R; }

// ============ montagem ============
let E, dyn, PL = {};
export async function setup(canvas) {
  await document.fonts.load(`italic 600 100px "News"`);
  E = new Impasto(canvas, { W: V, H: V, ss: 2 }); dyn = new Strokes(4096);
  const up = (R, st, w, h) => ({ b: E.batch(st.data()), tex: E.texture(R.ctx.canvas), w, h });
  if (CENA === 'mapa') {
    const R = new Ref(V, V, 1), M = document.createElement('canvas'); M.width = M.height = V; drawMapa(R, M);
    const md = M.getContext('2d').getImageData(0, 0, V, V).data;
    const T0 = { N: +(q.get('n') ?? .4), NE: +(q.get('ne') ?? 1), CO: +(q.get('co') ?? 1.9) };
    const rev = (x, y) => { const i = ((y | 0) * V + (x | 0)) * 4, r = md[i], g = md[i + 1], b = md[i + 2], a = md[i + 3];
      if (a < 128) return -50; if (!r && !g && !b) return NEVER; const k = r > 128 ? 'N' : g > 128 ? 'NE' : 'CO';
      return T0[k] + hsh(x * .37 + y * .11) * .35 + (k === 'N' ? (1080 - x) : k === 'NE' ? (y - 200) : (x - 300)) / 1080 * .5; };
    PL.map = up(R, paintRef(R, { R: [30, 15, 7.5, 3.5], T: 12, seed: 7, rev }), V, V);
    const t30 = textoPlate('30%', '#3a2618'), t25 = textoPlate('25%', '#1e6b2c');
    PL.t30 = up(t30, paintRef(t30, { R: [14, 7, 3.5], T: 10, seed: 3, app: (x) => x / 460 * .6 }), 460, 230);
    PL.t25 = up(t25, paintRef(t25, { R: [14, 7, 3.5], T: 10, seed: 4, app: (x) => x / 460 * .6 }), 460, 230);
  } else {
    const R = new Ref(VW, VH, 1); drawVaranda(R);
    PL.var = up(R, paintRef(R, { R: [40, 20, 10, 5, 2.6], T: 12, seed: 5 }), VW, VH);
  }
  window.DUR = +(q.get('dur') || 7);
  return frame;
}
const plate = (pl, o) => { E.under(pl.tex, pl.w, pl.h, o); E.draw(pl.b, o); };
const flush = o => { if (dyn.n) E.drawNow(dyn.data(), o); dyn.clear(); };

// ponteiros: m em minutos (0..∞, 60 = meio-dia); smear = minutos percorridos no último quadro, para o rastro do giro
function ponteiros(m, smear = 0, k = 1) {
  const [cx, cy] = CLK, n = Math.min(10, 1 + Math.floor(Math.abs(smear) / 6));
  for (let i = n - 1; i >= 0; i--) {
    const mm = m - smear * i / n, al = i ? .22 * (1 - i / n) : 1;
    const am = mm / 60 * TAU, ah = (mm - 60) / 720 * TAU;
    const hand = (a, len, wid, c) => dyn.push({ x: cx + Math.sin(a) * len * .42, y: cy - Math.cos(a) * len * .42, ang: a - Math.PI / 2, len, wid, c, c2: shade(c, .8), type: KNIFE, taper: .85, alpha: al * k, hgt: 1.3, seed: 11 + i });
    hand(ah, 92, 15, hex('#1c120c')); hand(am, 136, 10, hex('#241610'));
  }
  dyn.push({ x: cx, y: cy, len: 20, wid: 20, c: hex('#b8862e'), type: DAB, seed: 3, hgt: 1.4 });
}
const cam = (x, y, z) => ({ x, y, zoom: z });

function frame(t) {
  E.begin();
  if (CENA === 'relogio') {                                   // fala 1: lavoura → relógio; ponteiro chega ao 12, para e volta 12 h
    const k = eio(seg(t, .3, 3.0));
    const C = cam(lerp(1260, 560, k), lerp(650, 470, k), lerp(1.0, 1.28, k) + seg(t, 3, 7) * .05);
    plate(PL.var, { t, cam: C, grey: 0 });
    const T12 = +(q.get('t12') ?? 3.55), S0 = +(q.get('s0') ?? 4.55), S1 = +(q.get('s1') ?? 5.7);
    const prev = tt => tt < T12 ? 57.6 + 2.4 * ss(tt / T12) : tt < S0 ? 60 : 60 - 720 * eio(seg(tt, S0, S1));
    ponteiros(prev(t), prev(t) - prev(t - 1 / 30)); flush({ t, cam: C, grey: 0, run: 0 });
    E.finish({ expo: 1.03, sat: 1.08, contrast: 1.05, vig: .24, spec: .24, light: [-.6, -.55, .7] });
  } else if (CENA === 'fim') {                                // fala 9: fim de tarde, ponteiro parado perto do 12
    const k = ss(seg(t, 0, 6));
    const C = cam(lerp(760, 560, k), lerp(560, 470, k), lerp(1.08, 1.32, k));
    plate(PL.var, { t, cam: C, grey: 0 });
    ponteiros(59.2 + Math.sin(t * 9) * .08 * seg(t, 1, 2)); flush({ t, cam: C, grey: 0, run: 0 });
    E.finish({ expo: .72, sat: .95, contrast: 1.12, vig: .55, spec: .4, light: [.9, -.25, .4], lightCol: [1, .7, .45], gain: [1.1, .86, .68] });
  } else if (CENA === 'folhinha') {                           // fala 3: o "12" da folhinha é riscado a espátula
    const z = lerp(1.42, 1.62, ss(seg(t, 0, 6.5)));
    const C = cam(FOL[0] + FOL[2] / 2 + 6, FOL[1] + FOL[3] / 2 + 10, z);
    plate(PL.var, { t, cam: C, grey: 0 });
    const ponto = (u, x0, y0, x1, y1) => [lerp(x0, x1, u), lerp(y0, y1, u)];
    const xs = [[.35, 1.0, FOL[0] + 30, FOL[1] + 110, FOL[0] + FOL[2] - 30, FOL[1] + 270], [.85, 1.45, FOL[0] + FOL[2] - 30, FOL[1] + 110, FOL[0] + 30, FOL[1] + 270]];
    xs.forEach(([a, b, x0, y0, x1, y1], j) => { const u = seg(t, a, b); if (u <= 0) return; const n = Math.ceil(u * 16);
      for (let i = 0; i < n; i++) { const [x, y] = ponto(i / 16, x0, y0, x1, y1); dyn.push({ x, y, ang: Math.atan2(y1 - y0, x1 - x0), len: 34, wid: 22, c: hex('#c0281a'), c2: hex('#e04a2a'), type: KNIFE, hgt: 1.5, seed: 40 + j * 20 + i, alpha: .95 }); } });
    flush({ t, cam: C, grey: 0, run: 0 });
    E.finish({ expo: 1.02, sat: 1.06, contrast: 1.05, vig: .28, spec: .3, light: [-.6, -.55, .7] });
  } else {                                                    // fala 6: mapa cinza; N, NE e CO ganham cor; 30% → 25%
    const C = cam(540, 540, 1 + .05 * ss(seg(t, 0, 6)));
    E.under(PL.map.tex, V, V, { t, cam: C, grey: .35, reveal: NEVER }); E.draw(PL.map.b, { t, cam: C, grey: 1, reveal: 0, revDur: .35 });
    const ta = +(q.get('a') ?? 2.6), tb = +(q.get('b') ?? 3.75), tc = +(q.get('c') ?? 4.25);
    const M30 = [.8, 0, 0, .8, 690, 40], o30 = seg(t, tb + .25, tb + .7);
    if (t > ta && o30 < 1) E.draw(PL.t30.b, { t, cam: C, M: M30, grey: 0, appear: ta, appDur: .7, alpha: 1 - o30 });
    if (t > tb) { const u = seg(t, tb - .05, tb + .3), n = Math.ceil(u * 12);
      for (let i = 0; i < n; i++) dyn.push({ x: 725 + i * 24, y: 40 + 96 - i * 1.6, ang: -.06, len: 46, wid: 20, c: hex('#c0281a'), type: KNIFE, hgt: 1.4, seed: 70 + i, alpha: 1 - o30 }); flush({ t, cam: C, grey: 0, run: 0 }); }
    if (t > tc) E.draw(PL.t25.b, { t, cam: C, M: M30, grey: 0, appear: tc, appDur: .7 });
    E.finish({ expo: 1.04, sat: 1.1, contrast: 1.05, vig: .26, spec: .26, light: [-.5, -.6, .7] });
  }
}
