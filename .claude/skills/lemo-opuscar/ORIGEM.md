# Origem

Skill copiada de github.com/lemomo-ai/lemo-opuscar (licença MIT, LemoLab), pasta `plugin/skills/lemo-opuscar/`,
commit 9eb7739a0fca4c6990fe966cb8b87b1930f7193a (10/11/2026). Instalação autorizada pelo editor em 11/11/2026.

- A biblioteca (guias, `core/`, `STYLE.md` de cada estilo) fica fora do repositório, em `~/lemo-opuscar`
  (o `scripts/setup.sh` baixa na primeira vez). Nada dela é copiado para `conteudo/`.
- Filmes de demonstração e quadros da galeria são CC BY 4.0: se algum for reaproveitado, crédito "LemoLab" com link.
- Seis faixas de voz das demos (Chalkboard, Circuit Board, Desktop Flythrough, Isometric Picture Book, Printed Long
  Take, Broadcast News Package) NÃO têm licença livre: não reutilizar.
- Neste container: o renderizador usa o Chromium já instalado (`PLAYWRIGHT_CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`).
  O ffmpeg do sistema é 6.1; a biblioteca pede 7+ só para o `mux.sh` (a mixagem dos vídeos do agro continua
  pelo nosso fluxo, com `loudnorm`).
- Nos vídeos do agro, o Lemo-Opuscar entra como **critério de direção e técnica de estilo**; as regras de
  `docs/video/DIRECAO_VIDEO_AGRO.md` (fonte oficial, nada de imagem de IA, sem rosto de frente etc.) continuam valendo.
