# Auditoria de padrão ouro dos roteiros do agro (desde 19/11/2026)

Pedido do editor (19/11/2026): "Precisamos de uma auditoria de roteiro sempre comparando com a estrutura do caseiro e do
irmão vendeu sem avisar. Esse último bateu 5.000 visualizações."

**Regra:**
- Todo roteiro da skill `video-agro` passa por esta auditoria **antes** de ser mostrado ao editor.
- A tabela da auditoria vai no arquivo do roteiro e na mensagem ao editor.
- Este arquivo fica acima do `PADRAO_CASEIRO.md` e do `PROMPT_VIDEO_AGRO.md` no que disserem de diferente.

## 1. Os dois vídeos de ouro e os outros

| Vídeo | Visualizações (informadas pelo editor) | Nota automática nesta auditoria |
|---|---|---|
| **"O irmão vendeu sem avisar"** (herança, CC arts. 1.794, 1.795, 1.314, 1.322) | **5.000** | **22/22** |
| **"O caseiro e o vizinho"** (usucapião, CC arts. 1.198, 1.208, 1.238, 1.239) | **2.200** | **22/22** |
| "O gado do vizinho comeu a sua roça" | o mais fraco dos 100% animação | 14/22 |
| "Comprou a terra e não é dono?" | alcance fraco | 13/22 |
| "O banco toma o seu sítio?" | entregue em 19/11; resultado ainda não informado | 12/22 |
| "O banco leiloa a sua fazenda sem juiz?" | não distribuído no Shorts (imagens do TikTok) | 11/22 |
| "O relógio zerou" (PLV 16) | — | 8/22 |
| "Cinco por dia" | — | 7/22 |
| "A porta e o porteiro" (EUDR) / "O prazo é quinta" (MP 1.376) | quase sem visualização / — | 6/22 |

- **A auditoria separa os grupos sem sobreposição:** os dois vídeos de ouro tiram 22, e nenhum outro passa de 14.
- **Limite:** é uma comparação de texto com 2 sucessos. Sem as métricas internas (retenção, compartilhamentos), é
  correlação, não prova de causa. Cada vídeo novo com número informado entra na tabela, e os itens são revistos.

## 2. Anatomia batida a batida (o molde comum aos dois)

| # | Função | Caseiro (2.200) | Irmão (5.000) | Molde |
|---|---|---|---|---|
| 1 | Gancho | "Você sabia que o **caseiro** que mora há vinte anos na **sua fazenda** **não pode** ficar com ela, mas um **estranho** que entra num pedaço dela **pode**?" | "Você sabia que, se o seu **irmão** vender a parte dele **da fazenda da herança** pra um **estranho** sem te avisar, **você pode** tomar o negócio pra você?" | "Você sabia que" + **pessoa próxima** + **o bem de quem assiste** + **um estranho** + **virada de poder** ("não pode / pode"). Até 30 palavras, sem sigla nem número |
| 2 | Chave | "A explicação está numa palavra: posse." | "A explicação está em três palavras: tanto por tanto." | **Frase fixa:** "A explicação está numa palavra: X." / "em N palavras: X." (até 3 palavras) |
| 3 | Tradução | "O caseiro cuida da terra em nome do patrão. Pra lei, ele é detentor, não possuidor." | "Enquanto a herança não é dividida, a fazenda é de todos os irmãos juntos, como num condomínio." | O **mesmo personagem** volta, e a lei vira uma comparação de balcão |
| 4 | Prova | "O Código Civil diz que…" (cartão 1: art. 1.198) | "E o Código Civil diz: …" (cartão 1: art. 1.794) | "O Código Civil diz" / "A lei diz" + cartão com o texto literal |
| 5 | Extensão | "O mesmo vale pra quem usa a sua terra por favor seu…" | "Se ninguém te avisou, você pode depositar o mesmo valor… em até 180 dias." | A regra alcança mais casos, ou já dá a ação com prazo |
| 6 | Reforço | **"Agora,** quem entra num pedaço da sua terra… começa a contar tempo pra virar dono." | "E tem mais: nenhum irmão pode arrendar ou emprestar a fazenda pra um estranho…" | Segundo fato ou virada |
| 7 | Virada | "São quinze anos, ou dez se ele morar ali ou produzir." | **"Agora,** o lado que pouca gente conta: … ela pode ser vendida, e o dinheiro repartido." | A **virada é anunciada com "Agora,"** (fala 6 ou 7) |
| 8 | Número / consolo | "…bastam cinco anos." (cartão 2: art. 1.239) | "E mesmo nessa venda… irmão tem preferência sobre estranho." (cartão 2: art. 1.322) | Fecha a escada de **prazo** (anos, dias) ou o contraste pessoa próxima × estranho |
| 9 | Pergunta | "Tem **alguém** usando um pedaço da **sua** terra sem você dizer nada?" | "Na **sua** família, **alguém** já vendeu parte da herança sem avisar?" | Pergunta sobre **alguém** da vida de quem assiste. Não é de sim ou não sobre um papel |
| 10 | Fecho | "Eu sou o Dr. Pelicioni, advogado. Na usucapião, **ficar calado conta tempo contra você.** Me segue pra proteger o que é seu." | "Eu sou o Dr. Pelicioni, advogado. Em herança de fazenda, **prazo perdido não volta.** Me segue pra proteger o que é da sua família." | Molde fixo, com uma **moral de tempo ou de omissão** |

**O que os dois têm em comum, além do texto:**
- **Uma voz só:** narrador do começo ao fim, e o editor só no fecho.
- **55 a 57 s**, com 183 a 193 palavras.
- **Prova:** só o Código Civil, com 2 cartões.
- **Imagem:** 100% pintura animada.
- **Tema atemporal.**
- **O conflito é entre pessoas em volta da terra:** caseiro × estranho e irmão × estranho. Em nenhum dos dois o
  antagonista é um banco, um órgão ou um mercado.

**Por que o irmão foi mais longe que o caseiro (hipótese, sem métricas internas):**
- **O gancho dá poder a quem assiste** ("você pode tomar o negócio pra você"), em vez de só ameaçar.
- **O personagem é da família,** e a família puxa marcação e compartilhamento.
- **O número é um prazo de ação curto,** 180 dias, que a pessoa precisa saber já.

## 3. Como fazer a auditoria

### Parte 1 — automática (o texto contra o ouro)

Comando: `python3 tools/video/agro-arte/auditar_roteiro.py falas.json --md auditoria.md`

- **A saída** tem 22 itens, com o valor do roteiro ao lado do caseiro e do irmão, e a lista dos desvios.
- **Aprovação:** **20/22 ou mais**. Cada item reprovado vem com uma linha de justificativa no roteiro.
- **Abaixo de 20:** o roteiro não é apresentado como recomendação. Ou se reescreve no molde, ou se troca a pauta.

### Parte 2 — de julgamento (preenchida à mão no roteiro)

| # | Pergunta | Como o ouro responde |
|---|---|---|
| M1 | A pergunta do vídeo é **a mesma** que aparece no autocomplete? | "caseiro pode pedir usucapião"; "irmão vendeu parte da herança" |
| M2 | O que está em jogo é **a própria terra ou a herança**, e não um prejuízo menor? | A fazenda e a herança |
| M3 | O antagonista é **uma pessoa** (estranho, vizinho, comprador), e não um banco ou um órgão? | O estranho |
| M4 | A "verdade" do vídeo **não** é um ditado conhecido? | Ninguém fala "caseiro não vira dono" nem "tanto por tanto" no balcão |
| M5 | Tem **ação com prazo** que quem assiste pode tomar? | Contar tempo; depositar em 180 dias |
| M6 | Atemporal (lei que vale daqui a um ano)? | Código Civil |
| M7 | **Uma variável nova só** em relação ao ouro (formato, imagem, trilha)? | — |
| M8 | Prova lida na fonte primária e imagem 100% própria? | Senado; pintura em código |

**Aprovação:** os 8 itens com "sim". Um "não" só passa com justificativa aceita pelo editor.

### Onde registrar

- **No roteiro:** a tabela da Parte 1, a tabela da Parte 2 e a nota.
- **Na mensagem ao editor:** a nota e os desvios, em 3 a 5 linhas.
- **Depois da publicação:** as visualizações informadas pelo editor entram na seção 1 deste arquivo.

## 4. Primeira aplicação: "O banco toma o seu sítio?" (entregue em 19/11, antes desta auditoria)

**Nota: 12/22.** Os desvios do ouro:
- **A2/A3/C1/M3 — sem pessoa próxima e sem estranho.** O antagonista é o banco e a empresa de insumos.
- **B1/B2 — a fala 2 fugiu do molde:** "A palavra que protege o seu sítio é impenhorável".
- **D1 — a fala 4 conta um caso do STF** em vez de "a lei diz".
- **E1 — sem "Agora,"** marcando a virada.
- **F1 — o número é de área** (4 módulos fiscais), não de prazo. E "módulo fiscal" exige explicação.
- **G2 — a pergunta é sobre provar o trabalho da família,** não sobre alguém.
- **H2 — a moral do fecho não fala de tempo.**

**Previsão honesta:** pela auditoria, este vídeo deve ficar abaixo do caseiro e do irmão. Se ele for bem mesmo assim, é
sinal de que o tema (banco e dívida) pesa mais do que esta auditoria mede, e os itens A3 e M3 são revistos.

## 5. Pautas que cabem no molde do ouro (para pesquisar e ler na fonte antes de propor)

| Pauta | Pessoa próxima × estranho | Prazo | O que falta |
|---|---|---|---|
| Arrendatário tem preferência para comprar a terra arrendada | arrendatário × comprador estranho | depósito em prazo legal | Ler o Estatuto da Terra (Lei 4.504/1964), art. 92, e o Decreto 59.566/1966 no Senado; checar o autocomplete |
| Passagem forçada até a estrada | vizinho × você | — (sem prazo) | Pronta (CC art. 1.285, 15/16 no Crivo); falta o item F1 |
| Herdeiro que cuida sozinho da fazenda vira dono? | irmão que mora na terra × os outros herdeiros | anos de posse | Ler o CC e a jurisprudência do STJ sobre usucapião entre herdeiros; tema delicado, a ser conferido |
| Doação da fazenda a um filho e a parte dos outros | pai × filhos | — | Ler o CC (colação, legítima). Fora do eixo A/B, então entra como exceção avisada (eixo F) |
