// Cenas do vídeo "O irmão vira dono da herança?" — pintadas em código, sem imagem gerada por IA. Recorte central x 420..1500.
// Composições novas, à maneira de mestres em domínio público:
//   hd_pissarro    — Camille Pissarro (1830–1903): a família toda reunida de pé no pátio da fazenda, pinceladas curtas e
//                    luz de dia clara; galinhas e um carro de boi
//   hd_bastien     — Jules Bastien-Lepage (1848–1884): um homem velho sentado sozinho na varanda ao entardecer, olhando
//                    o campo; realismo de figura grande, fundo de campo alto
//   hd_caillebotte — Gustave Caillebotte (1848–1894): um homem de joelhos consertando o assoalho/cerca da varanda, tábuas
//                    em perspectiva, luz entrando de lado (melhorias na casa)
(() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
  const grad = (g, x0, y0, x1, y1, stops) => { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; };
  const ell = (g, x, y, rx, ry, rot, cor) => { g.fillStyle = cor; g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, TAU); g.fill(); };
  const tela = (c, id, cor) => { c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.16; c.drawImage(P.texture(id, cor, { scale: 0.006, amt: 14, grain: 8, seed: 97 }), 0, 0); c.restore(); };
  const figura = (g, x, y, s, roupa, pele, chapeu) => {
    g.fillStyle = roupa; poly(g, [[x - 34 * s, y], [x - 26 * s, y - 150 * s], [x + 26 * s, y - 150 * s], [x + 34 * s, y]]); g.fill();
    g.fillStyle = '#3a2e24'; g.fillRect(x - 22 * s, y, 16 * s, 70 * s); g.fillRect(x + 6 * s, y, 16 * s, 70 * s);
    ell(g, x, y - 172 * s, 22 * s, 25 * s, 0, pele);
    if (chapeu) { ell(g, x, y - 188 * s, 48 * s, 11 * s, 0, chapeu); ell(g, x, y - 200 * s, 24 * s, 14 * s, 0, chapeu); }
  };

  // ---------------------------------------------------------------- Pissarro: a família reunida no pátio
  SCENES['hd_pissarro'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 420, [[0, '#9ac0e0'], [1, '#e8eee8']]); g.fillRect(0, 0, W, 420);
      g.fillStyle = '#6a9a5a'; poly(g, [[0, 420], [600, 360], [1200, 400], [1920, 360], [1920, 460], [0, 460]]); g.fill();
      g.fillStyle = '#e8dcc0'; g.fillRect(420, 220, 1080, 260); g.fillStyle = '#b8603a'; poly(g, [[400, 226], [960, 130], [1520, 226]]); g.fill();   // a casa ao fundo
      for (let k = 0; k < 6; k++) { g.fillStyle = '#4a6a8a'; g.fillRect(480 + k * 170, 300, 60, 70); }
      g.fillStyle = grad(g, 0, 470, 0, H, [[0, '#c8b080'], [1, '#9a7a4a']]); g.fillRect(0, 470, W, H - 470);       // o pátio de terra batida
      const fam = [[620, '#3a5a8a', '#d8b860'], [760, '#a83a2a', null], [900, '#5a7a3a', '#d8b860'], [1040, '#e8e0cc', null], [1180, '#7a5a8a', '#d8b860'], [1320, '#c87a2a', null]];
      fam.forEach(([x, cor, ch], k) => figura(g, x, 900 + (k % 2) * 20, 1.1, cor, '#9a6a44', ch));       // os irmãos todos, de pé no pátio
      for (let k = 0; k < 7; k++) ell(g, 480 + k * 140 + (k % 2) * 40, 980 + (k % 3) * 20, 22, 14, 0, k % 2 ? '#f0ece0' : '#b8682a');   // galinhas
      g.fillStyle = '#7a5a3a'; g.fillRect(1380, 760, 120, 60); ell(g, 1400, 840, 30, 30, 0, '#5a3a20'); ell(g, 1480, 840, 30, 30, 0, '#5a3a20');   // carro de boi
      return M.broken(a, { cell: 6, len: 10, wid: 6, passes: 3, angle: (x, y) => Math.sin(x * .02 + y * .03) * 1.2, seed: 311, jit: 10, skip: 0.03, sat: 1.05, warm: [250, 235, 200], cool: [90, 110, 140] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      const r = rng(41); c.fillStyle = 'rgba(255,250,230,.5)'; for (let i = 0; i < 26; i++) { const x = 420 + ((r() * 1080 + t * 22 * (r() + .2)) % 1080), y = 140 + r() * 300 + Math.sin(t + i) * 8; c.fillRect(x, y, 3, 2); }   // folhas no vento
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,248,220,${.08 + .03 * Math.sin(t * 1.5)})`; c.fillRect(0, 0, W, H); c.restore();
      tela(c, 'canvas_pi', '#ece2cc');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Bastien-Lepage: o velho sozinho na varanda
  SCENES['hd_bastien'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 300, [[0, '#c8b8a0'], [1, '#e8d0a0']]); g.fillRect(0, 0, W, 300);                    // céu baixo de fim de tarde
      g.fillStyle = grad(g, 0, 300, 0, 700, [[0, '#8a9a5a'], [1, '#b8a860']]); g.fillRect(0, 300, W, 400);               // campo alto (horizonte alto, como em Bastien-Lepage)
      for (let k = 0; k < 60; k++) { g.strokeStyle = 'rgba(80,90,40,.4)'; g.lineWidth = 3; g.beginPath(); g.moveTo(420 + k * 18, 700); g.lineTo(424 + k * 18, 640 - (k % 5) * 6); g.stroke(); }
      g.fillStyle = '#7a5a3a'; g.fillRect(0, 700, W, H - 700); g.fillStyle = '#5a3e26'; for (let k = 0; k < 8; k++) g.fillRect(0, 720 + k * 46, W, 4);   // assoalho da varanda
      g.fillStyle = '#e8e0cc'; g.fillRect(1340, 0, 40, 760); g.fillRect(500, 0, 40, 760);                                // colunas
      g.fillStyle = '#5a3a1e'; g.fillRect(820, 700, 200, 40); g.fillRect(830, 740, 16, 140); g.fillRect(994, 740, 16, 140); g.fillRect(1000, 520, 16, 220);   // cadeira
      g.fillStyle = '#4a4a5a'; poly(g, [[840, 720], [870, 500], [990, 500], [1010, 720]]); g.fill();                    // o velho, paletó escuro
      g.fillStyle = '#3a3a44'; poly(g, [[860, 720], [1000, 720], [1040, 860], [880, 860]]); g.fill();                   // pernas
      ell(g, 930, 450, 46, 54, 0, '#b88a64'); ell(g, 930, 410, 50, 22, 0, '#e8e4dc');                                     // rosto e cabelo branco
      g.fillStyle = '#5a3a22'; g.fillRect(1030, 560, 10, 320);                                                            // a bengala
      return M.broken(a, { cell: 6, len: 14, wid: 5, passes: 2, angle: (x, y) => 1.57 + Math.sin(x * .01) * .2, seed: 321, jit: 9, skip: 0.03, sat: .9, warm: [250, 220, 170], cool: [80, 80, 90] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; const gr = c.createLinearGradient(1500, 0, 700, 700); gr.addColorStop(0, `rgba(255,200,130,${.28 + .04 * Math.sin(t)})`); gr.addColorStop(1, 'rgba(255,200,130,0)'); c.fillStyle = gr; c.fillRect(0, 0, W, H); c.restore();
      const r = rng(61); c.fillStyle = 'rgba(255,230,170,.55)'; for (let i = 0; i < 24; i++) { const x = 420 + r() * 1080, y = 300 + ((r() * 400 - t * 10 * (r() + .2)) % 400 + 400) % 400; c.fillRect(x, y, 2, 2); }   // mosquitinhos na luz
      tela(c, 'canvas_bl', '#e8dcc4');
    }
    return { draw };
  })();

  // ---------------------------------------------------------------- Caillebotte: o conserto da varanda
  SCENES['hd_caillebotte'] = (() => {
    let plate, built = false;
    function build() {
      const a = P.canvas(), g = a.getContext('2d');
      g.fillStyle = grad(g, 0, 0, W, 0, [[0, '#d8c8a8'], [1, '#f0e4c8']]); g.fillRect(0, 0, W, 420);                     // parede clara
      g.fillStyle = '#fff4d0'; poly(g, [[1180, 60], [1460, 60], [1460, 360], [1180, 360]]); g.fill();                    // a janela com luz
      g.strokeStyle = '#8a6a44'; g.lineWidth = 8; g.strokeRect(1180, 60, 280, 300); g.beginPath(); g.moveTo(1320, 60); g.lineTo(1320, 360); g.stroke();
      for (let k = 0; k < 22; k++) { const x0 = 420 + k * 52; g.fillStyle = k % 2 ? '#a07040' : '#b8844c'; poly(g, [[960 + (x0 - 960) * .35, 420], [960 + (x0 + 52 - 960) * .35, 420], [960 + (x0 + 52 - 960) * 1.6, H], [960 + (x0 - 960) * 1.6, H]]); g.fill(); }   // tábuas novas em perspectiva
      g.fillStyle = '#6a4a2a'; for (let k = 0; k < 6; k++) poly(g, [[960 + (420 + k * 190 - 960) * .35, 420], [960 + (440 + k * 190 - 960) * .35, 420], [960 + (440 + k * 190 - 960) * 1.6, H], [960 + (420 + k * 190 - 960) * 1.6, H]]);   // tábuas velhas ainda escuras
      g.fill();
      g.fillStyle = '#f0ece0'; poly(g, [[760, 760], [800, 560], [920, 540], [960, 700], [900, 780]]); g.fill();           // o homem de joelhos, camisa branca
      ell(g, 860, 520, 34, 38, 0, '#a87a54'); g.fillStyle = '#3a3a4a'; poly(g, [[760, 760], [960, 700], [1000, 820], [740, 860]]); g.fill();
      g.strokeStyle = '#5a3a20'; g.lineWidth = 9; g.beginPath(); g.moveTo(960, 640); g.lineTo(1060, 720); g.stroke(); ell(g, 1066, 724, 20, 12, .6, '#7a7a7a');   // o martelo
      for (let k = 0; k < 8; k++) ell(g, 620 + k * 30, 900 + (k % 2) * 8, 6, 3, 0, '#d8c8a0');                           // aparas
      g.fillStyle = '#c8a070'; g.fillRect(1120, 820, 260, 40); g.fillRect(1140, 870, 260, 40);                          // tábuas novas empilhadas
      return M.broken(a, { cell: 6, len: 14, wid: 5, passes: 2, angle: (x, y) => y > 420 ? Math.atan2(H - 420, (x - 960) * 1.25) : 0.1, seed: 331, jit: 9, skip: 0.03, sat: .95, warm: [255, 235, 190], cool: [90, 80, 70] });
    }
    function draw(c, lt) {
      if (!built) { plate = build(); built = true; }
      const t = Math.max(0, lt); c.drawImage(plate, 0, 0);
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = `rgba(255,236,190,${.16 + .05 * Math.sin(t * 1.1)})`; poly(c, [[1180, 60], [1460, 60], [1300, 1080], [700, 1080]]); c.fill(); c.restore();   // feixe de luz da janela
      const bat = Math.abs(Math.sin(t * 5)), r = rng(71); c.fillStyle = `rgba(255,240,210,${.5 * bat})`; for (let i = 0; i < 12; i++) c.fillRect(1050 + r() * 50, 690 + r() * 40, 3, 3);   // pó a cada martelada
      tela(c, 'canvas_cb', '#ece0c8');
    }
    return { draw };
  })();
})();
