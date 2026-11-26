// Cenas do vídeo "Poço artesiano é crime?". Padrão de DIRECAO_ARTISTICA.md e DIRECAO_MOTION.md (26/11/2026).
//   pc_grimm — à maneira de Georg Grimm (1846–1887), paisagista do Brasil: o cerrado no fim da tarde, o cata-vento de ferro
//              sobre o poço e a caixa d'água de madeira (foco no terço direito), trilha que leva até eles, veredas com buritis.
//   pc_corte — prancha de geologia do séc. XIX (gravura aquarelada): corte do terreno mostrando o poço descendo pelas
//              camadas até o aquífero. Função (DIRECAO_MOTION.md): LOCALIZAR + REVELAR — a água de debaixo da terra.
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const X0 = 420;                                   // borda esquerda do recorte quadrado
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const rgba = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
  const mix = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.14; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 211 }), 0, 0); c.restore(); };

  // Nuvem com volume: muitos lóbulos, base sombreada fria, topo aceso quente pelo sol baixo à esquerda.
  function nuvem(g, x, y, s, seed, luz = [255, 236, 200], sombra = [150, 150, 175]) {
    const r = rng(seed);
    for (let i = 0; i < 26; i++) {
      const a = r() * TAU, d = r() * 120 * s, lx = x + Math.cos(a) * d * 1.7, ly = y + Math.sin(a) * d * 0.45, rr = (40 + r() * 70) * s;
      const t = clamp((y + 40 * s - ly) / (110 * s), 0, 1);           // quanto mais alto o lóbulo, mais luz
      const gr = g.createRadialGradient(lx - rr * .3, ly - rr * .35, rr * .1, lx, ly, rr);
      gr.addColorStop(0, rgba(mix(sombra, luz, .35 + .65 * t), 1)); gr.addColorStop(.82, rgba(mix(sombra, luz, .25 + .6 * t), .97)); gr.addColorStop(1, rgba(mix(sombra, luz, .2 + .5 * t), 0));
      g.fillStyle = gr; g.beginPath(); g.arc(lx, ly, rr, 0, TAU); g.fill();
    }
  }
  // Serra: crista em fbm, cor clareando com a distância (perspectiva atmosférica).
  function serra(g, base, amp, freq, seed, cor) {
    g.fillStyle = cor; g.beginPath(); g.moveTo(0, H);
    for (let x = 0; x <= W; x += 6) g.lineTo(x, base - amp * (0.5 + P.fbm(x * freq + seed, seed * .37, 5)));
    g.lineTo(W, H); g.closePath(); g.fill();
  }
  // Tufo de capim: leque de folhas curvas.
  function tufo(g, x, y, h, cor, r, n = 9) {
    g.strokeStyle = cor; g.lineCap = 'round';
    for (let i = 0; i < n; i++) { const a = -Math.PI / 2 + (r() - .5) * 1.3, l = h * (.6 + r() * .5); g.lineWidth = 1.5 + r() * 2.5;
      g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * l * .5, y + Math.sin(a) * l * .6, x + Math.cos(a) * l + (r() - .5) * 14, y + Math.sin(a) * l); g.stroke(); }
  }

  // ---------------------------------------------------------------- Grimm: o cata-vento no cerrado
  SCENES['pc_grimm'] = (() => {
    let ceu, terra, built = false;
    const SOL = [600, 340], TX = 1190, TY = 700;                    // a torre do cata-vento (foco)
    const trilha = u => { const p0 = [560, 1130], p1 = [760, 900], p2 = [1000, 800], p3 = [TX - 20, TY + 10]; const v = 1 - u;
      return [v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0], v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1]]; };
    function cerradoArvore(g, x, y, s, r) {                         // tronco retorcido e galhos abertos; copa em cachos com sombra embaixo
      g.strokeStyle = '#3a2a1c'; g.lineCap = 'round';
      const ramo = (x0, y0, a, l, w, n) => { const x1 = x0 + Math.cos(a) * l, y1 = y0 + Math.sin(a) * l; g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo((x0 + x1) / 2 + (r() - .5) * l * .5, (y0 + y1) / 2, x1, y1); g.stroke();
        if (n > 0) { ramo(x1, y1, a - .6 + (r() - .5) * .4, l * .7, w * .62, n - 1); ramo(x1, y1, a + .5 + (r() - .5) * .4, l * .7, w * .62, n - 1); }
        else for (let i = 0; i < 9; i++) { const cx = x1 + (r() - .5) * 40 * s, cy = y1 + (r() - .5) * 18 * s; ell(g, cx, cy + 5 * s, 20 * s, 10 * s, 0, 'rgba(40,56,30,.9)'); ell(g, cx, cy, 18 * s, 11 * s, 0, rgba(mix([74, 98, 50], [120, 134, 66], r()), .95)); ell(g, cx - 6 * s, cy - 5 * s, 9 * s, 5 * s, 0, 'rgba(255,214,150,.4)'); } };
      ramo(x, y, -Math.PI / 2 + (r() - .5) * .3, 70 * s, 11 * s, 3); }
    function buriti(g, x, y, s) { g.strokeStyle = '#4a3a28'; g.lineWidth = 6 * s; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 4 * s, y - 150 * s); g.stroke();
      for (let k = 0; k < 14; k++) { const a = -Math.PI * (k / 13); g.strokeStyle = 'rgba(56,84,48,.95)'; g.lineWidth = 3 * s; g.beginPath(); g.moveTo(x + 4 * s, y - 150 * s);
        g.quadraticCurveTo(x + Math.cos(a) * 30 * s, y - 150 * s + Math.sin(a) * 40 * s - 10 * s, x + Math.cos(a) * 60 * s, y - 150 * s + Math.sin(a) * 30 * s + 10 * s); g.stroke(); } }
    function build() {
      ceu = P.canvas(); let g = ceu.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 640, [[0, '#5c7ca6'], [.5, '#b0bccb'], [.82, '#f3d6a2'], [1, '#f7c487']]); g.fillRect(0, 0, W, 640);
      const halo = g.createRadialGradient(SOL[0], SOL[1], 10, SOL[0], SOL[1], 500); halo.addColorStop(0, 'rgba(255,240,205,.95)'); halo.addColorStop(1, 'rgba(255,210,150,0)'); g.fillStyle = halo; g.fillRect(0, 0, W, 700);
      [[260, 150, 1.0, 21], [820, 110, 1.2, 22], [1380, 170, 1.05, 23], [1060, 330, .55, 24]].forEach(([x, y, s, k]) => nuvem(g, x, y, s, 600 + k));
      ceu = M.broken(ceu, { cell: 7, len: 18, wid: 9, passes: 3, angle: (x, y) => .08 + P.noise(x * .004, y * .004) * .5, seed: 2601, jit: 9, skip: 0.02, sat: 1.02, warm: [255, 228, 180], cool: [100, 120, 170] });
      terra = P.canvas(); g = terra.getContext('2d');
      serra(g, 570, 70, .0016, 41, '#9aa6b8'); serra(g, 606, 45, .0026, 47, '#7f8f86');
      const im = g.getImageData(0, 0, W, H), d = im.data;
      for (let y = 600; y < H; y++) for (let x = 0; x < W; x++) { const hz = 630 - 20 * P.fbm(x * .003 + 47, 4.7, 5); if (y < hz) continue;
        const i = (y * W + x) * 4, k = (y - hz) / (H - hz), n = P.fbm(x * .005, y * .015, 4);
        let c = mix([186, 168, 104], [104, 110, 58], Math.pow(k, .8)); c = mix(c, [214, 182, 110], clamp(.3 + n, 0, 1) * (1 - k) * .7);    // cerrado seco, dourado
        c = mix(c, [255, 214, 140], clamp(1 - Math.hypot(x - SOL[0], (y - 640) * 2.4) / 1300, 0, 1) * .3); d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 255; }
      g.putImageData(im, 0, 0);
      g.fillStyle = 'rgba(70,110,70,.85)'; for (let x = 380; x < 1560; x += 6) { const y = 640 + 6 * Math.sin(x * .01); g.fillRect(x, y - 4, 7, 8 + 4 * P.noise(x * .02, 1)); }   // a vereda
      for (const [x, s] of [[520, .7], [600, .8], [1450, .75], [1500, .65]]) buriti(g, x, 646, s);
      const ra = rng(91); for (const [x, y, s] of [[690, 730, 1.0], [880, 700, .7], [1430, 790, 1.35], [480, 860, 1.5]]) cerradoArvore(g, x, y, s, ra);
      for (let u = 0; u <= 1.0001; u += .003) { const [x, y] = trilha(u), w = lerp(150, 26, u); g.fillStyle = rgba(mix([190, 120, 76], [214, 156, 106], u), 1); g.fillRect(x - w / 2, y - 3, w, 6); }
      const rt = rng(93); for (const side of [-1, 1]) for (let u = 0; u < .97; u += .012) { const [x, y] = trilha(u), w = lerp(150, 26, u); tufo(g, x + side * w * .52, y, 8 + 26 * (1 - u), rgba(mix([120, 120, 60], [196, 170, 96], rt()), .9), rt, 5); }
      // a caixa d'água: tonel de madeira com aros de ferro, sobre quatro pernas com travessas
      g.strokeStyle = '#4a3420'; g.lineWidth = 8; for (const [x0, x1] of [[TX - 150, TX - 132], [TX - 36, TX - 54], [TX - 120, TX - 112], [TX - 66, TX - 74]]) { g.beginPath(); g.moveTo(x0, TY + 4); g.lineTo(x1, TY - 168); g.stroke(); }
      g.lineWidth = 4; g.beginPath(); g.moveTo(TX - 145, TY - 40); g.lineTo(TX - 40, TY - 120); g.moveTo(TX - 40, TY - 40); g.lineTo(TX - 145, TY - 120); g.stroke();
      g.fillStyle = '#7a5636'; g.fillRect(TX - 142, TY - 250, 104, 84); for (let k = 0; k < 7; k++) { g.fillStyle = k % 2 ? 'rgba(40,24,12,.25)' : 'rgba(255,226,176,.18)'; g.fillRect(TX - 142 + k * 15, TY - 250, 3, 84); }
      ell(g, TX - 90, TY - 250, 52, 9, 0, '#5a3e24'); ell(g, TX - 90, TY - 166, 52, 9, 0, '#5a3e24');
      g.fillStyle = '#3a3634'; for (const y of [TY - 236, TY - 206, TY - 178]) g.fillRect(TX - 144, y, 108, 5);
      g.fillStyle = 'rgba(255,226,176,.35)'; g.fillRect(TX - 142, TY - 250, 20, 84);
      ell(g, TX - 40, TY + 12, 160, 10, 0, 'rgba(60,36,20,.3)');
      // tufos escuros de primeiro plano (moldura)
      const rf = rng(97); g.fillStyle = grad(g, 0, 920, 0, H, [[0, 'rgba(40,46,24,0)'], [1, 'rgba(34,38,20,.8)']]); g.fillRect(0, 920, W, 160);
      for (let i = 0; i < 60; i++) tufo(g, X0 - 20 + rf() * 1120, 1080 - rf() * 40, 50 + rf() * 70, rgba(mix([60, 66, 30], [150, 130, 60], rf()), .95), rf, 7);
      terra = M.broken(terra, { cell: 6, len: 13, wid: 7, passes: 3, angle: (x, y) => (y < 640 ? 0 : -0.2 + P.noise(x * .01, y * .01) * .6), seed: 2701, jit: 9, skip: 0.03, sat: 1.04, warm: [255, 220, 160], cool: [80, 96, 130] });
      { const g = terra.getContext('2d');                         // a torre de ferro do cata-vento, nítida por cima da pincelada
        g.strokeStyle = '#3a3634'; g.lineWidth = 5; g.beginPath(); g.moveTo(TX - 40, TY + 6); g.lineTo(TX - 6, TY - 300); g.moveTo(TX + 40, TY + 6); g.lineTo(TX + 6, TY - 300); g.stroke();
        g.lineWidth = 2.5; for (let k = 0; k < 7; k++) { const y0 = TY + 6 - k * 44, y1 = y0 - 44, w0 = lerp(40, 6, (TY + 6 - y0) / 306), w1 = lerp(40, 6, (TY + 6 - y1) / 306);
          g.beginPath(); g.moveTo(TX - w0, y0); g.lineTo(TX + w1, y1); g.moveTo(TX + w0, y0); g.lineTo(TX - w1, y1); g.moveTo(TX - w1, y1); g.lineTo(TX + w1, y1); g.stroke(); }
        g.strokeStyle = 'rgba(255,220,170,.55)'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(TX - 40, TY + 6); g.lineTo(TX - 6, TY - 300); g.stroke();
        g.fillStyle = '#4a4440'; g.fillRect(TX - 16, TY - 4, 32, 14); g.strokeStyle = '#5a4026'; g.lineWidth = 4; g.beginPath(); g.moveTo(TX + 10, TY + 2); g.quadraticCurveTo(TX - 40, TY - 60, TX - 90, TY - 168); g.stroke(); }   // o cano até a caixa
    }
    function draw(c, lt) {
      if (!built) { build(); built = true; }
      const t = Math.max(0, lt);
      c.save(); c.translate(-t * 3, 0); c.scale(1.04, 1.04); c.drawImage(ceu, 0, 0); c.restore();
      c.drawImage(terra, 0, 0);
      // as pás do cata-vento girando com o vento, e o leme
      const hx = TX, hy = TY - 304, ang = t * 2.2;
      c.save(); c.translate(hx, hy); c.strokeStyle = '#2e2a28'; c.lineWidth = 3; c.beginPath(); c.moveTo(0, 0); c.lineTo(70, -6); c.stroke();
      c.fillStyle = '#3a3634'; poly(c, [[60, -6], [96, -30], [100, 12]]); c.fill();
      for (let k = 0; k < 16; k++) { const a = ang + k * TAU / 16; c.save(); c.rotate(a); c.fillStyle = k % 2 ? '#7a7470' : '#9a948c'; poly(c, [[8, -3], [58, -10], [58, 10], [8, 3]]); c.fill(); c.restore(); }
      c.strokeStyle = '#2e2a28'; c.lineWidth = 2; c.beginPath(); c.arc(0, 0, 58, 0, TAU); c.stroke(); c.fillStyle = '#2e2a28'; c.beginPath(); c.arc(0, 0, 7, 0, TAU); c.fill(); c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; for (let k = 0; k < 5; k++) { const a = .22 + k * .09 + Math.sin(t * .3 + k) * .01; c.fillStyle = `rgba(255,226,170,${.05 + .02 * Math.sin(t * .8 + k)})`;
        poly(c, [[SOL[0], SOL[1]], [SOL[0] + Math.cos(a) * 1600, SOL[1] + Math.sin(a) * 1600], [SOL[0] + Math.cos(a + .035) * 1600, SOL[1] + Math.sin(a + .035) * 1600]]); c.fill(); } c.restore();
      const rv = rng(29); c.save(); c.lineCap = 'round'; for (let i = 0; i < 110; i++) { const x = X0 - 10 + rv() * 1100, y = 1085, l = 40 + rv() * 60, sw = Math.sin(t * 1.5 + x * .01) * 10;
        c.strokeStyle = rgba(mix([96, 96, 44], [210, 180, 100], rv()), .85); c.lineWidth = 2 + rv() * 2; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + sw * .4, y - l * .6, x + sw, y - l); c.stroke(); } c.restore();
      c.save(); c.strokeStyle = 'rgba(60,50,50,.7)'; c.lineWidth = 2; for (let i = 0; i < 3; i++) { const x = 700 + ((t * 24 + i * 70) % 700), y = 250 + i * 16 + Math.sin(t * 2 + i) * 4, w = Math.sin(t * 8 + i) * 4;
        c.beginPath(); c.moveTo(x - 9, y - w); c.quadraticCurveTo(x - 4, y - 5, x, y); c.quadraticCurveTo(x + 4, y - 5, x + 9, y - w); c.stroke(); } c.restore();
      const vg = c.createRadialGradient(1000, 600, 300, 1000, 600, 900); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(30,20,10,.34)'); c.fillStyle = vg; c.fillRect(0, 0, W, H);
      tela(c, 'canvas_pcg', '#efe2c8');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Prancha de geologia: o poço até o aquífero
  SCENES['pc_corte'] = (() => {
    let base, built = false;
    const PX = 900;                                              // o poço, no terço esquerdo do recorte
    const CAM = [[0, 330, '#8a7a4a', 'solo'], [330, 420, '#a8502e', 'terra'], [420, 560, '#c49a6a', 'argila'], [560, 760, '#d8c08c', 'arenito'], [760, 900, '#5f97b6', 'aquifero'], [900, 1080, '#5e534c', 'rocha']];
    const yC = (k, x) => CAM[k][0] + 14 * Math.sin(x * .004 + k) + 10 * P.noise(x * .006, k);
    function build() {
      base = P.canvas(); const g = base.getContext('2d');
      g.fillStyle = '#efe4c8'; g.fillRect(0, 0, W, H);                                  // o papel da prancha
      g.fillStyle = grad(g, 0, 0, 0, 300, [[0, '#9fb8cc'], [1, '#e8dcc0']]); g.fillRect(0, 0, W, 300);   // céu aquarelado
      for (let k = 1; k < CAM.length; k++) { g.fillStyle = CAM[k][2]; g.beginPath(); g.moveTo(0, H); for (let x = 0; x <= W; x += 8) g.lineTo(x, yC(k, x)); g.lineTo(W, H); g.closePath(); g.fill(); }
      // superfície: pasto, cerca, casa e o cata-vento pequeno
      for (let x = 0; x < W; x += 14) { g.strokeStyle = 'rgba(70,96,40,.9)'; g.lineWidth = 2; for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(x + k * 4, 302); g.lineTo(x + k * 4 + (k - 1) * 5, 286 - (x % 5)); g.stroke(); } }
      g.fillStyle = '#8a9a52'; g.beginPath(); g.moveTo(0, 340); for (let x = 0; x <= W; x += 8) g.lineTo(x, 300 + 10 * Math.sin(x * .006)); g.lineTo(W, 340); g.closePath(); g.fill();
      g.fillStyle = '#efe6d4'; g.fillRect(1230, 250, 80, 50); g.fillStyle = '#a84a2a'; poly(g, [[1222, 254], [1270, 226], [1318, 254]]); g.fill();
      // texturas de gravura: pontilhado no arenito, hachura na argila, blocos na rocha, gotas azuis no aquífero
      const r = rng(5);
      for (let i = 0; i < 4000; i++) { const x = r() * W, y = 560 + r() * 200; if (y < yC(3, x) || y > yC(4, x)) continue; g.fillStyle = 'rgba(120,96,60,.5)'; g.fillRect(x, y, 2, 2); }
      g.strokeStyle = 'rgba(110,60,30,.35)'; g.lineWidth = 1.2; for (let x = 0; x < W; x += 9) { g.beginPath(); g.moveTo(x, yC(2, x) + 4); g.lineTo(x + 14, yC(3, x) - 4); g.stroke(); }
      g.strokeStyle = 'rgba(30,24,20,.55)'; g.lineWidth = 2; for (let i = 0; i < 70; i++) { const x = r() * W, y = 930 + r() * 140; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 30 + r() * 60, y + (r() - .5) * 30); g.lineTo(x + 50 + r() * 80, y + (r() - .5) * 40); g.stroke(); }   // fendas da rocha
      g.strokeStyle = 'rgba(70,50,30,.6)'; g.lineWidth = 2; for (let i = 0; i < 40; i++) { const x = r() * W; let y = 330, xx = x; g.beginPath(); g.moveTo(xx, y); for (let k = 0; k < 6; k++) { xx += (r() - .5) * 20; y += 12 + r() * 10; g.lineTo(xx, y); } g.stroke(); }   // raízes no solo
      for (let i = 0; i < 260; i++) { const x = r() * W, y = 430 + r() * 120; if (y < yC(2, x) + 6 || y > yC(3, x) - 6) continue; ell(g, x, y, 4 + r() * 6, 3 + r() * 4, r() * 3, rgba(mix([150, 120, 90], [220, 200, 170], r()), .9)); }   // seixos na argila
      g.strokeStyle = 'rgba(220,240,250,.45)'; g.lineWidth = 2; for (let k = 0; k < 5; k++) { g.beginPath(); for (let x = 0; x <= W; x += 10) { const y = 790 + k * 22 + 6 * Math.sin(x * .01 + k); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); }   // linhas de fluxo no aquífero
      for (let i = 0; i < 1600; i++) { const x = r() * W, y = 760 + r() * 140; if (y < yC(4, x) + 4 || y > yC(5, x) - 4) continue; ell(g, x, y, 3, 4, 0, 'rgba(230,244,250,.55)'); }
      base = M.broken(base, { cell: 5, len: 10, wid: 6, passes: 2, angle: () => 0, seed: 2801, jit: 7, skip: 0.02, sat: 1.0, warm: [255, 230, 180], cool: [90, 110, 140] });
      { const g = base.getContext('2d');
        g.strokeStyle = 'rgba(60,40,24,.8)'; g.lineWidth = 2; for (let k = 1; k < CAM.length; k++) { g.beginPath(); for (let x = 0; x <= W; x += 8) x ? g.lineTo(x, yC(k, x)) : g.moveTo(x, yC(k, x)); g.stroke(); }
        g.fillStyle = '#3e3a36'; g.fillRect(PX - 14, 280, 28, yC(4, PX) + 60 - 280); g.fillStyle = '#d8d4cc'; g.fillRect(PX - 9, 286, 18, yC(4, PX) + 54 - 286);   // o tubo do poço
        g.fillStyle = 'rgba(40,30,20,.6)'; for (let y = 300; y < yC(4, PX) + 50; y += 18) g.fillRect(PX - 14, y, 28, 2);
        g.strokeStyle = '#2e2a28'; g.lineWidth = 3; g.beginPath(); g.moveTo(PX - 22, 300); g.lineTo(PX - 4, 150); g.moveTo(PX + 22, 300); g.lineTo(PX + 4, 150); g.stroke();   // torre do cata-vento
        g.lineWidth = 2; for (let k = 0; k < 4; k++) { const y = 300 - k * 37; g.beginPath(); g.moveTo(PX - 20 + k * 4, y); g.lineTo(PX + 16 - k * 4, y - 37); g.stroke(); }
        g.font = 'italic 700 30px Georgia, serif'; g.fillStyle = '#4a3420'; g.textAlign = 'left';
        g.fillText('Fig. 1 — Corte do terreno', 440, 1050); }
    }
    function draw(c, lt) {
      if (!built) { build(); built = true; }
      const t = Math.max(0, lt), ez = u => u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
      c.drawImage(base, 0, 0);
      // o aquífero cintila devagar (a água está ali)
      c.save(); c.globalCompositeOperation = 'screen'; const r = rng(7); for (let i = 0; i < 90; i++) { const x = 400 + r() * 1150, y = 770 + r() * 120, a = .2 + .3 * Math.abs(Math.sin(t * 1.3 + i));
        c.fillStyle = `rgba(200,236,255,${a})`; c.fillRect(x, y, 3, 3); } c.restore();
      // REVELAR: a água sobe pelo tubo, de 1 s a 4 s, e jorra em cima
      const u = ez(clamp((t - 1) / 3, 0, 1)), yb = yC(4, PX) + 50, ytop = 290, yw = lerp(yb, ytop, u);
      c.fillStyle = 'rgba(90,170,220,.95)'; c.fillRect(PX - 7, yw, 14, yb - yw);
      c.save(); c.strokeStyle = 'rgba(230,248,255,.9)'; c.lineWidth = 2; for (let k = 0; k < 6; k++) { const y = yb - ((t * 120 + k * 40) % Math.max(1, yb - yw)); if (y > yw) { c.beginPath(); c.moveTo(PX - 4, y); c.lineTo(PX + 4, y - 10); c.stroke(); } } c.restore();
      if (u >= 1) { c.save(); c.fillStyle = 'rgba(140,200,235,.85)'; for (let k = 0; k < 14; k++) { const p = ((t * 1.4 + k / 14) % 1), x = PX + 14 + p * 70, y = 292 - Math.sin(p * Math.PI) * 30 + p * 10; ell(c, x, y, 3, 3, 0, 'rgba(150,210,240,.9)'); } c.restore(); }
      // pás do cata-vento pequeno
      c.save(); c.translate(PX, 148); for (let k = 0; k < 12; k++) { c.save(); c.rotate(t * 2 + k * TAU / 12); c.fillStyle = k % 2 ? '#6a6460' : '#8a847c'; poly(c, [[4, -2], [30, -6], [30, 6], [4, 2]]); c.fill(); c.restore(); } c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = .1; c.drawImage(P.texture('papel_pc', '#e6d6b0', { scale: .004, amt: 18, grain: 10, seed: 33 }), 0, 0); c.restore();
      const vg = c.createRadialGradient(960, 560, 360, 960, 560, 900); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(70,50,20,.3)'); c.fillStyle = vg; c.fillRect(0, 0, W, H);
    }
    return { draw };
  })();
})();
