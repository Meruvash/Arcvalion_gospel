---
name: video-agro
description: Produz vídeo curto de agronegócio (Reels quadrado, ~1 min) no padrão aprovado pelo editor — roteiro "Você sabia" com fatos lidos na fonte oficial, pinturas animadas em código à maneira de mestres em domínio público (Van Gogh, Sisley, Monet, Pissarro), pouco documento na tela, legenda amarela, narração ElevenLabs e conclusão do Dr. Pelicioni. Use quando pedirem "vídeo do agro", "vídeo de agronegócio", "vídeo sobre crédito rural / dívida rural / MP / resolução do CMN".
---

# Vídeo do agro

**Leia antes de qualquer coisa:**
1. `docs/video/DIRECAO_VIDEO_AGRO.md`: imagem, voz e proporção. É o padrão atual, com **mais
   animação e menos documento**.
2. `docs/video/PROMPT_VIDEO_AGRO.md`: estrutura do roteiro ("Você sabia", 10 batidas) e regras do
   portal.
3. Exemplo aprovado: `docs/video/roteiros/mp1376-prazo-quinta.md`.

## Fluxo
1. **Tema novo e verificável.** Procure o assunto da semana no crédito rural (CMN/BCB, MP, lei,
   STJ, Congresso). Leia a norma na fonte primária e anote link e data.
2. **Roteiro na conversa**, no formato de tabela do PROMPT. **Pare e espere a aprovação.**
3. **Plano de imagem** junto com o roteiro: para cada fala, que pintura entra, onde entram os 2 ou 3
   cartões de prova e qual tipografia animada usar. Respeite os 70% de animação.
4. Aprovado o roteiro: vozes (`tools/video/agro-arte/gerar_vozes.py`), conferência por transcrição,
   pinturas (`tools/video/agro-arte/cenas/`), prints oficiais (`tools/video/agro-arte/prints/`),
   montagem em HyperFrames e render. Os passos estão em `tools/video/agro-arte/README.md`.
5. **Trilha:** `tools/video/agro-arte/trilha/gerar_trilha.py --estilo agronejo` (padrão) ou `--estilo catira`, alternando entre
   vídeos seguidos. Confira que é instrumental (0 palavras na transcrição). Regras em `docs/video/TRILHA_AGRO.md`.
6. **Prévia curta → aprovação → vídeo completo.** Entregue com a lista da seção 4 do
   `DIRECAO_VIDEO_AGRO.md`.

## Não fazer
- Repetir imagem de vídeo anterior (pintura, mapa, gráfico ou foto). Confira e atualize `docs/video/CENAS_USADAS.md`.
- Citar na narração birô de crédito ou cobrança (Serasa, SPC, Boa Vista) num vídeo para devedores: a fonte vai só no rodapé.
- Repetir frase-fórmula de vídeo anterior ("Parece erro. Mas não é.", "E é justamente aí que a história fica ainda mais estranha…" ou qualquer outra). Cada roteiro com palavras próprias.
- Usar segunda voz sem necessidade real (o padrão é não ter).
- Repetir o ângulo de um vídeo anterior.
- Usar documento em tela cheia por muito tempo.
- Mostrar TV ou onda de áudio quando houver segunda voz.
- Pintar rosto de frente.
- Usar imagem de IA, foto sem licença, estilo de artista vivo ou estúdio, Portinari ou Tarsila.
- Fazer render antes de o roteiro ser aprovado.
