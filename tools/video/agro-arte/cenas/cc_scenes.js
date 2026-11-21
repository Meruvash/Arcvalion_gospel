// Cenas do vídeo "Papel atrasado trava a fazenda?" (CCIR) — pintadas em código. Recorte central x 420..1500.
// Composições novas, à maneira de mestres em domínio público:
//   cc_cezanne  — Paul Cézanne (1839–1906): a fazenda vista do alto, retalhada em lotes como no cadastro, pinceladas
//                 construtivas em diagonal, serra azulada ao fundo
//   cc_corot    — Camille Corot (1796–1875): a árvore grande junto da cerca e da porteira, a pasta de papéis no
//                 mourão (sem figura humana); verdes prateados, luz de manhã
//   cc_courbet  — Gustave Courbet (1819–1877): o balcão escuro, livro de registro aberto, lamparina, pena no tinteiro (sem figura humana)
//   cc_seurat   — Georges Seurat (1859–1891): a praça da cidade pequena com a agência do banco, em pontos de cor (sem figura humana)
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 97 }), 0, 0); c.restore(); };
  const figura = (g, x, y, s, roupa, pele, chapeu, calca = '#3a2e24') => {
    g.fillStyle = roupa; poly(g, [[x - 34 * s, y], [x - 26 * s, y - 150 * s], [x + 26 * s, y - 150 * s], [x + 34 * s, y]]); g.fill();
    g.fillStyle = calca; g.fillRect(x - 22 * s, y, 16 * s, 80 * s); g.fillRect(x + 6 * s, y, 16 * s, 80 * s);
    ell(g, x, y - 172 * s, 22 * s, 25 * s, 0, pele);
    if (chapeu) { ell(g, x, y - 188 * s, 50 * s, 11 * s, 0, chapeu); ell(g, x, y - 200 * s, 25 * s, 15 * s, 0, chapeu); }
  };
  const nuvens = (c, t, seed, y0, cor, vel) => {
    const r = rng(seed); c.save(); c.globalAlpha = .55;
    for (let i = 0; i < 7; i++) { const x = 300 + ((r() * 1400 + t * vel * (0.6 + r())) % 1500), y = y0 + r() * 90; ell(c, x, y, 120 + r() * 80, 26 + r() * 14, 0, cor); ell(c, x + 60, y - 14, 80, 24, 0, cor); }
    c.restore();
  };

  // ---------------------------------------------------------------- Cézanne: a fazenda em lotes (o cadastro)
  SCENES['cc_cezanne'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 300, [[0, '#7aa6cc'], [1, '#d8e4e0']]); g.fillRect(0, 0, W, 300);
      g.fillStyle = '#6a7aa0'; poly(g, [[300, 300], [620, 170], [820, 230], [1040, 120], [1320, 220], [1620, 300]]); g.fill();   // a serra
      g.fillStyle = '#8a9a8a'; poly(g, [[300, 300], [1620, 300], [1620, 330], [300, 330]]); g.fill();
      // os lotes, em perspectiva: faixas que se abrem para baixo
      const cores = ['#a8b85a', '#d8b060', '#6a9a4a', '#c88a4a', '#8ab060', '#e0c070', '#5a8a4a', '#b87a3a', '#9ac06a', '#d0a050', '#7aa050', '#c8945a'];
      const linhas = [320, 380, 470, 600, 780, 1080], col = (y, k) => 960 + (k - 3) * (120 + (y - 300) * 0.9);
      let n = 0;
      for (let i = 0; i < linhas.length - 1; i++) for (let k = 0; k < 6; k++) {
        const y0 = linhas[i], y1 = linhas[i + 1];
        g.fillStyle = cores[(n++ * 5 + i) % cores.length];
        poly(g, [[col(y0, k), y0], [col(y0, k + 1), y0], [col(y1, k + 1), y1], [col(y1, k), y1]]); g.fill();
      }
      g.strokeStyle = 'rgba(70,50,30,.55)'; g.lineWidth = 5;   // as divisas
      for (let k = 0; k <= 6; k++) { g.beginPath(); g.moveTo(col(320, k), 320); g.lineTo(col(1080, k), 1080); g.stroke(); }
      linhas.forEach(y => { g.beginPath(); g.moveTo(col(y, 0), y); g.lineTo(col(y, 6), y); g.stroke(); });
      g.fillStyle = '#b8603a'; poly(g, [[930, 330], [990, 330], [1210, 1080], [1090, 1080]]); g.fill();   // a estrada de terra vermelha
      g.fillStyle = '#f0e8d8'; g.fillRect(1240, 410, 110, 60); g.fillStyle = '#a84a2a'; poly(g, [[1228, 414], [1295, 380], [1362, 414]]); g.fill();   // a sede
      for (let k = 0; k < 5; k++) ell(g, 1400 + k * 34, 440, 22, 34, 0, '#3a6a3a');   // as árvores da sede
      return M.broken(a, { cell: 9, len: 22, wid: 9, passes: 3, angle: () => -0.75, seed: 523, jit: 14, skip: 0.04, sat: 1.08, warm: [250, 225, 170], cool: [90, 110, 160] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      nuvens(c, t, 17, 40, 'rgba(250,250,245,.8)', 18);
      const x = lerp(990, 1130, (t * 0.06) % 1), y = lerp(360, 1000, (t * 0.06) % 1);   // a caminhonete subindo a estrada
      ell(c, x, y, 18 + (y - 360) * .03, 9 + (y - 360) * .015, 0, '#e8e0d0');
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,240,200,${.06 + .03 * Math.sin(t * 1.3)})`; c.fillRect(0, 0, W, H); c.restore();
      tela(c, 'canvas_cz', '#ece2cc');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Corot: a conversa na porteira
  SCENES['cc_corot'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#b8c8c8'], [1, '#eae6d4']]); g.fillRect(0, 0, W, 560);
      g.fillStyle = '#8a9a7a'; poly(g, [[0, 560], [700, 500], [1300, 540], [1920, 500], [1920, 620], [0, 620]]); g.fill();
      g.fillStyle = grad(g, 0, 600, 0, H, [[0, '#9aa878'], [1, '#5a6a42']]); g.fillRect(0, 600, W, H - 600);
      g.fillStyle = '#c8b48a'; poly(g, [[880, 600], [940, 600], [1180, 1080], [900, 1080]]); g.fill();   // o caminho
      g.fillStyle = '#4a3a2a'; g.fillRect(560, 250, 46, 560);   // o tronco da árvore grande
      for (let k = 0; k < 9; k++) ell(g, 420 + (k % 3) * 150, 160 + Math.floor(k / 3) * 110, 170, 110, 0, ['#6a7a5a', '#7a8a68', '#5a6a4a'][k % 3]);
      g.fillStyle = '#7a6040';   // a cerca e a porteira
      for (let k = 0; k < 3; k++) g.fillRect(960, 700 + k * 50, 520, 14);
      for (let k = 0; k < 4; k++) g.fillRect(960 + k * 170, 680, 18, 190);
      g.fillStyle = '#8a6a44'; poly(g, [[1000, 712], [1140, 762], [1140, 776], [1000, 726]]); g.fill();
      g.fillStyle = '#c8a070'; g.fillRect(1118, 640, 58, 46); g.fillStyle = '#a8804a'; g.fillRect(1118, 640, 58, 6);   // a pasta de papéis deixada no mourão
      return M.broken(a, { cell: 7, len: 14, wid: 9, passes: 3, angle: (x, y) => Math.sin(x * .01 + y * .02) * .9, seed: 611, jit: 12, skip: 0.05, sat: 0.92, warm: [240, 232, 200], cool: [120, 140, 140] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const r = rng(53); c.fillStyle = 'rgba(230,236,210,.55)';
      for (let i = 0; i < 40; i++) { const x = 300 + r() * 520 + Math.sin(t * 1.7 + i) * 6, y = 60 + r() * 360 + Math.cos(t * 1.3 + i) * 4; c.fillRect(x, y, 5, 3); }   // as folhas tremendo
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,250,230,${.07 + .03 * Math.sin(t)})`; c.fillRect(0, 0, W, H); c.restore();
      tela(c, 'canvas_co', '#ece6d4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Courbet: o livro de registro
  SCENES['cc_courbet'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, W, H, [[0, '#2a2018'], [1, '#14100c']]); g.fillRect(0, 0, W, H);
      g.fillStyle = '#3a2c20'; for (let k = 0; k < 5; k++) g.fillRect(480 + k * 200, 120, 150, 380);   // as estantes de livros
      for (let k = 0; k < 40; k++) { g.fillStyle = ['#5a3a24', '#6a4a2a', '#4a3a2a', '#7a5a34'][k % 4]; g.fillRect(490 + (k % 8) * 125 + (k % 3) * 6, 140 + Math.floor(k / 8) * 72, 26, 62); }
      g.fillStyle = '#5a3a22'; g.fillRect(380, 640, 1160, 440);   // o balcão
      g.fillStyle = '#eee4c8'; poly(g, [[700, 700], [960, 680], [1220, 700], [1240, 820], [960, 840], [680, 820]]); g.fill();   // o livro aberto
      g.strokeStyle = 'rgba(80,60,40,.5)'; g.lineWidth = 2; for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(720, 712 + k * 14); g.lineTo(940, 694 + k * 14); g.stroke(); g.beginPath(); g.moveTo(980, 694 + k * 14); g.lineTo(1210, 712 + k * 14); g.stroke(); }
      ell(g, 1360, 600, 40, 60, 0, '#c89a4a'); g.fillStyle = '#6a4a24'; g.fillRect(1340, 650, 40, 40);   // a lamparina
      return M.broken(a, { cell: 8, len: 16, wid: 10, passes: 3, angle: (x, y) => Math.cos(y * .02) * .6, seed: 733, jit: 10, skip: 0.03, sat: 1.0, warm: [230, 190, 130], cool: [60, 60, 70] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const fl = .55 + .12 * Math.sin(t * 9) + .06 * Math.sin(t * 23);   // a chama da lamparina
      const gr = c.createRadialGradient(1360, 600, 10, 1360, 600, 700); gr.addColorStop(0, `rgba(255,200,110,${.45 * fl})`); gr.addColorStop(1, 'rgba(255,200,110,0)');
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      ell(c, 1280, 800, 26, 16, 0, '#1a1410'); c.strokeStyle = '#e8dcc0'; c.lineWidth = 4; c.beginPath(); c.moveTo(1280, 796); c.lineTo(1310 + Math.sin(t * 1.5) * 3, 720); c.stroke();   // a pena no tinteiro
      const vira = (t * 0.25) % 1, fx = 960 + Math.cos(vira * Math.PI) * 250;   // a folha do livro virando devagar
      c.fillStyle = `rgba(238,228,200,${.55 * Math.sin(vira * Math.PI)})`; poly(c, [[960, 684], [fx, 690 - Math.sin(vira * Math.PI) * 60], [fx, 830 - Math.sin(vira * Math.PI) * 60], [960, 840]]); c.fill();
      tela(c, 'canvas_cb', '#d8cbb0');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Seurat: a praça com a agência do banco
  SCENES['cc_seurat'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 380, [[0, '#8ab8e0'], [1, '#e8eef0']]); g.fillRect(0, 0, W, 380);
      g.fillStyle = '#e8dcc0'; g.fillRect(560, 200, 800, 420);   // a agência
      g.fillStyle = '#c8b890'; poly(g, [[540, 210], [960, 120], [1380, 210]]); g.fill();
      for (let k = 0; k < 6; k++) { g.fillStyle = '#f4ecdc'; g.fillRect(610 + k * 140, 260, 40, 360); }   // as colunas
      g.fillStyle = '#3a5a7a'; g.fillRect(880, 440, 160, 180);   // a porta
      g.fillStyle = '#f0c24b'; g.fillRect(700, 214, 520, 34);   // a faixa da fachada (sem nome de banco)
      g.fillStyle = grad(g, 0, 620, 0, H, [[0, '#d8c8a0'], [1, '#b8a070']]); g.fillRect(0, 620, W, H - 620);   // a praça
      g.fillStyle = '#5a4a3a'; g.fillRect(480, 360, 24, 300); for (let k = 0; k < 7; k++) ell(g, 492 + Math.cos(k) * 90, 350 + Math.sin(k) * 30, 110, 22, k * .9, '#3a7a4a');   // a palmeira
      g.fillStyle = '#2a6a3a'; ell(g, 1440, 520, 120, 160, 0, '#3a7a3a');
      return M.broken(a, { cell: 6, len: 6, wid: 6, passes: 3, angle: () => 0, seed: 829, jit: 26, skip: 0.02, sat: 1.15, warm: [255, 220, 150], cool: [110, 130, 220] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const r = rng(71);
      for (let i = 0; i < 260; i++) { const x = 420 + r() * 1080, y = r() * H, a = .25 + .2 * Math.sin(t * 2 + i); c.fillStyle = `rgba(${r() > .5 ? '255,230,160' : '140,160,240'},${a})`; c.fillRect(x, y, 6, 6); }   // os pontos vibrando
      const r2 = rng(5); c.fillStyle = 'rgba(250,250,250,.7)'; for (let i = 0; i < 4; i++) { const x = 420 + ((r2() * 1080 + t * 40) % 1080); ell(c, x, 34 + i * 20, 60, 12, 0, 'rgba(250,250,250,.6)'); }   // nuvens em pontos
      tela(c, 'canvas_se', '#ece2cc');
    }
    return { draw };
  })();
})();
