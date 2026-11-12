// Cenas do vídeo "A porta e o porteiro" (acordo Mercosul–UE + EUDR) — pintadas em código, sem imagem gerada por IA.
// Recorte quadrado central (x 420..1500 de 1920x1080). Composições novas, à maneira de mestres em domínio público:
//   eu_boudin     — Eugène Boudin (1824–1898): céu enorme sobre o porto, navio graneleiro carregando
//   eu_delft      — Vermeer, "Vista de Delft" (1660–61): cidade europeia do outro lado da água, com a porta da cidade
//   eu_post       — Frans Post (1612–1680), paisagens do Brasil holandês: mata, lavoura e palmeiras sob céu alto
//   eu_post_corte — a mesma paisagem: um trecho de mata é aberto e fica cinza ("depois de 31/12/2020")
//   eu_klee       — Paul Klee, "Estradas principais e secundárias" (1929): lavouras vistas de cima; camadas do CAR por cima
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 41 }), 0, 0); c.restore(); };
  const nuvens = (g, r, n, y0, y1, cor, sombra) => { for (let i = 0; i < n; i++) { const x = 380 + r() * 1180, y = y0 + r() * (y1 - y0), w = 80 + r() * 200;
    g.fillStyle = grad(g, 0, y - w * .4, 0, y + w * .3, [[0, cor], [1, sombra]]); for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * w * 1.4, y + (r() - .5) * w * .3, w * (.35 + r() * .35), w * (.18 + r() * .14), 0, 0, TAU); g.fill(); } } };

  // ---------------------------------------------------------------- Boudin: porto sob céu imenso, navio carregando
  SCENES['eu_boudin'] = (() => {
    let plate, built = false; const HZ = 700;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(611);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#5f8fc8'], [0.6, '#a9c6e0'], [1, '#e8e4d4']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 22, 80, 520, '#fbf8f0', '#b8bcc4');
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#7aa0b0'], [0.5, '#5a8090'], [1, '#c8b890']]); g.fillRect(0, HZ, W, H - HZ);
      g.fillStyle = '#c8b48a'; poly(g, [[0, 900], [700, 860], [1920, 880], [1920, H], [0, H]]); g.fill();                      // cais e areia
      // navio graneleiro: casco vermelho e preto, superestrutura branca à popa, guindastes
      g.fillStyle = '#2a2a30'; poly(g, [[470, 640], [1200, 640], [1165, 700], [505, 700]]); g.fill();
      g.fillStyle = '#9a2a22'; poly(g, [[505, 700], [1165, 700], [1155, 716], [515, 716]]); g.fill();
      g.fillStyle = '#eeeae0'; g.fillRect(1050, 560, 110, 80); g.fillRect(1080, 520, 60, 40); g.fillStyle = '#c8402a'; g.fillRect(1100, 490, 18, 30);
      g.strokeStyle = '#d8b040'; g.lineWidth = 7; for (const x of [600, 760, 920]) { g.beginPath(); g.moveTo(x, 640); g.lineTo(x, 520); g.lineTo(x + 70, 560); g.stroke(); }
      // silos e esteira no cais
      for (const [x, h] of [[1300, 230], [1356, 250], [1412, 230]]) { g.fillStyle = grad(g, x - 26, 0, x + 26, 0, [[0, '#b8c0c8'], [0.5, '#f4f4f0'], [1, '#98a0aa']]); g.fillRect(x - 26, 880 - h, 52, h); }
      g.strokeStyle = '#6a6a70'; g.lineWidth = 10; g.beginPath(); g.moveTo(1290, 690); g.lineTo(1110, 610); g.stroke();
      // figuras pequenas no cais, de costas (Boudin)
      for (let i = 0; i < 9; i++) { const x = 480 + i * 80 + r() * 30, y = 905 + r() * 20; g.fillStyle = ['#2a3a5a', '#f0ece0', '#8a3a2a', '#3a3a3a'][i % 4]; g.fillRect(x - 7, y - 34, 14, 34); g.fillStyle = '#5a4030'; g.beginPath(); g.arc(x, y - 40, 6, 0, TAU); g.fill(); }
      return M.broken(a, { cell: 7, len: 18, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.1 + Math.sin(x * 0.006) * 0.4 : 0.02, seed: 61, jit: 14, skip: 0.06, sat: 1.1, warm: [255, 236, 200], cool: [110, 130, 180] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const r = rng(17 + Math.floor(t * 12)); c.fillStyle = 'rgba(255,250,235,.55)';                                          // brilho da água
      for (let i = 0; i < 140; i++) { const x = 420 + r() * 1080, y = 720 + r() * 140; c.fillRect(x, y, 10 + r() * 30, 2.5); }
      c.save(); c.fillStyle = 'rgba(230,200,120,.85)'; for (let i = 0; i < 40; i++) { const k = (t * .8 + i / 40) % 1; c.beginPath(); c.arc(lerp(1285, 1115, k), lerp(688, 612, k) - 6, 5, 0, TAU); c.fill(); } c.restore();   // grãos subindo pela esteira
      tela(c, 'canvas_bd', '#e8dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Vermeer: a cidade europeia, com a porta, do outro lado da água
  SCENES['eu_delft'] = (() => {
    let plate, built = false; const HZ = 560;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(711);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#6f93b8'], [0.7, '#c8d4dc'], [1, '#e4e0d0']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 14, 60, 330, '#f6f4ec', '#9aa2ae');
      // cidade: casario, telhados vermelhos, duas torres e a porta (arco escuro com torreões)
      for (let i = 0; i < 26; i++) { const x = 380 + i * 46, h = 60 + r() * 70; g.fillStyle = ['#8a6a50', '#a07a5a', '#6a5a4a', '#b08a62'][i % 4]; g.fillRect(x, HZ - h, 46, h); g.fillStyle = ['#a8402a', '#6a3a2a', '#8a4a32'][i % 3]; poly(g, [[x - 2, HZ - h], [x + 23, HZ - h - 30], [x + 48, HZ - h]]); g.fill(); }
      g.fillStyle = '#5a4a3e'; g.fillRect(860, HZ - 210, 200, 210); g.fillStyle = '#4a3a30'; g.fillRect(840, HZ - 260, 50, 260); g.fillRect(1030, HZ - 260, 50, 260);
      g.fillStyle = '#2a3440'; poly(g, [[835, HZ - 260], [865, HZ - 320], [895, HZ - 260]]); g.fill(); poly(g, [[1025, HZ - 260], [1055, HZ - 320], [1085, HZ - 260]]); g.fill();
      g.fillStyle = '#1e1a18'; g.beginPath(); g.moveTo(915, HZ); g.lineTo(915, HZ - 90); g.arc(960, HZ - 90, 45, Math.PI, 0); g.lineTo(1005, HZ); g.fill();     // a porta
      g.fillStyle = '#d8ccb0'; g.fillRect(1260, HZ - 280, 40, 280); g.fillStyle = '#3a4a5a'; poly(g, [[1252, HZ - 280], [1280, HZ - 360], [1308, HZ - 280]]); g.fill();
      // água larga e cais em primeiro plano
      g.fillStyle = grad(g, 0, HZ, 0, 900, [[0, '#5a6a6a'], [1, '#3a4a50']]); g.fillRect(0, HZ, W, 340);
      g.fillStyle = grad(g, 0, 880, 0, H, [[0, '#c8b080'], [1, '#8a7450']]); poly(g, [[0, 900], [1920, 870], [1920, H], [0, H]]); g.fill();
      g.fillStyle = '#2a3a4a'; poly(g, [[560, 640], [760, 640], [740, 672], [580, 672]]); g.fill(); g.fillStyle = '#3a3028'; poly(g, [[1180, 700], [1420, 700], [1400, 732], [1200, 732]]); g.fill();
      return M.broken(a, { cell: 6, len: 13, wid: 5, passes: 2, angle: (x, y) => y < HZ ? 0.05 : 0.02, seed: 71, jit: 10, skip: 0.06, sat: 1.0, warm: [250, 232, 190], cool: [90, 110, 150] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'soft-light'; c.globalAlpha = 0.35; c.fillStyle = grad(c, 0, 0, W, 0, [[0, 'rgba(0,0,0,0)'], [0.45, '#fff2c0'], [0.6, 'rgba(0,0,0,0)']]); c.translate(t * 40, 0); c.fillRect(-400, 0, W + 800, 560); c.restore();   // luz que passa sobre a cidade
      const r = rng(3 + Math.floor(t * 8)); c.fillStyle = 'rgba(240,236,220,.5)'; for (let i = 0; i < 70; i++) c.fillRect(420 + r() * 1080, 570 + r() * 300, 16 + r() * 30, 2);
      tela(c, 'canvas_dl', '#e6dcc6');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Frans Post: mata, lavoura e palmeiras sob céu alto; variante com corte
  function postPlate() {
    const a = P.canvas(), g = a.getContext('2d'), r = rng(811), HZ = 600;
    g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#7aa4cc'], [0.6, '#c8dce4'], [1, '#f0e8cc']]); g.fillRect(0, 0, W, HZ);
    nuvens(g, r, 12, 120, 420, '#fbf8ee', '#c4c8cc');
    g.fillStyle = '#6a8a7a'; g.beginPath(); g.moveTo(0, HZ); g.quadraticCurveTo(700, HZ - 40, 1300, HZ - 20); g.quadraticCurveTo(1650, HZ - 30, 1920, HZ); g.lineTo(1920, HZ + 20); g.lineTo(0, HZ + 20); g.fill();
    // mata nativa (direita) e lavoura de soja (esquerda), planície em faixas
    g.fillStyle = '#2f5a2a'; poly(g, [[1000, 610], [1920, 590], [1920, 860], [1060, 820]]); g.fill();
    for (let i = 0; i < 260; i++) { const x = 1000 + r() * 920, y = 600 + r() * 240; g.fillStyle = ['#2a4a22', '#3f6a30', '#1e3a1a', '#5a8040'][i % 4]; g.beginPath(); g.ellipse(x, y, 18 + r() * 22, 12 + r() * 12, 0, 0, TAU); g.fill(); }
    g.fillStyle = '#9ac050'; poly(g, [[0, 620], [1000, 610], [1060, 820], [0, 860]]); g.fill();
    g.strokeStyle = 'rgba(60,110,40,.5)'; g.lineWidth = 3; for (let k = 0; k < 40; k++) { g.beginPath(); g.moveTo(k * 26, 620); g.lineTo(-200 + k * 34, 860); g.stroke(); }
    g.fillStyle = '#c8a860'; poly(g, [[0, 860], [1920, 840], [1920, H], [0, H]]); g.fill();
    g.fillStyle = '#d8bc78'; poly(g, [[880, 860], [1000, 860], [1120, H], [760, H]]); g.fill();                                   // caminho de terra
    for (let i = 0; i < 160; i++) { const x = 380 + r() * 1180, y = 930 + r() * 160; if (x > 800 && x < 1100) continue; g.fillStyle = ['#1e2a18', '#2a3a20', '#3a4a26', '#4a5a2a'][i % 4]; g.beginPath(); g.ellipse(x, y, 30 + r() * 40, 18 + r() * 26, r() * 2, 0, TAU); g.fill(); }   // vegetação escura (Post)
    g.fillStyle = '#5a3a24'; g.fillRect(930, 900, 26, 14); g.fillRect(975, 905, 26, 14); g.fillStyle = '#e8dcc0'; g.fillRect(944, 884, 10, 18);   // carro de boi pequeno e tropeiro de costas
    // engenho branco ao longe (Post) e palmeiras + cactos em primeiro plano, como moldura
    g.fillStyle = '#f2ece0'; g.fillRect(640, 580, 70, 34); g.fillStyle = '#a8502a'; poly(g, [[632, 582], [675, 560], [718, 582]]); g.fill();
    const palm = (x, y, h) => { g.strokeStyle = '#5a4a30'; g.lineWidth = 9; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 20, y - h / 2, x + 8, y - h); g.stroke();
      for (let k = 0; k < 9; k++) { const a2 = -Math.PI + k / 8 * Math.PI; g.strokeStyle = '#2e4a24'; g.lineWidth = 6; g.beginPath(); g.moveTo(x + 8, y - h); g.quadraticCurveTo(x + 8 + Math.cos(a2) * 60, y - h - 30, x + 8 + Math.cos(a2) * 110, y - h + Math.abs(Math.sin(a2)) * 10 + 40); g.stroke(); } };
    palm(500, 1000, 460); palm(1380, 1020, 520); palm(1450, 1030, 380);
    g.fillStyle = '#2a3a22'; for (const [x, h] of [[440, 160], [470, 210], [1500, 180]]) { g.fillRect(x, 1030 - h, 22, h); g.fillRect(x - 24, 1030 - h * .6, 22, 10); g.fillRect(x - 24, 1030 - h * .6 - 50, 12, 50); }
    return { cv: M.broken(a, { cell: 7, len: 14, wid: 5, passes: 2, angle: (x, y) => y < HZ ? 0.04 : 0.1, seed: 81, jit: 10, skip: 0.06, sat: 1.05, warm: [250, 230, 180], cool: [90, 110, 120] }), HZ };
  }
  let POST = null;
  const CORTE = [[1160, 650], [1420, 640], [1460, 760], [1180, 780]];                 // trecho de mata que é aberto
  function postDraw(c, t, corte) {
    if (!POST) POST = postPlate();
    c.drawImage(POST.cv, 0, 0);
    const r = rng(23); c.save(); c.strokeStyle = 'rgba(60,40,30,.8)'; c.lineWidth = 2.5;                                       // aves
    for (let i = 0; i < 6; i++) { const x = 600 + i * 60 + t * 25, y = 260 + i * 12 + Math.sin(t * 2 + i) * 5, f = Math.sin(t * 7 + i) * 7; c.beginPath(); c.moveTo(x - 12, y + f * .5); c.quadraticCurveTo(x - 5, y - f, x, y); c.quadraticCurveTo(x + 5, y - f, x + 12, y + f * .5); c.stroke(); }
    c.restore();
    if (corte) {
      const k = ss(corte[0], corte[0] + 1.6, t), g2 = ss(corte[1], corte[1] + 1.0, t);
      if (k > 0) { c.save(); poly(c, CORTE.map(([x, y]) => [lerp(1310, x, k), lerp(710, y, k)])); c.clip();
        c.fillStyle = `rgb(${lerp(168, 130, g2) | 0},${lerp(128, 128, g2) | 0},${lerp(80, 126, g2) | 0})`; c.fillRect(1100, 600, 420, 220);
        for (let i = 0; i < 40; i++) { c.fillStyle = `rgba(${lerp(90, 90, g2)},${lerp(70, 90, g2)},${lerp(50, 92, g2)},.6)`; c.fillRect(1160 + r() * 300, 650 + r() * 120, 30 + r() * 30, 3); }    // tocos e leiras
        c.restore();
        if (g2 > 0) { c.save(); c.globalAlpha = g2; c.strokeStyle = '#f6efd8'; c.setLineDash([12, 8]); c.lineWidth = 4; poly(c, CORTE); c.stroke(); c.restore(); } }
    }
    tela(c, 'canvas_fp', '#e8dcc2');
  }
  SCENES['eu_post'] = { draw(c, lt) { postDraw(c, Math.max(0, lt), null); } };
  SCENES['eu_post_corte'] = { draw(c, lt) { const q = new URLSearchParams(location.search); postDraw(c, Math.max(0, lt), [+(q.get('c0') || 3.6), +(q.get('c1') || 5.4)]); } };

  // ---------------------------------------------------------------- Klee: lavouras vistas de cima; camadas do CAR por cima
  SCENES['eu_klee'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(911);
      g.fillStyle = '#d8c89a'; g.fillRect(0, 0, W, H);
      const COL = ['#e2b84a', '#8cb050', '#c8783a', '#5a9a5a', '#e8d070', '#a8c070', '#b85a3a', '#6a8a4a', '#d89a50', '#f0c868'];
      let y = 0; while (y < H) { const h = 24 + r() * 70; let x = 380; while (x < 1540) { const w = 60 + r() * 220; g.fillStyle = COL[(r() * COL.length) | 0]; g.fillRect(x, y, w, h); x += w; } y += h; }   // faixas de Klee
      g.strokeStyle = 'rgba(60,40,30,.55)'; g.lineWidth = 3; for (let i = 0; i < 26; i++) { const yy = r() * H; g.beginPath(); g.moveTo(380, yy); g.lineTo(1540, yy + (r() - .5) * 40); g.stroke(); }
      g.strokeStyle = '#efe4c8'; g.lineWidth = 10; g.beginPath(); g.moveTo(420, 980); g.bezierCurveTo(800, 700, 1100, 640, 1500, 160); g.stroke();       // estrada principal
      g.fillStyle = '#2f5a2a'; g.beginPath(); g.ellipse(1250, 820, 150, 110, 0.4, 0, TAU); g.fill();                                                   // reserva de mata
      return M.broken(a, { cell: 6, len: 14, wid: 5, passes: 2, angle: (x, y) => 0.02 + Math.sin(y * 0.03) * 0.15, seed: 91, jit: 12, skip: 0.05, sat: 1.1, warm: [255, 230, 170], cool: [110, 110, 150] });
    }
    const CAR = [[640, 300], [1220, 260], [1360, 620], [1380, 940], [700, 960], [580, 620]];
    const draw = (c, lt) => {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), q = new URLSearchParams(location.search), T = ['tcar', 'tdes', 'temb', 'tprot'].map((k, i) => +(q.get(k) || [8.1, 9.1, 9.9, 10.9][i]));
      c.save(); const z = 1 + 0.06 * ss(0, 15, t); c.translate(960, 540); c.scale(z, z); c.translate(-960, -540); c.drawImage(plate, 0, 0); c.restore();
      const per = (pts) => { let L = 0; for (let i = 0; i < pts.length; i++) { const [x1, y1] = pts[i], [x2, y2] = pts[(i + 1) % pts.length]; L += Math.hypot(x2 - x1, y2 - y1); } return L; };
      const k = ss(T[0], T[0] + 1.2, t);                                                       // 1) perímetro do CAR, desenhado
      if (k > 0) { c.save(); c.strokeStyle = '#fff8e0'; c.lineWidth = 7; c.setLineDash([per(CAR) * k, 9999]); poly(c, CAR); c.stroke(); c.restore(); }
      const kd = ss(T[1], T[1] + .6, t);                                                      // 2) registro de desmatamento: mancha marcada
      if (kd > 0) { c.save(); c.globalAlpha = kd; c.strokeStyle = '#e8502a'; c.lineWidth = 5; c.beginPath(); c.ellipse(820, 420, 90, 60, 0.3, 0, TAU); c.stroke(); c.restore(); }
      const ke = ss(T[2], T[2] + .6, t);                                                      // 3) embargo: hachura vermelha
      if (ke > 0) { c.save(); c.globalAlpha = ke * .85; c.beginPath(); c.rect(1020, 360, 220, 160); c.clip(); c.strokeStyle = '#c0281a'; c.lineWidth = 6; for (let i = -10; i < 30; i++) { c.beginPath(); c.moveTo(1020 + i * 22, 360); c.lineTo(1020 + i * 22 - 160, 520); c.stroke(); } c.restore();
        c.save(); c.globalAlpha = ke; c.strokeStyle = '#c0281a'; c.lineWidth = 4; c.strokeRect(1020, 360, 220, 160); c.restore(); }
      const kp = ss(T[3], T[3] + .6, t);                                                      // 4) área protegida: contorno verde
      if (kp > 0) { c.save(); c.globalAlpha = kp; c.strokeStyle = '#7fe08a'; c.lineWidth = 6; c.setLineDash([16, 10]); c.beginPath(); c.ellipse(1250, 820, 170, 128, 0.4, 0, TAU); c.stroke(); c.restore(); }
      tela(c, 'canvas_kl', '#e6dcc4');
    };
    return { draw };
  })();
})();
