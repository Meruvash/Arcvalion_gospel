# Teste do crivo de notícias: 30/10/2026

Aplicação do `docs/CRIVO_NOTICIAS.md` a pautas reais do dia, vindas de portais conservadores, e às três notas
publicadas em 29/10, para ver se o crivo explica por que elas saíram fracas. Nada aqui foi publicado: é teste.

## 1. O que o teste encontrou antes de pontuar

**O coletor escondia os portais conservadores.** A rodada 1 ordenava as candidatas pela lista de temas, escrita só em
português. Matéria em inglês (Christian Post, Fox, National Review…) tirava 0 ponto de tema e caía para o fim; das 80
vagas da pauta, o Guiame ocupava quase todas, porque publica dezenas de itens por dia. Corrigido em
`tools/editorial/coletar.py` e `config/fontes.json`:

| | Antes | Depois |
|---|---|---|
| Temas | só português | português e inglês |
| Portal conservador | sem marca | `"conservador": true`, +1 de prioridade e "portal conservador" na pauta |
| Itens por feed | sem limite (Guiame com mais de 20 nas 80 vagas) | no máximo 6 por feed |
| Feeds conservadores dos EUA | Fox, National Review, Washington Examiner, Dispatch, American Conservative | + Daily Wire, Daily Signal, Federalist, Free Beacon, Faithwire, Live Action |
| Pauta de 30/10 (3 dias) | 329 candidatas, 80 listadas, quase só Guiame | 163 candidatas, 25 fontes diferentes nas 80 listadas |

**Fontes testadas em 30/10/2026:**

- **Funcionam** (feed liberado para robôs e sem bloqueio a bots de IA): Daily Wire, Daily Signal, Federalist, Free
  Beacon, Faithwire, Live Action.
- **Funcionam, mas o robots.txt bloqueia bots de IA**: LifeSiteNews, The Free Press e Gazeta do Povo. Ficam para
  leitura manual.
- **Sem feed**: PragerU, Washington Stand e CBN News (404). A PragerU fica para leitura manual.
- **Robots proíbe robôs**: Brasil Paralelo.
- **Feed quebrado**: Revista Oeste (XML inválido).
- **Página bloqueada para leitura (403)**: Daily Signal. O feed funciona; a página, não.

## 2. As três notas de 29/10 no crivo novo

| Nota | Valor (8) | Viral (7) | Cristã (5) | Total | Diagnóstico |
|---|---|---|---|---|---|
| Comissão da Câmara aprova regras para vítima de violência na escola | 6 | 2 | 1 | **9** | Correta e útil, mas sem personagem, sem emoção, sem gancho e sem leitura cristã. É a "notícia genérica" |
| Pew: religião se estabiliza nos EUA | 4 | 4 | 1 | **9** | Dado bom, mas sem Brasil, sem personagem e com o toque cristão fraco |
| Canadá: projeto barra eutanásia por doença mental | 5 | 4 | 4 | **13** | A melhor das três: contraste ("barra, mas libera") e tema de vida |

O crivo novo põe duas das três na faixa "só se faltar nota". Isso confirma o diagnóstico do responsável editorial:
elas tinham valor jornalístico, mas nenhum eixo de viralização nem toque cristão.

## 3. Pautas de hoje (30/10), com origem em portais conservadores

Os pontos de cada eixo seguem as perguntas de sim ou não do crivo. "Conferido" quer dizer que lemos a fonte primária.

| # | Pauta | Origem | Trilha | Eliminatório | V | B | C | Total |
|---|---|---|---|---|---|---|---|---|
| 1 | Pastor processa para invalidar emenda que tira a definição de casamento da Constituição da Virgínia; votação em 3/11 | [Christian Post](https://www.christianpost.com/news/pastor-sues-to-block-virginia-same-sex-marriage-amendment.html), Daily Signal | quente | — (conferido: [petição](https://static1.squarespace.com/static/5eecbc7b39d48008de082248/t/6ada4dcf6ef04957c8814e66/1792691663493/2026-10-22+-+Purves+v.+VBOE+Complaint.pdf), [pergunta 2 da cédula](https://www.elections.virginia.gov/election-law/proposed-constitutional-amendment-question-2/)) | 7 | 6 | 5 | **18** |
| 2 | Bispos dos EUA aos católicos: "discípulos de Jesus primeiro, americanos depois" | [Gazeta do Povo](https://www.gazetadopovo.com.br/mundo/bispos-dos-eua-pedem-aos-catolicos-coloquem-a-fe-antes-da-politica/), [EWTN](https://www.ewtnnews.com/world/us/u-s-bishops-urge-catholic-voters-start-with-your-faith) | quente | — (falta abrir os vídeos da USCCB) | 6 | 5 | 4 | **15** |
| 3 | Dia da Reforma (31/10): como a Reforma moldou a liberdade de consciência | [PragerU, "How the Reformation Shaped Your World"](https://www.prageru.com/videos/how-the-reformation-shaped-your-world) (2018) | atemporal | — (conferir cada afirmação; "Aqui estou, não posso fazer outra coisa" tem autoria discutida) | 6 | 5 | 4 | **15** |
| 4 | Piloto Joey Logano e a esposa adotam as duas crianças que acolhiam | Live Action, [Jayski](https://www.jayski.com/2026/10/22/joey-and-brittany-logano-finalize-adoption-of-two-children/) | atemporal (o fato é de 22/10) | quente: mais de 7 dias. Atemporal: precisa de gancho e da fé dita pelo casal | 6 | 4 | 4 | **14** |
| 5 | Pastor do RJ volta a ser alvo da PF por suspeita de lavagem | [Gazeta do Povo](https://www.gazetadopovo.com.br/brasil/pastor-rj-volta-a-ser-alvo-pf-suspeita-lavagem-dinheiro/) | quente | — (nota da PF; presunção de inocência) | 7 | 3 | 2 | **12** |
| 6 | Filho de pastor cubano detido pelo ICE depois de se abrigar numa igreja | Christian Post | quente | — (falta nota do ICE e da igreja) | 4 | 4 | 4 | **12** |
| 7 | Igreja em Brasília pichada depois do 2º turno | Guiame | quente | **Pendente**: só a postagem do pastor; a busca não achou outra fonte nem registro policial público | 4 | 4 | 3 | **11*** |
| 8 | Promotor não acusa casal que tentou matar bebê de 31 semanas | LifeSiteNews | quente | **Eliminada**: a busca não achou o caso fora do portal (regra 1) | — | — | — | — |
| 9 | "Eu era uma vítima trans de 14 anos" (depoimento) | Daily Wire | — | **Eliminada como notícia**: só depoimento e opinião (regra 2). Pode entrar em "O que dizem" de uma nota sobre a Emenda 3 do Missouri | — | — | — | — |
| 10 | "Como construir um legado familiar que dure séculos" | Federalist | — | **Eliminada**: ensaio de opinião (regra 2) | — | — | — | — |
| 11 | Pastor assassinado por gangue na Colômbia | Faithwire | — | **Eliminada**: fato de 19/10, mais de 7 dias (regra 6) | — | — | — | — |
| 12 | Mulher morre depois de seguir conselho médico do ChatGPT | Daily Wire | — | **Eliminada**: sem eixo de fé, família ou liberdade (regra 3) | — | — | — | — |

\* Só publica depois de achar a postagem original do pastor e um registro policial. Mesmo assim, sem atribuir a
autoria a grupo político.

**Edição do dia pelo crivo:** manchete com a pauta 1 (18), a pauta 2 (15) e a pauta 3 como atemporal (15). A
mistura fica com 2 quentes e 1 atemporal, no máximo 1 de política americana (a 2 é sobre fé e voto, não sobre
partido) e o efeito no Brasil coberto por 1 e 3. Reservas: a 4 vira atemporal quando houver gancho; a 5 é a nota
brasileira do dia se faltar uma.

### Pontos da manchete, linha por linha

- **Valor (7):** petição com link (2); plebiscito estadual (2); o mesmo debate no Brasil, no PL 5167/2009, aprovado
  em comissão da Câmara em outubro de 2023 (2; conferir a tramitação na página da Câmara); duas fontes
  independentes, Christian Post e o site eleitoral da Virgínia (1); sem número de pesquisa (0).
- **Viral (6):** indignação ou mobilização (1); personagem com nome, o pastor Ben Purves (1); moeda social, o
  argumento de procedimento que a grande imprensa não deu (1); utilidade, a convocação de oração (1); gatilho, a
  votação de terça (1); cabe num cartão (1); não contraria narrativa (0).
- **Cristã (5):** Mateus 19.4-6 (2); fé vivida, mais de 400 pastores numa carta aberta (1); pede oração (1); rende
  estudo sobre casamento (1).

## 4. Exemplo do "nosso toque" (rascunho da manchete, não publicado)

Rascunho para mostrar o padrão. Ainda falta ouvir o outro lado (Virginians for Marriage Equality), achar uma foto
com licença e confirmar a tramitação do PL 5167/2009.

- **Título (14 palavras):** Pastor da Virgínia pede à Justiça que invalide emenda do casamento votada na terça
- **Lide:** O pastor Ben Purves, da Occoquan Bible Church, pediu à Justiça do condado de Prince William, na
  Virgínia (EUA), que invalide a emenda que tira da Constituição estadual a definição de casamento entre homem e
  mulher, caso seja aprovada. A ação é de 22 de outubro; o plebiscito é em 3 de novembro.
- **Por que importa (toque: o que o fato revela):** O processo não discute a Bíblia, discute o rito. A lei da
  Virgínia manda divulgar a emenda três meses antes da eleição da Assembleia, e a ação diz que isso não foi feito.
  Defender o casamento também passa por exigir que as regras do jogo sejam cumpridas, sem atalho.
- **O que muda para você (toque: o que fazer):** Se você tem família ou igreja parceira na Virgínia, a votação é
  na terça, 3/11. No Brasil, o tema está na Câmara, no PL 5167/2009.
- **O que dizem:** a petição, "Esses passos existem para informar os eleitores antes da eleição decisiva da
  Assembleia" (tradução livre); Victoria Cobb, do Founding Freedoms Law Center (tradução livre); e o lado a favor
  da emenda, ainda por ouvir.
- **Nossa opinião (toque: a Escritura e um conselho):** Perguntado sobre casamento, Jesus voltou ao princípio: o
  Criador "os fez homem e mulher" (Mateus 19.4, NVI). Ore pelos pastores da Virgínia nesta semana e acompanhe o
  projeto daqui. Convicção firme, tom manso.
- **Chamada:** 400 pastores, uma ação na Justiça e um plebiscito na terça: a Virgínia vota o casamento ⚖️
- **Pergunta:** A sua igreja fala de casamento com a mesma clareza?

## 5. Ajustes que o teste sugeriu (já incorporados)

1. Tema em inglês no coletor e limite de 6 itens por feed (seção 1).
2. Eliminatório de opinião pura: metade do que os portais conservadores publicam é ensaio (Federalist, Daily
   Wire). Vira fonte de "O que dizem", não notícia.
3. Trilha atemporal com gancho obrigatório: a PragerU publica pouco e quase nada datado. O valor dela está em
   juntar um vídeo bom a uma data (Dia da Reforma, Ação de Graças, Natal).
4. Conferência de citação histórica: o vídeo da Reforma esbarra em frase de autoria discutida. A regra 7 dos
   eliminatórios pega isso.
5. O crivo não escolhe lado sozinho. A pauta 5 (pastor investigado) e a 6 (imigração) pontuam bem e incomodam. Elas
   entram pelo critério, com presunção de inocência e os dois lados.

Fontes consultadas no teste: [Christian Post](https://www.christianpost.com/news/pastor-sues-to-block-virginia-same-sex-marriage-amendment.html),
[Virginia Department of Elections](https://www.elections.virginia.gov/election-law/proposed-constitutional-amendment-question-2/),
[Gazeta do Povo](https://www.gazetadopovo.com.br/mundo/bispos-dos-eua-pedem-aos-catolicos-coloquem-a-fe-antes-da-politica/),
[PragerU](https://www.prageru.com/videos/how-the-reformation-shaped-your-world),
[PragerU, Real Talk com Bill Federer](https://www.prageru.com/videos/can-america-survive-attacks-on-its-judeo-christian-roots-historian-bill-federer-responds),
[Jayski](https://www.jayski.com/2026/10/22/joey-and-brittany-logano-finalize-adoption-of-two-children/),
[IBDFAM sobre o PL 5167/2009](https://ibdfam.org.br/noticias/11238/Comiss%C3%A3o+da+C%C3%A2mara+aprova), feeds de
30/10/2026 (Daily Wire, Daily Signal, Federalist, LifeSiteNews, Faithwire, Live Action, Gazeta do Povo).

## 6. Reavaliação com a prioridade geográfica (mesma noite)

O responsável editorial definiu a ordem: nacional, Rondônia, Porto Velho. Internacional só entra com impacto grande
e direto no Brasil, de preferência atemporal (seção 0 do crivo). Com isso:

- **Virgínia** perdeu os 2 pontos de proximidade: o debate existe aqui, mas não é o mesmo projeto nem o mesmo caso.
  Ficou com 16 (valor 5, viral 6, cristã 5).
- **Reforma** ganhou um gancho nacional, o PL 3183/2026 do Senado, que leva o Dia Nacional do Evangélico para
  31 de outubro e o torna feriado. Ficou com 17 (valor 8, viral 5, cristã 4) e virou a manchete.
- **Bispos dos EUA** ficou com 13 (valor 4, viral 5, cristã 4).

As três foram publicadas a pedido do responsável editorial, com data de 29/10/2026 (horário de Brasília). Duas
são internacionais: pela regra nova, a partir da próxima edição entra no máximo uma por dia.

**Fontes de Rondônia testadas em 29/10/2026, por volta das 21h de Brasília:**

- **Entram na coleta** (feed válido): Governo de Rondônia, Rondoniagora, G1 Rondônia e News Rondônia.
- **Ficam para leitura manual:**
  - Rondônia Ao Vivo: não tem feed;
  - Rondônia Dinâmica: XML quebrado;
  - Tudo Rondônia: bloqueia o acesso (403);
  - Câmara de Porto Velho: proíbe robôs;
  - ALE-RO, Prefeitura de Porto Velho, TJ-RO e MP-RO: o feed não responde.

O coletor passou a aceitar feed com entidade de HTML e data em ISO, comuns nos portais regionais.
