# Plano de SEO e divulgação de O Paladino

Auditoria de 30/10/2026 feita no repositório e no site no ar (https://opaladino.com.br). Este arquivo fica fora do site
(a pasta `docs/` não é publicada).

## 1. Diagnóstico

### O que já está bom (não mexer)

- Toda página tem canonical, Open Graph, um único H1, `max-image-preview:large` (imagem grande no Discover) e um
  bloco JSON-LD coerente com o que aparece na página. Quem garante isso é o `tools/checar_seo.py`, que roda no CI e no deploy.
- Há `sitemap.xml` (35 URLs), com lastmod real (só muda quando o conteúdo muda), e `sitemap-noticias.xml` no padrão do
  Google Notícias (notas das últimas 48 h).
- O `robots.txt` libera todos os robôs, e o `llms.txt` serve aos assistentes de IA, que citam a fonte.
- As páginas são estáticas e leves (cerca de 50 KB de HTML), saem do GitHub Pages pela CDN, usam fonte local com preload
  e imagens com `srcset`. A página 404 tem `noindex` e a prévia de revisão também.
- `www.opaladino.com.br` redireciona para o domínio principal, e o endereço antigo (`meruvash.github.io/Arcvalion_gospel/`) também.
- As notícias usam `NewsArticle`, com data visível igual à do JSON-LD e trilha (`BreadcrumbList`).

### Problemas encontrados

| # | Problema | Impacto | Situação |
|---|----------|---------|----------|
| 1 | O arquivo da chave do IndexNow (`e6a19f….txt`) não existia no ar: o `tools/indexnow.py` parava sem avisar o Bing | Alto: o Bing (que também abastece o ChatGPT Search e o Copilot) não era avisado das matérias novas | **Corrigido** |
| 2 | Não havia feed RSS | Alto: Google Publisher Center, Feedly, Inoreader, Flipboard e agregadores dependem de feed | **Corrigido** (`/feed.xml`) |
| 3 | Os códigos de verificação do Search Console e do Bing (`verificacao` em `config/portal.json`) não saíam em página nenhuma | Alto: sem verificação não há Search Console | **Corrigido no código**; falta colar os códigos (ver fase 1) |
| 4 | O medidor de visitas (`analytics.cloudflare_token`) também não saía: o site está sem nenhuma medição | Alto: não dá para saber o que funciona | **Corrigido no código**; falta o token |
| 5 | `http://` não redireciona para `https://`: o GitHub Pages está com "Enforce HTTPS" desligado | Médio: conteúdo duplicado e aviso de "não seguro" | Ação sua (fase 1) |
| 6 | Sete notas guardam a editoria pelo slug (`politica-e-sociedade`), e a etiqueta aparecia assim no site | Médio: etiqueta feia na página e editoria errada para o Google | **Corrigido** (o build mostra o nome da editoria) |
| 7 | Organization sem `sameAs` (o portal não tem redes próprias em `config/portal.json`) | Médio: o Google não liga o site aos perfis e demora a montar o painel da marca | Ação sua: criar os perfis do portal |
| 8 | Faltavam `articleSection`, `article:section`, `article:modified_time`, `isAccessibleForFree` e `publishingPrinciples` | Baixo/médio: sinais de confiança para o Google Notícias | **Corrigido** |
| 9 | Descrição do arquivo de notícias tinha só 50 caracteres | Baixo | **Corrigido** |
| 10 | O título da home é "O Paladino: jornalismo com princípios", sem nenhuma palavra que alguém busque | Médio | **Feito** em 30/10/2026: "O Paladino: notícias gospel, política e família com visão cristã" |
| 11 | Não há páginas por editoria com endereço fixo | — | **Descartado** pelo editor em 30/10/2026: a separação por editoria dentro de Notícias basta |
| 12 | Descrição das notícias = lide inteiro (até ~370 caracteres); o Google corta em ~155 | Baixo: o Google corta sozinho, mas a frase fica truncada | **Feito**: campo opcional `descricao_seo`; sem ele, primeira frase do lide ou lide cortado em 155 |
| 13 | Autoria só como "Redação O Paladino" | Baixo/médio para E-E-A-T | Fase 3 (página do editor, sem mencionar advocacia) |

## 2. O que mudou no código (este branch)

- `tools/build_sitemap.py` gera também o `feed.xml` (RSS 2.0, 50 itens, notícias e estudos, só o que está no sitemap) e o
  arquivo da chave do IndexNow a partir de `indexnow_chave`.
- `tools/seo.py`:
  - `cabeca()` põe em toda página o `<link rel="alternate">` do feed e as metas `google-site-verification` / `msvalidate.01`
    quando preenchidas.
  - `ANALYTICS` sai do `cloudflare_token`.
  - `Organization` ganha `sameAs` (das `redes`), `publishingPrinciples` e `foundingDate`.
  - Os artigos ganham `articleSection` e `isAccessibleForFree`.
- `tools/build_home.py`: as notas ganham `article:section` e `article:modified_time`, a editoria aparece pelo nome e o arquivo de notícias ganha uma descrição melhor.
- `tools/indexnow.py` lê a chave do `config/portal.json` (um lugar só).
- Teste novo (`tests/test_portal.py`, classe `Feed`).

## 2b. Feito em 30/10/2026 (segunda rodada)

- Título da home trocado; descrição curta das notícias (`descricao_seo` ou resumo automático do lide).
- Ligação notícia ↔ estudo: bloco "Para entender" nas notas (estudos do campo `estudos`; sem nenhum, os dois mais
  recentes) e "Notícias sobre este tema" nos estudos. O `checar_noticia.py` recusa slug de estudo inexistente.

## 3. Plano

### Fase 1: esta semana (ações suas, sem código)

1. **GitHub Pages > Enforce HTTPS**: em Settings > Pages do repositório, marcar "Enforce HTTPS".
2. **Google Search Console** (https://search.google.com/search-console):
   - Adicionar a propriedade de **Domínio** `opaladino.com.br`, verificada por registro TXT na Cloudflare (o mais robusto).
     Ou, se preferir a propriedade de prefixo de URL, cole o código em `config/portal.json` > `verificacao.google`.
   - Enviar `sitemap.xml` e `sitemap-noticias.xml` em "Sitemaps".
   - Em "Inspeção de URL", pedir indexação da home, de `/noticias/`, de `/estudos/` e das 5 notícias mais fortes do dia.
3. **Bing Webmaster Tools** (https://www.bing.com/webmasters): "Importar do Google Search Console" (um clique) e enviar os
   dois sitemaps. O Bing abastece o ChatGPT Search, o Copilot e o DuckDuckGo.
4. **Medição**: Cloudflare > Web Analytics > Add a site > `opaladino.com.br`. Cole o token em `analytics.cloudflare_token`.
   Não usa cookies, então não precisa de aviso de consentimento.
5. **Google Publisher Center / Google Notícias** (https://publishercenter.google.com): cadastrar a publicação, com nome,
   logo e o feed `https://opaladino.com.br/feed.xml` por seção. Isso ajuda a aparecer em "Notícias" e no "Seguir" do Discover.
6. **Rodar `python3 tools/indexnow.py --tudo`** depois do deploy deste branch (agora a chave está no ar).
7. **Perfis do portal** (não do editor): Instagram, canal de WhatsApp, Telegram, YouTube e X com o nome "O Paladino".
   Cole os endereços em `config/portal.json` > `redes`. Eles aparecem no rodapé e no `sameAs` automaticamente.
   O Instagram pessoal do editor não entra em `redes`.

### Fase 2: próximos 30 dias (código, posso fazer)

1. ~~Páginas fixas por editoria~~: descartado pelo editor em 30/10/2026 (a separação dentro de Notícias basta). Não propor de novo.
2. **Título da home com palavra buscada**, por exemplo "O Paladino: notícias gospel, política e família com visão cristã".
   A decisão é sua, porque mexe na marca.
3. **Campo opcional `descricao_seo`** nas notícias (até 155 caracteres), com fallback para o lide.
4. **Links internos**: em cada nota, um bloco "Para entender" que liga ao estudo bíblico relacionado quando o tema bate,
   e do estudo para as notícias do mesmo tema. Isso distribui autoridade para os estudos, que são o conteúdo perene.
5. **Search Console semanal na verificação**: a skill `verificacao` lê o relatório de páginas não indexadas e corrige o que for do site.

### Fase 3: 60 a 90 dias (conteúdo e autoridade)

1. **Estudos que respondem buscas reais.** Os estudos são o que traz tráfego o ano inteiro. Na pauta
   (`conteudo/pauta_estudos.json`), priorize perguntas que as pessoas digitam, como "o que significa…", "o que a Bíblia diz
   sobre…", "dízimo é bíblico?" e "o que é o arrebatamento", com o título no formato da pergunta. Antes de pautar, use o
   Google Trends (Brasil, categoria Religião) e o "As pessoas também perguntam" do Google.
2. **Página do editor responsável** (`/sobre/` ampliado ou `/equipe/<nome>/`): nome, função e o que ele assina, sem
   mencionar advocacia nem oferecer serviço (regra de 30/10/2026). Liga o `Person` ao `publisher`.
3. **Backlinks**: oferecer o "Versículo diário" (`/consulta/`) e os estudos como material de apoio para igrejas, células
   e escolas dominicais. Um link do site de uma igreja vale mais que dezenas de posts.
4. **Newsletter** (o Worker já existe em `worker/`; falta `interacoes.api`): um resumo diário por e-mail, que é tráfego que não depende do Google.

## 4. Divulgação

O pacote diário já existe: `python3 tools/divulgacao.py` gera `divulgacao/<data>.md` com textos prontos para Instagram,
WhatsApp e Telegram. O que falta é ter onde postar e uma rotina.

### Canais, por ordem de retorno esperado para um portal cristão no Brasil

1. **Canal de WhatsApp "O Paladino"**: é o maior canal do público evangélico. Poste o "Resumo do dia" do pacote uma vez por
   dia, no fim da tarde. Coloque o link do canal no rodapé (`redes.whatsapp_canal`).
2. **Grupos de WhatsApp e Telegram de igrejas, células e ministérios**: peça a pastores e líderes conhecidos para repassar o
   estudo da semana, não a notícia do dia. Estudo é visto como serviço, e notícia política como propaganda.
3. **Instagram do portal**: um post por dia com a notícia mais forte (o cartão `img/og/noticia-*.jpg` já tem o tamanho
   certo) e um carrossel por semana com um estudo. Nos Stories, use o adesivo de link para a matéria.
4. **YouTube Shorts, Reels e TikTok**: 30 a 45 segundos lendo o "Por que importa" de uma nota, com a fonte na tela.
5. **Google Discover**: não se posta nada. Ele puxa sozinho matérias com foto grande, título claro e site verificado, o que
   já está pronto depois da fase 1.

### Rotina sugerida (15 minutos por dia)

| Horário | O quê |
|---------|-------|
| 9h, depois dos estudos | Stories com o estudo do dia |
| 12h | Post do Instagram com a notícia mais forte |
| 18h | Resumo do dia no canal de WhatsApp e no Telegram |
| Domingo | Carrossel do estudo da semana, para os grupos de igreja |

### Texto de lançamento para mandar a contatos (pronto para colar)

```
Lançamos O Paladino (opaladino.com.br): notícias do mundo evangélico, de política e de família, sempre com fonte e
data, e estudos bíblicos com o que dizem os teólogos de cada lado, além da nossa posição pentecostal.
Todo dia tem versículo, notícia e estudo novo. Se fizer sentido para você, repasse para o seu grupo. 🙏
```

### Como medir (depois da fase 1)

- **Search Console > Desempenho**: cliques, impressões e as consultas que trazem gente. Revise toda segunda.
- **Search Console > Páginas**: quantas URLs estão indexadas. A meta é todas as do sitemap em até 2 semanas.
- **Cloudflare Web Analytics**: as páginas mais vistas e de onde vem o tráfego (Google, WhatsApp, Instagram).
- **Metas para 90 dias**: 100% do sitemap indexado; aparecer na aba Notícias para buscas como "notícias gospel hoje";
  cada estudo entre os 10 primeiros resultados para a pergunta do título.
