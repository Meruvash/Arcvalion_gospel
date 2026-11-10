# Auditoria de repositórios — estúdio de webdocumentários

Data da coleta: 10/11/2026. Todo o material está em `/home/user/webdoc-research/` (fora dos projetos
Arcvalion_gospel e Golden-Geek, que não foram tocados). Clones rasos (`--depth 1`) em `repos/`.

**Legenda de confiabilidade**
- **[V]** verificado por mim: li o código, o arquivo de licença ou rodei algo.
- **[A]** dado da API de busca do GitHub (estrelas, licença SPDX, data do último push). Estrelas podem ser infladas.
- **[D]** declarado pelo projeto (README, site). Não comprovado.
- **[H]** hipótese ou avaliação minha.

Os vídeos de demonstração dos READMEs são anexos do GitHub (`user-attachments`). **Não assisti a nenhum
deles.** Toda nota de "qualidade demonstrada" abaixo se apoia no que eu mesmo renderizei, ou fica
marcada como não verificada.

---

## 1. Ranking

O ranking mede a utilidade para *este* objetivo: webdocumentário com mapas reais, fotos em 2.5D,
tipografia e dados, guiado pelo Claude Code.

| # | Repositório | Papel recomendado | Por quê, em uma linha |
|---|---|---|---|
| 1 | **heygen-com/hyperframes** | Motor de render e ciclo do agente | Apache-2.0, feito para agentes, `check` que pega erros reais; renderizou a PoC sem falhas |
| 2 | **remotion-dev/remotion** | Motor alternativo / plano B | O mais maduro (desde 2020), ótimo ecossistema; licença paga para empresas com mais de 3 funcionários |
| 3 | **d3-geo + Natural Earth** (fora da lista inicial) | Mapas vetoriais | Base dos mapas das duas PoCs, domínio público e ISC |
| 4 | **maplibre-gl-js + Protomaps + deck.gl** (fora da lista) | Mapas com imagem de base, 3D e rotas | Licenças abertas, sem token; precisa de "bake" quadro a quadro |
| 5 | **Depth-Anything-V2-Small** (fora da lista) | Profundidade para 2.5D | Apache-2.0 só no checkpoint Small; rodou em 40 s na CPU |
| 6 | **nateherkai/herk-edit-kit** | Fonte de *processos* (playbook, validadores) | MIT; bom método de edição, mas o estilo "Vox" é derivado da Vox e não deve ser adotado |
| 7 | **gitethanwoo/video-editing** | Fonte de *portões de qualidade* | MIT, pequeno, com checagens determinísticas de entrega |
| 8 | **calesthio/OpenMontage** | Referência de orquestração (não usar como base) | AGPL-3.0, enorme, centrado em APIs generativas pagas |
| 9 | **veedstudio/open-edit** | Referência de CLI de render e revisão | Apache-2.0; parte das funções depende de login VEED ou fal |
| 10 | **notivn/AIEV** | Referência de UI e fila de render | MIT; centrado em talking-head e TikTok vietnamita, com Gemini pago |
| 11 | **motion-canvas/motion-canvas** | Não recomendado | MIT, mas sem release no npm desde fev/2025 |
| 12 | **bouclem/OpenAnimateMyMaps** | Ler o código de câmera; não depender dele | MIT, 2★, feito em um dia, sem testes, GUI de navegador |
| — | Opus Motion Library (GovinduSasanka) | Referência de catálogo | MIT sobre Remotion; mapas sem geografia real |
| — | EarnEdits | Fora do escopo técnico | Loja de projetos de After Effects; site bloqueado para leitura automática |

---

## 2. Fichas por projeto

### 2.1 heygen-com/hyperframes
- **Licença:** Apache-2.0 [V] (LICENSE). **Estado:** 82.212★, último push em 10/11/2026, criado em 10/03/2026 [A]. npm `hyperframes` 0.9.30, publicado em 10/11/2026 [V]. É pré-1.0 e muda rápido: o herk-edit-kit fixa a 0.7.109 e a atual é a 0.9.30 [V].
- **Arquitetura:** HTML + CSS + qualquer animação "seekável" (GSAP, WAAPI, CSS, canvas, three.js). Uma timeline GSAP pausada é registrada em `window.__timelines`, e o motor busca quadro a quadro em Chrome headless (captura *beginframe*). Monorepo com cli, engine, producer, lint, studio, player, `aws-lambda` e `gcp-cloud-run` [V].
- **Registro de blocos:** 210 blocos e 239 componentes [V]. Os relevantes aqui são `world-map`, `us-map*`, `data-chart`, `bar-chart-race`, `camera-dolly-zoom`, `parallax-*`, `camera-rig-depth-stack`, `paper-collage-reveal`, `torn-paper-rip`, `grain-overlay`, `text-match-cut` e as famílias `transitions-*`.
- **Integração com Claude Code:** plugin oficial (`claude plugin install hyperframes@hyperframes`) e skills com regras explícitas: determinismo, sem rede, sem `Math.random` sem semente [V]. O `hyperframes check` roda lint, runtime, layout, contraste, *craft* e áudio. **Na PoC ele detectou de verdade** texto de 17 px abaixo do piso de legibilidade em celular (28 px) e um contraste de 4,25:1 [V].
- **Geração automática:** CLI `render` com qualidade draft/looks/delivery, workers paralelos e render parcial [V].
- **Limitações:** proíbe rede no render, então mapas com tiles precisam ser "assados" antes [V, skill]. Fotos acima de 2 MB não são embutidas no bundle (aviso no check) [V]. O lint pede sub-composições por cena, e a PoC em arquivo único gerou 3 avisos [V]. **A telemetria vem ligada**: a skill manda rodar um "usage beacon". Desliguei com `DO_NOT_TRACK=1` [V].
- **Custo:** grátis. O app Studio tem plano Pro com modelos da HeyGen [D]. GSAP é grátis sob licença própria da Webflow, que não é OSI [V via subagente, gsap.com].

### 2.2 remotion-dev/remotion
- **Licença:** *source-available* própria [V] (LICENSE.md). Grátis para indivíduos, empresas com até 3 funcionários e organizações sem fins lucrativos. Acima disso exige **Company License** paga (preço em remotion.pro, que não consultei). Proíbe revender um derivado do Remotion.
- **Estado:** 72.218★, push em 10/11/2026, existe desde jun/2020 [A]. npm 4.0.542 [V]. É o projeto mais maduro do grupo.
- **Arquitetura:** React + TypeScript. Cada quadro é função de `useCurrentFrame()`, renderizado em Chrome headless e codificado com ffmpeg [V]. Tem pacotes oficiais úteis aqui [V]: `@remotion/gsap`, `@remotion/motion-blur`, `@remotion/transitions`, `@remotion/light-leaks`, `@remotion/noise`, `@remotion/three`, `@remotion/lottie`, `@remotion/captions`, `@remotion/maptiler` (interno, sem documentação) e `@remotion/lambda`.
- **Claude Code:** `@remotion/claude-code-plugin` e `@remotion/skills` com 13 skills, entre elas `remotion-maps` [V]. A skill de mapas usa **Mapbox** (token e conta) [V], e eu trocaria por MapLibre ou d3.
- **Na PoC:** o typecheck do TypeScript passou de primeira, e o render de 15 s levou 54 a 65 s em 4 vCPUs [V].
- **Limitações:** a licença (ver custo). Não tem um equivalente ao `check` do HyperFrames para legibilidade e contraste [H, não encontrei]. Exige React/TS de quem mantém.

### 2.3 nateherkai/herk-edit-kit
- **Licença:** MIT no LICENSE, mais `licenses/PIPELINE-USE-PERMISSION.txt` (permite uso comercial e redistribuição, mantendo o aviso) [V]. O GitHub mostra NOASSERTION por causa dos múltiplos arquivos [A].
- **Estado:** 2.726★, push em 14/10/2026, criado em abr/2026 [A]. Fixa `hyperframes` 0.7.109 e `gsap` 3.14.2 [V], defasados em relação à atual.
- **Conteúdo:** 15 skills espelhadas para Claude e Codex: cut-silences, cut-mistakes, edit-video, video-storytelling, motion-showreel, short-form-edit e outras [V]. Traz 410 cartões HTML em 2 estilos (o README diz 406) [V], 2 templates de cena, `EDITING-PLAYBOOK.md`, `MOTION_PHILOSOPHY.md`, validador de *beat-sync*, preflight e revisão de EDL [V].
- **Foco:** vídeo de *talking head* e reels de criador. Não é documentário de arquivo.
- **Ponto de atenção:** o estilo `01-vox-explainer` declara: "Animated-documentary collage in the **Vox house style**… derived from the reference images" [V]. Isso é praticamente uma identidade de terceiro, e o próprio kit avisa que Vox, Kallaway e Infinite são "aesthetic reference names" sem endosso [V]. **Recomendo não usar esses cartões como estão**, por respeito à restrição de não copiar identidades.
- **Transcrição:** ElevenLabs Scribe (pago) por padrão, com Whisper local como alternativa [V/D].
- **Vale aproveitar:** a disciplina de regras (cada nota de revisão vira regra em skill), o validador de beat-sync e a regra "cortar entre frases, nunca dentro" [V, commit].

### 2.4 calesthio/OpenMontage
- **Licença:** **AGPL-3.0** [V]. A URL original parece ter migrado: a busca retorna `OpenMontageInc/OpenMontage` com 79.390★, push em 09/11/2026, criado em mar/2026 [A]. O clone por `calesthio/OpenMontage` funcionou [V], mas não confirmei o redirecionamento (o GitHub devolveu 403 à consulta).
- **Arquitetura:** Python (222 arquivos em `tools/`) com 13 pipelines YAML: documentary-montage, animated-explainer, cinematic e outros [V]. Usa skills de "diretores" por etapa, um compositor Remotion (`remotion-composer`, com cortes como `stat_card`, `bar_chart` e `line_chart`) e também HyperFrames (`tools/video/hyperframes_compose.py`) [V]. Tem `cost_tracker`, `provider_routing` e dezenas de provedores pagos (Veo, Sora, Kling, Flux, Imagen, Pika etc.) [V].
- **Pipeline documental:** `documentary-montage.yaml` é **beta**. Ele busca e recorta footage de Pexels, Archive.org, NASA, Wikimedia e Unsplash com CLIP [V]. Não anima mapas nem fotos.
- **Mapas:** existe um módulo bom de *planejamento* (`motion-graphics/categories/maps/module.md`). Ele separa a "pista vetorial" (D3 + TopoJSON) da "pista basemap" (MapLibre assado quadro a quadro com `bake-basemap.mjs`) [V]. **Esse documento é a melhor referência conceitual sobre mapas que encontrei**, e pode ser lido mesmo sem adotar o código.
- **Exemplos:** os vídeos do README são majoritariamente generativos ("Pixar-style", Kling e Veo, com custo de US$ 1,33 a 4) [D]. Não assisti.
- **Por que não usar como base [H]:** AGPL; superfície gigante (878 arquivos de código e 158 skills em markdown) que pesa no contexto do agente; o valor dele está na orquestração de modelos generativos, contrária à regra "nunca imagem gerada por IA" do seu portal; e muita mudança de provedores (o último commit adiciona Pika).

### 2.5 notivn/AIEV
- **Licença e estado:** MIT [V]. 157★, push em 04/11/2026 [A].
- **Arquitetura:** Next.js (UI na porta 6868) + Express com Claude Agent SDK e SQLite. Cenas em HyperFrames e montagem em Remotion [V/D].
- **Foco:** talking-head, karaokê vietnamita, TikTok. Ilustrações via **Gemini (pago, cerca de US$ 0,05/imagem)** [D].
- **Vale aproveitar:** a ideia de painel com fila de render e a documentação de CPU vs. GPU por etapa (README) [V].

### 2.6 veedstudio/open-edit
- **Licença e estado:** Apache-2.0 (Copyright VEED) [V]. 1.793★, push em 05/11/2026 [A]. CLI `@veedstudio/openedit-cli` 0.8.0 [V].
- **Funções:** `render` de página HTML em Chrome com quadro exato, cache por segmento e re-render parcial; revisão automática (`review`) do vídeo gerado; `mux-audio` em -14 LUFS / -1 dBTP; transcrição local com WhisperX ou paga pela VEED; geração via fal com a chave do usuário [V].
- **Limitação:** login VEED para transcrição premium e para a passagem ao editor [V].
- **Vale aproveitar:** o conceito de *checks* de entrega como módulos (`cli/src/verify/`) e o loudness padrão.

### 2.7 gitethanwoo/video-editing
- **Licença e estado:** MIT [V]. 4★, criado em jul/2026 [A]. São 3 skills e 11 arquivos de código [V].
- **Vale aproveitar:** portões de qualidade (geometria, duração, codec, fps, sample rate, loudness, decodificação completa, checksum); proveniência de B-roll com estado de aprovação; e a regra "descrição de modelo é hipótese quando o sinal determinístico discorda" [V]. Isso combina com o "nada inventado" do seu CLAUDE.md.

### 2.8 motion-canvas/motion-canvas
- **Licença e estado:** MIT [V]. 19.763★ [A]. Último commit em 02/07/2026 [V], mas a **última versão no npm (3.17.2) é de 16/02/2025** [V].
- **Avaliação:** bom para animação vetorial imperativa (geradores TypeScript) e com editor próprio. O fork com API headless é o `midrender/revideo` (MIT, 4.198★, push em jul/2026) [A, subagente]. Sem release há 21 meses, não serve como base [H].

### 2.9 bouclem/OpenAnimateMyMaps
- **Licença e estado:** MIT [V]. 2★, criado e último push em 23/09/2026 [A]. Changelog "0.1.0 — initial build", "Tests: none yet" [V].
- **Arquitetura:** Next.js + MapLibre 6 + three.js + Mediabunny (WebCodecs) [V]. É um estúdio de navegador, sem modo headless.
- **Atenção:** usa tiles Esri satellite e CARTO raster (`lib/basemaps.ts`) [V], cujos termos de uso precisam ser checados antes de qualquer uso comercial [H].
- **Vale ler:** `lib/cameraMath.ts` e `lib/timeline.ts` (câmera fly-to, órbita e varredura), e o LESSONS.md sobre as quebras do MapLibre v6 [V].

### 2.10 Opus Motion Library (GovinduSasanka/opus-motion-library) — investigado pelo subagente
- MIT sobre Remotion 4. 10★, criado em 21/10/2026 [A].
- Declara 616 "motions" [D]; o subagente contou os arquivos por família [V-sub]. Inclui famílias úteis como `camera/` (dolly-zoom, orbit-parallax, rack-focus), `image/` (ken-burns, torn-paper-collage) e `hud/` (location-time-stamp, source-tag).
- **Mapas sem geografia real.** O cabeçalho de `choropleth-fill.tsx` diz: "ABSTRACT regions… no real geography" [V-sub].
- Não renderizei nada dele. Serve como catálogo de ideias, não como base.

### 2.11 EarnEdits (earnedits.com) — investigado pelo subagente
- O site devolveu **403 (Cloudflare)** a toda leitura automática, e eu não troquei o user-agent para me passar por navegador. **Nada foi verificado em primeira mão.**
- Pelas fontes indiretas (blogs de afiliados): é uma loja ou assinatura de **projetos de After Effects (.aep)**, com categorias como "VOX Edits", "Storytelling" e "Mo-graph". Os preços são conflitantes entre as fontes: US$ 17 a 27/mês. Não encontrei texto de licença nem vídeos de amostra [D, não verificado].
- **Conclusão [H]:** é útil como *referência de linguagem*, mas não pode ser incorporado num pipeline por código. Os arquivos .aep são comerciais e exigem After Effects, e não consegui ver o que contêm.

### 2.12 Outros projetos relevantes (levantamento do subagente via API de busca)
| Projeto | ★ / licença / push [A] | Uso proposto |
|---|---|---|
| d3/d3-geo + nvkelso/natural-earth-vector | ISC; domínio público | mapas vetoriais editoriais (**usado nas PoCs**) |
| maplibre/maplibre-gl-js | 12k / BSD-3 / 11-2026 | mapas com basemap, terreno, globo; render quadro a quadro |
| protomaps/basemaps (PMTiles) | 771 / OSM ODbL | basemap auto-hospedado, sem servidor de tiles nem token |
| visgl/deck.gl | 14,7k / MIT | rotas animadas (TripsLayer), arcos, hexbins |
| CesiumGS/cesium | 15,9k / Apache-2.0 | globo 3D; tiles fotorrealistas do Google exigem conta e cota |
| DepthAnything/Depth-Anything-V2 | código Apache-2.0; **só o Small é Apache, Base/Large são CC-BY-NC** | profundidade para 2.5D (**usado nas PoCs**) |
| BrokenSource/DepthFlow | 1,6k / **AGPL-3.0** | paralaxe por shader a partir da profundidade (GPU) |
| ggml-org/whisper.cpp · SYSTRAN/faster-whisper | MIT | transcrição local com tempos por palavra |
| m-bain/whisperX | BSD-2 | alinhamento por palavra; a diarização usa modelos pyannote com acesso restrito |
| kajisho5/ffmpeg-skill | 5k / MIT | MCP de ffmpeg (loudness, legendas) |
| digitalsamba/claude-code-video-toolkit | 2,5k / MIT | skills Remotion+ffmpeg; desligar os geradores de imagem por IA |
| midrender/revideo | 4,2k / MIT | alternativa MIT ao Remotion; sem push há cerca de 4 meses |
| ManimCommunity/manim | 42k / MIT | diagramas e matemática; fraco para mapas e fotos |
| Mapbox GL JS | licença proprietária desde a v2 | **evitar** (token e cobrança por carga) |
| TTS: chatterbox (MIT), Piper1 (GPL, licença por voz), F5-TTS e Coqui XTTS (pesos NC) | — | só se houver narração sintética; o padrão deve ser voz humana |

A tabela completa do subagente, com notas de risco, está resumida em `research/notes/` (arquivo
`outros-projetos.md`).

---

## 3. O que não consegui verificar
- **Qualidade visual** de qualquer vídeo de demonstração dos READMEs (Herk, OpenMontage, HyperFrames, Opus). Não assisti.
- EarnEdits por completo (403).
- O preço da Company License do Remotion. Também não sei se a sua organização se enquadra na licença gratuita: isso depende de ser pessoa física, ONG ou empresa com até 3 funcionários.
- Estrelas reais e se o `calesthio/OpenMontage` redireciona para `OpenMontageInc/OpenMontage`.
- O comportamento do `@remotion/maptiler`, que é interno e não tem documentação.
