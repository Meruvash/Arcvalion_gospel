# Cenas em pintura a óleo com espátula (Lemo-Opuscar)

Motor `impasto` do Lemo-Opuscar (github.com/lemomo-ai/lemo-opuscar, MIT, LemoLab), usado desde o vídeo
"O relógio zerou" (12/11/2026) **só nas cenas em que ele é visualmente superior** ao modelo antigo (decisão do editor):
objetos pintados com relevo de tinta e luz rasante (relógio, folhinha) e mapa com a cor "reposta pela espátula".
As outras cenas continuam no modelo antigo (huashu-art-motion, `../cenas/`).

- `plv16_film.js` + `plv16_index.html` (copie com estes nomes; a página importa `./plv16_film.js`): cenas `relogio`, `folhinha`, `mapa` e `fim` (escolhidas por `?cena=`).
  Copie para uma pasta de projeto com `engine/` (de `~/lemo-opuscar/styles/impasto/demo/engine/`), `lib/`
  (d3 + `br_uf.js` de `../aquarela/`) e `fonts/` (Newsreader 600 itálico).
- `render_plv16.sh`: render de cada clipe em 1080×1080 a 30 fps com o renderizador da biblioteca. Usa o Chromium do
  container via `PLAYWRIGHT_CHROME`.
- Neste container, o WebGL roda em software (SwiftShader). Cada clipe de ~6 s leva vários minutos.
- Regras do motor (STYLE.md do estilo): sem grão de filme, semente fixa por pincelada, texto grande a espátula e texto
  pequeno em DOM por cima.
