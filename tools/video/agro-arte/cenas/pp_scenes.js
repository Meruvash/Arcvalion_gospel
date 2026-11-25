// Cenas do vídeo "O banco toma o seu sítio?" — pintadas em código, sem imagem gerada por IA. Recorte central x 420..1500.
// Composições novas, à maneira de mestres em domínio público:
//   pp_almeida   — Almeida Júnior (1850–1899): família caipira na roça, luz forte do sol brasileiro, terra vermelha,
//                  o pai apoiado na enxada, a mãe com o lenço, a criança com a moringa; casa de pau a pique ao fundo
//   pp_lhermitte — Léon Lhermitte (1844–1925): colheita em família ao entardecer, feixes de trigo/feijão no chão,
//                  luz dourada rasante, figuras a contraluz
//   pp_chardin   — Jean-Siméon Chardin (1699–1779): natureza-morta sobre a mesa de madeira — a caderneta da roça aberta,
//                  o chapéu de palha, a enxada encostada, um cesto de feijão e a lamparina
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 93 }), 0, 0); c.restore(); };
  const figura = (g, x, y, s, roupa, pele, chapeu) => {        // corpo de pé, levemente de lado
    g.fillStyle = roupa; poly(g, [[x - 34 * s, y], [x - 26 * s, y - 150 * s], [x + 26 * s, y - 150 * s], [x + 34 * s, y]]); g.fill();
    g.fillStyle = '#3a2e24'; g.fillRect(x - 22 * s, y, 16 * s, 70 * s); g.fillRect(x + 6 * s, y, 16 * s, 70 * s);
    ell(g, x, y - 172 * s, 22 * s, 25 * s, 0, pele);
    if (chapeu) { ell(g, x, y - 188 * s, 48 * s, 11 * s, 0, chapeu); ell(g, x, y - 200 * s, 24 * s, 14 * s, 0, chapeu); }
  };

  // ---------------------------------------------------------------- Almeida Júnior: a família na roça
  SCENES['pp_almeida'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 520, [[0, '#7ab0e0'], [1, '#e8eef0']]); g.fillRect(0, 0, W, 520);                      // céu claro de meio-dia
      g.fillStyle = '#5a8a4a'; poly(g, [[0, 520], [500, 420], [900, 470], [1300, 400], [1920, 480], [1920, 560], [0, 560]]); g.fill();   // mata ao fundo
      g.fillStyle = grad(g, 0, 520, 0, H, [[0, '#c86a3a'], [1, '#8a3a1a']]); g.fillRect(0, 520, W, H - 520);                   // terra vermelha
      g.fillStyle = '#d8c8a0'; g.fillRect(1180, 380, 240, 150); g.fillStyle = '#6a5a3a'; poly(g, [[1160, 384], [1300, 310], [1440, 384]]); g.fill();   // casa de pau a pique
      g.fillStyle = '#3a2a1a'; g.fillRect(1280, 440, 40, 90);
      for (let k = 0; k < 9; k++) { g.strokeStyle = 'rgba(90,40,16,.5)'; g.lineWidth = 10; g.beginPath(); g.moveTo(420 + k * 140, H); g.lineTo(880 + k * 30, 560); g.stroke(); }   // sulcos
      for (let k = 0; k < 28; k++) ell(g, 460 + (k % 7) * 150 + (k > 13 ? 40 : 0), 600 + Math.floor(k / 7) * 110, 34, 16, 0, '#4a8a2a');   // pés de mandioca/feijão
      figura(g, 760, 900, 1.5, '#e8e0cc', '#8a5a36', '#d8b860');            // o pai, camisa clara, apoiado na enxada
      g.strokeStyle = '#5a3a1e'; g.lineWidth = 9; g.beginPath(); g.moveTo(830, 560); g.lineTo(880, 1000); g.stroke(); g.fillStyle = '#7a7a7a'; g.fillRect(860, 990, 60, 18);
      figura(g, 1010, 880, 1.35, '#3a5a8a', '#9a6a44', null); ell(g, 1010, 640, 30, 16, 0, '#e8e0d0');   // a mãe de saia azul e lenço
      figura(g, 1180, 880, .9, '#b84a2a', '#9a6a44', null); ell(g, 1230, 790, 22, 28, 0, '#a85a30');     // a criança com a moringa
      return M.broken(a, { cell: 7, len: 16, wid: 6, passes: 2, angle: (x, y) => 0.3 + Math.sin(y * .006) * .4, seed: 251, jit: 12, skip: 0.04, sat: 1.05, warm: [255, 230, 180], cool: [70, 80, 100] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,240,200,${.10 + .04 * Math.sin(t * 1.3)})`; c.fillRect(0, 0, W, 560); c.restore();   // calor do meio-dia
      const r = rng(31); c.fillStyle = 'rgba(255,230,190,.5)'; for (let i = 0; i < 30; i++) { const x = 420 + r() * 1080, y = 560 + ((r() * 500 - t * 25 * (r() + .3)) % 500 + 500) % 500; c.fillRect(x, y, 3, 3); }   // poeira da terra
      tela(c, 'canvas_aj', '#ead8c0');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Lhermitte: a colheita em família ao entardecer
  SCENES['pp_lhermitte'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#8aa0c0'], [.6, '#f0c890'], [1, '#ffd890']]); g.fillRect(0, 0, W, 560);
      ell(g, 1380, 520, 90, 90, 0, '#fff0b0');                                                                             // sol baixo
      g.fillStyle = '#6a7a5a'; poly(g, [[0, 560], [700, 500], [1400, 540], [1920, 510], [1920, 600], [0, 600]]); g.fill();
      g.fillStyle = grad(g, 0, 560, 0, H, [[0, '#e0a84a'], [1, '#8a5a24']]); g.fillRect(0, 560, W, H - 560);                 // campo colhido, dourado
      for (let k = 0; k < 6; k++) { const x = 470 + k * 190, y = 700 + (k % 2) * 60; g.fillStyle = '#c89a4a'; poly(g, [[x - 40, y + 60], [x - 10, y - 50], [x + 10, y - 50], [x + 40, y + 60]]); g.fill(); g.fillStyle = '#8a6a2a'; g.fillRect(x - 30, y + 4, 60, 10); }   // feixes
      figura(g, 700, 920, 1.55, '#4a4a5a', '#6a4a2a', '#c8a050');          // o pai com o feixe nos ombros
      g.fillStyle = '#d8a850'; poly(g, [[640, 650], [800, 600], [820, 640], [660, 690]]); g.fill();
      figura(g, 980, 940, 1.4, '#7a3a2a', '#6a4a2a', null); ell(g, 980, 690, 30, 18, 0, '#ece2c8');      // a mãe com o lenço, a contraluz
      figura(g, 1180, 930, 1.0, '#5a6a8a', '#6a4a2a', '#c8a050');         // o filho
      return M.broken(a, { cell: 7, len: 15, wid: 6, passes: 2, angle: (x, y) => 0.1 + Math.sin(x * .005) * .3, seed: 261, jit: 11, skip: 0.04, sat: 1.0, warm: [255, 220, 160], cool: [80, 80, 110] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; const gr = c.createRadialGradient(1380, 520, 20, 1380, 520, 700); gr.addColorStop(0, `rgba(255,210,140,${.2 + .04 * Math.sin(t)})`); gr.addColorStop(1, 'rgba(255,220,150,0)'); c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      const r = rng(55); c.fillStyle = 'rgba(255,236,180,.6)'; for (let i = 0; i < 40; i++) { const x = 420 + ((r() * 1080 + t * 30 * (r() + .2)) % 1080), y = 560 + r() * 400 + Math.sin(t + i) * 6; c.fillRect(x, y, 2, 2); }   // palha no ar
      tela(c, 'canvas_lh', '#ecdcc0');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Chardin: a caderneta da roça
  SCENES['pp_chardin'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2711);
      g.fillStyle = grad(g, 0, 0, W, H, [[0, '#4a4234'], [1, '#2a241c']]); g.fillRect(0, 0, W, H);                          // parede escura, quente
      g.fillStyle = '#7a5a36'; g.fillRect(0, 640, W, H - 640); g.fillStyle = '#5a4026'; g.fillRect(0, 640, W, 26);             // mesa
      g.strokeStyle = '#6a4a2a'; g.lineWidth = 11; g.beginPath(); g.moveTo(1360, 120); g.lineTo(1240, 700); g.stroke(); g.fillStyle = '#8a8a86'; poly(g, [[1210, 690], [1290, 700], [1280, 740], [1200, 728]]); g.fill();   // enxada encostada
      ell(g, 640, 600, 150, 40, 0, '#d8b868'); ell(g, 640, 570, 78, 52, 0, '#d0ae5e'); g.fillStyle = '#8a3a2a'; g.fillRect(568, 584, 144, 12);   // chapéu de palha
      g.fillStyle = '#efe6cc'; poly(g, [[780, 760], [1110, 730], [1130, 900], [800, 930]]); g.fill();                        // a caderneta aberta
      g.strokeStyle = '#b8a888'; g.lineWidth = 2; g.beginPath(); g.moveTo(955, 745); g.lineTo(965, 915); g.stroke();
      for (let k = 0; k < 7; k++) { g.strokeStyle = 'rgba(40,40,80,.55)'; g.lineWidth = 3; g.beginPath(); g.moveTo(800, 790 + k * 18); g.lineTo(930, 780 + k * 18); g.stroke(); g.beginPath(); g.moveTo(980, 776 + k * 18); g.lineTo(1100, 766 + k * 18); g.stroke(); }   // anotações
      ell(g, 1300, 820, 110, 50, 0, '#9a6a34'); ell(g, 1300, 800, 96, 30, 0, '#6a2a1a');                                     // cesto de feijão
      for (let k = 0; k < 40; k++) ell(g, 1230 + r() * 140, 790 + r() * 20, 6, 4, r() * 3, '#4a1a10');
      g.fillStyle = '#a0a8a0'; g.fillRect(520, 700, 60, 110); ell(g, 550, 690, 26, 30, 0, '#d8e0d0');                          // lamparina
      return M.broken(a, { cell: 6, len: 13, wid: 5, passes: 2, angle: (x, y) => 0.6 + Math.sin(x * .004) * .3, seed: 271, jit: 10, skip: 0.03, sat: .95, warm: [250, 225, 180], cool: [60, 60, 60] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; const f = .32 + .06 * Math.sin(t * 9) * Math.sin(t * 3.7);              // a chama da lamparina tremendo
      const gr = c.createRadialGradient(550, 660, 6, 550, 660, 560); gr.addColorStop(0, `rgba(255,200,110,${f})`); gr.addColorStop(1, 'rgba(255,200,110,0)'); c.fillStyle = gr; c.fillRect(0, 0, W, H);
      c.fillStyle = 'rgba(255,230,150,.95)'; c.beginPath(); c.ellipse(550, 650 + Math.sin(t * 11) * 2, 7, 16, 0, 0, TAU); c.fill(); c.restore();
      const n = Math.min(7, Math.floor(t * 2.2)); c.save(); c.strokeStyle = 'rgba(30,30,90,.85)'; c.lineWidth = 3;                // uma linha nova sendo anotada
      for (let k = 0; k < n; k++) { c.beginPath(); c.moveTo(985, 900 - k * 4); c.lineTo(985 + 16 * k, 898 - k * 4); c.stroke(); } c.restore();
      tela(c, 'canvas_cd', '#e6dcc4');
    }
    return { draw };
  })();
})();
