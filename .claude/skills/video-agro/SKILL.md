---
name: video-agro
description: Produz vídeo curto de agronegócio (Reels quadrado, ~1 min) no padrão aprovado pelo editor — roteiro "Você sabia" com fatos lidos na fonte oficial, pinturas animadas em código à maneira de mestres em domínio público (Van Gogh, Sisley, Monet, Pissarro), pouco documento na tela, legenda amarela, narração ElevenLabs e conclusão do Dr. Pelicioni. Use quando pedirem "vídeo do agro", "vídeo de agronegócio", "vídeo sobre crédito rural / dívida rural / MP / resolução do CMN".
---

# Vídeo do agro

**Leia antes de qualquer coisa:**
0. `docs/video/PADRAO_CASEIRO.md`: o padrão que fez "O caseiro vira dono" passar de 2.200 visualizações. Vale
   acima dos outros arquivos: fala 1 com personagem + "sua" terra/família + mito desfeito e ameaça na mesma frase;
   palavra-chave na fala 2; pergunta final sobre a vida de quem assiste; 50 a 62 s; Crivo do Caseiro de 12/16 ou mais.
1. `docs/video/DIRECAO_VIDEO_AGRO.md`: imagem, voz e proporção. É o padrão atual, com **mais
   animação e menos documento**.
2. `docs/video/PROMPT_VIDEO_AGRO.md`: estrutura do roteiro ("Você sabia", 10 batidas) e regras do
   portal.
3. Exemplo de referência: `docs/video/roteiros/usucapiao-caseiro-vizinho.md` (o que mais rodou).

## Fluxo
1. **Pauta pela política de originalidade** (`docs/video/PAUTA_AGRO.md`, obrigatória):
   - pelo menos 5 candidatas, de 3 eixos ou mais;
   - rodízio de eixos, com dívida e crédito em no máximo 1 de cada 4 vídeos;
   - conferência em `docs/video/PAUTAS_USADAS.md`;
   - Crivo do Caseiro (`PADRAO_CASEIRO.md`, seção 4) em cada uma, com a busca no autocomplete;
   - as 3 melhores apresentadas com nota.

   Leia a norma ou o dado na fonte primária e anote link e data.
2. **Auditoria de padrão ouro antes de mostrar o roteiro** (`docs/video/AUDITORIA_PADRAO_OURO.md`):
   - parte automática: `python3 tools/video/agro-arte/auditar_roteiro.py falas.json --md auditoria.md`, que precisa de 21/23 ou mais;
   - parte de julgamento: os itens M1 a M8;
   - as duas tabelas vão no roteiro e um resumo na mensagem ao editor;
   - depois do render: `python3 tools/video/agro-arte/auditar_video.py video.mp4 --tempos hf/assets/data/tempos.json` (Parte 3: abertura e ritmo, todos os itens de V1 a V5 e S1).
2.1. **Roteiro na conversa**, no formato de tabela do PROMPT. **Pare e espere a aprovação.**
3. **Plano de imagem** junto com o roteiro: para cada fala, que pintura entra, onde entram os 2 ou 3
   cartões de prova e qual tipografia animada usar. Respeite os 70% de animação.
4. Aprovado o roteiro: vozes (`tools/video/agro-arte/gerar_vozes.py`), conferência por transcrição.
   **Voz do editor (clone): sempre pelo `tools/video/agro-arte/voz_editor_s_neutro.py`.** Ele gera candidatas sem
   "style" e com mais estabilidade, mede o "S" de cada uma e fica com a mais neutra, sem o chiado carioca (pedido do
   editor, 17/11/2026).
   Depois:
   pinturas (`tools/video/agro-arte/cenas/`), prints oficiais (`tools/video/agro-arte/prints/`),
   montagem em HyperFrames e render. Os passos estão em `tools/video/agro-arte/README.md`.
5. **Trilha:** `tools/video/agro-arte/trilha/gerar_trilha.py --estilo agronejo` (padrão) ou `--estilo catira`, alternando entre
   vídeos seguidos. Confira que é instrumental (0 palavras na transcrição). Regras em `docs/video/TRILHA_AGRO.md`.
6. **Prévia curta → aprovação → vídeo completo.** Entregue com a lista da seção 4 do
   `DIRECAO_VIDEO_AGRO.md`.
7. **Capa no quadro 0** (seção 2.1.0 da direção): o primeiro quadro funciona como thumbnail, com a pintura viva e o
   gancho em 2 a 4 palavras gigantes. Exporte `capa.jpg` e mande junto. Gere também as **capas do Instagram
   em 9:16 e 4:5** (`tools/video/agro-arte/capa_instagram/LEIAME.md`), porque o quadro do vídeo quadrado fica mal formatado no
   Instagram (pedido do editor, 17/11/2026). **Trilha normalizada em −30 LUFS**, com volume 1
   (seção 3).
7b. **Crivo de qualidade antes de entregar** (pedido do editor, 21/11/2026): `python3 tools/video/agro-arte/crivo_qualidade.py
   final.mp4` e revisão visual de TODAS as folhas, item por item (H1 a H7). As fontes de IA com gente passam antes pelo
   crivo em modo imagem. Gente da IA só como foto parada; nada de boneco pintado sem braço e sem rosto. Tabela no roteiro.
8. **Sempre, junto com o vídeo final:** a **legenda do Instagram** e o **título do YouTube** (com 2 alternativas e
   descrição curta), nas regras da seção 4 da direção. Guarde os dois no arquivo do roteiro, seção "Publicação".

## Editor no canto (desde 18/11/2026)
- Quando o editor mandar a gravação das falas dele, siga a direção, seção 2.8:
  - recorte com `tools/video/agro-arte/recortar_apresentador.py`;
  - voz real dele;
  - prévia curta antes do vídeo completo.
- Sem gravação, a fala vai pelo clone com o seletor de S neutro.

## Antes de todo roteiro (pedido do editor, 20/11/2026)
1. **Pesquisa de tendências, sempre:**
   - autocomplete do Google e do YouTube, com sementes da linha que rende (família, herança, terra);
   - notícias da semana;
   - a lista do que está em alta vai no topo do roteiro.
2. **Prévia realista com o Wan:** gerar 2 a 4 imagens das cenas principais com o Wan 2.2 em modo imagem, na GPU grátis do
   Kaggle (`tools/video/agro-arte/ia_kaggle/wan22_previa_t4.py`), e mandar ao editor junto com o roteiro.

## Entrega técnica
- Áudio final em **48 kHz** (`-ar 48000` depois do `loudnorm`). Confira com `ffprobe` antes de entregar. Ver a direção, seção 3.
- **Sem limpeza de metadados** (decisão do editor, 19/11/2026): o arquivo sai igual ao do caseiro e do irmão, com a etiqueta padrão do ffmpeg. Nada de `-map_metadata -1`, `-fflags +bitexact` ou remoção de `encoder`.

## Não fazer
- Gerar a voz do editor com "style" acima de 0, com o modelo eleven_turbo_v2_5, ou sem passar pelo seletor de "S" (`voz_editor_s_neutro.py`): o clone chia o "S" de fim de sílaba ("desses", "resto", "juiz").
- Abrir com órgão, sigla, país ou percentual de mercado; capa com número sozinho; pergunta final sobre o setor (`PADRAO_CASEIRO.md`).
- Repetir imagem de vídeo anterior (pintura, mapa, gráfico ou foto). Confira e atualize `docs/video/CENAS_USADAS.md`.
- Citar na narração birô de crédito ou cobrança (Serasa, SPC, Boa Vista) num vídeo para devedores: a fonte vai só no rodapé.
- Repetir frase-fórmula de vídeo anterior ("Parece erro. Mas não é.", "E é justamente aí que a história fica ainda mais estranha…" ou qualquer outra). Cada roteiro com palavras próprias.
- Usar segunda voz sem necessidade real (o padrão é não ter).
- Repetir o ângulo, a norma ou o eixo do vídeo anterior (veja `PAUTA_AGRO.md` e `PAUTAS_USADAS.md`).
- Usar documento em tela cheia por muito tempo.
- Mostrar TV ou onda de áudio quando houver segunda voz.
- Pintar rosto de frente.
- Usar IA paga (MuAPI, créditos da Higgsfield ou qualquer serviço cobrado); IA gratuita pode (direção, seção 2.9). Foto sem licença, estilo de artista vivo ou estúdio, Portinari ou Tarsila.
- Fazer render antes de o roteiro ser aprovado.
