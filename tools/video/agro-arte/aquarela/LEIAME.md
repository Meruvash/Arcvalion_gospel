# Mapas e gráficos em aquarela (p5.brush)

- `mapa.html`: Brasil em aquarela e lápis. Os estados "molham" em verde no tempo da fala, com números a lápis
  (fonte Caveat, OFL). Edite a lista `HL` (UF, cor, opacidade, início em segundos, rótulo, deslocamento) e a câmera `CAM`.
- `graficos.html#barras` e `graficos.html#queda`: gráficos de caderno de campo. Edite os dados e os tempos no topo de
  cada modo.
- Render quadro a quadro (Chromium sem GPU, determinístico):
  `node render_frames.cjs mapa.html 9.6 frames 30` e depois
  `ffmpeg -framerate 30 -i frames/f%05d.png -c:v libx264 -crf 16 -pix_fmt yuv420p mapa.mp4`.
  Para conferir antes: `--stills 2.5,8.9`.
- Dados do mapa: `br_uf.js`, estados do Brasil do Natural Earth 1:50m admin-1 (domínio público). d3-array e d3-geo
  (ISC) fazem a projeção.
- O exemplo traz os números do vídeo "Cinco por dia" (Serasa Experian, 2º trimestre de 2026). Troque pelos dados de
  cada vídeo, sempre com fonte.
