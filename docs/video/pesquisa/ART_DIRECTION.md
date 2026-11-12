# Direção de arte — proposta de identidade audiovisual (Fase 5)

Nome de trabalho: **"Arquivo Aberto"**. É uma linguagem para webdocumentários históricos, políticos,
científicos e culturais, em que **o documento é o protagonista** e a animação existe para apontar,
medir e situar. É uma proposta original: não reproduz paleta, tipografia nem assinatura visual da Vox,
de Johnny Harris ou do EarnEdits.

## 1. Princípios
1. **Evidência antes de efeito.** Todo elemento animado é um documento, um dado, um lugar ou uma
   citação, com fonte visível na tela. Não há elemento decorativo sem função.
2. **Uma ideia por plano.** Um sujeito, um rótulo, uma fonte.
3. **A câmera explica.** O movimento sempre responde a "para onde olhar agora?". Sem bounce, sem
   overshoot, sem tremor.
4. **Material de arquivo é intocável.** Sem colorização, sem preenchimento generativo apresentado como
   original. Retoque de camada 2.5D só para esconder emendas, e documentado.
5. **Uma série, uma gramática.** Os mesmos tokens, curvas e componentes em todos os episódios. O que
   muda entre temas é só a cor de acento.

## 2. Diferenças deliberadas em relação às referências
Paleta de "papel" quente é convenção do gênero. O estilo `vox-explainer` do Herk usa `#efe9dc`, e o
nosso papel ficou próximo disso (`#EEE8DC`). Para não confundir as identidades, os traços abaixo são
nossos e devem ser mantidos:
- **Sem marcador azul nem contorno de "adesivo"**, que são as assinaturas associadas à Vox. O destaque
  é um **fio fino** (3 px) mais o **itálico serifado em cor de acento**.
- **Etiquetas em monoespaçada** (IBM Plex Mono) para tudo que é metadado: fonte, escala, data,
  crédito. É a marca "arquivo/ficha catalográfica" da série.
- **Movimento contínuo e suave** (sem stop-motion "on twos").
- **Mapas como prancha cartográfica**: grade, escala, fonte e projeção sempre declaradas no canto
  inferior.

## 3. Tokens (versão 0.1, os usados nas PoCs)
| Token | Valor | Uso |
|---|---|---|
| `paper` | `#EEE8DC` | fundo das pranchas |
| `paperShade` | `#E1D8C6` | painéis e planos de fundo secundários |
| `ink` | `#15171A` | texto principal, contornos |
| `inkSoft` | `#5A5F63` | legendas, metadados (**corrigir para ≥ 4,5:1**: o `check` mediu 4,25:1 em algum par) |
| `accent` | `#C23B22` (vermelhão) | um conceito por vídeo; temas podem trocar o acento (ex.: azul-petróleo para ciência) |
| `ocean` / `land` | `#E7E1D3` / `#CEC5B2` | mapa base, de baixo contraste para o destaque "acender" |
| Serifa | Newsreader (OFL) | títulos, números, citações; itálico para unidades e ênfase |
| Rótulo | IBM Plex Sans Condensed (OFL) | nomes de lugar, legendas |
| Metadado | IBM Plex Mono (OFL) | fonte, crédito, escala, data |
| `easeEnter` | `cubic-bezier(.22,1,.36,1)` | entrada de texto e elementos |
| `easeCamera` | `cubic-bezier(.65,0,.35,1)` | câmera, transições |
| Grão | textura procedural com semente, 6–14% em multiply | unifica foto, mapa e prancha |

## 4. Tipografia e legibilidade em celular
- Corpo mínimo de **28 px a 1080p**: é o piso do `check` do HyperFrames, cerca de 2,6% da altura. Os
  créditos de 15–17 px da PoC **não passam** e serão revistos para 22–24 px em mono, com o crédito
  completo também na descrição do vídeo.
- Títulos de 56–72 px, números-heróis de 160–200 px com algarismos tabulares, no máximo 2 linhas por
  quadro.
- Área de título segura de 80%, área de ação de 90%. Uma versão vertical (9:16) derivada do mesmo spec,
  com outra grade.
- Contraste de pelo menos 4,5:1 em todo texto; sobre foto, sempre com faixa de sombra.

## 5. Gramática de movimento
| Elemento | Duração | Curva | Regra |
|---|---|---|---|
| Entrada de texto (máscara) | 0,8–0,9 s | `easeEnter` | defasagem de 0,12–0,15 s entre linhas |
| Contagem numérica | 1,0–1,2 s | `easeEnter` | termina antes da palavra seguinte na narração |
| Câmera em foto | 5–8 s | `easeCamera` | deslocamento relativo entre planos de no máximo 4%; zoom de no máximo 10% |
| Zoom de mapa | 2–4 s | `easeCamera` + escala log | troca de nível de detalhe (1:110m → 1:50m → 1:10m → basemap) pela escala |
| Transição | 0,8–1,0 s | `easeCamera` | sempre motivada (lugar → foto, prancha → dado) |
| Segurar | ≥ 1,5 s | deriva linear de 1–3% | todo plano final de bloco respira |

## 6. Componentes da série (a desenvolver)
- **Prancha de mapa:** globo ou plano; destaque; pino; rota; coropleta; escala e fonte.
- **Foto 2.5D:** camadas, câmera, legenda e crédito.
- **Documento em close:** página escaneada; foco numa frase com fio de acento; citação literal com
  referência.
- **Número-herói** e **quadro de números** (como a PoC); **gráfico de barras e linha** com fonte.
- **Linha do tempo** horizontal com marcos.
- **Citação:** aspas em serifa grande, autor e data em mono.
- **Abertura e encerramento** da série, com a mesma assinatura sonora curta.

## 7. Som (proposta)
- Locução humana gravada; trilha discreta, com ducking de 8–12 dB sob a voz.
- Desenho de som mínimo: um "toque de papel" nas transições de prancha e um pulso grave no pino.
- Entrega em −14 LUFS integrado, com pico de −1 dBTP.
- Biblioteca de efeitos só com CC0, ou compradas com licença guardada no repositório.
