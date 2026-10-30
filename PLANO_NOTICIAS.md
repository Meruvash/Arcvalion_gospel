# Plano da página inicial de notícias

A página inicial de meruvash.github.io/Arcvalion_gospel passa a ser um portal de notícias de jogos de tabuleiro, no formato do BoardGameGeek e da Ludopedia: manchete, últimas notícias, jogos em alta, lançamentos no Brasil, financiamentos, agenda e as nossas resenhas. Toda notícia passa por um crivo editorial, como as fotos e as resenhas já passam.

## 1. Como BGG e Ludopedia montam a página inicial

| Bloco | BoardGameGeek | Ludopedia | Nós |
|---|---|---|---|
| Notícias | BGG News (W. Eric Martin), lista cronológica | Notícias da comunidade e das editoras | Manchete + últimas notícias, com crivo |
| Jogos em alta | The Hotness (mais acessados) | Ranking e jogos em destaque | "Em alta": jogos que mais aparecem nas notícias da semana e nas nossas resenhas |
| Lançamentos | Novos itens no banco de dados | Lançamentos nacionais | "Chegando ao Brasil": anúncios e pré-vendas das editoras nacionais |
| Financiamento | Crowdfunding em destaque | Pouco destaque | Campanhas relevantes no Catarse, Kickstarter e Gamefound |
| Eventos | Fóruns e agenda | Eventos e encontros | Agenda: prêmios, feiras (Essen, Gen Con, Diversão Offline) |
| Conteúdo próprio | Reviews de usuários | Resenhas e vídeos | Nossas resenhas de jogos premiados |

## 2. Estrutura da nova página inicial

Ordem no celular, de cima para baixo:

1. **Manchete**: a notícia mais relevante do dia, com foto, título, lide e fonte.
2. **Últimas notícias**: 6 a 8 cartões com data, título, uma linha de resumo, selo da categoria e fonte.
3. **Chegando ao Brasil**: lançamentos e pré-vendas das editoras nacionais.
4. **Em alta**: 5 jogos com capa, cada um com a notícia ou resenha que o colocou ali.
5. **Financiamentos**: campanhas ativas que passam no crivo, com meta, valor arrecadado e prazo.
6. **Agenda**: próximos prêmios e eventos, com data.
7. **Últimas resenhas**: os 4 cartões mais recentes de O Paladino.
8. **Comunidade**: grupo do WhatsApp e Instagram.

A **Consulta Golden Geek**, que hoje ocupa a página inicial, vai para `meruvash.github.io/Arcvalion_gospel/consulta/`, com link no menu. Cada notícia ganha página própria em `/noticias/<data>-<assunto>/`, com prévia de WhatsApp, e há um arquivo em `/noticias/`.

## 3. Fontes

Testadas em 28/10/2026 com o robô do site, que respeita o `robots.txt`.

**Coleta automática (feed liberado para robôs)**

| Fonte | País | O que traz | Situação do feed |
|---|---|---|---|
| BoardGameWire | Reino Unido | Mercado: editoras, vendas, aquisições | ativo (19/10) |
| Board Game Quest | EUA | Notícias, lançamentos, financiamentos | ativo (27/10) |
| Meeple Mountain | EUA | Notícias e análises | ativo (27/10) |
| Spiel des Jahres | Alemanha | Prêmio mais importante do mundo | ativo (01/10) |
| Covil dos Jogos | Brasil | Notícias e lançamentos nacionais | ativo (27/10) |
| Dicebreaker | Reino Unido | Notícias | **feed parado desde maio de 2024**; acompanhar pelo site |

**Acompanhamento manual (o site proíbe robôs; você ou eu lemos e citamos com link)**

| Fonte | País | Por que importa |
|---|---|---|
| BGG News | EUA | A principal fonte de anúncios de jogos do mundo |
| Ludopedia | Brasil | Lançamentos e comunidade brasileira |
| Shut Up & Sit Down | Reino Unido | Crítica de referência |
| Tabletop Gaming | Reino Unido | Revista do setor |
| Wargamer | Reino Unido | Notícias diárias de tabuleiro |

**Fontes primárias (confirmam a notícia)**: sites e redes oficiais das editoras nacionais (Galápagos, Devir, Grok, MeepleBR, Conclave, Ludofy e outras) e internacionais, páginas oficiais dos prêmios (Spiel des Jahres, As d'Or, Golden Geek, Origins, Kennerspiel), páginas das campanhas (Catarse, Kickstarter, Gamefound, BackerKit) e sites dos eventos.

Fontes que não responderam do servidor na nuvem (Tábula Quadrada, Jogando Offline, blog da Galápagos, Mesa de Jogo) serão testadas de novo antes de entrar na lista.

### Fontes nacionais (pesquisa de 28/10/2026)

O Brasil não tem um portal jornalístico dedicado só a jogos de tabuleiro. As notícias nacionais nascem nas editoras e circulam na Ludopedia, em fóruns e em podcasts. Por isso a cobertura nacional se apoia em fontes primárias (as editoras) e na Ludopedia, com as outras como radar.

| Fonte | O que traz | Como acompanhar | Situação |
|---|---|---|---|
| **Ludopedia: API oficial** | Calendário de lançamentos no Brasil, editoras, jogos | API com chave (`ludopedia.com.br/api`); a página proíbe robôs, mas a API é o caminho oficial | **pedir chave de acesso** (você, com a conta da Ludopedia) |
| Ludopedia: LudoNews e "Rodada da semana nas editoras nacionais" | Resumo das novidades das editoras brasileiras | leitura manual | ativo (cobertura de Essen em 26–27/10) |
| **Devir Brasil** | Lançamentos, campeonatos de Catan e Carcassonne | feed da categoria de tabuleiro, liberado | ativo (15/09) |
| **Grok Games** | Lançamentos e pré-vendas | página liberada, sem feed: o robô compara a página dia a dia | liberado |
| **Diversão Offline** | Maior evento de tabuleiro do país | página liberada, para a Agenda | liberado |
| **Compara Jogos: "Estação de Notícias"** | Resumo quinzenal de notícias do hobby | fórum liberado para robôs | ativo |
| **Covil dos Jogos** | Notícias e lançamentos | feed liberado | ativo (27/10) |
| Galápagos, MeepleBR | Os maiores lançamentos nacionais | sites proíbem robôs: Instagram e newsletter, leitura manual | manual |
| Conclave, PaperGames, Ludens Spirit, Calamity, Bucaneiros | Lançamentos e financiamentos nacionais | redes e newsletter; blog da PaperGames sem posts no feed | manual |
| Catarse (categoria Jogos) | Financiamentos nacionais | API pública; não respondeu do servidor na nuvem, testar de novo | a testar |
| Fabuloso Podcast, BoardCast Brasil | Notícias comentadas da semana | radar de pauta, nunca fonte única | manual |

**Segunda rodada de testes (28/10/2026)**

| Fonte | O que traz | Situação |
|---|---|---|
| **Galápagos: Spoiler Board** (site dos eventos Spoiler Fest e Spoiler Night) | Os anúncios semestrais da maior editora do país | o site da Galápagos bloqueia robôs (403); endereço do Spoiler Board a confirmar. Entra na Agenda e como leitura obrigatória nas semanas de evento |
| **Laranja Cast** | Notícias geek com cobertura de tabuleiro (cobriu o Spoiler Night 2025) | feed liberado, ativo (27/10); filtrar por tabuleiro |
| **JWave** | Notícias geek, anunciou o Spoiler Night 2025 | feed liberado, ativo (28/10); filtrar por tabuleiro |
| **Vivente Andante** | Notícias de board games e lançamentos | feed respondeu, ativo (28/10); confirmar regras do site |
| Drops de Jogos (UAI) | Cobertura de Spoiler Fest e lançamentos nacionais | feed ativo, mas o site proíbe robôs: manual |
| Poltrona Nerd | Seção de board games | feed ativo, mas o site proíbe robôs: manual |
| X (Twitter) | Perfis das editoras e de jornalistas do setor | proíbe robôs; a API de leitura do X é paga. Fica fora da coleta automática |

**Lançamentos de cada editora**: `editoras_br.json` guarda, para cada editora nacional, a página de lançamentos, o feed (quando houver), o Instagram e se o site libera robôs. O robô visita as liberadas (Devir, Grok) e avisa o que mudou; as outras ficam na leitura manual. A API da Ludopedia cobre todas de uma vez no calendário de lançamentos.

**API da Ludopedia (LudoAPI, versão alfa)**: documentação em `ludopedia.com.br/api/documentacao.html`. Tem o endpoint `GET /lancamentos` (calendário de lançamentos no Brasil, por mês) e `GET /jogos`. Acesso: criar um aplicativo em `ludopedia.com.br/aplicativos`; o `access_token` gerado junto serve para o nosso uso, sem o fluxo OAuth. O token fica num segredo do ambiente (`LUDOPEDIA_TOKEN`), nunca no repositório. Dúvidas: api@ludopedia.com.br.

**Bluesky**: API pública e gratuita (`public.api.bsky.app`), sem chave. Responde do servidor na nuvem. A lista de perfis a seguir (editoras, prêmios, jornalistas, criadores nacionais) fica em `bluesky.json` e é revisada antes de entrar na coleta.

**Para fortalecer a cobertura nacional**
1. **Chave da API da Ludopedia** (pedido seu): resolve o bloco "Chegando ao Brasil" com dados oficiais, sem raspagem.
2. **Newsletter das editoras** num e-mail do projeto (Galápagos, MeepleBR, Grok, Conclave, Devir, PaperGames). Os anúncios chegam primeiro ali.
3. **Lista de imprensa**: pedir às editoras para entrar na lista de divulgação de O Paladino (mesmo pedido do kit de fotos).
4. **Comunidade**: no grupo do WhatsApp, um canal para leitores mandarem anúncios. O crivo exige a fonte primária antes de publicar.

## 4. Crivo editorial das notícias

Segue a lógica do crivo das fotos: primeiro eliminatórios, depois pontuação. Fica escrito em `PADRAO_EDITORIAL.md` e é conferido por `tools/noticias/checar_noticia.py`, que se recusa a publicar uma nota fora do padrão.

**Eliminatórios (a notícia não entra)**
- Sem fonte primária: só boato, vazamento ou "fontes dizem".
- Conteúdo pago ou release sem fato novo ("promoção da semana", "jogo X está incrível").
- Mais de 14 dias de atraso, a não ser em lançamento no Brasil.
- Já publicada por nós, mesmo vinda de outra fonte (deduplicação).
- Jogo, editora ou campanha sem relação com tabuleiro moderno (RPG, card game colecionável, videogame), salvo adaptação de jogo de tabuleiro.

**Pontuação de relevância (ordena as notas e decide as rodadas extras de pesquisa: a meta é ter pelo menos 5 com 5 pontos ou mais; manchete é a maior)**

| Critério | Pontos |
|---|---|
| Lançamento ou pré-venda confirmado no Brasil | 4 |
| Prêmio grande (indicação ou vencedor): Spiel des Jahres, Kennerspiel, As d'Or, Golden Geek | 4 |
| Jogo que já tem resenha nossa ou está na pauta | 3 |
| Jogo no top 100 do BGG ou de designer premiado | 3 |
| Notícia do mercado com efeito no Brasil (preço, distribuição, editora nova) | 3 |
| Financiamento acima de US$ 500 mil ou R$ 200 mil, ou recorde | 2 |
| Confirmada por duas fontes independentes | 2 |
| Evento grande (Essen, Gen Con, Diversão Offline) | 2 |

**Edição diária (29/10/2026, pedido do usuário)**

O corte de 5 pontos estava deixando dias sem nenhuma notícia. A meta passa a ser **no mínimo 5 notas por dia, sem limite máximo** ("quanto mais notícia, melhor"), e a qualidade vem primeiro:

1. **Rodada 1:** fontes automáticas (`coletar.py`: feeds, Bluesky, Ludopedia). Toda candidata que passa pelos eliminatórios é pontuada.
2. **Rodada 2**, se não houver 5 notas com 5 pontos ou mais: pesquisa em outras fontes, com preferência para as nacionais (editoras, Ludopedia, Compara Jogos, Catarse, eventos).
3. **Rodada 3**, se ainda faltar: pesquisa em fontes diferentes das duas primeiras (BGG News, sites internacionais, prêmios, Kickstarter e Gamefound).
4. Toda candidata que passa pelos eliminatórios e pelo padrão é publicada, inclusive abaixo de 5 pontos; notícia extra nunca sai do ar para manter um número. A maior pontuação é a manchete.
5. Os eliminatórios e o padrão de texto valem para todas. Menos de 5 só se nem 5 candidatas passarem pelos eliminatórios depois das três rodadas, e o resumo do dia explica.

**Regras de texto**
1. Título informativo, sem caça-clique: o que aconteceu, com quem.
2. Lide de 40 a 70 palavras: o fato, quando, onde e por que importa para quem joga no Brasil.
3. Corpo de 80 a 200 palavras, escrito por nós. Nada copiado; citação de outro site só curta, entre aspas e com fonte.
4. Fonte com link no fim, e a data da consulta.
5. Preço sempre com data. Data de lançamento sempre como "previsto" até sair.
6. Foto só da editora (imagem de divulgação, com crédito), de licença livre ou nossa. Sem foto boa, a nota não sai: procure em outras fontes ou troque de notícia (pedido do usuário em 29/10/2026).

## 5. Skills e ferramentas a desenvolver

| Skill / ferramenta | O que faz | Saída |
|---|---|---|
| `noticias` (skill) | Orquestra o dia: coleta, crivo, redação, revisão e publicação | Edição do dia publicada |
| `tools/noticias/coletar.py` | Lê os feeds liberados, respeitando o `robots.txt` e as pausas pedidas, e junta candidatas | `.cache/noticias/candidatas.json` |
| `tools/noticias/crivo.py` | Aplica eliminatórios e pontuação, deduplica e marca a manchete | Lista ordenada com o motivo de cada nota |
| `tools/noticias/checar_noticia.py` | Confere regras de texto, fontes e datas antes de publicar | Aprova ou recusa, com o motivo |
| `conteudo/noticias/<data>-<assunto>.json` | Uma nota por arquivo, como as resenhas. Para a busca automática de fotos, inclua `jogo` (nome oficial), `editora` e `fontes` (`[título, url, uso]`, com a página da editora quando houver) | Fonte da página da notícia |
| `tools/build_home.py` | Gera a página inicial com os 8 blocos | `index.html` |
| `tools/build_noticia.py` | Gera a página de cada notícia e o arquivo `/noticias/` | `noticias/...` |
| `agenda.json` | Datas de prêmios e eventos, revisadas por mês | Bloco Agenda |
| `editoras_br.json` | Páginas de lançamentos e redes das editoras nacionais | Bloco Chegando ao Brasil |

O robô de notícias reaproveita o cliente do robô de imagens (`tools/imagens/robo.py`): mesmo `robots.txt`, mesmas pausas, mesma identificação.

## 6. Fluxo de cada dia

1. **Coleta** (automática, de manhã): feeds liberados.
2. **Leitura manual** (10 minutos): BGG News e Ludopedia. Você me manda links que valham a pena, ou eu consulto na conversa.
3. **Crivo**: o robô ordena as candidatas e eu confiro as fontes primárias.
4. **Redação**: eu escrevo as notas que passaram, no padrão.
5. **Sua aprovação**: você vê a edição do dia antes de publicar (como foi com as fotos). Depois que o padrão estiver firme, a aprovação pode ficar só para a manchete.
6. **Publicação**: página inicial, páginas das notas e prévias do WhatsApp.

## 7. Etapas

| Etapa | Entrega | Para você ver |
|---|---|---|
| 1. Protótipo da página inicial | Página com os 8 blocos e notas de exemplo, num ramo separado | Capturas de celular e computador |
| 2. Crivo e padrão das notícias | Regras em `PADRAO_EDITORIAL.md` e `checar_noticia.py` | 5 notas reais do dia avaliadas |
| 3. Coleta automática | `coletar.py` e `crivo.py` com as fontes liberadas | Relatório de um dia de coleta |
| 4. Páginas de notícia e arquivo | `build_noticia.py` e `/noticias/` | Uma nota publicada de ponta a ponta |
| 5. Blocos de dados | Agenda, Chegando ao Brasil, Financiamentos, Em alta | Página inicial completa |
| 6. Rotina | Skill `noticias` e tarefa agendada diária | Primeira semana de edições |

## 8. Riscos e cuidados

- **Direito autoral**: notícia é fato e pode ser recontada, mas texto e foto têm dono. Por isso: texto próprio, citação curta e foto com crédito ou licença.
- **Fontes que bloqueiam robôs** (BGG, Ludopedia): só leitura manual e citação com link, nunca raspagem.
- **Feeds que param** (Dicebreaker parou em 2024): `coletar.py` avisa quando uma fonte passa 30 dias sem nada novo.
- **Volume**: melhor 3 notas boas por dia do que 15 fracas. O crivo corta; a página inicial mostra o que passou.

## 9. Decisões tomadas (28/10/2026)

1. **No mínimo 5 notas por dia, sem máximo**: tudo o que passa pelos eliminatórios sai; as três rodadas de pesquisa buscam pelo menos 5 com 5 pontos ou mais (alterado em 29/10/2026; antes, corte fixo de 5 pontos). Ver "Edição diária" na seção 4.
2. **Aprovação só da manchete**; as outras 4 saem depois do crivo e do `checar_noticia.py`.
3. **A Consulta Golden Geek vai para `/consulta/`**, com link no menu.
4. **Financiamento coletivo entra**, com o mesmo crivo (fonte primária: a página da campanha).
5. **Reforçar as fontes nacionais** (seção 3, "Fontes nacionais").
