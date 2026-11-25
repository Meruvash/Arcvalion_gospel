// Cenas do vídeo "Comprou a terra e não é dono?" — pintadas em código, sem imagem gerada por IA.
// Recorte central x 420..1500. Composições novas, à maneira de mestres em domínio público:
//   es_terborch     — Gerard ter Borch (1617–1681): o oficial do registro, de costas, à mesa com o livro de matrículas;
//                     a luz da janela no cetim; a pena escrevendo
//   es_hoogstraten  — Samuel van Hoogstraten (1627–1678): trompe-l'œil de uma gaveta entreaberta com a escritura amarrada em
//                     fita vermelha, um molho de chaves e o pó subindo na luz
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 91 }), 0, 0); c.restore(); };

  // ---------------------------------------------------------------- ter Borch: o oficial do registro
  SCENES['es_terborch'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2301);
      g.fillStyle = grad(g, 0, 0, W, 0, [[0, '#2a241c'], [.6, '#4a3e2e'], [1, '#2a241c']]); g.fillRect(0, 0, W, H);         // fundo escuro (ter Borch)
      g.fillStyle = grad(g, 1100, 0, 1500, 0, [[0, 'rgba(240,226,190,.0)'], [1, 'rgba(240,226,190,.22)']]); g.fillRect(1100, 0, 400, H);   // luz da janela à direita
      g.fillStyle = '#3a2a1c'; g.fillRect(560, 640, 760, 440);                                                               // mesa
      g.fillStyle = '#5a1a14'; poly(g, [[540, 620], [1340, 620], [1380, 760], [500, 760]]); g.fill();                      // toalha
      g.fillStyle = '#e8dcc0'; poly(g, [[1090, 600], [1350, 584], [1366, 652], [1098, 672]]); g.fill();                     // livro de matrículas aberto
      g.strokeStyle = '#7a6a50'; g.lineWidth = 2; for (let k = 0; k < 7; k++) { g.beginPath(); g.moveTo(1104, 608 + k * 8); g.lineTo(1346, 594 + k * 8); g.stroke(); }
      g.fillStyle = '#1a1612'; ell(g, 1420, 630, 26, 12, 0, '#1a1612'); g.fillRect(1400, 600, 40, 32);                     // tinteiro
      // o oficial, de costas: casaco escuro, gola branca larga, cabelo longo, chapéu
      g.fillStyle = '#18140f'; poly(g, [[700, 1080], [740, 640], [820, 560], [960, 560], [1040, 640], [1080, 1080]]); g.fill();
      g.fillStyle = '#ece6d8'; poly(g, [[800, 572], [980, 572], [1000, 610], [780, 610]]); g.fill();                       // gola
      ell(g, 890, 520, 64, 70, 0, '#3a2a1e'); ell(g, 890, 470, 120, 26, 0, '#14100c'); ell(g, 890, 440, 62, 40, 0, '#14100c');   // cabelo e chapéu
      g.fillStyle = '#c8b8a0'; poly(g, [[1040, 650], [1180, 600], [1190, 618], [1050, 672]]); g.fill();                     // braço com a manga clara
      return M.broken(a, { cell: 7, len: 14, wid: 6, passes: 2, angle: (x, y) => 1.4 + Math.sin(x * .004) * .3, seed: 231, jit: 12, skip: 0.04, sat: .95, warm: [250, 220, 170], cool: [60, 60, 70] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const px = 1230 + Math.sin(t * 6) * 14, py = 628 + Math.abs(Math.sin(t * 3)) * 8;                                   // a pena escrevendo
      c.save(); c.strokeStyle = '#f2ecd8'; c.lineWidth = 5; c.beginPath(); c.moveTo(px, py); c.lineTo(px + 50, py - 110); c.stroke();
      c.strokeStyle = '#d8d0b8'; c.lineWidth = 12; c.beginPath(); c.moveTo(px + 30, py - 70); c.lineTo(px + 52, py - 112); c.stroke(); c.restore();
      const n = Math.floor(t * 3) % 40; c.save(); c.strokeStyle = 'rgba(40,30,20,.8)'; c.lineWidth = 2;                       // linhas novas no livro
      for (let k = 0; k < Math.min(n, 18); k++) { c.beginPath(); c.moveTo(1110 + k * 12, 650); c.lineTo(1116 + k * 12, 646); c.stroke(); } c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; { const gr = c.createLinearGradient(1050, 0, 1500, 0); gr.addColorStop(0, 'rgba(255,236,190,0)'); gr.addColorStop(1, `rgba(255,236,190,${.14 + .05 * Math.sin(t)})`); c.fillStyle = gr; c.fillRect(1050, 0, 450, H); } c.restore();
      tela(c, 'canvas_tb', '#e4dac2');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Hoogstraten: a escritura na gaveta
  SCENES['es_hoogstraten'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(2401);
      g.fillStyle = grad(g, 0, 0, 0, H, [[0, '#6a4a2a'], [1, '#3a2614']]); g.fillRect(0, 0, W, H);                          // frente da cômoda
      g.strokeStyle = 'rgba(30,18,8,.5)'; g.lineWidth = 3; for (let i = 0; i < 40; i++) { g.beginPath(); g.moveTo(420, 30 + i * 26 + r() * 6); g.bezierCurveTo(800, 20 + i * 26, 1200, 40 + i * 26, 1500, 30 + i * 26); g.stroke(); }   // veios
      g.fillStyle = '#2a1a0c'; g.fillRect(520, 420, 880, 420);                                                               // vão da gaveta
      g.fillStyle = grad(g, 0, 380, 0, 460, [[0, '#8a6a42'], [1, '#5a3e22']]); poly(g, [[480, 760], [1440, 760], [1500, 880], [420, 880]]); g.fill();   // gaveta puxada (frente)
      g.fillStyle = '#c8a050'; ell(g, 960, 820, 40, 14, 0, '#c8a050');                                                       // puxador de latão
      g.fillStyle = '#efe4c4'; poly(g, [[640, 520], [1180, 480], [1220, 740], [680, 770]]); g.fill();                        // a escritura dobrada
      g.strokeStyle = '#8a7a5a'; g.lineWidth = 2; for (let k = 0; k < 9; k++) { g.beginPath(); g.moveTo(680, 560 + k * 20); g.lineTo(1170, 525 + k * 20); g.stroke(); }
      g.fillStyle = '#a8201a'; poly(g, [[880, 490], [920, 488], [960, 770], [920, 772]]); g.fill();                          // fita vermelha
      ell(g, 925, 640, 40, 22, .3, '#b02a20'); ell(g, 905, 660, 18, 30, -.4, '#8a1a14');                                     // laço e lacre
      [[1260, 640], [1300, 660], [1280, 690]].forEach(([x, y], k) => { g.strokeStyle = '#b8a070'; g.lineWidth = 8; g.beginPath(); g.arc(x, y, 26, 0, TAU); g.stroke(); g.fillStyle = '#a89060'; g.fillRect(x + 20, y - 4, 70, 9); });   // molho de chaves
      return M.broken(a, { cell: 6, len: 13, wid: 5, passes: 2, angle: (x, y) => 0.05 + Math.sin(y * .01) * .1, seed: 241, jit: 10, skip: 0.03, sat: 1.0, warm: [250, 220, 170], cool: [70, 60, 50] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; const gr = c.createLinearGradient(1500, 0, 600, 900); gr.addColorStop(0, 'rgba(255,230,170,.35)'); gr.addColorStop(1, 'rgba(255,230,170,0)'); c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      const r = rng(77); c.fillStyle = 'rgba(255,240,200,.55)'; for (let i = 0; i < 50; i++) { const x = 600 + r() * 800, y = (900 - (t * 18 * (r() + .4)) % 900) - r() * 100; c.fillRect(x, y, 2, 2); }   // pó subindo na luz
      tela(c, 'canvas_hg', '#e6dcc4');
    }
    return { draw };
  })();
})();
