// Cenas do vídeo "O vizinho fechou a estrada?" (servidão de passagem). Padrão de docs/video/DIRECAO_ARTISTICA.md (25/11/2026):
// quadro completo, ponto focal nos terços do recorte 1080 (x 420..1500), 4 planos, luz de fim de tarde, paleta harmônica.
//   sv_parreiras — à maneira de Antônio Parreiras (1860–1937), paisagista brasileiro (estrutura de "Paisagem", c. 1900:
//                  estrada que entra pela esquerda em curva, árvore-moldura no lado oposto, serra azul e céu largo).
//                  Foco: a porteira de madeira trancada com corrente e cadeado, sobre a estrada de terra vermelha.
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

  SCENES['sv_parreiras'] = (() => {
    let ceu, terra, frente, built = false;
    const SOL = [610, 300];
    const curva = t => {                              // a estrada em S: da base do quadro até a porteira e além, rumo ao horizonte
      const p0 = [640, 1120], p1 = [1180, 900], p2 = [620, 760], p3 = [905, 668];
      const u = 1 - t; return [u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0], u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]];
    };
    const larg = t => lerp(250, 46, Math.pow(t, .8));
    function build() {
      // ---------- céu ----------
      ceu = P.canvas(); let g = ceu.getContext('2d');
      g.fillStyle = grad(g, 0, 0, 0, 640, [[0, '#5f7fa8'], [.45, '#a9b9c8'], [.78, '#f1d9a8'], [1, '#f6c98a']]); g.fillRect(0, 0, W, 640);
      const halo = g.createRadialGradient(SOL[0], SOL[1], 10, SOL[0], SOL[1], 520); halo.addColorStop(0, 'rgba(255,244,214,.95)'); halo.addColorStop(.15, 'rgba(255,226,170,.55)'); halo.addColorStop(1, 'rgba(255,210,150,0)');
      g.fillStyle = halo; g.fillRect(0, 0, W, 700);
      [[200, 150, 1.0, 1], [760, 110, 1.25, 2], [1300, 170, 1.0, 3], [1780, 120, 1.1, 4], [1080, 330, .62, 5], [470, 380, .5, 6]].forEach(([x, y, s, k]) => nuvem(g, x, y, s, 400 + k));
      ceu = M.broken(ceu, { cell: 7, len: 18, wid: 9, passes: 3, angle: (x, y) => .08 + P.noise(x * .004, y * .004) * .5, seed: 2001, jit: 9, skip: 0.02, sat: 1.02, warm: [255, 228, 180], cool: [100, 120, 170] });
      // ---------- terra (tudo o que não se move) ----------
      terra = P.canvas(); g = terra.getContext('2d');
      serra(g, 560, 120, .0016, 3, '#9aa7bd');                    // serra mais distante, quase céu
      serra(g, 598, 90, .0024, 11, '#7d8fa6');
      serra(g, 630, 60, .0034, 19, '#6d7f78');                    // morro próximo, já esverdeado
      // pasto em faixas com variação (fbm) e luz rasante
      const im = g.getImageData(0, 0, W, H), d = im.data;
      for (let y = 600; y < H; y++) for (let x = 0; x < W; x++) {
        const hz = 640 - 40 * P.fbm(x * .0034 + 19, 19 * .37, 5); if (y < hz) continue;
        const i = (y * W + x) * 4, k = (y - hz) / (H - hz), n = P.fbm(x * .004, y * .012, 4), n2 = P.fbm(x * .03, y * .06, 2);
        let c = mix([150, 160, 92], [70, 96, 44], Math.pow(k, .7));            // longe claro e amarelado, perto escuro
        c = mix(c, [196, 170, 90], clamp(.35 + n * .9, 0, 1) * (1 - k) * .7);   // manchas de capim seco ao sol
        c = mix(c, [40, 62, 34], clamp(n2 * .6 + .1, 0, 1) * k * .6);
        const sol = clamp(1 - Math.hypot(x - SOL[0], (y - 640) * 2.4) / 1400, 0, 1);
        c = mix(c, [255, 214, 140], sol * .28);
        d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 255;
      }
      g.putImageData(im, 0, 0);
      // mata de galeria no fundo, com luz de borda
      const r = rng(5);
      for (let i = 0; i < 90; i++) { const x = r() * W, y = 628 + r() * 22 - 30 * P.fbm(x * .0034 + 19, 6.97, 5), s = 10 + r() * 22;
        ell(g, x, y, s * 1.3, s, 0, rgba(mix([52, 74, 60], [88, 104, 80], r()), .95)); ell(g, x - s * .4, y - s * .4, s * .6, s * .4, 0, 'rgba(250,214,150,.25)'); }
      // cupinzeiros no pasto
      for (const [x, y, s] of [[1210, 700, 1], [700, 735, 1.3], [1380, 760, 1.6]]) { g.fillStyle = '#a65a34'; poly(g, [[x - 14 * s, y], [x - 6 * s, y - 26 * s], [x + 4 * s, y - 30 * s], [x + 13 * s, y]]); g.fill(); g.fillStyle = 'rgba(255,220,170,.35)'; poly(g, [[x - 6 * s, y - 26 * s], [x + 4 * s, y - 30 * s], [x - 2 * s, y]]); g.fill(); ell(g, x + 18 * s, y + 2, 20 * s, 4 * s, 0, 'rgba(40,40,30,.3)'); }
      // a estrada: miolo vermelho, bordas mais escuras, trilhas de pneu e capim no meio
      for (let t = 0; t <= 1.0001; t += .0025) { const [x, y] = curva(t), w = larg(t);
        g.fillStyle = rgba(mix([182, 82, 46], [214, 126, 76], t * .8 + .1 * P.noise(t * 40, 1)), 1); g.fillRect(x - w / 2, y - 3, w, 6); }
      for (const off of [-.22, .22]) { g.strokeStyle = 'rgba(120,46,24,.55)'; g.lineWidth = 3; g.beginPath();
        for (let t = 0; t <= 1; t += .01) { const [x, y] = curva(t), w = larg(t); t ? g.lineTo(x + off * w, y) : g.moveTo(x + off * w, y); } g.stroke(); }
      const rg = rng(9); for (let t = .02; t < .95; t += .012) { const [x, y] = curva(t), w = larg(t); tufo(g, x + (rg() - .5) * w * .1, y, 6 + 16 * (1 - t), 'rgba(120,130,60,.8)', rg, 4); }
      for (const side of [-1, 1]) for (let t = .0; t < .97; t += .01) { const [x, y] = curva(t), w = larg(t); tufo(g, x + side * w * .52, y, 10 + 34 * (1 - t), rgba(mix([92, 110, 50], [170, 150, 80], rg()), .9), rg, 5); }
      // cerca de arame que corre pelo pasto e encontra a porteira
      const cx = (t) => lerp(430, 1500, t);
      for (let k = 0; k <= 16; k++) { const x = cx(k / 16), y = 672 + (x - 905) * .03; if (Math.abs(x - 905) < 70) continue;
        g.fillStyle = '#4a3624'; g.fillRect(x - 5, y - 64, 10, 68); g.fillStyle = 'rgba(255,214,150,.55)'; g.fillRect(x - 5, y - 64, 3, 68); }
      g.strokeStyle = 'rgba(70,60,50,.7)'; g.lineWidth = 1.2; for (const h of [18, 36, 54]) { g.beginPath(); g.moveTo(430, 672 + (430 - 905) * .03 - h); g.lineTo(1500, 672 + (1500 - 905) * .03 - h); g.stroke(); }
      // ---------- o foco: a porteira trancada ----------
      const PX = 905, PY = 676, S = 1.8;
      const R_ = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(PX + x * S, PY + y * S, w * S, h * S); };
      R_(-72, -96, 15, 102, '#3a2716'); R_(58, -96, 15, 102, '#3a2716');                                   // mourões
      R_(-72, -96, 4, 102, 'rgba(255,214,150,.6)'); R_(58, -96, 4, 102, 'rgba(255,214,150,.6)');
      for (let k = 0; k < 5; k++) { const y = -82 + k * 15; R_(-57, y, 115, 8, k % 2 ? '#866444' : '#9b7650'); R_(-57, y, 115, 2, 'rgba(255,232,186,.5)'); R_(-57, y + 6, 115, 2, 'rgba(40,24,12,.35)'); }
      g.strokeStyle = '#6a4c2e'; g.lineWidth = 6 * S; g.beginPath(); g.moveTo(PX - 54 * S, PY - 18 * S); g.lineTo(PX + 56 * S, PY - 80 * S); g.stroke();
      g.strokeStyle = 'rgba(255,226,176,.45)'; g.lineWidth = 2 * S; g.beginPath(); g.moveTo(PX - 54 * S, PY - 21 * S); g.lineTo(PX + 56 * S, PY - 83 * S); g.stroke();
      for (let k = 0; k < 7; k++) { g.strokeStyle = k % 2 ? '#9a968c' : '#cfcac0'; g.lineWidth = 2.4; g.beginPath(); g.ellipse(PX + (50 + k * 3.2) * S, PY + (-56 + k * 3) * S, 4, 2.6, k % 2 ? .9 : -.4, 0, TAU); g.stroke(); }   // corrente
      R_(68, -36, 13, 13, '#c89a30'); R_(68, -36, 13, 3, '#f0cc60'); g.strokeStyle = '#7a6018'; g.lineWidth = 3; g.beginPath(); g.arc(PX + 74.5 * S, PY - 37 * S, 4.5 * S, Math.PI, 0); g.stroke();   // cadeado
      ell(g, PX + 70 * S, PY + 8, 140 * S, 10 * S, 0, 'rgba(60,28,16,.38)');                                     // sombra longa
      // a estrada continua depois da porteira até sumir no morro
      g.strokeStyle = 'rgba(214,140,92,.9)'; g.lineWidth = 10; g.beginPath(); g.moveTo(PX + 4, PY - 4); g.bezierCurveTo(PX + 60, PY - 30, PX + 150, PY - 36, PX + 230, PY - 52); g.stroke();
      // ---------- moldura escura do primeiro plano (esquerda) ----------
      const rf = rng(13); g.fillStyle = grad(g, 0, 900, 0, H, [[0, 'rgba(36,46,24,0)'], [1, 'rgba(30,38,20,.85)']]); g.fillRect(0, 900, W, 180);
      for (let i = 0; i < 70; i++) tufo(g, X0 - 20 + rf() * 260, 1080 - rf() * 60, 70 + rf() * 90, rgba(mix([40, 56, 28], [96, 104, 46], rf()), .95), rf, 8);
      terra = M.broken(terra, { cell: 6, len: 13, wid: 7, passes: 3, angle: (x, y) => (y < 640 ? 0 : -0.25 + P.noise(x * .01, y * .01) * .6), seed: 2101, jit: 10, skip: 0.03, sat: 1.04, warm: [255, 220, 160], cool: [80, 96, 130] });
      // ---------- o ipê-amarelo, moldura da direita (fica por cima, desenhado à parte para florir e balançar) ----------
      frente = P.canvas(); g = frente.getContext('2d');
      g.strokeStyle = '#3a2a1e'; g.lineCap = 'round';
      const pontas = [];
      const galho = (x, y, a, l, w, n) => { if (n <= 3) pontas.push([x, y]); if (n === 0 || l < 8) return; const x2 = x + Math.cos(a) * l, y2 = y + Math.sin(a) * l;
        g.lineWidth = w; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo((x + x2) / 2 + (rf() - .5) * l * .2, (y + y2) / 2, x2, y2); g.stroke();
        galho(x2, y2, a - .38 + (rf() - .5) * .25, l * .7, w * .66, n - 1); galho(x2, y2, a + .38 + (rf() - .5) * .25, l * .7, w * .66, n - 1); };
      galho(1480, 1080, -Math.PI / 2 - .03, 280, 36, 7);
      const ip = rng(31);
      for (const camada of [0, 1, 2]) for (const [tx, ty] of pontas) {            // 3 passadas: sombra ocre, amarelo, luz limão do lado do sol
        if (ty > 640) continue; const rr = 30 + ip() * 26;
        for (let i = 0; i < 40; i++) { const a = ip() * TAU, d = Math.sqrt(ip()) * rr, x = tx + Math.cos(a) * d, y = ty + Math.sin(a) * d * .8;
          const lado = (Math.cos(a) * -.7 + Math.sin(a) * -.7);                    // >0 = lado de cima-esquerda (sol)
          if (camada === 0 && lado > .2) continue; if (camada === 2 && lado < .35) continue;
          const cor = camada === 0 ? [176, 112, 18] : camada === 1 ? [238, 182, 36] : [255, 236, 120];
          g.fillStyle = rgba(cor, .92); g.beginPath(); g.ellipse(x, y, 4 + ip() * 5, 3 + ip() * 4, ip() * 3, 0, TAU); g.fill(); }
      }
      for (let i = 0; i < 120; i++) { const x = 1150 + ip() * 360, y = 960 + ip() * 110; ell(g, x, y, 3, 2, ip() * 3, `rgba(240,${190 + (i % 3) * 15},60,${.5 + ip() * .4})`); }   // flores caídas no chão
      frente = M.broken(frente, { cell: 5, len: 9, wid: 6, passes: 2, angle: () => -0.4, seed: 2203, jit: 8, skip: 0.02, sat: 1.08, warm: [255, 230, 150], cool: [110, 90, 60], base: false });
    }
    // Nuvens desenhadas uma vez num sprite largo e deslizadas devagar.
    let nuvens; const buildNuvens = () => { nuvens = P.canvas(2600, 640); const g = nuvens.getContext('2d');
      [[300, 170, 1.1, 1], [900, 120, 1.4, 2], [1500, 200, 1.0, 3], [2100, 140, 1.3, 4], [1250, 330, .7, 5], [520, 360, .6, 6]].forEach(([x, y, s, k]) => nuvem(g, x, y, s, 400 + k)); };
    function draw(c, lt) {
      if (!built) { build(); built = true; }
      const t = Math.max(0, lt);
      c.save(); c.translate(-t * 3, 0); c.scale(1.04, 1.04); c.drawImage(ceu, 0, 0); c.restore();
      c.drawImage(terra, 0, 0);
      // raios de sol rasantes
      c.save(); c.globalCompositeOperation = 'screen';
      for (let k = 0; k < 5; k++) { const a = .25 + k * .09 + Math.sin(t * .3 + k) * .01; c.fillStyle = `rgba(255,226,170,${.05 + .02 * Math.sin(t * .8 + k)})`;
        poly(c, [[SOL[0], SOL[1]], [SOL[0] + Math.cos(a) * 1600, SOL[1] + Math.sin(a) * 1600], [SOL[0] + Math.cos(a + .035) * 1600, SOL[1] + Math.sin(a + .035) * 1600]]); c.fill(); }
      c.restore();
      // ipê balançando de leve (rotação mínima a partir da base)
      c.save(); c.translate(1480, 1080); c.rotate(Math.sin(t * .9) * .006); c.translate(-1480, -1080); c.drawImage(frente, 0, 0); c.restore();
      // flores de ipê caindo e girando
      const r = rng(77); c.save();
      for (let i = 0; i < 46; i++) { const sp = 30 + r() * 40, x0 = 1150 + r() * 380, ph = r() * 20, y = 300 + ((t * sp + ph * 40) % 800), x = x0 - (y - 300) * .35 + Math.sin(t * 1.6 + i) * 14;
        c.save(); c.translate(x, y); c.rotate(t * 2 + i); c.fillStyle = `rgba(255,${200 + (i % 3) * 15},60,.9)`; c.beginPath(); c.ellipse(0, 0, 5, 3, 0, 0, TAU); c.fill(); c.restore(); }
      c.restore();
      // capim do primeiro plano ondulando ao vento
      const rv = rng(19); c.save(); c.lineCap = 'round';
      for (let i = 0; i < 120; i++) { const x = X0 - 10 + rv() * 1100, y = 1085, l = 40 + rv() * 70, sw = Math.sin(t * 1.4 + x * .01) * 10;
        c.strokeStyle = rgba(mix([60, 76, 34], [180, 160, 80], rv()), .85); c.lineWidth = 2 + rv() * 2; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + sw * .4, y - l * .6, x + sw, y - l); c.stroke(); }
      c.restore();
      // poeira dourada no ar contra o sol
      const rp = rng(41); c.save(); for (let i = 0; i < 60; i++) { const x = 520 + rp() * 700 + Math.sin(t * .5 + i) * 20, y = 420 + ((rp() * 400 - t * (5 + rp() * 8)) % 400 + 400) % 400;
        c.fillStyle = `rgba(255,236,190,${.25 + .35 * rp()})`; c.fillRect(x, y, 2.5, 2.5); } c.restore();
      // pássaros ao longe
      c.save(); c.strokeStyle = 'rgba(60,50,50,.7)'; c.lineWidth = 2; for (let i = 0; i < 4; i++) { const x = 760 + ((t * 26 + i * 60) % 700), y = 240 + i * 14 + Math.sin(t * 2 + i) * 4, w = Math.sin(t * 8 + i) * 4;
        c.beginPath(); c.moveTo(x - 9, y - w); c.quadraticCurveTo(x - 4, y - 5, x, y); c.quadraticCurveTo(x + 4, y - 5, x + 9, y - w); c.stroke(); } c.restore();
      // vinheta suave para segurar o olho no centro
      const vg = c.createRadialGradient(960, 600, 300, 960, 600, 900); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(30,20,10,.35)'); c.fillStyle = vg; c.fillRect(0, 0, W, H);
      tela(c, 'canvas_sv', '#efe2c8');
    }
    return { draw };
  })();
})();
