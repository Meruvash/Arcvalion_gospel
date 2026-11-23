// Cenas do vídeo "Multa ambiental prescreve?" — pintadas em código, SEM figura humana. Recorte central x 420..1500.
// Composições novas, à maneira de mestres em domínio público:
//   ib_menzel   — Adolph Menzel (1815–1905): a escrivaninha velha junto da janela, a gaveta aberta com papéis amarelados
//                 e um envelope; poeira na luz (a multa esquecida na gaveta)
//   ib_inness   — George Inness (1825–1894): o pasto em névoa dourada, o sol cruzando o céu e as estações passando
//                 (o verde seca e volta): os anos correndo
//   ib_whistler — James McNeill Whistler (1834–1903): noturno azul sobre a represa da fazenda, luzes da sede refletidas,
//                 um relógio de parede que volta ao zero (o prazo interrompido)
//   ib_durand   — Asher Brown Durand (1796–1886): a nascente com a mata ciliar, mudas novas plantadas na margem
//                 (o dever de reparar o dano continua)
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 173 }), 0, 0); c.restore(); };

  // ---------------------------------------------------------------- Menzel: a gaveta com a multa esquecida
  SCENES['ib_menzel'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, H, [[0, '#6a5a44'], [1, '#3a2e22']]); g.fillRect(0, 0, W, H);   // a parede escura de madeira
      g.fillStyle = '#e8dcb8'; g.fillRect(1180, 120, 300, 420);   // a janela clara
      g.fillStyle = grad(g, 0, 140, 0, 520, [[0, '#cfe0e8'], [.6, '#e8e4c8'], [.61, '#9aae6a'], [1, '#6a8a42']]); g.fillRect(1196, 136, 268, 388);
      g.fillStyle = '#5a4630'; g.fillRect(1326, 136, 10, 388); g.fillRect(1196, 320, 268, 10);
      g.fillStyle = '#6a4a2a'; g.fillRect(460, 560, 900, 40);   // o tampo da escrivaninha
      g.fillStyle = '#5a3e22'; g.fillRect(480, 600, 860, 300);   // o corpo
      g.fillStyle = '#4a3218'; g.fillRect(500, 900, 40, 180); g.fillRect(1280, 900, 40, 180);
      g.fillStyle = '#7a5630'; poly(g, [[600, 690], [1100, 690], [1180, 800], [540, 800]]); g.fill();   // a gaveta puxada pra fora
      g.fillStyle = '#3a2614'; poly(g, [[620, 700], [1080, 700], [1150, 790], [560, 790]]); g.fill();
      const r = rng(23);   // os papéis amarelados dentro da gaveta
      for (let i = 0; i < 9; i++) { g.save(); g.translate(640 + i * 50, 700 + r() * 20); g.rotate((r() - .5) * .3); g.fillStyle = ['#e8d8a0', '#dccb8a', '#f0e2b0'][i % 3]; g.fillRect(0, 0, 120, 70); g.restore(); }
      g.fillStyle = '#f2e6c4'; g.save(); g.translate(820, 520); g.rotate(-.08); g.fillRect(0, 0, 220, 120); g.restore();   // o envelope sobre a mesa
      g.strokeStyle = '#b8a070'; g.lineWidth = 4; g.beginPath(); g.moveTo(822, 522); g.lineTo(930, 590); g.lineTo(1038, 506); g.stroke();
      ell(g, 560, 540, 40, 14, 0, '#3a3a3a'); g.fillStyle = '#c8b070'; g.fillRect(552, 470, 16, 70);   // o lampião apagado
      return M.broken(a, { cell: 7, len: 13, wid: 8, passes: 3, angle: (x, y) => (y < 560 ? 1.57 : 0.1), seed: 1301, jit: 10, skip: 0.05, sat: 0.95, warm: [240, 210, 150], cool: [70, 60, 70] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen';   // o feixe de luz da janela sobre a mesa
      c.fillStyle = `rgba(255,236,190,${.18 + .05 * Math.sin(t * .9)})`; poly(c, [[1180, 140], [1480, 140], [1120, 900], [620, 900]]); c.fill(); c.restore();
      const r = rng(8); c.save();   // poeira dançando na luz
      for (let i = 0; i < 50; i++) { const x = 700 + r() * 650 + Math.sin(t * .7 + i) * 12, y = 200 + ((r() * 650 + t * (6 + r() * 10)) % 650); c.fillStyle = `rgba(255,240,200,${.3 + .3 * r()})`; c.fillRect(x, y, 3, 3); }
      c.restore();
      tela(c, 'canvas_mz', '#e8d8b8');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Inness: os anos passando no pasto
  SCENES['ib_inness'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 640, [[0, '#c8b080'], [1, '#f0dca8']]); g.fillRect(0, 0, W, 640);
      g.fillStyle = '#8a8a6a'; poly(g, [[0, 640], [600, 600], [1200, 630], [1920, 590], [1920, 660], [0, 660]]); g.fill();
      g.fillStyle = grad(g, 0, 650, 0, H, [[0, '#8a9a52'], [1, '#4a5a2a']]); g.fillRect(0, 650, W, H - 650);
      for (let k = 0; k < 3; k++) {   // as árvores isoladas do pasto
        const x = [620, 1040, 1380][k], s = [1, .7, .85][k];
        g.fillStyle = '#3a3020'; g.fillRect(x - 8 * s, 640 - 160 * s, 16 * s, 175 * s);
        ell(g, x + 30 * s, 650, 120 * s, 14 * s, 0, 'rgba(40,50,25,.5)'); ell(g, x, 640 - 200 * s, 110 * s, 80 * s, 0, '#4a5a32'); ell(g, x + 40 * s, 640 - 230 * s, 70 * s, 50 * s, 0, '#5a6a3a');
      }
      return M.broken(a, { cell: 9, len: 20, wid: 11, passes: 3, angle: () => 0.15, seed: 1409, jit: 14, skip: 0.05, sat: 0.9, warm: [250, 220, 160], cool: [90, 100, 110] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt), cyc = (t / 2.2) % 1;   // um "ano" a cada 2,2 s
      const sx = lerp(380, 1540, cyc), sy = 330 - Math.sin(cyc * Math.PI) * 250;
      c.drawImage(plate, 0, 0);
      ell(c, sx, sy, 46, 46, 0, 'rgba(255,240,190,.9)');   // o sol atravessando o céu
      c.save(); c.globalCompositeOperation = 'multiply';   // a estação seca: o verde vira palha e volta
      const seca = (Math.sin(t / 2.2 * TAU) + 1) / 2; c.fillStyle = `rgba(220,170,90,${.35 * seca})`; c.fillRect(0, 650, W, H - 650); c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = 'rgba(255,250,235,.12)'; c.fillRect(0, 560, W, 160); c.restore();   // a névoa
      tela(c, 'canvas_in', '#ece0c4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Whistler: noturno e o relógio que volta ao zero
  SCENES['ib_whistler'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#14243a'], [1, '#3a5270']]); g.fillRect(0, 0, W, 560);
      g.fillStyle = '#1a2a3a'; poly(g, [[0, 560], [700, 520], [1300, 545], [1920, 515], [1920, 580], [0, 580]]); g.fill();   // a mata escura
      g.fillStyle = grad(g, 0, 575, 0, H, [[0, '#2a4260'], [1, '#101c2c']]); g.fillRect(0, 575, W, H - 575);   // a represa
      g.fillStyle = '#22303e'; g.fillRect(780, 470, 260, 90); poly(g, [[760, 474], [910, 410], [1060, 474]]); g.fill();   // a sede
      g.fillStyle = '#f0c870'; g.fillRect(820, 500, 30, 30); g.fillRect(960, 500, 30, 30);
      return M.broken(a, { cell: 9, len: 24, wid: 12, passes: 3, angle: () => 0, seed: 1511, jit: 8, skip: 0.04, sat: 0.85, warm: [240, 200, 140], cool: [40, 60, 100] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); for (let i = 0; i < 6; i++) { const y = 600 + i * 28, a = .25 + .15 * Math.sin(t * 2 + i); c.fillStyle = `rgba(240,200,112,${a})`; c.fillRect(820 + Math.sin(t * 1.5 + i) * 6, y, 30, 6); c.fillRect(960 + Math.sin(t * 1.3 + i) * 6, y, 30, 6); } c.restore();   // o reflexo das janelas
      const cx = 1260, cy = 260, R = 120;   // o relógio grande pintado no céu: o ponteiro corre e volta ao zero
      ell(c, cx, cy, R + 10, R + 10, 0, 'rgba(230,220,190,.85)'); ell(c, cx, cy, R, R, 0, 'rgba(245,238,215,.95)');
      c.strokeStyle = '#2a2a2a'; c.lineWidth = 4; for (let k = 0; k < 12; k++) { const an = k / 12 * TAU; c.beginPath(); c.moveTo(cx + Math.sin(an) * (R - 16), cy - Math.cos(an) * (R - 16)); c.lineTo(cx + Math.sin(an) * (R - 4), cy - Math.cos(an) * (R - 4)); c.stroke(); }
      const ciclo = t % 3.2, ang = ciclo < 2.6 ? (ciclo / 2.6) * TAU * .85 : TAU * .85 * (1 - (ciclo - 2.6) / .6);
      c.strokeStyle = '#8a1a10'; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.sin(ang) * (R - 24), cy - Math.cos(ang) * (R - 24)); c.stroke();
      ell(c, cx, cy, 9, 9, 0, '#2a2a2a');
      const r = rng(4); c.save(); for (let i = 0; i < 70; i++) { c.fillStyle = `rgba(255,255,230,${.3 + .5 * Math.abs(Math.sin(t * 1.7 + i))})`; c.fillRect(420 + r() * 1080, r() * 420, 2, 2); } c.restore();   // estrelas
      tela(c, 'canvas_wh', '#d8dce4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Durand: a nascente e as mudas novas
  SCENES['ib_durand'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 500, [[0, '#a8c0c8'], [1, '#e8e4cc']]); g.fillRect(0, 0, W, 500);
      for (let k = 0; k < 10; k++) {   // a mata ciliar alta dos dois lados
        const x = k < 5 ? 420 + k * 70 : 1180 + (k - 5) * 70, h = 520 + (k % 3) * 60;
        g.fillStyle = '#3a3020'; g.fillRect(x, 700 - h, 14, h);
        for (let j = 0; j < 4; j++) ell(g, x + 7 + (j % 2 ? 40 : -30), 700 - h + j * 70, 80, 60, 0, ['#3a5a2a', '#4a6a32', '#2e4a22'][j % 3]);
      }
      g.fillStyle = grad(g, 0, 620, 0, H, [[0, '#6a7a3a'], [1, '#3a4a22']]); g.fillRect(0, 620, W, H - 620);
      g.fillStyle = grad(g, 0, 640, 0, H, [[0, '#9ab8c0'], [1, '#5a7a8a']]); g.beginPath(); g.moveTo(940, 640); g.bezierCurveTo(1060, 760, 840, 880, 1000, 1080); g.lineTo(700, 1080); g.bezierCurveTo(820, 900, 860, 760, 920, 640); g.closePath(); g.fill();   // o córrego sinuoso
      g.fillStyle = '#7a6a4a'; for (let i = 0; i < 12; i++) ell(g, 760 + (i * 37) % 300, 760 + i * 26, 18, 9, 0, '#8a7a5a');   // pedras da margem
      for (let i = 0; i < 6; i++) {   // as mudas novas plantadas na margem, com estaca
        const x = i < 3 ? 640 + i * 70 : 1210 + (i - 3) * 70, y = 900 + (i % 2) * 40;
        g.fillStyle = '#c8a870'; g.fillRect(x, y - 90, 6, 90); ell(g, x + 3, y - 60, 22, 16, 0, '#6aa040'); ell(g, x - 10, y - 40, 16, 10, 0, '#7ab04a');
      }
      return M.broken(a, { cell: 7, len: 14, wid: 8, passes: 3, angle: (x, y) => (y < 620 ? 1.4 : 0.3), seed: 1601, jit: 11, skip: 0.05, sat: 1.0, warm: [240, 230, 190], cool: [90, 120, 130] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.strokeStyle = 'rgba(240,250,255,.55)'; c.lineWidth = 3;   // a água correndo
      const rr = rng(31); for (let i = 0; i < 22; i++) { const p = ((t * .2 + rr()) % 1), y = lerp(660, 1060, p), cx = 930 + Math.sin(p * 5.5) * 70 - p * 80, w = lerp(10, 50, p); c.beginPath(); c.moveTo(cx - w / 2, y); c.quadraticCurveTo(cx, y - 4, cx + w / 2, y); c.stroke(); }
      c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,250,220,${.08 + .04 * Math.sin(t)})`; c.fillRect(0, 0, W, H); c.restore();
      tela(c, 'canvas_du', '#e8e4cc');
    }
    return { draw };
  })();
})();
