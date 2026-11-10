# Pipeline dos vídeos do agro: pinturas em código + HyperFrames

Ferramentas do vídeo da MP 1.376 (10/11/2026), que é o padrão dos vídeos do agro. A direção está
em `docs/video/DIRECAO_VIDEO_AGRO.md`.

## Dependências (fora do repositório)
- **Motor de pinturas:** skill `huashu-art-motion` (MIT, github.com/alchaincyf/huashu-art-motion,
  commit `1468196505a51728686db118d52561aa27a25124`). Para usar, clone numa pasta de trabalho fora do
  repositório: `git clone https://github.com/alchaincyf/huashu-art-motion /tmp/huashu && git -C /tmp/huashu checkout 1468196`.
  - Copie `cenas/cenas_agro.js` e `cenas/eras_agro.js` para `scripts/engine/` da skill.
  - Gere o render com o Chromium do ambiente (sem instalar outro):
    `sed "s#p.chromium.launch(args=#p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args=#" render.py > render_local.py`
- **Montagem:** `hyperframes` 0.9.30 e `gsap` 3.14.2 (npm, numa pasta de trabalho), com
  `DO_NOT_TRACK=1` e `PRODUCER_HEADLESS_SHELL_PATH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
- **Vozes:** ElevenLabs (credencial do ambiente). Fontes: Inter, Newsreader e IBM Plex (OFL,
  via @fontsource).

## Passos (pasta de trabalho de cada vídeo, fora do git: `voz/`, `prints/`, `hf/`)
1. `falas.json` com as falas aprovadas (ver `falas_exemplo_mp1376.json`).
   Rode `python3 gerar_vozes.py 1,2,3`.
   - Pós-processamento: `silenceremove` (pausas acima de 0,3 s) e `atempo=1.08` no narrador; nunca
     na voz clonada.
   - Transcreva cada fala com o speech-to-text da ElevenLabs (`scribe_v1`, palavras com tempo) e
     compare com o roteiro.
2. Prints oficiais com posição dos trechos: `node prints/capturar.cjs` (página do BCB) e
   `node prints/print_cn2.cjs` (andamento da MP no Congresso). Ajuste URL e trechos.
3. Pinturas, na pasta da skill:
   `uv run -q --with playwright python render_local.py --film agro --solo mp_fazenda --from 0 --to 10 --fps 30 --crf 16 --no-counter --out fazenda-wide.mp4`
   - Recorte quadrado com `ffmpeg -vf crop=1080:1080:420:0`.
   - O aviso de página com "404" é um arquivo de vitrine ausente e pode ser ignorado.
4. `python3 preparar.py`: narração montada, tempos por palavra e recortes dos prints.
5. Gerador da composição: use `montar_exemplo_mp1376.py` como modelo. Ele gera `hf/index.html` com
   as cenas, as legendas e os efeitos.
   - **No próximo vídeo:** troque as cenas de documento em tela cheia por cartões pequenos sobre a
     pintura (ver a direção).
6. `npx hyperframes check --json`, depois `snapshot` para olhar os quadros, depois
   `render --quality high`.
7. Entrega: `loudnorm=I=-14.5:TP=-1.5`, H.264 CRF 18, `+faststart`.

As mídias (vozes, renders, prints) não entram no git. Elas são regeneráveis a partir destes scripts.
