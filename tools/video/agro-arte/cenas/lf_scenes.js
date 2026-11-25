// Cenas do vídeo "O banco leiloa a sua fazenda sem juiz?" — pintadas em código, sem imagem gerada por IA.
// Recorte central x 420..1500. Composições novas, à maneira de mestres em domínio público:
//   lf_hooch — Pieter de Hooch (1629–1684): sala de cartório com porta aberta para a luz, mesa com o livro de registro e o carimbo
//   lf_heda  — Willem Claesz. Heda (1594–1680): natureza-morta do leilão — martelo de madeira, papéis, a planta da fazenda, moedas
//   lf_corot — Camille Corot (1796–1875): porteira de fazenda se abrindo ao amanhecer, névoa prateada e árvores leves
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 81 }), 0, 0); c.restore(); };

  // ---------------------------------------------------------------- de Hooch: o cartório
  SCENES['lf_hooch'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2001);
      g.fillStyle = grad(g, 0, 0, 0, H, [[0, '#5a4630'], [1, '#2e2216']]); g.fillRect(0, 0, W, H);                        // parede escura
      g.fillStyle = '#7a5a3a'; g.fillRect(0, 760, W, 320);                                                                   // assoalho
      for (let i = 0; i < 12; i++) { g.fillStyle = i % 2 ? '#c8b89a' : '#3a2e22'; for (let j = 0; j < 4; j++) poly(g, [[420 + i * 95 + j * 30, 760 + j * 80], [515 + i * 95 + j * 30, 760 + j * 80], [545 + i * 95 + (j + 1) * 30, 840 + j * 80], [450 + i * 95 + (j + 1) * 30, 840 + j * 80]]), g.fill(); }   // piso xadrez (de Hooch)
      g.fillStyle = '#f6e8c0'; g.fillRect(1120, 220, 260, 540);                                                              // porta aberta para o pátio claro
      g.fillStyle = grad(g, 0, 220, 0, 760, [[0, '#cfe2ee'], [.6, '#f6ead0'], [1, '#d8c890']]); g.fillRect(1140, 240, 220, 520);
      g.fillStyle = '#6a8a4a'; g.fillRect(1140, 640, 220, 120);
      g.fillStyle = '#4a3420'; g.fillRect(1100, 200, 300, 24); g.fillRect(1100, 200, 24, 560); g.fillRect(1376, 200, 24, 560);
      g.fillStyle = '#5a3a24'; g.fillRect(520, 600, 520, 40); g.fillRect(540, 640, 30, 200); g.fillRect(990, 640, 30, 200);    // mesa
      g.fillStyle = '#8a2a1a'; g.fillRect(500, 560, 560, 50);                                                                // toalha vermelha
      g.fillStyle = '#efe4c8'; poly(g, [[600, 520], [820, 510], [830, 570], [610, 580]]); g.fill();                          // livro de registro aberto
      g.strokeStyle = '#6a5a40'; g.lineWidth = 3; for (let k = 0; k < 6; k++) { g.beginPath(); g.moveTo(620, 528 + k * 8); g.lineTo(810, 520 + k * 8); g.stroke(); }
      g.fillStyle = '#2a1a10'; g.fillRect(880, 520, 28, 46); ell(g, 894, 520, 26, 10, 0, '#3a2414');                         // carimbo
      g.fillStyle = '#e8d8b0'; g.fillRect(700, 260, 220, 160); g.strokeStyle = '#4a3420'; g.lineWidth = 10; g.strokeRect(700, 260, 220, 160);   // quadro com a planta da fazenda
      g.strokeStyle = '#6a8a4a'; g.lineWidth = 3; for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(720, 290 + k * 25); g.lineTo(900, 280 + k * 28); g.stroke(); }
      return M.broken(a, { cell: 7, len: 15, wid: 6, passes: 2, angle: (x, y) => y > 760 ? 0.15 : 1.5, seed: 201, jit: 12, skip: 0.05, sat: 1.0, warm: [255, 220, 160], cool: [70, 70, 90] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; const k = .55 + .1 * Math.sin(t * .6);                                // a luz da porta varre o piso
      const gr = c.createLinearGradient(1250, 300, 700, 1080); gr.addColorStop(0, `rgba(255,230,170,${.35 * k})`); gr.addColorStop(1, 'rgba(255,230,170,0)');
      c.fillStyle = gr; c.beginPath(); c.moveTo(1140, 240); c.lineTo(1360, 240); c.lineTo(1100, 1080); c.lineTo(560, 1080); c.closePath(); c.fill(); c.restore();
      const r = rng(31); c.fillStyle = 'rgba(255,240,200,.5)'; for (let i = 0; i < 40; i++) { const x = 800 + r() * 500, y = (r() * 900 + t * 12 * (r() + .3)) % 900 + 150; c.fillRect(x, y, 2, 2); }   // poeira na luz
      tela(c, 'canvas_lh', '#e6dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Heda: a mesa do leilão
  SCENES['lf_heda'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2101);
      g.fillStyle = grad(g, 0, 0, W, H, [[0, '#4a4a3e'], [1, '#22221c']]); g.fillRect(0, 0, W, H);                          // fundo neutro esverdeado (Heda)
      g.fillStyle = grad(g, 0, 640, 0, H, [[0, '#8a7a5a'], [1, '#5a4a32']]); g.fillRect(0, 640, W, H - 640);                // mesa
      g.fillStyle = '#ece4cc'; poly(g, [[540, 700], [1040, 660], [1100, 900], [600, 950]]); g.fill();                        // a planta da fazenda, desenrolada
      g.strokeStyle = '#6a8a4a'; g.lineWidth = 3; poly(g, [[620, 740], [980, 712], [1020, 870], [660, 900]]); g.stroke();
      for (let k = 0; k < 6; k++) { g.beginPath(); g.moveTo(640 + k * 10, 760 + k * 22); g.lineTo(990, 735 + k * 22); g.stroke(); }
      g.fillStyle = '#d8ccae'; poly(g, [[1120, 760], [1380, 740], [1400, 820], [1140, 840]]); g.fill();                     // edital do leilão
      g.fillStyle = '#3a2a1a'; g.font = '700 30px Georgia, serif'; g.save(); g.translate(1160, 790); g.rotate(-0.07); g.fillText('LEILÃO', 0, 0); g.restore();
      [[1240, 900], [1270, 912], [1300, 896]].forEach(([x, y]) => { ell(g, x, y, 30, 10, 0, '#b8902a'); ell(g, x, y - 4, 30, 10, 0, '#e0c060'); });   // moedas
      g.fillStyle = '#c8c8c0'; poly(g, [[480, 520], [520, 520], [540, 660], [460, 660]]); g.fill(); ell(g, 500, 520, 40, 12, 0, '#e8e8e0');           // taça de estanho
      return M.broken(a, { cell: 7, len: 14, wid: 6, passes: 2, angle: (x, y) => y > 640 ? 0.05 : 1.2, seed: 211, jit: 12, skip: 0.04, sat: .9, warm: [240, 210, 160], cool: [70, 75, 70] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      // o martelo: sobe e bate na base de madeira duas vezes (1º e 2º leilão)
      const bate = (a) => { const u = clamp((t - a) / .5, 0, 1); return u < .6 ? -0.6 * Math.sin(u / .6 * Math.PI / 2) : -0.6 + 0.6 * ((u - .6) / .4); };
      const ang = t < 2.5 ? bate(1.0) : bate(3.6);
      c.save(); c.translate(900, 600); c.fillStyle = '#4a2a14'; c.beginPath(); c.ellipse(0, 50, 90, 22, 0, 0, TAU); c.fill();   // base
      c.translate(-160, 10); c.rotate(ang); c.fillStyle = '#6a3a1a'; c.fillRect(0, -10, 200, 20); c.fillStyle = '#5a2e14'; c.fillRect(170, -40, 70, 80); c.restore();
      const flash = Math.max(0, 1 - Math.abs(t - 1.5) * 4) + Math.max(0, 1 - Math.abs(t - 4.1) * 4);
      if (flash > 0) { c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,235,190,${.18 * flash})`; c.fillRect(0, 0, W, H); c.restore(); }
      tela(c, 'canvas_lhd', '#e2d8c0');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Corot: a porteira ao amanhecer
  SCENES['lf_corot'] = (() => {
    let plate, built = false; const HZ = 600;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2201);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#b8c4c0'], [.6, '#e8e4cc'], [1, '#f6eccc']]); g.fillRect(0, 0, W, HZ);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#9aa880'], [1, '#5a6a44']]); g.fillRect(0, HZ, W, H - HZ);
      for (let i = 0; i < 70; i++) { const x = r() < .5 ? 420 + r() * 300 : 1180 + r() * 320, y = 200 + r() * 380; ell(g, x, y, 30 + r() * 50, 20 + r() * 40, r(), ['rgba(90,110,80,.55)', 'rgba(120,135,100,.5)', 'rgba(70,90,64,.5)'][i % 3]); }   // árvores de Corot, leves
      g.strokeStyle = '#4a4434'; g.lineWidth = 6; [[560, 600, 520, 260], [1300, 600, 1340, 240]].forEach(([x0, y0, x1, y1]) => { g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo((x0 + x1) / 2 + 30, (y0 + y1) / 2, x1, y1); g.stroke(); });
      g.fillStyle = '#c8b48a'; poly(g, [[880, H], [1040, H], [980, HZ], [940, HZ]]); g.fill();                              // estrada
      g.fillStyle = '#4a3a26'; g.fillRect(780, 560, 30, 260); g.fillRect(1110, 560, 30, 260);                                // moirões da porteira
      g.fillStyle = '#5a4a32'; for (const x of [440, 600, 1300, 1460]) g.fillRect(x, 620, 16, 200); g.fillRect(420, 660, 360, 10); g.fillRect(1140, 660, 360, 10);
      return M.broken(a, { cell: 8, len: 16, wid: 7, passes: 2, angle: (x, y) => y < HZ ? 0.2 + Math.sin(x * 0.005) * .5 : -1.3, seed: 221, jit: 14, skip: 0.05, sat: .85, warm: [250, 236, 200], cool: [120, 130, 120] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), k = ss(0.5, 4.5, t);
      c.drawImage(plate, 0, 0);
      // folha da porteira girando para dentro (abrindo)
      c.save(); c.translate(810, 600); const w = 300 * Math.cos(k * 1.2);
      c.fillStyle = '#6a5438'; for (let i = 0; i < 4; i++) c.fillRect(0, 20 + i * 48, w, 16); c.fillRect(Math.max(w - 16, 0), 0, 16, 200);
      c.strokeStyle = '#6a5438'; c.lineWidth = 12; c.beginPath(); c.moveTo(4, 180); c.lineTo(Math.max(w - 8, 4), 24); c.stroke(); c.restore();
      c.save(); c.translate(1110, 600); const w2 = -300 * Math.cos(k * 1.2);
      c.fillStyle = '#6a5438'; for (let i = 0; i < 4; i++) c.fillRect(Math.min(w2, 0), 20 + i * 48, Math.abs(w2), 16); c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; const gr = c.createRadialGradient(960, 560, 10, 960, 560, 520); gr.addColorStop(0, `rgba(255,236,190,${.25 + .35 * k})`); gr.addColorStop(1, 'rgba(255,236,190,0)'); c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      c.save(); c.fillStyle = `rgba(240,240,236,${.28 * (1 - k)})`; c.fillRect(0, 380, W, 420); c.restore();                    // névoa que se dissipa
      tela(c, 'canvas_lc', '#e8e0cc');
    }
    return { draw };
  })();
})();
