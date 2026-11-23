# Fórmulas da novela curta (medidas no modelo de 1 hora, 22–23/11/2026)

Base de todo roteiro de novela do outro Instagram. Os roteiros são escritos em JSON e passam por
`python3 tools/video/novela/auditar_novela.py roteiro.json` antes de ir ao editor. **Nenhum vídeo é gerado antes de o
editor ver o roteiro.**

## 1. De onde vêm os números
- **Modelo:** "【FULL】Married Into a Wealthy Family by Mistake", canal Whisper of Romantic, https://youtu.be/iqlSvK0sH60.
- **Fonte da medição:** a transcrição completa (11.538 palavras), lida pelo Virlo em 22/11/2026.
- **Script de medição:** `tools/video/novela/medir_modelo.py`. A transcrição não fica no repositório, por direito
  autoral.
- **Como foi medido:** cada um dos 12 ciclos de humilhação e virada foi marcado por uma frase-âncora de início, uma de
  virada e uma de fim. A posição é dada em **% do texto**, que serve de aproximação do tempo. O download do vídeo foi
  bloqueado, então não há minutagem real.
- **Contagens por ciclo:** dinheiro, insulto, súplica, proteção, prova (fake/real) e descrença, por expressões fixas.
  Elas mostram a presença e a intensidade de cada elemento, não uma contagem exata de cenas.
- **Limite honesto:** "comprovado" aqui quer dizer **a estrutura que esse sucesso usa, medida**. Não conseguimos os
  números de audiência do vídeo: o Virlo só lê Shorts, e o canal não tem nenhum. A prova de desempenho no nosso
  público virá dos testes publicados.

## 2. O que a medição mostrou

| Ciclo | Início | Virada | Fim | Palavras | Insultos antes da virada | Descrença | Prova | Súplica | Proteção |
|---|---|---|---|---|---|---|---|---|---|
| C1 casamento errado | 0,4% | 2,4% | 2,8% | 275 | 0 | 0 | 0 | 0 | 0 |
| C2 elevador do presidente | 3,4% | 3,7% | 4,0% | 74 | 0 | 0 | 0 | 0 | 0 |
| C3 prima no escritório | 6,1% | 8,0% | 8,1% | 234 | 2 | 0 | 0 | 0 | 0 |
| C4 avó × neto (ironia) | 9,1% | 10,3% | 10,4% | 130 | 0 | 0 | 0 | 0 | 0 |
| C5 ex na mansão | 11,2% | 13,7% | 15,5% | 481 | 3 | 0 | 2 | 0 | 0 |
| **C6 anel de poder** | 19,7% | 25,9% | 32,4% | 1.463 | 6 | 4 | 14 | 3 | 3 |
| **C7 falso presidente** | 36,9% | 39,5% | 43,7% | 791 | 2 | 3 | 4 | 3 | 3 |
| **C8 reunião de turma** | 47,3% | 54,5% | 57,7% | 1.191 | 10 | 1 | 9 | 0 | 2 |
| **C9 câmara de comércio** | 59,6% | 66,2% | 66,4% | 763 | 8 | 1 | 2 | 0 | 0 |
| C10 prima rebaixada | 67,6% | 68,7% | 69,5% | 221 | 1 | 0 | 0 | 2 | 0 |
| **C11 mãe desconfia** | 82,2% | 85,4% | 88,5% | 726 | 1 | 0 | 0 | 0 | 0 |
| **C12 ex volta + revelação** | 91,9% | 98,4% | 99,8% | 966 | 1 | 13 | 1 | 2 | 3 |

Em negrito estão os **6 ciclos-pilar**, os de mais de 700 palavras.

**As 6 leis que saem da tabela:**
1. **Abertura em rajada.** Os 4 primeiros ciclos cabem nos primeiros 10% do vídeo, com um ciclo a cada 2 a 3%. Depois
   os ciclos ficam maiores, com intervalo mediano de 8,5%. O conflito começa com 0,4% do vídeo, junto com o primeiro
   número em dinheiro ("cirurgia de 100 mil dólares").
2. **A virada vem depois do meio do ciclo.** Ela cai a 64% do ciclo na mediana (média 69%), com quartis em 49% e 93%.
   Nos pilares, a mediana é 60%. A humilhação ocupa a maior parte do tempo, e a virada é curta e seca.
3. **Humilhação em escada:** há insulto antes da virada nos 6 pilares, com mediana de 4 por ciclo.
4. **Descrença:** em 5 dos 6 pilares, a vítima diz a verdade e é chamada de mentirosa antes da virada.
5. **Objeto-prova:** em 5 dos 6 pilares há um objeto que o vilão chama de falso ou barato e que decide tudo (o anel,
   a pulseira, o convite, o quadro).
6. **Poder escondido:** nos 6 pilares, o poder do humilhado já existia e só é revelado. O marido é o dono, e a
   velhinha é a presidente.

**Outros dados:**
- **Queda do vilão:** acontece nos 6 pilares. Em 3 ele implora ("Spare me"); nos outros é punido.
- **Proteção ou recompensa:** aparece em 4 dos 6 pilares ("My wife…", "Who dares…").
- **Testemunhas:** em 4 dos 6 pilares a humilhação é pública (escritório, restaurante, turma, banquete).
- **Dinheiro:** há número em dinheiro em 3 dos 6 pilares e em 5 dos 12 ciclos.

## 3. A fórmula do Reels (um ciclo-pilar em 60 a 90 s)

Cada Reels é **um ciclo-pilar completo** e termina em gancho, como um episódio:

```
GANCHO (0–3 s) → HUMILHAÇÃO ×2 ou mais, em escada, diante de testemunhas → PROVA DESPREZADA → DESCRENÇA
→ [VIRADA entre 48% e 81% do tempo, alvo 60%] REVELAÇÃO com o mesmo objeto → LEI com fonte
→ QUEDA do vilão → PROTEÇÃO ou RECOMPENSA → fala do Dr. Pelicioni → GANCHO FINAL ("PARTE 2")
```

**Pesos do verificador.** Cada peso é a fração dos 6 pilares em que o elemento aparece. A aprovação pede nota de 0,85
ou mais.

| Item | Regra | Peso |
|---|---|---|
| F1 | 2 ou mais ataques ou humilhações antes da virada | 1,00 |
| F2 | descrença antes da virada | 0,83 |
| F3 | o mesmo objeto é desprezado antes e é decisivo depois | 0,83 |
| F4 | virada entre 48% e 81% da duração | 1,00 |
| F5 | queda do vilão depois da virada | 1,00 |
| F6 | proteção ou recompensa | 0,67 |
| F7 | número em dinheiro dito ou escrito | 0,50 |
| F8 | humilhação diante de testemunhas | 0,67 |
| F9 | primeiro ataque até 10% do tempo | 1,00 |
| F10 | poder escondido revelado | 1,00 |

**Obrigatórias.** Se qualquer uma falhar, o roteiro reprova:

| Item | Regra |
|---|---|
| O1 | aviso "dramatização" |
| O2 | gancho de 0 a 3 s |
| O3 | toda LEI com link da fonte oficial |
| O4 | nenhuma batida com mais de 10 s |
| O5 | as falas cabem no tempo: áudio até 2,9 palavras/s, texto até 4 palavras/s de leitura |
| O6 | termina em GANCHO_FINAL |
| O7 | linha do tempo sem buraco |

## 4. As premissas do modelo, traduzidas para o rural

| Premissa do modelo (ciclo) | O que é no modelo | Tradução rural/jurídica |
|---|---|---|
| Objeto desprezado é o poder (C6) | o anel "de prata" é o anel de poder do grupo | o livro velho do pai, o contrato, o recibo, a escritura |
| Falso poderoso desmascarado (C7) | o "presidente" do restaurante é um impostor | o "doutor" comprador é corretor; o "dono" não registrou |
| O humilde tem o poder (C4, C9) | a velhinha catadora é a presidente | o arrendatário, o caseiro ou a irmã da roça têm o direito na lei |
| Ex volta quando a vítima sobe (C12) | o ex quer voltar depois da virada | o irmão ou vizinho que humilhou volta pedindo acordo (bom para a parte 2) |
| Prova contra o arrogante (C8) | a grife da rival é falsificada | o papel do vilão tem falha: sem registro, sem aviso, prazo vencido |
| Erro sem volta abre a série (C1) | casou com o homem errado | assinou, vendeu ou deixou vencer: o erro que puxa a história |

**Para gerar variações:** escolha 1 premissa, troque o objeto e o vilão, e use só fato de lei já lido na fonte. Cada
roteiro novo usa objeto, gancho final e frase de impacto diferentes dos anteriores, registrados em `NOVELAS_USADAS.md`.

## 5. Protagonista: Dr. Pelicioni (desde 23/11/2026)
O lugar do "poderoso que chega na virada" do modelo (o "Who dares touch her?") é sempre do **Dr. Pelicioni**. Ficha e
limites estão em `PERSONAGEM_DR_PELICIONI.md`. Com `"protagonista": "Dr. Pelicioni"` no JSON, o verificador exige:
- **O8:** ele não aparece antes da virada, entra na batida de REVELAÇÃO, tem fala de LEI e faz uma previsão
  (`previsao`) que se cumpre depois (`previsao_cumprida`);
- **O9:** nenhuma promessa de resultado, pedido de contratação ou ponto de exclamação nas falas dele.

## 6. O que o verificador não vê
O verificador confere a estrutura a partir das marcas que o roteirista declara (tipos e `marcas`). Ele **não julga** se a
humilhação dói, se a fala soa natural ou se a lei está certa. Isso continua sendo leitura humana, como a parte de
julgamento da auditoria do agro.
