// Cenas do vídeo "O caseiro e o vizinho" — pintadas em código, sem imagem gerada por IA. Recorte central x 420..1500.
//   us_homer   — Winslow Homer (1836–1910): homem de costas consertando a cerca no pasto, luz forte de fim de manhã
//   us_bonheur — Rosa Bonheur (1822–1899): gado do vizinho pastando do lado de cá, porteira aberta
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 51 }), 0, 0); c.restore(); };
  const ceu = (g, r, HZ, c0, c1) => { g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, c0], [1, c1]]); g.fillRect(0, 0, W, HZ);
    for (let i = 0; i < 10; i++) { const x = 420 + r() * 1080, y = 80 + r() * 300, w = 90 + r() * 160; g.fillStyle = 'rgba(255,255,255,.9)'; for (let k = 0; k < 5; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * w, y + (r() - .5) * 30, w * .45, w * .18, 0, 0, TAU); g.fill(); } } };

  // ---------------------------------------------------------------- Homer: o caseiro consertando a cerca, de costas
  SCENES['us_homer'] = (() => {
    let plate, built = false; const HZ = 520;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1301);
      ceu(g, r, HZ, '#4f86c6', '#d6e4e8');
      g.fillStyle = '#6a8a5a'; g.beginPath(); g.moveTo(0, HZ); g.quadraticCurveTo(900, HZ - 50, 1920, HZ - 10); g.lineTo(1920, HZ + 30); g.lineTo(0, HZ + 30); g.fill();
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#9ab868'], [0.5, '#7a9a48'], [1, '#5a7a34']]); g.fillRect(0, HZ + 20, W, H - HZ);
      for (let i = 0; i < 900; i++) { const x = r() * W, y = HZ + 40 + r() * 520; g.strokeStyle = ['#a8c070', '#6a8a3a', '#c8c878'][i % 3]; g.lineWidth = 2; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - .5) * 6, y - 8 - (y - HZ) * .03); g.stroke(); }
      // cerca de moirões em diagonal, com dois moirões tombados no ponto do conserto
      for (let k = 0; k < 9; k++) { const x = 460 + k * 130, y = 660 + k * 24, h = 150 + k * 10; if (k === 4 || k === 5) continue; g.fillStyle = '#6a4a2e'; g.fillRect(x, y - h, 18, h); }
      g.strokeStyle = '#3a3a3a'; g.lineWidth = 3; for (const dy of [-120, -80, -40]) { g.beginPath(); g.moveTo(460, 660 + dy); g.lineTo(980, 756 + dy); g.moveTo(1240, 804 + dy); g.lineTo(1500, 852 + dy); g.stroke(); }
      g.fillStyle = '#6a4a2e'; g.save(); g.translate(1060, 830); g.rotate(1.35); g.fillRect(0, 0, 18, 170); g.restore();
      g.fillStyle = '#c8b88a'; g.fillRect(1180, 820, 70, 30);                       // rolo de arame no chão
      // casinha amarela ao longe, que liga com a cena da sede
      g.fillStyle = '#f2cf6a'; g.fillRect(1320, 470, 80, 46); g.fillStyle = '#a8402a'; poly(g, [[1312, 472], [1360, 444], [1408, 472]]); g.fill();
      return M.broken(a, { cell: 7, len: 16, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.05 : -1.3 + Math.sin(x * .01) * .3, seed: 131, jit: 12, skip: 0.05, sat: 1.05, warm: [255, 232, 180], cool: [90, 110, 140] });
    }
    function homem(c0, t) {                                                        // de costas, camisa clara, chapéu de palha, braço com martelo
      const cv = P.scratch('hm_homem'); if (cv.width !== 500) { cv.width = 500; cv.height = 600; } const c = cv.getContext('2d'); c.reset(); c.clearRect(0, 0, 500, 600);
      const golpe = Math.max(0, Math.sin(t * 3.2)) ** 3;
      c.save(); c.translate(230, 580); c.scale(1.5, 1.5);
      c.fillStyle = '#3a3a4a'; c.fillRect(-26, -120, 20, 120); c.fillRect(6, -120, 20, 120);
      c.fillStyle = '#e8e0cc'; c.beginPath(); c.moveTo(-34, -120); c.lineTo(-30, -230); c.lineTo(30, -230); c.lineTo(34, -120); c.closePath(); c.fill();
      c.fillStyle = '#9a6a4a'; c.beginPath(); c.arc(0, -246, 18, 0, TAU); c.fill();
      c.fillStyle = '#e8c070'; c.beginPath(); c.ellipse(0, -258, 40, 10, 0, 0, TAU); c.fill(); c.beginPath(); c.ellipse(0, -266, 20, 14, 0, Math.PI, TAU); c.fill();
      c.save(); c.translate(28, -220); c.rotate(-0.4 - golpe * 1.4); c.fillStyle = '#e8e0cc'; c.fillRect(-7, 0, 14, 80); c.fillStyle = '#5a3a24'; c.fillRect(-3, 70, 6, 40); c.fillStyle = '#4a4a50'; c.fillRect(-14, 104, 28, 12); c.restore();
      c.restore();
      const rep = M.broken(cv, { cell: 4, len: 10, wid: 4, passes: 2, angle: () => 1.5, seed: 133, jit: 10, skip: 0.02, base: true, sat: 1.0, warm: [250, 230, 190], cool: [70, 80, 110] });
      c0.drawImage(rep, 1110 - 230, 900 - 580);
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0); homem(c, t);
      tela(c, 'canvas_hm', '#e8dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Rosa Bonheur: o gado do vizinho do lado de cá, porteira aberta
  SCENES['us_bonheur'] = (() => {
    let plate, built = false; const HZ = 480;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1401);
      ceu(g, r, HZ, '#7a9ac0', '#f0e4c8');
      g.fillStyle = '#7a8a6a'; g.fillRect(0, HZ - 10, W, 40);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#a8b070'], [1, '#6a7a3a']]); g.fillRect(0, HZ + 20, W, H - HZ);
      // cerca de tábuas atravessando, com a porteira aberta no meio
      g.fillStyle = '#7a5a3a'; for (let k = 0; k < 12; k++) { const x = 400 + k * 100; if (k >= 5 && k <= 6) continue; g.fillRect(x, 560, 14, 130); }
      for (const y of [590, 640]) { g.fillRect(400, y, 480, 10); g.fillRect(1100, y, 460, 10); }
      g.fillStyle = '#8a6a44'; g.strokeStyle = '#8a6a44'; g.lineWidth = 11;
      g.beginPath(); g.moveTo(905, 585); g.lineTo(1015, 640); g.moveTo(905, 640); g.lineTo(1015, 700); g.moveTo(905, 585); g.lineTo(1015, 700); g.stroke();
      g.fillRect(1008, 630, 12, 80);                                                  // folha da porteira aberta para dentro
      return M.broken(a, { cell: 7, len: 15, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.05 : -1.2, seed: 141, jit: 12, skip: 0.05, sat: 1.0, warm: [250, 226, 176], cool: [100, 110, 130] });
    }
    const VACAS = [[620, 820, 1.2, '#f4efe4', '#7a4a30'], [900, 880, 1.45, '#8a5a3a', null], [1210, 800, 1.1, '#e8e2d4', '#3a2a20'], [1380, 900, 1.35, '#6a3a24', '#f4efe4']];
    function vaca(c, x, y, s2, cor, mancha, t, i) {
      const cab = Math.sin(t * 1.1 + i) * 6;
      c.save(); c.translate(x, y); c.scale(s2, s2);
      c.fillStyle = '#3a2a20'; for (const dx of [-62, -40, 40, 62]) c.fillRect(dx, 8, 11, 78);
      c.fillStyle = cor; c.beginPath(); c.ellipse(0, 0, 96, 34, 0, 0, TAU); c.fill(); c.beginPath(); c.ellipse(-70, -6, 30, 30, 0, 0, TAU); c.fill();
      if (mancha) { c.fillStyle = mancha; c.beginPath(); c.ellipse(-20, -8, 26, 18, .3, 0, TAU); c.fill(); }
      c.fillStyle = cor; c.save(); c.translate(92, 18 + cab); c.beginPath(); c.moveTo(-14, -26); c.lineTo(10, -20); c.lineTo(34, 30); c.lineTo(18, 40); c.lineTo(-10, 6); c.closePath(); c.fill(); c.fillStyle = '#e8dcc8'; c.beginPath(); c.moveTo(-6, -22); c.lineTo(-16, -44); c.lineTo(2, -24); c.fill(); c.beginPath(); c.moveTo(6, -20); c.lineTo(14, -42); c.lineTo(14, -18); c.fill(); c.restore();
      c.strokeStyle = '#3a2a20'; c.lineWidth = 4; c.beginPath(); c.moveTo(-84, -4); c.quadraticCurveTo(-104, 20 + Math.sin(t * 3 + i) * 8, -96, 40); c.stroke();
      c.restore();
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const cv = P.scratch('bh_vacas'); if (cv.width !== W) { cv.width = W; cv.height = H; } const g2 = cv.getContext('2d'); g2.reset(); g2.clearRect(0, 0, W, H);
      VACAS.forEach(([x, y, s2, cor, m], i) => vaca(g2, x + t * (i % 2 ? 6 : -4), y, s2, cor, m, t, i));
      c.drawImage(M.broken(cv, { cell: 5, len: 12, wid: 5, passes: 2, angle: () => 0.1, seed: 143, jit: 10, skip: 0.02, base: true, sat: 1.0, warm: [250, 228, 180], cool: [80, 80, 100] }), 0, 0);
      tela(c, 'canvas_bh', '#e6dcc4');
    }
    return { draw };
  })();
})();
