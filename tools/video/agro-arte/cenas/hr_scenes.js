// Cenas do vídeo "O irmão vendeu sem avisar" (herança de fazenda) — pintadas em código, sem imagem gerada por IA.
// Recorte central x 420..1500. Composições novas, à maneira de mestres em domínio público:
//   hr_constable — John Constable (1776–1837): porteira de madeira fechada com corrente e cadeado, céu de nuvens altas
//   hr_courbet   — Gustave Courbet (1819–1877): placa "VENDE-SE" pregada na cerca, céu fechando sobre o pasto
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.17; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 61 }), 0, 0); c.restore(); };
  const nuvens = (g, r, n, y0, y1, cor, sombra) => { for (let i = 0; i < n; i++) { const x = 380 + r() * 1180, y = y0 + r() * (y1 - y0), w = 90 + r() * 200;
    g.fillStyle = grad(g, 0, y - w * .4, 0, y + w * .3, [[0, cor], [1, sombra]]); for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(x + (r() - .5) * w * 1.4, y + (r() - .5) * w * .3, w * (.35 + r() * .35), w * (.18 + r() * .14), 0, 0, TAU); g.fill(); } } };

  // ---------------------------------------------------------------- Constable: porteira fechada com corrente
  SCENES['hr_constable'] = (() => {
    let plate, built = false; const HZ = 560;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1501);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#4a72a8'], [0.6, '#a8bcd0'], [1, '#e8e4d0']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 16, 60, 380, '#fbf8ee', '#8a96a8');
      g.fillStyle = '#4a6a3a'; g.beginPath(); g.moveTo(0, HZ); g.quadraticCurveTo(600, HZ - 60, 1200, HZ - 20); g.quadraticCurveTo(1600, HZ - 50, 1920, HZ); g.lineTo(1920, HZ + 30); g.lineTo(0, HZ + 30); g.fill();
      for (let i = 0; i < 40; i++) { g.fillStyle = ['#2f4a26', '#3f5a2e', '#4a6a34'][i % 3]; g.beginPath(); g.ellipse(380 + r() * 400, HZ - 20 - r() * 120, 40 + r() * 40, 30 + r() * 30, 0, 0, TAU); g.fill(); }     // olmos à esquerda (Constable)
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#8aa858'], [1, '#4a6a2a']]); g.fillRect(0, HZ + 20, W, H - HZ);
      g.fillStyle = '#c8b078'; poly(g, [[880, HZ + 20], [1040, HZ + 20], [1160, H], [760, H]]); g.fill();                              // estrada que entra na fazenda
      // moirões grossos e porteira de cinco tábuas, fechada
      g.fillStyle = '#5a3e26'; g.fillRect(700, 560, 46, 360); g.fillRect(1180, 560, 46, 360);
      g.fillStyle = '#8a6a44'; for (let k = 0; k < 5; k++) g.fillRect(746, 600 + k * 52, 434, 20);
      g.strokeStyle = '#8a6a44'; g.lineWidth = 18; g.beginPath(); g.moveTo(756, 820); g.lineTo(1170, 610); g.stroke();
      // cerca seguindo dos dois lados
      g.fillStyle = '#6a4a2e'; for (const x of [440, 560, 1340, 1460]) g.fillRect(x, 620, 20, 260); g.fillRect(420, 660, 280, 12); g.fillRect(1226, 660, 280, 12);
      return M.broken(a, { cell: 7, len: 16, wid: 6, passes: 2, angle: (x, y) => y < HZ ? 0.1 + Math.sin(x * 0.005) * 0.4 : -1.3, seed: 151, jit: 12, skip: 0.05, sat: 1.05, warm: [255, 232, 186], cool: [90, 110, 150] });
    }
    function corrente(c, t) {                                                    // corrente e cadeado balançando de leve no moirão
      const sw = Math.sin(t * 1.6) * 0.06; c.save(); c.translate(1190, 690); c.rotate(sw);
      c.strokeStyle = '#8a8a90'; c.lineWidth = 6; for (let i = 0; i < 9; i++) { c.beginPath(); c.ellipse(-30 + i * 9, Math.sin(i * .6) * 14 + i * 3, 9, 6, i % 2 ? 1.2 : .2, 0, TAU); c.stroke(); }
      c.fillStyle = '#c8a040'; c.fillRect(-4, 40, 34, 30); c.strokeStyle = '#a8a8ae'; c.lineWidth = 6; c.beginPath(); c.arc(13, 40, 11, Math.PI, TAU); c.stroke(); c.restore();
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0); corrente(c, t);
      c.save(); c.globalAlpha = .18; c.fillStyle = 'rgba(40,50,70,1)'; c.translate(-((t * 30) % 600), 0); for (let k = 0; k < 4; k++) { c.beginPath(); c.ellipse(500 + k * 600, 820, 380, 70, 0, 0, TAU); c.fill(); } c.restore();   // sombra de nuvem passando
      tela(c, 'canvas_cs', '#e8dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Courbet: placa VENDE-SE na cerca, céu fechando
  SCENES['hr_courbet'] = (() => {
    let plate, built = false; const HZ = 600;
    function build() {
      const a = P.canvas(), g = a.getContext('2d'), r = rng(1601);
      g.fillStyle = grad(g, 0, 0, 0, HZ, [[0, '#2a2e36'], [0.5, '#5a5a5a'], [1, '#a8a088']]); g.fillRect(0, 0, W, HZ);
      nuvens(g, r, 18, 40, 420, '#8a8a88', '#2a2a30');
      g.fillStyle = '#3a4a2a'; g.fillRect(0, HZ - 10, W, 40);
      g.fillStyle = grad(g, 0, HZ, 0, H, [[0, '#6a7a3a'], [1, '#3a4a20']]); g.fillRect(0, HZ + 20, W, H - HZ);
      g.fillStyle = '#c8a878'; g.fillRect(1240, HZ - 60, 110, 70); g.fillStyle = '#6a2a1a'; poly(g, [[1230, HZ - 58], [1295, HZ - 100], [1360, HZ - 58]]); g.fill();   // a casa da família ao longe
      // cerca de arame em primeiro plano com a placa pregada num moirão
      g.fillStyle = '#4a3420'; for (let k = 0; k < 9; k++) g.fillRect(420 + k * 140, 700 + k * 6, 20, 260);
      g.strokeStyle = '#2a2a2a'; g.lineWidth = 3; for (const y of [760, 820, 880]) { g.beginPath(); g.moveTo(420, y); g.lineTo(1520, y + 50); g.stroke(); }
      return M.broken(a, { cell: 8, len: 18, wid: 7, passes: 2, angle: (x, y) => y < HZ ? 0.15 + Math.sin(x * 0.004 + y * 0.01) * 0.6 : -1.3, seed: 161, jit: 14, skip: 0.05, sat: 0.95, warm: [230, 200, 150], cool: [70, 80, 100] });
    }
    function placa(c, t) {
      const sw = Math.sin(t * 2.4) * 0.05; c.save(); c.translate(840, 640); c.rotate(-0.06 + sw);
      c.fillStyle = '#f2ead6'; c.fillRect(-170, 0, 340, 130); c.strokeStyle = '#3a2a1a'; c.lineWidth = 6; c.strokeRect(-170, 0, 340, 130);
      c.fillStyle = '#b0281a'; c.font = '900 62px Georgia, serif'; c.textAlign = 'center'; c.fillText('VENDE-SE', 0, 88); c.restore();
      c.strokeStyle = '#3a2a1a'; c.lineWidth = 3; c.beginPath(); c.moveTo(700, 650); c.lineTo(980, 640); c.stroke();
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), d = ss(0, 8, t);
      c.drawImage(plate, 0, 0); placa(c, t);
      c.save(); c.fillStyle = `rgba(14,16,24,${0.1 + 0.3 * d})`; c.fillRect(0, 0, W, H); c.restore();                                       // o céu fecha
      const r = rng(7 + Math.floor(t * 14)); c.strokeStyle = `rgba(200,200,210,${0.25 * d})`; c.lineWidth = 1.5;                    // chuva fina chegando
      for (let i = 0; i < 160 * d; i++) { const x = 420 + r() * 1080, y = r() * H; c.beginPath(); c.moveTo(x, y); c.lineTo(x - 8, y + 26); c.stroke(); }
      tela(c, 'canvas_cb', '#e0d8c4');
    }
    return { draw };
  })();
})();
