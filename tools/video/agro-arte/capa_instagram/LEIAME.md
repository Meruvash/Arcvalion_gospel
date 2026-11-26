# Capa do Instagram (9:16 e 4:5)

Pedido do editor (17/11/2026): a capa tirada do quadro 0 do vídeo quadrado fica mal formatada no Instagram. Por isso,
todo vídeo do agro passa a ser entregue também com duas capas próprias:

- **9:16 (1080×1920):** capa do Reels. O texto fica dentro da faixa central de 4:5, para não ser cortado na grade.
- **4:5 (1080×1350):** grade do perfil.

Como gerar (o exemplo é o vídeo do gado do vizinho):

1. Tire o fundo do clipe de abertura **sem textos**, ampliado e recortado:
   - 9:16: `ffmpeg -ss 0.3 -i roca.mp4 -frames:v 1 -vf "scale=1920:1920,crop=1080:1920:X:0" bg_v.jpg`, com X escolhido
     para os personagens aparecerem;
   - 4:5: `-vf "scale=1350:1350,crop=1080:1350:135:0" bg_f.jpg`.
2. Copie os HTML de exemplo para a pasta do fundo, junto com a fonte `inter-latin-900-normal.woff2`. Troque a etiqueta,
   o título e a linha de baixo pelos da capa do vídeo.
3. Tire o print com o Playwright (viewport 1080×1920 e 1080×1350) e exporte em JPG.


## Modelo atual (25/11/2026): `modelo/`
`v.html` (9:16) e `f.html` (4:5) com fundo desfocado (`bgb_v.jpg`, `bgb_f.jpg`), quadro (`quad.png`), chip, título, subtítulo e carimbo; `node shot.cjs` gera `capa-9x16.png` e `capa-4x5.png`. Preparar as imagens:
```
ffmpeg -ss 4 -i cena.mp4 -frames:v 1 quad.png
ffmpeg -i quad.png -vf "scale=1920:1920,crop=1080:1920,boxblur=24" bgb_v.jpg
ffmpeg -i quad.png -vf "scale=1350:1350,crop=1080:1350,boxblur=24" bgb_f.jpg
```
Copie a fonte `inter-latin-900-normal.woff2` para a mesma pasta. Troque chip, título, subtítulo e carimbo; o carimbo fica no céu (`top: calc(… + 40 a 150px)`), nunca sobre o foco.
