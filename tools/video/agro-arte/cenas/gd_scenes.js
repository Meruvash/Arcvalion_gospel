// Cenas do vídeo "O gado do vizinho comeu a sua roça" — pintadas em código, sem imagem gerada por IA.
// Recorte central x 420..1500. Composições novas, à maneira de mestres em domínio público:
//   gd_potter   — Paulus Potter (1625–1654): boi malhado em primeiro plano, comendo o milho pisoteado, céu holandês baixo
//   gd_rousseau — Théodore Rousseau (1812–1867): depois do temporal, um tronco caído sobre a cerca de arame, céu limpando
//   gd_millet   — Jean-François Millet (1814–1875): galinhas ciscando no terreiro junto da tela de arame, luz de fim de tarde
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 71 }), 0, 0); c.restore(); };
  const nuvens = (g, r, n, y0, y1, cor, sombra) => { for (let i = 0; i < n; i++) { const x = 380 + r() * 1180, y = y0 + r() * (y1 - y0), w = 90 + r() * 200;
    g.fillStyle = grad(g, 0, y - w * .4, 0, y + w * .3, [[0, cor], [1, sombra]]); for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * w * 1.4, y + (r() - .5) * w * .3, w * (.35 + r() * .35), w * (.18 + r() * .14), 0, 0, TAU); g.fill(); } } };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };

  // ---------------------------------------------------------------- Potter: boi no milho pisoteado
  SCENES['gd_potter'] = (() => {
    let plate, built = false; const HZ = 520;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1701);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#5a7ea8'], [0.55, '#b8c4cc'], [1, '#ece4cc']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 14, 60, 360, '#f8f2e2', '#8c94a0');
      g.fillStyle = '#5a7a3a'; g.fillRect(0, HZ - 6, W, 30);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#7a9a44'], [1, '#4a6a26']]); g.fillRect(0, HZ + 20, W, H - HZ);
      for (let i = 0; i < 70; i++) { const x = 420 + r() * 1100, y = HZ + 30 + r() * 120, h = 90 + r() * 80;            // milho em pé ao fundo
        g.strokeStyle = r() < .5 ? '#3f7a2a' : '#4e8a30'; g.lineWidth = 5; g.beginPath(); g.moveTo(x, y + h); g.lineTo(x + (r() - .5) * 10, y); g.stroke();
        g.fillStyle = '#d8b84a'; g.fillRect(x - 3, y - 14, 6, 16); }
      for (let i = 0; i < 40; i++) { const x = 420 + r() * 1100, y = 820 + r() * 220;                                       // milho pisoteado no chão
        g.strokeStyle = r() < .5 ? '#8a8a3a' : '#a89a4a'; g.lineWidth = 6; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 60 + r() * 60, y + (r() - .5) * 30); g.stroke(); }
      // o boi malhado, grande, de lado, cabeça baixa no milho
      const bx = 900, by = 730;
      g.fillStyle = '#2a2420'; [[-120, 0], [-80, 6], [70, 4], [110, 0]].forEach(([dx, dy]) => g.fillRect(bx + dx, by + 40 + dy, 22, 150));
      ell(g, bx, by, 200, 92, 0, '#f2ece0'); ell(g, bx - 140, by - 18, 84, 84, 0, '#f2ece0');
      ell(g, bx - 40, by - 30, 70, 44, .3, '#201c1a'); ell(g, bx + 90, by + 20, 50, 34, -.4, '#201c1a'); ell(g, bx - 150, by + 20, 34, 26, .5, '#201c1a');
      g.fillStyle = '#ebe4d6'; poly(g, [[bx + 170, by - 40], [bx + 250, by + 60], [bx + 290, by + 140], [bx + 240, by + 160], [bx + 180, by + 50]]); g.fill();
      ell(g, bx + 268, by + 152, 30, 20, 0, '#d4a8a0');
      g.strokeStyle = '#e8dcc0'; g.lineWidth = 10; g.beginPath(); g.moveTo(bx + 236, by + 64); g.quadraticCurveTo(bx + 254, by + 20, bx + 290, by + 16); g.stroke();
      return M.broken(a, { cell: 7, len: 16, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.1 + Math.sin(x * 0.005) * 0.4 : (y > 800 ? 0.2 : -1.4), seed: 171, jit: 12, skip: 0.05, sat: 1.0, warm: [255, 230, 180], cool: [90, 110, 140] });
    }
    function rabo(c, t) {                                                      // o rabo espanta mosca
      const sw = Math.sin(t * 3.1) * 0.25; c.save(); c.translate(684, 700); c.rotate(sw);
      c.strokeStyle = '#2a2420'; c.lineWidth = 9; c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(-26, 70, -10, 150); c.stroke();
      c.fillStyle = '#1a1614'; c.beginPath(); c.ellipse(-10, 160, 12, 22, 0, 0, TAU); c.fill(); c.restore();
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0); rabo(c, t);
      const bob = Math.sin(t * 2.2) * 6; c.save(); c.globalAlpha = .9; c.strokeStyle = '#4e8a30'; c.lineWidth = 6;     // folha de milho na boca, mastigando
      c.beginPath(); c.moveTo(1170, 880 + bob); c.lineTo(1230, 850 + bob); c.stroke(); c.restore();
      tela(c, 'canvas_gp', '#e8dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Rousseau: árvore caída sobre a cerca depois do temporal
  SCENES['gd_rousseau'] = (() => {
    let plate, built = false; const HZ = 600;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1801);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#3a4252'], [0.5, '#7a8088'], [1, '#d8cca8']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 12, 40, 300, '#9a9a98', '#3a3e48');
      { const rg = g.createRadialGradient(1300, 430, 10, 1300, 430, 320); rg.addColorStop(0, 'rgba(250,228,180,.7)'); rg.addColorStop(1, 'rgba(250,228,180,0)'); g.fillStyle = rg; g.fillRect(900, 200, 800, 460); }   // o céu abrindo
      g.fillStyle = '#3a4a28'; g.fillRect(0, HZ - 20, W, 50);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#5e7034'], [1, '#2e3e18']]); g.fillRect(0, HZ + 20, W, H - HZ);
      for (let i = 0; i < 26; i++) ell(g, 480 + r() * 300, HZ - 80 - r() * 160, 50 + r() * 40, 40 + r() * 30, 0, ['#2a3a1e', '#3a4a26', '#1e2a14'][i % 3]);   // mata ao fundo (Barbizon)
      // cerca de arame em diagonal
      g.fillStyle = '#3a2a18'; for (let k = 0; k < 8; k++) g.fillRect(460 + k * 140, 640 + k * 18, 18, 230);
      g.strokeStyle = '#2a2a2a'; g.lineWidth = 3; [690, 750, 810].forEach(y => { g.beginPath(); g.moveTo(460, y); g.lineTo(940, y + 70); g.moveTo(1120, y + 100); g.lineTo(1500, y + 150); g.stroke(); });
      // o tronco tombado, com galhos e a raiz arrancada, por cima da cerca amassada
      g.fillStyle = '#4a3420'; poly(g, [[560, 560], [600, 540], [1300, 900], [1270, 940]]); g.fill();
      g.fillStyle = '#5a3e24'; g.beginPath(); g.ellipse(560, 560, 70, 90, -.4, 0, TAU); g.fill();                           // raiz
      for (let i = 0; i < 9; i++) { const u = .35 + i * .07, x = lerp(600, 1290, u), y = lerp(545, 915, u);
        g.strokeStyle = '#4a3420'; g.lineWidth = 10; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 30 + r() * 60, y - 80 - r() * 60); g.stroke();
        for (let k = 0; k < 4; k++) ell(g, x + 40 + r() * 70, y - 110 - r() * 60, 34 + r() * 20, 22 + r() * 14, 0, ['#3a5a26', '#4a6a2e', '#2e4a1e'][k % 3]); }
      g.fillStyle = 'rgba(120,140,160,.45)'; for (let i = 0; i < 6; i++) { g.beginPath(); g.ellipse(500 + r() * 900, 960 + r() * 80, 90 + r() * 60, 12, 0, 0, TAU); g.fill(); }   // poças
      return M.broken(a, { cell: 8, len: 18, wid: 7, passes: 2, angle: (x, y) => y < HZ ? 0.12 + Math.sin(x * 0.004) * 0.5 : -1.3, seed: 181, jit: 14, skip: 0.05, sat: .92, warm: [235, 205, 150], cool: [70, 80, 100] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), d = ss(0, 6, t);
      c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; { const rg = c.createRadialGradient(1300, 430, 10, 1300, 430, 360 + 260 * d); rg.addColorStop(0, `rgba(255,220,150,${0.08 + 0.22 * d})`); rg.addColorStop(1, 'rgba(255,220,150,0)'); c.fillStyle = rg; c.fillRect(0, 0, W, H); } c.restore();   // luz voltando
      const r = rng(9 + Math.floor(t * 12)); c.fillStyle = `rgba(230,236,240,${0.5 * (1 - d)})`;                         // últimas gotas
      for (let i = 0; i < 80 * (1 - d); i++) { const x = 420 + r() * 1080, y = r() * H; c.fillRect(x, y, 2, 14); }
      tela(c, 'canvas_gr', '#e0d8c4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Millet: galinhas junto da tela, fim de tarde
  SCENES['gd_millet'] = (() => {
    let plate, built = false; const HZ = 470;
    const HENS = [[700, 860, 1, 1.1, '#c8662a'], [880, 930, -1, 1.25, '#f2ece0'], [1080, 880, 1, 1.0, '#1e1a18'], [1250, 960, -1, 1.3, '#b8562a'], [560, 980, 1, 1.35, '#e8dcc0']];
    function hen(g, x, y, d, s, cor) {
      ell(g, x, y, 46 * s, 32 * s, 0, cor); ell(g, x + d * 36 * s, y - 34 * s, 18 * s, 18 * s, 0, cor);
      g.fillStyle = '#c8281a'; g.beginPath(); g.ellipse(x + d * 38 * s, y - 54 * s, 8 * s, 6 * s, 0, 0, TAU); g.fill();
      g.fillStyle = '#e8b030'; poly(g, [[x + d * 52 * s, y - 36 * s], [x + d * 66 * s, y - 32 * s], [x + d * 52 * s, y - 28 * s]]); g.fill();
      g.fillStyle = cor; poly(g, [[x - d * 40 * s, y - 10 * s], [x - d * 74 * s, y - 40 * s], [x - d * 58 * s, y + 4 * s]]); g.fill();   // cauda
      g.strokeStyle = '#d8a030'; g.lineWidth = 4 * s; g.beginPath(); g.moveTo(x - 8 * s, y + 28 * s); g.lineTo(x - 10 * s, y + 52 * s); g.moveTo(x + 10 * s, y + 28 * s); g.lineTo(x + 12 * s, y + 52 * s); g.stroke();
    }
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1901);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#8aa0b4'], [0.6, '#e8d0a0'], [1, '#f4dca8']]); g.fillRect(0, 0, W, HZ);
      g.fillStyle = '#6a7a48'; g.fillRect(0, HZ - 10, W, 40);
      g.fillStyle = '#c8a878'; g.fillRect(1180, HZ - 140, 320, 150); g.fillStyle = '#8a4a2a'; poly(g, [[1160, HZ - 138], [1340, HZ - 230], [1520, HZ - 138]]); g.fill();   // paiol
      g.fillStyle = '#5a3a24'; g.fillRect(1290, HZ - 90, 60, 100);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#c8aa76'], [1, '#8a6a42']]); g.fillRect(0, HZ + 20, W, H - HZ);               // terreiro de chão batido
      for (let i = 0; i < 120; i++) { g.fillStyle = r() < .5 ? 'rgba(90,70,40,.35)' : 'rgba(240,220,170,.35)'; g.fillRect(420 + r() * 1100, HZ + 40 + r() * 560, 6 + r() * 14, 3); }
      // a tela de arame (malha), presa em moirões, separando o terreiro da roça verde do outro lado
      g.fillStyle = '#5e8a3a'; g.fillRect(0, HZ + 20, W, 120);
      g.fillStyle = '#4a3420'; for (let k = 0; k < 7; k++) g.fillRect(430 + k * 180, HZ - 40, 16, 260);
      g.strokeStyle = 'rgba(70,70,70,.85)'; g.lineWidth = 2; for (let x = 420; x < 1520; x += 22) { g.beginPath(); g.moveTo(x, HZ - 20); g.lineTo(x + 40, HZ + 200); g.moveTo(x + 40, HZ - 20); g.lineTo(x, HZ + 200); g.stroke(); }
      return M.broken(a, { cell: 7, len: 15, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.05 : 0.1, seed: 191, jit: 12, skip: 0.05, sat: 1.0, warm: [255, 220, 160], cool: [100, 110, 130] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const cv = P.scratch('gm_hens'); if (cv.width !== W) { cv.width = W; cv.height = H; } const g2 = cv.getContext('2d'); g2.reset(); g2.clearRect(0, 0, W, H);
      HENS.forEach(([x, y, d, s, cor], i) => { const peck = Math.max(0, Math.sin(t * 2.4 + i * 1.7)) ** 6; g2.save(); g2.translate(x + Math.sin(t * .4 + i) * 20, y); g2.rotate(d * peck * .5); hen(g2, 0, 0, d, s, cor); g2.restore(); });
      c.save(); c.strokeStyle = 'rgba(60,60,64,.75)'; c.lineWidth = 2.5; for (let x = 436; x < 1500; x += 26) { c.beginPath(); c.moveTo(x, 450); c.lineTo(x + 52, 690); c.moveTo(x + 52, 450); c.lineTo(x, 690); c.stroke(); } c.restore();   // a tela de arame
      c.drawImage(M.broken(cv, { cell: 4, len: 10, wid: 4, passes: 2, angle: () => 0.2, seed: 193, jit: 10, skip: 0.02, base: true, sat: 1.0, warm: [250, 228, 180], cool: [80, 80, 100] }), 0, 0);
      c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,190,110,.35)'; c.fillRect(0, 0, W, H); c.restore();   // luz de fim de tarde
      tela(c, 'canvas_gm', '#e8dcc4');
    }
    return { draw };
  })();
})();
