# Evidências do padrão de roteiro (Reel Novela)

Método e resultados de `REEL_NOVELA_ROTEIRO_PADRAO.md`, de 23/11/2026. Para reproduzir:

```bash
# baixar a legenda oficial em inglês (não fica presa a IP; sai até da nuvem do Claude Code)
#   @distube/ytdl-core: info.captionTracks → languageCode "en" (não a "en (auto)") → URL + "&fmt=json3"
python3 tools/video/analisar_roteiro.py legenda_en.json3 docs/video/pesquisa/reel_novela/roteiro_codificacao.json saida.json
```

Saída registrada: `docs/video/pesquisa/reel_novela/roteiro_metricas.json`. A transcrição completa é obra de terceiros e
**não fica no repositório**: o script a recria com `--transcricao`.

## 1. Método: análise de conteúdo dirigida

Segue o roteiro clássico de análise de conteúdo (pré-análise, codificação, inferência) com controles de reprodutibilidade:

1. **Corpus.** A trilha de legenda **manual** em inglês, enviada pelo canal; a trilha automática foi descartada.
   - Ela já tem marcação de tempo.
   - Veio com ruído de leitura automática: linhas de lixo, versões progressivas da mesma fala e palavras grudadas.
2. **Limpeza com regras explícitas**, contadas: 1.998 falas viram 1.839.
   - 116 linhas de lixo (menos de 2 letras ou sigla solta);
   - 21 versões progressivas (fica a mais completa);
   - 22 duplicatas.
   - Resultado: 11.274 palavras e 1.828 palavras distintas.
3. **Leitura integral.** As 1.839 falas foram lidas do começo ao fim, sem amostragem.
4. **Livro de códigos com definição operacional**, em `roteiro_codificacao.json`, campo `livro_de_codigos`, com 10 categorias:
   - PREMISSA, PLANTIO, HUMILHAÇÃO, ESCALADA, CHEGADA, REVELAÇÃO, PUNIÇÃO, AFETO, GANCHO e PAGAMENTO.
5. **Codificação.** 71 batidas em 11 ciclos; cada uma tem tempo e citação literal curta, como prova.
6. **Conferência automática da codificação.** O script procura cada citação na transcrição limpa, a até 20 s do tempo anotado,
   exigindo sobreposição de palavras ≥ 0,6.
   - Na 1ª rodada: **70/71**. Pegou um erro meu de tempo: "You a country bumpkin" estava em 1.166 s, e o certo é 1.193 s.
   - Corrigido, ficou **71/71**.
7. **Validação cruzada, independente da leitura humana.** Um léxico de status baixo, definido antes do teste, foi contado
   por algoritmo dentro e fora das janelas de humilhação codificadas.
   - A significância vem de um teste de permutação em blocos de 60 s (2.000 permutações), que preserva a dependência local.
8. **Medidas automáticas de linguagem:** palavras por fala, palavras por minuto, fórmulas verbais por expressão regular,
   nomes e perguntas.

## 2. Resultados

### Validação cruzada (a prova principal)

| | Status baixo por mil palavras |
|---|---|
| Dentro das janelas codificadas como humilhação/escalada | **14,81** |
| Fora delas | **5,03** |
| Razão | **2,94** |
| p (permutação em blocos de 60 s) | **0,0005** |

Leitura: o algoritmo, que não sabe onde marquei humilhação, acha o vocabulário de desprezo de classe concentrado exatamente
nesses trechos. A chance de isso acontecer por acaso é de 1 em 2.000.

### Batidas por tipo (71)

| Humilhação | Revelação | Afeto | Chegada | Punição | Escalada | Plantio | Gancho | Pagamento | Premissa |
|---|---|---|---|---|---|---|---|---|---|
| 14 | 11 | 10 | 9 | 8 | 6 | 5 | 4 | 3 | 1 |

### Tempos do ciclo na fonte (8 ciclos de "tapa na cara")

| Medida | Mediana | Faixa |
|---|---|---|
| Humilhação → chegada do protetor | 189 s | 50 – 411 s (n = 7) |
| Chegada → revelação | 97 s | 29 – 147 s (n = 4) |
| Humilhação → punição | 242 s | 69 – 556 s (n = 8) |
| Duração do ciclo | 312 s | 155 – 665 s |
| Intervalo entre punições | 581 s (~10 min) | 214 – 1.433 s |

Posição relativa das batidas (0 = 1ª humilhação, 1 = punição):

| Ciclo | Escalada | Chegada | Revelação |
|---|---|---|---|
| 2 | 0,68 | 0,65 | — |
| 3 | — | — | 0,89 |
| 4 | 0,78 | 0,89 | — |
| 5 | 0,65 | 0,47 | 0,96 |
| 6 | 0,69 | 0,73 | 0,47 (falsificação descoberta antes do clímax) |
| 7 | 0,74 | 0,85 | 0,92 |
| 8 | — | 0,73 | — |
| 11 | — | 0,94 | — |
| **Mediana** | **0,69** (n = 5) | **0,73** (n = 7) | **0,90** (n = 4) |

A escalada é a batida mais regular (0,65 a 0,78). A chegada varia mais.

### Linguagem

- 134,5 palavras por minuto; mediana de 6 palavras por fala (máximo 15).
- Uma fala a cada ~2,7 s, próximo do plano mediano de 2,43 s do padrão visual: é praticamente uma fala por plano.
- Perguntas: 99 de 688 falas (14,4%), contadas só no trecho final (a partir de ~54:30), único com pontuação na legenda.
- Menções: Kane 146, Mia 123, Alexander 63, Tom 43, Grandma 24, Sophie 22, Collins 20.
- Fórmulas verbais, com os primeiros tempos (mm:ss):

| Fórmula | Vezes | Onde |
|---|---|---|
| "How dare you" | 9 | 17:57, 27:05, 33:42, 49:36, 51:28, 53:49… |
| "Impossible" / "can't be" | 10 | 14:57, 20:09, 26:16, 28:03, 37:11, 37:32… |
| "Spare me" / "I was wrong" | 7 | 23:20, 24:40, 37:52, 37:54, 38:59, 59:02… |
| "Do you know who…" | 2 | 36:49, 54:50 |

### Motivos recorrentes (busca na transcrição)

- **Heroína recusa riqueza, 7 vezes:** 16:15, 22:41, 28:53, 31:16, 50:03, 74:39, 76:46.
- **Acusação de falsidade como motor da revelação** ("fake", "fraud", "counterfeit", "impersonate"): 19 falas.
  - Ciclos envolvidos: anel (20:15 – 26:39), falso CEO (37:43 – 37:58), Dior falsificado (45:00), esmeralda (48:30), quadro (76:19).

## 3. Classificação das afirmações do padrão

| Afirmação | Classe | Base |
|---|---|---|
| Ordem das batidas do ciclo | [C], validada por léxico [V] | 8/11 ciclos; razão de 2,94 com p = 0,0005 |
| Regra 70/30 e posições 0,69 / 0,73 / 0,90 | [M] sobre [C] | tabela acima; n entre 4 e 7, então são tendências |
| Inversão verdadeiro/falso | [C] | 4 de 8 ciclos; 19 falas de "fake/fraud" |
| Personagens-função | [C] | leitura integral |
| Plantar e pagar | [C] | 4 pares com tempo |
| 6 palavras por fala, 134 ppm, 14% de perguntas | [M] | script |
| Fórmulas verbais | [M] | regex; a contagem é de falas, não de cenas |
| Molde de 60 s e 90 s | **[D]** | projeção das proporções medidas num ciclo comprimido; **nunca testado com público** |
| Recomendações de uso no portal | **[D]** | linha editorial da casa |

## 4. Limites

- **Um único codificador** (Claude). Para padrão científico pleno falta um segundo codificador independente e o cálculo do
  kappa de Cohen sobre uma amostra de cenas.
- **Uma única obra.** Para generalizar o gênero, codificar mais 3 ou 4 novelas de canais diferentes com o mesmo livro de códigos.
- **A legenda não é o áudio.** A trilha manual tem erros de leitura ("a by thousand walnut year"); as contagens de palavras
  têm erro pequeno. A estrutura não é afetada: 71/71 batidas conferidas.
- **Os moldes de 60/90 s são extrapolação:** a fonte é uma novela de 84 min. Medir Reels curtos do gênero confirmaria
  as proporções na escala curta.
- **Pontuação:** só o trecho final da legenda tem "?" e "!"; a fração de perguntas vale para esse trecho.
