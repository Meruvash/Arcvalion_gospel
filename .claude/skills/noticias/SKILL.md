---
name: noticias
description: Monta a edição diária de notícias do portal — coleta (feeds de fontes primárias e gospel), crivo editorial, no mínimo 3 notas por dia na fase de teste (meta de 5 pontos ou mais) no padrão das notícias (docs/PADRAO_EDITORIAL.md), foto com licença, atualização dos blocos da home, build e envio para a prévia de revisão. Cópia da skill noticias do Elite Boardgamers, com uma diferença: nada vai ao ar sem revisão humana. Use quando pedirem "/noticias", "edição do dia", "notícias de hoje" ou quando a tarefa agendada diária disparar.
---

# Edição diária de notícias

Meta da fase de teste: **3 notas por dia** que passem nos eliminatórios e no padrão (o Elite publica no mínimo 5). As três rodadas de pesquisa servem para chegar a 3 notas com **5 pontos ou mais**. **Nada é publicado pela rotina**: as notas saem com `"status": "revisao"` e aparecem só em `/previa/` (fora do Google), até uma pessoa revisora aprovar (`tools/publicar.py aprovar ... --revisor <slug>`).

## 1. Coletar, em até três rodadas

Depois de cada rodada, pontue as candidatas novas (seção 2). Com 3 notas de 5 pontos ou mais, pare.

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

Regras de texto (as do Elite, adaptadas): fato tem fonte, opinião tem dono; o tom opinativo só em Por que importa, Interessa a você se…, Pense duas vezes se… e Nossa opinião; título, lide, números, contexto e No Brasil são neutros. Em política, relate cada lado com a sua fonte; a perspectiva cristã e conservadora aparece na opinião e na escolha da pauta, nunca na distorção do fato. Nada de adjetivo de torcida (detonou, lacrou, humilhou). Citação literal só de frase que você leu na fonte. Loja de varejo não aparece no texto.

**Foto é obrigatória** (skill `imagens`): `python3 tools/imagens/baixar.py <url> <slug>.jpg --credito "..." --pagina <url>`. Sem foto com licença, troque de notícia. Nunca gere imagem por IA.

`python3 tools/noticias/checar_noticia.py conteudo/noticias/<arquivo>.json` precisa passar (os avisos de vício de texto pedem reescrita com um fato concreto).

## 4. Atualizar os blocos da home

`conteudo/home.json`: `em_alta` (Destaques: assuntos mais citados nas notas dos últimos 7 dias, cada um ligado a uma nota com o assunto no título) e `campanhas` (Missões e campanhas, com fonte). `conteudo/agenda.json`: eventos com data, local e fonte; tire o que passou.

## 5. Build e prévia

1. `python3 tools/build.py` e `python3 tools/checar_seo.py publico`.
2. Confira no celular (Playwright, 390 px) a `/previa/` e cada nota: sem rolagem lateral, foto certa, crédito visível.
3. Commit e push na `main` do repositório do portal: `Notícias de <dd/mm/aaaa> para revisão: <títulos curtos>`. O deploy publica o site com as notas só na prévia.
4. Escreva em `conteudo/chamadas.json` a `chamada` e a `pergunta` de cada nota (regras de "Chamadas para redes" do padrão). Depois da aprovação, `python3 tools/divulgacao.py` gera os textos de WhatsApp, Telegram e Instagram.
5. Resumo para a redação: rodadas feitas e o que cada uma achou, as notas (título, selo, pontos, fonte primária), a manchete, o que ficou de fora e por quê, o link de cada prévia (`<site>/previa/noticias/<slug>/`) e o comando de aprovação.
