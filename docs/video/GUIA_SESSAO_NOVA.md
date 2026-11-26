# Guia para sessão nova: vídeos do agro (comece por aqui)

Resumo de tudo o que foi aprendido e aprovado pelo editor (Dr. Pelicioni) de 10 a 25/11/2026. Leia este arquivo inteiro
antes de pesquisar pauta, escrever roteiro ou gerar vídeo. Cada regra aponta para o arquivo que a detalha. Em caso de
conflito, vale o `CLAUDE.md` e, depois, a regra com a data mais recente.

---

## 1. O que o canal é (e não é)

- **Público:** produtor rural brasileiro (dono de terra, pequeno e médio).
- **Formato:** vídeo curto quadrado (1080 × 1080, 50 a 62 s) para Reels/Shorts. Narrador e, no fim, o Dr. Pelicioni
  (voz clonada).
- **Lado:** **a favor do produtor.** Nada de ensinar peão, caseiro, arrendatário ou fiscal a cobrar o dono
  (`PAUTA_AGRO.md`, seção 0, decisão de 23/11/2026).
- **Marca visual:** pintura animada em código, à maneira de mestres em domínio público (de preferência paisagistas
  brasileiros). "As pinturas de IA todo mundo consegue fazer" (editor, 25/11/2026).
- **Nada inventado:** fato com fonte primária lida (lei no Planalto, súmula no STF, acórdão), com link e data. Citação
  literal só de texto lido.

## 2. O que deu resultado (por que fazemos assim)

| Vídeo | Resultado | O que ensinou |
|---|---|---|
| "O caseiro e o vizinho" (16/11) | 2.200 visualizações | Nasceu o **Padrão Caseiro**: dúvida que o produtor já busca, personagem próximo, terra em risco, mito desfeito e ameaça na 1ª frase |
| "O irmão vendeu sem avisar" (16/11) | passou de 5.000 | Segundo padrão ouro: família, venda sem avisar, prazo curto |
| "A porta e o porteiro" (EUDR) | quase nada | Abrir com órgão, sigla, país ou percentual não funciona |
| "Papel atrasado" (CCIR, v1) | reprovado pelo editor | Gente gerada por IA saiu deformada. Daí o **crivo de qualidade** e a regra de não gerar gente |
| "Multa ambiental prescreve?" (23/11) | o editor notou que a **animação** atraiu mais que as imagens de IA | Daí a **direção artística** (pintura completa, de obra de arte) |
| "O vizinho fechou a estrada?" (25/11) | **sucesso** (editor, 26/11) | Modelo atual: dúvida do Google com o mito na boca do vizinho, lei a favor do produtor, 100% pintura em código, cada movimento com função e uma cena espacial (mapa) quando a mensagem pede |

Os números e as análises completas estão em `PADRAO_CASEIRO.md`, seções 1 e 5.1.

## 3. Mapa dos arquivos

### Regras (ler nesta ordem)
1. `CLAUDE.md` (raiz): resumo de todas as regras, com datas.
2. `docs/video/PADRAO_CASEIRO.md`: roteiro que viraliza. A seção 4 é o Crivo do Caseiro (nota da pauta); a 5.3 traz os
   5 moldes de gancho.
3. `docs/video/PAUTA_AGRO.md`: lado do produtor, eixos A a I, rodízio, mínimo de 5 candidatas.
4. `docs/video/AUDITORIA_PADRAO_OURO.md`: auditoria do roteiro (23 itens, aprovação com 21 ou mais).
5. `docs/video/DIRECAO_ARTISTICA.md`: como pintar (quadro completo, foco, 4 planos, luz, paleta), código primeiro e
   crivo A1–A10.
6. `docs/video/DIRECAO_MOTION.md`: todo movimento, 3D e letreiro com função. Crivo M1–M8 e plano de imagem com coluna
   "Função".
7. `docs/video/DIRECAO_VIDEO_AGRO.md`: voz, legenda amarela, IA grátis (seção 2.9), crivo de qualidade H1–H7, entrega.
8. `docs/video/PROMPT_VIDEO_AGRO.md` e `TRILHA_AGRO.md`: estrutura de 10 falas e trilha.

### Registros (consultar antes e atualizar depois de cada vídeo)
- `docs/video/PAUTAS_USADAS.md`: cada pauta, eixo, gancho e situação (aprovada, recusada e por quê).
- `docs/video/CENAS_USADAS.md`: cada cena já usada. **Nenhuma imagem se repete.**
- `docs/video/roteiros/*.md`: um arquivo por vídeo, com pesquisa, falas, auditoria, fatos com fonte, cuidados, plano de
  imagem, crivos, entrega e publicação (título, descrição, legenda). **Modelo atual:**
  `docs/video/roteiros/servidao-passagem.md`.

### Ferramentas (`tools/video/agro-arte/`)
| Arquivo | Para quê |
|---|---|
| `README.md` | Instalação do motor de pinturas (huashu-art-motion) e do HyperFrames |
| `auditar_roteiro.py falas.json` | Auditoria de padrão ouro (23 itens; reconhece os 5 moldes de gancho) |
| `gerar_vozes.py`, `voz_editor_s_neutro.py`, `processar_vozes.py`, `preparar.py` | Vozes, transcrição e linha do tempo (`tempos.json`) |
| `trilha/gerar_trilha.py saida.mp3 60000 --estilo catira\|agronejo` | Trilha instrumental (alternar os estilos entre vídeos) |
| `cenas/*_scenes.js` e `cenas/eras_*.js` | Pinturas em código. **Referência atual: `cenas/sv_scenes.js`** (porteira, ponte, mapa, porteira aberta) |
| `montar_exemplo_*.py` | Montagem HyperFrames. **Referência atual: `montar_exemplo_servidao.py`** (câmera com função, régua, transições mapa ↔ chão) |
| `crivo_qualidade.py video.mp4` | Folhas de quadros e listas H1–H7, A1–A10 e M1–M8 |
| `auditar_video.py video.mp4 --tempos tempos.json` | Abertura e ritmo (V1–V5, S1, S2) |
| `capa_instagram/modelo/` (`v.html`, `f.html`, `shot.cjs`) | Capas do Instagram em 9:16 e 4:5 (fundo desfocado, quadro, título, carimbo) |
| `ia_kaggle/` | Scripts do Wan 2.2 na GPU grátis do Kaggle (hoje só para paisagem sem gente) |

### Pesquisas guardadas
- `docs/video/pesquisa/novela-ia-barata-e-boa.md` (e notas na pasta de mesmo nome): ferramentas de vídeo com IA,
  preços e qualidade (25/11/2026).
- `docs/video/DIRECAO_MOTION.md`, seção "Fontes": princípios de motion, Bruce Block, câmera motivada, quadros de estilo.

### Novela (outro Instagram)
- Skill `novela` e `docs/video/novela/`. A sessão própria da novela segue essas regras, separadas das do agro.

## 4. Fluxo de um vídeo (passo a passo)

1. **Pesquisa de tendência.**
   - Autocomplete do Google: `https://suggestqueries.google.com/complete/search?client=firefox&hl=pt-BR&gl=br&q=…`,
     com sementes como "produtor rural pode", "fazenda pode", "estrada rural", "servidão de passagem", "poço artesiano",
     "multa ambiental".
   - Notícias da semana (WebSearch).
   - Se ajudar, o Virlo.
2. **Pauta.**
   - No mínimo 5 candidatas, de 3 eixos ou mais, com nota no Crivo do Caseiro (12 ou mais de 16).
   - Rodízio de eixos: nunca o mesmo eixo em dois vídeos seguidos; o eixo A no máximo 1 em 4.
   - Só pautas a favor do produtor.
   - Registrar em `PAUTAS_USADAS.md`.
3. **Fonte primária.**
   - Ler a lei, a súmula ou o acórdão e anotar a citação literal.
   - O Planalto às vezes recusa o `curl`; nesse caso, use o subagente `web-fetch`.
4. **Roteiro de 10 falas.**
   - Molde de gancho diferente do vídeo anterior (você sabia, pergunta + resposta seca, ordem contrária, suspense,
     imagina).
   - Fecho do editor: "Eu sou o Dr. Pelicioni, advogado. Na/Em X, …. Me segue pra proteger a sua terra."
   - Rodar `auditar_roteiro.py` (21/23 ou mais).
5. **Plano de imagem** com as colunas Falas | Cena | Função | Movimento | Por que (`DIRECAO_MOTION.md`, seção 8):
   - 4 a 5 pinturas completas;
   - 3D só para espaço ou geografia (mapa, maquete, caminho);
   - Higgsfield só se uma cena necessária exigir precisão que o código não alcança, com justificativa escrita.
6. **Quadros de estilo.** Pintar 1 ou 2 cenas-chave em código e passar no crivo artístico **antes** de mostrar.
   - Mandar ao editor o roteiro, a tabela da auditoria e os quadros de estilo, e **esperar a aprovação**.
7. **Produção.** Pasta de trabalho fora do repositório, por exemplo `/home/user/webdoc-research/poc/<tema>/`.
   - Copiar `gerar_vozes.py`, `processar_vozes.py`, `preparar.py` e a montagem de referência.
   - Vozes: `gerar_vozes.py 1,…,9`, depois `voz_editor_s_neutro.py falas.json 10`, `processar_vozes.py` e `preparar.py`.
   - Trilha: `gerar_trilha.py`, `loudnorm=I=-30:TP=-6`; conferir 0 palavras no STT.
   - Pinturas: copiar `*_scenes.js` e `eras_*.js` para o motor e renderizar com `render_local.py --film X --solo id`.
     Recortar `crop=1080:1080:420:0`.
   - Montagem: `python3 montar.py`, `npx hyperframes check`, snapshots dos momentos-chave e `render --quality high`.
   - **Render em alta qualidade** (pedido do editor, 26/11/2026: "o vídeo está muito compactado"):
     `npx hyperframes render --quality high --video-frame-format png --video-bitrate 16M --max-bitrate 24M -o render.mp4`.
   - **Master só no áudio, sem recomprimir o vídeo:** `ffmpeg -i render.mp4 -c:v copy -af "loudnorm=I=-14.5:TP=-2:LRA=11,alimiter=limit=0.83:level=disabled,aresample=48000"
     -ar 48000 -c:a aac -b:a 192k -movflags +faststart final.mp4`. Confira com `ffprobe` se a taxa ficou em 10 Mbps ou mais
     (de 60 a 100 MB por minuto).
8. **Crivos.**
   - Rodar `crivo_qualidade.py` e abrir **todas** as folhas: H1–H7, A1–A10, M1–M8.
   - Rodar `auditar_video.py`.
   - Corrigir o que reprovar e renderizar de novo. Os erros mais comuns estão na seção 6.
9. **Entrega.**
   - Arquivos: mp4, capa (quadro 0), capas do Instagram em 9:16 e 4:5, título do YouTube e 2 alternativas, descrição
     com fontes, legenda do Instagram.
   - Atualizar o roteiro (Entrega, Crivos, Publicação), `PAUTAS_USADAS.md` e `CENAS_USADAS.md`.
   - Rodar os checadores do `CLAUDE.md`, fazer o commit e o push.

## 5. Receitas técnicas

- **HyperFrames:**
  ```
  export DO_NOT_TRACK=1 PRODUCER_HEADLESS_SHELL_PATH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
  npx hyperframes check
  npx hyperframes snapshot --at T --no-end -o dir   (gera uma pasta com um png)
  npx hyperframes render --quality high -o x.mp4
  ```
  - O que o JavaScript da página usar precisa ser número: `FAL()` só existe no Python. Passe os valores pelo `C` ou
    pelo `M`.
  - **Cada overlay na sua própria `data-track-index`.** Duas camadas na mesma faixa fazem uma delas não sumir.
- **Motor de pinturas (huashu-art-motion):**
  - Instalação no `README.md` desta pasta.
  - Renderizar: `uv run -q --with playwright python render_local.py --film <nome> --solo <id> --from 0 --to <s> --fps 30 --crf 16 --no-counter --out x.mp4`.
  - O aviso "404 page error" é inofensivo.
  - O quadro é de 1920 × 1080 e o recorte quadrado vai de x = 420 a 1500: componha dentro dele.
  - Desenhe por cima da pincelada (`M.broken`) os elementos que precisam de nitidez: divisas, ponte, letras. Para isso,
    pegue o contexto do canvas **novo** que o `broken` devolve.
- **Vozes (ElevenLabs, chave injetada pelo proxy; use `xi-api-key: dummy`):**
  - Narrador: `plASsyS7JE6GCAvx9uIc` (eleven_multilingual_v2, style 0,25, atempo 1,08).
  - Editor: só pelo `voz_editor_s_neutro.py` (style 0, nunca eleven_turbo_v2_5).
- **Higgsfield (créditos do editor):**
  - Usar só com a justificativa da regra "código primeiro".
  - Custos medidos: Seedance 2.0 Mini, 5 s em 1:1, 5 créditos; Seedance 2.5, 35; imagem `gpt_image_2_6`, 0,75.
  - O filtro de direitos autorais às vezes recusa o texto: reescreva e reenvie.
  - Gente: só em plano aberto, de costas ou de longe, e conferida no crivo.
- **Kaggle (GPU T4 grátis, credencial injetada pelo proxy):**
  - Enviar: `POST https://www.kaggle.com/api/v1/kernels/push` com o JSON do kernel (`enableGpu`,
    `machineShape: NvidiaTeslaT4`).
  - Acompanhar: `/api/v1/kernels/status` e `/kernels/output`.
  - O nome de usuário do Kaggle é do editor: pergunte, não grave no repositório.
  - O Wan 2.2 em imagem é bom para paisagem. Animar gente por IA a 576 px deforma: proibido.
- **3D (Three.js, `three.min.js` do motor):**
  - Renderiza no Chromium com `--use-angle=swiftshader`, cerca de 2 s por quadro.
  - Só para mapa ou maquete com informação. O teste da "porteira 3D" ficou como exemplo do que não fazer.

## 6. Erros que já cometemos (não repetir)

- **Gente gerada por IA deformada** (CCIR v1): não gerar gente; se for indispensável, só em plano aberto e conferida.
- **Pinturas pobres** ("livrinhos", objetos soltos em fundo chapado): sempre um quadro completo.
- **3D sem função** (porteira no meio do nada): 3D só para espaço ou mapa.
- **Letreiro em cima do foco ou da legenda:**
  - rótulo do mapa sobre a legenda;
  - "10 ANOS" sobre a ponte;
  - etiquetas sobre a porteira.

  Confira A10 em cada folha.
- **Overlay que não some:** duas camadas na mesma faixa do HyperFrames, ou duração negativa quando a palavra-gatilho
  cai depois do corte.
- **Copa de árvore em meia-lua ou bloco chapado:** cachos de flor também nos nós intermediários, com 3 tons (sombra,
  meio e luz).
- **Elementos alinhados ao lado errado da cena:** ponte que não atravessa o rio, porteira de perfil. Calcule a geometria
  (cruzamento da estrada com o rio, direção da estrada) em vez de chutar coordenadas.
- **Pauta contra o produtor** (moradia do peão): recusada. Sempre a favor do produtor.
- **Gancho repetido** ("Você sabia" todo dia): alternar os 5 moldes.
- **Vídeo compactado demais** (até o poço, 26/11/2026): a montagem saía com cerca de 3 Mbps e era recomprimida no master
  (CRF 18), terminando em 1,8 Mbps. A pincelada e o céu degradê perdiam textura antes mesmo da recompressão do Instagram e
  do YouTube. Agora o render sai a 16 Mbps e o master copia o vídeo sem recomprimir (seção 4, passo 7).
- **Item S2 do `auditar_video.py`:** marca falas em que só entra um letreiro suave. É aceitável pela direção de motion,
  mas avise o editor.

## 7. O que fica fora do repositório (e como refazer)

- **Vídeos finais, capas e prévias:** `/home/user/webdoc-research/roteiros/` (o contêiner da sessão é apagado). Se o
  editor pedir um vídeo antigo, regenere pela montagem guardada (`montar_exemplo_*.py`) e pelas cenas (`cenas/`).
- **Pastas de trabalho** (`/home/user/webdoc-research/poc/<tema>/`): vozes, trilha e quadros renderizados. São
  recriáveis pelos scripts.
- **Segredos:** nunca no repositório. As chaves do ElevenLabs, Kaggle e Higgsfield vêm do ambiente ou do proxy.
