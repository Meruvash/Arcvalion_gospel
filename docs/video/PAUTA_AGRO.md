# Política de pesquisa e originalidade de pauta (vídeos do agro)

Pedido do editor (12/11/2026), depois de quatro roteiros seguidos sobre dívida e crédito rural: "você está num loop
tratando do mesmo assunto em todos os vídeos". Esta política vale **antes** de qualquer roteiro da skill `video-agro` e
está acima do hábito de procurar "o assunto da semana no crédito rural".

## 1. Eixos de pauta (rodízio obrigatório)

| Eixo | Exemplos de assunto |
|---|---|
| **A. Dívida e crédito rural** | MP, CMN, prorrogação, recuperação judicial, Plano Safra |
| **B. Terra e documentação** | georreferenciamento, CAR, CCIR, ITR, usucapião rural, posse, regularização |
| **C. Tributos e custos** | reforma tributária (IBS/CBS), Funrural, nota do produtor, ITR, energia, frete |
| **D. Mercado e exportação** | regras de compradores (União Europeia, China, EUA), tarifas, preços, rastreabilidade |
| **E. Clima, safra e produção** | Conab, IBGE, El Niño/La Niña, pragas, tecnologia que chegou ao campo |
| **F. Família, sucessão e contratos** | herança de fazenda, holding, arrendamento, parceria, Estatuto da Terra |
| **G. Trabalho e segurança** | NR-31, trabalhador rural, aposentadoria rural, acidentes, roubo de gado e defensivos |
| **H. Meio ambiente e licenças** | Código Florestal, outorga de água, licenciamento, multas ambientais |
| **I. Histórias e curiosidades do campo** | casos reais e lugares curiosos do agro, "existe um lugar onde…", história de uma lavoura, de uma cidade ou de uma família |

- **Rodízio:** nunca dois vídeos seguidos no mesmo eixo.
- **Limite do eixo A:** no máximo **1 vídeo em cada 4**, porque é o eixo do público endividado e o mais fácil de repetir.
- **Exceção:** um fato novo de impacto direto (por exemplo, a sanção da lei das dívidas) pode furar o rodízio só como
  **atualização curta**, avisando o editor de que é exceção.

## 2. Pesquisa mínima antes de propor

Antes de escrever o roteiro, levante **pelo menos 5 pautas candidatas, de pelo menos 3 eixos diferentes**, usando os três
tipos de fonte:

1. **Demanda do público:** o que o produtor está perguntando ou assistindo.
   - autocomplete do Google e do YouTube;
   - tendências em vídeo curto (Virlo, quando disponível);
   - perguntas em portais e fóruns do agro.
2. **Agenda oficial:** o que muda por norma ou decisão, sempre com o texto lido na fonte primária.
   - Diário Oficial, CMN e BC (API de normativos), Receita;
   - MAPA, Incra, Conab, IBGE;
   - STF e STJ;
   - Câmara e Senado (dados abertos);
   - para regra estrangeira, o texto oficial do país ou bloco (no caso da União Europeia, o EUR-Lex).
3. **Imprensa do agro:** Canal Rural, Globo Rural, Notícias Agrícolas, Agência Senado/Câmara e portais regionais. Use para
   achar a pauta, nunca como prova final.

## 2.1 Aprendizado de desempenho (16/11/2026)
"A porta e o porteiro" (acordo Mercosul–UE + EUDR) **praticamente não teve visualização**. Era um assunto institucional e
macroeconômico, com dado positivo de mercado e sem conflito nem dinheiro do espectador em jogo.

Os vídeos de agro que mais viralizaram no Brasil entre agosto e novembro de 2026 (pesquisa no Virlo, 16/11/2026) têm três
coisas em comum:
- **Lacuna de curiosidade logo na 1ª frase:** "Existe uma cidade aqui do lado de Mossoró que foi construída do zero…",
  "poucas pessoas sabem disso, mas existe…".
- **História com conflito:** herança dividida entre irmãos, patrão e trabalhador, quem fica com a fazenda.
- **Algo do espectador em jogo:** a terra dele, o dinheiro dele, a família dele. Exemplo: "Você financiou um carro de 50
  mil… vai pagar 100 mil?".

Nos vídeos de direito, o que mais roda é o mito × verdade sobre um direito que a pessoa acha que não tem.

**Regras daí em diante:**
- **Evite:** pauta institucional, macroeconômica ou de "boa notícia do setor" sem algo do espectador em jogo.
- **Prefira:** pergunta que o produtor faria no balcão do sindicato ("o vizinho pode me cobrar a cerca?", "o caseiro pode
  ficar com a fazenda?").
- **Use o Virlo** (`find_videos`, `search_hooks`) na pesquisa de demanda, sempre que estiver disponível.

## 3. Critérios de escolha (nota de 1 a 5 em cada um)

| Critério | Pergunta |
|---|---|
| Novidade | É fato dos últimos 30 dias, ou um prazo que vence nos próximos 60? |
| Alcance | Afeta muitos produtores (por cultura, região ou porte)? |
| Utilidade | O produtor faz algo diferente depois de ver? |
| Prova | Há documento oficial para mostrar e citar? |
| Gancho | Cabe numa frase de "Você sabia…" que surpreende? |
| **Curiosidade (peso 2)** | A primeira frase abre uma pergunta que a pessoa precisa ver respondida? |
| **Em jogo para o espectador (peso 2)** | Mexe com a terra, o dinheiro ou a família de quem assiste? |
| Originalidade | Eixo, ângulo e fonte são diferentes dos últimos vídeos (§ 4)? |

Apresente ao editor as **3 melhores**, com a nota de cada uma e uma linha de justificativa, mais a recomendação. Só depois
escreva o roteiro da escolhida, ou da recomendada, se o editor já tiver pedido o roteiro direto.

## 4. Originalidade

- **Antes de propor,** confira `docs/video/PAUTAS_USADAS.md`: data, eixo, norma ou fato, ângulo e gancho de cada vídeo.
- **Mesma norma ou fato:** proibido repetir, salvo fato novo de verdade (sanção, veto, decisão, prazo vencido). Nesse
  caso, é atualização curta e o editor é avisado.
- **Gancho:** proibido repetir a estrutura do anterior (por exemplo, "prazo que acaba", duas vezes seguidas). Varie entre
  número surpreendente, contradição, pergunta do público, comparação, contagem regressiva e história de um produto.
- **Depois da entrega:** registre o vídeo em `PAUTAS_USADAS.md`. Imagens e trilha continuam no `CENAS_USADAS.md`.
