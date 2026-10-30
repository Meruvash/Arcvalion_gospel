# Crivo de escolha das notícias

Pedido do responsável editorial em 30/10/2026: as primeiras notas saíram fracas e genéricas (comissão da Câmara,
pesquisa do Pew). A pauta passa a nascer em **portais conservadores consolidados** dos EUA e do Brasil, traduzida e
reescrita por nós, com duas trilhas (**quente** e **atemporal**) e com o nosso toque: a relevância cristã do fato.
Este documento diz onde procurar, o que elimina uma pauta, como pontuar (0 a 20) e como escrever o toque.
Modelo do crivo: o do Elite Boardgamers (eliminatórios, depois pontos; manchete é a maior nota do dia).

Teste de 30/10/2026, com notícias reais: `docs/TESTE_CRIVO_2026-10-30.md`.

## 0. Prioridade geográfica (30/10/2026)

Pedido do responsável editorial: a edição é **nacional primeiro**, depois **Rondônia**, depois **Porto Velho**.

| Ordem | Abrangência | Quando entra |
|---|---|---|
| 1 | Brasil | Sempre: é o núcleo da edição (pelo menos 3 das 5 notas do dia) |
| 2 | Rondônia | Toda pauta do estado que passe no crivo (meta: 1 por dia) |
| 3 | Porto Velho | Toda pauta da capital que passe no crivo |
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
| Revista Oeste, Crusoé, O Antagonista (feed parcial) | Política, Judiciário, liberdade de expressão | Política partidária pura não entra (seção 3) |
| Pleno News, Guiame (feed) | Igrejas e pastores no Brasil, perseguição traduzida | Agregadores: quase nunca são a origem |
| Jovem Pan (feed com filtro) | Repercussão no Congresso | — |

**Rondônia e Porto Velho**

| Fonte | Como acompanhar |
|---|---|
| Governo de Rondônia (feed, primária), Rondoniagora, G1 Rondônia, News Rondônia (feed) | rodada 1, com filtro de temas, leis, Assembleia, Câmara, prefeitura, Justiça, MP, Conselho Tutelar e segurança |
| Assembleia Legislativa (ALE-RO), Prefeitura e Câmara de Porto Velho, TJ-RO, MP-RO, Arquidiocese de Porto Velho, convenções e igrejas evangélicas do estado | manual (sem feed ou robots proíbe): fontes primárias para confirmar |
| Rondônia Ao Vivo, Rondônia Dinâmica, Tudo Rondônia | manual (sem feed válido ou bloqueio) |

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
3. **É política partidária pura**: pesquisa eleitoral, briga de candidato, escândalo sem eixo de fé, família, vida,
   educação ou liberdade (religiosa, de expressão, de consciência).
4. **Fofoca ou celebridade sem fé**: a fé da pessoa precisa ser o assunto, dito por ela.
5. **Isca de raiva sem substância**: o fato, contado sem adjetivo, não interessa a ninguém.
6. **Trilha quente com mais de 7 dias** sem desdobramento novo (vale a data do fato, não a do portal).
7. **Atemporal sem conferência**: afirmação histórica ou citação que não achamos na origem.
8. **Sem foto com licença** (regra das notícias, `docs/FOTOS.md`). Foto do portal de origem não serve.
9. **Já publicada por nós**, mesmo vinda de outro portal.

## 4. Pontuação (0 a 20)

Cada linha é uma pergunta de sim ou não, para duas pessoas chegarem à mesma nota. Some os três eixos.

### A. Valor jornalístico (até 8)

| Pergunta | Pontos |
|---|---|
| Há **documento primário** com link na nota (processo, decisão, lei, relatório, vídeo integral)? | 2 |
| É **decisão ou ato de quem tem poder** (tribunal, Congresso, governo, plebiscito, denominação grande) ou atinge milhares de pessoas? | 2 |
| **Proximidade**: é de Rondônia ou Porto Velho, ou é nacional? (Internacional só ganha estes pontos se o mesmo projeto, decisão ou caso estiver aqui ou afetar brasileiros diretamente) | 2 |
| Tem **número forte com fonte** (pesquisa com ficha técnica, estatística oficial)? | 1 |
| Está confirmada por **duas fontes independentes**? | 1 |

### B. Potencial de viralização (até 7)

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

### C. Relevância cristã (até 5)

| Pergunta | Pontos |
|---|---|
| Há **uma passagem bíblica que um pastor usaria** sobre o assunto, sem forçar? | 2 |
| Mostra **fé vivida**: testemunho, coragem, perseguição, caridade, arrependimento? | 1 |
| **Pede resposta do cristão**: oração, cuidado, posicionamento, conhecimento para conversar com os filhos? | 1 |
| **Rende estudo** ou série (tema que volta: vida, casamento, liberdade, Reforma, perseguição)? | 1 |

### Cortes

| Nota | Decisão |
|---|---|
| 14 a 20 | Pauta forte: candidata a manchete; escreva primeiro |
| 11 a 13 | Publica |
| 8 a 10 | Só se faltar nota no dia, e nunca como manchete |
| 0 a 7 | Não entra |

**Mistura do dia** (5 notas, 2 com Opinião Forte): pelo menos 3 nacionais, 1 de Rondônia ou Porto Velho quando
houver pauta que passe, no máximo 1 internacional (de preferência atemporal), e pelo menos 1 atemporal por dia. Empate: a mais recente e com mais fontes primárias.

Na nota, o crivo fica registrado assim (`checar_noticia.py` confere a soma, os limites, o corte e a abrangência):

```json
"crivo": {
  "pontos": 15,
  "trilha": "quente",
  "abrangencia": "nacional",
  "eixos": {"valor": 6, "viral": 5, "cristao": 4},
  "origem": {"nome": "The Christian Post", "url": "https://..."},
  "criterios": ["Documento primário (2)", "Ato de poder: plebiscito (2)", "..."]
}
```

## 5. O nosso toque: a lente cristã

O fato fica neutro (título, lide, números, contexto, No Brasil). O toque vai em três lugares, em três movimentos:

1. **Por que importa** (30 a 70 palavras): o que o fato **revela**. Não repete o lide; diz o que está em jogo para
   a família, a igreja ou a liberdade.
2. **O que muda para você**: o que o leitor cristão **faz** com isso (orar por quem, como conversar com os filhos,
   que direito existe, o que acompanhar).
3. **Nossa opinião** (20 a 60 palavras): o que a **Escritura** diz, com a referência e a tradução (ex.: "Provérbios
   31.8, NVI"), e um conselho claro. Uma frase curta e citável para quem compartilha.

Regras do toque:
- Versículo que cabe, nunca enfeite. Se não há passagem óbvia, a nota não ganha os 2 pontos de C, e tudo bem.
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

A chamada (`conteudo/chamadas.json`) usa o eixo B: a emoção, o personagem, o contraste. Tudo o que ela promete
está na nota. Proibido "chocante", "a mídia esconde", "compartilhe antes que apaguem", CAIXA ALTA e urgência falsa.
A pergunta final convida o leitor cristão a responder ("Você conversaria sobre isso com seus filhos?").
