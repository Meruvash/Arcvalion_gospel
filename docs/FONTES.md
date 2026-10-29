<!-- Levantamento de 29/10/2026 feito com apoio de IA: feeds e robots.txt testados com curl da nuvem; tamanhos da página pública da Similarweb. Revise antes de usar como referência. config/fontes.json recebeu as fontes de nível A e B da lista A (sem Ultimato, cujo robots.txt bloqueia robôs de IA). -->

# Mapa de fontes cristãs e conservadoras para pauta e atribuição

Levantamento feito em **29/10/2026**. Serve para escolher **fontes de pauta e de atribuição**, não para copiar conteúdo. Toda matéria continua exigindo apuração, fonte primária e revisão humana (ver `CLAUDE.md` e `docs/PADRAO_EDITORIAL.md`).

## Como foi feito (leia antes de usar os números)

- **Feeds testados de verdade** em 29/10/2026, entre 22h50 e 23h10 UTC, da nuvem (IP de datacenter, via proxy), com `curl -sS -L -m 20 -A "PortalCristao-pauta/1.0"`. Um feed só conta como **"funciona"** quando responde HTTP 200, o corpo é RSS, Atom ou RDF e traz itens. A coluna "último item" mostra a data de `pubDate`/`updated`/`dc:date` mais recente do feed, em UTC.
- **robots.txt** lido para cada domínio (o do destino final, se houve redirecionamento). Duas colunas:
  - "robots `*`": se o grupo `User-agent: *` proíbe o caminho do feed. "livre" quer dizer que não proíbe.
  - "bots de IA": se o robots.txt tem `Disallow: /` para GPTBot, ClaudeBot, anthropic-ai, CCBot, Google-Extended, PerplexityBot e afins. Isso **não impede** a leitura do feed pelo nosso coletor, que se identifica como `PortalCristao-pauta/1.0` e não é bot de treinamento. Mesmo assim, é um sinal claro da vontade do site, e o editor deve conhecê-lo.
- **Tamanho**: quase sempre vem da página pública da Similarweb (`https://www.similarweb.com/website/<domínio>/`), relatório rotulado "September 2026" e consultado em 29/10/2026. Atenção:
  - A página mostra o número de visitas sob o título "Total Visits Last 3 Months" e não deixa claro se é o total do trimestre ou do último mês. Use o número só para **comparar ordem de grandeza** entre sites.
  - O **ranking no país** é o indicador mais comparável.
  - São estimativas da Similarweb, não auditoria. Comscore não tem dado público recente para esses sites.
  - Números declarados pelo próprio veículo aparecem marcados como "autodeclarado".
  - Onde está "não levantado", não procurei. Onde está "não encontrado", procurei e não achei.
- **"bloqueado (403) da nuvem"** quer dizer que o site barrou o IP de datacenter, em geral com o desafio "Just a moment..." da Cloudflare. **Não quer dizer que o site morreu.** Teste de uma rede comum antes de descartar.
- **Confiabilidade**: as notas de "linha/confiabilidade" são recomendações editoriais para o nosso uso. Quando cito avaliação externa, dou o link:
  - **WP:RSP** é a lista de fontes recorrentes da Wikipédia em inglês ([Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources)), consultada em 29/10/2026.
  - Os status usados: "geralmente confiável", "sem consenso", "geralmente não confiável" e "depreciada". É uma régua externa, útil mas não definitiva.
- **Slug de editoria**: o pedido citava `cultura-crista`, mas o `config/editorias.json` usa **`musica-e-cultura`**. O JSON do fim usa o slug real.

---

## 1. Brasil: portais e instituições cristãs/evangélicas

| Nome | URL | País/língua | Tipo | Tamanho (fonte, data) | Linha/confiabilidade | Feed | Feed funciona? (último item) | robots `*` / bots de IA |
|---|---|---|---|---|---|---|---|---|
| Pleno News | https://pleno.news | BR/pt | portal (notícias gerais e gospel) | Similarweb set/2026: 833K visitas exibidas; rank BR #6.559 ([link](https://www.similarweb.com/website/pleno.news/)) | Ligado ao Grupo MK, fundado em 2017 ([Sul21](https://sul21.com.br/?p=19519)); linha conservadora; tem colunistas políticos. Nível B: confirmar fatos na fonte primária | https://pleno.news/feed | Sim, 30 itens (29/10 16:08) | livre / não bloqueia |
| Guiame | https://guiame.com.br | BR/pt | portal | Similarweb set/2026: 132,4K; rank BR #40.277 ([link](https://www.similarweb.com/website/guiame.com.br/)) | Evangélico, muito noticiário internacional de perseguição traduzido. Nível B/C: rastrear a origem | https://guiame.com.br/rss | Sim, 24 itens (28/10 20:10) | livre / não |
| Gospel Prime, agora "Good Prime" | https://www.gospelprime.com.br, que redireciona (301) para https://goodprime.co | BR/pt | portal e opinião | Similarweb set/2026: goodprime.co com 22,3K e rank BR #120.205; gospelprime.com.br com 5,4K ([1](https://www.similarweb.com/website/goodprime.co/), [2](https://www.similarweb.com/website/gospelprime.com.br/)). A queda deve vir da troca de domínio | **Mudou de domínio e de nome.** O site novo usa os arquivos `logo-gospelprime.png` e os mesmos perfis sociais "gospelprime". Não achei anúncio público da mudança. Opinativo. Nível C | https://goodprime.co/feed/ | Responde (1 item, 28/10 22:37), **mas o robots.txt proíbe `/feed/` para `*`**. Não usar no coletor | **proíbe /feed/** / não |
| Comunhão | https://comunhao.com.br | BR/pt | revista e portal | Similarweb set/2026: 52,2K; rank BR #76.142 ([link](https://www.similarweb.com/website/comunhao.com.br/)) | Revista evangélica capixaba, mais institucional. Nível B | https://comunhao.com.br/feed/ | Responde (10 itens, 29/10 21:11), **mas o robots.txt proíbe `/feed/` para `*`** | **proíbe /feed/** / não |
| Gospel+ (Gospel Mais) | https://gospelmais.com/noticias (antes noticias.gospelmais.com.br) | BR/pt | portal | Similarweb set/2026: gospelmais.com com 26,2K e rank BR #105.266 ([link](https://www.similarweb.com/website/gospelmais.com/)) | Agregador, muita nota curta e celebridade gospel. Nível C | https://gospelmais.com/noticias/feed | Sim, 20 itens (29/10 20:22) | livre / não |
| Folha Gospel | https://folhagospel.com | BR/pt | portal | Similarweb set/2026: 37,3K; rank BR #76.953 ([link](https://www.similarweb.com/website/folhagospel.com/)) | Agregador evangélico. Nível C | https://folhagospel.com/feed/ | Sim, 10 itens (29/10 09:47) | livre / não |
| Canção Nova Notícias | https://noticias.cancaonova.com | BR/pt | portal (católico) | Similarweb set/2026, domínio cancaonova.com inteiro: rank BR #351 ([link](https://www.similarweb.com/website/cancaonova.com/)). O número de visitas não aparece de forma clara | Comunidade católica, com cobertura da Igreja no Brasil. Nível B | https://noticias.cancaonova.com/feed/ | Sim, 12 itens (29/10 19:24) | livre / não |
| Vatican News (português) | https://www.vaticannews.va/pt.html | Vaticano/pt | primária (Santa Sé) | Similarweb set/2026, vaticannews.va inteiro: 14,7M; rank global #5.205 ([link](https://www.similarweb.com/website/vaticannews.va/)) | Órgão oficial do Dicastério para a Comunicação. Primária para atos do Papa e da Santa Sé. Nível A | https://www.vaticannews.va/pt.rss.xml | Sim, 50 itens (29/10 17:45) | livre / **bloqueia** GPTBot, ClaudeBot, CCBot, Google-Extended e outros |
| CNBB | https://www.cnbb.org.br | BR/pt | primária (católica) | Similarweb set/2026: 599,1K; rank BR #10.633 ([link](https://www.similarweb.com/website/cnbb.org.br/)) | Já está no `config/fontes.json`. Nível A para posições da CNBB | https://www.cnbb.org.br/feed/ | **Já no config. Funciona** (10 itens, 29/10 19:54) | livre / **bloqueia** bots de IA |
| ACI Digital (EWTN) | https://www.acidigital.com | BR/pt | agência (católica) | Similarweb set/2026: 170,9K; rank BR #34.162 ([link](https://www.similarweb.com/website/acidigital.com/)) | Do grupo ACI/EWTN. A EWTN anunciou em 15/01/2026 que as marcas ACI viram "EWTN News" com o tempo ([EWTN](https://www.ewtn.com/pressroom/article/521)). Nível B | `/rss` devolve página HTML | **Não** (nenhum feed encontrado) | livre / **bloqueia** bots de IA |
| Portas Abertas Brasil | https://portasabertas.org.br | BR/pt | ONG (perseguição) | Similarweb set/2026: 92,7K; rank BR #41.681 ([link](https://www.similarweb.com/website/portasabertas.org.br/)) | Braço brasileiro da Open Doors e da Lista Mundial da Perseguição. Parte interessada, mas com metodologia publicada. Nível B | `/feed/` e `/noticias/feed/` redirecionam para a home | **Não** (sem feed) | livre / não |
| Ultimato | https://www.ultimato.com.br | BR/pt | revista e editora | Similarweb set/2026: 108,7K; rank BR #46.880 ([link](https://www.similarweb.com/website/ultimato.com.br/)) | Evangélica, perfil reflexivo e teológico. Nível B | http://feeds.feedburner.com/ultimato | Sim, mas é parcial: 6 itens **sem data por item** (lastBuildDate 29/10/2026) | livre / **bloqueia** GPTBot, anthropic-ai, CCBot, Google-Extended, PerplexityBot |
| Aliança Cristã Evangélica Brasileira | https://aliancaevangelica.org.br | BR/pt | primária (entidade) | não levantado | Entidade representativa (ligada à WEA). Primária para as próprias notas. Nível A para posições próprias | https://aliancaevangelica.org.br/feed/ | Sim, 10 itens (26/10 17:20) | livre / não |
| Notícias Adventistas | https://noticias.adventistas.org/pt/ | BR/pt | primária (denominacional) | não levantado | Canal oficial da Igreja Adventista na América do Sul. Nível A para fatos da denominação | https://noticias.adventistas.org/pt/feed/ | Sim, 10 itens (29/10 19:46) | livre / não |
| CGADB (Assembleias de Deus) | https://cgadb.org.br | BR/pt | primária (convenção) | não levantado | Primária para atos da convenção | https://cgadb.org.br/feed/ | **Parado**: 1 item, de 17/05/2023 | livre / não |
| Convenção Batista Brasileira | https://convencaobatista.com.br | BR/pt | primária (convenção) | não levantado | Primária para atos da CBB | `/feed/` dá 404; `?format=feed` devolve HTML | **Não** (sem feed) | livre / não |
| ANAJURE | https://anajure.org.br | BR/pt | ONG jurídica (liberdade religiosa) | não levantado | Associação de juristas evangélicos. Parte interessada, mas útil para casos de liberdade religiosa. Nível B | `www.anajure.org.br` dá erro Cloudflare 525; `anajure.org.br/feed/` dá 404 | **Não** | livre / **bloqueia** bots de IA |
| CPAD News | https://www.cpadnews.com.br | BR/pt | portal (editora das ADs) | Similarweb set/2026: 14,9K; rank BR #117.787 ([link](https://www.similarweb.com/website/cpadnews.com.br/)) | Editora ligada às Assembleias de Deus. Nível B | /feed/ e /rss | **Bloqueado (403) da nuvem**, com desafio Cloudflare. O site não está morto | robots também 403 |
| Púlpito Cristão | https://pulpitocristao.com | BR/pt | blog e opinião | não levantado | Opinativo. Nível C | https://pulpitocristao.com/feed/ | Sim, 9 itens (27/10 03:19) | livre / não |
| Cristianismo Hoje | https://www.cristianismohoje.com.br | BR/pt | revista | não encontrado | — | — | **Inacessível**: o domínio não resolve da nuvem (proxy 502, DNS EAI_AGAIN). Pode estar fora do ar; confirmar de rede local | — |
| Gnotícias | https://gnoticias.com.br | BR/pt | portal | não encontrado | — | redireciona (301) para samuraipaper.com, que responde **522** | **Não**. Parece desativado ou vendido | — |
| Christianity Today em português | https://www.christianitytoday.com/pt/ | EUA/pt | revista | — | A seção `/pt/` dá 404. Use o feed principal da CT, que já está no config | — | **Não** | — |

## 2. Brasil: notícias e opinião conservadora ou de direita

| Nome | URL | País/língua | Tipo | Tamanho (fonte, data) | Linha/confiabilidade | Feed | Feed funciona? (último item) | robots `*` / bots de IA |
|---|---|---|---|---|---|---|---|---|
| Gazeta do Povo | https://www.gazetadopovo.com.br | BR/pt | jornal digital | Similarweb set/2026: 15,1M; rank BR #238 ([link](https://www.similarweb.com/website/gazetadopovo.com.br/)) | Jornal com redação profissional e linha editorial de centro-direita/conservadora declarada. Tem paywall parcial. Nível B+ (bom para pauta; confirmar dados oficiais) | https://www.gazetadopovo.com.br/feed/rss/ultimas-noticias.xml | Sim, 181 itens (29/10 22:45). Precisa de filtro | livre / **bloqueia** GPTBot, CCBot, PerplexityBot |
| O Antagonista | https://oantagonista.com.br | BR/pt | portal | Similarweb set/2026: 44,9M; rank BR #78 ([link](https://www.similarweb.com/website/oantagonista.com.br/)) | Notas rápidas, muito político. Nível B: confirmar na fonte | https://oantagonista.com.br/feed/ | Sim, 15 itens (29/10 22:46) | livre / não |
| Revista Oeste | https://revistaoeste.com | BR/pt | revista e portal | Similarweb set/2026: 11,1M; rank BR #391 ([link](https://www.similarweb.com/website/revistaoeste.com/)). Autodeclarado: 100 mil assinantes ([Oeste](https://revistaoeste.com/imprensa/revista-oeste-atinge-a-marca-de-100-mil-assinantes/); a data da página não foi confirmada porque o acesso deu 403) | Conservadora/liberal, com forte opinião. Paywall nas reportagens semanais. Nível B | https://revistaoeste.com/feed/ | Sim, 10 itens (29/10 22:49) | livre / **bloqueia** ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended |
| Jovem Pan News | https://jovempan.com.br | BR/pt | rádio, TV e portal | Similarweb set/2026: 7,9M; rank BR #503 ([link](https://www.similarweb.com/website/jovempan.com.br/)) | Grande grupo de mídia, com comentaristas de direita. Nível B | https://jovempan.com.br/feed/ | Sim, 10 itens (29/10 22:52) | livre / não |
| Jornal da Cidade Online | https://www.jornaldacidadeonline.com.br | BR/pt | portal e opinião | Similarweb set/2026: 2,7M; rank BR #1.638 ([link](https://www.similarweb.com/website/jornaldacidadeonline.com.br/)) | Histórico conturbado: [Aos Fatos](https://aosfatos.org/noticias/perfis-apocrifos-somem-do-jornal-da-cidade-online-apos-reportagem-do-aos-fatos/) apontou perfis apócrifos de autores. O site foi citado nos relatórios da CPMI das Fake News e da CPI da Covid. Em 2023 ganhou ação contra a Aos Fatos ([Poder360](https://www.poder360.com.br/justica/justica-condena-aos-fatos-a-pagar-r-10-000-a-site-bolsonarista/)). **Nível C: nunca atribuir fato só a ele** | /rss, /feed, /feed.xml | **Não** (404) | livre / não |
| Brasil Paralelo | https://www.brasilparalelo.com.br | BR/pt | produtora e portal | Similarweb set/2026: 2,2M; rank BR #2.087 ([link](https://www.similarweb.com/website/brasilparalelo.com.br/)). Autodeclarado: "mais de 650 mil membros assinantes" ([BP, 15/07/2026](https://www.brasilparalelo.com.br/noticias/brasil-paralelo-prepara-grande-evento-para-comemorar-seus-10-anos)) | Produtora de documentários com seção de notícias. Fortemente opinativa. Nível C para fatos e bom termômetro de pauta | https://www.brasilparalelo.com.br/noticias/feed.xml | Sim, 50 itens (29/10 21:23) | livre / não |
| Diário do Poder | https://diariodopoder.com.br | BR/pt | portal | Similarweb set/2026: 1,3M; rank BR #4.544 ([link](https://www.similarweb.com/website/diariodopoder.com.br/)) | Bastidores de Brasília (Cláudio Humberto). Nível B/C | https://diariodopoder.com.br/feed | Sim, 10 itens (29/10 21:24) | livre / não |
| Conexão Política | https://www.conexaopolitica.com.br | BR/pt | portal | Similarweb set/2026: 134,6K; rank BR #34.207 ([link](https://www.similarweb.com/website/conexaopolitica.com.br/)) | Agregador de direita. Nível C | https://www.conexaopolitica.com.br/feed/ | Responde (20 itens, 29/10 15:52), **mas o robots.txt proíbe `/feed/` para `*`** | **proíbe /feed/** / bloqueia anthropic-ai, CCBot |
| Revista Crusoé | https://crusoe.com.br | BR/pt | revista semanal | Similarweb set/2026: 118,4K; rank BR #37.510 ([link](https://www.similarweb.com/website/crusoe.com.br/)) | Investigativa, do mesmo grupo de O Antagonista. Paywall. Nível B | https://crusoe.com.br/feed/ | Sim, 15 itens (23/10 06:30). É semanal | livre / não |
| Revista Timeline | https://www.revistatimeline.com | BR/pt | revista e opinião | Similarweb set/2026: 45,3K; rank BR #75.851 ([link](https://www.similarweb.com/website/revistatimeline.com/)) | Opinião conservadora. Nível C | https://www.revistatimeline.com/feed | Sim, 20 itens (21/10 17:27), com baixa frequência | livre / não |
| Revista Esmeril | https://revistaesmeril.com.br | BR/pt | opinião | não levantado | Opinião e cultura conservadora. Nível C | https://revistaesmeril.com.br/feed/ | Sim, 6 itens (29/10 17:55) | livre / não |
| Instituto Mises Brasil | https://mises.org.br | BR/pt | think tank e opinião | não levantado | Liberal (escola austríaca). Opinião; nível C para fatos | https://mises.org.br/feed/ | Sim, 16 itens (29/10 19:04) | livre / não |
| Senso Incomum | https://www.sensoincomum.org | BR/pt | opinião | não levantado | — | https://www.sensoincomum.org/rss/ | **Quase parado**: último item de 21/07/2026 | livre / não |
| Terça Livre | https://tercalivre.com.br | BR/pt | — | — | Canal do YouTube encerrado em 2021. Sites retirados do ar em 2022 ([Poder360](https://www.poder360.com.br/midia/dois-sites-de-allan-dos-santos-sao-retirados-do-ar/), [Gazeta do Povo](https://www.gazetadopovo.com.br/vida-e-cidadania/alexandre-de-moraes-determina-que-anatel-retire-do-ar-site-de-allan-dos-santos/)). **Não usar** | — | **Inacessível**: o domínio não resolve da nuvem (DNS) | — |
| Renova Mídia | https://renovamidia.com.br | BR/pt | — | não encontrado | Não achei notícia sobre o fim do site | — | **Inacessível**: o domínio não resolve (DNS ENOTFOUND). Provavelmente fora do ar | — |
| Crítica Nacional | https://www.criticanacional.com.br | BR/pt | — | não encontrado | — | — | **Inacessível**: o domínio não resolve da nuvem (proxy 502) | — |
| *Referências de centro, para contraponto e checagem:* Poder360 | https://www.poder360.com.br | BR/pt | jornal digital | não levantado | Nível A/B | https://www.poder360.com.br/feed/ | Sim, 10 itens (29/10 22:49) | livre / não |
| *Referência:* Veja | https://veja.abril.com.br | BR/pt | revista | não levantado | Nível A/B | https://veja.abril.com.br/feed/ | Sim, 20 itens (29/10 22:37) | livre / não |
| *Referência:* Folha, seção Poder | https://www1.folha.uol.com.br/poder/ | BR/pt | jornal | não levantado | Nível A/B. Paywall | https://feeds.folha.uol.com.br/poder/rss091.xml | Sim, 100 itens (29/10 19:34) | livre / **bloqueia** ClaudeBot, anthropic-ai, CCBot, PerplexityBot |
| *Referência:* Estadão, seção Política | https://www.estadao.com.br/politica/ | BR/pt | jornal | não levantado | Nível A/B. Paywall | https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/politica/ | Sim, 20 itens (29/10 22:17) | livre / **bloqueia** ClaudeBot, GPTBot e outros |

## 3. Internacional: notícias cristãs

| Nome | URL | País/língua | Tipo | Tamanho (fonte, data) | Linha/confiabilidade | Feed | Feed funciona? (último item) | robots `*` / bots de IA |
|---|---|---|---|---|---|---|---|---|
| Christianity Today | https://www.christianitytoday.com | EUA/en | revista | Similarweb set/2026: 1,3M; rank EUA #15.054 ([link](https://www.similarweb.com/website/christianitytoday.com/)) | Principal revista evangélica, com padrões jornalísticos. Nível A/B | https://www.christianitytoday.com/feed/ | **Já no config. Funciona** (10 itens, 29/10 13:37) | livre / **bloqueia** ClaudeBot, GPTBot e outros |
| The Gospel Coalition | https://www.thegospelcoalition.org | EUA/en | ministério e opinião | Similarweb set/2026: 5M; rank EUA #4.429 ([link](https://www.similarweb.com/website/thegospelcoalition.org/)) | Reformado. Mais teologia do que notícia. Bom para "Fé e Bíblia" | https://www.thegospelcoalition.org/feed/ | Sim, 17 itens (29/10 04:04) | livre / não |
| Desiring God | https://www.desiringgod.org | EUA/en | ministério | Similarweb set/2026: 4,4M; rank EUA #5.292 ([link](https://www.similarweb.com/website/desiringgod.org/)) | Devocional e teológico (John Piper) | https://www.desiringgod.org/blog.rss | **Bloqueado (403) da nuvem**, com Cloudflare. O robots também tem `Disallow: *.rss` | robots proíbe *.rss / não |
| Crosswalk / Christian Headlines | https://www.crosswalk.com | EUA/en | portal (Salem Media) | Similarweb set/2026, crosswalk.com: 2,2M; rank EUA #7.531 ([link](https://www.similarweb.com/website/crosswalk.com/)) | Agregador. Nível B/C | Notícias: https://www.crosswalk.com/headlines/rss.xml (destino de christianheadlines.com/rss/). Geral: https://www.crosswalk.com/rss.xml | Sim, 10 itens (29/10 17:30); geral com 8 itens (29/10 07:00) | livre / não |
| The Christian Post | https://www.christianpost.com | EUA/en | portal | Similarweb set/2026: 1,7M; rank EUA #9.236 ([link](https://www.similarweb.com/website/christianpost.com/)) | Evangélico conservador, com volume alto. Nível B | https://www.christianpost.com/rss | Sim, 30 itens (29/10 18:53) | livre / não |
| CBN News | https://cbn.com | EUA/en | TV e portal | Similarweb set/2026: 1,6M; rank EUA #11.849 ([link](https://www.similarweb.com/website/cbn.com/)) | WP:RSP: "sem consenso" (Christian Broadcasting Network). Nível B | Os feeds antigos (`www2.cbn.com/rss-*`) devolvem HTML. `cbn.com/rss.xml` é um feed de 2005 | **Não** (sem feed atual) | livre / não |
| National Catholic Register | https://www.ncregister.com | EUA/en | jornal (EWTN) | Similarweb set/2026: 1,3M; rank EUA #13.378 ([link](https://www.similarweb.com/website/ncregister.com/)) | Católico, do grupo EWTN. Nível B | https://www.ncregister.com/feeds/general-news.xml | Sim, 20 itens (29/10 17:02) | livre / não |
| EWTN News (ex-Catholic News Agency) | https://www.ewtnnews.com | EUA/en | agência | Similarweb set/2026: rank EUA #19.074 ([link](https://www.similarweb.com/website/ewtnnews.com/)) | **A CNA virou EWTN News** em janeiro de 2026, e catholicnewsagency.com redireciona ([EWTN, 15/01/2026](https://www.ewtn.com/pressroom/article/521)). Nível B | https://www.ewtnnews.com/rss (o feed antigo da CNA redireciona para cá) | Sim, 32 itens (29/10 20:11) | livre (o robots declara `Content-Signal: ai-train=no`) / **bloqueia** bots de IA |
| The Pillar | https://www.pillarcatholic.com | EUA/en | jornalismo católico independente | Similarweb set/2026: 1,3M; rank EUA #17.245 ([link](https://www.similarweb.com/website/pillarcatholic.com/)) | Reportagem investigativa sobre a Igreja. Nível A/B | https://www.pillarcatholic.com/feed | Sim, 20 itens (29/10 19:34) | livre / não |
| WORLD | https://wng.org | EUA/en | revista | Similarweb set/2026: 679K; rank EUA #20.383 ([link](https://www.similarweb.com/website/wng.org/)) | Jornalismo evangélico com padrão profissional. Nível B | https://wng.org/feeds/rss/magazine.rss (destino de /rss) | Sim, 5 itens (29/10 18:53) | livre / não |
| Religion News Service | https://religionnews.com | EUA/en | agência | Similarweb set/2026: 468,8K; rank EUA #34.239 ([link](https://www.similarweb.com/website/religionnews.com/)) | Agência laica especializada em religião. Nível A | https://religionnews.com/feed/ | **Bloqueado (403) da nuvem**, com Cloudflare. Testar de outra rede | robots 403 |
| Premier Christian News | https://premierchristian.news | Reino Unido/en | portal e rádio | Similarweb set/2026: 419,6K; rank Reino Unido #11.328 ([link](https://www.similarweb.com/website/premierchristian.news/)) | Principal mídia cristã britânica. Nível B | /feed, /rss, /en/rss | **Bloqueado (403) da nuvem** | livre / não |
| Relevant | https://relevantmagazine.com | EUA/en | revista (cultura) | Similarweb set/2026: 207,2K ([link](https://www.similarweb.com/website/relevantmagazine.com/)) | Cultura cristã jovem. Bom para "Música e Cultura" | https://relevantmagazine.com/feed/ | Sim, 29 itens (29/10 20:16) | livre / não |
| Baptist Press | https://www.baptistpress.com | EUA/en | agência (Convenção Batista do Sul) | Similarweb set/2026: 110K; rank EUA #96.335 ([link](https://www.similarweb.com/website/baptistpress.com/)) | Agência oficial da SBC. Primária para a denominação | https://www.baptistpress.com/feed/ | **Vazio**: HTTP 200, mas com 0 itens | livre / **bloqueia** bots de IA. A home dá 403 da nuvem |
| Christian Today | https://www.christiantoday.com | Reino Unido/en | portal | Similarweb set/2026: 139,2K, sem rank ([link](https://www.similarweb.com/website/christiantoday.com/)) | Nível B/C | https://www.christiantoday.com/rss.xml | Sim, 200 itens (29/10 10:47) | livre / não |
| Christian Daily International | https://www.christiandaily.com | Internacional/en | portal | não levantado | Ligado à rede da Aliança Evangélica Mundial (WEA). Nível B | https://www.christiandaily.com/rss.xml | Sim, 250 itens (29/10 16:15) | livre / não |
| Evangelical Focus | https://evangelicalfocus.com | Europa/en, es | portal | Similarweb set/2026: 45,6K ([link](https://www.similarweb.com/website/evangelicalfocus.com/)) | Aliança Evangélica Espanhola. Bom para a Europa. Nível B | /rss, /rss/news (erro 500), /feed | **Não** | livre / não |
| International Christian Concern | https://www.persecution.org | EUA/en | ONG (perseguição) | não levantado | ONG de advocacy. Confirmar casos em fonte local. Nível B | https://persecution.org/feed/ | Sim, 10 itens (29/10 22:30) | livre / não |
| Voice of the Martyrs (EUA) | https://www.persecution.com | EUA/en | ONG | não levantado | Advocacy. Nível B/C | /feed, /rss | **Não** (404) | livre / não |
| Open Doors (Internacional e EUA) | https://www.opendoors.org, https://www.opendoorsus.org | Internacional/en | ONG (Lista Mundial da Perseguição) | não levantado | Ver grupo 5 | — | **Não**. Os feeds dão 404; opendoorsus.org responde 429 | **opendoors.org: `User-Agent: *` com `Disallow: /`**, só libera buscadores e alguns bots de IA nomeados. Só leitura pontual |
| Lausanne Movement | https://lausanne.org | Internacional/en | movimento missionário | não levantado | Institucional | `/feed` redireciona para a home; só existe feed de "web stories" | **Não** | livre / não |
| World Evangelical Alliance | https://worldea.org | Internacional/en | primária (entidade) | não levantado | — | https://worldea.org/feed/ | **Não**: HTTP 500 com a mensagem "GridPane Security has disabled the RSS" | livre / bloqueia Amazonbot |
| Vatican News (inglês) | https://www.vaticannews.va/en.html | Vaticano/en | primária | ver o grupo 1 | Nível A | https://www.vaticannews.va/en.rss.xml | Sim, 50 itens (29/10 17:05) | livre / **bloqueia** bots de IA |
| Mission Network News | https://www.mnnonline.org | EUA/en | portal (missões) | não levantado | — | https://www.mnnonline.org/feed/ | **Parado**: último item de 05/09/2023 | livre / bloqueia bots de IA |
| Christian Institute | https://www.christian.org.uk | Reino Unido/en | ONG e advocacy | não levantado | Advocacy | Página `/rss-feeds/` sem feed válido | **Não** | livre / não |

## 4. Internacional: notícias conservadoras

| Nome | URL | País/língua | Tipo | Tamanho (fonte, data) | Linha/confiabilidade | Feed | Feed funciona? (último item) | robots `*` / bots de IA |
|---|---|---|---|---|---|---|---|---|
| Fox News | https://www.foxnews.com | EUA/en | TV e portal | Similarweb set/2026: 204,3M; rank EUA #57 ([link](https://www.similarweb.com/website/foxnews.com/)) | WP:RSP: "sem consenso" para notícias em geral; "geralmente não confiável" para política e ciência e para os talk shows. Nível B/C | https://moxie.foxnews.com/google-publisher/latest.xml | Sim, 24 itens (29/10 18:37) | livre / não |
| New York Post | https://nypost.com | EUA/en | tabloide | Similarweb set/2026: 93,4M; rank EUA #152 ([link](https://www.similarweb.com/website/nypost.com/)) | WP:RSP: "geralmente não confiável" (o entretenimento é "sem consenso"). Nível C | https://nypost.com/feed/ | Sim, 22 itens (29/10 18:52) | livre / **bloqueia** ClaudeBot, anthropic-ai e outros |
| The Telegraph | https://www.telegraph.co.uk | Reino Unido/en | jornal | Similarweb set/2026: 58,9M; rank Reino Unido #46 ([link](https://www.similarweb.com/website/telegraph.co.uk/)) | WP:RSP: "geralmente confiável" (sem consenso em temas trans). Paywall. Nível A/B | /rss.xml, /news/rss.xml | **Bloqueado (402) da nuvem**, com a página "unusual activity" | livre / não |
| Breitbart | https://www.breitbart.com | EUA/en | portal | Similarweb set/2026: 21,8M; rank EUA #760 ([link](https://www.similarweb.com/website/breitbart.com/)) | WP:RSP: **depreciada e na lista negra**. Nível C: só como termômetro | https://feeds.feedburner.com/breitbart | Sim, 48 itens (29/10 20:21) | livre / não |
| Newsmax | https://www.newsmax.com | EUA/en | TV e portal | Similarweb set/2026: 17,2M; rank EUA #912 ([link](https://www.similarweb.com/website/newsmax.com/)) | WP:RSP: **depreciada**. Nível C | /rss/Newsfront/16/ | **Bloqueado da nuvem** (erro HTTP/2 INTERNAL_ERROR na conexão) | robots inacessível |
| GB News | https://www.gbnews.com | Reino Unido/en | TV e portal | Similarweb set/2026: 11,5M; rank Reino Unido #230 ([link](https://www.similarweb.com/website/gbnews.com/)) | WP:RSP: "geralmente não confiável" (2025). Nível C | https://www.gbnews.com/feeds/news.rss | Sim, 28 itens (29/10 19:39) | livre / não |
| The Daily Wire | https://www.dailywire.com | EUA/en | portal e opinião | Similarweb set/2026: 7,7M; rank EUA #1.889 ([link](https://www.similarweb.com/website/dailywire.com/)) | WP:RSP: "geralmente não confiável". Nível C | https://www.dailywire.com/feeds/rss.xml | Sim, 26 itens (29/10 17:27) | robots 404, ou seja, sem restrição |
| The Free Press | https://www.thefp.com | EUA/en | jornalismo e opinião | Similarweb set/2026: 3,7M; rank EUA #4.919 ([link](https://www.similarweb.com/website/thefp.com/)) | WP:RSP: "sem consenso" (2024). Paywall parcial. Nível B | https://www.thefp.com/feed | Sim, 20 itens (29/10 21:47) | livre / **bloqueia** bots de IA |
| TheBlaze | https://www.theblaze.com | EUA/en | portal | Similarweb set/2026: 3,4M; rank EUA #4.315 ([link](https://www.similarweb.com/website/theblaze.com/)) | WP:RSP: "geralmente não confiável" (Blaze Media). Nível C | https://www.theblaze.com/feeds/feed.rss | Sim, 28 itens (29/10 22:36) | livre / não |
| National Review | https://www.nationalreview.com | EUA/en | revista e opinião | Similarweb set/2026: 3,1M; rank EUA #5.073 ([link](https://www.similarweb.com/website/nationalreview.com/)) | WP:RSP: "sem consenso"; tratar como opinião. Nível B para análise | https://www.nationalreview.com/feed/ | Sim, 20 itens (29/10 20:21) | livre / não |
| The Spectator | https://spectator.com (antigo spectator.co.uk) | Reino Unido/en | revista | Similarweb set/2026: 2,8M ([link](https://www.similarweb.com/website/spectator.com/)) | WP:RSP: "sem consenso"; opinião | /feed, /rss | **Não** (404 depois da mudança de domínio) | livre / não |
| Washington Examiner | https://www.washingtonexaminer.com | EUA/en | revista e portal | Similarweb set/2026: 2,4M; rank EUA #7.311 ([link](https://www.similarweb.com/website/washingtonexaminer.com/)) | WP:RSP: "sem consenso". Nível B/C | https://www.washingtonexaminer.com/feed/ | Sim, 10 itens (29/10 22:24) | livre / bloqueia CCBot, Bytespider |
| The Daily Caller | https://dailycaller.com | EUA/en | portal | Similarweb set/2026: rank EUA #7.134 ([link](https://www.similarweb.com/website/dailycaller.com/)) | WP:RSP: **depreciada**. Nível C | https://dailycaller.com/feed/ | Sim, 25 itens (29/10 21:32) | livre / **bloqueia** ClaudeBot, GPTBot e outros |
| The Washington Times | https://www.washingtontimes.com | EUA/en | jornal | Similarweb set/2026: 1,9M; rank EUA #9.360 ([link](https://www.similarweb.com/website/washingtontimes.com/)) | WP:RSP: "sem consenso". Tem seção de fé (`/rss/headlines/culture/faith/`) | /rss/headlines/news/ e /culture/faith/ | **Bloqueado (403) da nuvem**, com Cloudflare | robots 403 |
| The Federalist | https://thefederalist.com | EUA/en | opinião | Similarweb set/2026: rank EUA #10.692 ([link](https://www.similarweb.com/website/thefederalist.com/)) | WP:RSP: "geralmente não confiável". Nível C | https://thefederalist.com/feed/ | Sim, 20 itens (29/10 20:10) | livre / não |
| The Daily Signal | https://www.dailysignal.com | EUA/en | portal | Similarweb set/2026: 1,1M; rank EUA #12.554 ([link](https://www.similarweb.com/website/dailysignal.com/)) | WP:RSP: a Heritage Foundation foi depreciada em 2025. O Daily Signal foi desmembrado da Heritage em junho de 2024, e a decisão de 2025 não tratou dele. Nível C | https://www.dailysignal.com/feed/ | Sim, 20 itens (29/10 22:30) | livre / não |
| The European Conservative | https://europeanconservative.com | Europa/en | revista | Similarweb set/2026: 228,1K ([link](https://www.similarweb.com/website/europeanconservative.com/)) | Opinião conservadora europeia | /feed/ | **Não**: HTTP 503 (site e robots) na hora do teste. Retestar | — |
| Brussels Signal | https://brusselssignal.eu | Europa/en | portal | não levantado | Conservador, cobre a UE. Nível B/C | https://brusselssignal.eu/feed/ | Sim, 12 itens (29/10 15:18) | livre / não |
| The American Conservative | https://www.theamericanconservative.com | EUA/en | revista | não levantado | WP:RSP: "sem consenso"; opinião | https://www.theamericanconservative.com/feed/ | Sim, 10 itens (29/10 12:41) | livre / não |
| First Things | https://firstthings.com | EUA/en | revista (religião e vida pública) | não levantado | Opinião intelectual cristã. Ótimo para "Fé e Bíblia" e para ensaios | https://firstthings.com/feed/ | Sim, 15 itens (29/10 14:47) | livre / não |
| The Dispatch | https://thedispatch.com | EUA/en | jornalismo e opinião (centro-direita) | não levantado | Faz checagem própria. Nível B | https://thedispatch.com/feed/ | Sim, 10 itens (29/10 22:33) | livre / bloqueia só meta-externalagent |
| UnHerd | https://unherd.com | Reino Unido/en | opinião | não levantado | WP:RSP: não consultado | https://unherd.com/feed/ | Sim, 9 itens (29/10 11:41) | livre / **bloqueia** bots de IA |
| Townhall | https://townhall.com | EUA/en | opinião (Salem) | não levantado | WP:RSP: "sem consenso"; opinião | https://townhall.com/feed/ | Sim, 50 itens (29/10 18:58) | livre / não |
| The American Spectator | https://spectator.org | EUA/en | opinião | não levantado | Opinião | https://spectator.org/feed/ | Sim, 10 itens (29/10 20:07) | livre / não |
| RealClearPolitics | https://www.realclearpolitics.com | EUA/en | agregador e pesquisas | não levantado | WP:RSP: "sem consenso". Útil para médias de pesquisas | https://www.realclearpolitics.com/index.xml | Sim, 32 itens (29/10 14:02) | livre / não |
| WSJ Opinion | https://www.wsj.com/opinion | EUA/en | jornal | não levantado | Paywall | https://feeds.a.dj.com/rss/RSSOpinion.xml | **Parado**: último item de 27/01/2025. O robots de wsj.com tem `User-agent: *` com `Disallow: /` | proíbe tudo para `*` |

## 5. Fontes primárias e de dados

| Nome | URL | País/língua | Tipo | Tamanho / indicador | Notas | Feed | Feed funciona? (último item) | robots `*` / bots de IA |
|---|---|---|---|---|---|---|---|---|
| Pew Research Center (religião) | https://www.pewresearch.org/religion/ | EUA/en | primária (pesquisa) | — | Referência mundial em dados religiosos. Nível A | https://www.pewresearch.org/feed/ (`/religion/feed/` redireciona para esse) | **Já no config. Funciona** (100 itens, 29/10 18:57). O filtro do config está certo | livre / não |
| Lifeway Research | https://research.lifeway.com | EUA/en | primária (pesquisa, ligada à SBC) | — | Nível A para os próprios levantamentos | Config: https://news.lifeway.com/feed/. Alternativa só de pesquisa: https://research.lifeway.com/feed/ | **Config funciona** (10 itens, 27/10). research.lifeway.com também (10 itens, 29/10 06:41) | livre / não |
| Barna Group | https://www.barna.com | EUA/en | primária (pesquisa) | — | Nível A, mas algumas pesquisas ficam atrás de paywall | https://www.barna.com/feed/ | **Parado**: último item de 04/05/2022 | livre / não |
| IBGE: Censo 2022, Religiões | https://agenciadenoticias.ibge.gov.br | BR/pt | primária oficial | Censo 2022: 26,9% de evangélicos e 56,7% de católicos (divulgado em 06/06/2025; [Agência Gov](https://agenciagov.ebc.com.br/noticias/202506/censo-2022-catolicos-seguem-em-queda-evangelicos-e-sem-religiao-crescem-no-pais)) | Nível A | https://agenciadenoticias.ibge.gov.br/agencia-noticias.rss | **Bloqueado (403) da nuvem**, com Cloudflare. Testar de outra rede | livre / não |
| Datafolha | https://datafolha.folha.uol.com.br | BR/pt | primária (pesquisa) | — | Pesquisas sobre religião e voto evangélico. Nível A, com ficha técnica | /rss e `feeds.folha…/datafolha/` | **Não** (404) | livre / **bloqueia** bots de IA |
| Frente Parlamentar Evangélica do Congresso Nacional | https://dadosabertos.camara.leg.br/api/v2/frentes/54477 | BR/pt | primária oficial (Câmara) | **232 membros** pela API de Dados Abertos da Câmara (consulta de 29/10/2026, `/frentes/54477/membros`). Coordenador registrado: Gilberto Nascimento (PODE-SP). Documento: https://www.camara.leg.br/internet/deputado/Frente_Parlamentar/54477-integra.pdf | Outras frentes da 57ª legislatura: Cristã e em Defesa da Religião (54402), Católica Apostólica Romana (54326), Defesa da Vida e da Família (54538), contra o Aborto (54333), Estado Laico e Liberdade Religiosa (55671) | API JSON, sem feed | API funciona | — |
| STF: Notícias | https://noticias.stf.jus.br | BR/pt | primária oficial | — | Decisões sobre liberdade religiosa, aborto, educação. Nível A | https://noticias.stf.jus.br/feed/ | Sim, 10 itens (29/10 00:18) | livre / não |
| Agência Brasil: Direitos Humanos | https://agenciabrasil.ebc.com.br | BR/pt | agência pública | — | Complementa o feed geral que já está no config | https://agenciabrasil.ebc.com.br/rss/direitos-humanos/feed.xml | Sim, 10 itens (29/10 15:47) | livre / não |
| USCIRF | https://www.uscirf.gov | EUA/en | primária oficial (comissão federal dos EUA) | — | Relatório anual sobre liberdade religiosa no mundo. Nível A | https://www.uscirf.gov/rss.xml | Sim, 10 itens (28/10 18:38) | livre / não |
| Departamento de Estado dos EUA: relatório de liberdade religiosa | https://www.state.gov | EUA/en | primária oficial | — | Nível A | /rss-feeds/ | **Bloqueado (403) da nuvem** | robots 403 |
| ACN: Ajuda à Igreja que Sofre (Brasil) | https://www.acn.org.br | BR/pt | ONG pontifícia | — | Relatório "Liberdade Religiosa no Mundo". Nível B+ | https://www.acn.org.br/feed/ | Sim, 10 itens (28/10 20:12) | livre / não |
| ACN International | https://acninternational.org | Internacional/en | ONG | — | Nível B+ | `/feed/` redireciona para a home | **Não** | livre / não |
| Open Doors: World Watch List | https://www.opendoors.org/en-US/persecution/countries/ | Internacional/en | ONG (índice anual) | — | Nível B (metodologia publicada; parte interessada). No Brasil, ver Portas Abertas | — | **Sem feed**; o robots proíbe `*` | **proíbe tudo para `*`**. Só leitura manual |
| ADF International | https://adfinternational.org | Internacional/en | ONG jurídica | — | Parte em processos; confirmar nos autos. Nível B | https://adfinternational.org/feed/ | **Vazio** (0 itens) | livre / não |
| Alliance Defending Freedom (EUA) | https://adflegal.org | EUA/en | ONG jurídica | — | Idem | https://adflegal.org/feed/ | **Vazio** (0 itens) | livre / não |
| Becket | https://www.becketlaw.org | EUA/en | ONG jurídica | — | Idem | https://www.becketlaw.org/feed/, que redireciona para becketfund.org/feed/ | **Vazio** (0 itens) | livre / não |
| ACLJ | https://aclj.org | EUA/en | ONG jurídica | — | Advocacy (Jay Sekulow). Nível B/C | /rss, /feed | **Não** (404) | livre / não |
| ERLC (Comissão de Ética e Liberdade Religiosa da SBC) | https://erlc.com | EUA/en | entidade denominacional | — | Primária para posições da SBC | https://erlc.com/feed/ | Sim, 10 itens (29/10 14:24) | livre / não |
| Christian Concern / Christian Legal Centre | https://christianconcern.com | Reino Unido/en | ONG jurídica | — | Parte em processos no Reino Unido. Nível B/C | https://christianconcern.com/feed/ | Sim, 17 itens (29/10 14:45) | livre / não |
| Forum 18 | https://www.forum18.org | Noruega/en | agência (liberdade religiosa: ex-URSS, China) | — | Muito sólida em sua área. Nível A/B | https://www.forum18.org/syndication/forum18.xml | Sim, mas é parcial: 8 itens **sem data por item** (lastBuildDate 29/10/2026) | livre / não |
| ONU News (português) | https://news.un.org/pt/ | ONU/pt | primária institucional | — | Nível A para atos da ONU | https://news.un.org/feed/subscribe/pt/news/all/rss.xml | Responde (30 itens, 29/10 08:00), mas o robots tem `Disallow: */news/` para `*`, regra fora do padrão que casa com o caminho do feed. Tratar como proibido até esclarecer | regra ambígua / não |

### Situação dos feeds que já estão em `config/fontes.json` (teste de 29/10/2026)

| Feed | Situação |
|---|---|
| Agência Senado | Funciona (15 itens, 29/10 21:02) |
| Agência Câmara | Funciona (20 itens, 29/10 20:59) |
| **Planalto** | Responde (RDF, 33 itens), mas **o item mais recente é de 27/09/2026**, mais de um mês parado. Pode ser o período eleitoral; verificar antes de confiar no feed |
| Banco Central | Funciona (Atom, 10 itens, 29/10 19:58) |
| Agência Brasil | Funciona (10 itens, 29/10 18:41) |
| CNBB | Funciona (10 itens, 29/10 19:54). O robots bloqueia bots de IA, mas `*` está livre |
| Pew Research | Funciona (100 itens, 29/10 18:57) |
| Lifeway (news.lifeway.com) | Funciona (10 itens, 27/10 14:55) |
| Christianity Today | Funciona (10 itens, 29/10 13:37). O robots bloqueia bots de IA, mas `*` está livre |

---

## Como usar

### Níveis de confiabilidade (recomendação editorial)

- **Nível A: pode sustentar o fato, com link e data.**
  - Fontes primárias oficiais: Câmara, Senado, STF, Planalto, IBGE, USCIRF, ONU, Vatican News/Santa Sé, CNBB, notas das próprias igrejas e convenções.
  - Institutos de pesquisa com ficha técnica: Pew, Lifeway, Datafolha, Barna.
  - Agências especializadas com política de correção pública: Religion News Service, The Pillar, Forum 18.
  - Mesmo assim, citação literal só de frase lida na fonte.
- **Nível B: bom gatilho de pauta e atribuível ("segundo a Gazeta do Povo…"), mas o fato central precisa de confirmação na fonte primária antes de publicar.**
  - No Brasil: Gazeta do Povo, Revista Oeste, O Antagonista, Crusoé, Jovem Pan, Pleno News, Canção Nova, Comunhão, Ultimato, ACI Digital/EWTN, Portas Abertas, ACN, ANAJURE.
  - Internacionais: Christianity Today, Christian Post, WORLD, NCRegister, EWTN News, CBN, The Free Press, National Review, Washington Examiner, Dispatch, Telegraph, Brussels Signal.
  - ONGs de advocacy (ICC, ADF, ACLJ, Christian Concern, Open Doors) também entram aqui. Elas são **parte interessada**: diga isso no texto e confirme casos em documento judicial ou imprensa local.
- **Nível C: só termômetro do que está circulando. Nunca atribuir fato só a eles; sempre voltar à origem.**
  - Brasil: Jornal da Cidade Online, Conexão Política, Brasil Paralelo (para fatos), Revista Timeline, Esmeril, Diário do Poder (bastidores), Good Prime/Gospel Prime, Gospel+, Folha Gospel, Púlpito Cristão.
  - Internacionais: Breitbart, Newsmax e Daily Caller (os três depreciados na WP:RSP), Daily Wire, Federalist, Blaze, NY Post, GB News, Daily Signal, Townhall.
  - Texto de opinião (Federalist, National Review, First Things, Mises etc.) é sempre opinião: citar como opinião de quem assina.

### Regras práticas

1. **Notícia internacional de perseguição** costuma vir em cadeia: Guiame ou Gospel Prime traduzem Christian Post ou ICC, que citam uma ONG local. Suba a cadeia até a origem (ONG, polícia, tribunal, imprensa local) e atribua a ela.
2. **Números de pesquisa**: sempre buscar o relatório original (Pew, Lifeway, Datafolha, IBGE) e informar data de campo, amostra e margem.
3. **Feeds de veículos generalistas** (Gazeta do Povo, Fox, NY Post, Jovem Pan…) devem usar `filtro` para não inundar a pauta.
4. **Respeitar o robots.txt.** Feeds proibidos para `*` (Good Prime, Comunhão, Conexão Política, Open Doors, WSJ, ONU News por regra ambígua) ficam fora do coletor e servem só para leitura pontual com link, como já diz o `_ajuda` do config.
5. **Bots de IA**: vários sites bloqueiam ClaudeBot, GPTBot e afins, mas liberam `*`. O coletor não é bot de IA, mas a pauta é preparada com ajuda de IA. Por isso os feeds desses sites estão separados abaixo (lista B), e cabe à pessoa revisora decidir se entram.
6. **Bloqueados da nuvem** (CPAD News, RNS, Premier, Washington Times, Telegraph, IBGE, State Dept., Desiring God, Newsmax) **não estão mortos**. Se o coletor rodar em IP de datacenter, vai falhar. Teste de uma rede comum antes de cadastrar.
7. **Mudanças recentes a registrar**:
   - Gospel Prime virou goodprime.co.
   - Catholic News Agency virou EWTN News (jan/2026).
   - Gnotícias redireciona para um domínio morto.
   - Terça Livre, Renova Mídia, Crítica Nacional e Cristianismo Hoje não resolvem DNS.
   - Os feeds de Baptist Press, ADF e Becket estão vazios.
   - Os feeds de CGADB, Barna, MNN e WSJ Opinion estão parados.

### JSON dos feeds que funcionam (para `config/fontes.json`)

Não repete os 9 feeds que já estão no config. Todos responderam HTTP 200 com RSS válido e itens em 29/10/2026, e o robots.txt **não** proíbe o caminho para `User-agent: *`. Os `filtro` usam o mesmo estilo de regex do campo `temas`. Revise o `tipo` e a `editoria` antes de colar: são sugestões.

**Lista A: sem restrição a bots de IA no robots.txt**

```json
[
 {"nome": "Pleno News", "url": "https://pleno.news/feed", "editoria": "noticias-gospel", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|pastor|gospel|católic|religios|perseguição|missionári|bíblia"},
 {"nome": "Guiame", "url": "https://guiame.com.br/rss", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Gospel+ Notícias", "url": "https://gospelmais.com/noticias/feed", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Folha Gospel", "url": "https://folhagospel.com/feed/", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Canção Nova Notícias", "url": "https://noticias.cancaonova.com/feed/", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Aliança Cristã Evangélica Brasileira", "url": "https://aliancaevangelica.org.br/feed/", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "Notícias Adventistas", "url": "https://noticias.adventistas.org/pt/feed/", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "ACN Brasil (Ajuda à Igreja que Sofre)", "url": "https://www.acn.org.br/feed/", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "STF Notícias", "url": "https://noticias.stf.jus.br/feed/", "editoria": "politica-e-sociedade", "tipo": "primaria"},
 {"nome": "Agência Brasil: Direitos Humanos", "url": "https://agenciabrasil.ebc.com.br/rss/direitos-humanos/feed.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria"},
 {"nome": "O Antagonista", "url": "https://oantagonista.com.br/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria"},
 {"nome": "Revista Crusoé", "url": "https://crusoe.com.br/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria"},
 {"nome": "Jovem Pan News", "url": "https://jovempan.com.br/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|liberdade religiosa|liberdade de expressão|família|aborto|escola|educação"},
 {"nome": "Brasil Paralelo: notícias", "url": "https://www.brasilparalelo.com.br/noticias/feed.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria"},
 {"nome": "Diário do Poder", "url": "https://diariodopoder.com.br/feed", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|bancada|família|aborto"},
 {"nome": "Poder360", "url": "https://www.poder360.com.br/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|liberdade religiosa|aborto|família|escola"},
 {"nome": "Veja", "url": "https://veja.abril.com.br/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|aborto|família"},
 {"nome": "Instituto Mises Brasil", "url": "https://mises.org.br/feed/", "editoria": "economia-e-negocios", "tipo": "secundaria"},
 {"nome": "Revista Esmeril", "url": "https://revistaesmeril.com.br/feed/", "editoria": "musica-e-cultura", "tipo": "secundaria"},
 {"nome": "Ultimato", "url": "http://feeds.feedburner.com/ultimato", "editoria": "fe-e-biblia", "tipo": "secundaria"},
 {"nome": "The Christian Post", "url": "https://www.christianpost.com/rss", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Christian Headlines (Crosswalk)", "url": "https://www.crosswalk.com/headlines/rss.xml", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "The Pillar", "url": "https://www.pillarcatholic.com/feed", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "National Catholic Register", "url": "https://www.ncregister.com/feeds/general-news.xml", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "WORLD", "url": "https://wng.org/feeds/rss/magazine.rss", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "International Christian Concern", "url": "https://persecution.org/feed/", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Christian Daily International", "url": "https://www.christiandaily.com/rss.xml", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Christian Today (UK)", "url": "https://www.christiantoday.com/rss.xml", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Forum 18", "url": "https://www.forum18.org/syndication/forum18.xml", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "USCIRF", "url": "https://www.uscirf.gov/rss.xml", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "ERLC (Southern Baptist Convention)", "url": "https://erlc.com/feed/", "editoria": "familia-e-valores", "tipo": "primaria"},
 {"nome": "Christian Concern (UK)", "url": "https://christianconcern.com/feed/", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "The Gospel Coalition", "url": "https://www.thegospelcoalition.org/feed/", "editoria": "fe-e-biblia", "tipo": "secundaria"},
 {"nome": "First Things", "url": "https://firstthings.com/feed/", "editoria": "fe-e-biblia", "tipo": "secundaria"},
 {"nome": "Relevant", "url": "https://relevantmagazine.com/feed/", "editoria": "musica-e-cultura", "tipo": "secundaria"},
 {"nome": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/latest.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|pastor|abortion|persecut|bible"},
 {"nome": "The Daily Wire", "url": "https://www.dailywire.com/feeds/rss.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|pastor|abortion|persecut|bible"},
 {"nome": "The Daily Signal", "url": "https://www.dailysignal.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|pastor|abortion|persecut|family"},
 {"nome": "National Review", "url": "https://www.nationalreview.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion|persecut"},
 {"nome": "Washington Examiner", "url": "https://www.washingtonexaminer.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion|persecut"},
 {"nome": "The Federalist", "url": "https://thefederalist.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion|persecut"},
 {"nome": "Breitbart", "url": "https://feeds.feedburner.com/breitbart", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|pastor|persecut"},
 {"nome": "TheBlaze", "url": "https://www.theblaze.com/feeds/feed.rss", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|pastor|abortion|persecut"},
 {"nome": "GB News", "url": "https://www.gbnews.com/feeds/news.rss", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|catholic|faith|relig|vicar|bishop|abortion|persecut"},
 {"nome": "The Dispatch", "url": "https://thedispatch.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion"},
 {"nome": "The American Conservative", "url": "https://www.theamericanconservative.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|catholic|faith|relig"},
 {"nome": "Brussels Signal", "url": "https://brusselssignal.eu/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|catholic|faith|relig|abortion|family|persecut"},
 {"nome": "Townhall", "url": "https://townhall.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion"},
 {"nome": "The American Spectator", "url": "https://spectator.org/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|catholic|faith|relig"},
 {"nome": "RealClearPolitics", "url": "https://www.realclearpolitics.com/index.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|poll"}
]
```

**Lista B: o feed está liberado para `*`, mas o robots.txt do site bloqueia bots de IA (ClaudeBot, GPTBot e afins). A decisão é da pessoa revisora.**

```json
[
 {"nome": "Vatican News (português)", "url": "https://www.vaticannews.va/pt.rss.xml", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "Vatican News (inglês)", "url": "https://www.vaticannews.va/en.rss.xml", "editoria": "noticias-gospel", "tipo": "primaria"},
 {"nome": "EWTN News (ex-Catholic News Agency)", "url": "https://www.ewtnnews.com/rss", "editoria": "noticias-gospel", "tipo": "secundaria"},
 {"nome": "Gazeta do Povo", "url": "https://www.gazetadopovo.com.br/feed/rss/ultimas-noticias.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|católic|religios|liberdade religiosa|liberdade de expressão|família|aborto|escola|educação"},
 {"nome": "Revista Oeste", "url": "https://revistaoeste.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria"},
 {"nome": "Folha de S.Paulo: Poder", "url": "https://feeds.folha.uol.com.br/poder/rss091.xml", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|aborto|família"},
 {"nome": "Estadão: Política", "url": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/politica/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "igreja|evangélic|cristã|cristão|religios|aborto|família"},
 {"nome": "The Free Press", "url": "https://www.thefp.com/feed", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|faith|relig|abortion"},
 {"nome": "New York Post", "url": "https://nypost.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|catholic|faith|relig|pastor|priest"},
 {"nome": "The Daily Caller", "url": "https://dailycaller.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|evangelical|catholic|faith|relig|abortion"},
 {"nome": "UnHerd", "url": "https://unherd.com/feed/", "editoria": "politica-e-sociedade", "tipo": "secundaria", "filtro": "church|christian|faith|relig"}
]
```

Observações sobre o JSON:

- **Ultimato** e **Forum 18** não têm data por item. Se o `tools/editorial/coletar.py` exigir `pubDate`, eles serão descartados ou ficarão sem data; confira o comportamento antes de colar.
- A **Revista Timeline** funciona, mas publica pouco (último item em 21/10). Ficou fora, mas pode entrar.
- **Fora de propósito**:
  - Robots proíbe o feed para `*`: Good Prime/Gospel Prime, Comunhão, Conexão Política, WSJ, ONU News.
  - Feed vazio: Baptist Press, ADF, ADF International, Becket.
  - Feed parado: CGADB, Barna, MNN, Senso Incomum.
