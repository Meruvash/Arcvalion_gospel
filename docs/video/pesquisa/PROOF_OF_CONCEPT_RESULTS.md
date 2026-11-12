# Provas de conceito — Remotion × HyperFrames

## 1. Configuração idêntica (o que foi igual nas duas)

| Item | Valor |
|---|---|
| Roteiro e tempos | `poc/shared/data/spec.json` (um único arquivo, lido pelas duas) |
| Resolução, fps e duração | 1920×1080, 30 fps, 15 s (450 quadros), H.264 |
| Mapa | Natural Earth 4.1.0, escala 1:50m (via `world-atlas` 2.0.2), convertido para `world.geo.json`; projeção ortográfica com d3-geo 3 |
| Foto | "Avenida Central 8", acervo do Instituto Moreira Salles, **domínio público** no Wikimedia Commons; data da foto não informada |
| Camadas 2.5D | geradas uma vez por `poc/shared/scripts/make_layers.py` (Depth-Anything-V2-**Small**, Apache-2.0, CPU) |
| Fontes | Newsreader, IBM Plex Sans Condensed e IBM Plex Mono (OFL, arquivos locais) |
| Textura | grão de papel procedural com semente fixa (1906), gerado por nós |
| Identidade | tokens de cor e curvas no `spec.json` (ver `ART_DIRECTION.md`) |
| Máquina | contêiner com 4 vCPUs, 15 GB de RAM, **sem GPU** (WebGL por software) |
| APIs pagas | nenhuma (o ElevenLabs está conectado no ambiente, mas não foi usado) |

**Fatos do roteiro** (Wikipédia pt, "Avenida Rio Branco (Rio de Janeiro)", consultada em 10/11/2026):
1.800 m de extensão, 33 m de largura e "após seis meses de trabalho estava aberta de ponta a ponta".
A Wikipédia é **fonte secundária**; para publicar, seria preciso confirmar em fonte primária.

**Problema de checagem achado durante o roteiro:** o mesmo artigo dá "641 casas" demolidas na seção
História e "300 casas coloniais" na seção Arquitetura. Tirei o número do roteiro. É um bom exemplo de
por que o pipeline precisa de uma etapa de checagem *antes* da animação.

### Roteiro (15 s)
| Tempo | Cena | Elementos |
|---|---|---|
| 0–5,4 s | **Mapa animado** | O globo gira do Atlântico até o Rio; zoom em escala log (430 → 5200 → 16000); graticula, destaque do Brasil, pino com pulso, rótulo "RIO DE JANEIRO / Capital federal · 1904", crédito do dado |
| 4,4–5,4 s | **Transição 1** | Íris circular aberta a partir do pino, revelando a foto (*match cut* do lugar) |
| 4,4–10,6 s | **Foto com paralaxe** | 3 planos; a câmera inclina da rua para a cúpula com aproximação de 8%; legenda com máscara; crédito |
| 9,8–10,6 s | **Transição 2** | Folha de papel entra girando e empurra a foto, que escurece e se desloca |
| 9,8–15 s | **Tipografia** | Chapéu com fio de acento; 3 números que contam (1.800 / 33 / 6) com unidade em itálico e legenda; filete desenhado; fonte da informação |

## 2. Resultados medidos

| Medida | Remotion 4.0.542 | HyperFrames 0.9.30 + GSAP 3.14.2 |
|---|---|---|
| Render de 15 s (4 vCPUs, sem GPU) | 54–65 s (3 execuções), `--concurrency=4`, CRF 16 | 79–81 s, `--quality high`, workers automáticos |
| Arquivo | 60,0 MB (cerca de 32 Mb/s) | 61,3 MB (cerca de 34 Mb/s) |
| Linhas de código da cena | 233 (6 arquivos TSX/TS) | 202 (1 HTML) |
| Validação pré-render | `tsc --noEmit`: 0 erros | `hyperframes check`: 0 erros, 5 avisos úteis (3 de estrutura, 1 de contraste 4,25:1, 1 de legibilidade com 17 px abaixo do piso de 28 px) |
| Diferença visual entre os dois (SSIM, 450 quadros) | — | média **0,969**; mapa 0,976; foto 0,960; tipografia 0,972; mínimo 0,920 em 7,13 s |
| Adaptações necessárias | `delayRender` para fontes e GeoJSON | dados como `<script>` (o HF proíbe *fetch*); telemetria desligada com `DO_NOT_TRACK=1`; Chrome do sistema via `PRODUCER_HEADLESS_SHELL_PATH` |

Arquivos:
- `poc/remotion/out/poc-remotion.mp4`
- `poc/hyperframes/out/poc-hyperframes.mp4`
- `poc/comparacao/lado-a-lado.mp4` (Remotion em cima, HyperFrames embaixo)
- Folhas de contato e quadros lado a lado em `research/evidencias/`

**Conclusão verificada:** com o mesmo spec, **o motor não altera o resultado visual**. As diferenças
entre os dois são de produtividade, ferramental, licença e manutenção, não de qualidade de imagem.

## 3. Falhas, dificuldades e o que foi corrigido

1. **Paralaxe automática: falha mais grave.**
   - v1, com fatores 0,35/0,70/1,00: o deslocamento entre planos expôs o preenchimento do fundo
     (manchas cinzentas) e duplicou a cúpula. Ver `evidencias/remotion-v1-paralaxe-forte.jpg`.
   - v2, com fatores 0,80/0,92/1,00: melhorou, mas ainda havia borrões nas bordas
     (`paralaxe-v2-t8.5.jpg`).
   - v3, com máscara dilatada no mesmo deslocamento: **piorou**, porque a área preenchida cresceu
     (`paralaxe-v3-mascara-dilatada-t8.5.jpg`).
   - Final, com máscaras de 71/41 px e fatores 0,90/0,96/1,00: aceitável em movimento, mas **ainda há
     resíduos** perto do letreiro "JORNAL DO COMMERCIO" e nos telhados (`paralaxe-final-t8.5.jpg`).
   - **Causa:** o inpainting clássico (OpenCV Telea) borra, e o modelo de profundidade erra em fachadas
     planas e letreiros.
   - **Conclusão:** paralaxe automática serve de **rascunho**. Para entrega, as camadas precisam de
     revisão manual, ou de inpainting generativo, que conflita com a regra "nunca imagem gerada por IA"
     do portal. Isso é decisão editorial sua.
2. **Mapa em zoom alto.** Os dados em 1:50m ficam poligonais no zoom de cidade. O destaque do Brasil
   ocupa o quadro inteiro e perde a função. O mapa está **correto e limpo, mas ainda não tem acabamento
   de referência**: faltam relevo, hidrografia, cidades vizinhas, textura cartográfica e uma escala.
   Precisa de dados 1:10m, de uma camada de basemap assada e de regras de "quando trocar o nível de
   detalhe".
3. **Pulso do pino.** Ele não ficou igual nos dois motores, porque usei *keyframes* de opacidade no
   GSAP e uma fórmula própria no Remotion. Isso mostra que **o spec precisa descrever a curva**, não só
   o horário, para garantir paridade.
4. **Wikimedia limitou as consultas da API (HTTP 429).** Resolvido com espera e novas tentativas
   (`tools/wm.py`), com um user-agent identificando o script.
5. **HyperFrames:** imagens acima de 2 MB não são embutidas no bundle, o que só gera aviso. O lint
   pede uma sub-composição por cena, e eu fiz arquivo único por rapidez.
6. **Não testado:** áudio e narração (sem locução disponível; não usei TTS pago), sincronização por
   palavra (só o esqueleto `narracao_referencia`), motion blur, basemap MapLibre e render em nuvem.

## 4. Avaliação honesta da qualidade
- **O que já está no nível pretendido [H]:** a tipografia (hierarquia, revelação por máscara, contagem
  em pt-BR, fonte visível), as curvas de movimento sem "cara de template", a transição pino → foto e a
  consistência entre cenas dada pelos tokens.
- **O que não está:** a paralaxe (artefatos), o mapa (pobre em informação no zoom final), a ausência de
  som e o fato de os créditos estarem pequenos demais para celular.
- **Não estou declarando qualidade profissional.** O vídeo renderiza e é consistente, mas, pelos
  critérios da sua referência, ainda é um **esboço técnico**.
