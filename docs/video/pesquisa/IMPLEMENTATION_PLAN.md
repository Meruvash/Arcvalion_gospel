# Recomendação técnica e plano de implementação (Fase 6)

> **Status: aguardando sua aprovação.** Nada do sistema definitivo foi construído. Os projetos
> Arcvalion_gospel e Golden-Geek não foram alterados, nenhuma dependência foi instalada neles e não
> houve commit nem push. Tudo está em `/home/user/webdoc-research/`.
>
> **Atenção:** o contêiner é efêmero. Se a sessão for encerrada, esta pasta se perde. Antes disso,
> preciso que você diga onde guardar o material: em um repositório, num branch, ou como download.

Os itens deste documento estão marcados como **[F]** fato verificado, **[H]** hipótese ou **[R]**
recomendação.

## 1. Ranking dos repositórios
Ver `REPOSITORY_AUDIT.md` §1. Resumo:
1. HyperFrames — motor.
2. Remotion — plano B.
3. d3-geo + Natural Earth.
4. MapLibre + Protomaps + deck.gl.
5. Depth-Anything-V2-Small.
6. Herk Edit Kit — processos.
7. gitethanwoo/video-editing — portões de qualidade.
8. OpenMontage — referência de orquestração.
9. open-edit.
10. AIEV.
11. Motion Canvas.
12. OpenAnimateMyMaps.

## 2. Evidências audiovisuais
- Vídeos: `poc/remotion/out/poc-remotion.mp4`, `poc/hyperframes/out/poc-hyperframes.mp4` e
  `poc/comparacao/lado-a-lado.mp4` [F].
- Quadros e folhas de contato: `research/evidencias/` [F]. Inclui a sequência de falhas da paralaxe
  (v1 → final).
- **Não assisti** a vídeos de terceiros (READMEs, YouTube). Os padrões de referência vêm de
  transcrições e entrevistas (`research/notes/`).

## 3. Comparação das provas de conceito
Ver `PROOF_OF_CONCEPT_RESULTS.md`. Em uma linha: paridade visual (SSIM 0,969) [F]. O Remotion
renderizou cerca de 30% mais rápido [F]. O HyperFrames tem checagem automática de legibilidade e
contraste que funcionou na prática [F]. A paralaxe automática e o mapa em zoom alto são os pontos
fracos, nos dois motores [F].

## 4. Arquitetura recomendada [R]

```
                ┌───────────────────────────────────────────────────────────┐
  pauta/pesquisa│ episodio/                                                 │
  (humano+Claude)│  roteiro.md  ──►  fontes.json (link+data por fato)       │
                │  locucao.wav ──►  cues.json (tempo por palavra, Whisper)  │
                │  arquivo/  (fotos, docs, com licença e proveniência)      │
                └──────────────┬────────────────────────────────────────────┘
                               ▼
                 spec.json (neutro de motor: cenas, tempos por cue, tokens)
                               │  validadores: fatos têm fonte? licenças? legibilidade?
         ┌─────────────────────┼─────────────────────────────┐
         ▼                     ▼                             ▼
  pré-processo mapas     pré-processo foto 2.5D        pré-processo áudio
  d3-geo/Natural Earth   Depth-Anything-Small →         ffmpeg: ducking,
  MapLibre+PMTiles       camadas → REVISÃO MANUAL       loudnorm −14 LUFS
  (bake quadro a quadro)  (gate humano)
         └─────────────────────┼─────────────────────────────┘
                               ▼
        biblioteca "Arquivo Aberto" (componentes de cena HyperFrames + GSAP)
                               ▼
        hyperframes check  →  snapshot/review  →  render draft  →  aprovação  →  render final
                               ▼
        portões de entrega (duração, codec, loudness, decodificação, checksum)  → MP4 + legendas + créditos
```

Decisões [R]:
- **Motor: HyperFrames**, com a versão fixada exatamente (sem `^`) e a telemetria desligada no projeto.
- **O spec é a fonte da verdade.** Ele descreve cena, tempos e curvas, e os componentes só o
  interpretam. A PoC mostrou que o mesmo spec roda nos dois motores, e é isso que permite trocar de
  motor se o HyperFrames quebrar.
- **Portões humanos explícitos:** aprovar o roteiro e as fontes; aprovar as camadas 2.5D; aprovar o
  draft; aprovar o final. É o equivalente às "seis rodadas de revisão" da Vox.
- **Sem IA generativa de imagem ou vídeo.** Isso segue a regra do seu CLAUDE.md. IA entra só na
  transcrição, na profundidade (usada como máscara, não como pixel novo) e no apoio do Claude ao código
  e à checagem.

## 5. Repositórios a clonar (quando aprovado) [R]
| Repositório | Como | Para quê |
|---|---|---|
| heygen-com/hyperframes | dependência npm `hyperframes@<versão exata>` + plugin/skills | motor e checagens |
| greensock/GSAP | npm `gsap@3.15.x` | animação |
| d3/d3-geo, topojson-client | npm | mapas |
| nvkelso/natural-earth-vector | dados 1:110m, 1:50m e 1:10m (domínio público) | geometria |
| maplibre/maplibre-gl-js + protomaps/basemaps | npm + arquivo PMTiles local | basemap (fase 3) |
| DepthAnything/Depth-Anything-V2 (Small, Hugging Face) | venv Python separado | máscaras 2.5D |
| ggml-org/whisper.cpp ou SYSTRAN/faster-whisper | binário ou venv | cues por palavra |
| herk-edit-kit, gitethanwoo/video-editing, OpenMontage | **só leitura**, para adaptar ideias citando a origem (MIT exige o aviso; OpenMontage é AGPL e **não se copia código**) | processos, portões, mapas |

## 6. Dependências necessárias [F, salvo indicação]
- Node 22+, npm, Chromium (já existe no ambiente: `/opt/pw-browsers`), ffmpeg 6+.
- Python 3.11+ com venv isolado: torch CPU, transformers, opencv-headless, pillow. São cerca de 1 GB
  instalados, e o modelo Small tem cerca de 100 MB [H].
- Opcionais: GPU (acelera render e profundidade); GIMP ou Krita para retoque de camadas;
  whisper.cpp.

## 7. Componentes a reutilizar [R]
- Da PoC (nossos): `make_layers.py`, `prep_geo.mjs`, `tools/frames.sh`, a cena de mapa, a de
  tipografia e as duas transições.
- Do HyperFrames: `check`, `snapshot`, `fitTextFontSize` e, como referência, os blocos `world-map`,
  `data-chart` e `transitions-*`. São Apache-2.0 e podem ser adaptados com o aviso de origem.
- Do herk-edit-kit (MIT): o validador de beat-sync, a regra de corte entre frases e o formato de
  registro de regras em skills.
- Do gitethanwoo/video-editing (MIT): portões de entrega e o manifesto de proveniência de B-roll.
- Do OpenMontage (AGPL, só ideias): a separação "pista vetorial × pista basemap" e o bake com
  `map.once('idle')` por quadro.

## 8. Componentes a desenvolver [R]
1. **Esquema do spec** (JSON Schema) com validação: cenas, cues, tokens e fontes obrigatórias por fato.
2. **Biblioteca "Arquivo Aberto":** prancha de mapa (com níveis de detalhe), foto 2.5D, documento em
   close, número-herói, gráfico, linha do tempo, citação, abertura e encerramento.
3. **Bake de basemap** (MapLibre + PMTiles, quadro a quadro, determinístico).
4. **Fluxo 2.5D com portão manual:** gera as camadas, abre uma prévia, recebe as camadas retocadas
   e só depois libera o render.
5. **Cues de narração:** WAV → Whisper → `cues.json` → tempos do spec por palavra.
6. **Mixagem e entrega:** ducking, loudness, legendas (SRT/VTT) e créditos automáticos a partir de
   `fontes.json`.
7. **Skill `webdoc` para o Claude Code**, com o fluxo, as regras e os portões, no mesmo formato das
   skills do seu repositório.
8. **Checagens próprias** que o HyperFrames não faz: fato sem fonte, licença de imagem ausente, crédito
   abaixo de 22 px e paridade de cores com os tokens.

## 9. Custos previstos
| Item | Custo | Base |
|---|---|---|
| HyperFrames, GSAP, d3, MapLibre, Natural Earth, Depth-Anything-Small, Whisper | **R$ 0** | licenças verificadas [F]; GSAP sob licença Webflow (grátis, mas não OSI) |
| Render local (15 s em cerca de 80 s em 4 vCPUs; 10 min de vídeo em cerca de 1 h) | R$ 0 além da máquina | extrapolação linear da PoC [H]; cenas pesadas podem custar mais |
| Render em nuvem (opcional) | não estimado | depende do provedor; só com aprovação |
| Remotion, se usado como motor e se a organização não se enquadrar na licença gratuita | Company License paga | preço não verificado (remotion.pro) |
| Basemap de satélite licenciado ou Google 3D Tiles | variável | só se você quiser imagem de satélite; o padrão é vetor/OSM |
| Efeitos sonoros e trilha | R$ 0 (CC0) a assinatura | decisão editorial |
| Locução | voz humana (sem custo de API) | TTS só com licença clara e sua aprovação |
| After Effects + GEOlayers (escape manual opcional) | assinatura Adobe + plugin | não recomendado como base |

## 10. Plano de implementação (após aprovação) [R]
Cada fase termina com uma entrega que você assiste e aprova antes da próxima.

| Fase | Entrega | Critério de aceite |
|---|---|---|
| 0. Decisões | onde fica o repositório do estúdio; motor (HF ou Remotion); política de inpainting; quem grava a locução | suas respostas às perguntas abaixo |
| 1. Fundação (1–2 sessões) | repositório `webdoc-studio` com spec + schema, tokens v1, 3 componentes da PoC portados para sub-composições HF, `check` sem avisos | a PoC re-renderiza idêntica a partir do spec v1 e `check` dá zero avisos de legibilidade/contraste |
| 2. Mapas (2 sessões) | prancha de mapa com níveis de detalhe (110m/50m/10m), rotas, coropleta, escala, fonte | 3 planos de mapa de exemplo aprovados por você |
| 3. Foto 2.5D (1–2 sessões) | fluxo com portão manual + guia de retoque | uma foto com paralaxe sem artefato visível em 100% |
| 4. Narração e som (2 sessões) | cues por palavra, ducking, loudness, legendas | um trecho de 60 s sincronizado por palavra |
| 5. Biblioteca completa (3+ sessões) | documento, gráfico, linha do tempo, citação, abertura e encerramento | episódio-piloto de 2–3 min |
| 6. Skill e operação | skill `webdoc` + checklist de publicação + render reprodutível | outro agente produz um episódio seguindo só a skill |

## 11. Perguntas para você decidir
1. **Licença do Remotion:** o projeto é de pessoa física, ONG, ou empresa com até 3 funcionários? Se
   sim, o Remotion fica grátis e a disputa empata. Prefere maturidade (Remotion) ou ferramentas de
   checagem para o agente (HyperFrames)? Minha recomendação é HyperFrames, com o spec neutro.
2. **Inpainting nas camadas 2.5D:** só retoque manual (mais lento e fiel ao arquivo) ou aceitar
   preenchimento generativo *apenas* em áreas ocultas, com aviso? Recomendo o manual, pela regra do
   seu portal.
3. **Onde viver:** um repositório novo (por exemplo `webdoc-studio`) ou uma pasta num dos dois
   repositórios existentes?
4. **Guardar esta pesquisa:** posso commitá-la num branch para não se perder quando o contêiner for
   encerrado?
