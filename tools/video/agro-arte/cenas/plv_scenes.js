// Cenas do vídeo "O relógio zerou" (PLV 16/2026, dívidas rurais) — pintadas em código, sem imagem gerada por IA.
// Recorte quadrado central (x 420..1500 de 1920x1080). Composições novas, à maneira de mestres em domínio público:
//   plv_congresso — Monet, série "Parlamento de Londres, pôr do sol" (1900-04): o Congresso Nacional na névoa dourada
//   plv_medas     — Monet, série das "Medas" (1890-91): sete medas de palha ao entardecer, uma por safra (2019 a 2025)
//   plv_chardin   — Chardin, natureza-morta: sacas de grão, balança de pratos e grãos no tampo
//   plv_vermeer   — Vermeer, interior com janela à esquerda: mesa com livro-caixa, moedas e mapa na parede (sem figura)
//   plv_ruisdael  — Ruisdael, "Campos de trigo" (c. 1670): céu enorme de nuvens, trigal com faixas de luz e sombra
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const radg = (g, x, y, r0, r1, stops) => { const gr = g.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.18; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 31 }), 0, 0); c.restore(); };

  // ---------------------------------------------------------------- Monet: o Congresso na névoa do entardecer
  SCENES['plv_congresso'] = (() => {
    let plate, built = false;
    const HZ = 640;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#6a5a9a'], [0.35, '#b07aa8'], [0.7, '#f0a070'], [1, '#f6c27a']]); g.fillRect(0, 0, W, HZ);
      g.fillStyle = radg(g, 1210, 380, 10, 520, [[0, 'rgba(255,214,120,.95)'], [0.25, 'rgba(255,170,90,.55)'], [1, 'rgba(255,170,90,0)']]); g.fillRect(0, 0, W, HZ);
      // silhueta do Congresso, azul-violeta contra o sol (Monet: forma dissolvida na luz)
      const sil = '#4a3a6e';
      g.fillStyle = sil;
      g.fillRect(560, HZ - 40, 800, 40);                                                        // laje horizontal
      g.fillRect(912, HZ - 330, 38, 290); g.fillRect(970, HZ - 330, 38, 290); g.fillRect(950, HZ - 214, 20, 26);   // as duas torres e a passarela
      g.beginPath(); g.ellipse(760, HZ - 40, 92, 52, 0, Math.PI, TAU); g.fill();                 // cúpula do Senado
      g.beginPath(); g.ellipse(1160, HZ - 96, 100, 56, 0, 0, Math.PI); g.fill(); g.fillStyle = '#6a5288'; g.beginPath(); g.ellipse(1160, HZ - 96, 100, 12, 0, 0, TAU); g.fill(); g.fillStyle = sil;   // cuia da Câmara
      g.fillRect(1150, HZ - 52, 22, 14);
      g.fillStyle = 'rgba(120,90,140,.6)'; g.fillRect(0, HZ - 12, W, 18);                        // gramado ao longe
      // espelho d'água
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#d8946a'], [0.4, '#8a6a9a'], [1, '#3e3a6a']]); g.fillRect(0, HZ, W, H - HZ);
      return M.broken(a, { cell: 9, len: 24, wid: 8, passes: 2, angle: (x, y) => y < HZ ? -0.15 + Math.sin(y * 0.01) * 0.2 : 0.02, seed: 61, jit: 18, skip: 0.06, sat: 1.12, warm: [255, 210, 150], cool: [110, 100, 190] });
    }
    function reflexo(c, t) {                                                                    // reflexos tremendo na água: pinceladas horizontais
      const r = rng(7 + Math.floor(t * 10));
      for (let i = 0; i < 260; i++) {
        const y = HZ + 10 + Math.pow(r(), 1.3) * 420, x = 1210 + (r() - .5) * (120 + (y - HZ) * 0.9);
        c.fillStyle = `rgba(255,${190 + (r() * 50) | 0},${110 + (r() * 60) | 0},${0.55 - (y - HZ) / 900})`; c.fillRect(x, y, 14 + r() * 40, 3 + r() * 4);
      }
      for (let i = 0; i < 120; i++) {                                                            // reflexo partido das torres
        const y = HZ + 6 + r() * 280, x = 912 + r() * 96 + Math.sin(y * 0.08 + t * 3) * 10;
        c.fillStyle = `rgba(74,58,110,${0.5 - (y - HZ) / 700})`; c.fillRect(x - 10, y, 22 + r() * 18, 4);
      }
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0); reflexo(c, t);
      c.save(); c.globalAlpha = 0.12 + 0.05 * Math.sin(t * 1.4); c.fillStyle = radg(c, 1210, 380, 10, 300, [[0, '#fff2c0'], [1, 'rgba(255,240,190,0)']]); c.fillRect(0, 0, W, H); c.restore();
      c.save(); c.strokeStyle = '#3a2e54'; c.lineWidth = 3; c.lineCap = 'round';                // aves cruzando
      for (let k = 0; k < 5; k++) { const x = 500 + k * 70 + t * 60, y = 220 + k * 18 + Math.sin(t * 2 + k) * 6, f = Math.sin(t * 8 + k) * 8; c.beginPath(); c.moveTo(x - 14, y + f * .5); c.quadraticCurveTo(x - 6, y - f, x, y); c.quadraticCurveTo(x + 6, y - f, x + 14, y + f * .5); c.stroke(); }
      c.restore(); tela(c, 'canvas_cg', '#e8dcc8');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Monet: as medas, uma por safra
  SCENES['plv_medas'] = (() => {
    let plate, built = false;
    const HZ = 470, MEDAS = [[520, 600, .62], [660, 640, .72], [800, 690, .84], [960, 760, 1.0], [1130, 690, .84], [1270, 640, .72], [1400, 600, .62]];
    function meda(g, x, y, s2) {
      g.fillStyle = grad(g, x - 90 * s2, 0, x + 90 * s2, 0, [[0, '#f6c060'], [0.55, '#d88a3a'], [1, '#7a4a6a']]);
      g.beginPath(); g.moveTo(x - 92 * s2, y); g.quadraticCurveTo(x - 96 * s2, y - 120 * s2, x - 40 * s2, y - 150 * s2); g.quadraticCurveTo(x, y - 230 * s2, x + 40 * s2, y - 150 * s2); g.quadraticCurveTo(x + 96 * s2, y - 120 * s2, x + 92 * s2, y); g.closePath(); g.fill();
      g.fillStyle = 'rgba(90,60,120,.55)'; g.beginPath(); g.ellipse(x + 120 * s2, y + 6, 150 * s2, 20 * s2, 0, 0, TAU); g.fill();     // sombra longa e violeta
    }
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#8fb0d8'], [0.6, '#f2c8a0'], [1, '#f8dca0']]); g.fillRect(0, 0, W, HZ);
      g.fillStyle = '#9a8ab0'; g.beginPath(); g.moveTo(0, HZ); g.quadraticCurveTo(600, HZ - 40, 1100, HZ - 14); g.quadraticCurveTo(1500, HZ - 34, 1920, HZ); g.lineTo(1920, HZ + 20); g.lineTo(0, HZ + 20); g.fill();
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#d8b870'], [0.4, '#c89a50'], [1, '#8a7a4a']]); g.fillRect(0, HZ, W, H - HZ);
      g.fillStyle = '#7a9a5a'; g.fillRect(0, HZ + 18, W, 30);
      MEDAS.forEach(([x, y, s2]) => meda(g, x, y, s2));
      return M.broken(a, { cell: 8, len: 20, wid: 7, passes: 2, angle: (x, y) => y < HZ ? 0.05 : -1.2 + Math.sin(x * 0.01) * 0.4, seed: 71, jit: 16, skip: 0.05, sat: 1.15, warm: [255, 214, 150], cool: [130, 110, 190] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'soft-light'; c.globalAlpha = 0.35 + 0.25 * ss(0, 9, t); c.fillStyle = grad(c, 0, 0, W, 0, [[0, '#ffb060'], [1, '#6a4aa0']]); c.fillRect(0, 0, W, H); c.restore();   // a luz muda, como na série
      const r = rng(3 + Math.floor(t * 6)); c.fillStyle = 'rgba(255,236,190,.7)';                // poeira de palha no ar
      for (let i = 0; i < 40; i++) { c.beginPath(); c.arc(420 + r() * 1080, 300 + r() * 400, 1.5 + r() * 2, 0, TAU); c.fill(); }
      tela(c, 'canvas_md', '#e6dcc4');
    }
    return { draw, MEDAS };
  })();

  // ---------------------------------------------------------------- Chardin: sacas, balança e grãos
  SCENES['plv_chardin'] = (() => {
    let plate, built = false;
    function saca(g, x, y, w, h, cor) {
      g.fillStyle = grad(g, x - w / 2, 0, x + w / 2, 0, [[0, '#5a4026'], [0.35, cor], [0.7, '#c8a46a'], [1, '#4a3420']]);
      g.beginPath(); g.moveTo(x - w * .46, y); g.quadraticCurveTo(x - w * .56, y - h * .5, x - w * .38, y - h); g.quadraticCurveTo(x, y - h * 1.12, x + w * .38, y - h); g.quadraticCurveTo(x + w * .56, y - h * .5, x + w * .46, y); g.closePath(); g.fill();
      g.strokeStyle = 'rgba(60,40,20,.5)'; g.lineWidth = 2; for (let k = 1; k < 9; k++) { g.beginPath(); g.moveTo(x - w * .45, y - h * k / 9); g.lineTo(x + w * .45, y - h * k / 9 - 4); g.stroke(); }   // trama da juta
      g.fillStyle = '#3a2a18'; g.fillRect(x - w * .2, y - h * 1.02, w * .4, 10);
    }
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = radg(g, 700, 300, 50, 1100, [[0, '#6a5a40'], [0.6, '#3a3024'], [1, '#1e1a14']]); g.fillRect(0, 0, W, H);                // fundo escuro de Chardin
      g.fillStyle = grad(g, 0, 760, 0, H, [[0, '#8a6a44'], [1, '#4a3622']]); g.fillRect(0, 760, W, H - 760);                             // tampo de madeira
      g.fillStyle = '#a8865a'; g.fillRect(0, 760, W, 10);
      saca(g, 680, 790, 300, 380, '#b89058'); saca(g, 920, 800, 250, 290, '#a88048');
      for (let i = 0; i < 260; i++) { const r = rng(400 + i)(); const x = 560 + rng(800 + i)() * 900, y = 800 + rng(1200 + i)() * 220;   // grãos espalhados
        g.fillStyle = ['#e8c878', '#d4ac5a', '#f0d690'][i % 3]; g.beginPath(); g.ellipse(x, y, 7, 5, r * 3, 0, TAU); g.fill(); }
      return M.broken(a, { cell: 7, len: 16, wid: 6, passes: 2, angle: (x, y) => y > 760 ? 0.05 : 1.4 + Math.sin(x * 0.02) * 0.3, seed: 81, jit: 14, skip: 0.06, sat: 1.0, warm: [250, 220, 160], cool: [80, 80, 110] });
    }
    function balanca(c, t) {                                                                    // balança de pratos: o prato dos grãos sobe (o preço cai)
      const k = ss(1.2, 3.4, t), ang = -0.22 * k, cx = 1260, cy = 470;
      c.save(); c.translate(cx, cy);
      c.fillStyle = '#7a5a2a'; c.fillRect(-8, 0, 16, 300); c.fillStyle = '#5a3e1a'; c.fillRect(-60, 290, 120, 18);
      c.rotate(ang); c.fillStyle = '#c89a3a'; c.fillRect(-170, -8, 340, 14);
      [[-160, 1], [160, -1]].forEach(([x, sgn]) => { c.save(); c.translate(x, 0); c.rotate(-ang);
        c.strokeStyle = '#a8803a'; c.lineWidth = 2; c.beginPath(); c.moveTo(0, 0); c.lineTo(-50, 120); c.moveTo(0, 0); c.lineTo(50, 120); c.stroke();
        c.fillStyle = '#d4a848'; c.beginPath(); c.ellipse(0, 122, 62, 14, 0, 0, TAU); c.fill();
        if (sgn > 0) { c.fillStyle = '#e8c878'; c.beginPath(); c.ellipse(0, 114, 46, 16, 0, Math.PI, TAU); c.fill(); }
        c.restore(); });
      c.restore();
      c.save(); c.fillStyle = radg(c, 380, 200, 10, 900, [[0, 'rgba(255,230,170,.22)'], [1, 'rgba(255,230,170,0)']]); c.fillRect(0, 0, W, H); c.restore();   // luz da janela, da esquerda
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0); balanca(c, t);
      const r = rng(5); c.fillStyle = '#e8c878';                                                // grãos que escorrem da saca do meio
      for (let i = 0; i < 26; i++) { const ph = (t * 0.9 + r()) % 1, x = 920 + (r() - .5) * 30 + ph * 40, y = 560 + ph * 230; c.beginPath(); c.ellipse(x, y, 6, 4, ph * 6, 0, TAU); c.fill(); }
      tela(c, 'canvas_ch', '#e0d4bc');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Vermeer: mesa com livro-caixa e moedas, luz da janela
  SCENES['plv_vermeer'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 420, 0, 1500, 0, [[0, '#d8ccb0'], [0.5, '#c4b494'], [1, '#8a7c62']]); g.fillRect(0, 0, W, H);                 // parede caiada
      // janela de vitral à esquerda
      g.fillStyle = grad(g, 420, 120, 560, 120, [[0, '#f4f0e0'], [1, '#c8d4d8']]); g.fillRect(420, 100, 150, 560);
      g.strokeStyle = '#5a5040'; g.lineWidth = 3; for (let k = 0; k < 14; k++) { g.beginPath(); g.moveTo(420, 100 + k * 44); g.lineTo(570, 100 + k * 44 + 30); g.stroke(); g.beginPath(); g.moveTo(420, 140 + k * 44); g.lineTo(570, 110 + k * 44); g.stroke(); }
      g.fillStyle = '#4a3a28'; g.fillRect(570, 90, 18, 580);
      // mapa na parede, com barra de madeira (como nos interiores de Vermeer)
      g.fillStyle = '#6a4a26'; g.fillRect(820, 140, 560, 16); g.fillRect(820, 520, 560, 14);
      g.fillStyle = grad(g, 830, 156, 1370, 520, [[0, '#d8c08a'], [1, '#b89a64']]); g.fillRect(830, 156, 540, 364);
      g.strokeStyle = 'rgba(90,70,40,.6)'; g.lineWidth = 3; g.beginPath(); g.moveTo(900, 220); g.bezierCurveTo(1000, 260, 980, 380, 1120, 420); g.bezierCurveTo(1220, 450, 1260, 330, 1330, 300); g.stroke();
      g.fillStyle = 'rgba(120,140,90,.5)'; g.beginPath(); g.ellipse(1060, 330, 110, 70, 0.3, 0, TAU); g.fill(); g.beginPath(); g.ellipse(1250, 420, 70, 50, -0.2, 0, TAU); g.fill();
      // mesa com tapete oriental vermelho e azul
      g.fillStyle = grad(g, 0, 640, 0, H, [[0, '#8a2a22'], [0.5, '#6a1e1a'], [1, '#3a1410']]); poly(g, [[420, 640], [1500, 640], [1500, H], [420, H]]); g.fill();
      g.strokeStyle = '#2a3a6a'; g.lineWidth = 10; for (let k = 0; k < 6; k++) { g.beginPath(); g.moveTo(420, 680 + k * 70); g.lineTo(1500, 690 + k * 70); g.stroke(); }
      // livro-caixa aberto
      g.fillStyle = '#f0e6cc'; poly(g, [[760, 720], [960, 700], [960, 860], [740, 880]]); g.fill(); poly(g, [[960, 700], [1170, 716], [1190, 876], [960, 860]]); g.fill();
      g.strokeStyle = 'rgba(80,70,60,.6)'; g.lineWidth = 2; for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(775, 735 + k * 17); g.lineTo(945, 718 + k * 17); g.stroke(); g.beginPath(); g.moveTo(975, 720 + k * 17); g.lineTo(1165, 734 + k * 17); g.stroke(); }
      // tinteiro e pena
      g.fillStyle = '#1e1a18'; g.beginPath(); g.ellipse(1290, 760, 28, 14, 0, 0, TAU); g.fill(); g.fillRect(1264, 720, 52, 40);
      g.strokeStyle = '#efe8d8'; g.lineWidth = 5; g.beginPath(); g.moveTo(1296, 724); g.quadraticCurveTo(1340, 640, 1400, 610); g.stroke();
      return M.broken(a, { cell: 6, len: 14, wid: 5, passes: 2, angle: (x, y) => y > 640 ? 0.04 : 1.5, seed: 91, jit: 10, skip: 0.08, sat: 1.05, warm: [255, 236, 190], cool: [90, 100, 140] });
    }
    function moedas(c, t) {                                                                     // duas pilhas de moedas crescem, moeda a moeda
      [[600, 850, 10], [700, 870, 15]].forEach(([x, y, n], j) => { const k = Math.floor(n * ss(0.4 + j * 0.5, 3.0 + j * 0.6, t));
        for (let i = 0; i < k; i++) { const yy = y - i * 12; c.fillStyle = '#7a5a1e'; c.beginPath(); c.ellipse(x, yy + 4, 42, 13, 0, 0, TAU); c.fill(); c.fillStyle = i % 2 ? '#e8c058' : '#d4a840'; c.beginPath(); c.ellipse(x, yy, 42, 13, 0, 0, TAU); c.fill(); } });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0); moedas(c, t);
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = grad(c, 560, 200, 1300, 900, [[0, 'rgba(255,246,214,.38)'], [1, 'rgba(255,246,214,0)']]); poly(c, [[570, 100], [1500, 600], [1500, H], [570, 680]]); c.fill(); c.restore();   // facho de luz
      const r = rng(9); c.fillStyle = 'rgba(255,250,230,.6)';                                   // poeira dançando na luz
      for (let i = 0; i < 50; i++) { const x = 600 + r() * 700 + Math.sin(t * .6 + i) * 20, y = 200 + r() * 500 + Math.cos(t * .5 + i) * 14; c.beginPath(); c.arc(x, y, 1.5 + r() * 1.5, 0, TAU); c.fill(); }
      tela(c, 'canvas_vm', '#e8dcc6');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Ruisdael: céu de nuvens sobre o trigal, luz que corre
  SCENES['plv_ruisdael'] = (() => {
    let plate, built = false;
    const HZ = 640;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(501);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#3a4a6a'], [0.5, '#7a8aa0'], [1, '#c8c4b0']]); g.fillRect(0, 0, W, HZ);
      for (let i = 0; i < 26; i++) { const x = r() * W, y = 60 + r() * 420, w = 120 + r() * 260;                                        // cúmulos de Ruisdael
        g.fillStyle = grad(g, 0, y - 80, 0, y + 60, [[0, '#f2eee2'], [0.6, '#a8a8a8'], [1, '#4a4e5a']]);
        for (let k = 0; k < 5; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * w, y + (r() - .5) * 50, w * (.3 + r() * .3), w * (.18 + r() * .14), 0, 0, TAU); g.fill(); } }
      g.fillStyle = '#4a5a3a'; g.fillRect(0, HZ - 8, W, 22);
      g.fillStyle = '#c8b8a0'; g.fillRect(1180, HZ - 50, 40, 44); g.fillStyle = '#6a3a2a'; poly(g, [[1172, HZ - 50], [1200, HZ - 78], [1228, HZ - 50]]); g.fill();   // casinha ao longe
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#c8a040'], [0.5, '#a07a28'], [1, '#5a4418']]); g.fillRect(0, HZ + 12, W, H - HZ);
      g.fillStyle = '#e0c060'; poly(g, [[420, H], [880, HZ + 14], [940, HZ + 14], [760, H]]); g.fill();                                // estrada de terra
      g.fillStyle = '#2e3a22'; g.fillRect(1320, 380, 18, 270); for (let i = 0; i < 70; i++) { g.beginPath(); g.ellipse(1330 + (r() - .5) * 200, 360 + (r() - .5) * 180, 30, 22, r() * 3, 0, TAU); g.fill(); }   // árvore solitária
      return M.broken(a, { cell: 8, len: 22, wid: 7, passes: 2, angle: (x, y) => y < HZ ? 0.1 + Math.sin(x * 0.004 + y * 0.01) * 0.6 : -1.3, seed: 101, jit: 14, skip: 0.05, sat: 0.95, warm: [240, 210, 150], cool: [80, 90, 120] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), dark = ss(0, 5, t);
      c.drawImage(plate, 0, 0);
      c.save(); c.fillStyle = `rgba(20,24,36,${0.15 + 0.35 * dark})`; c.fillRect(0, 0, W, H); c.restore();                              // o céu fecha
      const x0 = 300 + t * 140;                                                                 // faixa de sol correndo pelo trigal
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = grad(c, x0 - 260, 0, x0 + 260, 0, [[0, 'rgba(255,220,130,0)'], [0.5, `rgba(255,220,130,${0.5 - 0.3 * dark})`], [1, 'rgba(255,220,130,0)']]); c.fillRect(0, HZ + 12, W, H - HZ); c.restore();
      tela(c, 'canvas_rd', '#e0d8c4');
    }
    return { draw };
  })();
})();
