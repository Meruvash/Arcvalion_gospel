# Comparação de arquiteturas

## Arquiteturas avaliadas
- **A — Remotion + bibliotecas** (d3-geo, MapLibre, `@remotion/*`, catálogo Opus como referência).
- **B — HyperFrames + GSAP + Herk Edit Kit** (cartões e skills do Herk).
- **C — OpenMontage como pipeline principal**, com componentes especializados.
- **D — Híbrida proposta:** um **spec editorial neutro de motor** (JSON: roteiro, *cues*, tokens,
  cenas, fontes) → **HyperFrames** como motor de render e de checagem → uma biblioteca **própria** de
  cenas documentais. Pré-processadores locais cuidam de mapas (d3 e MapLibre assado), 2.5D (profundidade
  com retoque) e áudio (ffmpeg). Do Herk, do OpenMontage e do video-editing aproveitam-se **processos**,
  não estéticas.
- **D′ — a mesma híbrida com Remotion como motor**, considerada como alternativa.

## Critérios e pesos
Qualidade visual potencial 30% · Automação 20% · Reutilização 15% · Integração com Claude Code 15% ·
Manutenção 10% · Custo operacional 10%. Notas de 0 a 10.

**Sobre as notas:** não são benchmark. São julgamentos apoiados nas evidências citadas. Onde a
evidência é a PoC, digo; onde é só código ou documentação, também. A e B foram medidas na PoC; C não
foi executada; D e D′ são projeções.

| Critério (peso) | A Remotion | B HF+GSAP+Herk | C OpenMontage | D Híbrida (HF) | D′ Híbrida (Remotion) |
|---|---|---|---|---|---|
| Qualidade potencial (30%) | **9** | **9** | 6 | **9** | **9** |
| Automação (20%) | 9 | 9 | 8 | 9 | 9 |
| Reutilização (15%) | **9** | 7 | 6 | 8 | **9** |
| Claude Code (15%) | 8 | **9** | 7 | **9** | 8 |
| Manutenção (10%) | **8** | 6 | 4 | 7 | **8** |
| Custo (10%) | 7* | **10** | 5 | **10** | 7* |
| **Total ponderado** | **8,55** | **8,50** | **6,25** | **8,75** | **8,55** |

\* O 7 do Remotion vale para o caso **com** Company License (organização com fins lucrativos e mais de
3 funcionários). Se o projeto se enquadrar na licença gratuita (pessoa física, ONG ou até 3
funcionários), a nota vira 10 e A e D′ sobem para 8,85. **Essa é a principal decisão em aberto, e
depende de você.**

## Justificativas

### Qualidade visual potencial
- **A = B = 9 (PoC).** Com o mesmo `spec.json`, as duas renderizaram o mesmo filme, com SSIM médio de
  0,969 e mínimo de 0,920 (no quadro 7,13 s, na paralaxe). As diferenças são de arredondamento de
  subpixel e do pulso do pino. Os dois motores rodam qualquer coisa que o Chrome desenha (SVG, canvas,
  WebGL, three.js), então o teto de qualidade é o mesmo. O que limita é o design e o insumo.
- **B teria 9 pela mesma razão**, mas usar os **cartões do Herk** puxaria para baixo (eu daria 6) por
  dois motivos: o estilo "vox-explainer" é derivado da identidade Vox, e os cartões são para
  talking-head. Por isso B fica em 9 só se usar HF+GSAP sem adotar os cartões.
- **C = 6.** O `remotion-composer` traz cortes genéricos (`stat_card`, `bar_chart`, `hero_title`), sem
  mapa geográfico real nem 2.5D. O pipeline documental é recuperação de footage de bancos, em beta. Os
  exemplos destacados são generativos (Veo, Kling), o oposto do que você quer [V código; D exemplos].

### Automação
- **A e B, 9 (PoC).** Render por CLI, determinístico, 15 s em 54 a 81 s numa máquina de 4 vCPUs sem
  GPU. Os dois têm render em nuvem: Lambda no Remotion; `aws-lambda` e `gcp-cloud-run` no HF.
- **C, 8.** Orquestra pesquisa → roteiro → ativos → edição com orçamento e checkpoints [V], mas depende
  de dezenas de provedores, e cada etapa automática dele é uma que você quer controlar editorialmente.

### Reutilização
- **A, 9.** Componentes React tipados, com props validadas pelo TypeScript. O typecheck pegou zero erros e
  forçou contratos claros. Existe um mercado de componentes (Opus, MIT; video-shotcraft).
- **B, 7.** As sub-composições HTML são reutilizáveis (registry com 210 blocos e 239 componentes), mas
  sem tipos. Os parâmetros passam por `data-var-*` e variáveis CSS. É mais frágil para uma biblioteca
  grande [H].
- **D, 8.** A reutilização fica no **spec** e nos **pré-processadores** (Python e Node independentes do
  motor), o que compensa parte da falta de tipos do HF. Projeção.

### Integração com Claude Code
- **B e D, 9 (PoC).** O `hyperframes check --json` devolveu achados acionáveis, cada um com dica de
  correção: legibilidade em celular, contraste AA e estrutura. Esse tipo de *feedback* fecha o ciclo do
  agente, porque ele vê o que fez sem depender de um humano para cada quadro. As skills e o plugin são
  oficiais.
- **A, 8.** Tem plugin e skills oficiais, e o TypeScript dá um ciclo rápido. Não encontrei checagem
  equivalente de legibilidade, contraste ou área segura, que teríamos de escrever.
- **C, 7.** Tem instruções para agentes, mas a superfície (158 skills, 222 ferramentas) consome
  contexto e diluiria as regras editoriais do seu projeto.

### Manutenção
- **A, 8.** Seis anos de vida, versão 4 estável, releases quase diárias.
- **B, 6 e D, 7.** O HyperFrames tem oito meses e está na 0.9.x: houve dezenas de versões entre a
  0.7.109 (fixada no Herk) e a 0.9.30. Espero quebras de API até a 1.0 [H]. A telemetria vem ligada.
  Há incentivo comercial da HeyGen (app Pro). Em D o risco cai porque o spec é neutro de motor: a PoC
  provou que o mesmo spec roda em Remotion.
- **C, 4.** É AGPL, e ser tão grande e mudar tanto (o último commit adiciona mais um provedor pago)
  pesa na manutenção.

### Custo operacional
- **B e D, 10.** HF é Apache-2.0. GSAP é grátis inclusive para uso comercial, mas sob licença própria
  da Webflow, que pode alterá-la. MapLibre, d3, Natural Earth e Depth-Anything-Small são abertos.
  Render local.
- **A e D′, 7 ou 10.** Depende da Company License (ver nota acima).
- **C, 5.** Por padrão chama APIs pagas (orçamento padrão de US$ 1 por vídeo no pipeline documental);
  a AGPL obriga a abrir o código modificado se o sistema for oferecido como serviço.

## Soluções híbridas consideradas e descartadas
- **OpenMontage orquestrando HF ou Remotion:** herdaria a AGPL e o viés generativo sem trazer
  componente documental pronto.
- **Remotion para compor + HF para cenas** (como o AIEV): dois motores para manter sem ganho de
  qualidade (a PoC mostra paridade).
- **After Effects + GEOlayers via MCP** (como Johnny Harris): a melhor qualidade por plano hoje, mas
  com assinatura Adobe, plugin pago, automação frágil e nada versionável no Git. Pode ser o
  "escape manual" para planos especiais.

## Veredito
- As duas mais promissoras, que foram para a PoC, são **A (Remotion)** e **B (HyperFrames + GSAP)**,
  usando de B apenas o motor e o GSAP, sem os cartões do Herk.
- A recomendação é **D**: spec neutro de motor, com HyperFrames como motor principal. A troca para
  **D′** (Remotion) deve acontecer se: (1) você precisar de tipagem forte numa biblioteca grande; ou
  (2) o HyperFrames quebrar compatibilidade de forma onerosa antes da 1.0; ou (3) a licença do
  Remotion for gratuita para você **e** você preferir maturidade a ferramentas de checagem.
