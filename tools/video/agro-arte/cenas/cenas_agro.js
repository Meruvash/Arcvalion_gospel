// Cenas do vídeo "MP 1.376 · o prazo é quinta" — pintadas em código, sem imagem gerada por IA.
// Composição pensada para o recorte quadrado central (x 420..1500 de 1920x1080).
// Estilos de mestres em domínio público: Almeida Júnior (realismo caipira), Van Gogh (seca, vendaval),
// impressionismo (granizo), Monet ("A Pega": geada). Composições novas, não cópia de quadros.
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };


  // =====================================================================================
  // 0) Van Gogh, "A Colheita" (1888) — fazenda grande e próspera em cores vivas
  //    planície em xadrez de lavouras até o horizonte, sede de telhado vermelho, silos,
  //    agricultor de pé, de costas, olhando a fazenda. Composição nova.
  // =====================================================================================
  SCENES['mp_fazenda'] = (() => {
    const VP = [980, 470];                                   // ponto de fuga das fileiras
    let base, farm, man, built = false;
    function plate() {
      const cv = P.canvas(), g = cv.getContext('2d'), r = rng(131);
      g.fillStyle = grad(g, 0, 0, 0, 470, [[0, '#1f5fc8'], [0.55, '#4f9ae0'], [1, '#bfe2f2']]); g.fillRect(0, 0, W, 490);
      for (let i = 0; i < 9; i++) { const x = 120 + r() * 1700, y = 80 + r() * 230, s2 = 0.6 + r() * 0.8; g.fillStyle = 'rgba(255,255,255,.95)'; for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * 180 * s2, y + (r() - .5) * 26 * s2, (50 + r() * 60) * s2, (22 + r() * 18) * s2, 0, 0, TAU); g.fill(); } }
      g.fillStyle = '#5a86c8'; g.beginPath(); g.moveTo(0, 470); g.quadraticCurveTo(400, 430, 800, 455); g.quadraticCurveTo(1300, 425, 1920, 460); g.lineTo(1920, 500); g.lineTo(0, 500); g.fill();
      // xadrez de lavouras em perspectiva: faixas horizontais × fileiras que convergem para VP
      const COLS = ['#7cc832', '#2f9e44', '#f2c22c', '#a6d84a', '#e09a24', '#3cb860', '#c8e04a', '#1f8a3a'];
      const ys = [470, 492, 520, 560, 615, 690, 790, 930, 1080];
      for (let b = 0; b < ys.length - 1; b++) {
        const y0 = ys[b], y1 = ys[b + 1];
        const nx = 9 - Math.min(5, b);
        for (let k = -nx; k <= nx; k++) {
          const xa = (y) => VP[0] + (k / nx) * 2600 * ((y - VP[1]) / (H - VP[1])) * 1.1, xb = (y) => VP[0] + ((k + 1) / nx) * 2600 * ((y - VP[1]) / (H - VP[1])) * 1.1;
          g.fillStyle = COLS[(b * 3 + k + 40) % COLS.length]; poly(g, [[xa(y0), y0], [xb(y0), y0], [xb(y1), y1], [xa(y1), y1]]); g.fill();
        }
      }
      // fileiras de plantio (linhas para o ponto de fuga)
      for (let k = -60; k <= 60; k++) { g.strokeStyle = k % 2 ? 'rgba(20,80,20,.28)' : 'rgba(255,250,170,.25)'; g.lineWidth = 3; g.beginPath(); g.moveTo(VP[0] + k * 6, 480); g.lineTo(VP[0] + k * 70, H); g.stroke(); }
      // estrada de terra clara cortando a planície até a sede
      g.fillStyle = '#e8c890'; poly(g, [[1210, 482], [1240, 482], [1010, H], [820, H]]); g.fill();
      return cv;
    }
    function farmPlate() {                                    // sede, galpão vermelho, silos, árvores — pintado à parte, traço mais fino
      const cv = P.canvas(), g = cv.getContext('2d');
      const tree = (x, y, s2, c1, c2) => { g.fillStyle = '#5a3a1a'; g.fillRect(x - 3 * s2, y - 30 * s2, 6 * s2, 30 * s2); g.fillStyle = c1; g.beginPath(); g.ellipse(x, y - 46 * s2, 30 * s2, 26 * s2, 0, 0, TAU); g.fill(); g.fillStyle = c2; g.beginPath(); g.ellipse(x - 8 * s2, y - 54 * s2, 16 * s2, 12 * s2, 0, 0, TAU); g.fill(); };
      [[1070, 486, 1.1], [1120, 484, 1.3], [1460, 484, 1.2], [1520, 486, 1.0], [1560, 488, 1.4]].forEach(([x, y, s2]) => tree(x, y, s2, '#1f7a3a', '#5cc85a'));
      // silos
      for (const [x, h] of [[1380, 120], [1418, 136], [1456, 120]]) { g.fillStyle = grad(g, x - 16, 0, x + 16, 0, [[0, '#9fb4cc'], [0.5, '#eef4fa'], [1, '#7a90aa']]); g.fillRect(x - 16, 486 - h, 32, h); g.fillStyle = '#c8d6e6'; g.beginPath(); g.ellipse(x, 486 - h, 16, 10, 0, Math.PI, TAU); g.fill(); }
      // galpão vermelho
      g.fillStyle = '#c8321e'; g.fillRect(1290, 432, 80, 54); g.fillStyle = '#8e1e14'; poly(g, [[1284, 434], [1330, 404], [1376, 434]]); g.fill(); g.fillStyle = '#f4e8d0'; g.fillRect(1318, 452, 24, 34);
      // sede: casa branca, telhado vermelho, varanda
      g.fillStyle = '#fbf6ea'; g.fillRect(1168, 440, 110, 46); g.fillStyle = '#d4442a'; poly(g, [[1158, 442], [1223, 408], [1288, 442]]); g.fill();
      g.fillStyle = '#3a5aa0'; for (let k = 0; k < 4; k++) g.fillRect(1178 + k * 26, 452, 12, 14); g.fillStyle = '#e8d8b8'; g.fillRect(1168, 474, 110, 4);
      return M.broken(cv, { cell: 4, len: 9, wid: 3.5, passes: 2, angle: (x, y) => (y < 440 ? 0.1 : 1.5), seed: 21, jit: 14, skip: 0.2, base: true, sat: 1.15, warm: [255, 230, 170], cool: [90, 110, 190] });
    }
    function manPlate() {                                     // agricultor de costas, camisa azul, chapéu de palha, mão na cintura
      const cv = P.canvas(), g = cv.getContext('2d'), x = 640, y = 1040;
      g.fillStyle = '#3a2a1e'; poly(g, [[x - 34, y], [x - 30, y - 150], [x - 4, y - 150], [x - 8, y]]); g.fill(); poly(g, [[x + 4, y], [x + 8, y - 150], [x + 34, y - 150], [x + 30, y]]); g.fill();   // calça
      g.fillStyle = '#4a3020'; g.beginPath(); g.ellipse(x - 20, y, 22, 8, 0, 0, TAU); g.fill(); g.beginPath(); g.ellipse(x + 20, y, 22, 8, 0, 0, TAU); g.fill();
      g.fillStyle = grad(g, x - 60, 0, x + 60, 0, [[0, '#2a5aa8'], [0.5, '#4a8ad8'], [1, '#2a4a90']]); poly(g, [[x - 44, y - 140], [x - 54, y - 290], [x - 30, y - 320], [x + 30, y - 320], [x + 54, y - 290], [x + 44, y - 140]]); g.fill();   // camisa
      g.fillStyle = '#2a5aa8'; poly(g, [[x + 46, y - 300], [x + 80, y - 240], [x + 56, y - 196], [x + 44, y - 210], [x + 58, y - 242], [x + 40, y - 280]]); g.fill();   // braço na cintura
      g.fillStyle = '#2f62b0'; poly(g, [[x - 48, y - 300], [x - 62, y - 220], [x - 56, y - 160], [x - 42, y - 164], [x - 44, y - 230], [x - 34, y - 290]]); g.fill();
      g.fillStyle = '#b07a4e'; g.beginPath(); g.ellipse(x - 52, y - 156, 9, 12, 0, 0, TAU); g.fill();
      g.fillStyle = '#9a6a42'; g.fillRect(x - 12, y - 340, 24, 24); g.beginPath(); g.ellipse(x, y - 360, 26, 30, 0, 0, TAU); g.fill();       // nuca
      g.fillStyle = '#f0cf6a'; g.beginPath(); g.ellipse(x, y - 376, 78, 18, 0, 0, TAU); g.fill(); g.fillStyle = '#f6dc84'; g.beginPath(); g.ellipse(x, y - 396, 36, 26, 0, Math.PI, TAU); g.fill(); g.fillRect(x - 36, y - 398, 72, 12);
      g.fillStyle = '#7a3a1a'; g.fillRect(x - 35, y - 392, 70, 7);
      return M.broken(cv, { cell: 4, len: 10, wid: 4, passes: 2, angle: (xx, yy) => (yy < y - 360 ? 0.1 : 1.45), seed: 23, jit: 12, skip: 0.15, base: true, sat: 1.1, warm: [255, 230, 170], cool: [70, 90, 180] });
    }
    function build() { base = plate(); farm = farmPlate(); man = manPlate(); built = true; }
    const angF = (x, y, t) => y < 470 ? (-0.15 + 0.35 * Math.sin(x * 0.006 + y * 0.012 - t * 0.8)) : Math.atan2(y - VP[1], x - VP[0]) + 0.25 * Math.sin(x * 0.01 - t * 2.4) * clamp((y - 480) / 500, 0, 1);
    const birds = Array.from({ length: 7 }, (_, i) => { const r = rng(8000 + i); return [r() * 600 + 300, 160 + r() * 140, r() * TAU]; });
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(base, 0, 0);
      P.strokes(c, base, { cell: 13, len: 36, width: 8, angle: angF, seed: 31, t, boil: 0, outline: 0.55, outlineCol: [20, 40, 110], outlineMix: 0.35, jitterCol: 22, mask: (x, y) => y < 470 });
      P.strokes(c, base, { cell: 10, len: 26, width: 7, angle: angF, seed: 33, t, boil: 0, outline: 0.6, outlineCol: [30, 60, 20], outlineMix: 0.35, jitterCol: 24, mask: (x, y) => y >= 466 });
      c.drawImage(farm, 0, 0);
      // trator ao longe numa fileira, com poeirinha
      const tx = 820 + ((t * 18) % 300), ty = 540;
      c.fillStyle = '#d42a1a'; c.fillRect(tx, ty - 12, 22, 12); c.fillStyle = '#222'; c.beginPath(); c.arc(tx + 4, ty, 6, 0, TAU); c.arc(tx + 18, ty, 4, 0, TAU); c.fill();
      c.fillStyle = 'rgba(240,220,170,.5)'; c.beginPath(); c.ellipse(tx - 16, ty - 4, 18, 7, 0, 0, TAU); c.fill();
      // pássaros
      c.save(); c.strokeStyle = '#1a2a4a'; c.lineWidth = 3; c.lineCap = 'round'; birds.forEach(([x, y, ph]) => { const xx = x + t * 40, yy = y + Math.sin(t * 1.5 + ph) * 10, f = Math.sin(t * 9 + ph) * 8; c.beginPath(); c.moveTo(xx - 14, yy + f * 0.5); c.quadraticCurveTo(xx - 6, yy - f, xx, yy); c.quadraticCurveTo(xx + 6, yy - f, xx + 14, yy + f * 0.5); c.stroke(); }); c.restore();
      // agricultor (respira levemente)
      const br = 1 + Math.sin(t * 1.3) * 0.005; c.save(); c.translate(640, 1040); c.scale(1, br); c.translate(-640, -1040); c.drawImage(man, 0, 0); c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture('canvas_fz', '#efe6d0', { scale: 0.006, amt: 12, grain: 8, seed: 11 }), 0, 0); c.restore();
    }
    return { draw };
  })();


  // =====================================================================================
  // RJ) Vídeo "Cinco por dia": fazenda com tempestade chegando / abrindo, e "O Semeador" à maneira de Millet
  // =====================================================================================
  let stormPlate = null;
  function storm(c, k, t) {                                  // k: 0 = céu limpo, 1 = tempestade cheia
    if (!stormPlate) { const a = P.canvas(), g = a.getContext('2d'), r = rng(171);
      for (let i = 0; i < 60; i++) { g.save(); g.filter = 'blur(10px)'; g.fillStyle = r() < 0.5 ? 'rgba(40,46,70,.85)' : 'rgba(80,86,110,.75)'; g.beginPath(); g.ellipse(r() * 2400 - 200, 20 + r() * 380, 140 + r() * 260, 50 + r() * 90, 0, 0, TAU); g.fill(); g.restore(); }
      stormPlate = M.broken(a, { cell: 11, len: 34, wid: 9, passes: 2, angle: (x, y) => -0.2 + 0.4 * Math.sin(x * 0.004 + y * 0.01), seed: 17, jit: 16, skip: 0.04, warm: [190, 190, 210], cool: [40, 40, 80] }); }
    if (k <= 0) return;
    c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = `rgba(70,78,104,${0.55 * k})`; c.fillRect(0, 0, W, H); c.restore();
    c.save(); c.globalAlpha = Math.min(1, k * 1.15); c.drawImage(stormPlate, -500 * (1 - k) - t * 10, 0, W + 400, 520 * (0.6 + 0.4 * k)); c.restore();
    if (k > 0.55) { const a = (k - 0.55) / 0.45; c.save(); c.strokeStyle = `rgba(210,220,240,${0.45 * a})`; c.lineWidth = 2; c.lineCap = 'round'; const r = rng(31);
      for (let i = 0; i < 260; i++) { const x0 = r() * 2100 - 100, ph = r(), f = ((t * 1.1 + ph) % 1), y = f * 1140 - 40, x = x0 - f * 160; c.beginPath(); c.moveTo(x, y); c.lineTo(x + 10, y - 44); c.stroke(); } c.restore(); }
  }
  SCENES['rj_fazenda_tempestade'] = { draw(c, lt) { const t = Math.max(0, lt); SCENES['mp_fazenda'].draw(c, t); storm(c, ss(0.8, 5.5, t) * 0.92, t); } };
  SCENES['rj_fazenda_abre'] = { draw(c, lt) { const t = Math.max(0, lt); SCENES['mp_fazenda'].draw(c, t + 6); storm(c, 0.92 - ss(0.3, 3.8, t) * 0.62, t + 6); } };

  // "O Semeador" (Millet, 1850, domínio público) — composição nova: semeador de perfil em terra arrendada, entardecer
  SCENES['rj_millet'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(181);
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#4a5470'], [0.5, '#9a8a78'], [1, '#f0c878']]); g.fillRect(0, 0, W, 600);
      const sg = g.createRadialGradient(1380, 500, 10, 1380, 500, 700); sg.addColorStop(0, 'rgba(255,214,140,.85)'); sg.addColorStop(1, 'rgba(255,214,140,0)'); g.fillStyle = sg; g.fillRect(0, 0, W, 600);
      // colina em diagonal (terra lavrada), escura à frente
      g.fillStyle = grad(g, 0, 380, 0, H, [[0, '#7a6440'], [0.4, '#5e4a2e'], [1, '#3a2c1c']]); poly(g, [[0, 420], [700, 470], [1920, 640], [1920, 1080], [0, 1080]]); g.fill();
      for (let i = 0; i < 70; i++) { const y = 470 + Math.pow(i / 70, 1.3) * 620; g.strokeStyle = i % 2 ? 'rgba(120,96,60,.6)' : 'rgba(40,30,18,.6)'; g.lineWidth = 3 + i * 0.12; g.beginPath(); g.moveTo(0, y - 40 + i * 0.6); g.lineTo(W, y + 150 - i * 1.4); g.stroke(); }
      // boi e lavrador ao longe, no topo da colina
      g.fillStyle = '#2e2418'; g.fillRect(1500, 600, 60, 26); g.fillRect(1505, 624, 6, 14); g.fillRect(1548, 624, 6, 14); g.fillRect(1590, 590, 10, 40);
      // cerca e placa "ARRENDADA" na margem direita
      g.strokeStyle = '#3a2c1c'; g.lineWidth = 7; for (let k = 0; k < 6; k++) { const x = 1180 + k * 70, y = 640 + k * 12; g.beginPath(); g.moveTo(x, y + 90); g.lineTo(x + 2, y); g.stroke(); }
      g.lineWidth = 4; g.beginPath(); g.moveTo(1180, 660); g.lineTo(1530, 720); g.moveTo(1180, 690); g.lineTo(1530, 750); g.stroke();
      return M.broken(a, { cell: 10, len: 28, wid: 8, passes: 2, angle: (x, y) => y < 520 ? -0.08 : 0.12 + (y - 500) * 0.0002, seed: 19, jit: 14, skip: 0.04, warm: [240, 200, 140], cool: [70, 70, 90], sat: 0.85 });
    }
    function sign(c) { c.save(); c.translate(1250, 600); c.rotate(-0.05); c.fillStyle = '#d8c8a0'; c.fillRect(-90, -34, 180, 58); c.strokeStyle = '#3a2c1c'; c.lineWidth = 4; c.strokeRect(-90, -34, 180, 58); c.fillStyle = '#3a2c1c'; c.fillRect(-6, 24, 12, 70);
      c.font = '700 30px Georgia, serif'; c.textAlign = 'center'; c.fillStyle = '#2a1e12'; c.fillText('ARRENDADA', 0, 6); c.restore(); }
    function sower(c, t) {                                    // silhueta grande, de perfil, passada diagonal, braço lançando a semente
      const cv = P.scratch('ml_sower'); if (cv.width !== 900) { cv.width = 900; cv.height = 900; } const g = cv.getContext('2d'); g.reset(); g.clearRect(0, 0, 900, 900);
      const ph = t * 1.5, arm = Math.sin(ph), step = Math.sin(ph) * 30;
      g.save(); g.translate(430, 820); g.scale(1.7, 1.7);
      g.fillStyle = '#2a2016'; poly(g, [[-16, -170], [-62 - step, 0], [-40 - step, 4], [10, -160]]); g.fill();          // perna de trás
      poly(g, [[-6, -170], [52 + step, -6], [76 + step, -2], [22, -168]]); g.fill();                                       // perna da frente
      g.fillStyle = '#4a3220'; g.beginPath(); g.moveTo(-34, -330); g.quadraticCurveTo(-52, -250, -30, -160); g.lineTo(34, -160); g.quadraticCurveTo(50, -250, 30, -334); g.closePath(); g.fill();   // casaco
      g.fillStyle = '#6e4a2c'; g.beginPath(); g.ellipse(-30, -215, 30, 44, 0.3, 0, TAU); g.fill();                         // bolsa de sementes
      g.save(); g.translate(20, -318); g.rotate(-1.9 + arm * 1.2); g.fillStyle = '#3a2618'; g.beginPath(); g.moveTo(-9, 0); g.lineTo(9, 0); g.lineTo(7, 130); g.lineTo(-7, 130); g.closePath(); g.fill(); g.fillStyle = '#7a5236'; g.beginPath(); g.arc(0, 136, 11, 0, TAU); g.fill(); g.restore();
      g.fillStyle = '#5a3c26'; g.beginPath(); g.ellipse(8, -362, 24, 28, 0.2, 0, TAU); g.fill();
      g.fillStyle = '#2a1e14'; g.beginPath(); g.ellipse(6, -382, 44, 11, -0.2, 0, TAU); g.fill(); g.beginPath(); g.ellipse(2, -392, 25, 19, -0.2, Math.PI, TAU); g.fill();
      g.restore();
      const rep = M.broken(cv, { cell: 6, len: 14, wid: 5, passes: 2, angle: (x, y) => 1.2 + 0.3 * Math.sin(y * 0.05), seed: 29, jit: 12, skip: 0.05, sat: 0.9, warm: [230, 190, 140], cool: [60, 50, 70] });
      const x0 = 540 - t * 10; c.drawImage(rep, x0, 230);
      const r = rng(5 + Math.floor(t * 8)); c.fillStyle = 'rgba(245,220,160,.9)';                                        // sementes no ar
      const hx = x0 + 430 + Math.cos(-1.9 + arm * 1.2 + Math.PI / 2) * 230, hy = 230 + 820 - 318 * 1.7 + Math.sin(-1.9 + arm * 1.2 + Math.PI / 2) * 230;
      for (let i = 0; i < 46; i++) { const d = 20 + r() * 300, a2 = 0.2 + r() * 1.0; c.beginPath(); c.arc(hx + Math.cos(a2) * d, hy + Math.sin(a2) * d * 0.9, 2.5 + r() * 2, 0, TAU); c.fill(); }
    }
    const crows = Array.from({ length: 9 }, (_, i) => { const r = rng(900 + i); return [r() * 900 + 200, 160 + r() * 260, r() * TAU]; });
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0); sign(c); sower(c, t);
      c.save(); c.strokeStyle = '#1e1a16'; c.lineWidth = 3; c.lineCap = 'round'; crows.forEach(([x, y, p]) => { const xx = x + t * 30, yy = y + Math.sin(t * 1.3 + p) * 8, f = Math.sin(t * 7 + p) * 9; c.beginPath(); c.moveTo(xx - 16, yy + f * .5); c.quadraticCurveTo(xx - 7, yy - f, xx, yy); c.quadraticCurveTo(xx + 7, yy - f, xx + 16, yy + f * .5); c.stroke(); }); c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.2; c.drawImage(P.texture('canvas_ml', '#e6dcc4', { scale: 0.006, amt: 14, grain: 8, seed: 12 }), 0, 0); c.restore();
    }
    return { draw };
  })();

  // =====================================================================================
  // 1) Almeida Júnior — REPROVADA pelo editor em 10/11/2026 (figura fraca, imagem pouco bonita). Fica só como registro; não usar.
  // =====================================================================================
  SCENES['mp_almeida'] = (() => {
    let bg, man, built = false;
    const SEAT = [860, 792];                       // ponto de apoio do quadril
    function background() {
      const cv = P.canvas(), g = cv.getContext('2d'), r = rng(21);
      // céu quente e pálido, morros secos e pasto amarelado (à direita, atrás do canto da casa)
      g.fillStyle = grad(g, 0, 0, 0, 600, [[0, '#cfd3cf'], [0.55, '#e6dcc2'], [1, '#e9d2a2']]); g.fillRect(0, 0, W, 640);
      g.fillStyle = '#b89a6a'; g.beginPath(); g.moveTo(1100, 560); g.quadraticCurveTo(1350, 470, 1600, 520); g.quadraticCurveTo(1780, 480, 1920, 510); g.lineTo(1920, 640); g.lineTo(1100, 640); g.fill();
      g.fillStyle = '#a38458'; g.beginPath(); g.moveTo(1100, 600); g.quadraticCurveTo(1400, 545, 1920, 585); g.lineTo(1920, 700); g.lineTo(1100, 700); g.fill();
      for (let i = 0; i < 900; i++) { const x = 1100 + r() * 820, y = 590 + Math.pow(r(), 1.4) * 200; g.fillStyle = ['#c9a96a', '#b8955a', '#d8bd84', '#9c7c4c'][(r() * 4) | 0]; g.fillRect(x, y, 2 + r() * 10, 1 + r() * 3); }
      // árvore seca no pasto
      g.strokeStyle = '#4a3a2a'; g.lineCap = 'round'; const br = (x, y, a, l, w, d) => { if (d > 6 || l < 6) return; const x2 = x + Math.cos(a) * l, y2 = y + Math.sin(a) * l; g.lineWidth = w; g.beginPath(); g.moveTo(x, y); g.lineTo(x2, y2); g.stroke(); br(x2, y2, a - 0.45 - r() * 0.3, l * 0.72, w * 0.68, d + 1); br(x2, y2, a + 0.4 + r() * 0.3, l * 0.7, w * 0.66, d + 1); };
      br(1390, 640, -Math.PI / 2 - 0.08, 70, 9, 0);
      // cerca de mourões
      g.strokeStyle = '#6a5038'; g.lineWidth = 6; for (let k = 0; k < 8; k++) { const x = 1150 + k * 105; g.beginPath(); g.moveTo(x, 700 - k * 2); g.lineTo(x + 2, 640 - k * 2); g.stroke(); }
      g.lineWidth = 2.5; g.beginPath(); g.moveTo(1150, 660); g.lineTo(1920, 648); g.moveTo(1150, 680); g.lineTo(1920, 668); g.stroke();
      // terreiro de terra vermelha (sol forte), com rachaduras e palha
      g.fillStyle = grad(g, 0, 700, 0, H, [[0, '#c48a58'], [0.5, '#b07446'], [1, '#93603a']]); g.fillRect(0, 700, W, H - 700);
      for (let i = 0; i < 1400; i++) { const x = r() * W, y = 705 + r() * 375; g.fillStyle = r() < 0.5 ? 'rgba(120,70,40,.35)' : 'rgba(230,180,130,.35)'; g.fillRect(x, y, 3 + r() * 14, 1 + r() * 3); }
      g.strokeStyle = 'rgba(90,50,28,.55)'; g.lineWidth = 2; for (let i = 0; i < 26; i++) { let x = 1000 + r() * 900, y = 840 + r() * 230; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (r() - .3) * 60; y += (r() - .5) * 22; g.lineTo(x, y); } g.stroke(); }
      g.strokeStyle = 'rgba(220,190,120,.7)'; g.lineWidth = 2; for (let i = 0; i < 70; i++) { const x = r() * W, y = 760 + r() * 300, a = r() * 3; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * 26, y + Math.sin(a) * 8); g.stroke(); }
      // parede de taipa caiada (iluminada pela esquerda), com reboco caído mostrando o barro
      g.fillStyle = grad(g, 0, 0, 1120, 0, [[0, '#d9cbae'], [0.6, '#e8dcc0'], [1, '#d2c2a0']]); g.fillRect(0, 0, 1120, 790);
      for (let i = 0; i < 7; i++) { let x = 40 + r() * 400, y = 160 + r() * 560; if (i > 3) { x = 820 + r() * 260; y = 120 + r() * 160; } const w = 60 + r() * 120, h = 30 + r() * 60; g.fillStyle = '#b08458'; const pts = []; for (let k = 0; k < 9; k++) { const a = k / 9 * TAU; pts.push([x + Math.cos(a) * w / 2 * (0.6 + r() * 0.5), y + Math.sin(a) * h / 2 * (0.6 + r() * 0.5)]); } poly(g, pts); g.fill(); g.strokeStyle = 'rgba(90,60,40,.5)'; g.lineWidth = 3; g.stroke();
        g.strokeStyle = 'rgba(120,80,50,.6)'; g.lineWidth = 2; for (let k = 0; k < 5; k++) { g.beginPath(); g.moveTo(x - w * 0.4, y - h * 0.3 + k * h * 0.15); g.lineTo(x + w * 0.4, y - h * 0.3 + k * h * 0.15 + (r() - .5) * 6); g.stroke(); } }
      for (let i = 0; i < 2200; i++) { g.fillStyle = r() < 0.5 ? 'rgba(170,150,120,.12)' : 'rgba(255,250,235,.16)'; g.fillRect(r() * 1120, r() * 790, 2 + r() * 8, 2 + r() * 8); }
      // beiral do telhado (sombra no alto da parede) e caibros
      g.fillStyle = 'rgba(60,40,25,.55)'; g.fillRect(0, 0, 1180, 70); g.fillStyle = '#6b4a2e'; g.fillRect(0, 50, 1190, 24);
      for (let k = 0; k < 12; k++) { g.fillStyle = '#5a3c24'; g.fillRect(20 + k * 98, 40, 22, 60); }
      g.fillStyle = 'rgba(80,55,35,.25)'; g.fillRect(0, 74, 1120, 90);
      // porta de madeira aberta: interior escuro
      g.fillStyle = '#2a1c14'; g.fillRect(470, 250, 300, 540);
      g.fillStyle = '#5c3e26'; g.fillRect(450, 236, 340, 22); g.fillRect(450, 236, 22, 556); g.fillRect(768, 236, 22, 556);
      g.fillStyle = '#7a5434'; poly(g, [[470, 258], [560, 270], [560, 780], [470, 790]]); g.fill();      // folha da porta aberta para dentro
      g.strokeStyle = 'rgba(40,25,15,.6)'; g.lineWidth = 3; for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(490 + k * 18, 266); g.lineTo(490 + k * 18, 784); g.stroke(); }
      // soleira (degrau de madeira)
      g.fillStyle = '#6e4c30'; g.fillRect(380, 786, 560, 30); g.fillStyle = '#8a6440'; g.fillRect(380, 786, 560, 8);
      g.fillStyle = 'rgba(40,25,15,.5)'; g.fillRect(380, 816, 560, 12);
      // sombra do corpo projetada no chão (sol da esquerda/alto)
      g.save(); g.filter = 'blur(6px)'; g.fillStyle = 'rgba(70,35,20,.45)'; poly(g, [[880, 820], [1180, 850], [1330, 900], [1260, 930], [1020, 900], [870, 860]]); g.fill(); g.restore();
      // canto da casa (aresta) e pé de parede úmido
      g.fillStyle = 'rgba(90,70,50,.35)'; g.fillRect(1100, 70, 24, 720); g.fillStyle = 'rgba(120,80,50,.25)'; g.fillRect(0, 740, 1120, 50);
      return M.broken(cv, { cell: 6, len: 15, wid: 5, passes: 2, angle: (x, y) => (y > 790 ? 0.08 : x < 1120 ? 1.5 + Math.sin(y * 0.03) * 0.3 : 0.05), seed: 5, jit: 10, skip: 0.35, sat: 1.0, warm: [255, 225, 170], cool: [120, 100, 120] });
    }
    function figure() {
      const cv = P.canvas(), g = cv.getContext('2d');
      const [sx, sy] = SEAT;
      // pernas (calça marrom arregaçada), joelhos para cima, pés descalços no chão
      g.fillStyle = '#6e5038'; poly(g, [[sx - 40, sy - 20], [sx + 120, sy - 120], [sx + 160, sy - 90], [sx + 30, sy + 8]]); g.fill();       // coxa
      g.fillStyle = '#5c422e'; poly(g, [[sx + 118, sy - 118], [sx + 160, sy - 92], [sx + 170, sy + 40], [sx + 128, sy + 44]]); g.fill();      // canela (sombra)
      g.fillStyle = '#7a5838'; poly(g, [[sx - 20, sy - 6], [sx + 80, sy - 96], [sx + 110, sy - 76], [sx + 30, sy + 16]]); g.fill();        // outra coxa
      g.fillStyle = '#6a4c32'; poly(g, [[sx + 80, sy - 94], [sx + 110, sy - 76], [sx + 100, sy + 46], [sx + 66, sy + 46]]); g.fill();
      g.fillStyle = '#8f6040'; g.beginPath(); g.ellipse(sx + 150, sy + 50, 34, 12, 0.05, 0, TAU); g.fill(); g.beginPath(); g.ellipse(sx + 88, sy + 52, 30, 11, 0, 0, TAU); g.fill();   // pés
      g.fillStyle = '#a06e48'; g.fillRect(sx + 128, sy + 18, 40, 26); g.fillRect(sx + 68, sy + 22, 34, 24);                                // tornozelos
      // tronco: camisa de algodão cru, inclinado para a frente
      g.fillStyle = grad(g, sx - 90, 0, sx + 80, 0, [[0, '#f2e8d2'], [0.55, '#e2d4b6'], [1, '#b8a888']]);
      poly(g, [[sx - 70, sy - 10], [sx - 92, sy - 170], [sx - 50, sy - 270], [sx + 40, sy - 262], [sx + 70, sy - 160], [sx + 40, sy - 20]]); g.fill();
      g.strokeStyle = 'rgba(150,130,100,.6)'; g.lineWidth = 4; [[sx - 40, sy - 240, sx - 20, sy - 60], [sx + 10, sy - 230, sx + 20, sy - 70]].forEach(([a, b, c2, d]) => { g.beginPath(); g.moveTo(a, b); g.quadraticCurveTo((a + c2) / 2 + 14, (b + d) / 2, c2, d); g.stroke(); });
      // braços: antebraços apoiados nos joelhos, mangas arregaçadas, mãos juntas
      g.fillStyle = '#d8c8a8'; poly(g, [[sx + 30, sy - 250], [sx + 70, sy - 236], [sx + 120, sy - 140], [sx + 92, sy - 124]]); g.fill();     // braço (manga)
      g.fillStyle = '#9a6a46'; poly(g, [[sx + 96, sy - 132], [sx + 122, sy - 142], [sx + 196, sy - 110], [sx + 184, sy - 92]]); g.fill();   // antebraço
      g.fillStyle = '#8a5c3c'; poly(g, [[sx - 30, sy - 240], [sx + 6, sy - 236], [sx + 70, sy - 130], [sx + 46, sy - 118]]); g.fill();
      g.fillStyle = '#7e5236'; poly(g, [[sx + 50, sy - 126], [sx + 72, sy - 134], [sx + 170, sy - 104], [sx + 160, sy - 86]]); g.fill();
      g.fillStyle = '#9a6a46'; g.beginPath(); g.ellipse(sx + 190, sy - 98, 22, 15, 0.3, 0, TAU); g.fill();                                 // mãos
      // pescoço e cabeça (rosto na sombra da aba), barba rala
      g.fillStyle = '#8a5a3a'; g.fillRect(sx - 20, sy - 300, 40, 40);
      g.fillStyle = '#93623f'; g.beginPath(); g.ellipse(sx + 6, sy - 330, 40, 48, 0.15, 0, TAU); g.fill();
      g.fillStyle = 'rgba(50,30,20,.55)'; g.beginPath(); g.ellipse(sx + 18, sy - 312, 30, 28, 0.2, 0, TAU); g.fill();
      g.fillStyle = 'rgba(40,25,15,.6)'; g.beginPath(); g.ellipse(sx + 28, sy - 342, 7, 4, 0, 0, TAU); g.fill();                         // olho na sombra
      // chapéu de palha de aba larga
      g.fillStyle = '#c9a862'; g.beginPath(); g.ellipse(sx + 4, sy - 362, 112, 26, 0.12, 0, TAU); g.fill();
      g.fillStyle = '#d8b874'; g.beginPath(); g.ellipse(sx - 2, sy - 384, 52, 38, 0.1, Math.PI, TAU); g.fill(); g.fillRect(sx - 54, sy - 386, 108, 14);
      g.fillStyle = '#5a3e24'; g.fillRect(sx - 52, sy - 378, 104, 9);
      g.strokeStyle = 'rgba(140,105,50,.6)'; g.lineWidth = 2; for (let k = -5; k <= 5; k++) { g.beginPath(); g.moveTo(sx + k * 18, sy - 352); g.lineTo(sx + k * 20, sy - 372); g.stroke(); }
      return M.broken(cv, { cell: 5, len: 11, wid: 4.5, passes: 2, angle: (x, y) => (y < sy - 300 ? 0.1 : 1.4), seed: 7, jit: 9, skip: 0.25, base: true, sat: 1.0, warm: [255, 220, 170], cool: [110, 90, 100] });
    }
    function build() { bg = background(); man = figure(); built = true; }
    const motes = Array.from({ length: 70 }, (_, i) => { const r = rng(300 + i); return [200 + r() * 1300, 150 + r() * 600, r() * TAU, 0.6 + r() * 1.6]; });
    function hen(c, t) {                                                     // galinha ciscando no terreiro
      const x = 1240 + Math.sin(t * 0.35) * 40, y = 930, peck = Math.max(0, Math.sin(t * 3.1)) ** 6;
      c.save(); c.translate(x, y); c.fillStyle = '#e9e0cc'; c.beginPath(); c.ellipse(0, 0, 34, 24, -0.1, 0, TAU); c.fill(); c.fillStyle = '#d6c8a8'; c.beginPath(); c.ellipse(-30, -10, 14, 18, -0.6, 0, TAU); c.fill();
      c.save(); c.translate(26, -14); c.rotate(peck * 1.1); c.fillStyle = '#efe6d2'; c.beginPath(); c.ellipse(10, -8, 11, 12, 0, 0, TAU); c.fill(); c.fillStyle = '#c0392b'; c.beginPath(); c.ellipse(10, -20, 7, 4, 0, 0, TAU); c.fill(); c.fillStyle = '#d8a030'; poly(c, [[20, -8], [30, -5], [20, -2]]); c.fill(); c.restore();
      c.strokeStyle = '#c89030'; c.lineWidth = 3; c.beginPath(); c.moveTo(-6, 22); c.lineTo(-8, 38); c.moveTo(8, 22); c.lineTo(10, 38); c.stroke(); c.restore();
    }
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(bg, 0, 0);
      // pasto distante tremulando de calor (faixa)
      c.save(); c.globalAlpha = 0.25; for (let y = 600; y < 700; y += 6) c.drawImage(bg, 1124, y, 796, 6, 1124 + Math.sin(t * 2 + y * 0.12) * 2, y, 796, 6); c.restore();
      hen(c, t);
      const br = 1 + Math.sin(t * 1.4) * 0.006;                              // respiração
      c.save(); c.translate(SEAT[0], SEAT[1]); c.scale(1, br); c.translate(-SEAT[0], -SEAT[1]); c.drawImage(man, 0, 0); c.restore();
      // poeira no feixe de sol
      c.save(); c.globalCompositeOperation = 'lighter';
      motes.forEach(([x, y, ph, s]) => { const xx = x + Math.sin(t * 0.4 + ph) * 30 + t * 6, yy = y + Math.cos(t * 0.3 + ph) * 18 - t * 3; c.fillStyle = `rgba(255,236,190,${0.18 + 0.12 * Math.sin(t * 2 + ph)})`; c.beginPath(); c.arc(xx, yy, s * 2, 0, TAU); c.fill(); });
      c.restore();
      // luz quente geral + vinheta suave
      c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,200,120,.25)'; c.fillRect(0, 0, W, H); c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.22; c.drawImage(P.texture('canvas_alm', '#e8dcc4', { scale: 0.006, amt: 14, grain: 8, seed: 3 }), 0, 0); c.restore();
    }
    return { draw };
  })();

  // =====================================================================================
  // 2) Van Gogh — seca: trigal ressecado, sol em redemoinho, chão rachado
  // =====================================================================================
  SCENES['mp_seca'] = (() => {
    const SUN = [1180, 290];
    let base, cracks, built = false;
    function build() {
      base = P.canvas(); const g = base.getContext('2d'), r = rng(41);
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#9fb86a'], [0.45, '#d9c450'], [1, '#f0b64a']]); g.fillRect(0, 0, W, 580);
      const sg = g.createRadialGradient(SUN[0], SUN[1], 20, SUN[0], SUN[1], 420); sg.addColorStop(0, '#fff3a0'); sg.addColorStop(0.25, '#f7d04a'); sg.addColorStop(0.6, 'rgba(240,170,60,.5)'); sg.addColorStop(1, 'rgba(240,170,60,0)'); g.fillStyle = sg; g.fillRect(0, 0, W, 600);
      g.fillStyle = '#7a6a4a'; g.beginPath(); g.moveTo(0, 560); g.quadraticCurveTo(500, 520, 960, 548); g.quadraticCurveTo(1400, 520, 1920, 556); g.lineTo(1920, 600); g.lineTo(0, 600); g.fill();
      g.fillStyle = grad(g, 0, 560, 0, 860, [[0, '#c9a050'], [1, '#b07a36']]); g.fillRect(0, 556, W, 320);
      for (let i = 0; i < 40; i++) { g.fillStyle = r() < 0.5 ? 'rgba(150,100,40,.5)' : 'rgba(220,180,90,.5)'; const y = 570 + Math.pow(r(), 1.3) * 290; g.fillRect(0, y, W, 2 + (y - 560) * 0.03); }
      g.fillStyle = grad(g, 0, 840, 0, H, [[0, '#a8743e'], [1, '#8a5a30']]); g.fillRect(0, 840, W, 240);
      cracks = P.canvas(); const k = cracks.getContext('2d'); k.strokeStyle = '#3a2414'; k.lineCap = 'round';
      for (let i = 0; i < 60; i++) { let x = r() * W, y = 860 + r() * 220; k.lineWidth = 2 + r() * 4; k.beginPath(); k.moveTo(x, y); for (let j = 0; j < 5; j++) { x += (r() - .5) * 140; y += (r() - .5) * 40; k.lineTo(x, clamp(y, 850, H)); } k.stroke(); }
      built = true;
    }
    const sunAng = (x, y, t) => { const dx = x - SUN[0], dy = y - SUN[1], d = Math.hypot(dx, dy); return Math.atan2(dy, dx) + Math.PI / 2 + 0.25 * Math.sin(d * 0.02 - t * 3); };
    const ang = (x, y, t) => y < 560 ? sunAng(x, y, t) : y < 850 ? 0.04 * Math.sin(x * 0.01) + 0.35 * Math.sin(x * 0.012 - t * 1.5) * ((y - 560) / 300) * 0.3 : 0.1;
    const stalks = Array.from({ length: 110 }, (_, i) => { const r = rng(900 + i); return [r() * W, 600 + Math.pow(r(), 0.8) * 270, r()]; });
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(base, 0, 0);
      P.strokes(c, base, { cell: 13, len: 34, width: 8, angle: ang, seed: 3, t, boil: 0, outline: 0.75, outlineCol: [40, 50, 110], outlineMix: 0.4, jitterCol: 26, mask: (x, y) => y < 556 });
      P.strokes(c, base, { cell: 11, len: 26, width: 7, angle: ang, seed: 5, t: 0, boil: 0, outline: 0.7, outlineCol: [70, 45, 30], outlineMix: 0.45, jitterCol: 22, mask: (x, y) => y >= 556 });
      // sol: anéis girando
      c.save(); c.lineCap = 'round'; for (let k = 0; k < 7; k++) { const R = 70 + k * 34, n = 14 + k * 4; for (let j = 0; j < n; j++) { const a = j / n * TAU + t * (0.3 + k * 0.05) * (k % 2 ? -1 : 1); c.strokeStyle = k < 2 ? '#fff0a0' : k < 4 ? '#f7cf48' : 'rgba(240,170,60,.75)'; c.lineWidth = 9 - k * 0.6; c.beginPath(); c.arc(SUN[0], SUN[1], R, a, a + 0.22); c.stroke(); } } c.restore();
      c.fillStyle = '#fff7c0'; c.beginPath(); c.arc(SUN[0], SUN[1], 60, 0, TAU); c.fill();
      // talos secos e quebrados, balançando
      c.save(); c.lineCap = 'round'; stalks.forEach(([x, y, q]) => { const h = 30 + (y - 600) * 0.35, sw = Math.sin(t * 2 + x * 0.02) * 0.08, bend = 0.5 + q * 0.6; c.strokeStyle = q < 0.5 ? '#8a6a34' : '#b8903e'; c.lineWidth = 2 + (y - 600) * 0.012; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + h * 0.2, y - h * 0.8, x + Math.sin(bend + sw) * h, y - Math.cos(bend + sw) * h * 0.6); c.stroke(); }); c.restore();
      c.drawImage(cracks, 0, 0);
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.2; c.drawImage(P.texture('canvas_vg', '#e8dcc0', { scale: 0.006, amt: 12, grain: 8, seed: 4 }), 0, 0); c.restore();
    }
    return { draw };
  })();

  // =====================================================================================
  // 3) Impressionismo — granizo: céu de tempestade, granizo caindo sobre o milharal
  // =====================================================================================
  SCENES['mp_granizo'] = (() => {
    let sky, field, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(61);
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#3e4256'], [0.6, '#5e6276'], [1, '#8a8a8e']]); g.fillRect(0, 0, W, 600);
      for (let i = 0; i < 40; i++) { g.save(); g.filter = 'blur(14px)'; g.fillStyle = r() < 0.5 ? 'rgba(40,40,60,.6)' : 'rgba(120,120,140,.5)'; g.beginPath(); g.ellipse(r() * W, 60 + r() * 380, 120 + r() * 220, 40 + r() * 70, 0, 0, TAU); g.fill(); g.restore(); }
      sky = M.broken(a, { cell: 10, len: 30, wid: 8, passes: 2, angle: () => -0.15, seed: 6, jit: 18, skip: 0.05, warm: [200, 200, 220], cool: [60, 60, 100] });
      const b = P.canvas(), f = b.getContext('2d');
      f.fillStyle = '#5a6a56'; f.beginPath(); f.moveTo(0, 560); f.quadraticCurveTo(700, 520, 1920, 552); f.lineTo(1920, 620); f.lineTo(0, 620); f.fill();
      f.fillStyle = '#c9c2b0'; f.fillRect(1320, 500, 80, 50); f.fillStyle = '#7a4a3a'; poly(f, [[1310, 500], [1360, 470], [1410, 500]]); f.fill();
      f.fillStyle = grad(f, 0, 580, 0, H, [[0, '#4e6e3a'], [1, '#2e4a22']]); f.fillRect(0, 580, W, H - 580);
      for (let i = 0; i < 60; i++) { const y = 590 + Math.pow(i / 60, 1.6) * 500; f.strokeStyle = i % 2 ? 'rgba(110,150,70,.7)' : 'rgba(40,60,30,.7)'; f.lineWidth = 2 + i * 0.25; f.beginPath(); f.moveTo(0, y); f.lineTo(W, y + (i % 3 - 1) * 3); f.stroke(); }
      for (let i = 0; i < 700; i++) { const k = Math.pow(r(), 1.5), y = 600 + k * 480, x = r() * W, h = 10 + k * 70; f.strokeStyle = ['#6a9a48', '#8ab45a', '#4a7a34', '#a8c070'][(r() * 4) | 0]; f.lineWidth = 2 + k * 4; f.beginPath(); f.moveTo(x, y); f.quadraticCurveTo(x - h * 0.3, y - h * 0.6, x - h * 0.5, y - h); f.stroke(); f.beginPath(); f.moveTo(x, y); f.quadraticCurveTo(x + h * 0.3, y - h * 0.5, x + h * 0.5, y - h * 0.8); f.stroke(); }
      field = M.broken(b, { cell: 8, len: 22, wid: 6, passes: 2, angle: (x, y) => y < 600 ? 0.02 : -1.2 + Math.sin(x * 0.03) * 0.5, seed: 9, jit: 22, skip: 0.04, warm: [220, 230, 160], cool: [60, 80, 110] });
      built = true;
    }
    const N = 300, hail = Array.from({ length: N }, (_, i) => { const r = rng(2000 + i); return [r() * 2200 - 140, r(), 0.6 + r() * 0.8]; });
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(sky, 0, 0); c.drawImage(field, 0, 0);
      const flash = Math.max(0, 1 - Math.abs(t - 1.1) * 6); if (flash > 0) { c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(230,230,255,${0.35 * flash})`; c.fillRect(0, 0, W, 600); c.restore(); }
      c.save(); c.lineCap = 'round';
      hail.forEach(([x0, ph, s]) => { const fall = ((t * 1.3 * s + ph) % 1), y = -40 + fall * 1160, x = x0 - fall * 260; c.strokeStyle = `rgba(225,232,248,${0.35 + 0.25 * s})`; c.lineWidth = 3 * s; c.beginPath(); c.moveTo(x, y); c.lineTo(x + 7, y - 26); c.stroke(); c.fillStyle = 'rgba(248,250,255,.98)'; c.beginPath(); c.arc(x, y, 6.5 * s, 0, TAU); c.fill(); c.strokeStyle = 'rgba(150,170,210,.8)'; c.lineWidth = 1.5; c.stroke(); });
      const r = rng(7 + Math.floor(t * 12)); const acc = Math.min(1, t / 2.5); const rs = rng(99); for (let i = 0; i < 520 * acc; i++) { const x = rs() * W, y = 610 + Math.pow(rs(), 0.8) * 470, s2 = 0.5 + (y - 610) / 470; c.fillStyle = 'rgba(244,247,255,.95)'; c.beginPath(); c.ellipse(x, y, 5 * s2, 3.5 * s2, 0, 0, TAU); c.fill(); }
      for (let i = 0; i < 70; i++) { const x = r() * W, y = 640 + r() * 440, b = r() * 22; c.fillStyle = 'rgba(250,252,255,.9)'; c.beginPath(); c.arc(x, y - b, 4 + r() * 3, 0, TAU); c.fill(); }
      c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.18; c.drawImage(P.texture('canvas_gr', '#e0dccc', { scale: 0.006, amt: 12, grain: 8, seed: 6 }), 0, 0); c.restore();
    }
    return { draw };
  })();

  // =====================================================================================
  // 4) Monet ("A Pega") — geada: campo branco, sombras azuis, cerca e uma pega no portão
  // =====================================================================================
  SCENES['mp_geada'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(81);
      g.fillStyle = grad(g, 0, 0, 0, 520, [[0, '#d4dbe0'], [1, '#efe6d8']]); g.fillRect(0, 0, W, 560);
      const sg = g.createRadialGradient(1500, 260, 10, 1500, 260, 300); sg.addColorStop(0, 'rgba(255,240,210,.9)'); sg.addColorStop(1, 'rgba(255,240,210,0)'); g.fillStyle = sg; g.fillRect(1100, 0, 820, 560);
      g.fillStyle = '#b8bcc6'; g.beginPath(); g.moveTo(0, 500); g.quadraticCurveTo(600, 450, 1200, 480); g.quadraticCurveTo(1600, 460, 1920, 490); g.lineTo(1920, 560); g.lineTo(0, 560); g.fill();
      for (let i = 0; i < 14; i++) { const x = r() * W, y = 440 + r() * 50; g.fillStyle = 'rgba(120,120,140,.55)'; g.beginPath(); g.ellipse(x, y, 30 + r() * 60, 40 + r() * 40, 0, Math.PI, TAU); g.fill(); }
      g.fillStyle = grad(g, 0, 520, 0, H, [[0, '#f2efe8'], [1, '#e2e2e6']]); g.fillRect(0, 520, W, H - 520);
      for (let i = 0; i < 260; i++) { const k = Math.pow(r(), 1.3), y = 540 + k * 540, x = r() * W; g.fillStyle = r() < 0.45 ? 'rgba(170,180,225,.35)' : r() < 0.7 ? 'rgba(255,246,232,.45)' : 'rgba(225,215,235,.35)'; g.beginPath(); g.ellipse(x, y, 60 + r() * 200 * (0.4 + k), 8 + r() * 22 * (0.4 + k), (r() - .5) * 0.08, 0, TAU); g.fill(); }
      for (let i = 0; i < 500; i++) { const k = Math.pow(r(), 1.4), y = 560 + k * 500, x = r() * W, h = 6 + k * 34; g.strokeStyle = r() < 0.6 ? '#9aa890' : '#c8d0c0'; g.lineWidth = 2 + k * 3; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - .5) * 10, y - h); g.stroke(); }
      // sombras azuis longas (sol baixo à direita)
      g.save(); g.filter = 'blur(8px)'; g.fillStyle = 'rgba(110,130,200,.45)'; poly(g, [[300, 760], [900, 700], [940, 740], [320, 820]]); g.fill(); g.restore();
      // cerca de vime/madeira e portão
      g.fillStyle = '#6a5a4c'; for (let k = 0; k < 14; k++) { const x = 220 + k * 66; g.fillRect(x, 610 + k * 4, 12, 150); }
      g.strokeStyle = '#7a6a58'; g.lineWidth = 9; g.beginPath(); g.moveTo(210, 640); g.lineTo(1140, 690); g.moveTo(210, 700); g.lineTo(1140, 750); g.stroke();
      g.fillStyle = '#7a6a58'; g.fillRect(1150, 600, 18, 210); g.fillRect(1380, 590, 18, 220);
      g.strokeStyle = '#8a7a66'; g.lineWidth = 8; for (const yy of [640, 690, 740]) { g.beginPath(); g.moveTo(1168, yy); g.lineTo(1380, yy - 6); g.stroke(); } g.beginPath(); g.moveTo(1168, 790); g.lineTo(1380, 650); g.stroke();
      g.fillStyle = 'rgba(255,255,255,.85)'; g.fillRect(200, 632, 940, 6); g.fillRect(1150, 596, 250, 6);
      plate = M.broken(a, { cell: 8, len: 20, wid: 7, passes: 2, angle: (x, y) => y < 520 ? -0.05 : 0.15 * Math.sin(x * 0.013 + y * 0.02) + (y > 800 ? 0.25 : 0), seed: 12, jit: 20, skip: 0.04, warm: [255, 236, 200], cool: [140, 150, 220], sat: 1.0 });
      built = true;
    }
    const spark = Array.from({ length: 140 }, (_, i) => { const r = rng(4000 + i); return [r() * W, 560 + r() * 500, r() * TAU]; });
    function magpie(c, t) {
      const x = 1270, y = 588, hop = Math.max(0, Math.sin(t * 2.4)) ** 8 * 10, tilt = Math.sin(t * 1.7) * 0.15;
      c.save(); c.translate(x, y - hop); c.fillStyle = '#16181e'; c.beginPath(); c.ellipse(0, 0, 26, 15, -0.2, 0, TAU); c.fill(); c.fillStyle = '#f2f2f4'; c.beginPath(); c.ellipse(4, 4, 14, 8, -0.2, 0, TAU); c.fill();
      c.fillStyle = '#16181e'; poly(c, [[-20, 2], [-74, 16], [-70, 8], [-18, -6]]); c.fill();
      c.save(); c.translate(22, -10); c.rotate(tilt); c.beginPath(); c.arc(0, 0, 10, 0, TAU); c.fill(); poly(c, [[8, -2], [20, 0], [8, 3]]); c.fill(); c.restore();
      c.strokeStyle = '#16181e'; c.lineWidth = 2.5; c.beginPath(); c.moveTo(-2, 14); c.lineTo(-2, 22 + hop); c.moveTo(6, 14); c.lineTo(6, 22 + hop); c.stroke(); c.restore();
    }
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(plate, 0, 0);
      c.save(); c.globalAlpha = 0.25; c.filter = 'blur(18px)'; c.fillStyle = '#ffffff'; c.beginPath(); c.ellipse(700 + t * 40, 500, 700, 50, 0, 0, TAU); c.fill(); c.restore();
      c.save(); c.globalCompositeOperation = 'lighter'; spark.forEach(([x, y, ph]) => { const a = Math.max(0, Math.sin(t * 4 + ph)) ** 6; if (a < 0.05) return; c.fillStyle = `rgba(255,255,255,${a})`; c.beginPath(); c.arc(x, y, 2 + a * 2.5, 0, TAU); c.fill(); c.fillRect(x - 6 * a, y - 0.6, 12 * a, 1.2); }); c.restore();
      magpie(c, t);
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.15; c.drawImage(P.texture('canvas_ge', '#ece6dc', { scale: 0.006, amt: 10, grain: 7, seed: 8 }), 0, 0); c.restore();
    }
    return { draw };
  })();

  // =====================================================================================
  // 5) Van Gogh — vendaval: cipreste em chama, trigal dobrando em ondas, céu em espiral
  // =====================================================================================
  SCENES['mp_vendaval'] = (() => {
    let base, built = false;
    const SP = [[700, 220], [1350, 300]];
    function build() {
      base = P.canvas(); const g = base.getContext('2d'), r = rng(101);
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#2a4a8a'], [0.6, '#5a86b8'], [1, '#a8c0c8']]); g.fillRect(0, 0, W, 580);
      SP.forEach(([x, y]) => { const sg = g.createRadialGradient(x, y, 10, x, y, 200); sg.addColorStop(0, 'rgba(230,236,240,.9)'); sg.addColorStop(1, 'rgba(230,236,240,0)'); g.fillStyle = sg; g.fillRect(x - 220, y - 220, 440, 440); });
      g.fillStyle = '#4a6a6a'; g.beginPath(); g.moveTo(0, 540); g.quadraticCurveTo(500, 470, 1000, 520); g.quadraticCurveTo(1500, 480, 1920, 530); g.lineTo(1920, 600); g.lineTo(0, 600); g.fill();
      g.fillStyle = grad(g, 0, 560, 0, H, [[0, '#d8b440'], [0.5, '#c89a30'], [1, '#9a7020']]); g.fillRect(0, 560, W, H - 560);
      for (let i = 0; i < 30; i++) { const y = 580 + Math.pow(i / 30, 1.4) * 500; g.fillStyle = i % 2 ? 'rgba(240,210,90,.6)' : 'rgba(150,110,30,.5)'; g.fillRect(0, y, W, 4 + i * 0.8); }
      built = true;
    }
    const spiral = (x, y, t) => { let best = null, bd = 1e9; for (const [sx, sy] of SP) { const d = Math.hypot(x - sx, y - sy); if (d < bd) { bd = d; best = [sx, sy]; } } const a = Math.atan2(y - best[1], x - best[0]); return bd < 260 ? a + Math.PI / 2 + 0.3 : -0.25 + 0.3 * Math.sin(x * 0.006 + y * 0.01 - t * 2); };
    const wheatA = (x, y, t) => -0.35 + 0.55 * Math.sin(x * 0.012 - t * 5 + y * 0.004) * clamp((y - 560) / 400, 0.3, 1);
    function cypress(c, t) {
      const x0 = 1180, y0 = 1000, Hc = 760, sw = Math.sin(t * 3.2) * 28;
      c.save(); c.lineCap = 'round';
      c.fillStyle = '#1c3220'; c.beginPath(); c.moveTo(x0 - 110, y0); for (let k = 0; k <= 20; k++) { const v = k / 20, w = Math.sin(Math.min(1, (1 - v) * 1.4) * Math.PI / 2) * 110 * (1 - v * 0.65); c.lineTo(x0 - w + sw * v * v, y0 - v * Hc); } for (let k = 20; k >= 0; k--) { const v = k / 20, w = Math.sin(Math.min(1, (1 - v) * 1.4) * Math.PI / 2) * 110 * (1 - v * 0.65); c.lineTo(x0 + w + sw * v * v, y0 - v * Hc); } c.fill();
      for (let i = 0; i < 900; i++) { const r = rng(6000 + i), v = Math.pow(r(), 0.8), y = y0 - v * Hc, wdt = Math.sin(Math.min(1, (1 - v) * 1.4) * Math.PI / 2) * 120 * (1 - v * 0.65), x = x0 + (r() - .5) * 2 * wdt + sw * v * v;
        const a = -Math.PI / 2 + (r() - .5) * 0.9 + sw * 0.004 * v; c.strokeStyle = ['#1f3a22', '#2e5230', '#3e6a3a', '#162a1a', '#55804a'][(r() * 5) | 0]; c.lineWidth = 11; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + Math.cos(a + 0.6) * 18, y + Math.sin(a + 0.6) * 18, x + Math.cos(a) * 46, y + Math.sin(a) * 46); c.stroke(); }
      c.restore();
    }
    const leaves = Array.from({ length: 50 }, (_, i) => { const r = rng(7000 + i); return [r(), r() * 900 + 100, r() * TAU]; });
    function draw(c, lt) {
      if (!built) build();
      const t = Math.max(0, lt);
      c.drawImage(base, 0, 0);
      P.strokes(c, base, { cell: 13, len: 40, width: 8, angle: spiral, seed: 11, t, boil: 0, outline: 0.8, outlineCol: [20, 30, 80], outlineMix: 0.45, jitterCol: 24, mask: (x, y) => y < 560 });
      P.strokes(c, base, { cell: 10, len: 30, width: 7, angle: wheatA, seed: 13, t, boil: 0, outline: 0.7, outlineCol: [80, 50, 20], outlineMix: 0.45, jitterCol: 26, mask: (x, y) => y >= 556 });
      cypress(c, t);
      c.save(); c.lineCap = 'round'; leaves.forEach(([ph, y, a]) => { const x = ((ph + t * 0.45) % 1) * 2200 - 140, yy = y + Math.sin(t * 4 + a) * 40; c.strokeStyle = '#e0c060'; c.lineWidth = 6; c.beginPath(); c.moveTo(x, yy); c.lineTo(x + 18 * Math.cos(t * 6 + a), yy + 8 * Math.sin(t * 6 + a)); c.stroke(); }); c.restore();
      c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.2; c.drawImage(P.texture('canvas_vd', '#e8dcc0', { scale: 0.006, amt: 12, grain: 8, seed: 9 }), 0, 0); c.restore();
    }
    return { draw };
  })();
})();
