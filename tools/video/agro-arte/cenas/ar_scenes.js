// Cenas do vídeo "Vendeu a terra arrendada sem avisar?" — pintadas em código, SEM figura humana (crivo de 21/11/2026).
// Recorte central x 420..1500. Composições novas, à maneira de mestres em domínio público:
//   ar_ruisdael  — Jacob van Ruisdael (1629–1682): a lavoura sob o céu enorme de nuvens, sombras de nuvem correndo
//                  sobre a plantação, a placa "VENDE-SE" na cerca
//   ar_hobbema   — Meindert Hobbema (1638–1709): a estrada reta entre árvores altas e finas até a sede da fazenda
//   ar_kuindzhi  — Arkhip Kuindzhi (1842–1910): o fim de tarde em brasa sobre os sulcos, a enxada e o chapéu de palha
//                  deixados na terra (quem trabalha a terra com as próprias mãos)
//   ar_levitan   — Isaac Levitan (1860–1900): a caixa de correio de madeira na beira da estrada de terra, bétulas e névoa;
//                  a bandeirinha sobe (chegou a notificação)
//   ar_hammershoi — Vilhelm Hammershøi (1864–1916): a sala vazia e cinzenta, a mesa com papéis e a janela para a lavoura
//                  lá longe (quem arrenda só como negócio)
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 131 }), 0, 0); c.restore(); };

  // ---------------------------------------------------------------- Ruisdael: o céu enorme e a placa de venda
  SCENES['ar_ruisdael'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 700, [[0, '#4a6a9a'], [.6, '#9ab4cc'], [1, '#e8e0c8']]); g.fillRect(0, 0, W, 700);
      const r = rng(41);   // os cúmulos grandes, iluminados por cima
      for (let i = 0; i < 16; i++) {
        const x = 360 + r() * 1200, y = 120 + r() * 380, s = 0.6 + r() * 0.9;
        ell(g, x + 20 * s, y + 34 * s, 190 * s, 60 * s, 0, 'rgba(120,124,140,.55)');
        ell(g, x - 40 * s, y, 150 * s, 90 * s, 0, '#d8d4cc'); ell(g, x + 80 * s, y - 20 * s, 120 * s, 80 * s, 0, '#ece8de');
        ell(g, x + 10 * s, y - 50 * s, 90 * s, 60 * s, 0, '#f8f4ea');
      }
      g.fillStyle = '#5a6a5a'; poly(g, [[0, 700], [500, 670], [900, 690], [1400, 660], [1920, 690], [1920, 730], [0, 730]]); g.fill();   // mata ao longe
      g.fillStyle = grad(g, 0, 720, 0, H, [[0, '#8a9a4a'], [1, '#4a5a28']]); g.fillRect(0, 720, W, H - 720);   // a lavoura
      g.strokeStyle = 'rgba(50,70,30,.5)'; g.lineWidth = 4;   // as linhas de plantio
      for (let k = -14; k <= 14; k++) { g.beginPath(); g.moveTo(960 + k * 30, 722); g.lineTo(960 + k * 190, H); g.stroke(); }
      g.fillStyle = '#6a5030';   // a cerca
      for (let k = 0; k < 4; k++) g.fillRect(420, 730 + k * 46, 600, 12);
      for (let k = 0; k < 5; k++) g.fillRect(430 + k * 150, 700, 20, 250);
      g.fillStyle = '#efe6cc'; g.fillRect(640, 620, 330, 120); g.strokeStyle = '#5a4026'; g.lineWidth = 8; g.strokeRect(640, 620, 330, 120);   // a placa
      g.fillStyle = '#5a4026'; g.fillRect(700, 740, 18, 70); g.fillRect(890, 740, 18, 70);
      g.fillStyle = '#8a2a1a'; g.font = '900 64px Georgia, serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('VENDE-SE', 805, 682);
      return M.broken(a, { cell: 8, len: 16, wid: 9, passes: 3, angle: (x, y) => y < 700 ? Math.sin(x * .004) * .5 : -.2, seed: 719, jit: 12, skip: 0.04, sat: 0.95, warm: [245, 230, 190], cool: [90, 110, 150] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'multiply';   // sombras de nuvem correndo sobre a lavoura
      for (let i = 0; i < 3; i++) {
        const x = ((t * 70 + i * 620) % 2200) - 140;
        const gr = c.createRadialGradient(x, 900, 20, x, 900, 380); gr.addColorStop(0, 'rgba(60,70,90,.45)'); gr.addColorStop(1, 'rgba(60,70,90,0)');
        c.fillStyle = gr; c.fillRect(0, 720, W, H - 720);
      }
      c.restore();
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,240,200,${.05 + .03 * Math.sin(t * 1.1)})`; c.fillRect(0, 0, W, 700); c.restore();
      c.save(); c.fillStyle = 'rgba(239,230,204,.92)'; c.fillRect(652, 632, 306, 96);   // as letras da placa, pintadas por cima para ficarem legíveis
      c.fillStyle = '#8a2a1a'; c.font = '900 66px Georgia, serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('VENDE-SE', 805, 684); c.restore();
      tela(c, 'canvas_ru', '#ece2cc');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Hobbema: a estrada entre as árvores até a sede
  SCENES['ar_hobbema'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 620, [[0, '#6a8ab0'], [1, '#e4e0cc']]); g.fillRect(0, 0, W, 620);
      const r = rng(7);
      for (let i = 0; i < 8; i++) ell(g, 380 + r() * 1200, 120 + r() * 240, 160, 50, 0, 'rgba(245,242,232,.85)');
      g.fillStyle = grad(g, 0, 600, 0, H, [[0, '#8a9a5a'], [1, '#5a6a32']]); g.fillRect(0, 600, W, H - 600);
      g.fillStyle = '#b8905a'; poly(g, [[940, 600], [980, 600], [1260, 1080], [660, 1080]]); g.fill();   // a estrada reta
      g.fillStyle = 'rgba(120,80,40,.4)'; poly(g, [[955, 600], [965, 600], [1000, 1080], [920, 1080]]); g.fill();
      g.fillStyle = '#f0e6d0'; g.fillRect(910, 560, 100, 50); g.fillStyle = '#9a4a2a'; poly(g, [[900, 564], [960, 530], [1020, 564]]); g.fill();   // a sede
      for (let side of [-1, 1]) for (let k = 0; k < 7; k++) {   // as árvores altas e finas, alinhadas
        const p = k / 6, x = 960 + side * lerp(70, 360, p), base = lerp(610, 1080, p), h = lerp(140, 900, p), w = lerp(3, 16, p);
        g.fillStyle = '#4a3a28'; g.fillRect(x - w / 2, base - h, w, h);
        for (let j = 0; j < 4; j++) ell(g, x + (j % 2 ? 1 : -1) * w * 2, base - h + j * h * .07, lerp(14, 70, p), lerp(12, 54, p), 0, ['#4a5a3a', '#5a6a42', '#3a4a2e'][j % 3]);
      }
      return M.broken(a, { cell: 7, len: 14, wid: 8, passes: 3, angle: (x, y) => y < 600 ? 0.1 : -1.2, seed: 811, jit: 11, skip: 0.05, sat: 0.9, warm: [240, 228, 190], cool: [100, 120, 140] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const r = rng(9); c.save();   // folhas caindo devagar entre as árvores
      for (let i = 0; i < 26; i++) { const x = 560 + r() * 800, y = ((r() * 900 + t * (30 + r() * 25)) % 900) + 120; c.fillStyle = 'rgba(90,110,60,.7)'; c.fillRect(x + Math.sin(t * 2 + i) * 8, y, 6, 4); }
      c.restore();
      c.save(); c.globalCompositeOperation = 'screen';   // a luz da manhã descendo pela estrada
      const gr = c.createRadialGradient(960, 600, 10, 960, 600, 520); gr.addColorStop(0, `rgba(255,236,190,${.22 + .06 * Math.sin(t * .9)})`); gr.addColorStop(1, 'rgba(255,236,190,0)');
      c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      tela(c, 'canvas_hb', '#ece2cc');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Kuindzhi: a enxada e o chapéu no fim de tarde
  SCENES['ar_kuindzhi'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 560, [[0, '#2a2440'], [.55, '#c8582a'], [1, '#ffcf6a']]); g.fillRect(0, 0, W, 560);
      ell(g, 1180, 520, 70, 70, 0, '#fff0b0');   // o sol baixo
      g.fillStyle = '#2a1c18'; poly(g, [[0, 560], [600, 540], [1100, 556], [1920, 536], [1920, 580], [0, 580]]); g.fill();
      g.fillStyle = grad(g, 0, 570, 0, H, [[0, '#7a3a1a'], [1, '#2a120a']]); g.fillRect(0, 570, W, H - 570);   // a terra arada, em brasa
      for (let k = 0; k < 22; k++) {   // os sulcos com a crista acesa pelo sol
        const y = 580 + Math.pow(k / 21, 1.7) * 500;
        g.strokeStyle = `rgba(255,170,80,${.25 + .4 * (k / 21)})`; g.lineWidth = 2 + k * .5;
        g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(640, y - 8, 1280, y + 8, W, y - 4); g.stroke();
      }
      g.save(); g.translate(1080, 800); g.rotate(-0.42);   // a enxada fincada na terra
      g.fillStyle = '#5a3a1e'; g.fillRect(-14, -470, 28, 470); g.fillStyle = '#3a3634'; poly(g, [[-80, 0], [80, 0], [66, 56], [-66, 56]]); g.fill(); g.restore();
      ell(g, 840, 760, 130, 32, 0, '#c8a04a'); ell(g, 840, 733, 64, 38, 0, '#d8b45a'); ell(g, 840, 752, 68, 9, 0, '#7a3a20');   // o chapéu de palha
      return M.broken(a, { cell: 8, len: 18, wid: 9, passes: 3, angle: (x, y) => y < 560 ? 0 : 0.05, seed: 907, jit: 10, skip: 0.04, sat: 1.15, warm: [255, 200, 120], cool: [60, 40, 80] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen';   // o brilho do sol pulsando de leve
      const gr = c.createRadialGradient(1180, 520, 20, 1180, 520, 600); gr.addColorStop(0, `rgba(255,220,140,${.35 + .08 * Math.sin(t * 1.4)})`); gr.addColorStop(1, 'rgba(255,220,140,0)');
      c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      const r = rng(3); c.save();   // poeira dourada subindo da terra
      for (let i = 0; i < 40; i++) { const x = 400 + r() * 1100, y = 1000 - ((r() * 500 + t * (20 + r() * 30)) % 500); c.fillStyle = `rgba(255,210,140,${.25 + .25 * r()})`; c.fillRect(x, y, 3, 3); }
      c.restore();
      tela(c, 'canvas_kz', '#e8d4b8');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Hammershøi: a sala vazia, os papéis e a lavoura lá longe
  SCENES['ar_hammershoi'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = '#b8b4a8'; g.fillRect(0, 0, W, H);   // a parede cinza
      g.fillStyle = '#8a8478'; g.fillRect(0, 860, W, H - 860);   // o assoalho
      g.fillStyle = '#ece8dc'; g.fillRect(1020, 180, 380, 520);   // a janela
      g.fillStyle = grad(g, 0, 200, 0, 680, [[0, '#c8d4dc'], [.55, '#dce0d4'], [.56, '#9aa86a'], [1, '#6a7a42']]); g.fillRect(1040, 200, 340, 480);   // a lavoura lá fora
      g.strokeStyle = 'rgba(60,70,40,.5)'; g.lineWidth = 2; for (let k = 0; k < 9; k++) { g.beginPath(); g.moveTo(1040 + k * 42, 466); g.lineTo(1040 + k * 42 - 30, 680); g.stroke(); }
      g.fillStyle = '#ece8dc'; g.fillRect(1205, 200, 12, 480); g.fillRect(1040, 430, 340, 12);   // o caixilho
      g.fillStyle = '#5a4a3a'; g.fillRect(480, 700, 560, 22); g.fillRect(500, 722, 18, 230); g.fillRect(1000, 722, 18, 230);   // a mesa
      g.fillStyle = '#f4f0e4'; g.save(); g.translate(600, 672); g.rotate(-0.06); g.fillRect(0, 0, 260, 30); g.restore();   // a pilha de papéis
      g.fillStyle = '#e8e2d2'; g.save(); g.translate(630, 650); g.rotate(0.05); g.fillRect(0, 0, 230, 26); g.restore();
      g.fillStyle = '#2a2a2a'; g.fillRect(900, 664, 70, 36); g.fillStyle = '#5a5a5a'; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) g.fillRect(906 + i * 21, 668 + j * 10, 16, 6);   // a calculadora
      return M.broken(a, { cell: 7, len: 12, wid: 8, passes: 3, angle: () => 1.57, seed: 1009, jit: 8, skip: 0.05, sat: 0.6, warm: [230, 226, 210], cool: [140, 140, 150] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen';   // o feixe de luz da janela no chão, mudando devagar
      c.fillStyle = `rgba(255,250,230,${.16 + .05 * Math.sin(t * .8)})`;
      poly(c, [[1020, 700], [1400, 700], [1300 + t * 4, 1080], [760 + t * 4, 1080]]); c.fill(); c.restore();
      const r = rng(5); c.save();   // poeira na luz
      for (let i = 0; i < 30; i++) { const x = 900 + r() * 500, y = 300 + ((r() * 700 + t * 12) % 700); c.fillStyle = 'rgba(255,250,230,.35)'; c.fillRect(x, y, 2, 2); }
      c.restore();
      tela(c, 'canvas_hm', '#e4e0d4');
    }
    return { draw };
  })();
  // ---------------------------------------------------------------- Levitan: a caixa de correio na beira da estrada
  SCENES['ar_levitan'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 600, [[0, '#9ab0c4'], [.7, '#e8dcc0'], [1, '#f4e4c4']]); g.fillRect(0, 0, W, 600);
      g.fillStyle = '#8a9aa0'; poly(g, [[0, 600], [500, 570], [1000, 590], [1500, 560], [1920, 590], [1920, 620], [0, 620]]); g.fill();   // mata azulada ao longe
      g.fillStyle = grad(g, 0, 610, 0, H, [[0, '#a8a86a'], [1, '#5a6a32']]); g.fillRect(0, 610, W, H - 610);   // o pasto
      g.fillStyle = '#b8683a'; poly(g, [[1000, 612], [1030, 612], [1500, 1080], [1100, 1080]]); g.fill();   // a estrada de terra
      for (let k = 0; k < 6; k++) {   // as bétulas finas à esquerda
        const x = 520 + k * 70, h = 520 - k * 30;
        g.fillStyle = '#efeae0'; g.fillRect(x, 640 - h, 10, h); g.fillStyle = '#3a3a34'; for (let j = 0; j < 8; j++) g.fillRect(x, 640 - h + j * h / 8 + 10, 10, 4);
        const rr = rng(50 + k); for (let j = 0; j < 14; j++) ell(g, x + 5 + (rr() - .5) * 90, 640 - h + rr() * h * .55, 10 + rr() * 16, 8 + rr() * 12, rr() * 3, ['#c8b860', '#a8a050', '#d8c870', '#b8a84a'][j % 4]);
      }
      g.fillStyle = '#5a4026'; g.fillRect(1240, 600, 22, 300);   // o mourão da caixa de correio
      g.fillStyle = '#7a5434'; g.fillRect(1180, 540, 150, 80); ell(g, 1255, 540, 75, 26, 0, '#7a5434');   // a caixa de correio de madeira
      g.fillStyle = '#4a3020'; g.fillRect(1180, 556, 12, 64);
      return M.broken(a, { cell: 7, len: 15, wid: 8, passes: 3, angle: (x, y) => y < 600 ? 0.05 : -0.9, seed: 1201, jit: 11, skip: 0.05, sat: 0.95, warm: [245, 230, 190], cool: [110, 130, 150] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const up = clamp((t - 1.0) / 0.8, 0, 1);   // a bandeirinha vermelha sobe: chegou correspondência
      c.save(); c.translate(1330, 590); c.rotate(-Math.PI / 2 * up); c.fillStyle = '#5a4026'; c.fillRect(0, -4, 60, 8); c.fillStyle = '#c0281a'; c.fillRect(44, -20, 34, 26); c.restore();
      c.save(); c.globalCompositeOperation = 'screen';   // a névoa da manhã passando
      for (let i = 0; i < 3; i++) { const x = ((t * 40 + i * 700) % 2300) - 200; const gr = c.createRadialGradient(x, 640, 10, x, 640, 420); gr.addColorStop(0, 'rgba(255,248,230,.28)'); gr.addColorStop(1, 'rgba(255,248,230,0)'); c.fillStyle = gr; c.fillRect(0, 380, W, 500); }
      c.restore();
      const r = rng(11); c.strokeStyle = 'rgba(200,200,120,.6)'; c.lineWidth = 3;   // o capim balançando
      for (let i = 0; i < 60; i++) { const x = 420 + r() * 1080, y = 900 + r() * 170, sw = Math.sin(t * 2 + i) * 10; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + sw / 2, y - 30, x + sw, y - 60); c.stroke(); }
      tela(c, 'canvas_lv', '#ece2cc');
    }
    return { draw };
  })();
})();
