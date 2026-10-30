---
name: noticias
description: Monta a edição diária de notícias do portal — coleta (feeds de fontes primárias e gospel), crivo editorial, no mínimo 5 notas por dia (2 delas com Opinião Forte; meta de 5 pontos ou mais) no padrão das notícias (docs/PADRAO_EDITORIAL.md), foto com licença, atualização dos blocos da home, build e publicação automática. Cópia da skill noticias do Elite Boardgamers. Use quando pedirem "/noticias", "edição do dia", "notícias de hoje" ou quando a tarefa agendada diária disparar.
---

# Edição diária de notícias

Meta: **no mínimo 5 notas por dia** que passem nos eliminatórios e no padrão, como no Elite. As três rodadas de pesquisa servem para chegar a 5 notas com **5 pontos ou mais**. **2 de cada 5 notas saem com Opinião Forte** (`"opiniao_forte": true`; diretriz em docs/PADRAO_EDITORIAL.md, "Opinião Forte"): escolha para elas os assuntos em que o portal tem tese clara e defensável (decisões de governo, Congresso e tribunais, liberdade religiosa, família, vida); as outras 3 seguem o tom padrão. **A rotina publica sozinha** (ordem do responsável editorial, 29/10/2026): cada nota é escrita com `"status": "revisao"`, passa em `tools/noticias/checar_noticia.py` e é publicada com `python3 tools/publicar.py aprovar <arquivo> --revisor anderson-pelicioni-de-castro --automatica`. Nota que não passa no validador não é publicada. A conferência é diária (ferramenta de revisão das 18h e skill `verificacao`).

## 1. Coletar, em até três rodadas

Depois de cada rodada, pontue as candidatas novas (seção 2). Com 5 notas de 5 pontos ou mais, pare.

**Rodada 1: fontes automáticas.** `python3 tools/editorial/coletar.py --dias 2` (`--dias 4` na segunda-feira). Lê os feeds de `config/fontes.json` respeitando o robots.txt e grava `.cache/pauta/<data>.md`, já ordenado (fontes primárias e temas do portal primeiro).

**Rodada 2: fontes nacionais lidas uma a uma.** Portais gospel que proíbem robôs (Gospel Prime, Gospel Mais, Comunhão, Guiame, Pleno News, Aliança Cristã Evangélica), sites das denominações e convenções (CGADB, CONAMAD, Convenção Batista Brasileira, Igreja Presbiteriana do Brasil, Igreja Universal, Lagoinha, Bola de Neve e outras), Portas Abertas (perseguição religiosa), Frente Parlamentar Evangélica, STF, Diário Oficial da União. Use WebSearch e WebFetch de uma página por vez (leitura pontual com citação e link, nunca raspagem). Busca em português: "igreja evangélica notícia hoje", "liberdade religiosa Brasil", "Frente Parlamentar Evangélica", "<denominação> nota oficial".

**Rodada 3: internacionais.** Christianity Today, Christian Post, Premier Christian News, Evangelical Focus, Pew Research, relatório Portas Abertas/Open Doors, comunicados de organizações cristãs internacionais com efeito no Brasil.

## 2. Escolher as notas (crivo)

**Eliminatórios (não entra):** sem fonte primária identificável (boato, "fontes dizem", post sem confirmação); conteúdo pago ou release sem fato novo; mais de 7 dias de atraso; já publicada por nós; assunto sem relação com fé, família, igreja ou sociedade; fato que só existe numa reportagem de outro veículo sem confirmação na fonte primária.

**Pontuação:**

| Critério | Pontos |
|---|---|
| Decisão de Congresso, governo ou tribunal com efeito sobre igrejas, famílias ou liberdade religiosa | 4 |
| Acontecimento relevante do mundo evangélico no Brasil (denominação, liderança, missão, evento grande) | 4 |
| Liberdade religiosa e perseguição a cristãos (Brasil ou exterior), com dado verificável | 3 |
| Tema que já tem estudo bíblico nosso ou rende estudo | 3 |
| Dado novo de pesquisa (IBGE, Datafolha, Pew, Lifeway) sobre fé e família | 3 |
| Confirmada por duas fontes independentes | 2 |
| Evento cristão grande com data e local confirmados | 2 |

Agrupe o que for do mesmo assunto. A de maior pontuação é a manchete (`"manchete": true`); `checar_noticia.py` recusa manchete que não seja a maior do dia.

## 3. Escrever

Uma nota por arquivo em `conteudo/noticias/<AAAA-MM-DD>-<assunto>.json`, no **padrão das notícias** (docs/PADRAO_EDITORIAL.md): `categoria` (slug da editoria), `selo` (Boa notícia, Vale acompanhar, Para refletir, Motivo de alerta, Informativo), `titulo` (8 a 16 palavras, sem caça-clique), `lide` (35 a 70), `por_que_importa` (30 a 70, análise nossa), `numeros` (2 a 4, cada um com fonte), `corpo` (1 a 3 parágrafos, 40 a 200 palavras), `no_brasil` (25 a 80), `critica` → seção "O que dizem" (1 a 3 posições atribuídas; `citacao: true` só com frase literal lida na página indicada em `url`), `para_quem` e `nao_e_para`, `veredito` (20 a 60, "Nossa opinião"), `fontes` (2 ou mais, com `tipo` primaria/secundaria e data), `crivo` (pontos e critérios), `instituicao` (quem fez o fato: "Senado Federal", "CGADB"), `estudos` (estudos nossos citados), `imagem` (arquivo, crédito com licença, alt), `ia` (`{"usada": true, "uso": "pesquisa, organização e primeira versão do texto"}`), `status: "revisao"`.

Regras de texto (as do Elite, adaptadas): fato tem fonte, opinião tem dono; o tom opinativo só em Por que importa, O que muda para você (`para_quem`) e Nossa opinião; Pontos de atenção (`nao_e_para`, 1 a 3 itens, obrigatório) traz só o que está pendente ou incerto, com fonte; título, lide, números, contexto e No Brasil são neutros. Em política, relate cada lado com a sua fonte; a perspectiva cristã e conservadora aparece na opinião e na escolha da pauta, nunca na distorção do fato. Nada de adjetivo de torcida (detonou, lacrou, humilhou). Nas notas com Opinião Forte, o tom inteligente, irônico e firme vale só em Por que importa, O que muda para você e Nossa opinião, seguindo as 10 regras da diretriz (tese única, tom nascido do fato, alvo em decisões e nunca em pessoas, o lado contrário com seu melhor argumento em O que dizem, frase citável no veredito). Citação literal só de frase que você leu na fonte. Loja de varejo não aparece no texto.

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
