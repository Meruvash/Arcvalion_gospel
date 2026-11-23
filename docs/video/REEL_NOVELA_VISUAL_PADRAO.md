# Reel Novela Visual padrão

Referência visual medida para Reels no formato de "novela curta" vertical. Versão 1.1, 23/11/2026.
Evidências, testes e classificação de cada afirmação em `REEL_NOVELA_VISUAL_EVIDENCIAS.md`. As marcas indicam a origem:
**[V]** medido e validado manualmente · **[M]** medido · **[E]** estimativa visual em amostra pequena · **[D]** decisão nossa, não medida.

- **Fonte medida:** *Married Into a Wealthy Family by Mistake — Now I'm Spoiled Rotten* (canal com marca "Whisper of Romance"),
  https://youtu.be/iqlSvK0sH60, versão completa de 83min50s: 1.779 planos, 10.060 quadros analisados a 2 fps, 240 quadros
  em resolução cheia para legenda e uma folha de contato de 24 quadros para leitura visual.
- **Ferramentas:** `tools/video/analisar_visual.py` (mede) e `tools/video/checar_reel_novela.py` (dá a nota).
  Os números-alvo estão em `REEL_NOVELA_VISUAL_PADRAO.json`.
- **Direitos:** o vídeo é de terceiros e foi baixado só para medir. Nada dele (quadro, áudio, texto, personagem) entra em
  vídeo nosso. Copiamos **proporções e ritmos**, não conteúdo.
- **Imagem:** os rostos e cenários da fonte têm aparência de imagem gerada por IA. Isso não muda as regras da casa:
  **nunca imagem gerada por IA em matéria** (CLAUDE.md). O padrão se aplica a material filmado, de arquivo licenciado ou às
  pinturas animadas em código da linha de vídeo do portal.

---

## 1. Formato

| Item | Fórmula / valor |
|---|---|
| Quadro | 9:16, **1080 × 1920**, 30 fps |
| Área segura de texto | 0,10 H ≤ y ≤ 0,80 H (a base fica para a interface do app e a marca) |
| Marca | canto inferior esquerdo, y ≈ 0,95 H, largura ≈ 0,45 W, translúcida, fixa o vídeo todo |

## 2. Ritmo de corte

**[V]** Duração de cada plano D, em segundos (n = 1.779). Quantis medidos, com IC 95% da mediana entre 2,33 e 2,57 s:

| p10 | p25 | p50 | p75 | p90 |
|---|---|---|---|---|
| 1,00 | 1,57 | 2,43 | 3,67 | 5,00 |

**Fórmula de geração (sem depender de modelo): transformação inversa pelos quantis medidos.**

```
u_i ~ Uniforme(0,1)
d_i = interpolação linear de u_i em {(0,10 ; 1,00) (0,25 ; 1,57) (0,50 ; 2,43) (0,75 ; 3,67) (0,90 ; 5,00)}
      para u_i < 0,10 use 0,8 s; para u_i > 0,90 interpole de 5,0 a 7,0 s
somar d_i até alcançar T; o último plano absorve a sobra
N ≈ T / 2,83          →  Reel de 60 s ≈ 21 planos · 90 s ≈ 32 planos
```

Forma fechada aproximada: **D ~ Gama(k = 2,40 ; θ = 1,18 s)**, com média kθ = 2,83 s e moda (k−1)θ = 1,65 s. A gama venceu a
log-normal no AIC (ΔAIC = 21); nenhum dos dois modelos passa no teste KS a 5%, então use a gama só como aproximação.
(Versão 1.0 dizia "log-normal": corrigido pela auditoria.)

**[M] O ritmo desacelera:** 23,4 cortes/min na primeira metade e 19,5 na segunda. Para Reel curto, use o ritmo da primeira
metade nos primeiros 30 s.

| Medida | Alvo | Faixa aceita |
|---|---|---|
| Cortes por minuto | 21,4 | 17 – 26 |
| Planos com menos de 2 s | 37% | 28% – 47% |
| Planos com mais de 6 s | 5% | 0% – 8% |
| Primeiro corte | 0,6 s | ≤ 1,5 s |

Regra prática: plano **acima de 6 s só 1 em cada 20** [V]. Plano de **fala** de 2,5 a 4 s e de **reação** (olhos
arregalados, mão no rosto) de 1 a 2 s logo depois de cada revelação **[D]**: impressão visual, ainda não medida.

## 3. Cor e luz

Valores por quadro, escala 0–255 para luminância e 0–1 para saturação:

| Medida | Alvo (média) | Faixa aceita | p10 – p90 da fonte |
|---|---|---|---|
| Luminância Y = 0,299R + 0,587G + 0,114B | 104 | 92 – 118 | 75 – 130 |
| Contraste σ_Y | 57 | 50 – 64 | 44 – 70 |
| Saturação S = (max−min)/max | 0,30 | 0,24 – 0,37 | 0,18 – 0,42 |
| Temperatura R − B | +22,6 | +11 – +34 | +2 – +43 |
| Colorido (Hasler-Süsstrunk) | 33 | 26 – 39 | 21 – 46 |

Leitura: imagem **média-clara, quente e de saturação moderada**. Quase nunca fria (p10 = +2): o branco puxa para o creme.
Luz suave, frontal ou lateral, sem sombra dura, com fundo desfocado.

**Paleta dominante** (k-means, 6 cores, peso = fração dos pixels):

| Cor | Peso | Papel |
|---|---|---|
| `#191313` quase preto quente | 21% | ternos, cabelo, sombras |
| `#9a8375` bege-taupe | 20% | pele em meia-luz, paredes |
| `#755c4e` marrom médio | 18% | cabelo, madeira |
| `#49352d` marrom escuro | 17% | fundos de interior |
| `#b4a8a3` cinza-rosado claro | 16% | paredes, mármore |
| `#d6d6d9` branco frio | 8% | luzes, camisas |

**Acentos** (pouca área, muito significado): **vermelho** (vestido e batom da antagonista), **dourado** (riqueza: colunas,
lustres, portas), **azul-marinho** (homens de poder), **rosa e creme** (a protagonista).
Fórmula de acento **[D]** (proposta, não medida): área do acento ≤ 10% do quadro, saturação do acento ≥ 2 × a saturação média do quadro.

## 4. Enquadramento e encenação

**[E]** Leitura dos 24 quadros da folha de contato (amostra pequena; IC 95% de "uma pessoa" vai de 28% a 65%):

| Tipo de plano | Frequência |
|---|---|
| Uma pessoa (close ou plano médio-próximo, às vezes com ombro de outra em primeiro plano) | ≈ 46% |
| Duas pessoas (diálogo, confronto) | ≈ 25% |
| Grupo (festa, família, seguranças) | ≈ 25% |
| Detalhe (mãos, objeto) | ≈ 4% |

- **Olhos a ≈ 0,30 H** da borda superior (terço superior); rosto centralizado na horizontal, ocupando 50–65% da largura no close.
- **Profundidade encenada:** quando há conflito, o antagonista fica **ao fundo, desfocado**, atrás da protagonista em close.
- **Contraste social no cenário:** escritório, faxina e rua para a "pobre"; mármore, dourado, lustre e carro preto para a
  "rica". O cenário conta a virada sem precisar de fala.
- Movimento de câmera e de gente **moderado**: diferença média entre quadros a cada 0,5 s com mediana 17,8 (faixa 11 – 31).

## 5. Legenda (queimada no vídeo)

Medido em 240 quadros em resolução cheia:

| Medida | Valor |
|---|---|
| Quadros com legenda | **63–70%** [V] (62,5% na conferência manual de 48 quadros; 70,8% no detector) |
| Topo do bloco | **0,694 H** · base 0,746 H (sobre o peito do personagem, nunca na boca) |
| Largura do bloco | 0,62 W (máximo ≈ 0,80 W) |
| Linhas | 1 ou 2, centralizadas |
| Altura da linha | ≈ 0,026 H (≈ 50 px em 1920) → corpo da fonte ≈ 0,024 H (≈ 46 px) |
| Estilo [V] | branco puro, sem serifa, contorno ou sombra escura fina, sem caixa de fundo. **Dois estilos**: A, negrito condensado sem pontuação (≈ 83%), e B, regular com "?" e ponto (≈ 17%, IC 7%–34%) |
| Comprimento [D] | frase curta, ≤ 35 caracteres por linha (estimado de 2 quadros, não medido) |

Fórmula de posição: `y_topo = 0,69 · H`, `x_centro = W / 2`, `largura ≤ 0,80 · W`.
Na linha de vídeo do portal a legenda é **amarela** (regra do editor para os vídeos do agro); este padrão mede o branco da fonte.
Quem decide a cor de cada série é o editor.

## 6. Som

| Medida | Fonte | Alvo nosso |
|---|---|---|
| Loudness integrada | −7,9 LUFS [M] (muito alto) | **−11 LUFS** [D] (faixa −14 a −8) |
| Faixa de loudness (LRA) | 13 LU | 8 – 14 LU |

O app normaliza o volume; acima de −8 LUFS só se ganha distorção.

## 7. Abertura (primeiros 3 s)

Na fonte, a abertura é **mais clara e menos saturada** que o resto: Y 119 contra 104 e S 0,18 contra 0,30. O primeiro corte
vem em **0,6 s**. Fórmula: `Y_abertura ≈ 1,15 · Y_médio`, `S_abertura ≈ 0,6 · S_médio`, primeiro corte ≤ 1 s, com rosto
em close no primeiro ou no segundo plano.
(Medido num único vídeo: trate como tendência, não como lei.)

## 8. Nota de aderência (como conferir um vídeo nosso)

```bash
python3 tools/video/analisar_visual.py meu_reel.mp4 /tmp/m.json
python3 tools/video/checar_reel_novela.py /tmp/m.json
```

Para cada medida k com faixa [min_k, max_k] e largura L_k = max_k − min_k:

```
s_k = 1                          se min_k ≤ x_k ≤ max_k
s_k = max(0 , 1 − d_k / L_k)     fora da faixa (d_k = distância até a faixa)
A   = Σ w_k · s_k / Σ w_k        aprovado se A ≥ 0,80
```

Pesos: ritmo 3 (mediana do plano, cortes por minuto), 2 (frações de plano curto e longo, primeiro corte, luminância,
saturação, temperatura, presença e posição da legenda) e 1 (contraste, colorido, movimento, largura da legenda,
loudness, resolução).
Calibração: o próprio vídeo-fonte tira **A = 0,930**. Perde só na resolução, porque a cópia medida é 480 × 854, e no
volume, porque −7,9 LUFS fica acima do teto que adotamos.

## 9. Limites desta medição

Detalhe completo em `REEL_NOVELA_VISUAL_EVIDENCIAS.md`, seções 7 e 8.

- Um único vídeo-fonte: as faixas são do estilo desse canal. Para virar padrão geral, medir mais 3 ou 4 novelas e recalcular.
- A cópia medida é 480 × 854: as medidas de cor, ritmo e posição não dependem da resolução, mas detalhe fino de textura não foi medido.
- O detector de pele em YCbCr confunde pele com madeira e bege (deu 40% do quadro); por isso o enquadramento vem da
  leitura visual da folha de contato, não desse número.
- O detector de cena usa limiar 0,30: dissolvências lentas podem não contar como corte.
