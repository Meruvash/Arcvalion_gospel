# Crivo de escolha das notícias

Pedido do responsável editorial em 30/10/2026: as primeiras notas saíram fracas e genéricas (comissão da Câmara,
pesquisa do Pew). A pauta passa a nascer em **portais conservadores consolidados** dos EUA e do Brasil, traduzida e
reescrita por nós, com duas trilhas (**quente** e **atemporal**) e com o nosso toque: a relevância cristã do fato.
Este documento diz onde procurar, o que elimina uma pauta, como pontuar (motor de relevância de 0 a 100, desde 31/10/2026) e como escrever o toque.
Modelo do crivo: o do Elite Boardgamers (eliminatórios, depois pontos; manchete é a maior nota do dia).

Teste de 30/10/2026, com notícias reais: `docs/TESTE_CRIVO_2026-10-30.md`.

## 0. Prioridade geográfica (30/10/2026)

Pedido do responsável editorial: a edição é **nacional primeiro**, depois **Rondônia**, depois **Porto Velho**.

| Ordem | Abrangência | Quando entra |
|---|---|---|
| 1 | Brasil | Sempre: é o núcleo da edição (pelo menos 3 das 5 notas do dia) |
| 2 | Rondônia | Só pauta do estado que passe no **teste temático** (eliminatório 10) e no corte. Não há cota local |
| 3 | Porto Velho | Idem: fato da capital entra só quando o próprio fato é de fé, igreja, liberdade, vida, família ou educação |
| 4 | Internacional | Só com **impacto grande e direto no Brasil** (o mesmo projeto tramita aqui, afeta brasileiros, muda regra que vale aqui) ou na trilha **atemporal**. No máximo 1 por dia |

## 1. A regra de ouro: o portal dá a pauta, a fonte primária dá o fato

Portal conservador é onde a gente **encontra** a história e o ângulo que a grande imprensa não deu. O fato publicado
é confirmado na **origem**: o processo (PDF da petição), a decisão, a lei, o vídeo da declaração, o relatório, a nota
da igreja, a postagem da própria pessoa. Assim a nota sai com a força do portal e sem herdar o exagero dele.

- O portal entra nas `fontes` como `secundaria` e no texto como "segundo o Daily Signal", "revelou o Federalist".
- Título de portal não é fato: "Pro-abortion DA won't charge couple" vira, na nossa nota, o que o promotor decidiu
  e o que ele disse, com a fonte de cada lado.
- **Nunca traduzir a matéria inteira.** Tradução integral é cópia (direito autoral) e o Google rebaixa conteúdo
  duplicado. Traduzimos os fatos e escrevemos texto próprio; citação literal curta, só de frase lida, marcada
  "tradução livre", com o link da página.

## 2. Onde procurar

Leitura na ordem abaixo. Os marcados com (feed) entram sozinhos na rodada 1 (`tools/editorial/coletar.py`, com
`"conservador": true` em `config/fontes.json`, que sobe a pauta na lista); os outros são leitura manual, uma página
por vez, com link (o robots.txt deles proíbe robôs ou bots de IA, ou não há feed).

**Brasil: notícia quente**

| Portal | Bom para | Cuidado |
|---|---|---|
| Gazeta do Povo (manual: bloqueia bots de IA) | Liberdade religiosa, educação, família, STF; colunas de Franklin Ferreira, Polzonoff | Separe reportagem de coluna |
| Revista Oeste, Crusoé, O Antagonista (feed parcial) | Política, Judiciário, liberdade de expressão, lideranças da direita | Política entra (eixo `politica`); boato de bastidor sem fonte, não |
| Pleno News, Guiame (feed) | Igrejas e pastores no Brasil, perseguição traduzida | Agregadores: quase nunca são a origem |
| Jovem Pan (feed com filtro) | Repercussão no Congresso | — |

**Rondônia e Porto Velho** (revisado em 30/10/2026, a pedido do responsável editorial: notícia local de verdade vem
dos veículos locais, não do site do governo)

Audiência de referência: pesquisa do Instituto Haverroth (setembro de 2025, 609 entrevistas presenciais em Porto
Velho) pôs o Rondoniaovivo como o site de notícias mais lembrado e acessado (75,3%), seguido de longe por
Rondoniagora (3,4%), Eu Ideal (3,0%), Portal de Rondônia (3,0%), Rondonoticias (2,5%), News Rondônia, O Observador e
Tudo Rondônia.

| Veículo | Bom para | Como acompanhar |
|---|---|---|
| **Rondoniaovivo** | Cidade, polícia, política e serviço em Porto Velho; reportagem própria | rodada 1: manchetes da página inicial (o RSS parou em 2020) |
| **Rondoniagora** | Política estadual e bastidores | rodada 1 (feed) |
| **G1 Rondônia / Rede Amazônica** | Reportagem com repórter, vídeo e documentos | rodada 1 (feed); WebFetch bloqueado, ler pela busca |
| **Rondônia Dinâmica** | Política, Justiça e Assembleia | rodada 1 (sitemap de notícias) |
| **News Rondônia** | Política e Assembleia | rodada 1 (feed) |
| **O Observador** | Polícia e cidade em Porto Velho | rodada 1 (feed; republicações de agências ficam fora) |
| **Eu Ideal** | Política de Porto Velho, Câmara Municipal | manual (o robots.txt só libera robôs com nome) |
| Tudo Rondônia, Rondonoticias, Portal de Rondônia, SIC TV, CBN Amazônia | Política e cidade | manual |
| Governo de Rondônia, ALE-RO, Prefeitura e Câmara de Porto Velho (SAPL), TJ-RO, MP-RO, Defesa Civil | Documento, decisão, número oficial | para confirmar e citar; não são a pauta principal |

**Regra local de fonte.** Em notícia de Rondônia ou Porto Velho, a reportagem própria de um veículo da tabela
(com repórter, entrevista com nome, documento ou presença no local) pode ser a base da nota. Ela entra nas `fontes`
com `"tipo": "reportagem_local"` e precisa de confirmação: outro veículo independente com reportagem própria, ou
uma fonte oficial (`primaria`). Nota de assessoria republicada por um portal não conta como reportagem. No texto, o
crédito aparece: "segundo o Rondoniaovivo", "como mostrou o G1 Rondônia". Fotos desses veículos têm direitos
reservados: só com autorização por escrito (`fotos.py local` com a licença dada pelo veículo).

**EUA: só com impacto grande no Brasil, ou como gancho da trilha atemporal**

| Portal | Bom para | Cuidado |
|---|---|---|
| The Daily Signal, da Heritage Foundation (feed) | Congresso, Suprema Corte, liberdade religiosa, plebiscitos estaduais | Linha da Heritage; confirmar no documento |
| The Daily Wire (feed) | Cultura, depoimentos (destransição, pais x escola), Hollywood | Título forte; muito opinião assinada |
| The Federalist (feed) | Aborto, escola, família, bastidor de mídia | Quase tudo é opinião: citar como opinião de quem assina |
| Washington Free Beacon (feed) | Investigação, documentos, universidades | Bom em documento: siga o link deles |
| The Christian Post (feed) | Processos de igrejas e pastores, perseguição, gospel nos EUA | Sobe a cadeia até o processo ou a ONG |
| Faithwire / CBN News (feed) | Testemunhos, celebridades cristãs, perseguição | Confirmar na postagem ou entrevista original |
| Live Action News (feed) | Aborto, adoção, vida | Organização pró-vida: parte interessada, dizer isso |
| Fox News, National Review, Washington Examiner, WORLD (feed) | Política e fé, com filtro de temas | — |
| LifeSiteNews, The Free Press (manual) | Igreja Católica e cultura; debates de ideias | Os dois bloqueiam bots de IA: só leitura pontual |

**Trilha atemporal**

| Fonte | Bom para | Cuidado |
|---|---|---|
| PragerU, vídeos de 5 minutos e Real Talk (manual, sem feed) | Raízes judaico-cristãs do Ocidente, família, história, ideias | É material de defesa de ideias: toda afirmação histórica ou citação de "Pais Fundadores" é conferida na origem (Founders Online, documento), porque citação apócrifa circula muito nesse tema |
| Brasil Paralelo (manual: robots proíbe robôs) | História do Brasil e da Igreja, educação | Idem |
| First Things, The Gospel Coalition, ERLC (feed) | Teologia pública, ética, família | Opinião assinada |
| Federalist e Daily Wire (ensaios de família e fé) | Maternidade, casamento, legado | Opinião assinada |

## 3. Eliminatórios: a pauta não entra se

0. **É internacional sem impacto grande e direto no Brasil** e não é atemporal (seção 0).
1. **Não tem fonte primária encontrável** (documento, decisão, vídeo, postagem da pessoa, nota oficial). Só o portal
   dizendo não basta.
2. **É só opinião**, sem fato novo por trás (coluna, editorial, "o que eu acho de"). Opinião vira fonte de "O que
   dizem", nunca a notícia.
3. **É bastidor político sem fato** (revisado em 30/10/2026, pedido do responsável editorial: o leitor de direita
   quer política, e Flávio Bolsonaro, Nikolas Ferreira e a oposição **entram**): fica de fora só o que não tem fato
   verificável, como "fulano estaria articulando", "segundo aliados", especulação de candidatura ou troca de farpa
   em rede social sem consequência. Decisão de tribunal, ato de governo, votação, viagem, pedido formal, processo,
   declaração pública gravada e pesquisa registrada são fato e entram. A cobertura relata cada lado com a sua fonte.
4. **Fofoca ou celebridade sem fé**: a fé da pessoa precisa ser o assunto, dito por ela.
5. **Isca de raiva sem substância**: o fato, contado sem adjetivo, não interessa a ninguém.
6. **Trilha quente com mais de 7 dias** sem desdobramento novo (vale a data do fato, não a do portal).
7. **Atemporal sem conferência**: afirmação histórica ou citação que não achamos na origem.
8. **Sem foto com licença** (regra das notícias, `docs/FOTOS.md`). Foto do portal de origem não serve.
9. **Já publicada por nós**, mesmo vinda de outro portal.
10. **Não tem pertinência temática** (30/10/2026, pedido do responsável editorial, depois de Parque Circuito, seca no
    Rio Madeira e Presépio Vivente da prefeitura saírem no ar): o **próprio fato** precisa ser sobre um eixo do portal
    (`config/relevancia.json`, `temas`): fé e igreja; liberdade religiosa, de expressão ou de consciência; vida;
    família e proteção de crianças; educação dos filhos; **política nacional** (lideranças da direita e da oposição,
    como Flávio Bolsonaro e Nikolas Ferreira, eleições, Congresso, decisões de tribunais e do governo sobre a
    oposição). Assunto de cidade (obra, parque, clima, trânsito, polícia,
    serviço público) sem esse eixo **não entra, por mais local, útil ou comovente que seja**. A lente cristã da nossa
    análise não transforma a pauta: um versículo que "cabe", "pede oração" ou "pede resposta do cristão" vale para
    quase qualquer fato e **nunca conta como tema**. Teste em uma frase: "este fato é sobre ___" (o eixo) sem citar a
    nossa opinião. Na nota, `crivo.tema = {"eixo", "porque"}`; `checar_noticia.py` recusa nota sem eixo válido.

## 4. Pontuação: motor de relevância (0 a 100)

Pedido do responsável editorial em 30/10/2026: o crivo de 0 a 20 deixava passar muita coisa fraca, porque somava
potencial de viralização e "versículo que cabe" com o mesmo peso de fato com consequência. Vale a partir de
**31/10/2026**; as notas publicadas antes guardam o crivo antigo. A avaliação que motivou a troca está em
`docs/AVALIACAO_CRIVO_2026-10-30.md`.

Os pesos, as réguas e os cortes ficam em **`config/relevancia.json`** (mudam sem mexer no código; os pesos precisam
somar 100). Cada critério recebe de 0 até o peso, com o **porquê em fatos concretos da pauta** (não "é importante":
"decisão já vale para a rede estadual inteira"). Use a régua do critério para chegar ao número.

| Critério | Peso | Régua (pontos mínimos da faixa) |
|---|---|---|
| Impacto público | 30 | 25: muda regra, direito ou dinheiro público já valendo para um estado, o país ou milhares (decisão, lei sancionada, decreto, votação concluída) · 15: efeito concreto numa cidade, comunidade ou grupo (serviço essencial, obra, ato do prefeito, decisão de denominação ou convenção nacional) · 5: efeito possível ou futuro (projeto em tramitação, ação sem julgamento, pesquisa) · 0: declaração, evento, homenagem, polêmica |
| Afinidade com o público | 25 | 20: núcleo do portal com efeito direto no leitor (igreja e liberdade religiosa no Brasil; vida, família, educação dos filhos; ato do poder público, inclusive de Rondônia e Porto Velho, **só quando o ato é sobre um desses temas**) · 10: tema do portal com efeito indireto (outro país, debate sem caso aqui) · 0: lateral (e aí a pauta já caiu no eliminatório 10) |
| Atualidade e urgência | 20 | 17: até 48 h, ou prazo, votação ou julgamento nos próximos dias · 10: até 7 dias · 5: mais antigo com desdobramento ou gancho de calendário · 0: sem novidade |
| Qualidade da comprovação | 15 | 13: documento primário lido na íntegra e confirmação independente · 9: fonte oficial ou duas reportagens próprias independentes · 5: uma reportagem própria · 0: agregador, republicação ou declaração sem prova |
| Originalidade e aprofundamento | 10 | 8: acrescenta fato, número ou contexto que as fontes não deram · 4: síntese com contexto próprio · 0: reescrita de uma fonte |

Regras que o número não muda:
- **Pontuação alta não substitui verificação.** Comprovação abaixo de **9** não publica, qualquer que seja o total:
  volte à apuração. Acusação grave, conteúdo jurídico sensível ou fato contestado pede revisão humana antes de sair.
- **Volume não é relevância.** Cinco portais repetindo a mesma nota de assessoria valem uma fonte: agrupe por
  acontecimento, ache a origem e pontue o acontecimento, não as manchetes.
- **Declaração sem consequência fica embaixo**: uma decisão judicial com efeito concreto pontua mais que a fala genérica
  de um político, e uma pesquisa de outro país pontua pouco em impacto, por mais que viralize.
- **Interesse público vence preferência.** Fato verdadeiro e relevante entra mesmo quando desfavorável a quem está
  perto da linha do portal; a régua é a mesma para todos os lados.
- Os eliminatórios da seção 3 continuam valendo antes da pontuação.

### Faixas e cortes

| Nota | Faixa | Decisão |
|---|---|---|
| 85 a 100 | Prioridade máxima | Escreva primeiro; candidata a manchete |
| 70 a 84 | Alta relevância | Publica; manchete só daqui para cima |
| 60 a 69 | Relevância moderada | Só para completar o dia, nunca como manchete |
| 0 a 59 | Moderada baixa ou baixa prioridade | Não entra (`checar_noticia.py` recusa) |

**Mistura do dia**: a manchete é a maior nota do dia (e precisa de 70 ou mais). Publica-se o que passa, não uma cota:
melhor 3 notas fortes que 5 com enchimento.

Na nota, o crivo fica registrado assim (`checar_noticia.py` confere a soma, o teto de cada peso, as justificativas, o
corte, o piso de comprovação e a abrangência; a página não mostra o motor: mostra o crivo público da seção 4.1):

```json
"crivo": {
  "escala": 100,
  "pontos": 77,
  "trilha": "quente",
  "abrangencia": "rondonia",
  "tema": {"eixo": "educacao", "porque": "A decisão muda a régua do gasto mínimo com educação da rede estadual"},
  "origem": {"nome": "Rondônia Dinâmica", "url": "https://..."},
  "criterios": {
    "impacto": {"pontos": 23, "porque": "Decisão do STF tira da lei estadual a regra que ...; ainda cabe agravo"},
    "afinidade": {"pontos": 18, "porque": "..."},
    "atualidade": {"pontos": 13, "porque": "..."},
    "comprovacao": {"pontos": 15, "porque": "Íntegra da decisão lida no portal do STF ..."},
    "originalidade": {"pontos": 8, "porque": "..."}
  }
}
```

A viralização e a lente cristã não somam mais pontos: entram na escolha do ângulo, na chamada (seção 7) e no toque
(seção 5), depois que a pauta já provou que importa.

### 4.1 Crivo público: o que a página mostra

Pedido do responsável editorial em 30/10/2026: o motor de 0 a 100 é a **ferramenta interna de escolha** e não vai
para o site. A seção "Por que esta notícia entrou" mostra o crivo de até 20 pontos, com a lista de critérios, como
nas primeiras notas (mais claro e mais bonito para o leitor). Ele **não decide nada**: quem decide se a nota entra são
os eliminatórios (seção 3, incluído o 10, de pertinência temática) e o motor. Depois de aprovada, a nota recebe a
versão pública em `crivo.publico`, marcando com honestidade as perguntas da tabela abaixo que o fato responde:

```json
"publico": {"pontos": 11, "eixos": {"valor": 8, "viral": 2, "cristao": 1},
            "criterios": ["Documento primário: íntegra da decisão do STF (2)", "Proximidade: Rondônia (2)", "..."]}
```

`checar_noticia.py` confere que cada critério termina com os pontos entre parênteses, que a soma bate com o total e
com os eixos e que cada eixo respeita o teto. A passagem bíblica pode aparecer aqui como critério de apresentação,
mas nunca serve para a pauta entrar (eliminatório 10).

#### A. Valor jornalístico (até 8)

| Pergunta | Pontos |
|---|---|
| Há **documento primário** com link na nota (processo, decisão, lei, relatório, vídeo integral)? | 2 |
| É **decisão ou ato de quem tem poder** (tribunal, Congresso, governo, plebiscito, denominação grande) ou atinge milhares de pessoas? | 2 |
| **Proximidade**: é de Rondônia ou Porto Velho, ou é nacional? (Internacional só ganha estes pontos se o mesmo projeto, decisão ou caso estiver aqui ou afetar brasileiros diretamente) | 2 |
| Tem **número forte com fonte** (pesquisa com ficha técnica, estatística oficial)? | 1 |
| Está confirmada por **duas fontes independentes**? | 1 |

#### B. Potencial de viralização (até 7)

Os seis princípios de *Contágio* (Jonah Berger) e a pesquisa de Berger e Milkman (emoção de alta ativação se
compartilha), em perguntas objetivas:

| Pergunta | Pontos |
|---|---|
| **Emoção de alta ativação** que o fato provoca sozinho, sem adjetivo nosso: indignação justa, admiração, esperança, espanto? Teste: dá para dizer a emoção numa palavra. | 1 |
| Tem **personagem com nome** (pastor, mãe, atleta, juiz), não só instituição? | 1 |
| **Contraria a narrativa dominante** ou surpreende? Teste: cabe numa frase "X, apesar de Y" ou "ninguém contou que…". | 1 |
| **Moeda social**: quem compartilha parece bem informado (dado inédito, documento, bastidor que a grande imprensa não deu)? | 1 |
| **Utilidade**: o leitor pode fazer algo com isso (orar, votar, proteger o filho, conhecer um direito, ajudar alguém)? | 1 |
| **Gatilho no calendário**: está na conversa da semana (eleição, julgamento marcado, data cristã, estreia, assunto em alta)? | 1 |
| **Cabe num cartão**: o fato inteiro cabe em até 15 palavras e tem foto que mostra o fato? | 1 |

#### C. Relevância cristã (até 5)

| Pergunta | Pontos |
|---|---|
| Há **uma passagem bíblica que um pastor usaria** sobre o assunto, sem forçar? | 2 |
| Mostra **fé vivida**: testemunho, coragem, perseguição, caridade, arrependimento? | 1 |
| **Pede resposta do cristão**: oração, cuidado, posicionamento, conhecimento para conversar com os filhos? | 1 |
| **Rende estudo** ou série (tema que volta: vida, casamento, liberdade, Reforma, perseguição)? | 1 |

## 5. O nosso toque: a lente cristã

O fato fica neutro (título, lide, números, contexto, No Brasil). O toque vai em três lugares, em três movimentos:

1. **Por que importa** (30 a 70 palavras): o que o fato **revela**. Não repete o lide; diz o que está em jogo para
   a família, a igreja ou a liberdade.
2. **O que muda para você**: o que o leitor cristão **faz** com isso (orar por quem, como conversar com os filhos,
   que direito existe, o que acompanhar).
3. **Nossa opinião** (20 a 60 palavras): o **nosso posicionamento** sobre o fato, dito com todas as letras (a gente
   apoia, concorda, discorda, cobra, recomenda), o porquê e um conselho concreto. Uma frase curta e citável para quem
   compartilha. **Sem versículo no meio** (pedido do responsável editorial, 30/10/2026): quando uma passagem cabe, ela
   vai no campo `versiculo` (`{"texto", "referencia", "traducao"}`) e aparece embaixo da opinião, em linha separada.

Regras do toque:
- Versículo que cabe, nunca enfeite, e sempre no campo `versiculo`, nunca dentro do texto da opinião. Se não há
  passagem óbvia, a nota sai sem versículo, e tudo bem.
- Firme na convicção, manso no tom (1 Pedro 3.15). Sem torcida partidária, sem desprezo por quem pensa diferente.
- Esperança onde houver: perseguição com o testemunho de quem resiste; derrota com o que a Igreja faz agora.
- Na trilha atemporal, a nota precisa de um **gancho de hoje** (data, aniversário, estreia, debate da semana) no
  lide: "No Dia da Reforma, …", "Com a estreia de …".

## 6. Tradução e adaptação

- Cargos e instituições em português, com o original na primeira menção: "Assembleia Legislativa da Virgínia
  (House of Delegates)".
- Explique o que o leitor brasileiro não conhece: plebiscito estadual, "Planned Parenthood", Roe e Dobbs.
- Números com a nossa pontuação (41%, 5.835 pessoas, US$ 2 milhões ≈ R$ … só com a cotação e a data).
- Citação traduzida: "(tradução livre)" no nome da fonte em "O que dizem".
- Termos de guerra cultural ("woke", "MAGA", "radical left") não entram no texto neutro; numa citação, ficam
  entre aspas e atribuídos.

## 7. Chamada para redes

A chamada (`conteudo/chamadas.json`) usa o que faz uma notícia circular: a emoção, o personagem, o contraste. Tudo o que ela promete
está na nota. Proibido "chocante", "a mídia esconde", "compartilhe antes que apaguem", CAIXA ALTA e urgência falsa.
A pergunta final convida o leitor cristão a responder ("Você conversaria sobre isso com seus filhos?").
