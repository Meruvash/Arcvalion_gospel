---
name: noticias
description: Monta a edição diária de notícias do portal — coleta (feeds e portais conservadores, com prioridade nacional, depois Rondônia e Porto Velho), crivo editorial de 0 a 20 (docs/CRIVO_NOTICIAS.md), no mínimo 5 notas por dia (2 com Opinião Forte; meta de 11 pontos ou mais) no padrão das notícias (docs/PADRAO_EDITORIAL.md), foto com licença, atualização dos blocos da home, build e publicação automática. Cópia da skill noticias do Elite Boardgamers. Use quando pedirem "/noticias", "edição do dia", "notícias de hoje" ou quando a tarefa agendada diária disparar.
---

# Edição diária de notícias

Meta: **no mínimo 5 notas por dia** que passem nos eliminatórios e tenham **11 pontos ou mais** no crivo de 0 a 20 (`docs/CRIVO_NOTICIAS.md`). **Prioridade geográfica** (pedido do responsável editorial, 30/10/2026): primeiro notícias **nacionais**, depois de **Rondônia**, depois de **Porto Velho**; internacional só com impacto grande e direto no Brasil, de preferência atemporal. Mistura do dia: pelo menos 3 nacionais, 1 de Rondônia ou Porto Velho quando houver pauta que passe no crivo, no máximo 1 internacional. A pauta nasce em **portais conservadores consolidados**; o fato é confirmado na fonte primária e o texto é nosso (tradução reescrita, nunca a matéria inteira). **2 de cada 5 notas saem com Opinião Forte** (`"opiniao_forte": true`; diretriz em docs/PADRAO_EDITORIAL.md, "Opinião Forte"): escolha para elas os assuntos em que o portal tem tese clara e defensável (decisões de governo, Congresso e tribunais, liberdade religiosa, família, vida); as outras 3 seguem o tom padrão. **A rotina publica sozinha** (ordem do responsável editorial, 29/10/2026): cada nota é escrita com `"status": "revisao"`, passa em `tools/noticias/checar_noticia.py` e é publicada com `python3 tools/publicar.py aprovar <arquivo> --revisor anderson-pelicioni-de-castro --automatica`. Nota que não passa no validador não é publicada. A conferência é diária (ferramenta de revisão das 18h e skill `verificacao`).

## 1. Coletar, em até três rodadas

Depois de cada rodada, pontue as candidatas novas (seção 2). Com 5 notas de 11 pontos ou mais, na mistura do dia, pare.

**Rodada 1: feeds.** `python3 tools/editorial/coletar.py --dias 2` (`--dias 4` na segunda-feira). Lê os feeds de `config/fontes.json` respeitando o robots.txt e grava `.cache/pauta/<data>.md`. Os portais conservadores (`"conservador": true`: Daily Signal, Daily Wire, Federalist, Free Beacon, Christian Post, Faithwire, Live Action, Fox, National Review, WORLD, O Antagonista, Crusoé, Pleno News…) aparecem marcados, e cada item mostra a abrangência (Brasil, Rondônia, Porto Velho, internacional); nacional e Rondônia sobem na lista, internacional não. Depois da rodada 1, leia as fontes primárias de Rondônia e Porto Velho que não têm feed (ALE-RO, Prefeitura e Câmara de Porto Velho, TJ-RO, MP-RO, Arquidiocese de Porto Velho, igrejas evangélicas do estado) e o Rondônia Ao Vivo.

**Rodada 2: portais conservadores lidos um a um** (seção 2 de `docs/CRIVO_NOTICIAS.md`): Gazeta do Povo, Revista Oeste, LifeSiteNews, The Free Press e, para a trilha atemporal, PragerU (vídeos de 5 minutos e Real Talk) e Brasil Paralelo. WebSearch e WebFetch de uma página por vez (leitura pontual com link, nunca raspagem). Para cada pauta boa, **suba até a origem**: o processo, a decisão, o vídeo, a postagem da pessoa, o relatório.

**Rodada 3: fontes do mundo cristão.** Portais gospel que proíbem robôs (Gospel Prime, Gospel Mais, Comunhão), denominações e convenções, Portas Abertas, Frente Parlamentar Evangélica, STF, Christianity Today, Premier, Pew, Lifeway.

## 2. Escolher as notas (crivo)

Siga `docs/CRIVO_NOTICIAS.md`: primeiro os **eliminatórios** (assunto que só se sustenta acusando pessoa identificável de crime ou má-fé sem fonte oficial, o crivo jurídico; sem fonte primária, só opinião, política partidária pura, celebridade sem fé, isca de raiva, quente com mais de 7 dias, atemporal sem conferência, sem foto com licença, repetida), depois os **três eixos**: valor jornalístico (até 8), potencial de viralização (até 7) e relevância cristã (até 5). Cada linha do crivo é uma pergunta de sim ou não; anote quais valeram.

Cortes: 14 a 20 é pauta forte (candidata a manchete); 11 a 13 publica; 8 a 10 só se faltar nota, nunca como manchete; abaixo de 8 não entra (`checar_noticia.py` recusa). Agrupe o que for do mesmo assunto. A de maior pontuação é a manchete (`"manchete": true`); `checar_noticia.py` recusa manchete que não seja a maior do dia.

Registre na nota: `"crivo": {"pontos": 15, "trilha": "quente", "eixos": {"valor": 6, "viral": 5, "cristao": 4}, "origem": {"nome": "<portal>", "url": "<matéria>"}, "criterios": [...]}`.

## 3. Escrever

Uma nota por arquivo em `conteudo/noticias/<AAAA-MM-DD>-<assunto>.json`, no **padrão das notícias** (docs/PADRAO_EDITORIAL.md): `categoria` (slug da editoria), `selo` (Boa notícia, Vale acompanhar, Para refletir, Motivo de alerta, Informativo), `titulo` (8 a 16 palavras, sem caça-clique), `lide` (35 a 70), `por_que_importa` (30 a 70, análise nossa), `numeros` (2 a 4, cada um com fonte), `corpo` (1 a 3 parágrafos, 40 a 200 palavras), `no_brasil` (25 a 80), `critica` → seção "O que dizem" (1 a 3 posições atribuídas; `citacao: true` só com frase literal lida na página indicada em `url`), `para_quem` e `nao_e_para`, `veredito` (20 a 60, "Nossa opinião"), `fontes` (2 ou mais, com `tipo` primaria/secundaria e data), `crivo` (pontos e critérios), `instituicao` (quem fez o fato: "Senado Federal", "CGADB"), `estudos` (estudos nossos citados), `imagem` (arquivo, crédito com licença, alt), `ia` (`{"usada": true, "uso": "pesquisa, organização e primeira versão do texto"}`), `status: "revisao"`.

**O nosso toque** (seção 5 de `docs/CRIVO_NOTICIAS.md`): Por que importa diz o que o fato revela; O que muda para você, o que o leitor cristão faz com ele; Nossa opinião traz a passagem bíblica (com referência e tradução) e um conselho claro, com uma frase curta e citável. Tradução e adaptação: seção 6 do mesmo documento.

Regras de texto (as do Elite, adaptadas): fato tem fonte, opinião tem dono; o tom opinativo só em Por que importa, O que muda para você (`para_quem`) e Nossa opinião; Pontos de atenção (`nao_e_para`, 1 a 3 itens, obrigatório) traz só o que está pendente ou incerto, com fonte; título, lide, números, contexto e No Brasil são neutros. Em política, relate cada lado com a sua fonte; a perspectiva cristã e conservadora aparece na opinião e na escolha da pauta, nunca na distorção do fato. Nada de adjetivo de torcida (detonou, lacrou, humilhou). Nas notas com Opinião Forte, o tom inteligente, irônico e firme vale só em Por que importa, O que muda para você e Nossa opinião, seguindo as 10 regras da diretriz (tese única, tom nascido do fato, alvo em decisões e nunca em pessoas, o lado contrário com seu melhor argumento em O que dizem, frase citável no veredito). Citação literal só de frase que você leu na fonte. Loja de varejo não aparece no texto. **Crivo jurídico** (docs/PADRAO_EDITORIAL.md): faça a leitura hostil de cada frase de opinião (como a pessoa citada e como um juiz leriam); nada de imputar crime ou intenção sem fonte oficial, crítica só a atos públicos, nada que desqualifique grupos, nada de duplo sentido; registre em `"checagem_juridica"` o que foi conferido (o validador exige e bloqueia rótulos como corrupto, criminoso, bandido, golpista nas partes de opinião).

**Foto é obrigatória** (skill `imagens`): `python3 tools/fotos.py buscar <slug>` procura nas páginas das `fontes` da nota (e em `--url`, `--tema` ou `--commons`), monta `.cache/fotos/<slug>/folha.jpg`; abra a folha com Read, escolha pelo que a foto mostra e grave com `python3 tools/fotos.py aprovar <slug> <n> --alt "..."`. Candidata "a confirmar" ou bloqueada fica para a redação. Com o link exato de uma foto de licença conhecida, `python3 tools/imagens/baixar.py <url> <slug>.jpg --credito "..." --pagina <url>`. Sem foto com licença, troque de notícia. Nunca gere imagem por IA. Regras em `docs/FOTOS.md`.

`python3 tools/noticias/checar_noticia.py conteudo/noticias/<arquivo>.json` precisa passar (os avisos de vício de texto pedem reescrita com um fato concreto).

## 4. Atualizar os blocos da home

`conteudo/home.json`: `em_alta` (Destaques: assuntos mais citados nas notas dos últimos 7 dias, cada um ligado a uma nota com o assunto no título) e `campanhas` (Missões e campanhas, com fonte). `conteudo/agenda.json`: eventos com data, local e fonte; tire o que passou.

## 5. Publicação e build

1. Para cada nota que passou no validador: `python3 tools/publicar.py aprovar conteudo/noticias/<arquivo>.json --revisor anderson-pelicioni-de-castro --automatica`.
2. `python3 tools/build_home.py` e `python3 tools/checar_seo.py`.
3. Confira no celular (Playwright, 390 px) a home e cada nota: sem rolagem lateral, foto certa, crédito visível.
4. Commit e push na `main` do repositório do portal: `Notícias de <dd/mm/aaaa>: <títulos curtos>`. O deploy publica o site.
5. Escreva em `conteudo/chamadas.json` a `chamada` e a `pergunta` de cada nota (regras de "Chamadas para redes" do padrão). `python3 tools/divulgacao.py` gera os textos de WhatsApp, Telegram e Instagram.
6. Resumo para a redação: rodadas feitas e o que cada uma achou, as notas publicadas (título, selo, pontos, fonte primária, link), a manchete e o que ficou de fora e por quê.
