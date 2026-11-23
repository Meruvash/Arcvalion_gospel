# Evidências do Reel Novela Visual padrão

Auditoria das fórmulas de `REEL_NOVELA_VISUAL_PADRAO.md`, feita em 23/11/2026.
Dados brutos em `docs/video/pesquisa/reel_novela/`. Para reproduzir tudo, com os mesmos sorteios pela semente 42:

```bash
python3 tools/video/analisar_visual.py <video> metricas.json --fps 2
python3 tools/video/validar_medicao.py <video> <pasta> --seed 42
```

## 0. Natureza das fórmulas

**Elas não foram extraídas de texto, roteiro ou script.** A fonte é o sinal do vídeo: pixels, mudanças de cena e áudio de
*Married Into a Wealthy Family by Mistake* (https://youtu.be/iqlSvK0sH60, 5.030 s, cópia 480×854 baixada pelo
`tools/youtube/baixar.mjs`). Por isso o protocolo é o de **medição de sinal com validação**, não o de mineração de texto:

1. **Proveniência:** cada número aponta para o código que o produz e para o dado bruto.
2. **Reprodutibilidade:** o cálculo foi refeito do zero e conferido.
3. **Validação dos detectores** contra anotação manual (padrão-ouro), com precisão e revocação.
4. **Incerteza:** intervalos de confiança de 95%.
   - Bootstrap em blocos de 1 minuto, porque quadros vizinhos são correlacionados e reamostrar quadro a quadro daria IC estreito demais.
   - Wilson para proporções.
5. **Teste de ajuste** do modelo de distribuição (KS e AIC) contra alternativas.
6. **Sensibilidade** ao parâmetro livre (limiar de corte).
7. **Estabilidade interna:** primeira metade contra segunda.
8. **Classificação honesta** de cada afirmação:
   - **[M]** medido por algoritmo;
   - **[V]** medido e validado manualmente;
   - **[E]** estimativa visual numa amostra pequena;
   - **[D]** decisão ou proposta nossa, não medida.

Limite de quem anotou: a anotação manual foi feita por mim (Claude) olhando as pranchas, um anotador só. Não há concordância
entre anotadores. As pranchas estão fora do repositório porque são quadros de obra de terceiros; regenere-as com o comando acima.

## 1. Reprodutibilidade

Recalculado do zero com `validar_medicao.py`, independente da primeira passada:

| Medida | 1ª passada | Recalculado | Igual? |
|---|---|---|---|
| Cortes (limiar 0,30) | 1.798 | 1.798 | sim |
| Mediana do plano | 2,43 s | 2,43 s | sim |
| Cortes por minuto | 21,40 (média por minuto) | 21,45 (total ÷ duração) | sim (diferença de definição) |
| Planos < 2 s | 37,3% | 37,3% | sim |
| Planos > 6 s | 5,2% | 5,2% | sim |

## 2. Validação dos detectores contra anotação manual

| Detector | Amostra | Resultado | IC 95% (Wilson) |
|---|---|---|---|
| Corte: precisão (só claros) | 24 cortes sorteados, antes e depois | 21/24 = 0,875 (os 3 restantes são duvidosos, nenhum é erro grosseiro) | 0,69 – 0,96 |
| Corte: precisão (claros + duvidosos) | idem | 24/24 = 1,00 | 0,86 – 1,00 |
| Corte: revocação | 2 janelas de 12 s, quadro a cada 0,25 s | 10/11 cortes claros (perdeu 402,15 s, após movimento borrado) | 0,62 – 0,98 |
| Legenda: precisão | 48 quadros sorteados | 30/31 = 0,968 (falso positivo: pulseira de brilhantes) | 0,84 – 0,99 |
| Legenda: revocação | idem | 30/30 = 1,00 | 0,89 – 1,00 |
| Legenda: prevalência real | idem | 30/48 = 62,5% | 48% – 75% |

Leitura:
- O detector de corte é confiável para ritmo médio.
- Ele subconta levemente cortes escondidos em movimento rápido, então o ritmo real é igual ou um pouco mais rápido que o medido.
- O detector de legenda é muito bom.

## 3. Incerteza das medidas principais (bootstrap em blocos de 1 min, 2.000 réplicas)

| Medida | Valor | IC 95% |
|---|---|---|
| Mediana da duração do plano | 2,43 s | 2,33 – 2,57 s |
| Fração de planos < 2 s | 37,3% | 34,5% – 40,2% |
| Cortes por minuto (média) | 21,4 | 20,5 – 22,4 |
| Luminância média | 104,1 | 101,7 – 106,4 |
| Saturação média | 0,304 | 0,290 – 0,318 |
| Temperatura R − B | +22,6 | +20,4 – +24,7 |

## 4. Teste do modelo de duração de plano (n = 1.779)

| Modelo | Parâmetros | KS (crítico 0,032 a 5%) | AIC |
|---|---|---|---|
| Log-normal | μ = 0,847, σ = 0,647 | 0,036 | 6.516 |
| **Gama** | k = 2,40, θ = 1,18 s | 0,039 | **6.495** |
| Exponencial | λ = 0,354 | 0,209 | 7.257 |

Conclusões (e **correção** do que estava escrito):
- A exponencial está descartada: o corte não é aleatório e sem memória.
- **Nenhum modelo passa no KS a 5%.** Com n = 1.779, o teste pega desvios pequenos nas pontas. A afirmação anterior "D segue
  uma log-normal" estava forte demais.
- O AIC favorece a **gama** (ΔAIC = 21, evidência forte); o KS favorece levemente a log-normal. Os dois descrevem bem o
  miolo da distribuição.
- **Fórmula adotada:** sortear pelos **quantis medidos** (transformação inversa), que não depende de modelo. A gama fica como
  forma fechada. Ver a seção 2 do padrão.

## 5. Sensibilidade ao limiar de corte

| Limiar | Cortes | Mediana | Cortes/min | < 2 s | > 6 s |
|---|---|---|---|---|---|
| 0,25 | 1.891 | 2,33 s | 22,6 | 40,8% | 4,8% |
| **0,30 (adotado)** | 1.798 | 2,43 s | 21,5 | 37,3% | 5,2% |
| 0,40 | 1.595 | 2,66 s | 19,0 | 33,8% | 8,5% |

A mediana varia ±0,2 s e os cortes por minuto ±2. As faixas do padrão (1,9 a 3,0 s e 17 a 26 cortes/min) cobrem essa
variação. A fração > 6 s é a mais sensível: no limiar 0,40 ela sai da faixa (8,5% > 8%). **Ao conferir um vídeo nosso, use
sempre o limiar 0,30.**

## 6. Estabilidade: primeira metade × segunda metade

| Medida | 1ª metade | 2ª metade |
|---|---|---|
| Cortes por minuto | 23,4 | **19,5** |
| Mediana do plano | 2,33 s | 2,63 s |
| Luminância | 104,2 | 104,1 |
| Saturação | 0,300 | 0,309 |
| Temperatura | +21,0 | +24,0 |

A cor é estável. **O ritmo desacelera cerca de 17%** da primeira para a segunda metade, e a média global esconde isso. O vídeo é
uma compilação de episódios (cartela "TO BE CONTINUED" em 4.466,9 s). Se a desaceleração acontece dentro de cada
episódio ou só entre episódios, **não foi medido**.

## 7. Classificação de cada afirmação do padrão

| Afirmação | Classe | Evidência |
|---|---|---|
| Quadro 9:16, 30 fps | [M] | ffprobe |
| Duração do plano (quantis, gama) | [V] | seções 2, 4 e 5 |
| 21,4 cortes/min, 37% < 2 s, 5% > 6 s | [V] | seções 2, 3 e 5 |
| Primeiro corte a 0,6 s | [M] | `cortes_brutos.json` (n = 1 vídeo) |
| Desaceleração entre metades | [M] | seção 6 |
| Luminância, contraste, saturação, temperatura, colorido | [M] | IC na seção 3; sem padrão-ouro manual (são medidas físicas diretas) |
| Paleta de 6 cores | [M] | k-means, semente 7; a ordem dos pesos pode variar ±2 pontos com outra semente (não testado) |
| Acentos vermelho, dourado, azul-marinho, creme | [E] | leitura visual das pranchas |
| Fórmula do acento (≤ 10% da área, saturação ≥ 2×) | **[D]** | proposta minha, **não medida** |
| Proporção de tipos de plano | [E] | 24 quadros: uma pessoa 11/24 (IC 28%–65%), duas 6/24 (12%–45%), grupo 6/24 (12%–45%) |
| Olhos a ~0,30 H | [E] | leitura visual; o detector de pele falhou (confunde bege e madeira) |
| Antagonista ao fundo desfocado; cenário rico × pobre | [E] | pranchas; frequência não medida |
| Plano de revelação subindo da mão ao rosto | [E] | 1 caso (536,5 – 542 s); frequência não medida |
| Movimento (diferença entre quadros) | [M] | sem validação manual |
| Legenda em ~63–70% dos quadros | [V] | 62,5% manual (48 quadros), 70,8% automático (120 quadros) |
| Legenda: topo a 0,69 H, largura 0,62 W | [M] | detector validado (seção 2) |
| Legenda: 2 estilos (A negrito condensado sem pontuação ≈ 83%; B regular com pontuação ≈ 17%) | [V] | 5/30 com estilo B (IC 7%–34%); **corrige** "sem ponto final" como regra geral |
| Legenda ≤ 35 caracteres por linha | **[D]** | estimado de 2 quadros, **não medido** |
| Plano de fala 2,5–4 s, reação 1–2 s | **[D]** | impressão qualitativa, **não medida** |
| Marca no canto inferior esquerdo | [E] | visível em todas as pranchas |
| −7,9 LUFS, LRA 13 | [M] | filtro ebur128 do ffmpeg |
| Alvo −11 LUFS | **[D]** | decisão nossa (a fonte é alta demais) |
| Abertura mais clara e menos saturada (×1,15 e ×0,6) | [M], n = 1 | só os 3 s iniciais de um vídeo: tendência, não regra |
| Nota de aderência A ≥ 0,80 | **[D]** | corte escolhido por nós; calibrado só na fonte (A = 0,93). Não há ainda vídeo "fora do padrão" para medir a discriminação |

## 8. O que falta para virar padrão robusto

1. Medir mais 3 ou 4 novelas de canais diferentes e recalcular as faixas como variação **entre vídeos**, não entre quadros.
2. Medir 3 ou 4 Reels que **não** são novela, para provar que a nota A separa um do outro.
3. Um segundo anotador independente nas pranchas, para medir a concordância (kappa de Cohen).
4. Medir o ritmo por episódio (onde estão as cartelas) para entender a desaceleração.
5. Medir de verdade a duração de plano de fala × reação, cruzando cortes com a presença de legenda.
