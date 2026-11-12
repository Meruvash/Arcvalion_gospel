# p5.brush (build standalone)

- Origem: https://github.com/acamposuribe/p5.brush (MIT; licença em `LICENSE.md`), npm `p5.brush` 3.0.0, arquivo `dist/brush.js`.
- Instalado em 11/11/2026 a pedido do editor, para mapas e dados em aquarela e lápis nos vídeos do agro.
- Não precisa do p5.js: exige WebGL2. Funciona no Chromium sem GPU do ambiente (SwiftShader):
  lance com `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`.
- Testado: determinístico com `brush.seed(n)` + `brush.noiseSeed(n)` no início de cada quadro (mesmo quadro, mesmo PNG);
  ~40–75 ms por quadro a 1080×1080 depois do primeiro (~1 s).
- Atenção: na v3 standalone não existe `brush.ellipse` (use `beginShape/vertex/endShape`); `brush.render()` no fim de cada quadro.
